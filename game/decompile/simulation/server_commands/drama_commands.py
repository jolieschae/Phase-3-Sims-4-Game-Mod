# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\drama_commands.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 13060 bytes
from _collections import defaultdict
import services, sims4, sims4.commands
from date_and_time import create_date_and_time
from drama_scheduler.drama_node import DramaNodeParticipantOption, BaseDramaNode
from drama_scheduler.drama_node_types import DramaNodeType
from event_testing.resolver import DoubleSimResolver
from server_commands.argument_helpers import TunableInstanceParam, get_optional_target, OptionalSimInfoParam
from venues.venue_event_drama_node import VenueEventDramaNode
logger = sims4.log.Logger('DramaCommands')

@sims4.commands.Command('drama.run_node', command_type=(sims4.commands.CommandType.Automation))
def run_node(drama_node: TunableInstanceParam(sims4.resources.Types.DRAMA_NODE), actor_sim_id: OptionalSimInfoParam=None, target_sim_id: OptionalSimInfoParam=None, _connection=None):
    actor_sim_info = get_optional_target(actor_sim_id, _connection, OptionalSimInfoParam)
    if target_sim_id is not None:
        target_sim_info = get_optional_target(target_sim_id, _connection, OptionalSimInfoParam)
    else:
        target_sim_info = None
    resolver = DoubleSimResolver(actor_sim_info, target_sim_info)
    if services.drama_scheduler_service().run_node(drama_node, resolver):
        sims4.commands.output('Successfully run drama node: {}  See Drama Node Log GSI for more details.'.format(drama_node.__name__), _connection)
    else:
        sims4.commands.output('Failed to run drama node: {}'.format(drama_node.__name__), _connection)


@sims4.commands.Command('drama.run_scheduled_node')
def run_node(drama_node_uid: int, _connection=None):
    node = services.drama_scheduler_service().get_scheduled_node_by_uid(drama_node_uid)
    if node is not None:
        node.run_immediate()


@sims4.commands.Command('drama.run_node_with_zone_id')
def run_node_with_zone_id(drama_node: TunableInstanceParam(sims4.resources.Types.DRAMA_NODE), actor_sim_id: OptionalSimInfoParam=None, target_sim_id: OptionalSimInfoParam=None, _connection=None):
    actor_sim_info = get_optional_target(actor_sim_id, _connection, OptionalSimInfoParam)
    if target_sim_id is not None:
        target_sim_info = get_optional_target(target_sim_id, _connection, OptionalSimInfoParam)
    else:
        target_sim_info = None
    resolver = DoubleSimResolver(actor_sim_info, target_sim_info)
    zone_id = services.current_zone_id()
    if services.drama_scheduler_service().run_node(drama_node, resolver, zone_id=zone_id):
        sims4.commands.output('Successfully run drama node: {}  See Drama Node Log GSI for more details.'.format(drama_node.__name__), _connection)
    else:
        sims4.commands.output('Failed to run drama node: {}'.format(drama_node.__name__), _connection)


@sims4.commands.Command('drama.schedule_node')
def schedule_node(drama_node: TunableInstanceParam(sims4.resources.Types.DRAMA_NODE), actor_sim_id: OptionalSimInfoParam=None, target_sim_id: OptionalSimInfoParam=None, days_from_now: int=None, _connection=None):
    actor_sim_info = get_optional_target(actor_sim_id, _connection, OptionalSimInfoParam)
    if target_sim_id is not None:
        target_sim_info = get_optional_target(target_sim_id, _connection, OptionalSimInfoParam)
    else:
        target_sim_info = None
    specific_time = None
    if days_from_now is not None:
        scheduled_day = int(services.time_service().sim_now.absolute_days()) + days_from_now
        specific_time = create_date_and_time(days=scheduled_day)
    else:
        resolver = DoubleSimResolver(actor_sim_info, target_sim_info)
        uid = services.drama_scheduler_service().schedule_node(drama_node, resolver, specific_time=specific_time)
        if uid is not None:
            sims4.commands.output('Successfully scheduled drama node: {}'.format(drama_node.__name__), _connection)
        else:
            sims4.commands.output('Failed to scheduled drama node: {}'.format(drama_node.__name__), _connection)


@sims4.commands.Command('drama.show_scheduled_nodes')
def show_scheduled_nodes(_connection=None):
    dss = services.drama_scheduler_service()
    for node in dss:
        sims4.commands.output('{}'.format(node), _connection)


@sims4.commands.Command('drama.show_active_nodes')
def show_active_nodes(_connection=None):
    dss = services.drama_scheduler_service()
    for node in dss.active_nodes_gen():
        sims4.commands.output('{}'.format(node), _connection)


@sims4.commands.Command('drama.show_drama_calendar')
def show_drama_calendar(_connection=None):
    dnm = services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)
    week_schedule = defaultdict(list)
    for node_type in dnm.types.values():
        valid_time_strings = node_type.get_debug_valid_time_strings()
        for day, valid_hours in valid_time_strings.items():
            day_string = '{}({})'.format(node_type.__name__, ','.join(valid_hours))
            week_schedule[day].append(day_string)

    for day, day_string_list in week_schedule.items():
        sims4.commands.output('{}'.format(day), _connection)
        for day_string in day_string_list:
            sims4.commands.output('   {}'.format(day_string), _connection)


@sims4.commands.Command('drama.score_nodes')
def score_nodes(_connection=None):
    for _ in services.drama_scheduler_service()._score_and_schedule_drama_nodes_gen(None):
        pass

    sims4.commands.output('Scored and scheduled nodes.  See GSI for details', _connection)


@sims4.commands.Command('drama.travel_to_event_zone', command_type=(sims4.commands.CommandType.Live))
def travel_to_event_zone(drama_node: TunableInstanceParam(sims4.resources.Types.DRAMA_NODE), _connection=None):
    if drama_node.drama_node_type == DramaNodeType.FESTIVAL:
        drama_node.travel_to_destination()
        return
    if drama_node.drama_node_type == DramaNodeType.VENUE_EVENT:
        drama_scheduler = services.drama_scheduler_service()
        if drama_scheduler is None:
            logger.error("Failed to run 'travel_to_event_zone' for ({}) because drama scheduler is not initiated.", str(drama_node))
        active_drama_nodes = [node for node in drama_scheduler.active_nodes_gen() if node.guid64 == drama_node.guid64]
        if not active_drama_nodes:
            logger.error("Failed to run 'travel_to_event_zone' for ({}), there is no event of that type active.")
            return
        active_drama_nodes[0].travel_to_destination()
        return
    logger.error("Unsupported drama node type({}) for 'travel to event zone. Travel cancelled for ({})", str(drama_node.drama_node_type), str(drama_node))


@sims4.commands.Command('drama.show_festival_info', command_type=(sims4.commands.CommandType.Live))
def show_festival_info(drama_node: TunableInstanceParam(sims4.resources.Types.DRAMA_NODE), _connection=None):
    drama_node.show_festival_info()


@sims4.commands.Command('drama.show_festival_info_by_drama_node_uid', command_type=(sims4.commands.CommandType.Live))
def show_festival_info_by_drama_node_uid(drama_node_uid: int, _connection=None):
    drama_scheduler_service = services.drama_scheduler_service()
    drama_node = drama_scheduler_service.get_active_node_by_uid(drama_node_uid)
    if drama_node is None:
        drama_node = drama_scheduler_service.get_scheduled_node_by_uid(drama_node_uid)
    drama_node.show_festival_info()


@sims4.commands.Command('drama.print_scoring_info')
def print_scoring_info(_connection=None):
    dnm = services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)
    filters_used = defaultdict(int)
    for node_type in dnm.types.values():
        if node_type.scoring is None:
            continue
        if node_type.sender_sim_info.type == DramaNodeParticipantOption.DRAMA_PARTICIPANT_OPTION_FILTER:
            filters_used[node_type.sender_sim_info.sim_filter] += 1

    for sim_filter, frequency in filters_used.items():
        sims4.commands.output('{}: {}'.format(sim_filter, frequency), _connection)


@sims4.commands.Command('drama.enable_drama_scheduler', command_type=(sims4.commands.CommandType.Automation))
def enable_drama_scheduler(_connection=None):
    services.drama_scheduler_service().set_enabled_state(True)


@sims4.commands.Command('drama.disable_drama_scheduler', command_type=(sims4.commands.CommandType.Automation))
def disable_drama_scheduler(_connection=None):
    services.drama_scheduler_service().set_enabled_state(False)


@sims4.commands.Command('drama.cancel_scheduled_node', command_type=(sims4.commands.CommandType.Live))
def cancel_scheduled_node(drama_node_uid: int, _connection=None):
    success = services.drama_scheduler_service().cancel_scheduled_node(drama_node_uid)
    if success:
        sims4.commands.output('Successfully cancelled scheduled drama node id: {}'.format(drama_node_uid), _connection)
    else:
        sims4.commands.output('Failed to cancel scheduled drama node id: {}'.format(drama_node_uid), _connection)


@sims4.commands.Command('drama.cancel_scheduled_node_by_type', command_type=(sims4.commands.CommandType.DebugOnly))
def cancel_scheduled_node_by_type(drama_node_type: DramaNodeType, _connection=None):
    drama_scheduler = services.drama_scheduler_service()
    nodes_to_cancel = drama_scheduler.get_scheduled_nodes_by_drama_node_type(drama_node_type)
    if nodes_to_cancel is None:
        sims4.commands.output('No drama nodes of type {} to cancel'.format(drama_node_type), _connection)
    else:
        failed_nodes = []
        for node in nodes_to_cancel:
            success = drama_scheduler.cancel_scheduled_node(node.uid)
            if not success:
                failed_nodes.append(node.uid)

        if failed_nodes:
            sims4.commands.output('Failed to cancel scheduled drama nodes: {}'.format(failed_nodes), _connection)
        else:
            sims4.commands.output('Successfully cancelled scheduled drama node with type {}'.format(drama_node_type), _connection)


@sims4.commands.Command('drama.cancel_scheduled_node_by_instance', command_type=(sims4.commands.CommandType.DebugOnly))
def cancel_scheduled_node_by_instance(node: TunableInstanceParam(sims4.resources.Types.DRAMA_NODE), _connection=None):
    drama_scheduler = services.drama_scheduler_service()
    drama_scheduler.cancel_scheduled_nodes_with_types((node,))
    sims4.commands.output('Successfully cancelled scheduled drama nodes with type {}'.format(node), _connection)


@sims4.commands.Command('drama.travel_to_event', command_type=(sims4.commands.CommandType.Live))
def travel_to_event(zone_id: int, _connection=None):
    travel_interaction = VenueEventDramaNode.GO_TO_VENUE_ZONE_INTERACTION
    if travel_interaction is None:
        return
    lot_id = services.get_persistence_service().get_lot_id_from_zone_id(zone_id)
    BaseDramaNode.push_travel_interaction(travel_interaction, lot_id)