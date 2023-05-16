# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gameplay_scenarios\scenario_handlers.py
# Compiled at: 2022-08-26 18:13:12
# Size of source mod 2**32: 12350 bytes
from date_and_time import DateAndTime
from situations.situation_goal_compound import SituationGoalCompound
import services
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
active_scenario_schema = GsiGridSchema(label='Active Scenario Data')
active_scenario_schema.add_field('scenario', label='Scenario')
active_scenario_schema.add_field('playtime', label='Time Played')
active_scenario_schema.add_field('active_phase', label='Active Phase')
with active_scenario_schema.add_has_many('Sims', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('sim_id', label='Sim ID', type=(GsiFieldVisualizers.INT))
    sub_schema.add_field('sim_name', label='Name')
    sub_schema.add_field('role', label='Scenario Role')
    sub_schema.add_field('is_instanced', label='Is Instanced?')
with active_scenario_schema.add_has_many('Phases', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('phase_name', label='Name')
    sub_schema.add_field('phase_state', label='State')
    sub_schema.add_field('phase_progress', label='Progress')
    sub_schema.add_field('phase_output', label='Output')
    sub_schema.add_field('phase_output_time', label='Output Time')
    sub_schema.add_field('next_phase', label='Next')
with active_scenario_schema.add_has_many('Goals', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('goal', label='Goal')
    sub_schema.add_field('parent', label='Parent')
    sub_schema.add_field('phase', label='Phase')
    sub_schema.add_field('progress', label='Progress')
    sub_schema.add_field('state', label='State')
    sub_schema.add_field('completion_time', label='Completion Time')
with active_scenario_schema.add_has_many('Terminators', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('condition', label='Condition')
    sub_schema.add_field('phase', label='Phase')
    sub_schema.add_field('state', label='State')
    sub_schema.add_field('scenario_outcome', label='Scenario Outcome')
    sub_schema.add_field('termination_time', label='Termination Time')

@GsiHandler('scenarios', active_scenario_schema)
def generate_scenario_data():
    household = services.active_household()
    if household is None:
        return
    scenario = household.scenario_tracker.active_scenario
    if scenario is None:
        return {'scenario': 'None'}
    return {'scenario':scenario.__class__.__name__, 
     'playtime':str(scenario.sim_time_lapsed), 
     'active_phase':resolve_active_phase_name(scenario), 
     'Sims':generate_sim_data(scenario), 
     'Phases':generate_phase_data(scenario), 
     'Goals':generate_goal_data(scenario), 
     'Terminators':generate_terminator_data(scenario), 
     'autoRefresh':True}


def generate_sim_data(scenario):
    data = []
    for sim_info in scenario.household:
        role = scenario.get_role_for_sim(sim_info.id)
        data.append({'sim_id':sim_info.id, 
         'sim_name':sim_info.full_name, 
         'role':'None' if role is None else str(role), 
         'is_instanced':'Yes' if sim_info.is_instanced else 'No'})

    return data


def generate_phase_data(scenario):
    data = []
    for phase in scenario.get_all_phases():
        output_key, next_phase_name, output_time = scenario.get_phase_last_output_info(phase.guid64) or (None,
                                                                                                         None,
                                                                                                         None)
        data.append({'phase_name':phase.__name__, 
         'phase_state':resolve_phase_state(scenario, phase), 
         'phase_progress':resolve_phase_progress(scenario, phase), 
         'phase_output':resolve_phase_output_key(output_key), 
         'phase_output_time':resolve_phase_output_time(output_time), 
         'next_phase':next_phase_name or 'N/A'})

    return data


def generate_goal_data(scenario):
    data = []
    phases = scenario.get_all_phases()
    if len(phases) != 0:
        active_goal_instances = {goal.guid64: goal for goal in scenario.active_goals_gen()}
        for phase in phases:
            for goal in phase.goals_gen():
                situation_goal = goal.situation_goal
                data.append(generate_per_goal_data(scenario, phase, situation_goal, active_goal_instances.get(situation_goal.guid64), None))
                for sub_goal in situation_goal.sub_goals:
                    data.append(generate_per_goal_data(scenario, phase, sub_goal, active_goal_instances.get(sub_goal.guid64), situation_goal))

    else:
        for goal in scenario.active_goals_gen():
            data.append(generate_per_goal_data_v2(goal, is_sub_goal=False))
            if issubclass(goal.__class__, SituationGoalCompound):
                for sub_goal in goal.sub_goals:
                    data.append(generate_per_goal_data_v2(sub_goal, is_sub_goal=True))

    return data


def generate_per_goal_data(scenario, phase, situation_goal, situation_goal_instance, parent_situation_goal):
    return {'goal':situation_goal.__name__, 
     'parent':parent_situation_goal.__name__ if parent_situation_goal is not None else 'N/A', 
     'phase':phase.__name__, 
     'progress':resolve_goal_progress_str(scenario, situation_goal, situation_goal_instance), 
     'state':resolve_goal_state(scenario, situation_goal, situation_goal_instance), 
     'completion_time':resolve_goal_completion_time(scenario.get_goal_completion_time(situation_goal.guid64))}


def generate_per_goal_data_v2(goal, is_sub_goal):
    return {'goal':goal.get_gsi_name(), 
     'progress':str(goal.completed_iterations) + ' / ' + str(goal.max_iterations), 
     'is_sub_goal':'Yes' if is_sub_goal else 'No'}


def generate_terminator_data(scenario):
    data = []
    for terminator in scenario.terminators:
        data.append({'condition':resolve_terminator_condition_str(terminator.termination_condition), 
         'phase':'N/A', 
         'state':'Active', 
         'scenario_outcome':terminator.scenario_outcome.__name__, 
         'termination_time':'N/A'})

    for phase in scenario.get_all_phases():
        for terminator in phase.terminators:
            data.append({'condition':resolve_terminator_condition_str(terminator.termination_condition), 
             'phase':phase.__name__, 
             'state':resolve_terminator_state_from_phase(scenario, phase), 
             'scenario_outcome':'N/A', 
             'termination_time':scenario.get_phase_termination_time(phase.guid64) or 'N/A'})

    return data


def resolve_active_phase_name(scenario):
    if scenario.current_phase is not None:
        return scenario.current_phase.__class__.__name__
    return 'None'


def resolve_phase_state(scenario, phase):
    if scenario.is_phase_active(phase.guid64):
        return 'Active'
    if scenario.is_phase_terminated(phase.guid64):
        return 'Terminated'
    if scenario.is_phase_skipped(phase.guid64):
        return 'Skipped'
    if scenario.is_phase_triggered(phase.guid64):
        return 'Triggered'
    return 'Unused'


def resolve_phase_progress(scenario, phase):
    goals = phase.mandatory_goals_list()
    total = sum((1 for _ in goals))
    completed = 0
    if scenario.is_phase_active(phase.guid64):
        remaining = 0
        for _, tuning in scenario.active_goals_and_tuning_gen():
            if tuning.mandatory:
                remaining += 1

        completed = total - remaining
    else:
        if scenario.is_phase_triggered(phase.guid64):
            if not scenario.is_phase_skipped(phase.guid64):
                completed = total
    return '{}/{}'.format(completed, total)


def resolve_phase_output_key(output_key):
    if output_key is None:
        return 'N/A'
    if output_key == -1:
        return ('Fallback', )
    return str(output_key)


def resolve_phase_output_time(output_time):
    if output_time is None:
        return 'N/A'
    date_and_time = DateAndTime(output_time)
    return str(date_and_time)


def resolve_goal_progress_str(scenario, situation_goal, active_situation_goal_instance):
    if active_situation_goal_instance is not None:
        return '{} / {}'.format(active_situation_goal_instance.completed_iterations, active_situation_goal_instance.max_iterations)
    if scenario.is_goal_completed(situation_goal.guid64):
        max_iterations = situation_goal.max_iterations
        return '{} / {}'.format(max_iterations, max_iterations)
    return '0 / {}'.format(situation_goal.max_iterations)


def resolve_goal_state(scenario, situation_goal, active_situation_goal_instance):
    if active_situation_goal_instance is not None:
        return 'Active'
    if scenario.is_goal_completed(situation_goal.guid64):
        return 'Completed'
    return 'Inactive'


def resolve_goal_completion_time(completion_time):
    if completion_time is None:
        return 'N/A'
    date_and_time = DateAndTime(completion_time)
    return str(date_and_time)


def resolve_terminator_condition_str(termination_condition):
    actor_role = termination_condition.scenario_test.actor_role
    actor_role_str = actor_role.__name__ if actor_role is not None else 'N/A'
    return str(termination_condition.scenario_test.test.__class__.__name__) + ', actor_role: ' + actor_role_str


def resolve_terminator_state_from_phase(scenario, phase):
    if scenario.is_phase_active(phase.guid64):
        return 'Active'
    if scenario.is_phase_terminated(phase.guid64):
        return 'Triggered'
    return 'Inactive'