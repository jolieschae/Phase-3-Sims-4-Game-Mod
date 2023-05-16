# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\career_handlers.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 14496 bytes
from careers.career_enums import DecoratorGigLotType, GigResult
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
from sims4.resources import Types
import services, sims4.resources

def generate_all_careers():
    instance_manager = services.get_instance_manager(Types.CAREER)
    if instance_manager.all_instances_loaded:
        return [cls.__name__ for cls in instance_manager.types.values()]
    return []


sim_career_schema = GsiGridSchema(label='Careers')
sim_career_schema.add_field('sim', label='Sim', width=2, unique_field=True)
sim_career_schema.add_field('sim_id', label='Sim ID', hidden=True)
sim_career_schema.add_field('career_uid', label='UID', hidden=True)
sim_career_schema.add_field('name', label='Name', width=2)
sim_career_schema.add_field('level', label='Level')
sim_career_schema.add_field('seniority', label='Seniority')
sim_career_schema.add_field('location', label='Location')
sim_career_schema.add_field('time_to_work', label='Time To Work')
sim_career_schema.add_field('current_work_time', label='Current Work')
sim_career_schema.add_field('next_work_time', label='Next Work')
sim_career_schema.add_field('is_work_time', label='Is Work Time')
sim_career_schema.add_field('currently_at_work', label='Currently At Work')
sim_career_schema.add_field('work_performance', label='Performance', type=(GsiFieldVisualizers.INT))
sim_career_schema.add_field('professional_reputation', label='Reputation', type=(GsiFieldVisualizers.INT))
with sim_career_schema.add_has_many('career_levels', GsiGridSchema, label='Levels') as (sub_schema):
    sub_schema.add_field('name', label='Name')
    sub_schema.add_field('simoleons', label='Simoleons/Hr')
    sub_schema.add_field('fired_lvl', label='Fire Lvl')
    sub_schema.add_field('demotion_lvl', label='Demotion Lvl')
    sub_schema.add_field('promote_lvl', label='Promote Lvl')
with sim_career_schema.add_has_many('career_history', GsiGridSchema, label='History') as (sub_schema):
    sub_schema.add_field('career', label='Career')
    sub_schema.add_field('track', label='Track')
    sub_schema.add_field('level', label='Level', type=(GsiFieldVisualizers.INT))
    sub_schema.add_field('user_level', label='User Level', type=(GsiFieldVisualizers.INT))
    sub_schema.add_field('overmax_level', label='Overmax Level', type=(GsiFieldVisualizers.INT))
    sub_schema.add_field('highest_level', label='Highest Level', type=(GsiFieldVisualizers.INT))
    sub_schema.add_field('time_of_leave', label='Time of Leave')
    sub_schema.add_field('daily_pay', label='Daily Pay', type=(GsiFieldVisualizers.INT))
    sub_schema.add_field('days_worked', label='Days Worked', type=(GsiFieldVisualizers.INT))
with sim_career_schema.add_has_many('career_custom_data', GsiGridSchema, label='Custom Data') as (sub_schema):
    sub_schema.add_field('field_key', label='Field Name')
    sub_schema.add_field('field_value', label='Field Value')
with sim_career_schema.add_has_many('objectives', GsiGridSchema, label='Current Objectives') as (sub_schema):
    sub_schema.add_field('objective', label='Objective')
    sub_schema.add_field('is_complete', label='Complete?')
with sim_career_schema.add_has_many('assignments', GsiGridSchema, label='Active Assignments') as (sub_schema):
    sub_schema.add_field('assignment', label='Assignment')
with sim_career_schema.add_has_many('offered_assignments', GsiGridSchema, label='Offered Assignments') as (sub_schema):
    sub_schema.add_field('assignment', label='Assignment')
    sub_schema.add_field('test_result', label='Test Result')
with sim_career_schema.add_has_many('gig_history', GsiGridSchema, label='Gig History') as (sub_schema):
    sub_schema.add_field('gig_title', label='Gig Name')
    sub_schema.add_field('customer_name', label='Customer')
    sub_schema.add_field('customer_id', label='Customer ID', hidden=True)
    sub_schema.add_field('zone_id', label='Zone ID', hidden=True)
    sub_schema.add_field('gig_type', label='Gig Type')
    sub_schema.add_field('gig_result', label='Result')
    sub_schema.add_field('gig_score', label='Score')
    sub_schema.add_field('gig_score_data', label='Score Data')
with sim_career_schema.add_view_cheat('careers.promote', label='Promote') as (cheat):
    cheat.add_token_param('career_uid')
    cheat.add_token_param('sim_id')
with sim_career_schema.add_view_cheat('careers.demote', label='Demote') as (cheat):
    cheat.add_token_param('career_uid')
    cheat.add_token_param('sim_id')
with sim_career_schema.add_view_cheat('careers.lay_off', label='Lay Off') as (cheat):
    cheat.add_token_param('career_uid')
    cheat.add_token_param('sim_id')
with sim_career_schema.add_view_cheat('careers.retire', label='Retire') as (cheat):
    cheat.add_token_param('career_uid')
    cheat.add_token_param('sim_id')
with sim_career_schema.add_view_cheat('careers.remove_career', label='Remove Career') as (cheat):
    cheat.add_token_param('career_uid')
    cheat.add_token_param('sim_id')
with sim_career_schema.add_view_cheat('careers.add_performance', label='+50 Performance') as (cheat):
    cheat.add_token_param('sim_id')
    cheat.add_static_param('50')
    cheat.add_token_param('career_uid')

def add_career_cheats(manager):
    with sim_career_schema.add_view_cheat('careers.add_career', label='Add Career') as (cheat):
        cheat.add_token_param('career_string', dynamic_token_fn=generate_all_careers)
        cheat.add_token_param('sim_id')


services.get_instance_manager(Types.CAREER).add_on_load_complete(add_career_cheats)

def get_work_hours_str(start_time, end_time):
    return '{0:D} {0:h}:{0:m} - {1:D} {1:h}:{1:m}'.format(start_time, end_time)


def get_career_level_data(career, career_track, level_data):
    for level in career_track.career_levels:
        level_name = level.__name__
        if career.current_level_tuning is level:
            level_name = '** {} **'.format(level_name)
        career_level_info = {'name':level_name, 
         'simoleons':level.simoleons_per_hour, 
         'fired_lvl':level.fired_performance_level, 
         'demotion_lvl':level.demotion_performance_level, 
         'promote_lvl':level.promote_performance_level}
        level_data.append(career_level_info)

    for track in career_track.branches:
        get_career_level_data(career, track, level_data)


def get_all_career_level_data(career):
    career_level_data = []
    get_career_level_data(career, career.start_track, career_level_data)
    return career_level_data


def get_career_history_data(sim_info):
    career_manager = services.get_instance_manager(sims4.resources.Types.CAREER)
    if career_manager is None:
        return ()
    career_history_data = []
    if sim_info.career_tracker is None:
        return career_history_data
    for key, career_history in sim_info.career_tracker.career_history.items():
        career = career_manager.get(key[0])
        if career is None:
            continue
        career_history_data.append({'career':career.__name__, 
         'track':career_history.career_track.__name__, 
         'level':career_history.level, 
         'user_level':career_history.user_level, 
         'overmax_level':career_history.overmax_level, 
         'highest_level':career_history.highest_level, 
         'time_of_leave':str(career_history.time_of_leave), 
         'daily_pay':career_history.daily_pay, 
         'days_worked':career_history.days_worked})

    return career_history_data


def get_gig_history_data(sim_info):
    gig_manager = services.get_instance_manager(sims4.resources.Types.CAREER_GIG)
    if gig_manager is None:
        return ()
    gig_history_data = []
    if sim_info.career_tracker is None:
        return gig_history_data
    for gig_history in sim_info.career_tracker.gig_history.values():
        gig = gig_manager.get(gig_history.gig_id)
        gig_score_data = ''
        for result_range in gig.decorator_gig_tuning.scoring_results:
            gig_score_data += '[result: ' + str(GigResult(result_range.result_type)) + ', min: ' + str(result_range.min) + ', max: ' + str(result_range.max) + ']'

        gig_title = gig.__name__ if gig is not None else str(gig_history.project_title)
        gig_history_data.append({'gig_title':gig_title, 
         'customer_name':gig_history.customer_name, 
         'customer_id':str(hex(gig_history.customer_id)), 
         'zone_id':str(hex(gig_history.lot_id)), 
         'gig_type':str(DecoratorGigLotType(gig_history.gig_lot_type)), 
         'gig_result':str(GigResult(gig_history.gig_result)), 
         'gig_score':str(gig_history.gig_score), 
         'gig_score_data':gig_score_data})

    return gig_history_data


@GsiHandler('sim_career_view', sim_career_schema)
def generate_sim_career_view_data(sim_id: int=None):
    sim_info_manager = services.sim_info_manager()
    if sim_info_manager is None:
        return
    career_view_data = []
    for sim_info in list(sim_info_manager.objects):
        if sim_info.career_tracker is None:
            continue
        careers = sim_info.careers.values()
        if careers:
            for career in careers:
                career_data = {'sim':'{}(uid: {})'.format(sim_info.full_name, int(career.guid64)), 
                 'sim_id':str(sim_info.sim_id), 
                 'career_uid':int(career.guid64)}
                career_data['name'] = type(career).__name__
                career_data['level'] = '{} ({})'.format(career.user_level, career.level)
                career_data['seniority'] = '{:.3f}'.format(career.get_career_seniority())
                career_data['location'] = str(career.get_career_location())
                time_to_work, next_start_time, next_end_time = career.get_next_work_time()
                career_data['time_to_work'] = str(time_to_work)
                if career._current_work_start is not None:
                    career_data['current_work_time'] = get_work_hours_str(career._current_work_start, career._current_work_end)
                if next_start_time is not None:
                    career_data['next_work_time'] = get_work_hours_str(next_start_time, next_end_time)
                career_data['is_work_time'] = career.is_work_time
                career_data['currently_at_work'] = career.currently_at_work
                career_data['work_performance'] = career.work_performance
                career_data['professional_reputation'] = career.professional_reputation
                career_data['objectives'] = []
                if career.current_level_tuning.aspiration is not None:
                    for objective in career.current_level_tuning.aspiration.objectives:
                        objective_data = {}
                        objective_data['objective'] = str(objective)
                        if sim_info.aspiration_tracker is not None and sim_info.aspiration_tracker.objective_completed(objective):
                            objective_data['is_complete'] = True
                        else:
                            objective_data['is_complete'] = False
                        career_data['objectives'].append(objective_data)

                career_data['assignments'] = []
                if career.on_assignment:
                    for assignment in career.active_assignments:
                        assignment_data = {}
                        assignment_data['assignment'] = str(assignment)
                        career_data['assignments'].append(assignment_data)

                career_data['offered_assignments'] = []
                for offered_assignment, test_result in career.assignment_handler_gsi_cache:
                    offer_data = {}
                    offer_data['assignment'] = str(offered_assignment)
                    offer_data['test_result'] = str(test_result)
                    career_data['offered_assignments'].append(offer_data)

                career_level_data = get_all_career_level_data(career)
                career_data['career_levels'] = career_level_data
                career_data['career_history'] = get_career_history_data(sim_info)
                career_data['gig_history'] = get_gig_history_data(sim_info)
                career_data['career_custom_data'] = []
                for field_key, field_value in career.get_custom_gsi_data().items():
                    career_data['career_custom_data'].append({'field_key':field_key, 
                     'field_value':field_value})

                career_view_data.append(career_data)

        else:
            career_data = {'sim':sim_info.full_name, 
             'sim_id':str(sim_info.sim_id)}
            career_data['name'] = 'No Career'
            career_data['career_levels'] = []
            career_data['career_history'] = get_career_history_data(sim_info)
            career_data['gig_history'] = get_gig_history_data(sim_info)
            career_view_data.append(career_data)

    return career_view_data