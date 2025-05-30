// package: counter
// file: counter.proto

import * as jspb from "google-protobuf";

export class CharacterRequest extends jspb.Message {
  getText(): string;
  setText(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CharacterRequest.AsObject;
  static toObject(includeInstance: boolean, msg: CharacterRequest): CharacterRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: CharacterRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CharacterRequest;
  static deserializeBinaryFromReader(message: CharacterRequest, reader: jspb.BinaryReader): CharacterRequest;
}

export namespace CharacterRequest {
  export type AsObject = {
    text: string,
  }
}

export class CharacterResponse extends jspb.Message {
  getCount(): number;
  setCount(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CharacterResponse.AsObject;
  static toObject(includeInstance: boolean, msg: CharacterResponse): CharacterResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: CharacterResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CharacterResponse;
  static deserializeBinaryFromReader(message: CharacterResponse, reader: jspb.BinaryReader): CharacterResponse;
}

export namespace CharacterResponse {
  export type AsObject = {
    count: number,
  }
}

