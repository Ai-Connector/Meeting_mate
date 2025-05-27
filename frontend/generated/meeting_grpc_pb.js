// GENERATED CODE -- DO NOT EDIT!

'use strict';
var grpc = require('@grpc/grpc-js');
var meeting_pb = require('./meeting_pb.js');

function serialize_meeting_DeleteMetadataRequest(arg) {
  if (!(arg instanceof meeting_pb.DeleteMetadataRequest)) {
    throw new Error('Expected argument of type meeting.DeleteMetadataRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_meeting_DeleteMetadataRequest(buffer_arg) {
  return meeting_pb.DeleteMetadataRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_meeting_DeleteMetadataResponse(arg) {
  if (!(arg instanceof meeting_pb.DeleteMetadataResponse)) {
    throw new Error('Expected argument of type meeting.DeleteMetadataResponse');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_meeting_DeleteMetadataResponse(buffer_arg) {
  return meeting_pb.DeleteMetadataResponse.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_meeting_EditMetadataRequest(arg) {
  if (!(arg instanceof meeting_pb.EditMetadataRequest)) {
    throw new Error('Expected argument of type meeting.EditMetadataRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_meeting_EditMetadataRequest(buffer_arg) {
  return meeting_pb.EditMetadataRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_meeting_EditMetadataResponse(arg) {
  if (!(arg instanceof meeting_pb.EditMetadataResponse)) {
    throw new Error('Expected argument of type meeting.EditMetadataResponse');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_meeting_EditMetadataResponse(buffer_arg) {
  return meeting_pb.EditMetadataResponse.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_meeting_MeetingStreamRequest(arg) {
  if (!(arg instanceof meeting_pb.MeetingStreamRequest)) {
    throw new Error('Expected argument of type meeting.MeetingStreamRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_meeting_MeetingStreamRequest(buffer_arg) {
  return meeting_pb.MeetingStreamRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_meeting_MeetingStreamResponse(arg) {
  if (!(arg instanceof meeting_pb.MeetingStreamResponse)) {
    throw new Error('Expected argument of type meeting.MeetingStreamResponse');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_meeting_MeetingStreamResponse(buffer_arg) {
  return meeting_pb.MeetingStreamResponse.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_meeting_SaveImportanceRequest(arg) {
  if (!(arg instanceof meeting_pb.SaveImportanceRequest)) {
    throw new Error('Expected argument of type meeting.SaveImportanceRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_meeting_SaveImportanceRequest(buffer_arg) {
  return meeting_pb.SaveImportanceRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_meeting_SaveImportanceResponse(arg) {
  if (!(arg instanceof meeting_pb.SaveImportanceResponse)) {
    throw new Error('Expected argument of type meeting.SaveImportanceResponse');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_meeting_SaveImportanceResponse(buffer_arg) {
  return meeting_pb.SaveImportanceResponse.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_meeting_SaveMetadataRequest(arg) {
  if (!(arg instanceof meeting_pb.SaveMetadataRequest)) {
    throw new Error('Expected argument of type meeting.SaveMetadataRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_meeting_SaveMetadataRequest(buffer_arg) {
  return meeting_pb.SaveMetadataRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_meeting_SaveMetadataResponse(arg) {
  if (!(arg instanceof meeting_pb.SaveMetadataResponse)) {
    throw new Error('Expected argument of type meeting.SaveMetadataResponse');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_meeting_SaveMetadataResponse(buffer_arg) {
  return meeting_pb.SaveMetadataResponse.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_meeting_TranscribeAndSummarizeRequest(arg) {
  if (!(arg instanceof meeting_pb.TranscribeAndSummarizeRequest)) {
    throw new Error('Expected argument of type meeting.TranscribeAndSummarizeRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_meeting_TranscribeAndSummarizeRequest(buffer_arg) {
  return meeting_pb.TranscribeAndSummarizeRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_meeting_TranscribeAndSummarizeResponse(arg) {
  if (!(arg instanceof meeting_pb.TranscribeAndSummarizeResponse)) {
    throw new Error('Expected argument of type meeting.TranscribeAndSummarizeResponse');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_meeting_TranscribeAndSummarizeResponse(buffer_arg) {
  return meeting_pb.TranscribeAndSummarizeResponse.deserializeBinary(new Uint8Array(buffer_arg));
}


var MeetingServiceService = exports.MeetingServiceService = {
  // Keep existing unary methods for now as per instruction to modify current server.
// We will later evaluate if they should be removed or if this new stream replaces them.
saveImportance: {
    path: '/meeting.MeetingService/SaveImportance',
    requestStream: false,
    responseStream: false,
    requestType: meeting_pb.SaveImportanceRequest,
    responseType: meeting_pb.SaveImportanceResponse,
    requestSerialize: serialize_meeting_SaveImportanceRequest,
    requestDeserialize: deserialize_meeting_SaveImportanceRequest,
    responseSerialize: serialize_meeting_SaveImportanceResponse,
    responseDeserialize: deserialize_meeting_SaveImportanceResponse,
  },
  transcribeAndSummarize: {
    path: '/meeting.MeetingService/TranscribeAndSummarize',
    requestStream: false,
    responseStream: false,
    requestType: meeting_pb.TranscribeAndSummarizeRequest,
    responseType: meeting_pb.TranscribeAndSummarizeResponse,
    requestSerialize: serialize_meeting_TranscribeAndSummarizeRequest,
    requestDeserialize: deserialize_meeting_TranscribeAndSummarizeRequest,
    responseSerialize: serialize_meeting_TranscribeAndSummarizeResponse,
    responseDeserialize: deserialize_meeting_TranscribeAndSummarizeResponse,
  },
  saveMetadata: {
    path: '/meeting.MeetingService/SaveMetadata',
    requestStream: false,
    responseStream: false,
    requestType: meeting_pb.SaveMetadataRequest,
    responseType: meeting_pb.SaveMetadataResponse,
    requestSerialize: serialize_meeting_SaveMetadataRequest,
    requestDeserialize: deserialize_meeting_SaveMetadataRequest,
    responseSerialize: serialize_meeting_SaveMetadataResponse,
    responseDeserialize: deserialize_meeting_SaveMetadataResponse,
  },
  editMetadata: {
    path: '/meeting.MeetingService/EditMetadata',
    requestStream: false,
    responseStream: false,
    requestType: meeting_pb.EditMetadataRequest,
    responseType: meeting_pb.EditMetadataResponse,
    requestSerialize: serialize_meeting_EditMetadataRequest,
    requestDeserialize: deserialize_meeting_EditMetadataRequest,
    responseSerialize: serialize_meeting_EditMetadataResponse,
    responseDeserialize: deserialize_meeting_EditMetadataResponse,
  },
  deleteMetadata: {
    path: '/meeting.MeetingService/DeleteMetadata',
    requestStream: false,
    responseStream: false,
    requestType: meeting_pb.DeleteMetadataRequest,
    responseType: meeting_pb.DeleteMetadataResponse,
    requestSerialize: serialize_meeting_DeleteMetadataRequest,
    requestDeserialize: deserialize_meeting_DeleteMetadataRequest,
    responseSerialize: serialize_meeting_DeleteMetadataResponse,
    responseDeserialize: deserialize_meeting_DeleteMetadataResponse,
  },
  // New bidirectional streaming RPC
processMeeting: {
    path: '/meeting.MeetingService/ProcessMeeting',
    requestStream: true,
    responseStream: true,
    requestType: meeting_pb.MeetingStreamRequest,
    responseType: meeting_pb.MeetingStreamResponse,
    requestSerialize: serialize_meeting_MeetingStreamRequest,
    requestDeserialize: deserialize_meeting_MeetingStreamRequest,
    responseSerialize: serialize_meeting_MeetingStreamResponse,
    responseDeserialize: deserialize_meeting_MeetingStreamResponse,
  },
};

exports.MeetingServiceClient = grpc.makeGenericClientConstructor(MeetingServiceService, 'MeetingService');
