# Pythonの公式イメージをベースイメージとして使用
FROM python:3.9-slim

# 作業ディレクトリを設定
WORKDIR /app

# 必要なライブラリをインストールするためのrequirements.txtをコピー
COPY ./requirements.txt /app/requirements.txt

# pipをアップグレードし、requirements.txtに記載されたライブラリをインストール
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . /app

# FastAPIアプリケーションを実行するコマンド
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
