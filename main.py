from fastapi import FastAPI, WebSocket, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

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

class Template(BaseModel):
    """Meeting template with predefined sections"""
    id: str
    name: str
    items: list[str]

class Meeting(BaseModel):
    """Meeting information"""
    id: str
    title: str
    datetime: str
    template_id: str | None = None

class RecordingStatus(BaseModel):
    """Status of meeting recording"""
    status: str = "stopped"  # recording | stopped | processing

class Section(BaseModel):
    """Meeting section (e.g., agenda, decisions, action items)"""
    id: str
    title: str
    order: int

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
mock_templates = [Template(id="t1", name="Default", items=["議題", "決定事項", "アクションアイテム"])]
mock_meetings = [Meeting(id="m1", title="Mock Meeting", datetime="2025-06-22T16:00:00", template_id="t1")]
mock_sections = {
    "m1": [
        Section(id="s1", title="議題", order=1),
        Section(id="s2", title="決定事項", order=2),
    ]
}
mock_items = {
    "s1": [Item(id="i1", section_id="s1", text="ダミー項目1", order=1)],
    "s2": [Item(id="i2", section_id="s2", text="ダミー項目2", order=1)],
}
mock_tasks = {
    "m1": [Task(id="task1", text="フォローアップメール送信", assignee="Bob", due_date="2025-06-23", status="open")]
}
mock_rec_status = {"m1": "stopped"}

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

@app.post("/templates", response_model=Template, tags=["テンプレート"], summary="テンプレート作成", description="新しい会議テンプレートを作成する")
def create_template(t: Template, user: User = Depends(get_current_user)):
    mock_templates.append(t)
    return t

@app.get("/templates/{template_id}", response_model=Template, tags=["テンプレート"], summary="テンプレート取得", description="IDで特定のテンプレートを取得する")
def get_template(template_id: str, user: User = Depends(get_current_user)):
    for tpl in mock_templates:
        if tpl.id == template_id:
            return tpl
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.patch("/templates/{template_id}", response_model=Template, tags=["テンプレート"], summary="テンプレート更新", description="既存のテンプレートを更新する")
def update_template(template_id: str, t: Template, user: User = Depends(get_current_user)):
    for idx, tpl in enumerate(mock_templates):
        if tpl.id == template_id:
            mock_templates[idx] = t
            return t
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.delete("/templates/{template_id}", tags=["テンプレート"], summary="テンプレート削除", description="IDでテンプレートを削除する")
def delete_template(template_id: str, user: User = Depends(get_current_user)):
    for tpl in mock_templates:
        if tpl.id == template_id:
            mock_templates.remove(tpl)
            return {"detail": "deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

# ----- Meeting Endpoints -----
@app.get("/meetings", response_model=list[Meeting], tags=["会議"], summary="会議一覧", description="利用可能な全ての会議を取得する")
def list_meetings(user: User = Depends(get_current_user)):
    return mock_meetings

@app.post("/meetings", response_model=Meeting, tags=["会議"], summary="会議作成", description="新しい会議を作成する")
def create_meeting(m: Meeting, user: User = Depends(get_current_user)):
    mock_meetings.append(m)
    return m

@app.get("/meetings/{meeting_id}", response_model=Meeting, tags=["会議"], summary="会議取得", description="IDで特定の会議を取得する")
def get_meeting(meeting_id: str, user: User = Depends(get_current_user)):
    for meet in mock_meetings:
        if meet.id == meeting_id:
            return meet
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.patch("/meetings/{meeting_id}", response_model=Meeting, tags=["会議"], summary="会議更新", description="既存の会議を更新する")
def update_meeting(meeting_id: str, m: Meeting, user: User = Depends(get_current_user)):
    for idx, meet in enumerate(mock_meetings):
        if meet.id == meeting_id:
            mock_meetings[idx] = m
            return m
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.delete("/meetings/{meeting_id}", tags=["会議"], summary="会議削除", description="IDで会議を削除する")
def delete_meeting(meeting_id: str, user: User = Depends(get_current_user)):
    for meet in mock_meetings:
        if meet.id == meeting_id:
            mock_meetings.remove(meet)
            return {"detail": "deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

# ----- Recording Endpoints -----
@app.post("/meetings/{meeting_id}/recording/start", tags=["録音"], summary="録音開始", description="特定の会議の録音を開始する")
def start_recording(meeting_id: str, user: User = Depends(get_current_user)):
    mock_rec_status[meeting_id] = "recording"
    return {"status": "recording"}

@app.post("/meetings/{meeting_id}/recording/stop", tags=["録音"], summary="録音停止", description="特定の会議の録音を停止する")
def stop_recording(meeting_id: str, user: User = Depends(get_current_user)):
    mock_rec_status[meeting_id] = "stopped"
    return {"status": "stopped"}

@app.get("/meetings/{meeting_id}/recording/status", response_model=RecordingStatus, tags=["録音"], summary="録音状態取得", description="特定の会議の現在の録音状態を取得する")
def recording_status(meeting_id: str, user: User = Depends(get_current_user)):
    return RecordingStatus(status=mock_rec_status.get(meeting_id, "stopped"))

# ----- Sections & Items Endpoints -----
@app.get("/meetings/{meeting_id}/sections", response_model=list[Section], tags=["セクション"], summary="セクション一覧", description="特定の会議の全てのセクションを取得する")
def list_sections(meeting_id: str, user: User = Depends(get_current_user)):
    return mock_sections.get(meeting_id, [])

@app.patch("/meetings/{meeting_id}/sections/{section_id}", response_model=Section, tags=["セクション"], summary="セクション更新", description="会議内の特定のセクションを更新する")
def update_section(meeting_id: str, section_id: str, sec: Section, user: User = Depends(get_current_user)):
    for s in mock_sections.get(meeting_id, []):
        if s.id == section_id:
            s.order = sec.order
            s.title = sec.title
            return s
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.post("/meetings/{meeting_id}/sections/{section_id}/items", response_model=Item, tags=["項目"], summary="項目追加", description="セクションに新しい項目を追加する")
def add_item(meeting_id: str, section_id: str, it: Item, user: User = Depends(get_current_user)):
    mock_items.setdefault(section_id, []).append(it)
    return it

@app.patch("/meetings/{meeting_id}/sections/{section_id}/items/{item_id}", response_model=Item, tags=["項目"], summary="項目更新", description="セクション内の既存の項目を更新する")
def update_item(meeting_id: str, section_id: str, item_id: str, it: Item, user: User = Depends(get_current_user)):
    items = mock_items.get(section_id, [])
    for existing in items:
        if existing.id == item_id:
            existing.order = it.order
            existing.text = it.text
            return existing
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.delete("/meetings/{meeting_id}/sections/{section_id}/items/{item_id}", tags=["項目"], summary="項目削除", description="セクションから項目を削除する")
def delete_item(meeting_id: str, section_id: str, item_id: str, user: User = Depends(get_current_user)):
    items = mock_items.get(section_id, [])
    for existing in items:
        if existing.id == item_id:
            items.remove(existing)
            return {"detail": "deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

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

# ----- Live WebSocket -----
@app.websocket("/meetings/{meeting_id}/live")
async def websocket_live(websocket: WebSocket, meeting_id: str):
    """
    会議中のリアルタイム更新のためのWebSocket接続を確立します。
    
    このエンドポイントは会議のセクションと項目に関するリアルタイム更新を送信します。
    クライアントはこれを使用して、更新をリアルタイムで表示することができます。
    """
    await websocket.accept()
    seq = 1
    try:
        while True:
            if seq == 5:
                # Section update to test reorder
                event = {"type": "section.update", "sectionId": "s2", "order": 1, "sequenceNumber": seq}
            elif seq == 7:
                # Item update to test item reorder
                event = {"type": "item.update", "sectionId": "s1", "itemId": "i1", "order": 2, "sequenceNumber": seq}
            else:
                event = {"type": "section.add", "sectionId": f"s{seq}", "title": f"セクション{seq}", "order": seq, "sequenceNumber": seq}
            await websocket.send_json(event)
            seq += 1
            await asyncio.sleep(2)
    finally:
        await websocket.close()
