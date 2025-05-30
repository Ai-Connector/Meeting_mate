import React, { useState, useEffect, useRef } from 'react';
// 日本語: 生成されたgRPCコードのインポート (Import generated gRPC code)
// messages (メッセージ)
import { CharacterRequest, CharacterResponse } from '../../generated/counter_pb'; 
// service client (サービスクライアント)
import { CounterClient } from '../../generated/counter_pb_service'; 
// grpc-web stream type, ClientReadableStream is a generic type.
// For a bidirectional stream, the client's stream object methods are directly available.
// We will type it as 'any' for simplicity as in many examples, 
// or use specific types if known from 'grpc-web'.
// The actual stream object returned by `client.countCharacters()` will have .on, .write, .cancel methods.
import { ClientReadableStream } from 'grpc-web'; // For typing stream.on('error', (err: grpcWeb.RpcError) => {...})

// 日本語: gRPCクライアントの初期化 (Initialize gRPC client)
// 実際のgRPCサーバーは50051ポートで動作します。gRPC-webは通常プロキシを必要とします。
// ここでは8080ポートを使用し、プロキシ（EnvoyやNext.jsのリライトなど）が処理することを想定します。
// (The actual gRPC server is on 50051. gRPC-web usually needs a proxy.)
// (We'll use 8080 and assume a proxy will handle it.)
const client = new CounterClient('http://localhost:8080'); 

const HomePage: React.FC = () => {
  const [inputText, setInputText] = useState<string>('');
  const [charCount, setCharCount] = useState<number>(0);
  const [error, setError] = useState<string>('');

  // 日本語: ストリームへの参照を保持 (Hold a reference to the stream)
  // streamRef.current will hold the object returned by client.countCharacters()
  const streamRef = useRef<ReturnType<typeof client.countCharacters> | null>(null);

  useEffect(() => {
    // 日本語: 双方向ストリーミングRPCの開始 (Start bidirectional streaming RPC)
    // client.countCharacters() は、リクエストメタデータとコールバックなしで呼び出されると、
    // クライアントストリームオブジェクトを返します。
    // (client.countCharacters(), when called without request metadata or callback,
    // returns the client stream object.)
    const stream = client.countCharacters();
    streamRef.current = stream;

    // 日本語: サーバーからのデータ受信時の処理 (Process data received from server)
    stream.on('data', (response: CharacterResponse) => {
      setCharCount(response.getCount());
      setError(''); // 日本語: 前のエラーをクリア (Clear previous errors)
    });

    // 日本語: エラー発生時の処理 (Process errors)
    // grpc-webのRpcError型を使用 (Use RpcError type from grpc-web for the error object)
    stream.on('error', (err: any) => { // err is of type grpcWeb.RpcError
      console.error('ストリームエラー (Stream Error):', err);
      setError(`エラー: ${err.message}`); // 日本語: Error message (Error: ${err.message})
      // More robust error handling might be needed depending on the error type
      // For example, err.code can give more specific gRPC error codes.
    });

    // 日本語: ストリーム終了時の処理 (Process stream end)
    stream.on('end', () => {
      console.log('ストリームが終了しました (Stream ended)');
      // ユーザーに通知するか、再接続を試みるなどの処理をここに追加できます
      // (You might want to inform the user or attempt to reconnect here)
    });

    // 日本語: コンポーネントのアンマウント時にストリームをクリーンアップ (Clean up stream on component unmount)
    return () => {
      if (streamRef.current) {
        streamRef.current.cancel(); // ストリームをキャンセル (Cancel the stream)
        console.log('アンマウント時にストリームがキャンセルされました (Stream cancelled on unmount)');
      }
    };
  }, []); // 日本語: 空の依存配列は、このeffectがマウント時に一度だけ実行され、アンマウント時にクリーンアップされることを意味します
          // (Empty dependency array means this effect runs once on mount and cleanup on unmount)

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newText = event.target.value;
    setInputText(newText);

    if (streamRef.current) {
      // 日本語: リクエストメッセージの作成と送信 (Create and send request message)
      const request = new CharacterRequest();
      request.setText(newText);
      streamRef.current.write(request); // データをストリームに書き込む (Write data to the stream)
    }
  };

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: '20px' }}>
      <h1>リアルタイム文字数カウンター (Real-time Character Counter)</h1>
      <input
        type="text"
        value={inputText}
        onChange={handleInputChange}
        placeholder="文字を入力してください" // 日本語: Enter text here
        style={{ padding: '10px', fontSize: '16px', width: '300px', marginBottom: '10px' }}
      />
      <p style={{ fontSize: '18px' }}>現在の文字数: {charCount}</p> {/* 日本語: Current character count: */}
      {error && <p style={{ color: 'red', fontSize: '16px' }}>{error}</p>}
    </div>
  );
};

export default HomePage;
```
