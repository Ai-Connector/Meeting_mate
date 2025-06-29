import asyncio
import websockets
import json

async def test_websocket():
    """
    WebSocket connection test to receive prompt information from backend.
    
    Note: This test only receives prompt information from backend to frontend.
    No prompt information is sent from frontend to backend (one-way communication).
    """
    uri = "ws://localhost:8000/meetings/m1/live"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket connection established")
            print("Receiving prompt information from backend...")
            print("-" * 50)
            
            message_count = 0
            while message_count < 15:  # Receive more messages
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    message_count += 1
                    
                    # Display different message types
                    msg_type = data.get("type", "unknown")
                    
                    if msg_type == "connection.established":
                        print(f"[{message_count}] Connection: {data.get('message', '')}")
                        
                    elif msg_type == "meeting.started":
                        print(f"[{message_count}] Meeting Started:")
                        print(f"   Message: {data.get('message', '')}")
                        prompts = data.get('prompts', {})
                        if prompts:
                            print(f"   Introduction: {prompts.get('introduction', '')}")
                            questions = prompts.get('questions', [])
                            if questions:
                                print(f"   Sample Question: {questions[0] if questions else ''}")
                                
                    elif msg_type == "section.status_changed":
                        print(f"[{message_count}] Section Status Changed:")
                        print(f"   Section ID: {data.get('sectionId', '')}")
                        print(f"   Status: {data.get('status', '')}")
                        print(f"   Message: {data.get('message', '')}")
                        prompts = data.get('prompts', {})
                        if prompts:
                            print(f"   Introduction: {prompts.get('introduction', '')}")
                            
                    elif msg_type == "section.transition":
                        print(f"[{message_count}] Section Transition:")
                        print(f"   From: {data.get('fromSectionId', '')} -> To: {data.get('toSectionId', '')}")
                        print(f"   Message: {data.get('message', '')}")
                        
                    elif msg_type == "item.added":
                        print(f"[{message_count}] Item Added:")
                        print(f"   Section ID: {data.get('sectionId', '')}")
                        print(f"   Item Text: {data.get('itemText', '')}")
                        
                    elif msg_type == "meeting.summary":
                        print(f"[{message_count}] Meeting Summary:")
                        print(f"   Message: {data.get('message', '')}")
                        
                    elif msg_type == "progress.prompt":
                        print(f"[{message_count}] Progress Prompt:")
                        prompts = data.get('prompts', {})
                        if prompts:
                            print(f"   Encouragement: {prompts.get('encouragement', '')}")
                            print(f"   Time Check: {prompts.get('time_check', '')}")
                            
                    else:
                        print(f"[{message_count}] Other Message ({msg_type}):")
                        print(f"   Data: {json.dumps(data, ensure_ascii=False, indent=2)}")
                    
                    print("-" * 50)
                    
                except websockets.exceptions.ConnectionClosed:
                    print("WebSocket connection closed")
                    break
                except json.JSONDecodeError:
                    print(f"JSON decode error: {message}")
                except Exception as e:
                    print(f"Error: {e}")
                    
    except Exception as e:
        print(f"WebSocket connection error: {e}")

async def test_websocket_simple():
    """
    Simple WebSocket test (original test)
    """
    uri = "ws://localhost:8000/meetings/m1/live"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")
        for i in range(5):  # Receive 5 messages
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received [{i+1}]: {data}")

if __name__ == "__main__":
    print("Starting WebSocket prompt information reception test...")
    print("This test demonstrates one-way communication from backend to frontend.")
    print("No prompt information is sent from frontend to backend.")
    print()
    
    # Run detailed test
    asyncio.run(test_websocket())