from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, status, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
# import firebase_admin
# from firebase_admin import credentials, firestore
from typing import List, Dict, Any, Optional, Set
# from google.cloud.firestore_v1.transaction import Transaction
from cache_manager import cache_manager

app = FastAPI(
    title="リアルタイム議事録モックAPI",
    description="リアルタイムの会議議事録と録音を管理するためのAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 1,
        "defaultModelExpandDepth": 2,
        "deepLinking": True,
        "displayRequestDuration": True,
        "syntaxHighlight.theme": "monokai",
        "operationsSorter": "method",
        "tagsSorter": "alpha",
        "docExpansion": "list",
        "showExtensions": True,
        "tryItOutEnabled": True
    }
)
# Allow CORS for frontend development
tmp_cors = ["*"]
app.add_middleware(CORSMiddleware, allow_origins=tmp_cors, allow_methods=["*"], allow_headers=["*"])

# ----- Schemas -----
class LoginRequest(BaseModel):
    """User login credentials"""
    email: str = "user@example.com"
    password: str = "password123"

class TokenResponse(BaseModel):
    """Authentication tokens for API access"""
    access_token: str
    refresh_token: str

class User(BaseModel):
    """User information"""
    id: str
    name: str
    email: str

class TemplateItem(BaseModel):
    """Template item within a section"""
    text: str
    order: int

class MeetingAssist(BaseModel):
    """会議アシスト情報"""
    section_id: str
    meeting_id: str
    generated_at: str
    status: str = "active"  # active, completed, outdated
    discussion_starter: str = ""  # 話の切り出し方
    key_questions: list[str] = []  # 重要な質問
    conclusion_guide: str = ""  # まとめの言葉
    time_management: dict = {}  # 時間管理のヒント
    participation_tips: list[str] = []  # 参加促進のヒント

class TemplateSection(BaseModel):
    """Template section with predefined items"""
    title: str
    order: int
    items: list[TemplateItem] = []

class Template(BaseModel):
    """Meeting template with predefined sections and items"""
    id: str
    name: str
    sections: list[TemplateSection]

class Meeting(BaseModel):
    """Meeting information"""
    id: str
    title: str
    datetime: str
    template_id: str | None = None
    status: str = "scheduled"  # scheduled | in_progress | completed

class RecordingStatus(BaseModel):
    """Status of meeting recording"""
    status: str = "stopped"  # recording | stopped | processing

class Section(BaseModel):
    """Meeting section (e.g., agenda, decisions, action items)"""
    id: str
    title: str
    order: int
    status: str = "not_started"  # not_started | in_progress | completed

class Item(BaseModel):
    """Content item within a section"""
    id: str
    section_id: str
    text: str
    order: int

class Task(BaseModel):
    """Action item or task from a meeting"""
    id: str
    text: str
    assignee: str | None = None
    due_date: str | None = None
    status: str = "open"  # open | done

# ----- In-memory mock data -----
mock_user = User(id="u1", name="Alice", email="alice@example.com")
mock_templates = [
    Template(
        id="t1", 
        name="標準会議テンプレート",
        sections=[
            TemplateSection(
                title="議題",
                order=1,
                items=[
                    TemplateItem(text="前回の議事録の確認", order=1),
                    TemplateItem(text="進捗状況の報告", order=2),
                    TemplateItem(text="課題の共有", order=3)
                ]
            ),
            TemplateSection(
                title="決定事項",
                order=2,
                items=[
                    TemplateItem(text="次回の目標設定", order=1),
                    TemplateItem(text="リソース配分", order=2)
                ]
            ),
            TemplateSection(
                title="アクションアイテム",
                order=3,
                items=[]
            )
        ]
    )
]
mock_meetings = [Meeting(id="m1", title="Mock Meeting", datetime="2025-06-22T16:00:00", template_id="t1", status="in_progress")]
# mock_sectionsを初期化
mock_sections = {}
mock_items = {
    "s1": [Item(id="i1", section_id="s1", text="ダミー項目1", order=1)],
    "s2": [Item(id="i2", section_id="s2", text="ダミー項目2", order=1)],
}
mock_tasks = {
    "m1": [Task(id="task1", text="フォローアップメール送信", assignee="Bob", due_date="2025-06-23", status="open")]
}
mock_rec_status = {"m1": "stopped"}

# ----- Firestore Setup -----
# Note: In production, use proper credentials management
# Temporarily disabled for testing
USE_FIRESTORE = False
print("Firestore disabled for testing - using mock data only")
db = None

# ----- Firestore Helper Functions -----
async def get_document(collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
    """Get a document from Firestore"""
    if not USE_FIRESTORE:
        return None
        
    doc_ref = db.collection(collection).document(doc_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None

async def set_document(collection: str, doc_id: str, data: Dict[str, Any]) -> None:
    """Set a document in Firestore"""
    if not USE_FIRESTORE:
        return
        
    db.collection(collection).document(doc_id).set(data)

async def update_document(collection: str, doc_id: str, data: Dict[str, Any]) -> None:
    """Update a document in Firestore"""
    if not USE_FIRESTORE:
        return
        
    db.collection(collection).document(doc_id).update(data)

async def delete_document(collection: str, doc_id: str) -> None:
    """Delete a document from Firestore"""
    if not USE_FIRESTORE:
        return
        
    db.collection(collection).document(doc_id).delete()

async def query_collection(collection: str, field: str, value: Any) -> List[Dict[str, Any]]:
    """Query documents from Firestore"""
    if not USE_FIRESTORE:
        return []
        
    docs = db.collection(collection).where(field, "==", value).stream()
    return [doc.to_dict() for doc in docs]

# ----- Transaction Helpers for Data Consistency -----
async def delete_meeting_with_related_data(meeting_id: str) -> None:
    """Delete a meeting and all related data (sections, items, tasks) in a transaction"""
    if not USE_FIRESTORE:
        # Fallback to mock data deletion
        if meeting_id in mock_meetings:
            mock_meetings.remove(next(m for m in mock_meetings if m.id == meeting_id))
        if meeting_id in mock_sections:
            del mock_sections[meeting_id]
        if meeting_id in mock_tasks:
            del mock_tasks[meeting_id]
        if meeting_id in mock_rec_status:
            del mock_rec_status[meeting_id]
        # Delete items belonging to sections of this meeting
        section_ids = [s.id for s in mock_sections.get(meeting_id, [])]
        for section_id in section_ids:
            if section_id in mock_items:
                del mock_items[section_id]
        return

    # Using Firestore transaction for atomic operations
    transaction = db.transaction()
    delete_meeting_transaction(transaction, meeting_id)
    
def delete_meeting_transaction(transaction: Any, meeting_id: str) -> None:
    """Transaction function to delete a meeting and all related data"""
    # Delete the meeting document
    meeting_ref = db.collection('meetings').document(meeting_id)
    transaction.delete(meeting_ref)
    
    # Delete all sections for this meeting
    sections = db.collection('sections').where('meeting_id', '==', meeting_id).stream()
    for section in sections:
        section_id = section.id
        transaction.delete(section.reference)
        
        # Delete all items for this section
        items = db.collection('items').where('section_id', '==', section_id).stream()
        for item in items:
            transaction.delete(item.reference)
    
    # Delete all tasks for this meeting
    tasks = db.collection('tasks').where('meeting_id', '==', meeting_id).stream()
    for task in tasks:
        transaction.delete(task.reference)
    
    # Delete recording status
    rec_status_ref = db.collection('recording_status').document(meeting_id)
    transaction.delete(rec_status_ref)

async def delete_section_with_items(meeting_id: str, section_id: str) -> None:
    """Delete a section and all its items in a transaction"""
    if not USE_FIRESTORE:
        # Fallback to mock data deletion
        if meeting_id in mock_sections:
            mock_sections[meeting_id] = [s for s in mock_sections[meeting_id] if s.id != section_id]
        if section_id in mock_items:
            del mock_items[section_id]
        return

    # Using Firestore transaction for atomic operations
    transaction = db.transaction()
    delete_section_transaction(transaction, meeting_id, section_id)

def delete_section_transaction(transaction: Any, meeting_id: str, section_id: str) -> None:
    """Transaction function to delete a section and all its items"""
    # Delete the section document
    section_ref = db.collection('sections').document(section_id)
    transaction.delete(section_ref)
    
    # Delete all items for this section
    items = db.collection('items').where('section_id', '==', section_id).stream()
    for item in items:
        transaction.delete(item.reference)

async def update_section_order(meeting_id: str, section_id: str, new_order: int) -> None:
    """Update section order and ensure order consistency"""
    if not USE_FIRESTORE:
        # Fallback to mock data update
        if meeting_id in mock_sections:
            for s in mock_sections[meeting_id]:
                if s.id == section_id:
                    s.order = new_order
                    break
        return

    # Get all sections for this meeting
    sections = db.collection('sections').where('meeting_id', '==', meeting_id).stream()
    sections_data = [(section.id, section.to_dict()) for section in sections]
    
    # Using transaction to ensure consistency
    transaction = db.transaction()
    update_section_order_transaction(transaction, sections_data, section_id, new_order)

def update_section_order_transaction(transaction: Any, sections_data: List[tuple], section_id: str, new_order: int) -> None:
    """Transaction function to update section order with consistency"""
    # Update the target section
    section_ref = db.collection('sections').document(section_id)
    transaction.update(section_ref, {'order': new_order})
    
    # Optional: Adjust other sections if needed to maintain consistent ordering
    # This is application-specific logic that depends on your requirements

# ----- WebSocket Manager -----
class WebSocketManager:
    """WebSocketコネクションを管理するクラス"""
    
    def __init__(self):
        # meeting_id -> Set[WebSocket]
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, meeting_id: str):
        """新しいWebSocket接続を追加"""
        await websocket.accept()
        if meeting_id not in self.active_connections:
            self.active_connections[meeting_id] = set()
        self.active_connections[meeting_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, meeting_id: str):
        """WebSocket接続を削除"""
        if meeting_id in self.active_connections:
            self.active_connections[meeting_id].discard(websocket)
            if not self.active_connections[meeting_id]:
                del self.active_connections[meeting_id]
    
    async def broadcast(self, meeting_id: str, message: dict):
        """特定の会議に接続しているすべてのクライアントにメッセージを送信"""
        if meeting_id in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[meeting_id]:
                try:
                    await connection.send_json(message)
                except RuntimeError:
                    # 接続が既に閉じられている場合
                    dead_connections.add(connection)
            
            # 死んだ接続を削除
            for dead in dead_connections:
                self.active_connections[meeting_id].discard(dead)
    
    async def send_section_assist(self, meeting_id: str, section_id: str, status: str):
        """セクションのステータス変更時に会議アシスト情報を送信"""
        # セクション情報を取得
        section_title = ""
        for s in mock_sections.get(meeting_id, []):
            if s.id == section_id:
                section_title = s.title
                break
        
        # 会議アシスト情報を生成
        assist_info = await generate_meeting_assist(meeting_id, section_id, section_title)
        
        message = {
            "type": "section.status_changed",
            "sectionId": section_id,
            "status": status,
            "meeting_assist": assist_info.dict(),
            "message": f"セクションのステータスが '{status}' に変更されました。"
        }
        
        await self.broadcast(meeting_id, message)
    
    async def send_meeting_assist(self, meeting_id: str, assist_type: str, custom_message: str = None):
        """会議の進行に関する会議アシスト情報を送信"""
        # 現在のセクション情報を取得（簡単な実装）
        current_section_id = None
        current_section_title = "会議"
        
        for section in mock_sections.get(meeting_id, []):
            if section.status == "in_progress":
                current_section_id = section.id
                current_section_title = section.title
                break
        
        # 会議アシスト情報を生成
        if current_section_id:
            assist_info = await generate_meeting_assist(meeting_id, current_section_id, current_section_title)
        else:
            # セクションが特定できない場合のデフォルト
            assist_info = await generate_meeting_assist(meeting_id, "general", "会議全般")
        
        message = {
            "type": "meeting.assist",
            "meetingId": meeting_id,
            "assistType": assist_type,
            "meeting_assist": assist_info.dict(),
            "message": custom_message or f"{assist_type} の会議アシスト情報が送信されました。"
        }
        
        await self.broadcast(meeting_id, message)
    
    async def send_assist_reminder(self, meeting_id: str, section_id: str = None):
        """会議アシスト機能のリマインダーを送信"""
        # セクション情報を取得
        section_title = "会議"
        if section_id:
            for s in mock_sections.get(meeting_id, []):
                if s.id == section_id:
                    section_title = s.title
                    break
        
        # 会議アシスト情報を生成
        assist_info = await generate_meeting_assist(meeting_id, section_id or "general", section_title)
        
        message = {
            "type": "meeting.assist_reminder",
            "meetingId": meeting_id,
            "sectionId": section_id,
            "meeting_assist": assist_info.dict(),
            "message": "会議アシスト機能からのリマインダーです。"
        }
        
        await self.broadcast(meeting_id, message)

# WebSocketマネージャーのインスタンスを作成
websocket_manager = WebSocketManager()

# ----- Meeting Assist Functions -----
# 会議アシスト機能用のヘルパー関数

async def generate_meeting_assist(meeting_id: str, section_id: str, section_title: str) -> MeetingAssist:
    """
    LLMを使用して会議アシスト情報を生成する
    現在はモック実装、実際にはLLM APIを呼び出す
    """
    from datetime import datetime
    
    # TODO: 実際のLLM生成ロジックを実装
    # 現在はセクションタイトルに基づく簡単なモック
    
    assist_info = MeetingAssist(
        section_id=section_id,
        meeting_id=meeting_id,
        generated_at=datetime.now().isoformat(),
        status="active",
        discussion_starter=f"{section_title}について話し合いを始めましょう。",
        key_questions=[
            f"{section_title}に関して、現在の状況はいかがですか？",
            "他に考慮すべき点はありますか？",
            "次のステップは何でしょうか？"
        ],
        conclusion_guide=f"{section_title}についての議論をまとめましょう。",
        time_management={
            "suggested_duration": "15分",
            "time_check": "時間を意識して進めましょう。"
        },
        participation_tips=[
            "全員の意見を聞きましょう",
            "具体例があると良いでしょう"
        ]
    )
    
    return assist_info

# ----- Helper Functions -----

# mock_sectionsを初期化
mock_sections = {
    "m1": [
        Section(
            id="s1", 
            title="議題", 
            order=1, 
            status="completed"
        ),
        Section(
            id="s2", 
            title="決定事項", 
            order=2, 
            status="in_progress"
        ),
    ]
}

# ----- Dependency -----
def get_current_user():
    return mock_user

# ----- Auth Endpoints -----
@app.post("/auth/login", response_model=TokenResponse, tags=["認証"], summary="システムにログイン", description="メールアドレスとパスワードでユーザーを認証する")
def login(req: LoginRequest):
    return TokenResponse(access_token="mock-token", refresh_token="mock-refresh")

@app.post("/auth/refresh", response_model=TokenResponse, tags=["認証"], summary="トークンの更新", description="リフレッシュトークンを使用して新しいアクセストークンを取得する")
def refresh():
    return TokenResponse(access_token="new-mock-token", refresh_token="new-mock-refresh")

@app.get("/users/me", response_model=User, tags=["ユーザー"], summary="現在のユーザーを取得", description="現在認証されているユーザーの情報を取得する")
def read_user(user: User = Depends(get_current_user)):
    return user

@app.patch("/users/me", response_model=User, tags=["ユーザー"], summary="ユーザープロフィールを更新", description="現在認証されているユーザーの情報を更新する")
def update_user(user_update: User, user: User = Depends(get_current_user)):
    return user_update

# ----- Template Endpoints -----
@app.get("/templates", response_model=list[Template], tags=["テンプレート"], summary="テンプレート一覧", description="利用可能な全ての会議テンプレートを取得する")
def list_templates(user: User = Depends(get_current_user)):
    return mock_templates

@app.post("/templates", response_model=Template, tags=["テンプレート"], summary="テンプレート作成", description="新しい会議テンプレートを作成する（セクションと項目を含む）")
async def create_template(t: Template, user: User = Depends(get_current_user)):
    # バリデーション: セクションの順序が重複していないことを確認
    section_orders = [section.order for section in t.sections]
    if len(section_orders) != len(set(section_orders)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="セクションの順序が重複しています。各セクションには一意の順序を設定してください。"
        )
    
    # バリデーション: 各セクション内の項目の順序が重複していないことを確認
    for section in t.sections:
        item_orders = [item.order for item in section.items]
        if len(item_orders) != len(set(item_orders)) and item_orders:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"セクション '{section.title}' 内の項目の順序が重複しています。各項目には一意の順序を設定してください。"
            )
    
    # モックデータに追加
    mock_templates.append(t)
    
    # Firestoreに保存
    if USE_FIRESTORE:
        template_data = t.dict()
        await set_document('templates', t.id, template_data)
    
    return t

@app.get("/templates/{template_id}", response_model=Template, tags=["テンプレート"], summary="テンプレート取得", description="IDで特定のテンプレートを取得する")
def get_template(template_id: str, user: User = Depends(get_current_user)):
    for tpl in mock_templates:
        if tpl.id == template_id:
            return tpl
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.patch("/templates/{template_id}", response_model=Template, tags=["テンプレート"], summary="テンプレート更新", description="既存のテンプレートを更新する（セクションと項目を含む）")
async def update_template(template_id: str, t: Template, user: User = Depends(get_current_user)):
    # バリデーション: セクションの順序が重複していないことを確認
    section_orders = [section.order for section in t.sections]
    if len(section_orders) != len(set(section_orders)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="セクションの順序が重複しています。各セクションには一意の順序を設定してください。"
        )
    
    # バリデーション: 各セクション内の項目の順序が重複していないことを確認
    for section in t.sections:
        item_orders = [item.order for item in section.items]
        if len(item_orders) != len(set(item_orders)) and item_orders:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"セクション '{section.title}' 内の項目の順序が重複しています。各項目には一意の順序を設定してください。"
            )
    
    # テンプレートの存在確認と更新
    template_found = False
    for idx, tpl in enumerate(mock_templates):
        if tpl.id == template_id:
            template_found = True
            mock_templates[idx] = t
            break
    
    # Firestoreの更新
    if template_found and USE_FIRESTORE:
        template_data = t.dict()
        await update_document('templates', template_id, template_data)
    
    if not template_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return t

@app.delete("/templates/{template_id}", tags=["テンプレート"], summary="テンプレート削除", description="IDでテンプレートを削除する")
async def delete_template(template_id: str, user: User = Depends(get_current_user)):
    # テンプレートの存在確認と削除
    template_found = False
    for tpl in mock_templates:
        if tpl.id == template_id:
            template_found = True
            mock_templates.remove(tpl)
            break
    
    # Firestoreからも削除
    if template_found and USE_FIRESTORE:
        await delete_document('templates', template_id)
    
    if not template_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return {"detail": "deleted"}

@app.post("/templates/examples", tags=["テンプレート"], summary="テンプレート例の追加", description="サンプルテンプレートを追加する")
async def add_template_examples(user: User = Depends(get_current_user)):
    """
    サンプルテンプレートを追加します。
    これは、ユーザーがテンプレートの作成方法を理解するのに役立ちます。
    """
    examples = [
        Template(
            id="example_project_meeting",
            name="プロジェクトミーティング",
            sections=[
                TemplateSection(
                    title="プロジェクト状況",
                    order=1,
                    items=[
                        TemplateItem(text="前回からの進捗", order=1),
                        TemplateItem(text="現在のマイルストーン状況", order=2),
                        TemplateItem(text="リソース使用状況", order=3)
                    ]
                ),
                TemplateSection(
                    title="課題と障害",
                    order=2,
                    items=[
                        TemplateItem(text="現在の課題", order=1),
                        TemplateItem(text="リスク分析", order=2)
                    ]
                ),
                TemplateSection(
                    title="次のステップ",
                    order=3,
                    items=[
                        TemplateItem(text="次回までのアクション", order=1),
                        TemplateItem(text="次回のマイルストーン", order=2)
                    ]
                )
            ]
        ),
        Template(
            id="example_weekly_team",
            name="週次チームミーティング",
            sections=[
                TemplateSection(
                    title="週間レビュー",
                    order=1,
                    items=[
                        TemplateItem(text="先週の目標達成状況", order=1),
                        TemplateItem(text="チームメンバーの進捗報告", order=2)
                    ]
                ),
                TemplateSection(
                    title="今週の計画",
                    order=2,
                    items=[
                        TemplateItem(text="今週の目標設定", order=1),
                        TemplateItem(text="タスク割り当て", order=2)
                    ]
                ),
                TemplateSection(
                    title="その他の議題",
                    order=3,
                    items=[]
                )
            ]
        )
    ]
    
    # 既存のテンプレートと重複しないように確認
    added_templates = []
    for example in examples:
        exists = False
        for tpl in mock_templates:
            if tpl.id == example.id:
                exists = True
                break
        
        if not exists:
            mock_templates.append(example)
            added_templates.append(example)
            
            # Firestoreに保存
            if USE_FIRESTORE:
                template_data = example.dict()
                await set_document('templates', example.id, template_data)
    
    return {
        "detail": f"{len(added_templates)} 個のサンプルテンプレートが追加されました",
        "templates": added_templates
    }

# ----- Meeting Endpoints -----
@app.get("/meetings", response_model=list[Meeting], tags=["会議"], summary="会議一覧", description="利用可能な全ての会議を取得する")
def list_meetings(user: User = Depends(get_current_user)):
    return mock_meetings

@app.post("/meetings", response_model=Meeting, tags=["会議"], summary="会議作成", description="新しい会議を作成する（テンプレートが指定されている場合は関連セクションも作成）")
async def create_meeting(m: Meeting, user: User = Depends(get_current_user)):
    # Add to mock data
    mock_meetings.append(m)
    
    # If template_id is provided, create sections and items from template
    if m.template_id:
        template = None
        
        # Find template in mock data
        for t in mock_templates:
            if t.id == m.template_id:
                template = t
                break
                
        # If template found, create sections and items
        if template:
            # Create sections based on template sections
            if m.id not in mock_sections:
                mock_sections[m.id] = []
                
            for template_section in template.sections:
                # Generate unique section ID
                section_id = f"s_{m.id}_{template_section.order}"
                
                # Create section
                section = Section(
                    id=section_id, 
                    title=template_section.title, 
                    order=template_section.order,
                    status="not_started"  # 初期状態は「未開始」
                )
                mock_sections[m.id].append(section)
                
                # Add to Firestore if enabled
                if USE_FIRESTORE:
                    section_data = {
                        "id": section_id,
                        "meeting_id": m.id,
                        "title": template_section.title,
                        "order": template_section.order,
                        "status": "not_started"
                    }
                    await set_document('sections', section_id, section_data)
                
                # Create items for this section
                if template_section.items:
                    if section_id not in mock_items:
                        mock_items[section_id] = []
                        
                    for template_item in template_section.items:
                        # Generate unique item ID
                        item_id = f"i_{section_id}_{template_item.order}"
                        
                        # Create item
                        item = Item(
                            id=item_id,
                            section_id=section_id,
                            text=template_item.text,
                            order=template_item.order
                        )
                        mock_items[section_id].append(item)
                        
                        # Add to Firestore if enabled
                        if USE_FIRESTORE:
                            item_data = {
                                "id": item_id,
                                "section_id": section_id,
                                "meeting_id": m.id,  # 検索効率化のため会議IDも保存
                                "text": template_item.text,
                                "order": template_item.order
                            }
                            await set_document('items', item_id, item_data)
        
        # Initialize recording status
        mock_rec_status[m.id] = "stopped"
        if USE_FIRESTORE:
            await set_document('recording_status', m.id, {"status": "stopped"})
    
    # Add to Firestore if enabled
    if USE_FIRESTORE:
        meeting_data = {
            "id": m.id,
            "title": m.title,
            "datetime": m.datetime,
            "template_id": m.template_id
        }
        await set_document('meetings', m.id, meeting_data)
        
    return m

@app.get("/meetings/{meeting_id}", response_model=Meeting, tags=["会議"], summary="会議取得", description="IDで特定の会議を取得する")
async def get_meeting(meeting_id: str, user: User = Depends(get_current_user)):
    # キャッシュからデータを取得
    cache_key = f"meeting:{meeting_id}"
    cached_meeting = await cache_manager.get(cache_key)
    
    if cached_meeting:
        return Meeting(**cached_meeting)
    
    # キャッシュになければモックデータまたはFirestoreから取得
    meeting_data = None
    
    # モックデータから検索
    for meet in mock_meetings:
        if meet.id == meeting_id:
            meeting_data = meet.dict()
            break
    
    # Firestoreから検索（モックデータになければ）
    if not meeting_data and USE_FIRESTORE:
        meeting_doc = await get_document('meetings', meeting_id)
        if meeting_doc:
            meeting_data = meeting_doc
    
    if not meeting_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # キャッシュに保存
    await cache_manager.set(cache_key, meeting_data, entity_type='meeting')
    
    return Meeting(**meeting_data)

# 会議データ全体（セクション、項目を含む）を一度に取得するエンドポイント
@app.get("/meetings/{meeting_id}/full", tags=["会議"], summary="会議データ全体取得", 
         description="会議データとそれに関連するセクション、項目を一度に取得する")
async def get_meeting_full(meeting_id: str, user: User = Depends(get_current_user)):
    """
    会議データとそれに関連するセクション、項目を一度に取得します。
    これにより、複数のAPIコールを減らし、フロントエンドの実装を簡素化できます。
    また、キャッシュを効率的に活用します。
    """
    # キャッシュからデータを取得
    cache_key = f"meeting_full:{meeting_id}"
    cached_data = await cache_manager.get(cache_key)
    
    if cached_data:
        return cached_data
    
    # 会議データを取得
    meeting_data = None
    for meet in mock_meetings:
        if meet.id == meeting_id:
            meeting_data = meet.dict()
            break
    
    if not meeting_data and USE_FIRESTORE:
        meeting_doc = await get_document('meetings', meeting_id)
        if meeting_doc:
            meeting_data = meeting_doc
    
    if not meeting_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # セクションデータを取得
    sections_data = []
    if meeting_id in mock_sections:
        sections_data = [section.dict() for section in mock_sections[meeting_id]]
    elif USE_FIRESTORE:
        sections = await query_collection('sections', 'meeting_id', meeting_id)
        if sections:
            sections_data = sections
            sections_data.sort(key=lambda x: x.get('order', 0))
    
    # 各セクションの項目を取得
    for section in sections_data:
        section_id = section['id']
        items_data = []
        
        if section_id in mock_items:
            items_data = [item.dict() for item in mock_items[section_id]]
        elif USE_FIRESTORE:
            items = await query_collection('items', 'section_id', section_id)
            if items:
                items_data = items
                items_data.sort(key=lambda x: x.get('order', 0))
        
        section['items'] = items_data
    
    # タスクデータを取得
    tasks_data = []
    if meeting_id in mock_tasks:
        tasks_data = [task.dict() for task in mock_tasks[meeting_id]]
    elif USE_FIRESTORE:
        tasks = await query_collection('tasks', 'meeting_id', meeting_id)
        if tasks:
            tasks_data = tasks
    
    # 録音状態を取得
    recording_status = "stopped"
    if meeting_id in mock_rec_status:
        recording_status = mock_rec_status[meeting_id]
    elif USE_FIRESTORE:
        rec_status = await get_document('recording_status', meeting_id)
        if rec_status:
            recording_status = rec_status.get('status', 'stopped')
    
    # 結果を組み立て
    result = {
        "meeting": meeting_data,
        "sections": sections_data,
        "tasks": tasks_data,
        "recording_status": recording_status
    }
    
    # キャッシュに保存（短めのTTL）
    await cache_manager.set(cache_key, result, ttl=30)  # 30秒間キャッシュ
    
    return result

@app.patch("/meetings/{meeting_id}", response_model=Meeting, tags=["会議"], summary="会議更新", description="既存の会議を更新する")
def update_meeting(meeting_id: str, m: Meeting, user: User = Depends(get_current_user)):
    for idx, meet in enumerate(mock_meetings):
        if meet.id == meeting_id:
            mock_meetings[idx] = m
            return m
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

# 会議データ全体を取得するヘルパー関数
async def get_meeting_full_data(meeting_id: str) -> Dict[str, Any]:
    """会議データとそれに関連するセクション、項目、タスクを取得する"""
    # 会議データを取得
    meeting_data = None
    for meet in mock_meetings:
        if meet.id == meeting_id:
            meeting_data = meet.dict()
            break
    
    if not meeting_data and USE_FIRESTORE:
        meeting_doc = await get_document('meetings', meeting_id)
        if meeting_doc:
            meeting_data = meeting_doc
    
    if not meeting_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # セクションデータを取得
    sections_data = []
    if meeting_id in mock_sections:
        sections_data = [section.dict() for section in mock_sections[meeting_id]]
    elif USE_FIRESTORE:
        sections = await query_collection('sections', 'meeting_id', meeting_id)
        if sections:
            sections_data = sections
            sections_data.sort(key=lambda x: x.get('order', 0))
    
    # 各セクションの項目を取得
    for section in sections_data:
        section_id = section['id']
        items_data = []
        
        if section_id in mock_items:
            items_data = [item.dict() for item in mock_items[section_id]]
        elif USE_FIRESTORE:
            items = await query_collection('items', 'section_id', section_id)
            if items:
                items_data = items
                items_data.sort(key=lambda x: x.get('order', 0))
        
        section['items'] = items_data
    
    # タスクデータを取得
    tasks_data = []
    if meeting_id in mock_tasks:
        tasks_data = [task.dict() for task in mock_tasks[meeting_id]]
    elif USE_FIRESTORE:
        tasks = await query_collection('tasks', 'meeting_id', meeting_id)
        if tasks:
            tasks_data = tasks
    
    # 録音状態を取得
    recording_status = "stopped"
    if meeting_id in mock_rec_status:
        recording_status = mock_rec_status[meeting_id]
    elif USE_FIRESTORE:
        rec_status = await get_document('recording_status', meeting_id)
        if rec_status:
            recording_status = rec_status.get('status', 'stopped')
    
    # 結果を組み立て
    result = {
        "meeting": meeting_data,
        "sections": sections_data,
        "tasks": tasks_data,
        "recording_status": recording_status
    }
    
    return result

# Firestoreに会議データを一括保存するヘルパー関数
async def save_meeting_data_to_firestore(meeting_id: str, meeting_data: Dict[str, Any]) -> None:
    """会議データをFirestoreに一括保存する"""
    if not USE_FIRESTORE:
        return
    
    try:
        # バッチ処理の開始
        batch = db.batch()
        
        # 会議データの保存
        meeting_ref = db.collection('meetings').document(meeting_id)
        batch.set(meeting_ref, meeting_data['meeting'])
        
        # セクションデータの保存
        for section in meeting_data['sections']:
            section_id = section['id']
            section_ref = db.collection('sections').document(section_id)
            
            # セクションから項目を取り出して別に保存
            items = section.pop('items', [])
            batch.set(section_ref, section)
            
            # 項目データの保存
            for item in items:
                item_id = item['id']
                item_ref = db.collection('items').document(item_id)
                batch.set(item_ref, item)
        
        # タスクデータの保存
        for task in meeting_data['tasks']:
            task_id = task['id']
            task_ref = db.collection('tasks').document(task_id)
            batch.set(task_ref, task)
        
        # 録音状態の保存
        rec_status_ref = db.collection('recording_status').document(meeting_id)
        batch.set(rec_status_ref, {"status": meeting_data['recording_status']})
        
        # バッチ処理の実行
        batch.commit()
        print(f"Meeting data saved to Firestore: {meeting_id}")
        
    except Exception as e:
        print(f"Error saving meeting data to Firestore: {e}")
        # エラーが発生しても処理を続行（ログに記録）

# ----- Meeting Status Endpoints -----
@app.post("/meetings/{meeting_id}/start", tags=["会議"], summary="会議開始", description="会議を開始状態に設定する")
async def start_meeting(meeting_id: str, user: User = Depends(get_current_user)):
    """会議を開始状態に設定し、ステータスを 'in_progress' に変更します"""
    # モックデータの更新
    meeting_found = False
    for meet in mock_meetings:
        if meet.id == meeting_id:
            meeting_found = True
            meet.status = "in_progress"
            meeting_data = meet.dict()
            break
    
    # Firestoreの更新
    if not meeting_found and USE_FIRESTORE:
        meeting_data = await get_document('meetings', meeting_id)
        if meeting_data:
            meeting_found = True
            meeting_data['status'] = "in_progress"
            await update_document('meetings', meeting_id, meeting_data)
    
    if not meeting_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # キャッシュの更新
    await cache_manager.delete(f"meeting:{meeting_id}")
    await cache_manager.delete(f"meeting_full:{meeting_id}")
    
    # WebSocketで会議開始の会議アシスト情報を送信
    await websocket_manager.send_meeting_assist(
        meeting_id, 
        "meeting_start", 
        "会議が開始されました。最初のセクションから始めましょう。"
    )
    
    return {"status": "in_progress", "message": "会議が開始されました"}

@app.post("/meetings/{meeting_id}/complete", tags=["会議"], summary="会議完了", description="会議を完了状態に設定し、すべてのデータをFirestoreに保存する")
async def complete_meeting(meeting_id: str, user: User = Depends(get_current_user)):
    """
    会議を完了状態に設定し、すべてのデータをFirestoreに保存します。
    このエンドポイントは、キャッシュにのみ存在する可能性のあるすべての変更を
    Firestoreに確実に保存するために使用します。
    """
    # モックデータの更新
    meeting_found = False
    meeting_data = None
    for meet in mock_meetings:
        if meet.id == meeting_id:
            meeting_found = True
            meet.status = "completed"
            meeting_data = meet.dict()
            break
    
    if not meeting_found:
        if USE_FIRESTORE:
            meeting_data = await get_document('meetings', meeting_id)
            if meeting_data:
                meeting_found = True
                meeting_data['status'] = "completed"
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # 会議の完全なデータを取得（セクション、項目を含む）
    full_data = await get_meeting_full_data(meeting_id)
    
    # Firestoreに保存
    if USE_FIRESTORE:
        # トランザクションまたはバッチ処理で一括保存
        await save_meeting_data_to_firestore(meeting_id, full_data)
    
    # キャッシュを更新
    await cache_manager.delete(f"meeting:{meeting_id}")
    await cache_manager.delete(f"meeting_full:{meeting_id}")
    
    # WebSocketで会議完了の会議アシスト情報を送信
    await websocket_manager.send_meeting_assist(
        meeting_id, 
        "meeting_complete", 
        "会議が完了しました。議事録の内容を確認し、アクションアイテムを整理しましょう。"
    )
    
    return {
        "status": "completed", 
        "message": "会議が完了し、すべてのデータが保存されました",
        "meeting_id": meeting_id
    }

@app.delete("/meetings/{meeting_id}", tags=["会議"], summary="会議削除", description="IDで会議を削除する（関連するセクション、項目、タスクも削除）")
async def delete_meeting(meeting_id: str, user: User = Depends(get_current_user)):
    # Check if meeting exists
    meeting_exists = False
    for meet in mock_meetings:
        if meet.id == meeting_id:
            meeting_exists = True
            break
            
    if not meeting_exists and not USE_FIRESTORE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        
    # Delete meeting and all related data in a transaction
    await delete_meeting_with_related_data(meeting_id)
    return {"detail": "deleted"}

# ----- Recording Endpoints -----
@app.post("/meetings/{meeting_id}/recording/start", tags=["録音"], summary="録音開始", description="特定の会議の録音を開始し、会議ステータスを更新する")
async def start_recording(meeting_id: str, user: User = Depends(get_current_user)):
    # 録音状態を更新
    mock_rec_status[meeting_id] = "recording"
    
    # 会議ステータスも 'in_progress' に更新
    meeting_found = False
    for meet in mock_meetings:
        if meet.id == meeting_id:
            meeting_found = True
            if meet.status == "scheduled":
                meet.status = "in_progress"
            break
    
    # Firestoreの更新
    if USE_FIRESTORE:
        # 録音状態を更新
        await set_document('recording_status', meeting_id, {"status": "recording"})
        
        # 会議ステータスも更新
        if not meeting_found:
            meeting_data = await get_document('meetings', meeting_id)
            if meeting_data and meeting_data.get('status') == "scheduled":
                meeting_data['status'] = "in_progress"
                await update_document('meetings', meeting_id, meeting_data)
    
    # キャッシュを更新
    await cache_manager.delete(f"meeting:{meeting_id}")
    await cache_manager.delete(f"meeting_full:{meeting_id}")
    
    # WebSocketで録音開始の会議アシスト情報を送信
    await websocket_manager.send_meeting_assist(
        meeting_id, 
        "recording_start", 
        "録音が開始されました。会議を進めましょう。"
    )
    
    return {"status": "recording", "meeting_status": "in_progress"}

@app.post("/meetings/{meeting_id}/recording/stop", tags=["録音"], summary="録音停止", description="特定の会議の録音を停止する")
async def stop_recording(meeting_id: str, user: User = Depends(get_current_user)):
    # 録音状態を更新
    mock_rec_status[meeting_id] = "stopped"
    
    # Firestoreの更新
    if USE_FIRESTORE:
        await set_document('recording_status', meeting_id, {"status": "stopped"})
    
    # キャッシュを更新
    await cache_manager.delete(f"meeting:{meeting_id}")
    await cache_manager.delete(f"meeting_full:{meeting_id}")
    
    return {
        "status": "stopped", 
        "message": "録音が停止されました。会議を完了するには /meetings/{meeting_id}/complete を呼び出してください。"
    }

@app.get("/meetings/{meeting_id}/recording/status", response_model=RecordingStatus, tags=["録音"], summary="録音状態取得", description="特定の会議の現在の録音状態を取得する")
def recording_status(meeting_id: str, user: User = Depends(get_current_user)):
    return RecordingStatus(status=mock_rec_status.get(meeting_id, "stopped"))

# ----- Sections & Items Endpoints -----
@app.get("/meetings/{meeting_id}/sections", response_model=list[Section], tags=["セクション"], summary="セクション一覧", description="特定の会議の全てのセクションを取得する")
async def list_sections(meeting_id: str, user: User = Depends(get_current_user)):
    # キャッシュからデータを取得
    cache_key = f"sections:{meeting_id}"
    cached_sections = await cache_manager.get(cache_key)
    
    if cached_sections:
        return [Section(**section) for section in cached_sections]
    
    # キャッシュになければモックデータまたはFirestoreから取得
    sections_data = []
    
    # モックデータから検索
    if meeting_id in mock_sections:
        sections_data = [section.dict() for section in mock_sections[meeting_id]]
    
    # Firestoreから検索（モックデータになければ）
    if not sections_data and USE_FIRESTORE:
        sections = await query_collection('sections', 'meeting_id', meeting_id)
        if sections:
            sections_data = sections
            # セクションを順序でソート
            sections_data.sort(key=lambda x: x.get('order', 0))
    
    # キャッシュに保存
    if sections_data:
        await cache_manager.set(cache_key, sections_data, entity_type='section')
        
        # 会議データとの依存関係を設定
        meeting_key = f"meeting:{meeting_id}"
        for section in sections_data:
            section_key = f"section:{section['id']}"
            await cache_manager.add_dependency(meeting_key, section_key)
    
    return [Section(**section) for section in sections_data]

@app.patch("/meetings/{meeting_id}/sections/{section_id}", response_model=Section, tags=["セクション"], summary="セクション更新", description="会議内の特定のセクションを更新する（順序の一貫性を保持）")
async def update_section(meeting_id: str, section_id: str, sec: Section, user: User = Depends(get_current_user)):
    # Check if section exists in mock data
    section_exists = False
    for s in mock_sections.get(meeting_id, []):
        if s.id == section_id:
            section_exists = True
            old_order = s.order
            
            # Update section data
            s.title = sec.title
            s.status = sec.status  # ステータスも更新
            
            # If order has changed, ensure consistency
            if s.order != sec.order:
                await update_section_order(meeting_id, section_id, sec.order)
            else:
                s.order = sec.order
                
            return s
            
    # If we're using Firestore and section wasn't found in mock data
    if USE_FIRESTORE:
        # Get section from Firestore
        section_data = await get_document('sections', section_id)
        if section_data and section_data.get('meeting_id') == meeting_id:
            # Update section in Firestore
            section_data['title'] = sec.title
            section_data['status'] = sec.status  # ステータスも更新
            
            # If order has changed, ensure consistency
            if section_data.get('order') != sec.order:
                await update_section_order(meeting_id, section_id, sec.order)
            else:
                section_data['order'] = sec.order
                await update_document('sections', section_id, section_data)
                
            # Return updated section
            return Section(
                id=section_id, 
                title=sec.title, 
                order=sec.order, 
                status=sec.status
            )
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

# セクションの会議アシスト情報を取得するエンドポイント
@app.get("/meetings/{meeting_id}/sections/{section_id}/assist", tags=["会議アシスト"], summary="セクション会議アシスト取得", description="会議内の特定のセクションの会議アシスト情報を取得する")
async def get_section_assist(meeting_id: str, section_id: str, user: User = Depends(get_current_user)):
    """
    特定のセクションの会議アシスト情報を取得します。
    LLMによって生成された話の切り出し方や重要な質問などが含まれます。
    
    注意: このエンドポイントは、WebSocketを使用していない場合や、追加の会議アシスト情報が必要な場合に呼び出してください。
    WebSocketを使用している場合は、セクションのステータス変更イベントとともに会議アシスト情報も送信されるため、
    通常はこのエンドポイントを明示的に呼び出す必要はありません。
    """
    # キャッシュからデータを取得
    cache_key = f"section_assist:{section_id}"
    cached_assist = await cache_manager.get(cache_key)
    
    if cached_assist:
        return MeetingAssist(**cached_assist)
    
    # セクションデータを取得
    section_found = False
    section_title = ""
    
    # モックデータから検索
    for s in mock_sections.get(meeting_id, []):
        if s.id == section_id:
            section_found = True
            section_title = s.title
            break
    
    # Firestoreから検索（モックデータになければ）
    if not section_found and USE_FIRESTORE:
        section_data = await get_document('sections', section_id)
        if section_data and section_data.get('meeting_id') == meeting_id:
            section_found = True
            section_title = section_data.get('title', '')
    
    if not section_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="指定されたセクションが見つかりません")
    
    # 会議アシスト情報を生成
    assist_info = await generate_meeting_assist(meeting_id, section_id, section_title)
    
    # キャッシュに保存
    await cache_manager.set(cache_key, assist_info.dict(), ttl=300)  # 5分間キャッシュ
    
    return assist_info

@app.patch("/meetings/{meeting_id}/sections/{section_id}/status", tags=["セクション"], summary="セクションステータス更新", description="会議内の特定のセクションのステータスを更新する")
async def update_section_status(
    meeting_id: str, 
    section_id: str, 
    status: str = Body(..., description="セクションの新しいステータス (not_started, in_progress, completed)"),
    user: User = Depends(get_current_user)
):
    """
    セクションのステータスのみを更新します。
    - not_started: まだ話し合われていない
    - in_progress: 現在話し合い中
    - completed: 話し合いが完了した
    
    注意: このエンドポイントはステータスの更新のみを行います。
    ステータスの更新後、WebSocketを通じてステータス変更イベントとともにプロンプト情報も送信されます。
    WebSocketを使用していない場合は、別途 GET /meetings/{meeting_id}/sections/{section_id}/prompts を呼び出してプロンプト情報を取得することもできます。
    """
    # ステータス値の検証
    if status not in ["not_started", "in_progress", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無効なステータスです。'not_started', 'in_progress', 'completed' のいずれかを指定してください。"
        )
    
    # モックデータの更新
    section_found = False
    updated_section = None
    
    for s in mock_sections.get(meeting_id, []):
        if s.id == section_id:
            section_found = True
            s.status = status
            updated_section = s
            break
    
    # Firestoreの更新
    if not section_found and USE_FIRESTORE:
        section_data = await get_document('sections', section_id)
        if section_data and section_data.get('meeting_id') == meeting_id:
            section_found = True
            section_data['status'] = status
            await update_document('sections', section_id, section_data)
            
            # 更新されたセクションを返すためのオブジェクトを作成
            updated_section = Section(
                id=section_id,
                title=section_data.get('title', ''),
                order=section_data.get('order', 0),
                status=status
            )
    
    if not section_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="指定されたセクションが見つかりません")
    
    # キャッシュを更新
    await cache_manager.delete(f"section:{section_id}")
    await cache_manager.delete(f"sections:{meeting_id}")
    await cache_manager.delete(f"meeting_full:{meeting_id}")
    
    # WebSocketでステータス変更と会議アシスト情報を通知
    await websocket_manager.send_section_assist(meeting_id, section_id, status)
    
    return updated_section

@app.get("/meetings/{meeting_id}/sections/status", tags=["セクション"], summary="セクションステータス一覧", description="特定の会議の全てのセクションのステータスを取得する")
async def list_section_statuses(meeting_id: str, user: User = Depends(get_current_user)):
    """
    特定の会議の全てのセクションのステータスを取得します。
    軽量な応答を返すため、セクションのIDとステータスのみを含みます。
    """
    # キャッシュからデータを取得
    cache_key = f"section_statuses:{meeting_id}"
    cached_statuses = await cache_manager.get(cache_key)
    
    if cached_statuses:
        return cached_statuses
    
    # セクションデータを取得
    section_statuses = []
    
    # モックデータから検索
    if meeting_id in mock_sections:
        for section in mock_sections[meeting_id]:
            section_statuses.append({
                "id": section.id,
                "title": section.title,
                "order": section.order,
                "status": section.status
            })
    
    # Firestoreから検索（モックデータになければ）
    elif USE_FIRESTORE:
        sections = await query_collection('sections', 'meeting_id', meeting_id)
        if sections:
            for section in sections:
                section_statuses.append({
                    "id": section.get('id'),
                    "title": section.get('title'),
                    "order": section.get('order', 0),
                    "status": section.get('status', 'not_started')
                })
            
            # セクションを順序でソート
            section_statuses.sort(key=lambda x: x.get('order', 0))
    
    # キャッシュに保存（短めのTTL）
    if section_statuses:
        await cache_manager.set(cache_key, section_statuses, ttl=15)  # 15秒間キャッシュ
    
    return section_statuses

@app.get("/meetings/{meeting_id}/sections/{section_id}/items", response_model=list[Item], tags=["項目"], summary="項目一覧", description="特定のセクションの全ての項目を取得する")
async def list_items(meeting_id: str, section_id: str, user: User = Depends(get_current_user)):
    # キャッシュからデータを取得
    cache_key = f"items:{section_id}"
    cached_items = await cache_manager.get(cache_key)
    
    if cached_items:
        return [Item(**item) for item in cached_items]
    
    # キャッシュになければモックデータまたはFirestoreから取得
    items_data = []
    
    # モックデータから検索
    if section_id in mock_items:
        items_data = [item.dict() for item in mock_items[section_id]]
    
    # Firestoreから検索（モックデータになければ）
    if not items_data and USE_FIRESTORE:
        items = await query_collection('items', 'section_id', section_id)
        if items:
            items_data = items
            # 項目を順序でソート
            items_data.sort(key=lambda x: x.get('order', 0))
    
    # キャッシュに保存
    if items_data:
        await cache_manager.set(cache_key, items_data, entity_type='item')
        
        # セクションデータとの依存関係を設定
        section_key = f"section:{section_id}"
        for item in items_data:
            item_key = f"item:{item['id']}"
            await cache_manager.add_dependency(section_key, item_key)
    
    return [Item(**item) for item in items_data]

@app.post("/meetings/{meeting_id}/sections/{section_id}/items", response_model=Item, tags=["項目"], summary="項目追加", description="セクションに新しい項目を追加する")
async def add_item(meeting_id: str, section_id: str, it: Item, user: User = Depends(get_current_user)):
    # モックデータに追加
    mock_items.setdefault(section_id, []).append(it)
    
    # Firestoreに追加
    if USE_FIRESTORE:
        item_data = it.dict()
        item_data['meeting_id'] = meeting_id  # 検索効率化のため会議IDも保存
        await set_document('items', it.id, item_data)
    
    # キャッシュを無効化
    await cache_manager.delete(f"items:{section_id}")
    
    # 依存関係を更新
    item_key = f"item:{it.id}"
    section_key = f"section:{section_id}"
    await cache_manager.add_dependency(section_key, item_key)
    
    return it

@app.patch("/meetings/{meeting_id}/sections/{section_id}/items/{item_id}", response_model=Item, tags=["項目"], summary="項目更新", description="セクション内の既存の項目を更新する")
async def update_item(meeting_id: str, section_id: str, item_id: str, it: Item, user: User = Depends(get_current_user)):
    # モックデータを更新
    item_found = False
    items = mock_items.get(section_id, [])
    for existing in items:
        if existing.id == item_id:
            item_found = True
            existing.order = it.order
            existing.text = it.text
            updated_item = existing
            break
    
    # Firestoreを更新
    if not item_found and USE_FIRESTORE:
        item_data = await get_document('items', item_id)
        if item_data and item_data.get('section_id') == section_id:
            item_found = True
            item_data['order'] = it.order
            item_data['text'] = it.text
            await update_document('items', item_id, item_data)
            updated_item = Item(
                id=item_id,
                section_id=section_id,
                text=it.text,
                order=it.order
            )
    
    if not item_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # キャッシュを更新
    item_key = f"item:{item_id}"
    item_data = updated_item.dict()
    await cache_manager.set(item_key, item_data, entity_type='item')
    
    # 関連キャッシュを無効化
    await cache_manager.delete(f"items:{section_id}")
    
    return updated_item

@app.delete("/meetings/{meeting_id}/sections/{section_id}/items/{item_id}", tags=["項目"], summary="項目削除", description="セクションから項目を削除する")
async def delete_item(meeting_id: str, section_id: str, item_id: str, user: User = Depends(get_current_user)):
    # Check if item exists in mock data
    item_exists = False
    item_data = None
    
    items = mock_items.get(section_id, [])
    for existing in items:
        if existing.id == item_id:
            item_exists = True
            item_data = existing
            items.remove(existing)
            return {"detail": "deleted"}
            
    # If we're using Firestore and item wasn't found in mock data
    if USE_FIRESTORE:
        # Delete item from Firestore
        item_data = await get_document('items', item_id)
        if item_data and item_data.get('section_id') == section_id:
            await delete_document('items', item_id)
            return {"detail": "deleted"}
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.post("/meetings/{meeting_id}/sections/{section_id}/items/{item_id}/move", response_model=Item, tags=["項目"], summary="項目移動", description="項目を別のセクションに移動する")
async def move_item(meeting_id: str, section_id: str, item_id: str, target_section_id: str, user: User = Depends(get_current_user)):
    """
    項目を別のセクションに移動します。
    - section_id: 現在の項目が属するセクションID
    - item_id: 移動する項目のID
    - target_section_id: 移動先のセクションID (クエリパラメータ)
    """
    # Validate target section exists
    target_section_exists = False
    
    # Check in mock data
    if meeting_id in mock_sections:
        for s in mock_sections[meeting_id]:
            if s.id == target_section_id:
                target_section_exists = True
                break
                
    # Check in Firestore if using it
    if not target_section_exists and USE_FIRESTORE:
        target_section = await get_document('sections', target_section_id)
        if target_section and target_section.get('meeting_id') == meeting_id:
            target_section_exists = True
            
    if not target_section_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target section not found")
    
    # Find the item to move
    item_found = False
    item_data = None
    
    # Check in mock data
    if section_id in mock_items:
        for item in mock_items[section_id]:
            if item.id == item_id:
                item_found = True
                item_data = item
                # Remove from current section
                mock_items[section_id].remove(item)
                # Add to target section with same properties
                if target_section_id not in mock_items:
                    mock_items[target_section_id] = []
                # Update section_id
                new_item = Item(
                    id=item.id,
                    section_id=target_section_id,
                    text=item.text,
                    order=item.order
                )
                mock_items[target_section_id].append(new_item)
                return new_item
    
    # Check in Firestore if using it
    if not item_found and USE_FIRESTORE:
        item = await get_document('items', item_id)
        if item and item.get('section_id') == section_id:
            item_found = True
            # Update section_id in Firestore
            item['section_id'] = target_section_id
            await update_document('items', item_id, item)
            return Item(
                id=item_id,
                section_id=target_section_id,
                text=item['text'],
                order=item['order']
            )
    
    if not item_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

# ----- Task Endpoints -----
@app.get("/meetings/{meeting_id}/tasks", response_model=list[Task], tags=["タスク"], summary="タスク一覧", description="特定の会議の全てのタスクを取得する")
def list_tasks(meeting_id: str, user: User = Depends(get_current_user)):
    return mock_tasks.get(meeting_id, [])

@app.post("/meetings/{meeting_id}/tasks", response_model=Task, tags=["タスク"], summary="タスク追加", description="会議に新しいタスクを追加する")
def add_task(meeting_id: str, t: Task, user: User = Depends(get_current_user)):
    mock_tasks.setdefault(meeting_id, []).append(t)
    return t

@app.patch("/meetings/{meeting_id}/tasks/{task_id}", response_model=Task, tags=["タスク"], summary="タスク更新", description="会議内の既存のタスクを更新する")
def update_task(meeting_id: str, task_id: str, t: Task, user: User = Depends(get_current_user)):
    tasks = mock_tasks.get(meeting_id, [])
    for idx, existing in enumerate(tasks):
        if existing.id == task_id:
            tasks[idx] = t
            return t
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.delete("/meetings/{meeting_id}/tasks/{task_id}", tags=["タスク"], summary="タスク削除", description="会議からタスクを削除する")
def delete_task(meeting_id: str, task_id: str, user: User = Depends(get_current_user)):
    tasks = mock_tasks.get(meeting_id, [])
    for existing in tasks:
        if existing.id == task_id:
            tasks.remove(existing)
            return {"detail": "deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

# ----- Meeting Assist Endpoints -----
@app.post("/meetings/{meeting_id}/assist/send", tags=["会議アシスト"], summary="会議アシスト送信", description="WebSocketを通じて会議参加者に会議アシスト情報を送信する")
async def send_meeting_assist(
    meeting_id: str, 
    assist_type: str = Body(..., description="アシストタイプ (meeting_start, section_change, meeting_complete, general)"),
    custom_message: str = Body(None, description="カスタムメッセージ"),
    user: User = Depends(get_current_user)
):
    """
    WebSocketを通じて会議参加者に会議アシスト情報を送信します。
    
    このエンドポイントは、会議の進行をサポートするために、
    LLMによって生成された会議アシスト情報をバックエンドからフロントエンドに送信します。
    """
    # 会議の存在確認
    meeting_exists = False
    for meet in mock_meetings:
        if meet.id == meeting_id:
            meeting_exists = True
            break
    
    if not meeting_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="指定された会議が見つかりません")
    
    # アシストタイプの検証
    valid_assist_types = ["meeting_start", "section_change", "meeting_complete", "general"]
    if assist_type not in valid_assist_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"無効なアシストタイプです。利用可能なタイプ: {valid_assist_types}"
        )
    
    # WebSocketで会議アシスト情報を送信
    await websocket_manager.send_meeting_assist(meeting_id, assist_type, custom_message)
    
    return {
        "message": "会議アシスト情報が送信されました",
        "meeting_id": meeting_id,
        "assist_type": assist_type,
        "custom_message": custom_message
    }

@app.post("/meetings/{meeting_id}/sections/{section_id}/assist/send", tags=["会議アシスト"], summary="セクション会議アシスト送信", description="WebSocketを通じて特定のセクションの会議アシスト情報を送信する")
async def send_section_assist_info(
    meeting_id: str,
    section_id: str,
    status: str = Body(..., description="セクションステータス (not_started, in_progress, completed)"),
    user: User = Depends(get_current_user)
):
    """
    WebSocketを通じて特定のセクションの会議アシスト情報を送信します。
    
    セクションのステータス変更時に、LLMによって生成された適切な会議アシスト情報を
    バックエンドからフロントエンドに送信します。
    """
    # セクションの存在確認
    section_exists = False
    for s in mock_sections.get(meeting_id, []):
        if s.id == section_id:
            section_exists = True
            break
    
    if not section_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="指定されたセクションが見つかりません")
    
    # ステータスの検証
    if status not in ["not_started", "in_progress", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無効なステータスです。'not_started', 'in_progress', 'completed' のいずれかを指定してください。"
        )
    
    # WebSocketでセクション会議アシスト情報を送信
    await websocket_manager.send_section_assist(meeting_id, section_id, status)
    
    return {
        "message": "セクション会議アシスト情報が送信されました",
        "meeting_id": meeting_id,
        "section_id": section_id,
        "status": status
    }

@app.post("/meetings/{meeting_id}/assist/reminder", tags=["会議アシスト"], summary="会議アシストリマインダー送信", description="WebSocketを通じて会議アシスト機能のリマインダーを送信する")
async def send_assist_reminder_endpoint(
    meeting_id: str,
    section_id: str = Body(None, description="対象セクションID（オプション）"),
    user: User = Depends(get_current_user)
):
    """
    WebSocketを通じて会議アシスト機能のリマインダーを送信します。
    
    時間管理や議論の焦点化をサポートするためのLLM生成アシスト情報を
    バックエンドからフロントエンドに送信します。
    """
    # 会議の存在確認
    meeting_exists = False
    for meet in mock_meetings:
        if meet.id == meeting_id:
            meeting_exists = True
            break
    
    if not meeting_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="指定された会議が見つかりません")
    
    # WebSocketで会議アシストリマインダーを送信
    await websocket_manager.send_assist_reminder(meeting_id, section_id)
    
    return {
        "message": "会議アシストリマインダーが送信されました",
        "meeting_id": meeting_id,
        "section_id": section_id
    }

# ----- Live WebSocket -----
@app.websocket("/meetings/{meeting_id}/live")
async def websocket_live(websocket: WebSocket, meeting_id: str):
    """
    会議中のリアルタイム更新のためのWebSocket接続を確立します。
    
    このエンドポイントは会議のセクションと項目に関するリアルタイム更新を送信します。
    クライアントはこれを使用して、更新をリアルタイムで表示することができます。
    
    注意: WebSocketを通じてバックエンドからフロントエンドへ会議アシスト情報が送信されます。
    セクションのステータス変更イベント（type: "section.status_changed"）には、meeting_assist フィールドが含まれており、
    これにはLLMによって生成された discussion_starter（話の切り出し方）、key_questions（重要な質問）、
    conclusion_guide（まとめの言葉）、time_management（時間管理）、participation_tips（参加促進のヒント）が含まれています。
    フロントエンドはこの情報を使用して、会議の進行をサポートできます。
    
    フロントエンドから会議アシスト情報は送信されません。バックエンドからフロントエンドへの一方向通信です。
    """
    # WebSocketマネージャーに接続を登録
    await websocket_manager.connect(websocket, meeting_id)
    
    try:
        # 接続確立の通知
        await websocket.send_json({
            "type": "connection.established",
            "meetingId": meeting_id,
            "message": "WebSocket接続が確立されました。バックエンドからリアルタイム更新を受信します。"
        })
        
        # 定期的に会議アシスト情報を送信するデモ
        seq = 1
        while True:
            # 実際の実装では、ここで会議の状態変化やセクションの更新を監視し、
            # 必要に応じて会議アシスト情報を送信します
            
            if seq == 1:
                # 会議開始時の会議アシスト送信
                assist_info = await generate_meeting_assist(meeting_id, "general", "会議開始")
                event = {
                    "type": "meeting.started",
                    "meetingId": meeting_id,
                    "meeting_assist": assist_info.dict(),
                    "message": "会議が開始されました。最初のセクションに進みましょう。",
                    "sequenceNumber": seq
                }
                
            elif seq == 2:
                # セクションステータス変更時の会議アシスト送信
                section_title = "議題"
                assist_info = await generate_meeting_assist(meeting_id, "s1", section_title)
                
                event = {
                    "type": "section.status_changed", 
                    "sectionId": "s1", 
                    "status": "in_progress", 
                    "meeting_assist": assist_info.dict(),
                    "message": "セクション「議題」が開始されました。",
                    "sequenceNumber": seq
                }
                
                # 実際のデータも更新
                if meeting_id in mock_sections:
                    for s in mock_sections[meeting_id]:
                        if s.id == "s1":
                            s.status = "in_progress"
                            break
                
            elif seq == 3:
                # 次のセクションへの移行時の会議アシスト
                assist_info = await generate_meeting_assist(meeting_id, "s2", "決定事項")
                event = {
                    "type": "section.transition",
                    "fromSectionId": "s1",
                    "toSectionId": "s2",
                    "meeting_assist": assist_info.dict(),
                    "message": "次のセクション「決定事項」に移ります。",
                    "sequenceNumber": seq
                }
                
                # セクションステータスを更新
                if meeting_id in mock_sections:
                    for s in mock_sections[meeting_id]:
                        if s.id == "s1":
                            s.status = "completed"
                        elif s.id == "s2":
                            s.status = "in_progress"
                
            elif seq == 4:
                # 新しい項目追加時の会議アシスト
                assist_info = await generate_meeting_assist(meeting_id, "s2", "決定事項")
                event = {
                    "type": "item.added",
                    "sectionId": "s2",
                    "itemId": f"i{seq}",
                    "itemText": "新しい決定事項",
                    "meeting_assist": assist_info.dict(),
                    "sequenceNumber": seq
                }
                
            elif seq == 5:
                # 会議終了時の会議アシスト
                assist_info = await generate_meeting_assist(meeting_id, "general", "会議まとめ")
                event = {
                    "type": "meeting.summary",
                    "meetingId": meeting_id,
                    "meeting_assist": assist_info.dict(),
                    "message": "会議の内容をまとめましょう。",
                    "sequenceNumber": seq
                }
                
            else:
                # 継続的な会議アシスト
                current_section = "s2"  # 現在のセクション
                assist_info = await generate_meeting_assist(meeting_id, current_section, "決定事項")
                event = {
                    "type": "meeting.assist",
                    "sectionId": current_section,
                    "meeting_assist": assist_info.dict(),
                    "sequenceNumber": seq
                }
            
            # イベントをクライアントに送信
            await websocket.send_json(event)
            seq += 1
            
            # 実際の実装では、イベント駆動で会議アシスト情報を送信するため、
            # この sleep は不要になります
            await asyncio.sleep(3)
            
    except WebSocketDisconnect:
        # 接続が切断された場合
        websocket_manager.disconnect(websocket, meeting_id)
        print(f"WebSocket disconnected for meeting {meeting_id}")
    except Exception as e:
        # その他のエラーが発生した場合
        print(f"WebSocket error for meeting {meeting_id}: {e}")
        websocket_manager.disconnect(websocket, meeting_id)

# キャッシュ無効化ヘルパー関数
async def invalidate_meeting_cache(meeting_id: str):
    """会議関連の全てのキャッシュを無効化"""
    # 個別のキャッシュを無効化
    await cache_manager.delete(f"meeting:{meeting_id}")
    await cache_manager.delete(f"meeting_full:{meeting_id}")
    
    # 依存関係も無効化
    await cache_manager.invalidate_with_dependencies(f"meeting:{meeting_id}")

async def invalidate_section_cache(meeting_id: str, section_id: str):
    """セクション関連のキャッシュを無効化"""
    await cache_manager.delete(f"section:{section_id}")
    await cache_manager.delete(f"sections:{meeting_id}")
    await cache_manager.delete(f"section_statuses:{meeting_id}")  # セクションステータスのキャッシュも無効化
    
    # セクションリストのキャッシュも無効化
    await cache_manager.delete(f"meeting_full:{meeting_id}")

async def invalidate_item_cache(section_id: str, item_id: str, meeting_id: str):
    """項目関連のキャッシュを無効化"""
    await cache_manager.delete(f"item:{item_id}")
    await cache_manager.delete(f"items:{section_id}")
    
    # 親のキャッシュも無効化
    await cache_manager.delete(f"section:{section_id}")
    await cache_manager.delete(f"sections:{meeting_id}")
    await cache_manager.delete(f"meeting_full:{meeting_id}")
