# Python標準ライブラリのインポート (Import Python standard libraries)
import grpc
from concurrent import futures
import time

# 生成されたgRPCコードのインポート (Import generated gRPC code)
from protos import counter_pb2
from protos import counter_pb2_grpc

# CounterServicerクラスの定義 (Define CounterServicer class)
class CounterServicer(counter_pb2_grpc.CounterServicer):
    # CountCharactersメソッドの実装 (Implement CountCharacters method)
    def CountCharacters(self, request_iterator, context):
        # クライアントからのリクエストストリームを処理します (Process the request stream from the client)
        for request in request_iterator:
            # 受信したテキストの文字数を計算します (Calculate the character count of the received text)
            count = len(request.text)
            # CharacterResponseオブジェクトを作成して返します (Create and return a CharacterResponse object)
            # yieldを使用してレスポンスをストリーミングします (Stream responses using yield)
            yield counter_pb2.CharacterResponse(count=count)

# serve関数の定義 (Define serve function)
def serve():
    # gRPCサーバーを作成します (Create a gRPC server)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # CounterServicerをサーバーに追加します (Add CounterServicer to the server)
    counter_pb2_grpc.add_CounterServicer_to_server(CounterServicer(), server)
    # サーバーを指定されたポートでリッスンします (Make the server listen on the specified port)
    server.add_insecure_port('[::]:50051')
    # サーバーを開始します (Start the server)
    server.start()
    print("サーバー起動中 ポート50051 (Server started on port 50051)")
    # サーバーが終了するまで待機します (Wait until the server is terminated)
    try:
        while True:
            time.sleep(86400)  # 1日待機 (Wait for one day)
    except KeyboardInterrupt:
        # Ctrl+Cが押されたらサーバーを停止します (Stop the server if Ctrl+C is pressed)
        server.stop(0)

# メインブロック (Main block)
if __name__ == '__main__':
    serve()
