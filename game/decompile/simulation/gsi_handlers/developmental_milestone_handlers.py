# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\developmental_milestone_handlers.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 9465 bytes
from build_buy import get_object_catalog_name
from developmental_milestones.developmental_milestone import DevelopmentalMilestone
from developmental_milestones.developmental_milestone_enums import DevelopmentalMilestoneStates
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
from sims.sim_info_types import Age
import services, sims4.resources
developmental_milestone_schema = GsiGridSchema(label='Developmental Milestones', sim_specific=True)
developmental_milestone_schema.add_field('sim_id', label='Sim ID', hidden=True)
developmental_milestone_schema.add_field('milestone', label='Milestone', unique_field=True, width=4.5)
developmental_milestone_schema.add_field('is_primary', label='Primary', width=1)
developmental_milestone_schema.add_field('is_repeatable', label='Repeatable', width=1)
developmental_milestone_schema.add_field('state', label='State', width=1.5)
developmental_milestone_schema.add_field('state_val', label='State Value', hidden=True)
developmental_milestone_schema.add_field('has_prev_goal', label='Completed Prev Goal', width=4.5)
developmental_milestone_schema.add_field('prerequisites', label='Prerequisites', width=5)
developmental_milestone_schema.add_field('goal', label='Goal', width=4)
developmental_milestone_schema.add_field('commodity', label='Commodity', width=4)
developmental_milestone_schema.add_field('value', label='Value', width=2)
developmental_milestone_schema.add_field('new_in_ui', label='New', width=1)
developmental_milestone_schema.add_field('inactive', label='Inactive', width=1)
developmental_milestone_schema.add_field('time_completed', label='Time Completed', width=4)
developmental_milestone_schema.add_field('age_completed', label='Age Completed', width=4)
developmental_milestone_schema.add_field('unlocked_with_sim_info', label='Unlocked with Sim', width=3)
developmental_milestone_schema.add_field('unlocked_with_object', label='Unlocked with Object', width=3)
developmental_milestone_schema.add_field('unlocked_in_zone', label='Unlocked in Zone', width=3)
developmental_milestone_schema.add_field('unlocked_career_track', label='Unlocked Career Track', width=3)
developmental_milestone_schema.add_field('unlocked_career_level', label='Unlocked Career Level', width=3)
developmental_milestone_schema.add_field('unlocked_trait', label='Unlocked Trait', width=3)
developmental_milestone_schema.add_field('unlocked_death_trait', label='Unlocked Death Trait', width=3)
with developmental_milestone_schema.add_has_many('previous_goals', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('goal', label='Goal', width=4)
    sub_schema.add_field('new_in_ui', label='New', width=2)
    sub_schema.add_field('time_completed', label='Time Completed', width=3)
    sub_schema.add_field('age_completed', label='Age Completed', width=3)
    sub_schema.add_field('unlocked_with_sim_info', label='Unlocked with Sim', width=3)
    sub_schema.add_field('unlocked_with_object', label='Unlocked with Object', width=3)
    sub_schema.add_field('unlocked_in_zone', label='Unlocked in Zone', width=3)
    sub_schema.add_field('unlocked_career_track', label='Unlocked Career Track', width=3)
    sub_schema.add_field('unlocked_career_level', label='Unlocked Career Level', width=3)
    sub_schema.add_field('unlocked_trait', label='Unlocked Trait', width=3)
    sub_schema.add_field('unlocked_death_trait', label='Unlocked Death Trait', width=3)

@GsiHandler('sim_developmental_milestone_view', developmental_milestone_schema)
def generate_sim_developmental_milestone_data(sim_id: int=None):
    milestone_view_data = []
    sim_info_manager = services.sim_info_manager()
    if sim_info_manager is not None:
        sim_info = sim_info_manager.get(sim_id)
        if sim_info is not None:
            tracker = sim_info.developmental_milestone_tracker
            if tracker is None:
                return False
            for milestone in services.get_instance_manager(sims4.resources.Types.DEVELOPMENTAL_MILESTONE).types.values():
                milestone_data = tracker._active_milestones_data.get(milestone)
                inactive = ''
                if milestone_data is None:
                    milestone_data = tracker._archived_milestones_data.get(milestone)
                    inactive = True
                if milestone_data is None:
                    continue
                is_primary = 'Yes' if milestone.is_primary_milestone is not None else ''
                milestone_state = tracker.get_milestone_state(milestone)
                new_in_ui = 'Yes' if (milestone_data and milestone_data.new_in_ui) else ''
                prerequisites_list = ''
                if milestone_state == DevelopmentalMilestoneStates.LOCKED:
                    if milestone.prerequisite_milestones:
                        prerequisites_list = str([prerequisite.__name__ for prerequisite in milestone.prerequisite_milestones])
                commodity_name = ''
                commodity_value = ''
                if not milestone_state == DevelopmentalMilestoneStates.ACTIVE:
                    if milestone_state == DevelopmentalMilestoneStates.UNLOCKED:
                        commodity = milestone.commodity
                        if commodity is not None:
                            commodity_name = commodity.__name__
                            if sim_info.has_statistic(commodity):
                                commodity_value = sim_info.get_stat_value(commodity)
                            else:
                                if milestone_state == DevelopmentalMilestoneStates.ACTIVE:
                                    commodity_value = 'MISSING'
                    is_repeatable = 'Yes' if milestone.repeatable else ''
                    time_completed = ''
                    age_completed = ''
                    has_prev_goal = ''
                    if milestone_data is not None:
                        time_completed = str(milestone_data.goal.completed_time) if (milestone_data.goal and milestone_data.goal.completed_time and isinstance(milestone_data.goal.completed_time, int)) else ''
                        age_completed = str(Age(milestone_data.age_completed)) if milestone_data.age_completed is not None else ''
                        has_prev_goal = '' if len(milestone_data.previous_goals) < 1 else 'yes'
                        previous_goals = []
                        for previous_goal_data in milestone_data.previous_goals.values():
                            goal = previous_goal_data.goal
                            prev_time_completed = str(goal.completed_time) if isinstance(goal.completed_time, int) else ''
                            prev_age_completed = str(Age(previous_goal_data.age_completed)) if previous_goal_data.age_completed is not None else ''
                            prev_goal_gsi_data = goal.get_gsi_data()
                            prev_goal_gsi_data.update({'new_in_ui':previous_goal_data.new_in_ui,  'time_completed':prev_time_completed, 
                             'age_completed':prev_age_completed})
                            previous_goals.append(prev_goal_gsi_data)

                    milestone_gsi_data = {'sim_id':str(sim_info.sim_id), 
                     'milestone':milestone.__name__, 
                     'is_repeatable':is_repeatable, 
                     'is_primary':is_primary, 
                     'state':milestone_state.name, 
                     'state_val':milestone_state, 
                     'has_prev_goal':has_prev_goal, 
                     'prerequisites':prerequisites_list, 
                     'commodity':commodity_name, 
                     'value':commodity_value, 
                     'new_in_ui':new_in_ui, 
                     'inactive':inactive, 
                     'previous_goals':previous_goals, 
                     'time_completed':time_completed, 
                     'age_completed':age_completed}
                    if milestone_state == DevelopmentalMilestoneStates.UNLOCKED and milestone_data.goal is not None:
                        milestone_gsi_data.update(milestone_data.goal.get_gsi_data())
                    else:
                        milestone_gsi_data.update({'goal': milestone.goal.__name__})
                    milestone_view_data.append(milestone_gsi_data)

    milestone_view_data.sort(key=(lambda data: str(int(data['state_val'])) + data['milestone']))
    return milestone_view_data