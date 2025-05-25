# Yuno gRPCサーバー

このプロジェクトは、会議関連の機能を提供するgRPCサーバーです。現在、双方向ストリーミングRPC (`ProcessMeeting`) を中心とした機能を提供しています。

## プロジェクト構成

プロジェクトは以下のファイルで構成されています。

*   **`meeting.proto`**:
    *   gRPCサービスの定義ファイルです (Protocol Buffers形式)。
    *   サービスメソッド、リクエストメッセージ、レスポンスメッセージの構造を定義します。
    *   主なRPCメソッド:
        *   `ProcessMeeting (stream MeetingStreamRequest) returns (stream MeetingStreamResponse)`: 会議の処理を行うための主要な双方向ストリーミングRPCです。クライアントは会議の初期設定、音声チャンク、重要事項マーカーなどをストリームで送信でき、サーバーは会議IDの確認、部分/最終文字起こし結果、要約、重要事項の確認などをストリームで返します。
        *   (オプション: もし既存の単項RPCもユーザーが利用可能として残す場合、それらも簡単に記載)
            *   `SaveImportance`, `TranscribeAndSummarize`, `SaveMetadata`, `EditMetadata`, `DeleteMetadata`: 以前の単項RPCメソッド群です。（現在は主に `ProcessMeeting` に統合されていますが、互換性のために残されている場合もあります）。

*   **`meeting_pb2.py`**:
    *   `meeting.proto` ファイルからProtocol Bufferコンパイラによって自動生成されたPythonコードです。
    *   `.proto`ファイルで定義されたメッセージ (`InitialSetup`, `AudioChunk`, `MeetingInitialized` など) のためのPythonクラスが含まれています。
    *   **このファイルは手動で編集しないでください。**

*   **`meeting_pb2_grpc.py`**:
    *   `meeting.proto` ファイルからgRPC Pythonツールによって自動生成されたPythonコードです。
    *   クライアントがサーバーメソッドを呼び出すためのスタブ (`MeetingServiceStub`) と、サーバーがサービスを実装するための基底クラス (`MeetingServiceServicer`) が含まれています。
    *   **このファイルは手動で編集しないでください。**

*   **`server.py`**:
    *   gRPCサーバーのメインスクリプトです。
    *   `MeetingServiceServicer` の実装を含んでおり、クライアントからのリクエストを処理するロジックがここに記述されています。
    *   新しい双方向ストリーミングRPC `ProcessMeeting` の具体的な処理フロー（初期設定の受信、音声チャンクの処理、文字起こしと要約のシミュレーション、重要事項マーカーの処理など）が実装されています。
    *   サーバーの起動とポートの待受もこのファイルで行います。

*   **`requirements.txt`**:
    *   このプロジェクトを実行するために必要なPythonパッケージとそのバージョンがリストされています。
    *   主に `grpcio` と `grpcio-tools` が含まれます。
    *   `pip install -r requirements.txt` を使用して依存関係をインストールできます。

*   **`README.md`**:
    *   このファイルです。プロジェクトの概要、構成、および使用方法について説明します。

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
# import meeting_pb2
# import meeting_pb2_grpc

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

## サーバーの起動方法

1.  必要な依存関係をインストールします:
    ```bash
    pip install -r requirements.txt
    ```
2.  サーバーを起動します:
    ```bash
    python server.py
    ```
    デフォルトでは、サーバーはポート `50051` で待受します。
