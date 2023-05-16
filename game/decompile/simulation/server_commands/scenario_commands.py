# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\scenario_commands.py
# Compiled at: 2022-08-26 18:13:12
# Size of source mod 2**32: 8028 bytes
from gameplay_scenarios import scenario_tracker
import services, sims4.commands, sims4.log
from gameplay_scenarios.scenario import Scenario
from server_commands.argument_helpers import TunableInstanceParam
logger = sims4.log.Logger('Scenarios')

def get_active_scenario_tracker(task_name_for_log: str='', log_failures: bool=True):
    active_household = services.active_household()
    if not active_household:
        if log_failures:
            sims4.commands.output('Failed to {} as there is no active household', task_name_for_log)
        return
    if not active_household.scenario_tracker:
        if log_failures:
            sims4.commands.output('Failed to {} as there is no active scenario', task_name_for_log)
        return
    return active_household.scenario_tracker


@sims4.commands.Command('scenarios.complete_goal', command_type=(sims4.commands.CommandType.DebugOnly))
def complete_goal(goal_id: int=0):
    active_scenario_tracker = get_active_scenario_tracker('complete goal')
    if active_scenario_tracker:
        active_scenario_tracker.force_complete_goal(goal_id)


@sims4.commands.Command('scenarios.toggle_show_hidden_goals', command_type=(sims4.commands.CommandType.DebugOnly))
def toggle_show_hidden_goals(enable: bool=None):
    if enable is None:
        enable = not scenario_tracker._show_hidden_goals
    scenario_tracker._show_hidden_goals = enable
    active_scenario_tracker = get_active_scenario_tracker(log_failures=False)
    if active_scenario_tracker:
        active_scenario_tracker.send_goal_update_op_to_client()


@sims4.commands.Command('scenarios.start', command_type=(sims4.commands.CommandType.DebugOnly))
def start_scenario(scenario_type: TunableInstanceParam(sims4.resources.Types.SNIPPET), _connection=None):
    household = services.active_household()
    if household is None:
        sims4.commands.output('Could not find an active household. Cannot start the scenario.', _connection)
        return

    def logger(msg):
        sims4.commands.output(msg, _connection)

    household.scenario_tracker.start_scenario(scenario_type, logger=logger)


@sims4.commands.Command('scenarios.cancel', command_type=(sims4.commands.CommandType.Live))
def cancel_scenario(_connection=None):
    household = services.active_household()
    if household is None:
        sims4.commands.output('Could not find an active household. Cannot cancel the scenario.', _connection)
        return

    def logger(msg):
        sims4.commands.output(msg, _connection)

    household.scenario_tracker.cancel_scenario(logger=logger)


def get_active_scenario(task_name_for_log: str=''):
    active_scenario_tracker = get_active_scenario_tracker(task_name_for_log)
    active_scenario = active_scenario_tracker.active_scenario
    if active_scenario is None:
        sims4.commands.output('No active scenario.')
    return active_scenario


@sims4.commands.Command('scenarios.reset_active_phase', command_type=(sims4.commands.CommandType.Cheat))
def reset_active_phase(_connection=None):
    active_scenario = get_active_scenario(_connection)
    if active_scenario is not None:
        active_scenario.reset_active_phase()


@sims4.commands.Command('scenarios.start_phase', command_type=(sims4.commands.CommandType.Cheat))
def start_scenario_phase(phase: TunableInstanceParam(sims4.resources.Types.SNIPPET), _connection=None):
    if phase is None:
        sims4.commands.output('{} is not a valid phase.'.format(phase), _connection)
        return
    active_scenario = get_active_scenario(_connection)
    if active_scenario is not None:
        active_scenario.start_phase(phase(scenario=active_scenario))


@sims4.commands.Command('scenarios.get_all_phases', command_type=(sims4.commands.CommandType.Cheat))
def get_current_scenario_all_phases(_connection=None):
    active_scenario = get_active_scenario(_connection)
    if active_scenario is not None:
        for phase in active_scenario.get_all_phases():
            sims4.commands.output('{}'.format(phase.__name__), _connection)


@sims4.commands.Command('scenarios.reset_goal', command_type=(sims4.commands.CommandType.Cheat))
def reset_scenario_goal(situation_goal: TunableInstanceParam(sims4.resources.Types.SITUATION_GOAL), _connection=None):
    if situation_goal is None:
        sims4.commands.output('{} is not a valid goal.'.format(situation_goal), _connection)
        return
    active_scenario = get_active_scenario(_connection)
    if active_scenario is not None:
        if not active_scenario.reset_goal(situation_goal.guid64):
            sims4.commands.output('Goal:{} is not an active goal.'.format(situation_goal), _connection)


@sims4.commands.Command('scenarios.get_all_active_goals', command_type=(sims4.commands.CommandType.Cheat))
def get_current_scenario_all_active_goals(_connection=None):
    active_scenario = get_active_scenario(_connection)
    if active_scenario is not None:
        for situation_goal in active_scenario.active_goals_gen():
            sims4.commands.output('{}'.format(situation_goal), _connection)


def get_active_scenario_tracker(task_name_for_log: str='', log_failures: bool=True):
    active_household = services.active_household()
    if not active_household:
        if log_failures:
            sims4.commands.output('Failed to {} as there is no active household', task_name_for_log)
        return
    if not active_household.scenario_tracker:
        if log_failures:
            sims4.commands.output('Failed to {} as there is no active scenario', task_name_for_log)
        return
    return active_household.scenario_tracker


@sims4.commands.Command('scenarios.complete_goal', command_type=(sims4.commands.CommandType.DebugOnly))
def complete_goal(goal_id: int=0):
    active_scenario_tracker = get_active_scenario_tracker('complete goal')
    if active_scenario_tracker:
        active_scenario_tracker.force_complete_goal(goal_id)


@sims4.commands.Command('scenarios.dump', command_type=(sims4.commands.CommandType.DebugOnly))
def dump_scenarios(_connection=None):
    instance_manager = services.get_instance_manager(sims4.resources.Types.SNIPPET)
    count = 0
    for scenario in instance_manager.get_ordered_types(only_subclasses_of=Scenario):
        sims4.commands.output('{} {}'.format(scenario.guid64, scenario.__name__), _connection)
        count += 1

    sims4.commands.output('Count = {}'.format(count), _connection)