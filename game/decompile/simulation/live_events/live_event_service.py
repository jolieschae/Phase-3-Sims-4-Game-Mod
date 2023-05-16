# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\live_events\live_event_service.py
# Compiled at: 2021-11-22 21:29:05
# Size of source mod 2**32: 16843 bytes
import enum, services, sims4
from distributor.ops import RequestLiveEvents
from distributor.rollback import ProtocolBufferRollback
from distributor.system import Distributor
from event_testing.resolver import SingleSimResolver
from event_testing.test_events import TestEvent
from persistence_error_types import ErrorCodes
from protocolbuffers import GameplaySaveData_pb2
from sims4.resources import Types
from sims4.service_manager import Service
from sims4.tuning.dynamic_enum import DynamicEnumLocked
from sims4.tuning.tunable import TunableReference, Tunable, TunableTuple, TunableVariant, TunableEnumEntry, TunableMapping, OptionalTunable, TunableRange
from sims4.tuning.tunable_base import ExportModes, GroupNames
from sims4.utils import classproperty
logger = sims4.log.Logger('Live Events', default_owner='asantos')

class LiveEventName(DynamicEnumLocked):
    DEFAULT = 0


class LiveEventState(enum.Int):
    COMPLETED = 0
    ACTIVE = 1


class LiveEventType(enum.Int):
    AB_TEST = 0
    LIVE_FESTIVAL = 1
    SCENARIO = 2


class TunableRealWorldDateAndTime(TunableTuple):

    def __init__(self, **kwargs):
        (super().__init__)(year=TunableRange(description='\n                Year\n                ',
  tunable_type=int,
  default=2021,
  minimum=2014), 
         month=TunableRange(description='\n                Month\n                ',
  tunable_type=int,
  default=1,
  minimum=1,
  maximum=12), 
         day=TunableRange(description='\n                Day\n                ',
  tunable_type=int,
  default=1,
  minimum=1,
  maximum=31), 
         hour=TunableRange(description='\n                Hour (24-hour)\n                ',
  tunable_type=int,
  default=0,
  minimum=0,
  maximum=23), 
         minute=TunableRange(description='\n                Minute\n                ',
  tunable_type=int,
  default=0,
  minimum=0,
  maximum=59), 
         export_class_name='TunableDateTuple', **kwargs)


class LiveEventService(Service):
    ACTION_TYPE_DRAMA_NODE = 0
    LIVE_EVENTS = TunableMapping(description='\n        A list of all of the live events that we want to add functionality for.\n        ',
      key_type=TunableEnumEntry(description='\n            The name of this live event, as defined by the PMs in the UM message.\n            ',
      tunable_type=LiveEventName,
      default=(LiveEventName.DEFAULT),
      invalid_enums=(
     LiveEventName.DEFAULT,)),
      value_type=TunableTuple(action=TunableVariant(description='\n                A gameplay action that runs when the event occurs.\n                ',
      start_drama_node=TunableTuple(description='\n                    If this event is active, we will schedule a drama node.\n                    ',
      drama_node=TunableReference(description='\n                        The drama node to schedule when the player is in this live event.\n                        This could be a Dialog drama node to trigger a dialog after a certain amount of time.\n                        ',
      manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE))),
      locked_args={'action_type': ACTION_TYPE_DRAMA_NODE}),
      locked_args={'None': None},
      default='None'),
      event_content=TunableVariant(description='\n                If enabled, specifies data related to the event that will be\n                exported to client/UI.\n                ',
      scenario=TunableReference(description='\n                    This option enables or disables a tuned scenario via the\n                    live event.\n                    ',
      manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
      class_restrictions=('Scenario', )),
      locked_args={'None': None},
      default='None',
      export_modes=(ExportModes.ClientBinary)),
      timing_data=TunableVariant(description='\n                Data about when the event should occur.\n                ',
      tuned_start_and_end=TunableTuple(description='\n                    This option allows a fixed start and end time to be tuned.\n                    ',
      start_date_and_time=TunableRealWorldDateAndTime(display_name='Start Date (UTC)'),
      end_date_and_time=TunableRealWorldDateAndTime(display_name='End Date (UTC)'),
      export_class_name='TunableStartAndEndDate'),
      locked_args={'None': None},
      default='None',
      export_modes=(ExportModes.ClientBinary)),
      event_type=TunableEnumEntry(description='\n                The type of live event this is.\n                ',
      tunable_type=LiveEventType,
      default=(LiveEventType.AB_TEST)),
      is_unique=Tunable(description='\n                If this event is unique, there can only be 1 event of this type active at a time.\n                ',
      tunable_type=bool,
      default=False),
      export_class_name='TunableLiveEventData',
      export_modes=(ExportModes.ServerXML)),
      tuple_name='TunableLiveEventDataMap')

    def __init__(self):
        self._live_events = {}
        self._awaiting_live_event_data = True

    @classproperty
    def save_error_code(cls):
        return ErrorCodes.SERVICE_SAVE_FAILED_LIVE_EVENT_SERVICE

    def save(self, object_list=None, zone_data=None, open_street_data=None, save_slot_data=None):
        service_data = GameplaySaveData_pb2.PersistableLiveEventService()
        for live_event in self._live_events:
            with ProtocolBufferRollback(service_data.live_event_data) as (live_event_data):
                live_event_data.event_id = live_event
                live_event_data.state = self._live_events[live_event]

        save_slot_data.gameplay_data.live_event_service = service_data

    def load(self, zone_data=None):
        save_slot_data_msg = services.get_persistence_service().get_save_slot_proto_buff()
        if save_slot_data_msg.gameplay_data.HasField('ab_test_service'):
            service_data = save_slot_data_msg.gameplay_data.ab_test_service
            for ab_test in service_data.ab_test_data:
                if str(ab_test.name) in LiveEventName:
                    self._live_events[LiveEventName[str(ab_test.name)]] = ab_test.state

        else:
            return save_slot_data_msg.gameplay_data.HasField('live_event_service') or None
        service_data = save_slot_data_msg.gameplay_data.live_event_service
        for live_event in service_data.live_event_data:
            self._live_events[live_event.event_id] = live_event.state

    def on_all_households_and_sim_infos_loaded(self, client):
        if not self.is_live_event_data_available():
            op = RequestLiveEvents()
            Distributor.instance().add_op_with_no_owner(op)

    def process_incoming_live_events(self, live_event_list):
        live_event_iter = iter(live_event_list)
        for live_event_string in live_event_iter:
            live_event_name_str, live_event_state = live_event_string.split(',')
            live_event_name_key = LiveEventName[live_event_name_str] if live_event_name_str in LiveEventName else None
            if live_event_name_key is None:
                logger.error('{} is not a valid name for a Live Event.', live_event_name_str, owner='asantos')
                continue
            if int(live_event_state) == LiveEventState.ACTIVE:
                if live_event_name_key not in self._live_events:
                    self.activate_live_event(live_event_name_key)
            if int(live_event_state) == LiveEventState.COMPLETED:
                self._live_events[live_event_name_key] = LiveEventState.COMPLETED

        self._awaiting_live_event_data = False
        event_manager = services.get_event_manager()
        event_manager.process_event(TestEvent.LiveEventStatesProcessed)

    def is_live_event_data_available(self):
        return not self._awaiting_live_event_data

    @staticmethod
    def process_live_event(live_event_name_key):
        live_event = LiveEventService.LIVE_EVENTS[live_event_name_key]
        if live_event:
            if live_event.action is not None:
                if live_event.action.action_type == LiveEventService.ACTION_TYPE_DRAMA_NODE:
                    resolver = SingleSimResolver(services.active_sim_info())
                    services.drama_scheduler_service().schedule_node(live_event.action.drama_node, resolver)

    @staticmethod
    def get_event_type_and_unique(live_event_name_key):
        if live_event_name_key in LiveEventService.LIVE_EVENTS:
            live_event = LiveEventService.LIVE_EVENTS[live_event_name_key]
            return (live_event.event_type, live_event.is_unique)
        return (None, None)

    def activate_live_event(self, live_event_name_key):
        event_type, is_unique = self.get_event_type_and_unique(live_event_name_key)
        active_unique_event = self.get_current_unique_live_event_of_type(event_type)
        if is_unique and active_unique_event is not None:
            logger.error('Trying to run unique live event {} of type {}, but event {} is already running.',
              (live_event_name_key.name),
              (LiveEventType(event_type).name), active_unique_event, owner='asantos')
        else:
            self._live_events[live_event_name_key] = LiveEventState.ACTIVE
            self.process_live_event(live_event_name_key)

    def get_live_event_state(self, live_event_name_key):
        return self._live_events.get(live_event_name_key)

    def set_live_event_state(self, live_event_name_key, state):
        self._live_events[live_event_name_key] = state

    def get_current_unique_live_event_of_type(self, event_type):
        for live_event_name_key, state in self._live_events.items():
            if state == LiveEventState.ACTIVE:
                live_event = LiveEventService.LIVE_EVENTS[live_event_name_key]
                if live_event and live_event.is_unique and live_event.event_type == event_type:
                    return live_event_name_key

    @staticmethod
    def verify_live_event_tuning():
        for live_event_name_key, live_event_data in LiveEventService.LIVE_EVENTS.items():
            action = live_event_data.action
            if action is None:
                continue
            if action.action_type == LiveEventService.ACTION_TYPE_DRAMA_NODE:
                if not hasattr(action.drama_node, 'live_event_telemetry_name'):
                    logger.error('Live event {} has a drama node that does not have a field live_event_telemetry_name. Please pick a Dialog drama node.',
                      (live_event_name_key.name),
                      owner='asantos')
                elif action.drama_node.live_event_telemetry_name is None:
                    logger.error("Live event {} has a drama node that hasn't tuned the field live_event_telemetry_name. Please set it to be the event name.",
                      (live_event_name_key.name),
                      owner='asantos')
                elif action.drama_node.live_event_telemetry_name != live_event_name_key:
                    logger.error('Live event {} has a drama node with the field live_event_telemetry_name different from the event name. Please make both the same.',
                      (live_event_name_key.name),
                      owner='asantos')