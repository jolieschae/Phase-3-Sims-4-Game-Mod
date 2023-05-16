# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: /Users/sims4builder/build/Beta/_deploy/Client/MacRelease/The Sims 4.app/Contents/Python/Generated/protocolbuffers/Calendar_pb2.py
# Compiled at: 2023-04-20 22:46:30
# Size of source mod 2**32: 3221 bytes
from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
DESCRIPTOR = descriptor.FileDescriptor(name='Calendar.proto',
  package='',
  serialized_pb='\n\x0eCalendar.proto"M\n\x14CalendarFavoriteData\x12\x14\n\x0chousehold_id\x18\x01 \x01(\x06\x12\x1f\n\x13favorited_event_ids\x18\x02 \x03(\x06B\x02\x10\x01"J\n\x1aPersistableCalendarService\x12,\n\rfavorite_data\x18\x01 \x03(\x0b2\x15.CalendarFavoriteData')
_CALENDARFAVORITEDATA = descriptor.Descriptor(name='CalendarFavoriteData',
  full_name='CalendarFavoriteData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
 descriptor.FieldDescriptor(name='household_id',
   full_name='CalendarFavoriteData.household_id',
   index=0,
   number=1,
   type=6,
   cpp_type=4,
   label=1,
   has_default_value=False,
   default_value=0,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='favorited_event_ids',
   full_name='CalendarFavoriteData.favorited_event_ids',
   index=1,
   number=2,
   type=6,
   cpp_type=4,
   label=3,
   has_default_value=False,
   default_value=[],
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=(descriptor._ParseOptions(descriptor_pb2.FieldOptions(), '\x10\x01')))],
  extensions=[],
  nested_types=[],
  enum_types=[],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=18,
  serialized_end=95)
_PERSISTABLECALENDARSERVICE = descriptor.Descriptor(name='PersistableCalendarService',
  full_name='PersistableCalendarService',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
 descriptor.FieldDescriptor(name='favorite_data',
   full_name='PersistableCalendarService.favorite_data',
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
  nested_types=[],
  enum_types=[],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=97,
  serialized_end=171)
_PERSISTABLECALENDARSERVICE.fields_by_name['favorite_data'].message_type = _CALENDARFAVORITEDATA
DESCRIPTOR.message_types_by_name['CalendarFavoriteData'] = _CALENDARFAVORITEDATA
DESCRIPTOR.message_types_by_name['PersistableCalendarService'] = _PERSISTABLECALENDARSERVICE

class CalendarFavoriteData(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _CALENDARFAVORITEDATA


class PersistableCalendarService(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _PERSISTABLECALENDARSERVICE