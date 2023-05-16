# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\career_commands.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 50889 bytes
from careers.career_base import set_career_event_override
from careers.career_event_manager import CareerEventManager
from careers.career_ops import CareerOps
from careers.career_tuning import Career
from careers.career_enums import CareerShiftType, TestEventCareersOrigin
from event_testing.game_option_tests import TestableGameOptions
from event_testing.resolver import SingleSimResolver
from event_testing.test_events import TestEvent
from interactions.context import QueueInsertStrategy
from objects.system import find_object
from rewards.reward_enums import RewardType
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target, TunableInstanceParam, RequiredTargetParam, OptionalSimInfoParam
from sims.sim_info_lod import SimInfoLODLevel
from sims4.common import Pack
from sims4.localization import LocalizationHelperTuning
import build_buy, distributor, interactions, random, services, sims4.commands, sims4.log
logger = sims4.log.Logger('CareerCommand', default_owner='rrodgers')

@sims4.commands.Command('careers.select', command_type=(sims4.commands.CommandType.Live))
def select_career--- This code section failed: ---

 L.  43         0  LOAD_FAST                'sim_id'
                2  LOAD_CONST               None
                4  COMPARE_OP               is
                6  POP_JUMP_IF_TRUE     32  'to 32'
                8  LOAD_FAST                'career_instance_id'
               10  LOAD_CONST               None
               12  COMPARE_OP               is
               14  POP_JUMP_IF_TRUE     32  'to 32'
               16  LOAD_FAST                'track_id'
               18  LOAD_CONST               None
               20  COMPARE_OP               is
               22  POP_JUMP_IF_TRUE     32  'to 32'
               24  LOAD_FAST                'level'
               26  LOAD_CONST               None
               28  COMPARE_OP               is
               30  POP_JUMP_IF_FALSE    46  'to 46'
             32_0  COME_FROM            22  '22'
             32_1  COME_FROM            14  '14'
             32_2  COME_FROM             6  '6'

 L.  44        32  LOAD_GLOBAL              logger
               34  LOAD_METHOD              error
               36  LOAD_STR                 'Not all of the data needed for the careers.select command was passed.'
               38  CALL_METHOD_1         1  '1 positional argument'
               40  POP_TOP          

 L.  45        42  LOAD_CONST               False
               44  RETURN_VALUE     
             46_0  COME_FROM            30  '30'

 L.  47        46  LOAD_GLOBAL              services
               48  LOAD_METHOD              get_instance_manager
               50  LOAD_GLOBAL              sims4
               52  LOAD_ATTR                resources
               54  LOAD_ATTR                Types
               56  LOAD_ATTR                CAREER
               58  CALL_METHOD_1         1  '1 positional argument'
               60  STORE_FAST               'career_manager'

 L.  48        62  LOAD_FAST                'career_manager'
               64  LOAD_METHOD              get
               66  LOAD_FAST                'career_instance_id'
               68  CALL_METHOD_1         1  '1 positional argument'
               70  STORE_FAST               'career_type'

 L.  49        72  LOAD_FAST                'career_type'
               74  LOAD_CONST               None
               76  COMPARE_OP               is
               78  POP_JUMP_IF_FALSE    94  'to 94'

 L.  50        80  LOAD_GLOBAL              logger
               82  LOAD_METHOD              error
               84  LOAD_STR                 'invalid career Id sent to careers.select'
               86  CALL_METHOD_1         1  '1 positional argument'
               88  POP_TOP          

 L.  51        90  LOAD_CONST               False
               92  RETURN_VALUE     
             94_0  COME_FROM            78  '78'

 L.  53        94  LOAD_FAST                'sim_id'
               96  LOAD_CONST               None
               98  COMPARE_OP               is
              100  POP_JUMP_IF_FALSE   116  'to 116'

 L.  54       102  LOAD_GLOBAL              logger
              104  LOAD_METHOD              error
              106  LOAD_STR                 'invalid sim Id passed to careers.select'
              108  CALL_METHOD_1         1  '1 positional argument'
              110  POP_TOP          

 L.  55       112  LOAD_CONST               False
              114  RETURN_VALUE     
            116_0  COME_FROM           100  '100'

 L.  57       116  LOAD_GLOBAL              services
              118  LOAD_METHOD              sim_info_manager
              120  CALL_METHOD_0         0  '0 positional arguments'
              122  LOAD_METHOD              get
              124  LOAD_FAST                'sim_id'
              126  CALL_METHOD_1         1  '1 positional argument'
              128  STORE_FAST               'sim_info'

 L.  59       130  LOAD_FAST                'sim_info'
              132  LOAD_CONST               None
              134  COMPARE_OP               is
              136  POP_JUMP_IF_FALSE   152  'to 152'

 L.  60       138  LOAD_GLOBAL              logger
              140  LOAD_METHOD              error
              142  LOAD_STR                 'invalid sim Id passed to careers.select. No sim info was found'
              144  CALL_METHOD_1         1  '1 positional argument'
              146  POP_TOP          

 L.  61       148  LOAD_CONST               False
              150  RETURN_VALUE     
            152_0  COME_FROM           136  '136'

 L.  63       152  LOAD_GLOBAL              services
              154  LOAD_METHOD              get_instance_manager
              156  LOAD_GLOBAL              sims4
              158  LOAD_ATTR                resources
              160  LOAD_ATTR                Types
              162  LOAD_ATTR                CAREER_TRACK
              164  CALL_METHOD_1         1  '1 positional argument'
              166  STORE_FAST               'career_track_manager'

 L.  64       168  LOAD_FAST                'career_track_manager'
              170  LOAD_METHOD              get
              172  LOAD_FAST                'track_id'
              174  CALL_METHOD_1         1  '1 positional argument'
              176  STORE_FAST               'career_track'

 L.  65       178  LOAD_FAST                'career_track'
              180  LOAD_CONST               None
              182  COMPARE_OP               is
              184  POP_JUMP_IF_FALSE   200  'to 200'

 L.  66       186  LOAD_GLOBAL              logger
              188  LOAD_METHOD              error
              190  LOAD_STR                 'invalid career track Id passed to careers.select'
              192  CALL_METHOD_1         1  '1 positional argument'
              194  POP_TOP          

 L.  67       196  LOAD_CONST               False
              198  RETURN_VALUE     
            200_0  COME_FROM           184  '184'

 L.  69       200  LOAD_FAST                'reason'
              202  LOAD_CONST               None
              204  COMPARE_OP               is
              206  POP_JUMP_IF_FALSE   222  'to 222'

 L.  70       208  LOAD_GLOBAL              logger
              210  LOAD_METHOD              error
              212  LOAD_STR                 'invalid career selection reason passed to careers.select'
              214  CALL_METHOD_1         1  '1 positional argument'
              216  POP_TOP          

 L.  71       218  LOAD_CONST               False
              220  RETURN_VALUE     
            222_0  COME_FROM           206  '206'

 L.  74       222  LOAD_FAST                'sim_info'
              224  LOAD_ATTR                career_tracker
              226  STORE_FAST               'career_tracker'

 L.  75       228  LOAD_FAST                'reason'
              230  LOAD_GLOBAL              CareerOps
              232  LOAD_ATTR                JOIN_CAREER
              234  COMPARE_OP               ==
          236_238  POP_JUMP_IF_FALSE   348  'to 348'

 L.  76       240  LOAD_FAST                'career_tracker'
              242  LOAD_METHOD              get_career_by_uid
              244  LOAD_FAST                'career_instance_id'
              246  CALL_METHOD_1         1  '1 positional argument'
              248  STORE_FAST               'current_career'

 L.  77       250  LOAD_FAST                'current_career'
              252  LOAD_CONST               None
              254  COMPARE_OP               is-not
          256_258  POP_JUMP_IF_FALSE   272  'to 272'

 L.  80       260  LOAD_FAST                'current_career'
              262  LOAD_METHOD              on_branch_selection
              264  LOAD_FAST                'career_track'
              266  CALL_METHOD_1         1  '1 positional argument'
              268  POP_TOP          
              270  JUMP_FORWARD        348  'to 348'
            272_0  COME_FROM           256  '256'

 L.  82       272  LOAD_FAST                'level'
              274  LOAD_GLOBAL              len
              276  LOAD_FAST                'career_track'
              278  LOAD_ATTR                career_levels
              280  CALL_FUNCTION_1       1  '1 positional argument'
              282  COMPARE_OP               >=
          284_286  POP_JUMP_IF_FALSE   310  'to 310'

 L.  83       288  LOAD_GLOBAL              logger
              290  LOAD_ATTR                error
              292  LOAD_STR                 'The career track {} does not have a level {}'

 L.  84       294  LOAD_FAST                'career_track'
              296  LOAD_FAST                'level'
              298  LOAD_STR                 'jmorrow'
              300  LOAD_CONST               ('owner',)
              302  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
              304  POP_TOP          

 L.  85       306  LOAD_CONST               False
              308  RETURN_VALUE     
            310_0  COME_FROM           284  '284'

 L.  89       310  LOAD_FAST                'career_type'
              312  LOAD_FAST                'sim_info'
              314  CALL_FUNCTION_1       1  '1 positional argument'
              316  STORE_FAST               'career'

 L.  90       318  LOAD_FAST                'career_tracker'
              320  LOAD_ATTR                add_career
              322  LOAD_FAST                'career'

 L.  91       324  LOAD_CONST               True

 L.  92       326  LOAD_FAST                'schedule_shift_type'

 L.  93       328  LOAD_FAST                'career_track'
              330  LOAD_ATTR                career_levels
              332  LOAD_FAST                'level'
              334  BINARY_SUBSCR    

 L.  94       336  LOAD_GLOBAL              RewardType
              338  LOAD_ATTR                MONEY
              340  BUILD_TUPLE_1         1 
              342  LOAD_CONST               ('show_confirmation_dialog', 'schedule_shift_override', 'career_level_override', 'disallowed_reward_types')
              344  CALL_FUNCTION_KW_5     5  '5 total positional and keyword args'
              346  POP_TOP          
            348_0  COME_FROM           270  '270'
            348_1  COME_FROM           236  '236'

 L.  96       348  LOAD_FAST                'reason'
              350  LOAD_GLOBAL              CareerOps
              352  LOAD_ATTR                QUIT_CAREER
              354  COMPARE_OP               ==
          356_358  POP_JUMP_IF_FALSE   376  'to 376'

 L.  97       360  LOAD_FAST                'career_tracker'
              362  LOAD_ATTR                remove_career
              364  LOAD_FAST                'career_instance_id'
              366  LOAD_GLOBAL              TestEventCareersOrigin
              368  LOAD_ATTR                QUIT_CAREER
              370  LOAD_CONST               ('test_event_origin',)
              372  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              374  POP_TOP          
            376_0  COME_FROM           356  '356'

Parse error at or near `POP_TOP' instruction at offset 374


@sims4.commands.Command('careers.send_to_work', command_type=(sims4.commands.CommandType.Live))
def send_to_work(sim_id: int=None, career_uid: int=None, _connection=None):
    if sim_id is None:
        logger.error('careers.send_to_work got no Sim to start the event for.')
        return False
    else:
        sim_info = services.sim_info_manager.get(sim_id)
        if sim_info is None:
            logger.error('invalid sim Id passed to careers.send_to_work')
            return False
        career = sim_info.career_tracker.get_career_by_uid(career_uid)
        if career.can_work_early:
            career.go_to_work_early
            return
        return sim_info.career_tracker.available_for_work(career) or None
    career.put_sim_in_career_rabbit_hole


@sims4.commands.Command('careers.set_follow_enabled', command_type=(sims4.commands.CommandType.Live))
def set_follow_enabled(sim_id: int=None, career_uid: int=None, enabled: bool=False, _connection=None):
    if sim_id is None:
        logger.error('Careers.set_follow_enabled got no Sim.')
        return False
    sim_info = services.sim_info_manager.get(sim_id)
    if sim_info is None:
        logger.error('Invalid sim Id passed to careers.set_follow_enabled')
        return False
    career_tracker = sim_info.career_tracker
    career = career_tracker.get_career_by_uid(career_uid)
    if career is None:
        logger.error('Invalid career Id passed to careers.set_follow_enabled')
        return False
    career.follow_enabled = enabled
    career_tracker.resend_career_data
    return True


@sims4.commands.Command('careers.leave_work', command_type=(sims4.commands.CommandType.Live))
def leave_work(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), sim_id: int=None, _connection=None):
    if sim_id is None:
        logger.error('careers.leave_work got no Sim to start the event for.')
        return False
    sim_info = services.sim_info_manager.get(sim_id)
    if sim_info is None:
        logger.error('invalid Sim Id passed to careers.leave_work')
        return False
    career = sim_info.career_tracker.get_career_by_uid(career_type.guid64)
    if career is None:
        logger.error('invalid Career Id passed to careers.leave_work')
        return False
    if career.is_work_time:
        career.leave_work_early
    return True


@sims4.commands.Command('careers.on_career_event_scoring_dialog_close', command_type=(sims4.commands.CommandType.Live))
def on_career_event_scoring_dialog_close(sim_id: int=None, _connection=None):
    if sim_id is None:
        logger.error('careers.leave_work got no Sim to start the event for.')
        return False
    sim = services.sim_info_manager.get(sim_id)
    if sim is None:
        logger.error('invalid Sim Id passed to careers.on_career_event_scoring_dialog_close')
        return False
    CareerEventManager.post_career_event_travel(sim)
    return True


@sims4.commands.Command('careers.stay_late', command_type=(sims4.commands.CommandType.Live))
def stay_late(_connection=None):
    career = services.get_career_service.get_career_in_career_event
    if career is not None:
        career.extend_career_session


@sims4.commands.Command('careers.list_careers')
def list_all_careers(_connection=None):
    career_manager = services.get_instance_manager(sims4.resources.Types.CAREER)
    current_time = services.time_service.sim_now
    sims4.commands.output('Current Time: {}'.format(current_time), _connection)
    for career_id in career_manager.types:
        career = career_manager.get(career_id)
        sims4.commands.output('{}: {}'.format(career, int(career.guid64)), _connection)
        cur_track = career.start_track
        sims4.commands.output('    {}: {}'.format(cur_track, int(cur_track.guid)), _connection)
        for career_level in cur_track.career_levels:
            sims4.commands.output('        {}'.format(career_level), _connection)


@sims4.commands.Command('qa.careers.info', command_type=(sims4.commands.CommandType.Automation))
def qa_print_sim_career_info(opt_sim: OptionalTargetParam=None, _connection=None):
    output = sims4.commands.AutomationOutput(_connection)
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('Target sim could not be found', _connection)
        return
    careers = sim.sim_info.careers.values
    results = 'CareerInfo; NumCareers:%d' % len(careers)
    for idx, career in enumerate(careers):
        company_name = career.get_company_name
        results += ', Name%d:%s' % (idx, type(career).__name__) + ', Performance%d:%s' % (idx, career.work_performance) + ', Level%d:%s' % (idx, career.level) + ', Track%d:%s' % (idx, career.current_track_tuning.__name__) + ', Company%d:%s' % (idx, company_name.hash)

    output(results)
    sims4.commands.output(results, _connection)


@sims4.commands.Command('careers.add_career', command_type=(sims4.commands.CommandType.Cheat))
def add_career_to_sim(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if career_type is None:
        career_names = []
        career_manager = services.get_instance_manager(sims4.resources.Types.CAREER)
        for career_id in career_manager.types:
            career_type = career_manager.get(career_id)
            career_names.append(career_type.__name__)

        all_careers_str = ' '.join(career_names)
        sims4.commands.output('Usage: careers.add_career <career_name> <opt_sim>)'.format(all_careers_str), _connection)
        sims4.commands.output('Please choose a valid career: {}'.format(all_careers_str), _connection)
        return
    if sim is not None:
        sim.sim_info.career_tracker.add_career(career_type(sim.sim_info))
        return True


@sims4.commands.Command('careers.remove_career', command_type=(sims4.commands.CommandType.Cheat))
def remove_career_from_sim(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        sim.sim_info.career_tracker.remove_career(career_type.guid64)
        return True
    return False


@sims4.commands.Command('careers.set_career_lay_off_enabled', pack=(Pack.EP13), command_type=(sims4.commands.CommandType.Live))
def set_career_lay_off_enabled(enabled: bool=True, _connection=None):
    career_service = services.get_career_service
    if career_service is None:
        return False
    career_service.career_lay_off_enabled = enabled
    services.get_event_manager.process_event((TestEvent.TestedGameOptionChanged), custom_keys=(
     TestableGameOptions.CAREER_LAY_OFF_ENABLED,))
    return True


@sims4.commands.Command('careers.lay_off', pack=(Pack.EP13), command_type=(sims4.commands.CommandType.Cheat))
def career_lay_off(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), opt_sim: OptionalTargetParam=None, _connection=None):
    career_service = services.get_career_service
    if not (career_service is None or career_service.career_lay_off_enabled):
        sims4.commands.output('The Career Lay Off pack game option is disabled.', _connection)
        return False
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        career = sim.sim_info.career_tracker.get_career_by_uid(career_type.guid64)
        if career is not None:
            career.lay_off
            return True
    return False


@sims4.commands.Command('careers.promote', command_type=(sims4.commands.CommandType.Cheat))
def career_promote_sim(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), opt_sim: OptionalTargetParam=None, check_can_change_level: bool=False, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        career = sim.sim_info.career_tracker.get_career_by_uid(career_type.guid64)
        if career is not None:
            if not check_can_change_level:
                career.promote
                return True
            if career.can_change_level:
                career.promote
                return True
    return False


@sims4.commands.Command('careers.demote', command_type=(sims4.commands.CommandType.Cheat))
def career_demote_sim(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        career = sim.sim_info.career_tracker.get_career_by_uid(career_type.guid64)
        if career is not None:
            career.demote
            return True
    return False


@sims4.commands.Command('careers.retire', command_type=(sims4.commands.CommandType.Cheat))
def career_retire_sim(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        return False
    sim_info.career_tracker.retire_career(career_type.guid64)
    return True


@sims4.commands.Command('careers.pay_retirement')
def career_pay_retirement(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        return False
    retirement = sim_info.career_tracker.retirement
    if retirement is None:
        return False
    retirement.pay_retirement
    return True


@sims4.commands.Command('careers.add_performance', command_type=(sims4.commands.CommandType.Cheat))
def add_career_performance(opt_sim: OptionalTargetParam=None, amount: int=None, career_type: TunableInstanceParam(sims4.resources.Types.CAREER)=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('careers.add_performance Invalid Sim passed', _connection)
        sims4.commands.output('Usage: careers.add_performance <opt_sim> <amount> <career type>', _connection)
        return
    if amount is None:
        sims4.commands.output('careers.add_performance Invalid amount passed', _connection)
        sims4.commands.output('Usage: careers.add_performance <opt_sim> <amount> <career type>', _connection)
        return
    if career_type is None:
        sims4.commands.output('careers.add_performance Invalid career passed', _connection)
        sims4.commands.output('Usage: careers.add_performance <opt_sim> <amount> <career type>', _connection)
        return
    if len(sim.sim_info.careers) > 0:
        career = sim.sim_info.career_tracker.get_career_by_uid(career_type.guid64)
        if career is not None:
            performance_stat = sim.statistic_tracker.get_statistic(career.current_level_tuning.performance_stat)
            performance_stat.add_value(amount)


@sims4.commands.Command('careers.set_performance', command_type=(sims4.commands.CommandType.Cheat))
def set_career_performance(career_type: TunableInstanceParam(sims4.resources.Types.CAREER)=None, amount: int=None, opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('careers.set_performance Invalid Sim passed', _connection)
        sims4.commands.output('Usage: careers.set_performance <career type> <amount> <opt_sim>', _connection)
        return
    if amount is None:
        sims4.commands.output('careers.set_performance Invalid amount passed', _connection)
        sims4.commands.output('Usage: careers.set_performance <career type> <amount> <opt_sim>', _connection)
        return
    if career_type is None:
        sims4.commands.output('careers.set_performance Invalid career passed', _connection)
        sims4.commands.output('Usage: careers.set_performance <career type> <amount> <opt_sim>', _connection)
        return
    if len(sim.sim_info.careers) > 0:
        career = sim.sim_info.career_tracker.get_career_by_uid(career_type.guid64)
        if career is not None:
            performance_stat = sim.statistic_tracker.get_statistic(career.current_level_tuning.performance_stat)
            performance_stat.set_value(amount)
            sim.sim_info.career_tracker.resend_career_data


@sims4.commands.Command('careers.set_performance_percentage', command_type=(sims4.commands.CommandType.Cheat))
def set_career_performance_percentage(career_type: TunableInstanceParam(sims4.resources.Types.CAREER)=None, percent: float=None, opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('careers.set_performance Invalid Sim passed', _connection)
        sims4.commands.output('Usage: careers.set_performance_percentage <career type> <percent> <opt_sim>', _connection)
        return
    if percent is None:
        sims4.commands.output('careers.set_performance Invalid amount passed', _connection)
        sims4.commands.output('Usage: careers.set_performance_percentage <career type> <percent> <opt_sim>', _connection)
        return
    if career_type is None:
        sims4.commands.output('careers.set_performance Invalid career passed', _connection)
        sims4.commands.output('Usage: careers.set_performance_percentage <career type> <percent> <opt_sim>', _connection)
        return
    if len(sim.sim_info.careers) > 0:
        career = sim.sim_info.career_tracker.get_career_by_uid(career_type.guid64)
        if career is not None:
            performance_stat = sim.statistic_tracker.get_statistic(career.current_level_tuning.performance_stat)
            stat_range = performance_stat.max_value - performance_stat.min_value
            amount = percent * stat_range + performance_stat.min_value
            performance_stat.set_value(amount)
            sim.sim_info.career_tracker.resend_career_data


@sims4.commands.Command('careers.update_find_career_interaction_availability', command_type=(sims4.commands.CommandType.Live))
def update_find_career_interaction_availability(sim: RequiredTargetParam=None, _connection=None):
    client = services.client_manager.get(_connection)
    sim = sim.get_target
    context = client.create_interaction_context(sim)
    aop = Career.FIND_JOB_PHONE_INTERACTION.generate_aop(sim, context)
    test_result = aop.test(context)
    tooltip = None if test_result.tooltip is None else test_result.tooltip(sim)
    op = distributor.ops.UpdateFindCareerInteractionAvailability(test_result.result, tooltip)
    distributor.system.Distributor.instance.add_op(sim.sim_info, op)


@sims4.commands.Command('careers.find_career', command_type=(sims4.commands.CommandType.Live))
def find_career(sim: RequiredTargetParam=None, _connection=None):
    sim = sim.get_target
    if sim.queue.has_duplicate_super_affordance(Career.FIND_JOB_PHONE_INTERACTION, sim, None):
        return False
    else:
        context = interactions.context.InteractionContext(sim, (interactions.context.InteractionContext.SOURCE_SCRIPT_WITH_USER_INTENT),
          (interactions.priority.Priority.High),
          insert_strategy=(QueueInsertStrategy.NEXT))
        enqueue_result = sim.push_super_affordance(Career.FIND_JOB_PHONE_INTERACTION, sim, context)
        return enqueue_result or False
    return True


@sims4.commands.Command('careers.show_parent_tracks', command_type=(sims4.commands.CommandType.DebugOnly))
def show_parent_tracks(sim: RequiredTargetParam=None, _connection=None):
    for track in services.get_instance_manager(sims4.resources.Types.CAREER_TRACK).get_ordered_types:
        sims4.commands.output('{} -> {}'.format(str(track), str(track.parent_track)), _connection)


@sims4.commands.Command('careers.show_career_level_info')
def show_career_level_info(sim: RequiredTargetParam=None, _connection=None):
    for level in services.get_instance_manager(sims4.resources.Types.CAREER_LEVEL).get_ordered_types:
        sims4.commands.output('{}: Career {}, Track {}, Level {}, User Level {}'.format(level.__name__, level.career.__name__ if level.career is not None else 'None', level.track.__name__ if level.track is not None else 'None', level.level, level.user_level), _connection)


@sims4.commands.Command('careers.override_career_event', command_type=(sims4.commands.CommandType.Automation))
def override_career_event(career_event: TunableInstanceParam(sims4.resources.Types.CAREER_EVENT), opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        sims4.commands.output('Failed to find Sim', _connection)
    else:
        set_career_event_override(sim_info, career_event)
        sims4.commands.output('{} will run {} on the next work day'.format(sim_info, career_event), _connection)


@sims4.commands.Command('careers.offer_specific_assignment', command_type=(sims4.commands.CommandType.DebugOnly))
def offer_specific_assignment(assignment: TunableInstanceParam(sims4.resources.Types.ASPIRATION)=None, opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        sims4.commands.output('Failed to find Sim', _connection)
        return
    for career in sim_info.career_tracker.careers.values:
        if assignment in set((tuning.career_assignment for tuning in career.current_track_tuning.assignments)):
            career.clear_career_assignments
            career.offer_assignments(forced_assignment=assignment)
            return

    sims4.commands.output('Assignment invalid or could not be found for current career.', _connection)


@sims4.commands.Command('careers.offer_assignments', command_type=(sims4.commands.CommandType.DebugOnly))
def offer_assignments(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        sims4.commands.output('Failed to find Sim', _connection)
        return
    for career in sim_info.career_tracker.careers.values:
        if not career.on_assignment:
            if not career.currently_at_work:
                sims4.commands.output('{} career is not inside work hours or Sim is already on assignment.'.format(career), _connection)
                continue
            career.offer_assignments


@sims4.commands.Command('careers.show_early_warning_dialog', command_type=(sims4.commands.CommandType.DebugOnly))
def show_early_warning_dialog(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        sims4.commands.output('Failed to find Sim', _connection)
        return
    for career in sim_info.career_tracker.careers.values:
        if career.currently_at_work:
            sims4.commands.output('{} career Sim is already at work.'.format(career), _connection)
            continue
        career.early_warning_callback


@sims4.commands.Command('careers.test_career_events', command_type=(sims4.commands.CommandType.DebugOnly))
def test_career_events(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        sims4.commands.output('Failed to find Sim', _connection)
        return
    resolver = SingleSimResolver(sim_info)
    for career in sim_info.careers.values:
        for event in career.career_events:
            if career.is_career_event_on_cooldown(event):
                sims4.commands.output('{} : on cooldown'.format(event.__name__), _connection)
            else:
                result = event.tests.run_tests(resolver)
                sims4.commands.output('{} : {}'.format(event.__name__, result), _connection)


@sims4.commands.Command('careers.enable_careers', command_type=(sims4.commands.CommandType.Automation))
def enable_careers(enable: bool=None, _connection=None):
    if enable is None:
        logger.error('Not all of the data needed for the careers.enable_careers was passed.')
        return
    services.get_career_service.enabled = enable


@sims4.commands.Command('careers.register_custom_career', command_type=(sims4.commands.CommandType.Live))
def register_custom_career(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)

    def on_response(dialog):
        if not dialog.accepted:
            return
        name = dialog.text_input_responses.get(Career.TEXT_INPUT_NEW_NAME)
        description = dialog.text_input_responses.get(Career.TEXT_INPUT_NEW_DESCRIPTION)
        sim_info.career_tracker.set_custom_career_data(custom_name=name, custom_description=description)

    register_dialog_data = Career.REGISTER_CAREER_DIALOG_DATA
    dialog = register_dialog_data.register_career_dialog(sim_info, SingleSimResolver(sim_info))
    text_input_overrides = None
    if sim_info.career_tracker.has_custom_career:
        text_input_overrides = {}
        custom_career_data = sim_info.career_tracker.custom_career_data
        text_input_overrides[Career.TEXT_INPUT_NEW_NAME] = lambda *_, **__: LocalizationHelperTuning.get_raw_text(custom_career_data.get_custom_career_name)
        text_input_overrides[Career.TEXT_INPUT_NEW_DESCRIPTION] = lambda *_, **__: LocalizationHelperTuning.get_raw_text(custom_career_data.get_custom_career_description)
    dialog.show_dialog(on_response=on_response, text_input_overrides=text_input_overrides)
    return True


@sims4.commands.Command('careers.unregister_custom_career', command_type=(sims4.commands.CommandType.Live))
def unregister_custom_career(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    sim_info.career_tracker.remove_custom_career_data
    return True


@sims4.commands.Command('careers.set_avg_careers', command_type=(sims4.commands.CommandType.Automation))
def set_avg_careers(average_careers: float, _connection=None):
    sim_info_manager = services.sim_info_manager
    sim_count = len(sim_info_manager)
    adult_career_sims_infos = []
    adult_jobless_sim_infos = []
    target_careers = sim_count * average_careers
    career_count = 0
    for sim_info_id in sim_info_manager:
        sim_info = sim_info_manager.get(sim_info_id)
        if sim_info is not None and sim_info.lod != SimInfoLODLevel.MINIMUM:
            if sim_info.career_tracker.has_career:
                career_count += 1
        if sim_info.is_young_adult_or_older:
            if sim_info.is_npc:
                adult_career_sims_infos.append(sim_info)
            elif sim_info.is_young_adult_or_older:
                if sim_info.is_npc:
                    adult_jobless_sim_infos.append(sim_info)

    needed_careers = target_careers - career_count
    career_delta = 0
    if needed_careers > 0:
        random.shuffle(adult_jobless_sim_infos)
        career_service = services.get_career_service
        careers = list((career for career in career_service.get_career_list if career.career_story_progression.joining is not None))
        for sim_info in adult_jobless_sim_infos:
            random.shuffle(careers)
            for career in careers:
                if career.is_valid_career(sim_info, from_join=True):
                    sim_info.career_tracker.add_career(career(sim_info))
                    career_delta += 1
                    needed_careers -= 1
                    break

            if needed_careers <= 0:
                break

    else:
        if needed_careers < 0:
            random.shuffle(adult_career_sims_infos)
            for sim_info in adult_career_sims_infos:
                for career_uid in sim_info.career_tracker.get_quittable_careers:
                    sim_info.career_tracker.remove_career(career_uid)
                    career_delta -= 1
                    needed_careers += 1
                    if needed_careers >= 0:
                        break

                if needed_careers >= 0:
                    break

    sims4.commands.output('Number of Target Careers: {}\nNumber of Initial Careers: {}\nCareer count delta:{} '.format(target_careers, career_count, career_delta), _connection)


@sims4.commands.Command('careers.add_pto', command_type=(sims4.commands.CommandType.DebugOnly))
def add_pto(amount: int=1, opt_sim: OptionalSimInfoParam=None, _connection=None):
    if amount is None:
        sims4.commands.output('Need to specify int # of pto days to add to Sim', _connection)
        return
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        logger.error('did not get valid sim_info')
        sims4.commands.output('Failed to find Sim', _connection)
        return
    for career in sim_info.careers.values:
        career.add_pto(amount)
        career.resend_career_data
        sims4.commands.output('add_pto: {} now has {} pto days after adding {} days'.format(career, career.pto, amount), _connection)


@sims4.commands.Command('careers.add_gig', command_type=(sims4.commands.CommandType.Automation))
def add_gig(gig: TunableInstanceParam(sims4.resources.Types.CAREER_GIG), opt_sim: OptionalSimInfoParam=None, sim_filter: TunableInstanceParam(sims4.resources.Types.SIM_FILTER)=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_filter is not None:
        results = services.sim_filter_service.submit_filter(sim_filter, callback=None, allow_yielding=False)
        chosen_result = sims4.random.pop_weighted([(result.score, result) for result in results])
        customer_sim_info = chosen_result.sim_info
        gig_budget = 10000
    else:
        customer_sim_info = None
        gig_budget = None
    if sim_info is None:
        logger.error('Failed to get sim info for add_gig.')
        sims4.commands.automation_output('CareerAddGigInfo; Status:Failed, Message:Failed to get sim info for add_gig.', _connection)
        return
    if gig is None:
        logger.error('Failed. Please provide a gig')
        sims4.commands.automation_output('CareerAddGigInfo; Status:Failed, Message:Please provide a gig.', _connection)
    now = services.time_service.sim_now
    time_till_gig = gig.get_time_until_next_possible_gig(now)
    if time_till_gig is None:
        logger.error('No possible scheduled times for gig.')
        sims4.commands.automation_output('CareerAddGigInfo; Status:Failed, Message:No possible scheduled times for gig.', _connection)
        return
    gig_time = now + time_till_gig
    sim_info.career_tracker.set_gig(gig, gig_time, customer_sim_info, gig_budget)


@sims4.commands.Command('careers.list_gigs')
def list_gigs(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        logger.error('Failed to get sim info for list_gigs.')
        return
    career_tracker = sim_info.career_tracker
    if career_tracker is None:
        logger.error('Failed to find career tracker on sim {} for list_gigs.', sim_info)
        return
    for career in career_tracker:
        for gig in career.get_current_gigs:
            sims4.commands.output(f"{career}: {type(gig).__name__} (ID:{gig.guid64})", _connection)


@sims4.commands.Command('careers.cancel_all_gigs', command_type=(sims4.commands.CommandType.Live))
def cancel_all_gigs(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        logger.error('Failed to get sim info for cancel_all_gigs.')
        return
    career = sim_info.career_tracker.get_career_by_uid(career_type.guid64)
    if career is None:
        logger.error('Failed to find career {} on sim {} for cancel_all_gigs.', career_type, sim_info)
        return
    for gig in list(career.get_current_gigs):
        career.cancel_gig(gig_id=(gig.guid64))


@sims4.commands.Command('careers.cancel_current_gig', command_type=(sims4.commands.CommandType.Live))
def cancel_current_gig(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        logger.error('Failed to get sim info for cancel_current_gig.')
        return
    career = sim_info.career_tracker.get_career_by_uid(career_type.guid64)
    if career is None:
        logger.error('Failed to find career {} on sim {} for cancel_current_gig.', career_type, sim_info)
        return
    career.cancel_gig


@sims4.commands.Command('careers.cancel_gig', command_type=(sims4.commands.CommandType.Live))
def cancel_gig(gig: TunableInstanceParam(sims4.resources.Types.CAREER_GIG), opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        logger.error('Failed to get sim info for cancel_gig.')
        return
    career = sim_info.career_tracker.get_career_by_uid(gig.career.guid64)
    if career is None:
        logger.error('Failed to find a career for gig {} on sim {} for cancel_gig.', gig, sim_info)
        return
    career.cancel_gig(gig_id=(gig.guid64))


@sims4.commands.Command('careers.score_current_home_assignment_gig', command_type=(sims4.commands.CommandType.DebugOnly))
def score_current_home_assignment_gig(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        logger.error('Failed to get sim info for score_current_home_assignment_gig.')
        return
    career = sim_info.career_tracker.get_career_by_uid(career_type.guid64)
    if career is None:
        logger.error('Failed to find career {} on sim {} for score_current_home_assignment_gig.', career_type, sim_info)
        return
    career.score_work_at_home_gig_early


def _get_gig_for_command(sim_info, career_type, _connection):
    sim_info = get_optional_target(sim_info, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        logger.error('Failed to get sim info for a career gig command.')
        return
    career = sim_info.career_tracker.get_career_by_uid(career_type.guid64)
    if career is None:
        logger.error('Failed to find career {} on sim {} for a career gig command.', career_type, sim_info)
        return
    gig = career.get_current_gig
    if gig is None:
        logger.error('Failed to find a gig on career {} on sim {} for a career gig command.', career_type, sim_info)
        return
    return gig


@sims4.commands.Command('careers.reveal_gig_client_preference', command_type=(sims4.commands.CommandType.Live))
def reveal_gig_client_preference(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), count: int=1, opt_sim: OptionalSimInfoParam=None, _connection=None):
    gig = _get_gig_for_command(opt_sim, career_type, _connection)
    if gig is None:
        return
    if not hasattr(gig, 'reveal_client_preference'):
        logger.error("Gig {} doesn't have client preferences to reveal on career {} on sim {} for reveal_gig_client_preference.", gig, career_type, sim_info)
        return
    gig.reveal_client_preference(count)


@sims4.commands.Command('careers.replace_gig_preference_category', command_type=(sims4.commands.CommandType.Live))
def replace_gig_preference_category(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), preference_category: TunableInstanceParam(sims4.resources.Types.CAS_PREFERENCE_CATEGORY), opt_sim: OptionalSimInfoParam=None, _connection=None):
    gig = _get_gig_for_command(opt_sim, career_type, _connection)
    if gig is None:
        return
    gig.replace_client_preference_by_category(preference_category)


@sims4.commands.Command('careers.replace_gig_preference')
def replace_gig_preference(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), old_preference: TunableInstanceParam(sims4.resources.Types.TRAIT), new_preference: TunableInstanceParam(sims4.resources.Types.TRAIT), opt_sim: OptionalSimInfoParam=None, _connection=None):
    gig = _get_gig_for_command(opt_sim, career_type, _connection)
    if gig is None:
        return
    gig.replace_client_preference(old_preference, new_preference)


@sims4.commands.Command('careers.show_gig_objects', command_type=(sims4.commands.CommandType.DebugOnly))
def show_gig_objects(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), opt_sim: OptionalSimInfoParam=None, _connection=None):
    gig = _get_gig_for_command(opt_sim, career_type, _connection)
    if gig is None:
        return
    customer_lot_id = gig.get_customer_lot_id
    if not customer_lot_id:
        logger.error('Failed to find a customer lot id on career {} on sim {} for show_gig_objects.', career_type, sim_info)
        return
    gig_objects = build_buy.get_gig_objects_added(customer_lot_id)
    manager = services.object_manager
    for gig_object_id in gig_objects:
        gig_object = manager.get(gig_object_id)
        sims4.commands.output("Gig Object: '{}' ".format(gig_object), _connection)


@sims4.commands.Command('careers.resend_data')
def resend_data(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        logger.error('Failed to get sim info for resend_data.')
        return
    career_tracker = sim_info.career_tracker
    if career_tracker is None:
        logger.error('Failed to find career tracker on sim {} for resend_data.', sim_info)
        return
    career_tracker.resend_career_data


@sims4.commands.Command('careers.show_reveal_sequence', command_type=(sims4.commands.CommandType.Live))
def show_reveal_sequence(opt_sim: OptionalSimInfoParam=None, active_gig: bool=True, _connection=None):
    sim_info = get_optional_target(opt_sim, _connection, target_type=OptionalSimInfoParam)
    if sim_info is None:
        sims4.commands.output('Failed to find SimInfo.', _connection)
        return False
    dialog = Career.REVEAL_SEQUENCE_DIALOG(sim_info, resolver=(SingleSimResolver(sim_info)), active_gig=active_gig)
    dialog.show_dialog(owner=sim_info)
    return True


@sims4.commands.Command('careers.delete_active_gig_photos', command_type=(sims4.commands.CommandType.Live))
def delete_active_gig_photos(opt_sim: OptionalSimInfoParam=None, active_gig: bool=True, career_type: TunableInstanceParam(sims4.resources.Types.CAREER)=None, _connection=None):
    sim_info = get_optional_target(opt_sim, _connection, target_type=OptionalSimInfoParam)
    if sim_info is None:
        sims4.commands.output('Failed to find SimInfo.', _connection)
        return False
    career = sim_info.career_tracker.get_career_by_uid(career_type.guid64)
    if career is None:
        sims4.commands.output('Sim is not in the interior decorator career.', _connection)
        return False
    sim_info.career_tracker.update_photo_difference(career, active_gig)
    return True


@sims4.commands.Command('careers.clear_deletion_from_gig_history', command_type=(sims4.commands.CommandType.Live))
def clear_deletion_from_gig_history(opt_sim: OptionalSimInfoParam=None, active_gig: bool=True, career_type: TunableInstanceParam(sims4.resources.Types.CAREER)=None, _connection=None):
    sim_info = get_optional_target(opt_sim, _connection, target_type=OptionalSimInfoParam)
    if sim_info is None:
        sims4.commands.output('Failed to find SimInfo.', _connection)
        return False
    career = sim_info.career_tracker.get_career_by_uid(career_type.guid64)
    if career is None:
        sims4.commands.output('Sim is not in the specified career.', _connection)
        return False
    sim_info.career_tracker.clear_deletion_cache_from_gig_history(career, active_gig)
    return True


@sims4.commands.Command('careers.clear_selected_photos_from_gig_history', command_type=(sims4.commands.CommandType.Live))
def clear_selected_photos_from_gig_history(opt_sim: OptionalSimInfoParam=None, active_gig: bool=True, career_type: TunableInstanceParam(sims4.resources.Types.CAREER)=None, _connection=None):
    sim_info = get_optional_target(opt_sim, _connection, target_type=OptionalSimInfoParam)
    if sim_info is None:
        sims4.commands.output('Failed to find SimInfo.', _connection)
        return False
    career = sim_info.career_tracker.get_career_by_uid(career_type.guid64)
    if career is None:
        sims4.commands.output('Sim is not in the specified career.', _connection)
        return False
    sim_info.career_tracker.clear_selected_photos_from_gig_history(career, active_gig)
    return True


@sims4.commands.Command('careers.calculate_individual_customer_gig_scoring', command_type=(sims4.commands.CommandType.Live))
def calculate_individual_customer_gig_scoring(career_type: TunableInstanceParam(sims4.resources.Types.CAREER), likes_value: int=1, dislikes_value: int=1, opt_sim: OptionalSimInfoParam=None, _connection=None):
    gig = _get_gig_for_command(opt_sim, career_type, _connection)
    if gig is None:
        return False
    gig.calculate_gig_score_for_client_household(likes_value, dislikes_value)
    return True