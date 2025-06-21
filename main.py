from fastapi import FastAPI
from typing import Optional
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase Admin SDKの初期化
# Cloud RunなどのGoogle Cloud環境では、引数なしでinitialize_app()を呼び出すと、
# 環境のサービスアカウントが自動的に使用されます。
try:
    firebase_admin.initialize_app()
except Exception as e:
    # ローカルでの開発時など、すでに初期化されている場合にエラーになるのを防ぐ
    # ただし、複数回初期化が呼ばれるような設計は避けるべき
    if not firebase_admin._apps: # type: ignore
        print(f"Failed to initialize Firebase Admin SDK: {e}")
        # ここでアプリケーションを停止するか、適切にエラー処理を行う
        # このサンプルではとりあえずprintしていますが、本番ではより堅牢な対応を

db = firestore.client()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # アプリケーション起動時にFirebaseが初期化されていることを確認（オプション）
    if firebase_admin._apps: # type: ignore
        print("Firebase Admin SDK initialized successfully.")
    else:
        print("Firebase Admin SDK not initialized.")


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

# --- User Registration ---
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str # 本番環境ではハッシュ化を検討

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: EmailStr

@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate):
    """
    新しいユーザーを作成し、Firestoreに保存します。
    """
    # Firestoreに保存するデータ
    # ここでは簡単のためパスワードを平文で保存していますが、
    # 本番環境では必ずハッシュ化してください。
    user_record = {
        "username": user_data.username,
        "email": user_data.email,
        "password": user_data.password, # セキュリティリスク！
        "created_at": firestore.SERVER_TIMESTAMP # サーバー側のタイムスタンプを記録
    }

    try:
        # Firestoreの 'users' コレクションに新しいドキュメントを追加
        # add() メソッドは自動的にユニークなIDを生成します。
        update_time, doc_ref = db.collection("users").add(user_record) # type: ignore

        # 生成されたドキュメントIDとユーザー情報をレスポンスとして返す
        return UserResponse(
            user_id=doc_ref.id,
            username=user_data.username,
            email=user_data.email
        )
    except Exception as e:
        # 簡単なエラーハンドリング
        # 本番ではより詳細なエラーログと適切なHTTPエラーレスポンスを返す
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
