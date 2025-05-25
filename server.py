from concurrent import futures
import grpc
import time # For simulating work and for _ONE_DAY_IN_SECONDS

import meeting_pb2
import meeting_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class MeetingServicer(meeting_pb2_grpc.MeetingServiceServicer):
    def SaveImportance(self, request, context):
        print(f"SaveImportance called with: {request}")
        # Dummy implementation
        return meeting_pb2.SaveImportanceResponse(success=True, message="Importance saved (stub).")

    def TranscribeAndSummarize(self, request, context):
        print(f"TranscribeAndSummarize called with audio_format: {request.audio_format} and data length: {len(request.audio_data)}")
        # Dummy implementation
        return meeting_pb2.TranscribeAndSummarizeResponse(
            transcription="This is a dummy transcription (stub).",
            summary="This is a dummy summary (stub).",
            error_message=""
        )

    def SaveMetadata(self, request, context):
        print(f"SaveMetadata called with: {request}")
        # Dummy implementation
        return meeting_pb2.SaveMetadataResponse(
            meeting_id="dummy_meeting_id_123",
            success=True,
            message="Metadata saved (stub)."
        )

    def EditMetadata(self, request, context):
        print(f"EditMetadata called with: {request}")
        # Dummy implementation
        return meeting_pb2.EditMetadataResponse(success=True, message="Metadata edited (stub).")

    def DeleteMetadata(self, request, context):
        print(f"DeleteMetadata called with: {request}")
        # Dummy implementation
        return meeting_pb2.DeleteMetadataResponse(success=True, message="Metadata deleted (stub).")

    def ProcessMeeting(self, request_iterator, context):
        print("ProcessMeeting called")
        client_id = context.peer() 
        print(f"Connection from {client_id}")
        
        chunk_count = 0

        try:
            for request in request_iterator:
                request_type = request.WhichOneof('payload')
                print(f"Received request: {request_type}")

                if request_type == 'initial_setup':
                    setup_data = request.initial_setup
                    print(f"  InitialSetup: {setup_data}")
                    # Simulate processing metadata from setup_data.metadata
                    metadata_title = setup_data.metadata.title if setup_data.metadata else "DefaultTitle"
                    
                    response = meeting_pb2.MeetingStreamResponse(
                        confirmation=meeting_pb2.MeetingInitialized(
                            meeting_id=f"fake_meeting_id_for_{metadata_title[:10].replace(' ', '_')}",
                            success=True,
                            message="Meeting initialized successfully."
                        )
                    )
                    yield response
                
                elif request_type == 'audio_chunk':
                    audio_data = request.audio_chunk
                    print(f"  AudioChunk: sequence_no={audio_data.sequence_number}, size={len(audio_data.content)}")
                    chunk_count += 1
                    
                    # Simulate partial transcription
                    partial_response = meeting_pb2.MeetingStreamResponse(
                        partial_transcription=meeting_pb2.PartialTranscription(
                            transcript_segment=f"Partial transcript for chunk {audio_data.sequence_number} (stub).",
                            sequence_number=audio_data.sequence_number,
                            is_interim=True
                        )
                    )
                    yield partial_response
                    
                    # Simulate final transcription and summary after N chunks for testing
                    if chunk_count % 3 == 0: # Example: every 3 chunks
                        time.sleep(0.1) # Simulate processing delay
                        final_transcript_response = meeting_pb2.MeetingStreamResponse(
                            final_transcription=meeting_pb2.FinalTranscription(
                                full_transcript=f"Final transcript up to chunk {audio_data.sequence_number} (stub)."
                            )
                        )
                        yield final_transcript_response
                        
                        summary_response = meeting_pb2.MeetingStreamResponse(
                            summary_result=meeting_pb2.SummaryResult(
                                summary_text="This is a meeting summary based on available transcription (stub)."
                            )
                        )
                        yield summary_response

                elif request_type == 'importance_marker':
                    marker_data = request.importance_marker
                    print(f"  ImportanceMarker: {marker_data}")
                    
                    ack_response = meeting_pb2.MeetingStreamResponse(
                        importance_ack=meeting_pb2.ImportanceSavedAck(
                            item_name=marker_data.item_name,
                            success=True,
                            message="Importance marker saved (stub)."
                        )
                    )
                    yield ack_response
                
                else:
                    # This case should ideally not be reached if protobuf handles `oneof` correctly
                    # and client sends valid messages.
                    print(f"  Unknown or unset payload in request: {request}")
                    error_response = meeting_pb2.MeetingStreamResponse(
                        error=meeting_pb2.StreamError(
                            code=grpc.StatusCode.INVALID_ARGUMENT.value[0], 
                            message=f"Unknown or unset payload in request."
                        )
                    )
                    yield error_response
                    
        except grpc.RpcError as e:
            print(f"RpcError during ProcessMeeting for {client_id}: {e}")
            # Example of how to inform client, though stream might be broken
            # error_response = meeting_pb2.MeetingStreamResponse(
            #     error=meeting_pb2.StreamError(
            #         code=e.code().value[0] if hasattr(e.code(), 'value') else grpc.StatusCode.UNKNOWN.value[0],
            #         message=f"RpcError: {e.details()}"
            #     )
            # )
            # try:
            #    yield error_response
            # except Exception as ex_yield:
            #    print(f"Failed to yield RpcError details to client: {ex_yield}")
        except Exception as e:
            print(f"General exception in ProcessMeeting for {client_id}: {e}")
            # error_response = meeting_pb2.MeetingStreamResponse(
            #     error=meeting_pb2.StreamError(
            #         code=grpc.StatusCode.INTERNAL.value[0],
            #         message=f"Internal server error: {type(e).__name__}"
            #     )
            # )
            # try:
            #    yield error_response
            # except Exception as ex_yield:
            #    print(f"Failed to yield General Exception details to client: {ex_yield}")
        finally:
            print(f"Client stream processing ended for {client_id}.")
            # Example: send a final status message if context is still active
            # if context.is_active():
            #     final_status_response = meeting_pb2.MeetingStreamResponse(
            #         error=meeting_pb2.StreamError(message="Stream processing finished.", code=0) # 0 for OK or a custom code
            #     )
            #     try:
            #         yield final_status_response
            #     except Exception as e:
            #         print(f"Error sending final status message: {e}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    meeting_pb2_grpc.add_MeetingServiceServicer_to_server(MeetingServicer(), server)
    
    port = "[::]:50051" # Listen on all available IPv4 and IPv6 addresses
    server.add_insecure_port(port)
    
    print(f"Starting server. Listening on port {port}")
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        print("Server stopping...")
        server.stop(0)
        print("Server stopped.")

if __name__ == '__main__':
    serve()
