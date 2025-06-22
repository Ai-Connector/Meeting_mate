import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://web:80/meetings/m1/live"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")
        for _ in range(10):  # Receive 10 messages
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received: {data}")

if __name__ == "__main__":
    asyncio.run(test_websocket())