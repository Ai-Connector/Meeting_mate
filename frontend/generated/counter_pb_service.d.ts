// package: counter
// file: counter.proto

import * as counter_pb from "./counter_pb";
import {grpc} from "@improbable-eng/grpc-web";

type CounterCountCharacters = {
  readonly methodName: string;
  readonly service: typeof Counter;
  readonly requestStream: true;
  readonly responseStream: true;
  readonly requestType: typeof counter_pb.CharacterRequest;
  readonly responseType: typeof counter_pb.CharacterResponse;
};

export class Counter {
  static readonly serviceName: string;
  static readonly CountCharacters: CounterCountCharacters;
}

export type ServiceError = { message: string, code: number; metadata: grpc.Metadata }
export type Status = { details: string, code: number; metadata: grpc.Metadata }

interface UnaryResponse {
  cancel(): void;
}
interface ResponseStream<T> {
  cancel(): void;
  on(type: 'data', handler: (message: T) => void): ResponseStream<T>;
  on(type: 'end', handler: (status?: Status) => void): ResponseStream<T>;
  on(type: 'status', handler: (status: Status) => void): ResponseStream<T>;
}
interface RequestStream<T> {
  write(message: T): RequestStream<T>;
  end(): void;
  cancel(): void;
  on(type: 'end', handler: (status?: Status) => void): RequestStream<T>;
  on(type: 'status', handler: (status: Status) => void): RequestStream<T>;
}
interface BidirectionalStream<ReqT, ResT> {
  write(message: ReqT): BidirectionalStream<ReqT, ResT>;
  end(): void;
  cancel(): void;
  on(type: 'data', handler: (message: ResT) => void): BidirectionalStream<ReqT, ResT>;
  on(type: 'end', handler: (status?: Status) => void): BidirectionalStream<ReqT, ResT>;
  on(type: 'status', handler: (status: Status) => void): BidirectionalStream<ReqT, ResT>;
}

export class CounterClient {
  readonly serviceHost: string;

  constructor(serviceHost: string, options?: grpc.RpcOptions);
  countCharacters(metadata?: grpc.Metadata): BidirectionalStream<counter_pb.CharacterRequest, counter_pb.CharacterResponse>;
}

