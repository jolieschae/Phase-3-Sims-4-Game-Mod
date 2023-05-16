# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\live_events\live_event_commands.py
# Compiled at: 2021-11-22 21:29:05
# Size of source mod 2**32: 4929 bytes
import services, sims4.commands
from live_events.live_event_service import LiveEventService, LiveEventState, LiveEventName
from event_testing.resolver import SingleSimResolver
from event_testing.test_events import TestEvent
logger = sims4.log.Logger('Live Events')

@sims4.commands.Command('live_events.get_live_events', command_type=(sims4.commands.CommandType.Live))
def get_live_events(*live_event_list: str, _connection=None):
    if live_event_list:
        live_event_service = services.get_live_event_service()
        if live_event_service is not None:
            live_event_service.process_incoming_live_events(live_event_list)


@sims4.commands.Command('live_events.open_event_dialog', command_type=(sims4.commands.CommandType.DebugOnly))
def open_event_dialog(live_event_name: str, _connection=None):
    if str(live_event_name) not in LiveEventName:
        sims4.commands.output('The live event {} does not exist'.format(live_event_name), _connection)
        return
    else:
        live_event_service = services.get_live_event_service()
        live_event_data = live_event_service.LIVE_EVENTS.get(LiveEventName[str(live_event_name)], None)
        if live_event_data is not None:
            if live_event_data.action.action_type == LiveEventService.ACTION_TYPE_DRAMA_NODE and hasattr(live_event_data.action.drama_node, 'dialog_and_loot'):
                resolver = SingleSimResolver(services.active_sim_info())
                if services.drama_scheduler_service().run_node(live_event_data.action.drama_node, resolver):
                    sims4.commands.output('Successfully run dialog drama node: {} from live event.'.format(live_event_data.action.drama_node.__name__), _connection)
                else:
                    sims4.commands.output('Failed to run dialog drama node: {} from live event'.format(live_event_data.action.drama_node.__name__), _connection)
                return
    sims4.commands.output('The live event does not have a dialog to show.', _connection)


@sims4.commands.Command('live_events.set_live_event_state', command_type=(sims4.commands.CommandType.DebugOnly))
def set_live_event_state(live_event_name: str, live_event_state: int=1, _connection=None):
    if live_event_state not in LiveEventState:
        sims4.commands.output('{} is not a valid live event state'.format(live_event_state), _connection)
        return
    else:
        if str(live_event_name) not in LiveEventName:
            sims4.commands.output('The live event {} does not exist'.format(live_event_name), _connection)
            return
            live_event_service = services.get_live_event_service()
            event_manager = services.get_event_manager()
            live_event = LiveEventName[str(live_event_name)]
            if live_event in live_event_service.LIVE_EVENTS:
                if live_event_state == LiveEventState.ACTIVE and live_event_service.get_live_event_state(live_event) is not LiveEventState.ACTIVE:
                    live_event_service.activate_live_event(live_event)
                    event_manager.process_event(TestEvent.LiveEventStatesProcessed)
        elif live_event_state == LiveEventState.COMPLETED and live_event_service.get_live_event_state(live_event) is not LiveEventState.COMPLETED:
            live_event_service.set_live_event_state(live_event, LiveEventState.COMPLETED)
            event_manager.process_event(TestEvent.LiveEventStatesProcessed)
        else:
            sims4.commands.output('The live event {} was already in the {} state'.format(live_event_name, LiveEventState(live_event_state).name), _connection)
            return
        sims4.commands.output('Live event {} set to {}'.format(live_event_name, LiveEventState(live_event_state).name), _connection)
        return