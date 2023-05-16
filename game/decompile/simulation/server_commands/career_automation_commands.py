# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\career_automation_commands.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 5908 bytes
from sims4.commands import automation_output
from server_commands.argument_helpers import get_optional_target, OptionalSimInfoParam, TunableInstanceParam
from date_and_time import create_time_span
from interactions.interaction_finisher import FinishingType
import sims4, sims4.commands, sims4.log, services, sims4.tuning.tunable
logger = sims4.log.Logger('CareerAutomationCommand', default_owner='kalucas')

@sims4.commands.Command('career_automation.schedule_work_now', command_type=(sims4.commands.CommandType.Automation))
def schedule_work_now(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), sim_id: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(sim_id, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        sims4.commands.output('Failed to find Sim', _connection)
        return
    else:
        career = sim_info.career_tracker.get_career_by_uid(career_type.guid64)
        schedule_start_time = services.time_service().sim_now
        _, next_start_time, next_end_time = career.get_next_work_time()
        career.start_new_career_session(schedule_start_time, schedule_start_time + create_time_span(hours=((next_end_time - next_start_time).in_hours())))
        career._try_offer_career_event()
        if career._current_work_start is schedule_start_time:
            msg = 'Succeeded, work immediately scheduled'
        else:
            msg = 'Failed, work not immediately scheduled'
    sims4.commands.automation_output(msg, _connection)


@sims4.commands.Command('career_automation.skip_first_day_flow', command_type=(sims4.commands.CommandType.Automation))
def skip_first_day_flow(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), sim_id: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(sim_id, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        sims4.commands.output('Failed to find Sim', _connection)
        return
    else:
        career = sim_info.career_tracker.get_career_by_uid(career_type.guid64)
        career.active_days_worked_statistic.add_value(2)
        career._has_attended_first_day = True
        if career.has_attended_first_day:
            msg = 'Succeeded, work immediately scheduled'
        else:
            msg = 'Failed, work not immediately scheduled'
    sims4.commands.automation_output(msg, _connection)


@sims4.commands.Command('career_automation.get_career_end_time', command_type=(sims4.commands.CommandType.Automation))
def get_career_end_time(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), sim_id: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(sim_id, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        sims4.commands.output('Failed to find Sim', _connection)
        return
    career = sim_info.career_tracker.get_career_by_uid(career_type.guid64)
    career_end_time = career._current_work_end.absolute_minutes()
    sims4.commands.output('EndTime; Time:{}'.format(career_end_time), _connection)
    sims4.commands.automation_output('EndTime; Time:{}'.format(career_end_time), _connection)


@sims4.commands.Command('career_automation.cancel_interactions_on_children', command_type=(sims4.commands.CommandType.Automation))
def cancel_interactions_on_children(obj_id: int, _connection=None):
    obj = services.object_manager().get(obj_id)
    sims4.commands.automation_output('InteractionSimId; Status:Begin', _connection)
    if obj is None:
        sims4.commands.output('Object id could not be resolved', _connection)
        sims4.commands.automation_output('InteractionSimId; Status:End', _connection)
        return
    obj_children = obj.children
    for child in obj_children:
        if child._interaction_refs is None:
            continue
        interactions = tuple(child._interaction_refs)
        for interaction in interactions:
            interaction.cancel((FinishingType.INTERACTION_INCOMPATIBILITY), cancel_reason_msg='Canceling interaction for cancel_interactions_on_children command.', ignore_must_run=True, immediate=True)
            sims4.commands.output('Canceled interaction {} on object {} out of interactions {}'.format(interaction, child, interactions), _connection)
            sims4.commands.output('InteractionSimId; Status:Data, SimId:{}'.format(interaction.sim.id), _connection)
            sims4.commands.automation_output('InteractionSimId; Status:Data, SimId:{}'.format(interaction.sim.id), _connection)

    sims4.commands.automation_output('InteractionSimId; Status:End', _connection)