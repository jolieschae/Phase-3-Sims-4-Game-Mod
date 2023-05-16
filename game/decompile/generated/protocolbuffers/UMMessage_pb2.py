# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: /Users/sims4builder/build/Beta/_deploy/Client/MacRelease/The Sims 4.app/Contents/Python/Generated/protocolbuffers/UMMessage_pb2.py
# Compiled at: 2023-04-20 22:46:31
# Size of source mod 2**32: 3884 bytes
from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
DESCRIPTOR = descriptor.FileDescriptor(name='UMMessage.proto',
  package='EA.Sims4.ECommerceServices',
  serialized_pb='\n\x0fUMMessage.proto\x12\x1aEA.Sims4.ECommerceServices"w\n\tUMMessage\x12E\n\x08messages\x18\x01 \x03(\x0b23.EA.Sims4.ECommerceServices.UMMessage.AttributeList\x1a#\n\rAttributeList\x12\x12\n\nattributes\x18\x01 \x03(\t"#\n\x14RefreshFeatureParams\x12\x0b\n\x03key\x18\x01 \x01(\x04')
_UMMESSAGE_ATTRIBUTELIST = descriptor.Descriptor(name='AttributeList',
  full_name='EA.Sims4.ECommerceServices.UMMessage.AttributeList',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
 descriptor.FieldDescriptor(name='attributes',
   full_name='EA.Sims4.ECommerceServices.UMMessage.AttributeList.attributes',
   index=0,
   number=1,
   type=9,
   cpp_type=9,
   label=3,
   has_default_value=False,
   default_value=[],
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None)],
  extensions=[],
  nested_types=[],
  enum_types=[],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=131,
  serialized_end=166)
_UMMESSAGE = descriptor.Descriptor(name='UMMessage',
  full_name='EA.Sims4.ECommerceServices.UMMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
 descriptor.FieldDescriptor(name='messages',
   full_name='EA.Sims4.ECommerceServices.UMMessage.messages',
   index=0,
   number=1,
   type=11,
   cpp_type=10,
   label=3,
   has_default_value=False,
   default_value=[],
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None)],
  extensions=[],
  nested_types=[
 _UMMESSAGE_ATTRIBUTELIST],
  enum_types=[],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=47,
  serialized_end=166)
_REFRESHFEATUREPARAMS = descriptor.Descriptor(name='RefreshFeatureParams',
  full_name='EA.Sims4.ECommerceServices.RefreshFeatureParams',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
 descriptor.FieldDescriptor(name='key',
   full_name='EA.Sims4.ECommerceServices.RefreshFeatureParams.key',
   index=0,
   number=1,
   type=4,
   cpp_type=4,
   label=1,
   has_default_value=False,
   default_value=0,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None)],
  extensions=[],
  nested_types=[],
  enum_types=[],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=168,
  serialized_end=203)
_UMMESSAGE_ATTRIBUTELIST.containing_type = _UMMESSAGE
_UMMESSAGE.fields_by_name['messages'].message_type = _UMMESSAGE_ATTRIBUTELIST
DESCRIPTOR.message_types_by_name['UMMessage'] = _UMMESSAGE
DESCRIPTOR.message_types_by_name['RefreshFeatureParams'] = _REFRESHFEATUREPARAMS

class UMMessage(message.Message, metaclass=reflection.GeneratedProtocolMessageType):

    class AttributeList(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
        DESCRIPTOR = _UMMESSAGE_ATTRIBUTELIST

    DESCRIPTOR = _UMMESSAGE


class RefreshFeatureParams(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _REFRESHFEATUREPARAMS