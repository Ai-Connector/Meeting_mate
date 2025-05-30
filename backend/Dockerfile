# ベースイメージを指定 (Specify the base image)
FROM python:3.10-slim

# 作業ディレクトリを設定 (Set the working directory)
WORKDIR /app

# protosディレクトリをコンテナにコピー (Copy the protos directory to the container)
COPY protos /app/protos

# backendディレクトリの中身をコンテナにコピー (Copy the contents of the backend directory to the container)
COPY backend /app/backend

# PYTHONPATH環境変数を設定 (Set the PYTHONPATH environment variable)
ENV PYTHONPATH /app

# backendディレクトリに移動して依存関係をインストール (Move to the backend directory and install dependencies)
RUN pip install --no-cache-dir -r backend/requirements.txt

# ポートを公開 (Expose the port)
EXPOSE 50051

# サーバーを実行するコマンドを指定 (Specify the command to run the server)
CMD ["python", "backend/server.py"]
