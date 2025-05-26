// package: meeting
// file: meeting.proto

import * as jspb from "google-protobuf";

export class SaveImportanceRequest extends jspb.Message {
  getItemName(): string;
  setItemName(value: string): void;

  getImportance(): number;
  setImportance(value: number): void;

  getDetails(): string;
  setDetails(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): SaveImportanceRequest.AsObject;
  static toObject(includeInstance: boolean, msg: SaveImportanceRequest): SaveImportanceRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: SaveImportanceRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): SaveImportanceRequest;
  static deserializeBinaryFromReader(message: SaveImportanceRequest, reader: jspb.BinaryReader): SaveImportanceRequest;
}

export namespace SaveImportanceRequest {
  export type AsObject = {
    itemName: string,
    importance: number,
    details: string,
  }
}

export class SaveImportanceResponse extends jspb.Message {
  getSuccess(): boolean;
  setSuccess(value: boolean): void;

  getMessage(): string;
  setMessage(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): SaveImportanceResponse.AsObject;
  static toObject(includeInstance: boolean, msg: SaveImportanceResponse): SaveImportanceResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: SaveImportanceResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): SaveImportanceResponse;
  static deserializeBinaryFromReader(message: SaveImportanceResponse, reader: jspb.BinaryReader): SaveImportanceResponse;
}

export namespace SaveImportanceResponse {
  export type AsObject = {
    success: boolean,
    message: string,
  }
}

export class TranscribeAndSummarizeRequest extends jspb.Message {
  getAudioData(): Uint8Array | string;
  getAudioData_asU8(): Uint8Array;
  getAudioData_asB64(): string;
  setAudioData(value: Uint8Array | string): void;

  getAudioFormat(): string;
  setAudioFormat(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): TranscribeAndSummarizeRequest.AsObject;
  static toObject(includeInstance: boolean, msg: TranscribeAndSummarizeRequest): TranscribeAndSummarizeRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: TranscribeAndSummarizeRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): TranscribeAndSummarizeRequest;
  static deserializeBinaryFromReader(message: TranscribeAndSummarizeRequest, reader: jspb.BinaryReader): TranscribeAndSummarizeRequest;
}

export namespace TranscribeAndSummarizeRequest {
  export type AsObject = {
    audioData: Uint8Array | string,
    audioFormat: string,
  }
}

export class TranscribeAndSummarizeResponse extends jspb.Message {
  getTranscription(): string;
  setTranscription(value: string): void;

  getSummary(): string;
  setSummary(value: string): void;

  getErrorMessage(): string;
  setErrorMessage(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): TranscribeAndSummarizeResponse.AsObject;
  static toObject(includeInstance: boolean, msg: TranscribeAndSummarizeResponse): TranscribeAndSummarizeResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: TranscribeAndSummarizeResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): TranscribeAndSummarizeResponse;
  static deserializeBinaryFromReader(message: TranscribeAndSummarizeResponse, reader: jspb.BinaryReader): TranscribeAndSummarizeResponse;
}

export namespace TranscribeAndSummarizeResponse {
  export type AsObject = {
    transcription: string,
    summary: string,
    errorMessage: string,
  }
}

export class SaveMetadataRequest extends jspb.Message {
  getTitle(): string;
  setTitle(value: string): void;

  getMeetingDate(): string;
  setMeetingDate(value: string): void;

  clearAttendeesList(): void;
  getAttendeesList(): Array<string>;
  setAttendeesList(value: Array<string>): void;
  addAttendees(value: string, index?: number): string;

  getAdditionalInfo(): string;
  setAdditionalInfo(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): SaveMetadataRequest.AsObject;
  static toObject(includeInstance: boolean, msg: SaveMetadataRequest): SaveMetadataRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: SaveMetadataRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): SaveMetadataRequest;
  static deserializeBinaryFromReader(message: SaveMetadataRequest, reader: jspb.BinaryReader): SaveMetadataRequest;
}

export namespace SaveMetadataRequest {
  export type AsObject = {
    title: string,
    meetingDate: string,
    attendeesList: Array<string>,
    additionalInfo: string,
  }
}

export class SaveMetadataResponse extends jspb.Message {
  getMeetingId(): string;
  setMeetingId(value: string): void;

  getSuccess(): boolean;
  setSuccess(value: boolean): void;

  getMessage(): string;
  setMessage(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): SaveMetadataResponse.AsObject;
  static toObject(includeInstance: boolean, msg: SaveMetadataResponse): SaveMetadataResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: SaveMetadataResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): SaveMetadataResponse;
  static deserializeBinaryFromReader(message: SaveMetadataResponse, reader: jspb.BinaryReader): SaveMetadataResponse;
}

export namespace SaveMetadataResponse {
  export type AsObject = {
    meetingId: string,
    success: boolean,
    message: string,
  }
}

export class EditMetadataRequest extends jspb.Message {
  getMeetingId(): string;
  setMeetingId(value: string): void;

  hasTitle(): boolean;
  clearTitle(): void;
  getTitle(): string;
  setTitle(value: string): void;

  hasMeetingDate(): boolean;
  clearMeetingDate(): void;
  getMeetingDate(): string;
  setMeetingDate(value: string): void;

  clearAttendeesList(): void;
  getAttendeesList(): Array<string>;
  setAttendeesList(value: Array<string>): void;
  addAttendees(value: string, index?: number): string;

  hasAdditionalInfo(): boolean;
  clearAdditionalInfo(): void;
  getAdditionalInfo(): string;
  setAdditionalInfo(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): EditMetadataRequest.AsObject;
  static toObject(includeInstance: boolean, msg: EditMetadataRequest): EditMetadataRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: EditMetadataRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): EditMetadataRequest;
  static deserializeBinaryFromReader(message: EditMetadataRequest, reader: jspb.BinaryReader): EditMetadataRequest;
}

export namespace EditMetadataRequest {
  export type AsObject = {
    meetingId: string,
    title: string,
    meetingDate: string,
    attendeesList: Array<string>,
    additionalInfo: string,
  }
}

export class EditMetadataResponse extends jspb.Message {
  getSuccess(): boolean;
  setSuccess(value: boolean): void;

  getMessage(): string;
  setMessage(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): EditMetadataResponse.AsObject;
  static toObject(includeInstance: boolean, msg: EditMetadataResponse): EditMetadataResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: EditMetadataResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): EditMetadataResponse;
  static deserializeBinaryFromReader(message: EditMetadataResponse, reader: jspb.BinaryReader): EditMetadataResponse;
}

export namespace EditMetadataResponse {
  export type AsObject = {
    success: boolean,
    message: string,
  }
}

export class DeleteMetadataRequest extends jspb.Message {
  getMeetingId(): string;
  setMeetingId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeleteMetadataRequest.AsObject;
  static toObject(includeInstance: boolean, msg: DeleteMetadataRequest): DeleteMetadataRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeleteMetadataRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeleteMetadataRequest;
  static deserializeBinaryFromReader(message: DeleteMetadataRequest, reader: jspb.BinaryReader): DeleteMetadataRequest;
}

export namespace DeleteMetadataRequest {
  export type AsObject = {
    meetingId: string,
  }
}

export class DeleteMetadataResponse extends jspb.Message {
  getSuccess(): boolean;
  setSuccess(value: boolean): void;

  getMessage(): string;
  setMessage(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeleteMetadataResponse.AsObject;
  static toObject(includeInstance: boolean, msg: DeleteMetadataResponse): DeleteMetadataResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeleteMetadataResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeleteMetadataResponse;
  static deserializeBinaryFromReader(message: DeleteMetadataResponse, reader: jspb.BinaryReader): DeleteMetadataResponse;
}

export namespace DeleteMetadataResponse {
  export type AsObject = {
    success: boolean,
    message: string,
  }
}

export class MeetingStreamRequest extends jspb.Message {
  hasInitialSetup(): boolean;
  clearInitialSetup(): void;
  getInitialSetup(): InitialSetup | undefined;
  setInitialSetup(value?: InitialSetup): void;

  hasAudioChunk(): boolean;
  clearAudioChunk(): void;
  getAudioChunk(): AudioChunk | undefined;
  setAudioChunk(value?: AudioChunk): void;

  hasImportanceMarker(): boolean;
  clearImportanceMarker(): void;
  getImportanceMarker(): ImportanceMarker | undefined;
  setImportanceMarker(value?: ImportanceMarker): void;

  getPayloadCase(): MeetingStreamRequest.PayloadCase;
  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): MeetingStreamRequest.AsObject;
  static toObject(includeInstance: boolean, msg: MeetingStreamRequest): MeetingStreamRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: MeetingStreamRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): MeetingStreamRequest;
  static deserializeBinaryFromReader(message: MeetingStreamRequest, reader: jspb.BinaryReader): MeetingStreamRequest;
}

export namespace MeetingStreamRequest {
  export type AsObject = {
    initialSetup?: InitialSetup.AsObject,
    audioChunk?: AudioChunk.AsObject,
    importanceMarker?: ImportanceMarker.AsObject,
  }

  export enum PayloadCase {
    PAYLOAD_NOT_SET = 0,
    INITIAL_SETUP = 1,
    AUDIO_CHUNK = 2,
    IMPORTANCE_MARKER = 3,
  }
}

export class InitialSetup extends jspb.Message {
  getMeetingId(): string;
  setMeetingId(value: string): void;

  getAudioFormat(): string;
  setAudioFormat(value: string): void;

  hasMetadata(): boolean;
  clearMetadata(): void;
  getMetadata(): SaveMetadataRequest | undefined;
  setMetadata(value?: SaveMetadataRequest): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): InitialSetup.AsObject;
  static toObject(includeInstance: boolean, msg: InitialSetup): InitialSetup.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: InitialSetup, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): InitialSetup;
  static deserializeBinaryFromReader(message: InitialSetup, reader: jspb.BinaryReader): InitialSetup;
}

export namespace InitialSetup {
  export type AsObject = {
    meetingId: string,
    audioFormat: string,
    metadata?: SaveMetadataRequest.AsObject,
  }
}

export class AudioChunk extends jspb.Message {
  getContent(): Uint8Array | string;
  getContent_asU8(): Uint8Array;
  getContent_asB64(): string;
  setContent(value: Uint8Array | string): void;

  getSequenceNumber(): number;
  setSequenceNumber(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): AudioChunk.AsObject;
  static toObject(includeInstance: boolean, msg: AudioChunk): AudioChunk.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: AudioChunk, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): AudioChunk;
  static deserializeBinaryFromReader(message: AudioChunk, reader: jspb.BinaryReader): AudioChunk;
}

export namespace AudioChunk {
  export type AsObject = {
    content: Uint8Array | string,
    sequenceNumber: number,
  }
}

export class ImportanceMarker extends jspb.Message {
  getItemName(): string;
  setItemName(value: string): void;

  getImportanceScore(): number;
  setImportanceScore(value: number): void;

  getDetails(): string;
  setDetails(value: string): void;

  getTimestampMs(): number;
  setTimestampMs(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ImportanceMarker.AsObject;
  static toObject(includeInstance: boolean, msg: ImportanceMarker): ImportanceMarker.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ImportanceMarker, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ImportanceMarker;
  static deserializeBinaryFromReader(message: ImportanceMarker, reader: jspb.BinaryReader): ImportanceMarker;
}

export namespace ImportanceMarker {
  export type AsObject = {
    itemName: string,
    importanceScore: number,
    details: string,
    timestampMs: number,
  }
}

export class MeetingStreamResponse extends jspb.Message {
  hasConfirmation(): boolean;
  clearConfirmation(): void;
  getConfirmation(): MeetingInitialized | undefined;
  setConfirmation(value?: MeetingInitialized): void;

  hasPartialTranscription(): boolean;
  clearPartialTranscription(): void;
  getPartialTranscription(): PartialTranscription | undefined;
  setPartialTranscription(value?: PartialTranscription): void;

  hasFinalTranscription(): boolean;
  clearFinalTranscription(): void;
  getFinalTranscription(): FinalTranscription | undefined;
  setFinalTranscription(value?: FinalTranscription): void;

  hasSummaryResult(): boolean;
  clearSummaryResult(): void;
  getSummaryResult(): SummaryResult | undefined;
  setSummaryResult(value?: SummaryResult): void;

  hasImportanceAck(): boolean;
  clearImportanceAck(): void;
  getImportanceAck(): ImportanceSavedAck | undefined;
  setImportanceAck(value?: ImportanceSavedAck): void;

  hasError(): boolean;
  clearError(): void;
  getError(): StreamError | undefined;
  setError(value?: StreamError): void;

  getPayloadCase(): MeetingStreamResponse.PayloadCase;
  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): MeetingStreamResponse.AsObject;
  static toObject(includeInstance: boolean, msg: MeetingStreamResponse): MeetingStreamResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: MeetingStreamResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): MeetingStreamResponse;
  static deserializeBinaryFromReader(message: MeetingStreamResponse, reader: jspb.BinaryReader): MeetingStreamResponse;
}

export namespace MeetingStreamResponse {
  export type AsObject = {
    confirmation?: MeetingInitialized.AsObject,
    partialTranscription?: PartialTranscription.AsObject,
    finalTranscription?: FinalTranscription.AsObject,
    summaryResult?: SummaryResult.AsObject,
    importanceAck?: ImportanceSavedAck.AsObject,
    error?: StreamError.AsObject,
  }

  export enum PayloadCase {
    PAYLOAD_NOT_SET = 0,
    CONFIRMATION = 1,
    PARTIAL_TRANSCRIPTION = 2,
    FINAL_TRANSCRIPTION = 3,
    SUMMARY_RESULT = 4,
    IMPORTANCE_ACK = 5,
    ERROR = 6,
  }
}

export class MeetingInitialized extends jspb.Message {
  getMeetingId(): string;
  setMeetingId(value: string): void;

  getSuccess(): boolean;
  setSuccess(value: boolean): void;

  getMessage(): string;
  setMessage(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): MeetingInitialized.AsObject;
  static toObject(includeInstance: boolean, msg: MeetingInitialized): MeetingInitialized.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: MeetingInitialized, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): MeetingInitialized;
  static deserializeBinaryFromReader(message: MeetingInitialized, reader: jspb.BinaryReader): MeetingInitialized;
}

export namespace MeetingInitialized {
  export type AsObject = {
    meetingId: string,
    success: boolean,
    message: string,
  }
}

export class PartialTranscription extends jspb.Message {
  getTranscriptSegment(): string;
  setTranscriptSegment(value: string): void;

  getSequenceNumber(): number;
  setSequenceNumber(value: number): void;

  getIsInterim(): boolean;
  setIsInterim(value: boolean): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): PartialTranscription.AsObject;
  static toObject(includeInstance: boolean, msg: PartialTranscription): PartialTranscription.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: PartialTranscription, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): PartialTranscription;
  static deserializeBinaryFromReader(message: PartialTranscription, reader: jspb.BinaryReader): PartialTranscription;
}

export namespace PartialTranscription {
  export type AsObject = {
    transcriptSegment: string,
    sequenceNumber: number,
    isInterim: boolean,
  }
}

export class FinalTranscription extends jspb.Message {
  getFullTranscript(): string;
  setFullTranscript(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): FinalTranscription.AsObject;
  static toObject(includeInstance: boolean, msg: FinalTranscription): FinalTranscription.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: FinalTranscription, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): FinalTranscription;
  static deserializeBinaryFromReader(message: FinalTranscription, reader: jspb.BinaryReader): FinalTranscription;
}

export namespace FinalTranscription {
  export type AsObject = {
    fullTranscript: string,
  }
}

export class SummaryResult extends jspb.Message {
  getSummaryText(): string;
  setSummaryText(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): SummaryResult.AsObject;
  static toObject(includeInstance: boolean, msg: SummaryResult): SummaryResult.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: SummaryResult, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): SummaryResult;
  static deserializeBinaryFromReader(message: SummaryResult, reader: jspb.BinaryReader): SummaryResult;
}

export namespace SummaryResult {
  export type AsObject = {
    summaryText: string,
  }
}

export class ImportanceSavedAck extends jspb.Message {
  getItemName(): string;
  setItemName(value: string): void;

  getSuccess(): boolean;
  setSuccess(value: boolean): void;

  getMessage(): string;
  setMessage(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ImportanceSavedAck.AsObject;
  static toObject(includeInstance: boolean, msg: ImportanceSavedAck): ImportanceSavedAck.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ImportanceSavedAck, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ImportanceSavedAck;
  static deserializeBinaryFromReader(message: ImportanceSavedAck, reader: jspb.BinaryReader): ImportanceSavedAck;
}

export namespace ImportanceSavedAck {
  export type AsObject = {
    itemName: string,
    success: boolean,
    message: string,
  }
}

export class StreamError extends jspb.Message {
  getCode(): number;
  setCode(value: number): void;

  getMessage(): string;
  setMessage(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): StreamError.AsObject;
  static toObject(includeInstance: boolean, msg: StreamError): StreamError.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: StreamError, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): StreamError;
  static deserializeBinaryFromReader(message: StreamError, reader: jspb.BinaryReader): StreamError;
}

export namespace StreamError {
  export type AsObject = {
    code: number,
    message: string,
  }
}

