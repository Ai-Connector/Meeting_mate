# Yuno gRPCサーバー

## 概要

本プロジェクトは、リアルタイム文字数カウンターです。
gRPCストリーミングを使用しており、以下のコンポーネントで構成されています。

*   フロントエンド
*   バックエンド
*   プロキシ

## プロジェクト構造

本プロジェクトの主要なディレクトリとファイルは以下の通りです。

*   `frontend/`: フロントエンドアプリケーション（Next.js）のソースコードが含まれています。ユーザーインターフェースを担当します。
*   `backend/`: バックエンドアプリケーション（Python gRPCサーバー）のソースコードが含まれています。文字数カウントのロジックを担当します。
*   `protos/`: gRPC通信で使用するProtocol Buffersの定義ファイル（`.proto`）が含まれています。クライアントとサーバー間のデータ構造を定義します。
*   `docker-compose.yml`: Dockerコンテナの構成を定義するファイルです。各サービス（フロントエンド、バックエンド、プロキシ）のビルドと実行を管理します。
*   `envoy.yaml`: Envoyプロキシの設定ファイルです。gRPC-WebのリクエストをバックエンドのgRPCサービスに変換・転送する役割を担います。

## プロトコル定義 (`protos/counter.proto`)

gRPC通信のプロトコルは `protos/counter.proto` ファイルで定義されています。

*   **サービス**: `Counter`
    *   **RPC**: `CountCharacters`
        *   **タイプ**: 双方向ストリーミング (Bidirectional Streaming)
        *   **説明**: クライアントはテキスト文字列をストリームとして送信し、サーバーは各受信テキストに対応する文字数をストリームとして返却します。リアルタイムでの文字数カウントを実現します。

*   **メッセージ**:
    *   `CharacterRequest`:
        *   `text (string)`: カウント対象の入力テキスト。
    *   `CharacterResponse`:
        *   `count (int32)`: 入力テキストの文字数。

## バックエンド (`backend/server.py`)

バックエンドはPythonで実装されたgRPCサーバーです。`backend/server.py` にコードがあります。

*   **`CounterServicer` クラス**:
    *   `protos/counter.proto` で定義された `Counter` サービスを実装します。
    *   **`CountCharacters` メソッド**:
        *   クライアントからの `CharacterRequest` メッセージのストリームを受信します。
        *   各リクエストに含まれる `text` フィールドの文字数を計算します。
        *   計算結果を `CharacterResponse` メッセージ（`count` フィールドに文字数を格納）として、ストリームでクライアントに返送します。
        *   クライアントがストリームを閉じるまで、この処理を継続します。これにより、クライアントが入力するたびにリアルタイムで文字数フィードバックを得ることが可能になります。

## フロントエンド (`frontend/pages/index.tsx`)

フロントエンドはNext.js (Reactフレームワーク) を使用して構築されており、`frontend/pages/index.tsx` に主要なロジックが含まれています。

*   **gRPC-Web接続**:
    *   `@improbable-eng/grpc-web` ライブラリと自動生成された `CounterClient` ( `frontend/generated/counter_pb_service.js` ) を使用して、gRPCサービスに接続します。
    *   通信はEnvoyプロキシ (`http://localhost:8080`) を介して行われます。EnvoyはブラウザからのgRPC-WebリクエストをバックエンドのgRPCサーバーが理解できる形式に変換します。

*   **リアルタイム文字数カウント**:
    *   ユーザーがテキストエリアに入力を行うと、`countCharacters` メソッドが呼び出されます。
    *   このメソッドはサーバーとの間に双方向ストリームを確立します。
    *   入力されたテキストは `CharacterRequest` メッセージとしてストリーム経由でサーバーに送信されます。
    *   サーバーからの `CharacterResponse` メッセージ（文字数を含む）をリッスンし、受信した文字数をリアルタイムで画面に表示します。
    *   ユーザーがテキストエリアの内容をクリアしたり、ストリームが予期せず終了した場合には、ストリームを適切に閉じる処理も行われます。

## コンテナ構成 (`docker-compose.yml`)

プロジェクト全体のサービスは `docker-compose.yml` ファイルによって定義・管理されます。以下の3つのサービスで構成されています。

*   **`backend`**:
    *   **役割**: Pythonで実装されたgRPCサーバーを実行します。文字カウントロジックを担当します。
    *   **Dockerfile**: `backend/Dockerfile`
    *   **ポート**: コンテナ内部の `50051` 番ポートでgRPCサービスを公開します。このポートはホストマシンには直接公開されず、`envoy` サービスからアクセスされます。
    *   **依存関係**: なし

*   **`frontend`**:
    *   **役割**: Next.jsで構築されたフロントエンドアプリケーションを実行します。ユーザーインターフェースを提供します。
    *   **Dockerfile**: `frontend/Dockerfile`
    *   **ポート**: ホストマシンの `3000` 番ポートをコンテナの `3000` 番ポートにマッピングします (`3000:3000`)。ブラウザから `http://localhost:3000` でアクセスできます。
    *   **依存関係**: `backend` と `envoy` に依存します (`depends_on`)。これにより、`frontend` が起動する前に `backend` と `envoy` が起動していることが保証されます。

*   **`envoy`**:
    *   **役割**: Envoyプロキシを実行します。gRPC-Web (HTTP/1.1) リクエストを `backend` のgRPC (HTTP/2) サービスに中継・変換します。
    *   **Dockerfile**: `envoy.yaml` を設定ファイルとして使用し、公式の `envoyproxy/envoy` イメージをベースにしています。
    *   **ポート**: ホストマシンの `8080` 番ポートをコンテナの `8080` 番ポートにマッピングします (`8080:8080`)。フロントエンドはこのポート (`http://localhost:8080`) を介してバックエンドと通信します。
    *   **依存関係**: `backend` に依存します (`depends_on`)。`envoy` がトラフィックを `backend` にルーティングできるようにするためです。

## Envoyプロキシ (`envoy.yaml`)

Envoyプロキシは、ブラウザベースのフロントエンドとgRPCバックエンド間の通信を可能にするための重要なコンポーネントです。設定は `envoy.yaml` ファイルで行われます。

*   **役割**:
    *   gRPC-Webプロキシとして機能します。最新のブラウザはHTTP/2上で動作する標準のgRPCを直接サポートしていないため、gRPC-Web (通常はHTTP/1.1上でラップされる) を使用する必要があります。Envoyは、フロントエンドからのgRPC-Webリクエストを受け取り、それをバックエンドの標準gRPCサービスが理解できる形式に変換します。
    *   逆も同様に、バックエンドからのgRPCレスポンスをgRPC-Web形式に変換してフロントエンドに返します。

*   **設定のポイント**:
    *   **リスナー**: ポート `8080` でHTTPリクエストを待ち受けます。フロントエンドアプリケーションはこのポート (`http://localhost:8080`) にリクエストを送信します。
    *   **ルーティング**: 受信したリクエストは、`backend` サービス（`docker-compose.yml` で定義）の `50051` 番ポート（バックエンドgRPCサーバーがリッスンしているポート）にルーティングされます。
    *   **gRPC-Webフィルタ (`envoy.filters.http.grpc_web`)**: このフィルタがgRPC-WebとgRPC間の変換を行います。
    *   **CORS (Cross-Origin Resource Sharing) 設定**: ブラウザが異なるオリジン（この場合はフロントエンドの `http://localhost:3000` とEnvoyの `http://localhost:8080`）間でリソースを共有できるように、適切なCORSヘッダーを設定しています。これにより、フロントエンドがEnvoyプロキシ経由でgRPCコールを行えるようになります。

## 実行方法

1.  Docker と Docker Compose がインストールされていることを確認してください。
2.  プロジェクトのルートディレクトリで以下のコマンドを実行し、すべてのサービスをビルドしてバックグラウンドで起動します。

    ```bash
    docker-compose up -d --build
    ```

3.  起動後、各サービスは以下のURLでアクセス可能になります。
    *   **フロントエンド**: `http://localhost:3000`
    *   **Envoyプロキシ (gRPC-Webエンドポイント)**: `http://localhost:8080`

    フロントエンドにアクセスすると、テキストエリアが表示され、入力した文字数がリアルタイムでカウントされます。
    バックエンドのgRPCサービス自体は直接ブラウザからアクセスできませんが、Envoyプロキシを介してフロントエンドと通信しています。

## 停止方法

以下のコマンドで起動中のコンテナを停止・削除できます。

```bash
docker-compose down
```
