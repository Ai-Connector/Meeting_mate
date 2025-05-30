// package: counter
// file: counter.proto

var counter_pb = require("./counter_pb");
var grpc = require("@improbable-eng/grpc-web").grpc;

var Counter = (function () {
  function Counter() {}
  Counter.serviceName = "counter.Counter";
  return Counter;
}());

Counter.CountCharacters = {
  methodName: "CountCharacters",
  service: Counter,
  requestStream: true,
  responseStream: true,
  requestType: counter_pb.CharacterRequest,
  responseType: counter_pb.CharacterResponse
};

exports.Counter = Counter;

function CounterClient(serviceHost, options) {
  this.serviceHost = serviceHost;
  this.options = options || {};
}

CounterClient.prototype.countCharacters = function countCharacters(metadata) {
  var listeners = {
    data: [],
    end: [],
    status: []
  };
  var client = grpc.client(Counter.CountCharacters, {
    host: this.serviceHost,
    metadata: metadata,
    transport: this.options.transport
  });
  client.onEnd(function (status, statusMessage, trailers) {
    listeners.status.forEach(function (handler) {
      handler({ code: status, details: statusMessage, metadata: trailers });
    });
    listeners.end.forEach(function (handler) {
      handler({ code: status, details: statusMessage, metadata: trailers });
    });
    listeners = null;
  });
  client.onMessage(function (message) {
    listeners.data.forEach(function (handler) {
      handler(message);
    })
  });
  client.start(metadata);
  return {
    on: function (type, handler) {
      listeners[type].push(handler);
      return this;
    },
    write: function (requestMessage) {
      client.send(requestMessage);
      return this;
    },
    end: function () {
      client.finishSend();
    },
    cancel: function () {
      listeners = null;
      client.close();
    }
  };
};

exports.CounterClient = CounterClient;

