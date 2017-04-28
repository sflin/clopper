# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc
from grpc.framework.common import cardinality
from grpc.framework.interfaces.face import utilities as face_utilities

import clopper_pb2 as clopper__pb2


class ClopperStub(object):
  """The greeting service definition.
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.SayHello = channel.unary_unary(
        '/hopperextension.Clopper/SayHello',
        request_serializer=clopper__pb2.HelloRequest.SerializeToString,
        response_deserializer=clopper__pb2.Greeting.FromString,
        )
    self.UpdateStatus = channel.unary_unary(
        '/hopperextension.Clopper/UpdateStatus',
        request_serializer=clopper__pb2.StatusRequest.SerializeToString,
        response_deserializer=clopper__pb2.InstanceUpdate.FromString,
        )
    self.ExecuteHopper = channel.unary_unary(
        '/hopperextension.Clopper/ExecuteHopper',
        request_serializer=clopper__pb2.HopRequest.SerializeToString,
        response_deserializer=clopper__pb2.HopResults.FromString,
        )


class ClopperServicer(object):
  """The greeting service definition.
  """

  def SayHello(self, request, context):
    """Greeting
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def UpdateStatus(self, request, context):
    """Status Updates
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ExecuteHopper(self, request, context):
    """Execute hopper
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_ClopperServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'SayHello': grpc.unary_unary_rpc_method_handler(
          servicer.SayHello,
          request_deserializer=clopper__pb2.HelloRequest.FromString,
          response_serializer=clopper__pb2.Greeting.SerializeToString,
      ),
      'UpdateStatus': grpc.unary_unary_rpc_method_handler(
          servicer.UpdateStatus,
          request_deserializer=clopper__pb2.StatusRequest.FromString,
          response_serializer=clopper__pb2.InstanceUpdate.SerializeToString,
      ),
      'ExecuteHopper': grpc.unary_unary_rpc_method_handler(
          servicer.ExecuteHopper,
          request_deserializer=clopper__pb2.HopRequest.FromString,
          response_serializer=clopper__pb2.HopResults.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'hopperextension.Clopper', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))