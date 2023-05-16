# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\developmental_milestones\developmental_milestone_commands.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 15165 bytes
from event_testing.resolver import SingleSimResolver
from developmental_milestones.developmental_milestone import DevelopmentalMilestone
from developmental_milestones.developmental_milestone import DevelopmentalMilestoneCategory
from developmental_milestones.developmental_milestone_tracker import MilestoneTelemetryContext
from distributor.ops import GenericProtocolBufferOp
from distributor.system import Distributor
from protocolbuffers.DistributorOps_pb2 import Operation
from protocolbuffers import Sims_pb2
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target, TunableInstanceParam, OptionalSimInfoParam, extract_ints
import services, sims4.commands
logger = sims4.log.Logger('DevelopmentalMilestones', default_owner='miking')

@sims4.commands.Command('developmental_milestones.print_milestones')
def print_milestones(opt_sim: OptionalTargetParam=None, _connection=None):
    output = sims4.commands.output
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        output('Target Sim not specified.', _connection)
        return False
        tracker = sim.sim_info.developmental_milestone_tracker
        if tracker is None:
            output('Target does not have a DevelopmentalMilestoneTracker.', _connection)
            return False
        output('Current Developmental Milestones for Sim {}:'.format(sim), _connection)
        milestones = tracker.active_milestones
        if milestones:
            for milestone_data in tracker.active_milestones:
                output('Milestone: {} State: {}'.format(milestone_data.milestone, milestone_data.state), _connection)

    else:
        output('No Active Milestones', _connection)
    return True


@sims4.commands.Command('developmental_milestones.activate_milestone')
def activate_milestone(milestone: TunableInstanceParam(sims4.resources.Types.DEVELOPMENTAL_MILESTONE), opt_sim: OptionalTargetParam=None, _connection=None):
    output = sims4.commands.output
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        output('Target Sim not specified.', _connection)
        return False
    tracker = sim.sim_info.developmental_milestone_tracker
    if tracker is None:
        output('Target does not have a DevelopmentalMilestoneTracker.', _connection)
        return False
    if not tracker.is_milestone_valid_for_sim(milestone):
        output('Milestone {} is not valid for Sim {}.'.format(milestone, sim), _connection)
        return False
    if tracker.is_milestone_active(milestone):
        output('Milestone {} is already active for Sim {}.'.format(milestone, sim), _connection)
        return False
    tracker.recursively_unlock_prerequisites(milestone, telemetry_context=(MilestoneTelemetryContext.CHEAT))
    if not tracker.is_milestone_active(milestone):
        logger.warn('activate_milestone cheat: recursively_unlock_prerequisites did not activate milestone {}. Activating it manually.', milestone)
        tracker.activate_milestone(milestone, telemetry_context=(MilestoneTelemetryContext.CHEAT))
    output('Milestone {} activated for Sim {}.'.format(milestone, sim), _connection)
    return True


@sims4.commands.Command('developmental_milestones.set_milestone_progress')
def set_milestone_progress(milestone: TunableInstanceParam(sims4.resources.Types.DEVELOPMENTAL_MILESTONE), value: float, opt_sim: OptionalTargetParam=None, _connection=None):
    output = sims4.commands.output
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        output('Target Sim not specified.', _connection)
        return False
    tracker = sim.sim_info.developmental_milestone_tracker
    if tracker is None:
        output('Target does not have a DevelopmentalMilestoneTracker.', _connection)
        return False
    if not tracker.is_milestone_valid_for_sim(milestone):
        output('Milestone {} is not valid for Sim {}.'.format(milestone, sim), _connection)
        return False
    if not tracker.is_milestone_active(milestone):
        output('Milestone {} is not active for Sim {}.'.format(milestone, sim), _connection)
        return False
    commodity_to_set = milestone.commodity
    if commodity_to_set is None:
        output('Milestone {} does not have a tuned commodity to set.'.format(milestone), _connection)
        return False
    sim.sim_info.commodity_tracker.set_value(commodity_to_set, value)
    new_value = sim.sim_info.commodity_tracker.get_value(commodity_to_set)
    output('Commodity {} set to value {} for Sim {}.'.format(commodity_to_set, new_value, sim), _connection)
    return True


@sims4.commands.Command('developmental_milestones.unlock_milestone')
def unlock_milestone(milestone: TunableInstanceParam(sims4.resources.Types.DEVELOPMENTAL_MILESTONE), opt_sim: OptionalTargetParam=None, _connection=None):
    output = sims4.commands.output
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        output('Target Sim not specified.', _connection)
        return False
    tracker = sim.sim_info.developmental_milestone_tracker
    if tracker is None:
        output('Target does not have a DevelopmentalMilestoneTracker.', _connection)
        return False
    if not tracker.is_milestone_valid_for_sim(milestone):
        output('Milestone {} is not valid for Sim {}.'.format(milestone, sim), _connection)
        return False
    if tracker.is_milestone_unlocked(milestone):
        output('Milestone {} is already unlocked for Sim {}.'.format(milestone, sim), _connection)
        return False
    tracker.recursively_unlock_prerequisites(milestone, telemetry_context=(MilestoneTelemetryContext.CHEAT))
    if not tracker.is_milestone_active(milestone):
        logger.warn('activate_milestone cheat: recursively_unlock_prerequisites did not activate milestone {}. Activating it manually.', milestone)
        tracker.activate_milestone(milestone, telemetry_context=(MilestoneTelemetryContext.CHEAT))
    tracker.unlock_milestone(milestone, telemetry_context=(MilestoneTelemetryContext.CHEAT))
    output('Milestone {} unlocked for Sim {}.'.format(milestone, sim), _connection)
    return True


@sims4.commands.Command('developmental_milestones.unlock_milestone_from_id')
def unlock_milestone_from_id(milestone_id: int, opt_sim: OptionalTargetParam=None, _connection=None):
    milestone_manager = services.get_instance_manager(sims4.resources.Types.DEVELOPMENTAL_MILESTONE)
    milestone = milestone_manager.get(milestone_id)
    if milestone is None:
        sims4.commands.output('Milestone ID {} is invalid'.format(milestone_id), _connection)
        return
    unlock_milestone(milestone, opt_sim, _connection)


@sims4.commands.Command('developmental_milestones.unlock_all_milestones')
def unlock_all_milestones(category_id: DevelopmentalMilestoneCategory=DevelopmentalMilestoneCategory.INVALID, opt_sim: OptionalTargetParam=None, _connection=None):
    output = sims4.commands.output
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        output('Target Sim not specified.', _connection)
        return False
    tracker = sim.sim_info.developmental_milestone_tracker
    if tracker is None:
        output('Target does not have a DevelopmentalMilestoneTracker.', _connection)
        return False
    for milestone in DevelopmentalMilestone.age_milestones_gen(sim.sim_info.age):
        if category_id != DevelopmentalMilestoneCategory.INVALID:
            if category_id != milestone.category:
                continue
            else:
                tracker.is_milestone_unlocked(milestone) or tracker.is_milestone_active(milestone) or tracker.activate_milestone(milestone, telemetry_context=(MilestoneTelemetryContext.CHEAT), send_ui_update=False)
            tracker.unlock_milestone(milestone, telemetry_context=(MilestoneTelemetryContext.CHEAT), send_ui_update=False)

    tracker.send_all_milestones_update_to_client()
    output('All milestones unlocked for Sim {}.'.format(sim), _connection)
    return True


@sims4.commands.Command('developmental_milestones.reset_all_milestones')
def reset_all_milestones(opt_sim: OptionalTargetParam=None, _connection=None):
    output = sims4.commands.output
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        output('Target Sim not specified.', _connection)
        return False
    tracker = sim.sim_info.developmental_milestone_tracker
    if tracker is None:
        output('Target does not have a DevelopmentalMilestoneTracker.', _connection)
        return False
    tracker._remove_all_milestones()
    tracker._activate_available_milestones(telemetry_context=(MilestoneTelemetryContext.CHEAT))
    tracker.send_all_milestones_update_to_client()
    output('All milestones reset for Sim {}.'.format(sim), _connection)
    return True


@sims4.commands.Command('developmental_milestones.mark_milestone_as_viewed', command_type=(sims4.commands.CommandType.Live))
def mark_as_viewed(milestone_id: int, goal_id: int=None, opt_target: OptionalSimInfoParam=None, _connection=None):
    output = sims4.commands.output
    target = get_optional_target(opt_target, _connection, target_type=OptionalSimInfoParam)
    if target is None:
        sims4.commands.output('No Sim with id {}'.format(opt_target), _connection)
        return False
    tracker = target.sim_info.developmental_milestone_tracker
    if tracker is None:
        output('Target does not have a DevelopmentalMilestoneTracker.', _connection)
        return False
    milestone_manager = services.get_instance_manager(sims4.resources.Types.DEVELOPMENTAL_MILESTONE)
    milestone = milestone_manager.get(milestone_id)
    if milestone is None:
        sims4.commands.output('Invalid milestone_id {}'.format(milestone_id), _connection)
        return False
    goal_id = goal_id if goal_id != 0 else None
    tracker.mark_milestone_as_viewed(milestone, goal_id=goal_id)


@sims4.commands.Command('developmental_milestones.mark_all_as_viewed', command_type=(sims4.commands.CommandType.Live))
def mark_all_as_viewed(milestone_ids: str='', goal_ids: str='', opt_target: OptionalSimInfoParam=None, _connection=None):
    output = sims4.commands.output
    target = get_optional_target(opt_target, _connection, target_type=OptionalSimInfoParam)
    if target is None:
        sims4.commands.output('No Sim with id {}'.format(opt_target), _connection)
        return False
    tracker = target.sim_info.developmental_milestone_tracker
    if tracker is None:
        output('Target {} does not have a DevelopmentalMilestoneTracker.'.format(target), _connection)
        return False
    milestone_manager = services.get_instance_manager(sims4.resources.Types.DEVELOPMENTAL_MILESTONE)
    milestone_ids = extract_ints(milestone_ids)
    goal_ids = extract_ints(goal_ids)
    for i in range(len(milestone_ids)):
        milestone_id = milestone_ids[i]
        goal_id = goal_ids[i]
        milestone = milestone_manager.get(milestone_id)
        if milestone is None:
            sims4.commands.output('Invalid milestone_id {}'.format(milestone_id), _connection)
            return False
        goal_id = goal_id if goal_id != 0 else None
        tracker.mark_milestone_as_viewed(milestone, goal_id=goal_id)


@sims4.commands.Command('lifetime_milestones.show_lifetime_milestones_panel', command_type=(sims4.commands.CommandType.Live))
def show_lifetime_milestones_panel(opt_sim: OptionalSimInfoParam=None, category_id: int=None, _connection=None):
    output = sims4.commands.output
    sim_info = get_optional_target(opt_sim, _connection)
    if sim_info is None:
        output('Target Sim not specified.', _connection)
        return False
    resolver = SingleSimResolver(sim_info)
    for loot_entry in DevelopmentalMilestone.VIEW_MILESTONES_LOOT:
        loot_entry.apply_to_resolver(resolver)

    tracker = sim_info.developmental_milestone_tracker
    if tracker is None:
        output('Target does not have a DevelopmentalMilestoneTracker.', _connection)
        return False
    msg = Sims_pb2.LifetimeMilestonesData()
    if category_id:
        msg.category_id = category_id
    op = GenericProtocolBufferOp(Operation.SHOW_LIFETIME_MILESTONES_PANEL, msg)
    Distributor.instance().add_op_with_no_owner(op)