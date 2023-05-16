# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\google\protobuf\service_reflection.py
# Compiled at: 2011-01-24 02:39:36
# Size of source mod 2**32: 11294 bytes
__author__ = 'petar@google.com (Petar Petrov)'

class GeneratedServiceType(type):
    _DESCRIPTOR_KEY = 'DESCRIPTOR'

    def __init__(cls, name, bases, dictionary):
        if GeneratedServiceType._DESCRIPTOR_KEY not in dictionary:
            return
        descriptor = dictionary[GeneratedServiceType._DESCRIPTOR_KEY]
        service_builder = _ServiceBuilder(descriptor)
        service_builder.BuildService(cls)


class GeneratedServiceStubType(GeneratedServiceType):
    _DESCRIPTOR_KEY = 'DESCRIPTOR'

    def __init__(cls, name, bases, dictionary):
        super(GeneratedServiceStubType, cls).__init__(name, bases, dictionary)
        if GeneratedServiceStubType._DESCRIPTOR_KEY not in dictionary:
            return
        descriptor = dictionary[GeneratedServiceStubType._DESCRIPTOR_KEY]
        service_stub_builder = _ServiceStubBuilder(descriptor)
        service_stub_builder.BuildServiceStub(cls)


class _ServiceBuilder(object):

    def __init__(self, service_descriptor):
        self.descriptor = service_descriptor

    def BuildService(self, cls):

        def _WrapCallMethod(srvc, method_descriptor, rpc_controller, request, callback):
            return self._CallMethod(srvc, method_descriptor, rpc_controller, request, callback)

        self.cls = cls
        cls.CallMethod = _WrapCallMethod
        cls.GetDescriptor = staticmethod((lambda: self.descriptor))
        cls.GetDescriptor.__doc__ = 'Returns the service descriptor.'
        cls.GetRequestClass = self._GetRequestClass
        cls.GetResponseClass = self._GetResponseClass
        for method in self.descriptor.methods:
            setattr(cls, method.name, self._GenerateNonImplementedMethod(method))

    def _CallMethod(self, srvc, method_descriptor, rpc_controller, request, callback):
        if method_descriptor.containing_service != self.descriptor:
            raise RuntimeError('CallMethod() given method descriptor for wrong service type.')
        method = getattr(srvc, method_descriptor.name)
        return method(rpc_controller, request, callback)

    def _GetRequestClass(self, method_descriptor):
        if method_descriptor.containing_service != self.descriptor:
            raise RuntimeError('GetRequestClass() given method descriptor for wrong service type.')
        return method_descriptor.input_type._concrete_class

    def _GetResponseClass(self, method_descriptor):
        if method_descriptor.containing_service != self.descriptor:
            raise RuntimeError('GetResponseClass() given method descriptor for wrong service type.')
        return method_descriptor.output_type._concrete_class

    def _GenerateNonImplementedMethod(self, method):
        return (lambda inst, rpc_controller, request, callback: self._NonImplementedMethod(method.name, rpc_controller, callback))

    def _NonImplementedMethod(self, method_name, rpc_controller, callback):
        rpc_controller.SetFailed('Method %s not implemented.' % method_name)
        callback(None)


class _ServiceStubBuilder(object):

    def __init__(self, service_descriptor):
        self.descriptor = service_descriptor

    def BuildServiceStub(self, cls):

        def _ServiceStubInit(stub, rpc_channel):
            stub.rpc_channel = rpc_channel

        self.cls = cls
        cls.__init__ = _ServiceStubInit
        for method in self.descriptor.methods:
            setattr(cls, method.name, self._GenerateStubMethod(method))

    def _GenerateStubMethod--- This code section failed: ---

 L. 266         0  LOAD_CONST               (None,)
                2  LOAD_CLOSURE             'method'
                4  LOAD_CLOSURE             'self'
                6  BUILD_TUPLE_2         2 
                8  LOAD_LAMBDA              '<code_object <lambda>>'
               10  LOAD_STR                 '_ServiceStubBuilder._GenerateStubMethod.<locals>.<lambda>'
               12  MAKE_FUNCTION_9          'default, closure'
               14  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `None' instruction at offset -1

    def _StubMethod(self, stub, method_descriptor, rpc_controller, request, callback):
        return stub.rpc_channel.CallMethod(method_descriptor, rpc_controller, request, method_descriptor.output_type._concrete_class, callback)