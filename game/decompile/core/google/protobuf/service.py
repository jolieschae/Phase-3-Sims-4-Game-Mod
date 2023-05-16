# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\google\protobuf\service.py
# Compiled at: 2011-01-24 02:39:36
# Size of source mod 2**32: 9357 bytes
__author__ = 'petar@google.com (Petar Petrov)'

class RpcException(Exception):
    pass


class Service(object):

    def GetDescriptor():
        raise NotImplementedError

    def CallMethod(self, method_descriptor, rpc_controller, request, done):
        raise NotImplementedError

    def GetRequestClass(self, method_descriptor):
        raise NotImplementedError

    def GetResponseClass(self, method_descriptor):
        raise NotImplementedError


class RpcController(object):

    def Reset(self):
        raise NotImplementedError

    def Failed(self):
        raise NotImplementedError

    def ErrorText(self):
        raise NotImplementedError

    def StartCancel(self):
        raise NotImplementedError

    def SetFailed(self, reason):
        raise NotImplementedError

    def IsCanceled(self):
        raise NotImplementedError

    def NotifyOnCancel(self, callback):
        raise NotImplementedError


class RpcChannel(object):

    def CallMethod(self, method_descriptor, rpc_controller, request, response_class, done):
        raise NotImplementedError