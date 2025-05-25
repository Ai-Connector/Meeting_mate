# Yuno gRPCサーバー

## 概要

このプロジェクトは、会議関連の機能を提供するgRPCバックエンドと、Next.jsで構築されたフロントエンドで構成されています。全体はDockerによって管理されます。

## プロジェクト構成

*   **`backend/`**: Pythonで実装されたgRPCサーバー関連のファイルが含まれます。
    *   `Dockerfile`: バックエンドサービス（gRPCサーバー）のコンテナ環境を定義します。
    *   `meeting.proto`: gRPCサービス（`ProcessMeeting` RPCなど）とそのメッセージ型をProtocol Buffers形式で定義します。
    *   `server.py`: `meeting.proto`で定義されたサービスのサーバー側実装です。会議処理のロジックが含まれます。
    *   `requirements.txt`: Python環境に必要な依存パッケージのリストです。
*   **`frontend/`**: Next.jsで実装されたフロントエンドアプリケーション関連のファイルが含まれます。
    *   `Dockerfile`: フロントエンドサービス（Next.jsアプリケーション）のコンテナ環境を定義します。
    *   `pages/`: Next.jsアプリケーションのページコンポーネントが配置されます。
    *   `package.json`: Node.jsプロジェクトの依存関係やスクリプト（ビルド、開発サーバー起動など）を定義します。
*   **`docker-compose.yml`**: バックエンドとフロントエンドのサービスを連携して起動・管理するためのDocker Compose設定ファイルです。
*   **`.gitignore`**: Gitのバージョン管理から除外するファイルやディレクトリを指定します。
*   **`README.md`**: このファイルです。プロジェクトの概要、構成、セットアップ方法について説明します。

## 双方向ストリーミングRPC: `ProcessMeeting`

`ProcessMeeting` は、クライアントとサーバー間で継続的な双方向通信を可能にするRPCです。

**主な機能:**

1.  **会議の初期化**: クライアントは `InitialSetup` メッセージを送信し、会議のメタデータ（タイトル、日付、参加者など）や音声フォーマットを設定します。サーバーは `MeetingInitialized` メッセージで応答し、会議IDを返します。
2.  **音声ストリーミングと文字起こし**: クライアントは `AudioChunk` メッセージを連続して送信します。サーバーは受け取った音声チャンクを処理し、`PartialTranscription` (部分的な文字起こし結果) や `FinalTranscription` (最終的な文字起こし結果) をストリームで返します。
3.  **要約の生成**: (シミュレーション)音声データに基づいて、サーバーは `SummaryResult` を返すことができます。
4.  **重要事項のマーキング**: クライアントは会議中に `ImportanceMarker` メッセージを送信して、特定のポイントに重要度やメモを設定できます。サーバーは `ImportanceSavedAck` でこれを確認します。
5.  **エラーハンドリング**: ストリーム中にエラーが発生した場合、サーバーは `StreamError` メッセージを送信します。

**使用例 (クライアント側の概念):**

```python
# (これは概念的なクライアントコードであり、実際には動作するクライアントスクリプトが必要です)
# import grpc
# import meeting_pb2 # backend/meeting_pb2.py に相当
# import meeting_pb2_grpc # backend/meeting_pb2_grpc.py に相当

# channel = grpc.insecure_channel('localhost:50051')
# stub = meeting_pb2_grpc.MeetingServiceStub(channel)

# def generate_requests():
#     # 1. InitialSetup を送信
#     metadata = meeting_pb2.SaveMetadataRequest(title="My Meeting", attendees=["UserA"])
#     initial_request = meeting_pb2.MeetingStreamRequest(
#         initial_setup=meeting_pb2.InitialSetup(metadata=metadata, audio_format="wav")
#     )
#     yield initial_request

#     # 2. AudioChunk を複数回送信
#     for i in range(5):
#         audio_chunk_request = meeting_pb2.MeetingStreamRequest(
#             audio_chunk=meeting_pb2.AudioChunk(content=b"some_audio_data_chunk_{i}", sequence_number=i)
#         )
#         yield audio_chunk_request
#         # import time
#         # time.sleep(0.5) # 実際の音声ストリーミングをシミュレート

#     # 3. ImportanceMarker を送信
#     marker_request = meeting_pb2.MeetingStreamRequest(
#         importance_marker=meeting_pb2.ImportanceMarker(item_name="Key Decision", importance_score=5, details="Agreed on X.")
#     )
#     yield marker_request

# responses = stub.ProcessMeeting(generate_requests())

# for response in responses:
#     if response.HasField('confirmation'):
#         print(f"Server confirmation: {response.confirmation.message}")
#     elif response.HasField('partial_transcription'):
#         print(f"Partial transcript: {response.partial_transcription.transcript_segment}")
#     # ... 他のレスポンスタイプも同様に処理 ...
```

## アプリケーションの実行方法

### 前提条件

*   Docker がインストールされていること。
*   Docker Compose がインストールされていること。

### ビルドと実行

以下のコマンドを実行して、バックエンドとフロントエンドのサービスをビルドし、起動します。

```bash
docker-compose up --build
```

### アクセス

*   **フロントエンド**: ブラウザで `http://localhost:3000` にアクセスします。
*   **バックエンド (gRPC)**: サービスは `localhost:50051` で利用可能になります。

## アプリケーションの停止方法

以下のコマンドを実行して、起動しているサービスを停止します。

```bash
docker-compose down
```
