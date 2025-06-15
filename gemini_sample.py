import os
import mimetypes
from google import genai
from google.genai import types

# -------------------------------------------------------------------------
# 1. クライアントの初期化 (ご提示のサンプル形式)
# -------------------------------------------------------------------------
# TODO: 'your-project-id' をご自身の Google Cloud プロジェクトIDに置き換えてください。
try:
    client = genai.Client(
        vertexai=True,
        project='yuno-463003',
        location='us-central1',
    )
except Exception as e:
    print(f"クライアントの初期化に失敗しました。プロジェクトIDや認証情報を確認してください。")
    print(f"エラー: {e}")
    client = None

# 使用するモデル名を指定します。
MODEL_NAME = "gemini-2.0-flash-001" 

# -------------------------------------------------------------------------
# 機能1: 会議の目的に合わせた「アジェンダ自動提案」機能
# -------------------------------------------------------------------------
def generate_agenda(meeting_purpose: str, total_time_minutes: int, participants: list[str]) -> str:
    """
    会議の目的、時間、参加者からアジェンダ案を生成します。

    Args:
        meeting_purpose (str): 会議の目的やテーマ。
        total_time_minutes (int): 会議の総時間（分）。
        participants (list[str]): 参加者の役職などのリスト。

    Returns:
        str: AIによって生成されたアジェンダ案。
    """
    if not client:
        return "クライアントが初期化されていません。"

    # AIへの指示（プロンプト）を作成します。
    prompt = f"""
    あなたは優秀なファシリテーターです。
    以下の情報に基づいて、会議のアジェンダを作成してください。
    各議題には推奨の時間配分を必ず含めてください。

    # 会議の情報
    - **会議の目的:** {meeting_purpose}
    - **会議の総時間:** {total_time_minutes}分
    - **主な参加者:** {', '.join(participants)}

    # 出力形式の例
    - 議題1 (XX分)
    - 議題2 (XX分)
    - 質疑応答 (XX分)

    ---
    **生成されるアジェンダ:**
    """

    print("機能1: アジェンダを生成しています...")
    try:
        # client.models.generate_content を使用してテキストコンテンツを生成
        response = client.models.generate_content(
          model=f'models/{MODEL_NAME}', # Vertex AI経由の場合、'models/' プレフィックスを付けるのが一般的です
          contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"アジェンダの生成中にエラーが発生しました: {e}"


# -------------------------------------------------------------------------
# 機能2: リアルタイム「議事録生成」＆「未議論テーマ指摘」機能
# -------------------------------------------------------------------------
def generate_minutes_and_check_agenda(audio_file_path: str, agenda_text: str) -> str:
    """
    会議の音声ファイルとアジェンダから、議事録要約と未議論項目を生成します。

    Args:
        audio_file_path (str): 会議の音声データ（MP3, WAVなど）のファイルパス。
        agenda_text (str): 事前に決定したアジェンダのテキスト。

    Returns:
        str: AIによって生成された議事録要約と未議論項目の指摘。
    """
    if not client:
        return "クライアントが初期化されていません。"
        
    if not os.path.exists(audio_file_path):
        return f"エラー: 音声ファイルが見つかりません: {audio_file_path}"

    print(f"\n機能2: 音声ファイル '{audio_file_path}' を処理しています...")
    
    # AIへの指示（プロンプト）を作成します。
    prompt = f"""
    あなたは会議の書記担当アシスタントです。
    提供された音声データとアジェンダに基づいて、以下のタスクを実行してください。

    1.  **議事録の要約:** 音声の内容を簡潔に要約してください。誰が何を話したかのポイントも入れてください。
    2.  **未議論項目の指摘:** 作成した議事録の内容と以下のアジェンダを比較し、まだ議論されていない、あるいは議論が不十分だと思われる項目を指摘してください。

    ---
    **事前アジェンダ:**
    {agenda_text}
    ---

    **出力:**
    """
    
    try:
        # 音声ファイルをバイトデータとして読み込む
        with open(audio_file_path, 'rb') as f:
            audio_bytes = f.read()

        # ファイルのMIMEタイプを推測
        mime_type, _ = mimetypes.guess_type(audio_file_path)
        if mime_type is None:
            # 推測できない場合は一般的なオーディオタイプを指定
            mime_type = 'audio/mp3' 
            print(f"MIMEタイプを推測できませんでした。'{mime_type}'として処理します。")

        # types.Part.from_bytes を使用して音声パートを作成
        audio_part = types.Part.from_bytes(
            data=audio_bytes,
            mime_type=mime_type,
        )

        # プロンプトと音声パートをリストにして渡す
        response = client.models.generate_content(
            model=f'models/{MODEL_NAME}',
            contents=[prompt, audio_part]
        )
        return response.text
    except Exception as e:
        return f"議事録の生成中にエラーが発生しました: {e}"


# -------------------------------------------------------------------------
# メイン処理: 各機能を実行する
# -------------------------------------------------------------------------
if __name__ == "__main__":
    if client:
        # --- 機能1の実行例 ---
        print("="*50)
        print("機能1: アジェンダ自動提案の実行")
        print("="*50)
        meeting_purpose_1 = "新製品「AI搭載スマートコーヒーメーカー」の販売戦略を決める"
        total_time_1 = 60
        participants_1 = ["営業部長", "マーケティング担当", "開発リーダー", "プロダクトマネージャー"]

        generated_agenda = generate_agenda(meeting_purpose_1, total_time_1, participants_1)
        print("\n--- 生成されたアジェンダ ---")
        print(generated_agenda)
        print("="*50)

        # --- 機能2の実行例 ---
        print("\n" + "="*50)
        print("機能2: 議事録生成＆未議論テーマ指摘の実行")
        print("="*50)
        
        # TODO: この音声ファイルをご自身のものに置き換えてください。
        #      内容は「新製品のターゲット顧客は30代のビジネスパーソンだ」といった会話を想定しています。
        audio_clip_path = "path/to/your/meeting_segment.mp3"
        
        # 機能1で生成されたアジェンダ（または事前に用意したアジェンダ）を使用
        agenda_for_minutes = generated_agenda 
        
        # 音声ファイルが存在するかチェックしてから実行
        if os.path.exists(audio_clip_path):
            minutes_and_check = generate_minutes_and_check_agenda(audio_clip_path, agenda_for_minutes)
            print("\n--- 生成された議事録要約と未議論項目の指摘 ---")
            print(minutes_and_check)
        else:
            print(f"ダミーの音声ファイルパスが設定されています。")
            print(f"'{audio_clip_path}' を実際の音声ファイルパスに置き換えて再度実行してください。")
        print("="*50)
