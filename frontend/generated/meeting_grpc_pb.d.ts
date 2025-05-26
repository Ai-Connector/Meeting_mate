// GENERATED CODE -- DO NOT EDIT!

// package: meeting
// file: meeting.proto

import * as meeting_pb from "./meeting_pb";
import * as grpc from "grpc";

interface IMeetingServiceService extends grpc.ServiceDefinition<grpc.UntypedServiceImplementation> {
  saveImportance: grpc.MethodDefinition<meeting_pb.SaveImportanceRequest, meeting_pb.SaveImportanceResponse>;
  transcribeAndSummarize: grpc.MethodDefinition<meeting_pb.TranscribeAndSummarizeRequest, meeting_pb.TranscribeAndSummarizeResponse>;
  saveMetadata: grpc.MethodDefinition<meeting_pb.SaveMetadataRequest, meeting_pb.SaveMetadataResponse>;
  editMetadata: grpc.MethodDefinition<meeting_pb.EditMetadataRequest, meeting_pb.EditMetadataResponse>;
  deleteMetadata: grpc.MethodDefinition<meeting_pb.DeleteMetadataRequest, meeting_pb.DeleteMetadataResponse>;
  processMeeting: grpc.MethodDefinition<meeting_pb.MeetingStreamRequest, meeting_pb.MeetingStreamResponse>;
}

export const MeetingServiceService: IMeetingServiceService;

export interface IMeetingServiceServer extends grpc.UntypedServiceImplementation {
  saveImportance: grpc.handleUnaryCall<meeting_pb.SaveImportanceRequest, meeting_pb.SaveImportanceResponse>;
  transcribeAndSummarize: grpc.handleUnaryCall<meeting_pb.TranscribeAndSummarizeRequest, meeting_pb.TranscribeAndSummarizeResponse>;
  saveMetadata: grpc.handleUnaryCall<meeting_pb.SaveMetadataRequest, meeting_pb.SaveMetadataResponse>;
  editMetadata: grpc.handleUnaryCall<meeting_pb.EditMetadataRequest, meeting_pb.EditMetadataResponse>;
  deleteMetadata: grpc.handleUnaryCall<meeting_pb.DeleteMetadataRequest, meeting_pb.DeleteMetadataResponse>;
  processMeeting: grpc.handleBidiStreamingCall<meeting_pb.MeetingStreamRequest, meeting_pb.MeetingStreamResponse>;
}

export class MeetingServiceClient extends grpc.Client {
  constructor(address: string, credentials: grpc.ChannelCredentials, options?: object);
  saveImportance(argument: meeting_pb.SaveImportanceRequest, callback: grpc.requestCallback<meeting_pb.SaveImportanceResponse>): grpc.ClientUnaryCall;
  saveImportance(argument: meeting_pb.SaveImportanceRequest, metadataOrOptions: grpc.Metadata | grpc.CallOptions | null, callback: grpc.requestCallback<meeting_pb.SaveImportanceResponse>): grpc.ClientUnaryCall;
  saveImportance(argument: meeting_pb.SaveImportanceRequest, metadata: grpc.Metadata | null, options: grpc.CallOptions | null, callback: grpc.requestCallback<meeting_pb.SaveImportanceResponse>): grpc.ClientUnaryCall;
  transcribeAndSummarize(argument: meeting_pb.TranscribeAndSummarizeRequest, callback: grpc.requestCallback<meeting_pb.TranscribeAndSummarizeResponse>): grpc.ClientUnaryCall;
  transcribeAndSummarize(argument: meeting_pb.TranscribeAndSummarizeRequest, metadataOrOptions: grpc.Metadata | grpc.CallOptions | null, callback: grpc.requestCallback<meeting_pb.TranscribeAndSummarizeResponse>): grpc.ClientUnaryCall;
  transcribeAndSummarize(argument: meeting_pb.TranscribeAndSummarizeRequest, metadata: grpc.Metadata | null, options: grpc.CallOptions | null, callback: grpc.requestCallback<meeting_pb.TranscribeAndSummarizeResponse>): grpc.ClientUnaryCall;
  saveMetadata(argument: meeting_pb.SaveMetadataRequest, callback: grpc.requestCallback<meeting_pb.SaveMetadataResponse>): grpc.ClientUnaryCall;
  saveMetadata(argument: meeting_pb.SaveMetadataRequest, metadataOrOptions: grpc.Metadata | grpc.CallOptions | null, callback: grpc.requestCallback<meeting_pb.SaveMetadataResponse>): grpc.ClientUnaryCall;
  saveMetadata(argument: meeting_pb.SaveMetadataRequest, metadata: grpc.Metadata | null, options: grpc.CallOptions | null, callback: grpc.requestCallback<meeting_pb.SaveMetadataResponse>): grpc.ClientUnaryCall;
  editMetadata(argument: meeting_pb.EditMetadataRequest, callback: grpc.requestCallback<meeting_pb.EditMetadataResponse>): grpc.ClientUnaryCall;
  editMetadata(argument: meeting_pb.EditMetadataRequest, metadataOrOptions: grpc.Metadata | grpc.CallOptions | null, callback: grpc.requestCallback<meeting_pb.EditMetadataResponse>): grpc.ClientUnaryCall;
  editMetadata(argument: meeting_pb.EditMetadataRequest, metadata: grpc.Metadata | null, options: grpc.CallOptions | null, callback: grpc.requestCallback<meeting_pb.EditMetadataResponse>): grpc.ClientUnaryCall;
  deleteMetadata(argument: meeting_pb.DeleteMetadataRequest, callback: grpc.requestCallback<meeting_pb.DeleteMetadataResponse>): grpc.ClientUnaryCall;
  deleteMetadata(argument: meeting_pb.DeleteMetadataRequest, metadataOrOptions: grpc.Metadata | grpc.CallOptions | null, callback: grpc.requestCallback<meeting_pb.DeleteMetadataResponse>): grpc.ClientUnaryCall;
  deleteMetadata(argument: meeting_pb.DeleteMetadataRequest, metadata: grpc.Metadata | null, options: grpc.CallOptions | null, callback: grpc.requestCallback<meeting_pb.DeleteMetadataResponse>): grpc.ClientUnaryCall;
  processMeeting(metadataOrOptions?: grpc.Metadata | grpc.CallOptions | null): grpc.ClientDuplexStream<meeting_pb.MeetingStreamRequest, meeting_pb.MeetingStreamResponse>;
  processMeeting(metadata?: grpc.Metadata | null, options?: grpc.CallOptions | null): grpc.ClientDuplexStream<meeting_pb.MeetingStreamRequest, meeting_pb.MeetingStreamResponse>;
}
