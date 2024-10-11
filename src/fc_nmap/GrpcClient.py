import grpc
from . fcproto import rpc_pb2, rpc_pb2_grpc

from . fcproto.request_response_pb2 import (
    ContactInfoResponse, Empty,
    HubInfoResponse, HubInfoRequest, FidRequest, MessagesResponse,
    )

class HubService:
    def __init__(self, address, use_async=False, use_ssl=False, timeout=10):
        self._async = use_async        
        if use_async:
            if use_ssl:
                self._channel = grpc.aio.secure_channel(address, grpc.ssl_channel_credentials())
            else:
                self._channel = grpc.aio.insecure_channel(address)
        else:
            if use_ssl:
                self._channel = grpc.secure_channel(address, grpc.ssl_channel_credentials())
            else:
                self._channel = grpc.insecure_channel(address)
        # grpc.channel_ready_future(self._channel).result(timeout=timeout)
        self._stub = rpc_pb2_grpc.HubServiceStub(self._channel)
    def close(self):
        self._channel.close()
    
    def GetInfo(self, db_stats=False, timeout=10) -> HubInfoResponse:
        return self._stub.GetInfo(HubInfoRequest(db_stats=db_stats), timeout=timeout)

    #  rpc GetCurrentPeers(Empty) returns (ContactInfoResponse);
    def GetCurrentPeers(self) -> ContactInfoResponse:
        return self._stub.GetCurrentPeers(Empty())
