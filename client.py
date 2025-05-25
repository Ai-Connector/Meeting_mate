import grpc
import time
import meeting_pb2
import meeting_pb2_grpc

def generate_requests():
    # 1. InitialSetup
    print("\n--- Sending InitialSetup ---")
    metadata = meeting_pb2.SaveMetadataRequest(
        title="Test Meeting via Client",
        meeting_date="2024-06-01",
        attendees=["Client User", "Test Bot"],
        additional_info="This is a test call from client.py"
    )
    initial_request = meeting_pb2.MeetingStreamRequest(
        initial_setup=meeting_pb2.InitialSetup(
            metadata=metadata,
            audio_format="opus" # Example audio format
        )
    )
    yield initial_request
    time.sleep(0.5) # Simulate some delay or processing

    # 2. AudioChunks
    print("\n--- Sending AudioChunks ---")
    for i in range(1, 4): # Send 3 audio chunks
        print(f"Sending AudioChunk sequence {i}")
        audio_chunk_request = meeting_pb2.MeetingStreamRequest(
            audio_chunk=meeting_pb2.AudioChunk(
                content=f"dummy_audio_data_chunk_content_seq_{i}".encode('utf-8'),
                sequence_number=i
            )
        )
        yield audio_chunk_request
        time.sleep(1) # Simulate audio streaming interval

    # 3. ImportanceMarker
    print("\n--- Sending ImportanceMarker ---")
    marker_request = meeting_pb2.MeetingStreamRequest(
        importance_marker=meeting_pb2.ImportanceMarker(
            item_name="Key Discussion Point from Client",
            importance_score=5,
            details="Client marked this as important during streaming.",
            timestamp_ms=int(time.time() * 1000) # Example timestamp
        )
    )
    yield marker_request
    time.sleep(0.5)

    print("\n--- Finished sending all requests ---")


def run_client():
    print("Starting gRPC client...")
    channel_address = 'localhost:50051' # Ensure this matches your server configuration
    
    try:
        with grpc.insecure_channel(channel_address) as channel:
            stub = meeting_pb2_grpc.MeetingServiceStub(channel)
            print(f"Connected to server at {channel_address}")

            print("\n--- Calling ProcessMeeting ---")
            responses = stub.ProcessMeeting(generate_requests())

            print("\n--- Receiving Responses ---")
            for response in responses:
                response_type = response.WhichOneof('payload')
                print(f"Received response type: {response_type}")

                if response_type == 'confirmation':
                    print(f"  Meeting Initialized: ID={response.confirmation.meeting_id}, Success={response.confirmation.success}, Msg='{response.confirmation.message}'")
                elif response_type == 'partial_transcription':
                    print(f"  Partial Transcription: Seq={response.partial_transcription.sequence_number}, Transcript='{response.partial_transcription.transcript_segment}', Interim={response.partial_transcription.is_interim}")
                elif response_type == 'final_transcription':
                    print(f"  Final Transcription: '{response.final_transcription.full_transcript}'")
                elif response_type == 'summary_result':
                    print(f"  Summary Result: '{response.summary_result.summary_text}'")
                elif response_type == 'importance_ack':
                    print(f"  Importance Ack: Item='{response.importance_ack.item_name}', Success={response.importance_ack.success}, Msg='{response.importance_ack.message}'")
                elif response_type == 'error':
                    print(f"  Stream Error: Code={response.error.code}, Msg='{response.error.message}'")
                else:
                    print(f"  Unknown response payload: {response}")
            
            print("\n--- Finished receiving all responses ---")

    except grpc.RpcError as e:
        print(f"gRPC call failed: {e.status()} - {e.details()}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("\nClient finished.")

if __name__ == '__main__':
    run_client()
