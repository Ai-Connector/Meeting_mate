# Realtime Minutes Mock Server ドキュメント

このドキュメントは、FastAPIベースのモックサーバーを使ってフロント開発をスムーズに行うためのガイドです。

---

## 1. 概要

* **目的**: バックエンド実装前に、フロントエンドが各APIの挙動を確認・実装できるようにする。
* **Tech Stack**: Python 3.9+, FastAPI, Uvicorn, CORSミドルウェア
* **データ**: インメモリのダミーデータを返却。永続ストレージ不要。

## 2. セットアップと起動方法

### Docker Compose を使用する方法（推奨）

```bash
git clone <repo-url>
cd yuno-backend
docker-compose up
```

これにより、アプリケーションは http://localhost:8000 でアクセス可能になります。

* 任意のオリジンからリクエスト可能（CORS設定済み）。

## 3. エンドポイント一覧

### 3.1 認証・ユーザー管理 (`/auth`, `/users/me`)

| メソッド  | パス              | 説明          | リクエスト例                                 | レスポンス例                                                     |
| ----- | --------------- | ----------- | -------------------------------------- | ---------------------------------------------------------- |
| POST  | `/auth/login`   | ダミー認証トークン発行 | `{ "email":"a@b.com","password":"p" }` | `{ "access_token":"mock-token","refresh_token":"..." }`    |
| POST  | `/auth/refresh` | トークン更新      | -                                      | `{ "access_token":"new-mock-token",... }`                  |
| GET   | `/users/me`     | ユーザー情報取得    | `Authorization: Bearer mock-token`     | `{ "id":"u1","name":"Alice","email":"alice@example.com" }` |
| PATCH | `/users/me`     | ユーザー情報更新    | 更新後の User JSON                         | 更新後の User JSON                                             |

### 3.2 テンプレート管理 (`/templates`)

| 方法     | パス                         | 説明   |
| ------ | -------------------------- | ---- |
| GET    | `/templates`               | 一覧取得 |
| POST   | `/templates`               | 作成   |
| GET    | `/templates/{template_id}` | 詳細取得 |
| PATCH  | `/templates/{template_id}` | 更新   |
| DELETE | `/templates/{template_id}` | 削除   |

### 3.3 会議管理 (`/meetings`)

| 方法     | パス                       | 説明   |
| ------ | ------------------------ | ---- |
| GET    | `/meetings`              | 一覧取得 |
| POST   | `/meetings`              | 作成   |
| GET    | `/meetings/{meeting_id}` | 詳細取得 |
| PATCH  | `/meetings/{meeting_id}` | 更新   |
| DELETE | `/meetings/{meeting_id}` | 削除   |

### 3.4 録音制御 (`/meetings/{meeting_id}/recording`)

| 方法   | パス                                        | 説明    |
| ---- | ----------------------------------------- | ----- |
| POST | `/meetings/{meeting_id}/recording/start`  | 録音開始  |
| POST | `/meetings/{meeting_id}/recording/stop`   | 録音停止  |
| GET  | `/meetings/{meeting_id}/recording/status` | ステータス |

### 3.5 セクション／アイテム管理

| 方法     | パス                                                             | 説明      |
| ------ | -------------------------------------------------------------- | ------- |
| GET    | `/meetings/{meeting_id}/sections`                              | セクション一覧 |
| PATCH  | `/meetings/{meeting_id}/sections/{section_id}`                 | セクション更新 |
| POST   | `/meetings/{meeting_id}/sections/{section_id}/items`           | アイテム追加  |
| PATCH  | `/meetings/{meeting_id}/sections/{section_id}/items/{item_id}` | アイテム更新  |
| DELETE | `/meetings/{meeting_id}/sections/{section_id}/items/{item_id}` | アイテム削除  |

### 3.6 タスク管理 (`/meetings/{meeting_id}/tasks`)

| 方法     | パス                                       | 説明   |
| ------ | ---------------------------------------- | ---- |
| GET    | `/meetings/{meeting_id}/tasks`           | 一覧取得 |
| POST   | `/meetings/{meeting_id}/tasks`           | 作成   |
| PATCH  | `/meetings/{meeting_id}/tasks/{task_id}` | 更新   |
| DELETE | `/meetings/{meeting_id}/tasks/{task_id}` | 削除   |

### 3.7 ライブ差分配信（WebSocket）

* **エンドポイント**: `ws://<host>/meetings/{meeting_id}/live`
* **認証不要**（モック）、常に接続許可
* **2秒ごとに `section.add` イベント**:

```json
{ "type": "section.add", "sectionId": "s1", "title": "セクション1", "order": 1, "sequenceNumber": 1 }
```

* **5回目のみ `section.update`** (並び替えテスト用):

```json
{ "type": "section.update", "sectionId": "s2", "order": 1, "sequenceNumber": 5 }
```

* **クライアント**はイベントを元にUIを更新。

### 3.8 フルスナップショット取得（フォールバック）

* 差分欠落/再接続時に全セクションを復旧

```http
GET /meetings/{meeting_id}/sections?full=true
```

---

## 4. 開発ポイント

1. **CORS**: 全オリジン/全メソッド/全ヘッダーを許可
2. **モックのステート管理**:

   * `PATCH`/`DELETE`で `mock_*` リストや辞書を実際に更新
   * 次回の `GET` に変更が反映される
3. **404 エラー処理**: 存在しない ID には `HTTPException(status_code=404)` を返却
4. **イベント順序管理**: `sequenceNumber` を利用し再接続・欠落検知をサポート
5. **モックのライフサイクル**: アプリ再起動で全データリセット、永続化なし
6. **Swagger UI**: `http://localhost:8000/docs` でドキュメント自動生成
7. **Swagger JSON**: `http://localhost:8000/openapi.json` で OpenAPI 仕様を取得可能

---

## 5. Swagger ドキュメントの保存

APIの Swagger ドキュメントをローカルファイルとして保存するには、以下の方法があります：

### 5.1 save_swagger.py スクリプトを使用する

```bash
# サーバーが実行中であることを確認してから:
python save_swagger.py --url http://localhost:8000 --output swagger.json
```

### 5.2 save_swagger.sh スクリプトを使用する

```bash
# 実行権限を付与
chmod +x save_swagger.sh

# 実行
./save_swagger.sh --url http://localhost:8000 --output swagger.json
```

これにより、OpenAPI 仕様が JSON ファイルとして保存され、API クライアントの生成やドキュメントの共有に利用できます。

---

上記を `README.md` 等に貼り付け、フロント開発にご利用ください。
