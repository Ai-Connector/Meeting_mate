# リアルタイム議事録モックAPI ドキュメント

このドキュメントは、FastAPIベースのリアルタイム議事録モックサーバーの完全なAPIリファレンスです。フロントエンド開発をスムーズに行うための包括的なガイドを提供します。

---

## 1. 概要

### 1.1 目的
- **フロントエンド開発支援**: バックエンド実装前に、フロントエンドが各APIの挙動を確認・実装できるようにする
- **リアルタイム機能**: WebSocketを使用したリアルタイム更新とAI会議アシスト機能をサポート
- **完全なモック環境**: 実際のプロダクション環境と同様のAPIレスポンスを提供

### 1.2 技術スタック
- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **WebSocket**: リアルタイム通信サポート
- **Cache**: Redis（オプション、利用不可時は自動的にキャッシュ無効化）
- **Database**: Firestore（現在は無効化、モックデータを使用）
- **CORS**: 全オリジン対応済み

### 1.3 主要機能
- **認証・ユーザー管理**: ログイン、トークン管理、ユーザー情報
- **テンプレート管理**: 会議テンプレートの作成・管理
- **会議管理**: 会議の作成、開始、完了、削除
- **録音制御**: 録音の開始・停止・状態管理
- **セクション管理**: 会議セクションの管理とステータス追跡
- **項目管理**: セクション内の議事録項目の管理
- **タスク管理**: アクションアイテムの管理
- **リアルタイム更新**: WebSocketによるライブ更新
- **AI会議アシスト**: LLM生成による会議進行サポート
- **キャッシュ機能**: 高速データアクセスのためのRedisキャッシュ

## 2. セットアップと起動方法

### 2.1 Docker Compose を使用する方法（推奨）

```bash
git clone <repo-url>
cd realtime-minutes-mock-server
docker-compose up
```

これにより、以下のサービスが起動します：
- **APIサーバー**: http://localhost:8000
- **Redis**: localhost:6379（キャッシュ用）

### 2.2 ローカル環境での起動

```bash
# 依存関係のインストール
pip install -r requirements.txt

# Redisサーバーの起動（オプション）
redis-server

# APIサーバーの起動
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2.3 アクセス情報

- **API Base URL**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **WebSocket**: ws://localhost:8000/meetings/{meeting_id}/live

### 2.4 設定

- **CORS**: 全オリジン、全メソッド、全ヘッダーを許可
- **認証**: モック実装（実際の認証は不要）
- **データ**: インメモリのモックデータを使用
- **キャッシュ**: Redis利用可能時は自動的に有効化

## 3. API エンドポイント詳細

### 3.1 認証・ユーザー管理

#### 3.1.1 ログイン
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**レスポンス:**
```json
{
  "access_token": "mock-token",
  "refresh_token": "mock-refresh"
}
```

#### 3.1.2 トークン更新
```http
POST /auth/refresh
```

**レスポンス:**
```json
{
  "access_token": "new-mock-token",
  "refresh_token": "new-mock-refresh"
}
```

#### 3.1.3 現在のユーザー情報取得
```http
GET /users/me
Authorization: Bearer mock-token
```

**レスポンス:**
```json
{
  "id": "u1",
  "name": "Alice",
  "email": "alice@example.com"
}
```

#### 3.1.4 ユーザー情報更新
```http
PATCH /users/me
Content-Type: application/json

{
  "id": "u1",
  "name": "Alice Updated",
  "email": "alice.updated@example.com"
}
```

### 3.2 テンプレート管理

#### 3.2.1 テンプレート一覧取得
```http
GET /templates
```

**レスポンス:**
```json
[
  {
    "id": "t1",
    "name": "標準会議テンプレート",
    "sections": [
      {
        "title": "議題",
        "order": 1,
        "items": [
          {"text": "前回の議事録の確認", "order": 1},
          {"text": "進捗状況の報告", "order": 2}
        ]
      }
    ]
  }
]
```

#### 3.2.2 テンプレート作成
```http
POST /templates
Content-Type: application/json

{
  "id": "t2",
  "name": "プロジェクト会議",
  "sections": [
    {
      "title": "進捗報告",
      "order": 1,
      "items": [
        {"text": "タスク完了状況", "order": 1}
      ]
    }
  ]
}
```

#### 3.2.3 テンプレート詳細取得
```http
GET /templates/{template_id}
```

#### 3.2.4 テンプレート更新
```http
PATCH /templates/{template_id}
Content-Type: application/json
```

#### 3.2.5 テンプレート削除
```http
DELETE /templates/{template_id}
```

#### 3.2.6 サンプルテンプレート追加
```http
POST /templates/examples
```

### 3.3 会議管理

#### 3.3.1 会議一覧取得
```http
GET /meetings
```

**レスポンス:**
```json
[
  {
    "id": "m1",
    "title": "Mock Meeting",
    "datetime": "2025-06-22T16:00:00",
    "template_id": "t1",
    "status": "in_progress"
  }
]
```

#### 3.3.2 会議作成
```http
POST /meetings
Content-Type: application/json

{
  "id": "m2",
  "title": "新しい会議",
  "datetime": "2025-01-28T10:00:00",
  "template_id": "t1",
  "status": "scheduled"
}
```

**注意**: `template_id`を指定すると、テンプレートに基づいてセクションと項目が自動的に作成されます。

#### 3.3.3 会議詳細取得
```http
GET /meetings/{meeting_id}
```

#### 3.3.4 会議データ全体取得（推奨）
```http
GET /meetings/{meeting_id}/full
```

**レスポンス:**
```json
{
  "meeting": {
    "id": "m1",
    "title": "Mock Meeting",
    "datetime": "2025-06-22T16:00:00",
    "template_id": "t1",
    "status": "in_progress"
  },
  "sections": [
    {
      "id": "s1",
      "title": "議題",
      "order": 1,
      "status": "completed",
      "items": [
        {
          "id": "i1",
          "section_id": "s1",
          "text": "ダミー項目1",
          "order": 1
        }
      ]
    }
  ],
  "tasks": [
    {
      "id": "task1",
      "text": "フォローアップメール送信",
      "assignee": "Bob",
      "due_date": "2025-06-23",
      "status": "open"
    }
  ],
  "recording_status": "stopped"
}
```

#### 3.3.5 会議更新
```http
PATCH /meetings/{meeting_id}
Content-Type: application/json
```

#### 3.3.6 会議開始
```http
POST /meetings/{meeting_id}/start
```

**レスポンス:**
```json
{
  "status": "in_progress",
  "message": "会議が開始されました"
}
```

#### 3.3.7 会議完了
```http
POST /meetings/{meeting_id}/complete
```

**レスポンス:**
```json
{
  "status": "completed",
  "message": "会議が完了し、すべてのデータが保存されました",
  "meeting_id": "m1"
}
```

#### 3.3.8 会議削除
```http
DELETE /meetings/{meeting_id}
```

### 3.4 録音制御

#### 3.4.1 録音開始
```http
POST /meetings/{meeting_id}/recording/start
```

**レスポンス:**
```json
{
  "status": "recording",
  "meeting_status": "in_progress"
}
```

#### 3.4.2 録音停止
```http
POST /meetings/{meeting_id}/recording/stop
```

**レスポンス:**
```json
{
  "status": "stopped",
  "message": "録音が停止されました。会議を完了するには /meetings/{meeting_id}/complete を呼び出してください。"
}
```

#### 3.4.3 録音状態取得
```http
GET /meetings/{meeting_id}/recording/status
```

**レスポンス:**
```json
{
  "status": "stopped"
}
```

### 3.5 セクション管理

#### 3.5.1 セクション一覧取得
```http
GET /meetings/{meeting_id}/sections
```

**レスポンス:**
```json
[
  {
    "id": "s1",
    "title": "議題",
    "order": 1,
    "status": "completed"
  },
  {
    "id": "s2",
    "title": "決定事項",
    "order": 2,
    "status": "in_progress"
  }
]
```

#### 3.5.2 セクション更新
```http
PATCH /meetings/{meeting_id}/sections/{section_id}
Content-Type: application/json

{
  "id": "s1",
  "title": "議題（更新）",
  "order": 1,
  "status": "completed"
}
```

#### 3.5.3 セクションステータス更新
```http
PATCH /meetings/{meeting_id}/sections/{section_id}/status
Content-Type: application/json

"in_progress"
```

**注意**: このエンドポイントはWebSocketを通じてステータス変更イベントとAI会議アシスト情報を送信します。

#### 3.5.4 セクションステータス一覧取得
```http
GET /meetings/{meeting_id}/sections/status
```

**レスポンス:**
```json
[
  {
    "id": "s1",
    "title": "議題",
    "order": 1,
    "status": "completed"
  },
  {
    "id": "s2",
    "title": "決定事項",
    "order": 2,
    "status": "in_progress"
  }
]
```

### 3.6 項目管理

#### 3.6.1 項目一覧取得
```http
GET /meetings/{meeting_id}/sections/{section_id}/items
```

**レスポンス:**
```json
[
  {
    "id": "i1",
    "section_id": "s1",
    "text": "ダミー項目1",
    "order": 1
  }
]
```

#### 3.6.2 項目追加
```http
POST /meetings/{meeting_id}/sections/{section_id}/items
Content-Type: application/json

{
  "id": "i2",
  "section_id": "s1",
  "text": "新しい項目",
  "order": 2
}
```

#### 3.6.3 項目更新
```http
PATCH /meetings/{meeting_id}/sections/{section_id}/items/{item_id}
Content-Type: application/json

{
  "id": "i1",
  "section_id": "s1",
  "text": "更新された項目",
  "order": 1
}
```

#### 3.6.4 項目削除
```http
DELETE /meetings/{meeting_id}/sections/{section_id}/items/{item_id}
```

#### 3.6.5 項目移動
```http
POST /meetings/{meeting_id}/sections/{section_id}/items/{item_id}/move
Content-Type: application/json

"target_section_id"
```

### 3.7 タスク管理

#### 3.7.1 タスク一覧取得
```http
GET /meetings/{meeting_id}/tasks
```

**レスポンス:**
```json
[
  {
    "id": "task1",
    "text": "フォローアップメール送信",
    "assignee": "Bob",
    "due_date": "2025-06-23",
    "status": "open"
  }
]
```

#### 3.7.2 タスク追加
```http
POST /meetings/{meeting_id}/tasks
Content-Type: application/json

{
  "id": "task2",
  "text": "資料準備",
  "assignee": "Alice",
  "due_date": "2025-01-30",
  "status": "open"
}
```

#### 3.7.3 タスク更新
```http
PATCH /meetings/{meeting_id}/tasks/{task_id}
Content-Type: application/json

{
  "id": "task1",
  "text": "フォローアップメール送信（完了）",
  "assignee": "Bob",
  "due_date": "2025-06-23",
  "status": "done"
}
```

#### 3.7.4 タスク削除
```http
DELETE /meetings/{meeting_id}/tasks/{task_id}
```

### 3.8 AI会議アシスト機能

#### 3.8.1 セクション会議アシスト取得
```http
GET /meetings/{meeting_id}/sections/{section_id}/assist
```

**レスポンス:**
```json
{
  "section_id": "s1",
  "meeting_id": "m1",
  "generated_at": "2025-01-27T10:30:00Z",
  "status": "active",
  "discussion_starter": "議題について話し合いを始めましょう。",
  "key_questions": [
    "議題に関して、現在の状況はいかがですか？",
    "他に考慮すべき点はありますか？",
    "次のステップは何でしょうか？"
  ],
  "conclusion_guide": "議題についての議論をまとめましょう。",
  "time_management": {
    "suggested_duration": "15分",
    "time_check": "時間を意識して進めましょう。"
  },
  "participation_tips": [
    "全員の意見を聞きましょう",
    "具体例があると良いでしょう"
  ]
}
```

#### 3.8.2 会議アシスト送信
```http
POST /meetings/{meeting_id}/assist/send
Content-Type: application/json

{
  "assist_type": "general",
  "custom_message": "会議の進行をサポートします"
}
```

**assist_type**: `meeting_start`, `section_change`, `meeting_complete`, `general`

#### 3.8.3 セクション会議アシスト送信
```http
POST /meetings/{meeting_id}/sections/{section_id}/assist/send
Content-Type: application/json

{
  "status": "in_progress"
}
```

#### 3.8.4 会議アシストリマインダー送信
```http
POST /meetings/{meeting_id}/assist/reminder
Content-Type: application/json

{
  "section_id": "s1"
}
```

### 3.9 WebSocket リアルタイム通信

#### 3.9.1 接続
```javascript
const ws = new WebSocket('ws://localhost:8000/meetings/m1/live');
```

**特徴:**
- **認証不要**（モック環境）
- **一方向通信**: バックエンドからフロントエンドへのAI会議アシスト情報送信のみ
- **自動接続管理**: 接続・切断の自動処理
- **リアルタイム更新**: セクションステータス変更、項目追加などのイベント配信

#### 3.9.2 WebSocketイベントタイプ

**1. 接続確立**
```json
{
  "type": "connection.established",
  "meetingId": "m1",
  "message": "WebSocket接続が確立されました。バックエンドからリアルタイム更新を受信します。"
}
```

**2. 会議開始アシスト**
```json
{
  "type": "meeting.started",
  "meetingId": "m1",
  "meeting_assist": {
    "section_id": "general",
    "meeting_id": "m1",
    "generated_at": "2025-01-27T10:30:00Z",
    "status": "active",
    "discussion_starter": "会議開始について話し合いを始めましょう。",
    "key_questions": [
      "現在の状況はいかがですか？",
      "他に考慮すべき点はありますか？",
      "次のステップは何でしょうか？"
    ],
    "conclusion_guide": "会議開始についての議論をまとめましょう。",
    "time_management": {
      "suggested_duration": "15分",
      "time_check": "時間を意識して進めましょう。"
    },
    "participation_tips": [
      "全員の意見を聞きましょう",
      "具体例があると良いでしょう"
    ]
  },
  "message": "会議が開始されました。最初のセクションに進みましょう。",
  "sequenceNumber": 1
}
```

**3. セクションステータス変更アシスト**
```json
{
  "type": "section.status_changed",
  "sectionId": "s1",
  "status": "in_progress",
  "meeting_assist": {
    "section_id": "s1",
    "meeting_id": "m1",
    "generated_at": "2025-01-27T10:30:00Z",
    "status": "active",
    "discussion_starter": "議題について話し合いを始めましょう。",
    "key_questions": [
      "議題に関して、現在の状況はいかがですか？",
      "他に考慮すべき点はありますか？"
    ],
    "conclusion_guide": "議題についての議論をまとめましょう。",
    "time_management": {
      "suggested_duration": "15分",
      "time_check": "時間を意識して進めましょう。"
    },
    "participation_tips": [
      "全員の意見を聞きましょう",
      "具体例があると良いでしょう"
    ]
  },
  "message": "セクション「議題」が開始されました。",
  "sequenceNumber": 2
}
```

**4. セクション移行アシスト**
```json
{
  "type": "section.transition",
  "fromSectionId": "s1",
  "toSectionId": "s2",
  "meeting_assist": {
    "section_id": "s2",
    "meeting_id": "m1",
    "discussion_starter": "決定事項について話し合いを始めましょう。",
    "key_questions": [
      "決定事項に関して、現在の状況はいかがですか？"
    ],
    "conclusion_guide": "決定事項についての議論をまとめましょう。",
    "time_management": {
      "suggested_duration": "15分"
    },
    "participation_tips": [
      "全員の意見を聞きましょう",
      "具体例があると良いでしょう"
    ]
  },
  "message": "次のセクション「決定事項」に移ります。",
  "sequenceNumber": 3
}
```

**5. 項目追加イベント**
```json
{
  "type": "item.added",
  "sectionId": "s2",
  "itemId": "i4",
  "itemText": "新しい決定事項",
  "meeting_assist": {
    "section_id": "s2",
    "meeting_id": "m1",
    "discussion_starter": "決定事項について話し合いを始めましょう。",
    "key_questions": [
      "決定事項に関して、現在の状況はいかがですか？"
    ]
  },
  "sequenceNumber": 4
}
```

**6. 会議終了アシスト**
```json
{
  "type": "meeting.summary",
  "meetingId": "m1",
  "meeting_assist": {
    "section_id": "general",
    "meeting_id": "m1",
    "discussion_starter": "会議まとめについて話し合いを始めましょう。",
    "conclusion_guide": "会議の内容をまとめましょう。",
    "participation_tips": [
      "アクションアイテムを確認しましょう",
      "次回の予定を決めましょう"
    ]
  },
  "message": "会議の内容をまとめましょう。",
  "sequenceNumber": 5
}
```

**7. 継続的な会議アシスト**
```json
{
  "type": "meeting.assist",
  "sectionId": "s2",
  "meeting_assist": {
    "section_id": "s2",
    "meeting_id": "m1",
    "discussion_starter": "決定事項について話し合いを始めましょう。",
    "key_questions": [
      "決定事項に関して、現在の状況はいかがですか？"
    ],
    "time_management": {
      "time_check": "時間を意識して進めましょう。"
    },
    "participation_tips": [
      "全員の意見を聞きましょう",
      "具体例があると良いでしょう"
    ]
  },
  "sequenceNumber": 6
}
```

#### 3.9.3 WebSocket使用例

```javascript
// WebSocket接続の確立
const ws = new WebSocket('ws://localhost:8000/meetings/m1/live');

// メッセージ受信の処理
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'connection.established':
      console.log('WebSocket接続が確立されました');
      break;
      
    case 'section.status_changed':
      console.log(`セクション ${data.sectionId} のステータスが ${data.status} に変更されました`);
      // AI会議アシスト情報を表示
      displayMeetingAssist(data.meeting_assist);
      break;
      
    case 'meeting.started':
      console.log('会議が開始されました');
      displayMeetingAssist(data.meeting_assist);
      break;
      
    case 'item.added':
      console.log(`新しい項目が追加されました: ${data.itemText}`);
      break;
      
    default:
      console.log('その他のイベント:', data);
  }
};

// AI会議アシスト情報の表示例
function displayMeetingAssist(assist) {
  console.log('話の切り出し方:', assist.discussion_starter);
  console.log('重要な質問:', assist.key_questions);
  console.log('まとめの言葉:', assist.conclusion_guide);
  console.log('時間管理:', assist.time_management);
  console.log('参加促進のヒント:', assist.participation_tips);
}

// 接続エラーの処理
ws.onerror = function(error) {
  console.error('WebSocketエラー:', error);
};

// 接続終了の処理
ws.onclose = function() {
  console.log('WebSocket接続が終了しました');
};
```

## 4. データモデル

### 4.1 主要エンティティ

#### User（ユーザー）
```json
{
  "id": "string",
  "name": "string",
  "email": "string"
}
```

#### Template（テンプレート）
```json
{
  "id": "string",
  "name": "string",
  "sections": [
    {
      "title": "string",
      "order": "integer",
      "items": [
        {
          "text": "string",
          "order": "integer"
        }
      ]
    }
  ]
}
```

#### Meeting（会議）
```json
{
  "id": "string",
  "title": "string",
  "datetime": "string (ISO 8601)",
  "template_id": "string | null",
  "status": "scheduled | in_progress | completed"
}
```

#### Section（セクション）
```json
{
  "id": "string",
  "title": "string",
  "order": "integer",
  "status": "not_started | in_progress | completed"
}
```

#### Item（項目）
```json
{
  "id": "string",
  "section_id": "string",
  "text": "string",
  "order": "integer"
}
```

#### Task（タスク）
```json
{
  "id": "string",
  "text": "string",
  "assignee": "string | null",
  "due_date": "string | null",
  "status": "open | done"
}
```

#### MeetingAssist（AI会議アシスト）
```json
{
  "section_id": "string",
  "meeting_id": "string",
  "generated_at": "string (ISO 8601)",
  "status": "active | completed | outdated",
  "discussion_starter": "string",
  "key_questions": ["string"],
  "conclusion_guide": "string",
  "time_management": {
    "suggested_duration": "string",
    "time_check": "string"
  },
  "participation_tips": ["string"]
}
```

### 4.2 ステータス定義

#### 会議ステータス
- **scheduled**: 予定済み（開始前）
- **in_progress**: 進行中
- **completed**: 完了

#### セクションステータス
- **not_started**: 未開始
- **in_progress**: 進行中
- **completed**: 完了

#### タスクステータス
- **open**: 未完了
- **done**: 完了

#### 録音ステータス
- **stopped**: 停止中
- **recording**: 録音中
- **processing**: 処理中

## 5. キャッシュ機能

### 5.1 Redis キャッシュ

APIサーバーは高速なデータアクセスのためにRedisキャッシュを使用します：

- **自動フォールバック**: Redis接続不可時は自動的にキャッシュ無効化
- **依存関係管理**: エンティティ間の依存関係を追跡し、関連データを自動無効化
- **TTL設定**: エンティティタイプ別の適切なキャッシュ期間

### 5.2 キャッシュキー構造

```
meeting:{meeting_id}           # 会議データ
meeting_full:{meeting_id}      # 会議データ全体（セクション・項目含む）
sections:{meeting_id}          # セクション一覧
section:{section_id}           # 個別セクション
items:{section_id}             # 項目一覧
item:{item_id}                 # 個別項目
section_assist:{section_id}    # セクション会議アシスト
section_statuses:{meeting_id}  # セクションステータス一覧
```

## 6. 開発・テスト

### 6.1 API テストスクリプト

```bash
# 全APIエンドポイントのテスト
python test_api.py
```

### 6.2 WebSocket テストスクリプト

```bash
# WebSocket接続とAI会議アシスト受信のテスト
python test_websocket.py
```

### 6.3 開発のポイント

1. **CORS設定**: 全オリジン、全メソッド、全ヘッダーを許可済み
2. **モックデータ管理**: 
   - `PATCH`/`DELETE`でモックデータを実際に更新
   - 次回の`GET`リクエストに変更が反映
3. **エラーハンドリング**: 存在しないIDには`404 Not Found`を返却
4. **WebSocketイベント順序**: `sequenceNumber`で再接続・欠落検知をサポート
5. **データ永続化**: アプリ再起動で全データリセット（モック環境）
6. **AI会議アシスト**: LLM生成による会議進行サポート（現在はモック実装）

### 6.4 ドキュメント

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 7. 本番環境との違い

### 7.1 モック環境の特徴

- **認証**: 実際の認証は不要（モックトークンを返却）
- **データベース**: Firestoreは無効化、インメモリデータを使用
- **AI機能**: LLM APIは無効化、モック会議アシスト情報を生成
- **永続化**: データはアプリ再起動時にリセット

### 7.2 本番環境で有効化される機能

- **Firebase認証**: 実際のユーザー認証
- **Firestore**: データの永続化
- **LLM API**: 実際のAI会議アシスト生成
- **セキュリティ**: 適切なCORS設定とアクセス制御

## 8. トラブルシューティング

### 8.1 よくある問題

**Q: WebSocket接続ができない**
A: ファイアウォールの設定を確認し、ポート8000が開放されていることを確認してください。

**Q: Redis接続エラーが表示される**
A: Redisサーバーが起動していない場合でも、APIは正常に動作します（キャッシュ無効化）。

**Q: APIレスポンスが遅い**
A: Redisキャッシュが有効な場合、初回アクセス後は高速化されます。

### 8.2 ログ確認

```bash
# Docker Composeでのログ確認
docker-compose logs -f web

# ローカル実行時のログ確認
# コンソール出力を確認
```

## 9. API エンドポイント一覧表

### 9.1 認証・ユーザー管理
| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| POST | `/auth/login` | ログイン | 不要 |
| POST | `/auth/refresh` | トークン更新 | 不要 |
| GET | `/users/me` | ユーザー情報取得 | 必要 |
| PATCH | `/users/me` | ユーザー情報更新 | 必要 |

### 9.2 テンプレート管理
| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| GET | `/templates` | テンプレート一覧取得 | 必要 |
| POST | `/templates` | テンプレート作成 | 必要 |
| GET | `/templates/{template_id}` | テンプレート詳細取得 | 必要 |
| PATCH | `/templates/{template_id}` | テンプレート更新 | 必要 |
| DELETE | `/templates/{template_id}` | テンプレート削除 | 必要 |
| POST | `/templates/examples` | サンプルテンプレート追加 | 必要 |

### 9.3 会議管理
| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| GET | `/meetings` | 会議一覧取得 | 必要 |
| POST | `/meetings` | 会議作成 | 必要 |
| GET | `/meetings/{meeting_id}` | 会議詳細取得 | 必要 |
| GET | `/meetings/{meeting_id}/full` | 会議データ全体取得 | 必要 |
| PATCH | `/meetings/{meeting_id}` | 会議更新 | 必要 |
| POST | `/meetings/{meeting_id}/start` | 会議開始 | 必要 |
| POST | `/meetings/{meeting_id}/complete` | 会議完了 | 必要 |
| DELETE | `/meetings/{meeting_id}` | 会議削除 | 必要 |

### 9.4 録音制御
| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| POST | `/meetings/{meeting_id}/recording/start` | 録音開始 | 必要 |
| POST | `/meetings/{meeting_id}/recording/stop` | 録音停止 | 必要 |
| GET | `/meetings/{meeting_id}/recording/status` | 録音状態取得 | 必要 |

### 9.5 セクション管理
| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| GET | `/meetings/{meeting_id}/sections` | セクション一覧取得 | 必要 |
| PATCH | `/meetings/{meeting_id}/sections/{section_id}` | セクション更新 | 必要 |
| PATCH | `/meetings/{meeting_id}/sections/{section_id}/status` | セクションステータス更新 | 必要 |
| GET | `/meetings/{meeting_id}/sections/status` | セクションステータス一覧取得 | 必要 |

### 9.6 項目管理
| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| GET | `/meetings/{meeting_id}/sections/{section_id}/items` | 項目一覧取得 | 必要 |
| POST | `/meetings/{meeting_id}/sections/{section_id}/items` | 項目追加 | 必要 |
| PATCH | `/meetings/{meeting_id}/sections/{section_id}/items/{item_id}` | 項目更新 | 必要 |
| DELETE | `/meetings/{meeting_id}/sections/{section_id}/items/{item_id}` | 項目削除 | 必要 |
| POST | `/meetings/{meeting_id}/sections/{section_id}/items/{item_id}/move` | 項目移動 | 必要 |

### 9.7 タスク管理
| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| GET | `/meetings/{meeting_id}/tasks` | タスク一覧取得 | 必要 |
| POST | `/meetings/{meeting_id}/tasks` | タスク追加 | 必要 |
| PATCH | `/meetings/{meeting_id}/tasks/{task_id}` | タスク更新 | 必要 |
| DELETE | `/meetings/{meeting_id}/tasks/{task_id}` | タスク削除 | 必要 |

### 9.8 AI会議アシスト
| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| GET | `/meetings/{meeting_id}/sections/{section_id}/assist` | セクション会議アシスト取得 | 必要 |
| POST | `/meetings/{meeting_id}/assist/send` | 会議アシスト送信 | 必要 |
| POST | `/meetings/{meeting_id}/sections/{section_id}/assist/send` | セクション会議アシスト送信 | 必要 |
| POST | `/meetings/{meeting_id}/assist/reminder` | 会議アシストリマインダー送信 | 必要 |

### 9.9 WebSocket
| プロトコル | エンドポイント | 説明 | 認証 |
|-----------|---------------|------|------|
| WebSocket | `/meetings/{meeting_id}/live` | リアルタイム通信 | 不要 |

---

このモックAPIサーバーを使用して、リアルタイム議事録アプリケーションのフロントエンド開発を効率的に進めることができます。すべてのAPIエンドポイントは完全に実装されており、実際のプロダクション環境と同様のレスポンスを提供します。
