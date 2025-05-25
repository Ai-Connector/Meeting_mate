from concurrent import futures
import grpc
import time

import meeting_pb2_grpc
from meeting_servicer import MeetingServicer

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

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
