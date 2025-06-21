import os
import mimetypes
from google import genai
from google.genai import types

# -------------------------------------------------------------------------
# クライアントの初期化
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
MODEL_NAME = "gemini-2.5-flash" # 文字起こしには gemini-2.5-flash が適しています

# -------------------------------------------------------------------------
# 音声の文字起こし機能
# -------------------------------------------------------------------------
def transcribe_audio(audio_file_path: str) -> str:
    """
    音声ファイルを文字起こしします。

    Args:
        audio_file_path (str): 音声データ（MP3, WAVなど）のファイルパス。

    Returns:
        str: AIによって生成された文字起こし結果。
    """
    if not client:
        return "クライアントが初期化されていません。"
        
    if not os.path.exists(audio_file_path):
        return f"エラー: 音声ファイルが見つかりません: {audio_file_path}"

    print(f"\n音声ファイル '{audio_file_path}' を文字起こししています...")
    
    # AIへの指示（プロンプト）を作成します。
    prompt = """
    あなたは高精度な音声文字起こしシステムです。
    以下の音声を正確に文字起こししてください。
    
    要件:
    1. 話者が複数いる場合は、可能であれば「話者1:」「話者2:」のように話者を区別してください
    2. 日本語の場合は日本語で、英語の場合は英語で文字起こしをしてください
    3. 音声内の言葉を省略せず、できるだけ正確に書き起こしてください
    4. 明らかな言い間違いや言い淀みも含めて忠実に文字起こししてください
    5. [笑]、[間]、[拍手]などの非言語情報も可能な限り記載してください
    
    出力形式:
    ```
    (話者情報がある場合)
    話者1: 発言内容
    話者2: 発言内容
    ...
    
    (話者情報がない場合)
    発言内容全文
    ```
    """
    
    try:
        # 音声ファイルをバイトデータとして読み込む
        with open(audio_file_path, 'rb') as f:
            audio_bytes = f.read()

        # ファイルのMIMEタイプを推測
        mime_type, _ = mimetypes.guess_type(audio_file_path)
        if mime_type is None:
            # 拡張子から推測
            if audio_file_path.lower().endswith('.mp3'):
                mime_type = 'audio/mp3'  # 参考コードに合わせて audio/mp3 を使用
            elif audio_file_path.lower().endswith('.wav'):
                mime_type = 'audio/wav'  # WAVの正しいMIMEタイプ
            else:
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
            model=MODEL_NAME,
            contents=[prompt, audio_part]
        )
        return response.text
    except Exception as e:
        return f"文字起こしの生成中にエラーが発生しました: {e}"

# -------------------------------------------------------------------------
# メイン処理: 文字起こし機能を実行する
# -------------------------------------------------------------------------
if __name__ == "__main__":
    if client:
        print("="*50)
        print("音声の文字起こしの実行")
        print("="*50)
        
        # MP3ファイルの文字起こし
        mp3_file_path = "sampleMP3.mp3"
        if os.path.exists(mp3_file_path):
            print(f"\nMP3ファイル '{mp3_file_path}' の文字起こしを開始します...")
            transcription_mp3 = transcribe_audio(mp3_file_path)
            print("\n--- MP3ファイルの文字起こし結果 ---")
            print(transcription_mp3)
        else:
            print(f"MP3ファイル '{mp3_file_path}' が見つかりません。")
        
        # WAVファイルの文字起こし
        wav_file_path = "sampleWAV.wav"
        if os.path.exists(wav_file_path):
            print(f"\nWAVファイル '{wav_file_path}' の文字起こしを開始します...")
            transcription_wav = transcribe_audio(wav_file_path)
            print("\n--- WAVファイルの文字起こし結果 ---")
            print(transcription_wav)
        else:
            print(f"WAVファイル '{wav_file_path}' が見つかりません。")
            
        print("="*50)