# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\situation_commands.py
# Compiled at: 2022-08-26 18:13:12
# Size of source mod 2**32: 84069 bytes
import build_buy, collections, date_and_time, mtx, objects, services, sims4.commands, sims4.log, situations, tag
from contextlib import contextmanager
from date_and_time import DateAndTime
from distributor import shared_messages
from distributor.rollback import ProtocolBufferRollback
from distributor.shared_messages import IconInfoData
from drama_scheduler.drama_node_types import DramaNodeType
from event_testing.resolver import SingleSimResolver
from event_testing.results import TestResult
from protocolbuffers import Consts_pb2, Situations_pb2, Lot_pb2, Localization_pb2
from protocolbuffers.ResourceKey_pb2 import ResourceKey
from server_commands.argument_helpers import get_optional_target, TunableInstanceParam, get_tunable_instance, OptionalSimInfoParam
from sims.self_interactions import TravelInteraction
from situations.base_situation import BaseSituation
from situations.situation_excursion import ExcursionSituation
from situations.situation_guest_list import SituationGuestList, SituationGuestInfo, SituationInvitationPurpose
from situations.situation_types import SituationCreationUIOption, SituationCallbackOption, SituationMedal, SituationUserFacingType, SituationCategoryUid
from world.region import Region
logger = sims4.log.Logger('Situations')
allow_debug_situations_in_ui = False

def should_display_situation(situation_instance, sim, target_sim_id, situation_category, from_situation_subset):
    global allow_debug_situations_in_ui
    tuned_to_show = situation_instance.creation_ui_option == SituationCreationUIOption.AVAILABLE or situation_instance.creation_ui_option == SituationCreationUIOption.DEBUG_AVAILABLE and allow_debug_situations_in_ui or from_situation_subset and situation_instance.creation_ui_option == SituationCreationUIOption.SPECIFIED_ONLY
    if situation_category == SituationCategoryUid.WEDDING:
        if situation_instance.category != SituationCategoryUid.WEDDING:
            return (
             TestResult(False), 0)
    elif situation_instance.category == SituationCategoryUid.WEDDING:
        return (
         TestResult(False), 0)
    result = situation_instance.is_situation_available(sim, target_sim_id)
    if tuned_to_show:
        mtx_id = 0
        if situation_instance.entitlement:
            if mtx.has_entitlement(situation_instance.entitlement):
                mtx_id = situation_instance.entitlement
            else:
                return (
                 TestResult(False), 0)
        return (
         result, mtx_id)
    return (TestResult(False), 0)


SITUATION_ID_BATCH_REPEATED_FIELDS = ('situation_resource_id', 'situation_name', 'category_id',
                                      'mtx_id', 'highest_medal_earned', 'tooltip',
                                      'allow_user_facing_goals', 'medal_icon_override',
                                      'scoring_lock_reason', 'new_entry')

class SituationIdEntry:
    __slots__ = SITUATION_ID_BATCH_REPEATED_FIELDS

    def __init__(self):
        for field in SITUATION_ID_BATCH_REPEATED_FIELDS:
            setattr(self, field, None)

    def append_to_message(self, msg):
        num_populated_fields = 0
        try:
            for field in SITUATION_ID_BATCH_REPEATED_FIELDS:
                value = getattr(self, field)
                repeated_field = getattr(msg, field)
                repeated_field.append(value)
                num_populated_fields += 1

        except:
            logger.exception('Exception while filling out a SituationIDBatch message')
            for i in range(num_populated_fields):
                field = SITUATION_ID_BATCH_REPEATED_FIELDS[i]
                repeated_field = getattr(msg, field)
                del repeated_field[-1]

    @classmethod
    @contextmanager
    def get_entry_with_rollback(cls, msg):
        entry = cls()
        try:
            yield entry
            entry.append_to_message(msg)
        except:
            logger.exception('Exception populating get_situation_ids')


@sims4.commands.Command('situations.set_situation_as_viewed', command_type=(sims4.commands.CommandType.Live))
def set_situation_as_viewed(sim_id: OptionalSimInfoParam, situation_id: int, _connection=None):
    sim = get_optional_target(sim_id, _connection, target_type=OptionalSimInfoParam)
    if sim is None:
        sims4.commands.output('Sim id {} is invalid.'.format(sim_id), _connection)
        return
    sim.household.set_is_situation_new_entry(situation_id, False)


@sims4.commands.Command('situations.get_situation_ids', command_type=(sims4.commands.CommandType.Live))
def get_situation_ids(session_id=0, sim_id=None, opt_target_id=None, situation_category=SituationCategoryUid.DEFAULT, *situation_ids, _connection=None):
    sim = get_optional_target(sim_id, _connection, target_type=OptionalSimInfoParam)
    if opt_target_id is None or opt_target_id == 0:
        target_sim_id = 0
    else:
        target_sim_id = opt_target_id
    household = sim.household
    instance_manager = services.get_instance_manager(sims4.resources.Types.SITUATION)
    situation_batch_msg = Situations_pb2.SituationIDBatch()
    situation_batch_msg.situation_session_id = session_id
    situation_batch_msg.scoring_enabled = household.situation_scoring_enabled
    valid_situations = []
    for situation_id in situation_ids:
        instance = instance_manager.get(situation_id)
        result, mtx_id = should_display_situation(instance, sim, target_sim_id, situation_category, True)
        if result or result.tooltip is not None:
            valid_situations.append((instance, mtx_id, result.tooltip))

    if not valid_situations:
        for instance in instance_manager.types.values():
            if instance.guid64 in situation_ids:
                continue
            result, mtx_id = should_display_situation(instance, sim, target_sim_id, situation_category, False)
            if result or result.tooltip is not None:
                valid_situations.append((instance, mtx_id, result.tooltip))

    for instance, mtx_id, tooltip in valid_situations:
        situation_id = instance.guid64
        with SituationIdEntry.get_entry_with_rollback(situation_batch_msg) as (entry):
            entry.situation_resource_id = situation_id
            entry.situation_name = instance._display_name
            entry.category_id = instance.category
            entry.mtx_id = mtx_id
            entry.highest_medal_earned = household.get_highest_medal_for_situation(situation_id)
            entry.new_entry = household.get_is_situation_new_entry(situation_id)
            resource_key = ResourceKey()
            icon = instance.medal_icon_override
            if icon is None:
                resource_key.type, resource_key.group, resource_key.instance = (0,
                                                                                0,
                                                                                0)
            else:
                resource_key.type, resource_key.group, resource_key.instance = icon.type, icon.group, icon.instance
            entry.medal_icon_override = resource_key
            if instance.scoring_lock_reason is None:
                entry.scoring_lock_reason = Localization_pb2.LocalizedString()
                entry.scoring_lock_reason.hash = 0
            else:
                entry.scoring_lock_reason = instance.scoring_lock_reason
            if tooltip is not None:
                entry.tooltip = tooltip()
            else:
                entry.tooltip = Localization_pb2.LocalizedString()
                entry.tooltip.hash = 0
            entry.allow_user_facing_goals = instance.allow_user_facing_goals

    shared_messages.add_message_if_selectable(sim, Consts_pb2.MSG_SITUATION_ID_BATCH, situation_batch_msg, True)


@sims4.commands.Command('situations.get_situation_data', command_type=(sims4.commands.CommandType.Live))
def get_situation_data(session_id: int=0, sim_id: OptionalSimInfoParam=None, *situation_ids, _connection=None):
    sim = get_optional_target(sim_id, _connection, target_type=OptionalSimInfoParam)
    instance_manager = services.get_instance_manager(sims4.resources.Types.SITUATION)
    situation_batch_msg = Situations_pb2.SituationDataBatch()
    situation_batch_msg.situation_session_id = session_id
    for situation_id in situation_ids:
        with ProtocolBufferRollback(situation_batch_msg.situations) as (situation_data):
            instance = instance_manager.get(situation_id)
            if instance is not None:
                shared_messages.build_icon_info_msg(IconInfoData(icon_resource=(instance._icon)), instance._display_name, situation_data.icon_info)
                situation_data.icon_info.desc = instance.situation_description
                situation_data.cost = instance._cost
                situation_data.max_participants = instance.max_participants
                if instance.activity_selection:
                    situation_data.available_activity_ids.extend([a.guid64 for a in instance.activity_selection.available_activities])
                    if instance.activity_selection.required_activities:
                        situation_data.required_activity_ids.extend([a.guid64 for a in instance.activity_selection.required_activities])
                if instance.customizable_style:
                    snippet_manager = services.get_instance_manager(sims4.resources.Types.SNIPPET)
                    style_data = snippet_manager.get(instance.customizable_style.guid64)
                    if style_data.customizable_guest_attire:
                        for color_tag, color_data_tuple in style_data.customizable_guest_attire.color_map.items():
                            with ProtocolBufferRollback(situation_data.style_data.guest_attire_colors) as (attire_color):
                                attire_color.color_tag = color_tag
                                attire_color.color_name = color_data_tuple.color_name
                                attire_color.color_value = color_data_tuple.color_value

                        for style_tag, style_name in style_data.customizable_guest_attire.style_map.items():
                            with ProtocolBufferRollback(situation_data.style_data.guest_attire_styles) as (attire_style):
                                attire_style.style_tag = style_tag
                                attire_style.style_name = style_name

                    if style_data.cas_edit_job:
                        situation_data.style_data.cas_edit_job_id = style_data.cas_edit_job.job.guid64
                        situation_data.style_data.cas_edit_outfit_category = style_data.cas_edit_job.outfit_category
                        resource_key = ResourceKey()
                        icon = style_data.cas_edit_job.no_sim_selected_icon
                        resource_key.type = icon.type
                        resource_key.group = icon.group
                        resource_key.instance = icon.instance
                        situation_data.style_data.cas_edit_no_sim_icon = resource_key
                if instance.display_special_object:
                    situation_data.style_data.special_object_help_tooltip = instance.display_special_object.help_tooltip
                    situation_data.style_data.no_special_object_label = instance.display_special_object.no_object_label
                    resource_key = ResourceKey()
                    icon = instance.display_special_object.no_object_icon
                    resource_key.type = icon.type
                    resource_key.group = icon.group
                    resource_key.instance = icon.instance
                    situation_data.style_data.no_special_object_icon = resource_key
                for medal in SituationMedal:
                    with ProtocolBufferRollback(situation_data.rewards) as (reward_msg):
                        level = instance.get_level_data(medal)
                        reward_msg.level = int(medal)
                        if level is not None:
                            if level.reward is not None:
                                if level.reward.reward_description is not None:
                                    reward_msg.display_name.extend([level.reward.reward_description])

                jobs = list(instance.get_tuned_jobs())
                jobs.sort(key=(lambda job: job.guid64))
                if instance.job_display_ordering is not None:
                    for ordered_job in reversed(instance.job_display_ordering):
                        if ordered_job in jobs:
                            jobs.remove(ordered_job)
                            jobs.insert(0, ordered_job)

                for job in jobs:
                    if job.sim_count.upper_bound > 0:
                        with ProtocolBufferRollback(situation_data.jobs) as (job_msg):
                            job_msg.job_resource_id = job.guid64
                            shared_messages.build_icon_info_msg(IconInfoData(icon_resource=(job.icon)), job.display_name, job_msg.icon_info)
                            job_msg.icon_info.desc = job.job_description
                            job_msg.is_hireable = job.can_be_hired
                            job_msg.min_required = job.sim_count.lower_bound
                            job_msg.max_allowed = job.sim_count.upper_bound
                            job_msg.hire_cost = job.hire_cost
                            if job.help_tooltip is not None:
                                job_msg.help_tooltip = job.help_tooltip

    shared_messages.add_message_if_selectable(sim, Consts_pb2.MSG_SITUATION_DATA_BATCH, situation_batch_msg, True)


@sims4.commands.Command('situations.get_prepopulated_job_for_sims', command_type=(sims4.commands.CommandType.Live))
def get_prepopulated_job_for_sims(session_id: int, situation_type: TunableInstanceParam(sims4.resources.Types.SITUATION), sim_id: OptionalSimInfoParam=None, opt_target_id: int=None, _connection=None):
    sim = get_optional_target(sim_id, _connection, target_type=OptionalSimInfoParam)
    prepopulate = situation_type.get_prepopulated_job_for_sims(sim, opt_target_id)
    assign_msg = Situations_pb2.SituationAssignJob()
    assign_msg.situation_session_id = session_id
    if prepopulate is not None:
        for sim_id, job_type_id in prepopulate:
            assign_msg.sim_ids.append(sim_id)
            assign_msg.job_resource_ids.append(job_type_id)

    shared_messages.add_object_message(sim, Consts_pb2.MSG_SITUATION_ASSIGN_JOB, assign_msg, True)


JobCallbackData = collections.namedtuple('JobCallbackData', ['session_id', 'sim_id', 'job_id', 'job_requirements'])

@sims4.commands.Command('situations.get_sims_for_job', command_type=(sims4.commands.CommandType.Live))
def get_sims_for_job--- This code section failed: ---

 L. 348         0  LOAD_GLOBAL              get_optional_target
                2  LOAD_FAST                'sim_id'
                4  LOAD_FAST                '_connection'
                6  LOAD_GLOBAL              OptionalSimInfoParam
                8  LOAD_CONST               ('target_type',)
               10  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
               12  STORE_FAST               'sim'

 L. 351        14  LOAD_GLOBAL              services
               16  LOAD_METHOD              time_service
               18  CALL_METHOD_0         0  '0 positional arguments'
               20  LOAD_ATTR                sim_now
               22  STORE_FAST               'situation_start_time'

 L. 352        24  LOAD_FAST                'situation_type'
               26  LOAD_ATTR                duration
               28  STORE_FAST               'duration'

 L. 353        30  LOAD_FAST                'duration'
               32  LOAD_CONST               0
               34  COMPARE_OP               >
               36  POP_JUMP_IF_FALSE    58  'to 58'

 L. 354        38  LOAD_FAST                'situation_start_time'
               40  LOAD_GLOBAL              date_and_time
               42  LOAD_METHOD              create_time_span
               44  LOAD_CONST               0
               46  LOAD_CONST               0
               48  LOAD_FAST                'duration'
               50  CALL_METHOD_3         3  '3 positional arguments'
               52  BINARY_ADD       
               54  STORE_FAST               'situation_end_time'
               56  JUMP_FORWARD         70  'to 70'
             58_0  COME_FROM            36  '36'

 L. 356        58  LOAD_GLOBAL              date_and_time
               60  LOAD_ATTR                INVALID_DATE_AND_TIME
               62  STORE_FAST               'situation_start_time'

 L. 357        64  LOAD_GLOBAL              date_and_time
               66  LOAD_ATTR                INVALID_DATE_AND_TIME
               68  STORE_FAST               'situation_end_time'
             70_0  COME_FROM            56  '56'

 L. 360        70  LOAD_CLOSURE             'job_type'
               72  BUILD_TUPLE_1         1 
               74  LOAD_CODE                <code_object get_sim_filter_gsi_name>
               76  LOAD_STR                 'get_sims_for_job.<locals>.get_sim_filter_gsi_name'
               78  MAKE_FUNCTION_8          'closure'
               80  STORE_FAST               'get_sim_filter_gsi_name'

 L. 363        82  LOAD_GLOBAL              services
               84  LOAD_METHOD              sim_filter_service
               86  CALL_METHOD_0         0  '0 positional arguments'
               88  LOAD_ATTR                submit_filter
               90  LOAD_DEREF               'job_type'
               92  LOAD_ATTR                filter

 L. 364        94  LOAD_CONST               None

 L. 365        96  LOAD_FAST                'sim'
               98  LOAD_ATTR                sim_info

 L. 366       100  LOAD_FAST                'situation_start_time'

 L. 367       102  LOAD_FAST                'situation_end_time'

 L. 368       104  LOAD_CONST               False

 L. 369       106  LOAD_FAST                'get_sim_filter_gsi_name'
              108  LOAD_CONST               ('requesting_sim_info', 'start_time', 'end_time', 'allow_yielding', 'gsi_source_fn')
              110  CALL_FUNCTION_KW_7     7  '7 total positional and keyword args'
              112  STORE_FAST               'results'

 L. 374       114  LOAD_DEREF               'job_type'
              116  LOAD_ATTR                additional_filter_for_user_selection
              118  POP_JUMP_IF_TRUE    128  'to 128'
              120  LOAD_DEREF               'job_type'
              122  LOAD_ATTR                additional_filter_list_for_user_selection
          124_126  POP_JUMP_IF_FALSE   406  'to 406'
            128_0  COME_FROM           118  '118'

 L. 375       128  BUILD_MAP_0           0 
              130  STORE_FAST               'conflicting_career_track_ids'

 L. 376       132  LOAD_GLOBAL              set
              134  CALL_FUNCTION_0       0  '0 positional arguments'
              136  STORE_FAST               'sim_constraints'

 L. 377       138  SETUP_LOOP          180  'to 180'
              140  LOAD_FAST                'results'
              142  GET_ITER         
              144  FOR_ITER            178  'to 178'
              146  STORE_FAST               'result'

 L. 378       148  LOAD_FAST                'sim_constraints'
              150  LOAD_METHOD              add
              152  LOAD_FAST                'result'
              154  LOAD_ATTR                sim_info
              156  LOAD_ATTR                id
              158  CALL_METHOD_1         1  '1 positional argument'
              160  POP_TOP          

 L. 379       162  LOAD_FAST                'result'
              164  LOAD_ATTR                conflicting_career_track_id
              166  LOAD_FAST                'conflicting_career_track_ids'
              168  LOAD_FAST                'result'
              170  LOAD_ATTR                sim_info
              172  LOAD_ATTR                id
              174  STORE_SUBSCR     
              176  JUMP_BACK           144  'to 144'
              178  POP_BLOCK        
            180_0  COME_FROM_LOOP      138  '138'

 L. 380       180  BUILD_LIST_0          0 
              182  STORE_FAST               'results'

 L. 381       184  LOAD_DEREF               'job_type'
              186  LOAD_ATTR                additional_filter_for_user_selection
          188_190  POP_JUMP_IF_FALSE   260  'to 260'

 L. 383       192  LOAD_GLOBAL              services
              194  LOAD_METHOD              sim_filter_service
              196  CALL_METHOD_0         0  '0 positional arguments'
              198  LOAD_ATTR                submit_filter
              200  LOAD_DEREF               'job_type'
              202  LOAD_ATTR                additional_filter_for_user_selection

 L. 384       204  LOAD_CONST               None

 L. 385       206  LOAD_FAST                'sim'
              208  LOAD_ATTR                sim_info

 L. 386       210  LOAD_FAST                'situation_start_time'

 L. 387       212  LOAD_FAST                'situation_end_time'

 L. 388       214  LOAD_FAST                'sim_constraints'

 L. 389       216  LOAD_CONST               False

 L. 390       218  LOAD_FAST                'get_sim_filter_gsi_name'
              220  LOAD_CONST               ('requesting_sim_info', 'start_time', 'end_time', 'sim_constraints', 'allow_yielding', 'gsi_source_fn')
              222  CALL_FUNCTION_KW_8     8  '8 total positional and keyword args'
              224  STORE_FAST               'or_results'

 L. 391       226  LOAD_FAST                'or_results'
              228  STORE_FAST               'results'

 L. 393       230  LOAD_FAST                'or_results'
          232_234  POP_JUMP_IF_FALSE   260  'to 260'

 L. 394       236  LOAD_SETCOMP             '<code_object <setcomp>>'
              238  LOAD_STR                 'get_sims_for_job.<locals>.<setcomp>'
              240  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              242  LOAD_FAST                'or_results'
              244  GET_ITER         
              246  CALL_FUNCTION_1       1  '1 positional argument'
              248  STORE_FAST               'used_ids'

 L. 395       250  LOAD_FAST                'sim_constraints'
              252  LOAD_METHOD              difference
              254  LOAD_FAST                'used_ids'
              256  CALL_METHOD_1         1  '1 positional argument'
              258  STORE_FAST               'sim_constraints'
            260_0  COME_FROM           232  '232'
            260_1  COME_FROM           188  '188'

 L. 397       260  LOAD_FAST                'sim_constraints'
          262_264  POP_JUMP_IF_FALSE   364  'to 364'

 L. 398       266  SETUP_LOOP          364  'to 364'
              268  LOAD_DEREF               'job_type'
              270  LOAD_ATTR                additional_filter_list_for_user_selection
              272  GET_ITER         
            274_0  COME_FROM           352  '352'
            274_1  COME_FROM           322  '322'
              274  FOR_ITER            362  'to 362'
              276  STORE_FAST               'additional_filter'

 L. 399       278  LOAD_GLOBAL              services
              280  LOAD_METHOD              sim_filter_service
              282  CALL_METHOD_0         0  '0 positional arguments'
              284  LOAD_ATTR                submit_filter
              286  LOAD_FAST                'additional_filter'

 L. 400       288  LOAD_CONST               None

 L. 401       290  LOAD_FAST                'sim'
              292  LOAD_ATTR                sim_info

 L. 402       294  LOAD_FAST                'situation_start_time'

 L. 403       296  LOAD_FAST                'situation_end_time'

 L. 404       298  LOAD_FAST                'sim_constraints'

 L. 405       300  LOAD_CONST               False

 L. 406       302  LOAD_FAST                'get_sim_filter_gsi_name'
              304  LOAD_CONST               ('requesting_sim_info', 'start_time', 'end_time', 'sim_constraints', 'allow_yielding', 'gsi_source_fn')
              306  CALL_FUNCTION_KW_8     8  '8 total positional and keyword args'
              308  STORE_FAST               'or_results'

 L. 407       310  LOAD_FAST                'results'
              312  LOAD_METHOD              extend
              314  LOAD_FAST                'or_results'
              316  CALL_METHOD_1         1  '1 positional argument'
              318  POP_TOP          

 L. 409       320  LOAD_FAST                'or_results'
          322_324  POP_JUMP_IF_FALSE   274  'to 274'

 L. 410       326  LOAD_SETCOMP             '<code_object <setcomp>>'
              328  LOAD_STR                 'get_sims_for_job.<locals>.<setcomp>'
              330  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              332  LOAD_FAST                'or_results'
              334  GET_ITER         
              336  CALL_FUNCTION_1       1  '1 positional argument'
              338  STORE_FAST               'used_ids'

 L. 411       340  LOAD_FAST                'sim_constraints'
              342  LOAD_METHOD              difference
              344  LOAD_FAST                'used_ids'
              346  CALL_METHOD_1         1  '1 positional argument'
              348  STORE_FAST               'sim_constraints'

 L. 412       350  LOAD_FAST                'sim_constraints'
          352_354  POP_JUMP_IF_TRUE    274  'to 274'

 L. 413       356  BREAK_LOOP       
          358_360  JUMP_BACK           274  'to 274'
              362  POP_BLOCK        
            364_0  COME_FROM_LOOP      266  '266'
            364_1  COME_FROM           262  '262'

 L. 416       364  SETUP_LOOP          406  'to 406'
              366  LOAD_FAST                'results'
              368  GET_ITER         
            370_0  COME_FROM           382  '382'
              370  FOR_ITER            404  'to 404'
              372  STORE_FAST               'result'

 L. 417       374  LOAD_FAST                'result'
              376  LOAD_ATTR                conflicting_career_track_id
              378  LOAD_CONST               None
              380  COMPARE_OP               is
          382_384  POP_JUMP_IF_FALSE   370  'to 370'

 L. 418       386  LOAD_FAST                'conflicting_career_track_ids'
              388  LOAD_FAST                'result'
              390  LOAD_ATTR                sim_info
              392  LOAD_ATTR                id
              394  BINARY_SUBSCR    
              396  LOAD_FAST                'result'
              398  STORE_ATTR               conflicting_career_track_id
          400_402  JUMP_BACK           370  'to 370'
              404  POP_BLOCK        
            406_0  COME_FROM_LOOP      364  '364'
            406_1  COME_FROM           124  '124'

 L. 421       406  LOAD_GLOBAL              Situations_pb2
              408  LOAD_METHOD              SituationJobSims
              410  CALL_METHOD_0         0  '0 positional arguments'
              412  STORE_FAST               'msg'

 L. 422       414  LOAD_FAST                'session_id'
              416  LOAD_FAST                'msg'
              418  STORE_ATTR               situation_session_id

 L. 423       420  LOAD_DEREF               'job_type'
              422  LOAD_ATTR                guid
              424  LOAD_FAST                'msg'
              426  STORE_ATTR               job_resource_id

 L. 424       428  LOAD_DEREF               'job_type'
              430  LOAD_ATTR                requirement_text
              432  LOAD_FAST                'msg'
              434  STORE_ATTR               requirements

 L. 427       436  LOAD_FAST                'results'
              438  LOAD_ATTR                sort
              440  LOAD_LAMBDA              '<code_object <lambda>>'
              442  LOAD_STR                 'get_sims_for_job.<locals>.<lambda>'
              444  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              446  LOAD_CONST               ('key',)
              448  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              450  POP_TOP          

 L. 429       452  SETUP_LOOP          562  'to 562'
              454  LOAD_FAST                'results'
              456  GET_ITER         
              458  FOR_ITER            560  'to 560'
              460  STORE_FAST               'result'

 L. 432       462  LOAD_FAST                'msg'
              464  LOAD_ATTR                sim_ids
              466  LOAD_METHOD              append
              468  LOAD_FAST                'result'
              470  LOAD_ATTR                sim_info
              472  LOAD_ATTR                id
              474  CALL_METHOD_1         1  '1 positional argument'
              476  POP_TOP          

 L. 434       478  LOAD_GLOBAL              ProtocolBufferRollback
              480  LOAD_FAST                'msg'
              482  LOAD_ATTR                sims
              484  CALL_FUNCTION_1       1  '1 positional argument'
              486  SETUP_WITH          550  'to 550'
              488  STORE_FAST               'situation_job_sim'

 L. 435       490  LOAD_FAST                'result'
              492  LOAD_ATTR                sim_info
              494  LOAD_ATTR                id
              496  LOAD_FAST                'situation_job_sim'
              498  STORE_ATTR               sim_id

 L. 436       500  LOAD_FAST                'result'
              502  LOAD_ATTR                sim_info
              504  LOAD_ATTR                household
              506  LOAD_ATTR                id
              508  LOAD_GLOBAL              services
              510  LOAD_METHOD              active_household_id
              512  CALL_METHOD_0         0  '0 positional arguments'
              514  COMPARE_OP               ==
          516_518  POP_JUMP_IF_FALSE   530  'to 530'

 L. 438       520  LOAD_FAST                'result'
              522  LOAD_ATTR                sim_info
              524  LOAD_ATTR                account_id
              526  LOAD_FAST                'situation_job_sim'
              528  STORE_ATTR               account_id
            530_0  COME_FROM           516  '516'

 L. 439       530  LOAD_FAST                'result'
              532  LOAD_ATTR                conflicting_career_track_id
          534_536  POP_JUMP_IF_FALSE   546  'to 546'

 L. 440       538  LOAD_FAST                'result'
              540  LOAD_ATTR                conflicting_career_track_id
              542  LOAD_FAST                'situation_job_sim'
              544  STORE_ATTR               career_track_id
            546_0  COME_FROM           534  '534'
              546  POP_BLOCK        
              548  LOAD_CONST               None
            550_0  COME_FROM_WITH      486  '486'
              550  WITH_CLEANUP_START
              552  WITH_CLEANUP_FINISH
              554  END_FINALLY      
          556_558  JUMP_BACK           458  'to 458'
              560  POP_BLOCK        
            562_0  COME_FROM_LOOP      452  '452'

 L. 442       562  LOAD_GLOBAL              shared_messages
              564  LOAD_METHOD              add_message_if_selectable
              566  LOAD_GLOBAL              services
              568  LOAD_METHOD              object_manager
              570  CALL_METHOD_0         0  '0 positional arguments'
              572  LOAD_METHOD              get
              574  LOAD_FAST                'sim'
              576  LOAD_ATTR                id
              578  CALL_METHOD_1         1  '1 positional argument'
              580  LOAD_GLOBAL              Consts_pb2
              582  LOAD_ATTR                MSG_SITUATION_JOB_SIMS
              584  LOAD_FAST                'msg'
              586  LOAD_CONST               True
              588  CALL_METHOD_4         4  '4 positional arguments'
              590  POP_TOP          

Parse error at or near `COME_FROM_LOOP' instruction at offset 364_0


@sims4.commands.Command('situations.get_valid_situation_locations', command_type=(sims4.commands.CommandType.Live))
def get_valid_situation_locations(sim_id: OptionalSimInfoParam, situation_type: TunableInstanceParam(sims4.resources.Types.SITUATION), *guests, _connection=None):
    sim = get_optional_target(sim_id, _connection, target_type=OptionalSimInfoParam)
    if not sim:
        sims4.commands.output('Invalid Sim ID: {}'.format(sim_id), _connection)
        return
    sim_info = sim.sim_info
    current_region = services.current_region()
    possible_zones = situation_type.get_possible_zone_ids_for_situation(host_sim_info=sim_info, guest_ids=guests)
    venue_manager = services.get_instance_manager(sims4.resources.Types.VENUE)
    persistence_service = services.get_persistence_service()
    locations_msg = Situations_pb2.SituationLocations()
    for zone_id in possible_zones:
        zone_data = persistence_service.get_zone_proto_buff(zone_id)
        if zone_data is None:
            continue
        neighborhood_data = persistence_service.get_neighborhood_proto_buff(zone_data.neighborhood_id)
        if neighborhood_data is None:
            continue
        region_description_id = neighborhood_data.region_id
        region_instance = Region.REGION_DESCRIPTION_TUNING_MAP.get(region_description_id)
        if not current_region.is_region_compatible(region_instance):
            continue
        lot_data = None
        for lot_owner_data in neighborhood_data.lots:
            if zone_id == lot_owner_data.zone_instance_id:
                lot_data = lot_owner_data
                break

        if zone_data is not None:
            if lot_data is not None:
                location_data = Lot_pb2.LotInfoItem()
                location_data.zone_id = zone_data.zone_id
                location_data.name = zone_data.name
                location_data.world_id = zone_data.world_id
                location_data.lot_template_id = zone_data.lot_template_id
                location_data.lot_description_id = zone_data.lot_description_id
                venue_tuning_id = build_buy.get_current_venue(zone_id)
                venue_tuning = venue_manager.get(venue_tuning_id)
                send_lot_owner = True
                if venue_tuning is not None:
                    location_data.venue_type_name = venue_tuning.display_name
                    send_lot_owner = venue_tuning.is_residential or venue_tuning.is_university_housing
            if lot_data.lot_owner:
                if send_lot_owner:
                    household_id = lot_data.lot_owner[0].household_id
                    household = services.household_manager().get(household_id)
                    if household is not None:
                        location_data.household_name = household.name
            locations_msg.situation_locations.append(location_data)

    shared_messages.add_object_message_for_sim_id(sim.id, Consts_pb2.MSG_SITUATION_LOCATIONS, locations_msg)


@sims4.commands.Command('situations.set_special_object')
def set_situation_special_object(situation_type_id, object_id, opt_sim=None, add_to_host_hidden_inventory=False, _connection=None):
    drama_scheduler = services.drama_scheduler_service()
    sim = get_optional_target(opt_sim, _connection, target_type=OptionalSimInfoParam)
    special_object = services.current_zone().find_object(object_id)
    if not special_object:
        sims4.commands.output("Couldn't find the specified object id {}. Object must be instanced.".format(object_id), _connection)
        return
    for drama_node in drama_scheduler.get_scheduled_nodes_by_drama_node_type(DramaNodeType.PLAYER_PLANNED):
        situation_seed = drama_node.get_situation_seed()
        if situation_seed.situation_type.guid64 == situation_type_id:
            if situation_seed.host_sim_id == sim.id:
                situation_seed.special_object_definition_id = special_object.definition.id
                crafting_component = special_object.get_component(objects.components.types.CRAFTING_COMPONENT)
                if crafting_component is not None:
                    recipe_name = crafting_component.get_recipe().get_recipe_name()
                    situation_seed.special_object_name = recipe_name
            break
    else:
        sims4.commands.output("Couldn't find a scheduled situation with ID {}".format(situation_type_id), _connection)
        return False

    if add_to_host_hidden_inventory:
        sim.inventory_component.player_try_add_object(special_object, hidden=True)
    sims4.commands.output('Added object {} to situation {}'.format(object_id, situation_type_id), _connection)


@sims4.commands.Command('situations.create')
def create_situation(situation_type: TunableInstanceParam(sims4.resources.Types.SITUATION), opt_sim: OptionalSimInfoParam=None, user_facing: bool=True, zone_id: int=0, _connection=None):
    situation_manager = services.get_zone_situation_manager()
    sim = get_optional_target(opt_sim, _connection, target_type=OptionalSimInfoParam)
    guest_list = SituationGuestList(False, sim.id)
    situation_id = situation_manager.create_situation(situation_type, guest_list=guest_list, user_facing=user_facing, zone_id=zone_id)
    if situation_id is not None:
        sims4.commands.output('Successfully created situation: {}.'.format(situation_id), _connection)
    else:
        sims4.commands.output('Insufficient funds to create situation.', _connection)


@sims4.commands.Command('situations.create_walkby')
def create_walkby_situation(situation_type: TunableInstanceParam(sims4.resources.Types.SITUATION), _connection=None):
    situation_id = services.current_zone().ambient_service.start_specific_situation(situation_type)
    if situation_id is not None:
        sims4.commands.output('Started situation {} with id {}'.format(situation_type, situation_id), _connection)
    else:
        sims4.commands.output('Could not start {}'.format(situation_type), _connection)


@sims4.commands.Command('situations.create_with_predefined_guest_list')
def create_situation_with_predefined_guest_list(situation_type: TunableInstanceParam(sims4.resources.Types.SITUATION), zone_id: int=0, _connection=None):
    situation_manager = services.get_zone_situation_manager()
    guest_list = situation_type.get_predefined_guest_list()
    if guest_list is None:
        sims4.commands.output('Unable to create guest list!', _connection)
        return
    else:
        situation_id = situation_manager.create_situation(situation_type, guest_list=guest_list, user_facing=False, zone_id=zone_id)
        if situation_id is not None:
            sims4.commands.output('Successfully created situation: {}.'.format(situation_id), _connection)
        else:
            sims4.commands.output('Insufficient funds to create situation', _connection)


@sims4.commands.Command('situations.create_for_venue', command_type=(sims4.commands.CommandType.DebugOnly))
def create_situation_for_venue_type(situation_type: TunableInstanceParam(sims4.resources.Types.SITUATION), venue_tuning: TunableInstanceParam(sims4.resources.Types.VENUE), opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection, target_type=OptionalSimInfoParam)
    if not services.current_zone().venue_service.has_zone_for_venue_type((venue_tuning,)):
        sims4.commands.output('There are no zones that support the venue tuning provided, {}.'.format(venue_tuning), _connection)
        return False
    else:
        situation_manager = services.get_zone_situation_manager()
        zone_id, _ = services.current_zone().venue_service.get_zone_and_venue_type_for_venue_types((venue_tuning,))
        guest_list = SituationGuestList(False, sim.id)
        situation_id = situation_manager.create_situation(situation_type, guest_list=guest_list, user_facing=True, zone_id=zone_id)
        if situation_id is None:
            sims4.commands.output('Insufficient funds to create situation', _connection)
        else:
            sims4.commands.output('Successfully created situation: {}.'.format(situation_id), _connection)


@sims4.commands.Command('situations.create_gl', command_type=(sims4.commands.CommandType.Live))
def create_situation_with_guest_list(situation_type: TunableInstanceParam(sims4.resources.Types.SITUATION), scoring_enabled: bool, zone_id: int=0, scheduled_time: int=0, drama_node_uid: int=0, activity_ids: str='', guest_style: tag.Tag=tag.Tag.INVALID, guest_color: tag.Tag=tag.Tag.INVALID, *args, _connection=None):
    if len(args) % 3 != 0:
        sims4.commands.output('Invalid guest list, its length must be a multiple of 3', _connection)
        sims4.commands.automation_output('SituationCreateGL; Status:Failed, Message:Invalid guest list, its length must be a multiple of 3. Guest list is {}'.format(args), _connection)
        return False
        situation_manager = services.get_zone_situation_manager()
        client = services.client_manager().get(_connection)
        if client.active_sim is not None:
            host_sim_id = client.active_sim.id
            client.active_sim.household.set_situation_scoring(scoring_enabled)
        else:
            host_sim_id = 0
        guest_list = SituationGuestList(situation_type.force_invite_only, host_sim_id)
        guest_list_is_good = True
        job_manager = services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)
        for job_name_or_key, sim_id_or_name, purpose_name in zip(args[0::3], args[1::3], args[2::3]):
            job_type = job_manager.get(job_name_or_key)
            try:
                purpose = SituationInvitationPurpose(purpose_name)
            except ValueError:
                sims4.commands.output('Invalid Purpose: {}. Use INVITED, HIRED, or PREFERRED'.format(purpose_name), _connection)
                sims4.commands.automation_output('SituationCreateGL; Status:Failed, Message: Invalid Purpose: {}. Use INVITED, HIRED, or PREFERRED'.format(purpose_name), _connection)
                guest_list_is_good = False
                continue

            try:
                sim_id = int(sim_id_or_name)
            except (ValueError, TypeError):
                sims4.commands.output('Incorrectly formatted sim_id {}'.format(sim_id_or_name), _connection)
                sims4.commands.automation_output('SituationCreateGL; Status:Failed, Message: Incorrectly formatted sim_id {}'.format(sim_id_or_name), _connection)
                guest_list_is_good = False
                continue

            guest_info = SituationGuestInfo.construct_from_purpose(sim_id, job_type, purpose)
            guest_list.add_guest_info(guest_info)

        if not guest_list_is_good:
            sims4.commands.output('FAILURE: bad guest list {}.'.format(situation_type), _connection)
            sims4.commands.automation_output('SituationCreateGL; Status:Failed, Message: Bad guest list {}.'.format(situation_type), _connection)
            return False
        guest_list = situation_type.get_extended_guest_list(guest_list=guest_list)
        scheduled_time_day_time = DateAndTime(scheduled_time) if scheduled_time != 0 else None
        drama_node = drama_node_uid if drama_node_uid else None
        if activity_ids == '0' or len(activity_ids) < 1:
            activity_id_list = None
    else:
        activity_id_list = list(map(int, activity_ids.split(',')))
    situation_id = situation_manager.create_situation(situation_type, guest_list=guest_list,
      zone_id=zone_id,
      scoring_enabled=scoring_enabled,
      scheduled_time=scheduled_time_day_time,
      existing_drama_node_uid=drama_node,
      activity_id_list=activity_id_list,
      guest_attire_style=guest_style,
      guest_attire_color=guest_color)
    if situation_id is not None and scheduled_time == 0:
        sims4.commands.output('Successfully created situation: {}.'.format(situation_id), _connection)
        sims4.commands.automation_output('SituationCreateGL; Status:Success, Id:{}'.format(situation_id), _connection)
    else:
        if situation_id is not None:
            sims4.commands.output('Successfully scheduled situation for the future: {}.'.format(situation_id), _connection)
            sims4.commands.automation_output('SituationCreateGL; Status:Success, Id:{}'.format(situation_id), _connection)
        else:
            sims4.commands.output('Insufficient funds to create situation', _connection)
            sims4.commands.automation_output('SituationCreateGL; Status:Failed, Message: Insufficient funds to create situation', _connection)
    return True


@sims4.commands.Command('qa.situations.create', command_type=(sims4.commands.CommandType.Automation))
def automation_create_situation(situation_type: TunableInstanceParam(sims4.resources.Types.SITUATION), opt_sim: OptionalSimInfoParam=None, _connection=None):
    if situation_type is None:
        sims4.commands.automation_output('SituationCreate; Status:Failed', _connection)
        return False
    else:
        situation_manager = services.get_zone_situation_manager()
        sim_spawner_service = services.sim_spawner_service()
        sim = get_optional_target(opt_sim, _connection, target_type=OptionalSimInfoParam)
        if sim is None:
            sims4.commands.automation_output('SituationCreate; Status:Failed', _connection)
            return False
            sim_spawner_service.enable_gui_smoke_notification()
            guest_list = SituationGuestList(invite_only=False, host_sim_id=(sim.id))
            situation_id = situation_manager.create_situation(situation_type, guest_list=guest_list)
            if situation_id is not None:
                sims4.commands.automation_output('SituationCreate; Status:Success, Id:{}'.format(situation_id), _connection)
        else:
            sims4.commands.automation_output('SituationCreate; Status:Failed', _connection)


@sims4.commands.Command('situations.allow_debug_situations')
def allow_debug_situations(allow: bool=True, _connection=None):
    global allow_debug_situations_in_ui
    allow_debug_situations_in_ui = allow


@sims4.commands.Command('situations.destroy')
def destroy_situation(situation_id: int, _connection=None):
    sit_man = services.get_zone_situation_manager()
    if situation_id is None:
        sims4.commands.output('No situation id specified.  Valid options are: ', _connection)
        _list_situations(sit_man, _connection=_connection)
        return
    sit_man.destroy_situation_by_id(situation_id)


@sims4.commands.Command('situations.destroy_all_situations')
def destroy_all_situations(_connection=None):
    services.get_zone_situation_manager().destroy_all_situations()


@sims4.commands.Command('situations.advance_phase')
def advance_situation_phase(situation_id: int=None, _connection=None):
    sit_man = services.get_zone_situation_manager()
    if situation_id is None:
        sims4.commands.output('No situation id specified.  Valid options are: ', _connection)
        _list_situations(sit_man, _connection=_connection)
        return
    sit = sit_man.get(situation_id)
    if sit is None:
        sims4.commands.output('Invalid situation id.  Valid options are: ', _connection)
        _list_situations(sit_man, _connection=_connection)
        return
    sit._transition_to_next_phase()


@sims4.commands.Command('qa.situations.advance_phase', command_type=(sims4.commands.CommandType.Automation))
def automation_advance_situation_phase(situation_id: int=None, _connection=None):
    situation_manager = services.get_zone_situation_manager()
    situation = situation_manager.get(situation_id)
    if situation is None:
        sims4.commands.automation_output('AdvancePhase; Success:False', _connection)
        return
    situation._transition_to_next_phase()
    sims4.commands.automation_output('AdvancePhase; Success:True', _connection)
    return True


@sims4.commands.Command('situations.on_situation_goal_button_clicked', command_type=(sims4.commands.CommandType.Live))
def on_situation_goal_button_clicked(situation_id: int, _connection=None):
    situation_manager = services.get_zone_situation_manager()
    situation = situation_manager.get(situation_id)
    if situation is None:
        sims4.commands.output('FAILURE: Situation with id {} is not found.'.format(situation_id), _connection)
        return False
    situation.on_situation_goal_button_clicked()
    return True


@sims4.commands.Command('situations.refresh_goals', command_type=(sims4.commands.CommandType.Live))
def refresh_goals(_connection=None):
    sit_man = services.get_zone_situation_manager()
    situations = sit_man.running_situations()
    for situation in situations:
        situation.refresh_situation_goals()

    sims4.commands.output("Sim's goals refreshed.", _connection)


@sims4.commands.Command('situations.complete_goal')
def complete_goal(goal_name, target_sim_id=None, _connection=None):
    if target_sim_id is None or target_sim_id == 0:
        target_sim = None
    else:
        target_sim = services.object_manager().get(int(target_sim_id, base=0))
    situations = services.get_zone_situation_manager().running_situations()
    success = False
    for situation in situations:
        success = situation.debug_force_complete_by_goal_name(goal_name, target_sim)
        if success:
            break

    if success:
        sims4.commands.output('Success: Goal {} Completed'.format(goal_name), _connection)
    else:
        sims4.commands.output('FAILURE: Goal {} NOT Completed'.format(goal_name), _connection)
    return success


@sims4.commands.Command('situations.complete_goal_id')
def complete_goal_id(goal_id: int, situation_id: int, _connection=None):
    situations = services.get_zone_situation_manager().running_situations()
    success = False
    for situation in situations:
        if situation.id == situation_id:
            situation_goal_tracker = situation._get_goal_tracker()
            success = situation_goal_tracker.debug_force_complete_by_goal_id(goal_id)
            if success:
                break

    if success:
        sims4.commands.output('Success: Goal {} Completed'.format(goal_id), _connection)
    else:
        sims4.commands.output('FAILURE: Goal {} NOT Completed'.format(goal_id), _connection)
    return success


@sims4.commands.Command('qa.situations.complete_goal', command_type=(sims4.commands.CommandType.Automation))
def automation_complete_goal(situation_id: int, goal_name, _connection=None):
    situation_manager = services.get_zone_situation_manager()
    situation = situation_manager.get(situation_id)
    if situation is None:
        sims4.commands.automation_output('CompleteGoal; Success:False', _connection)
        return False
    else:
        result = situation.debug_force_complete_named_goal(goal_name, None)
        if result:
            sims4.commands.automation_output('CompleteGoal; Success:True', _connection)
        else:
            sims4.commands.automation_output('CompleteGoal; Success:False', _connection)
    return result


@sims4.commands.Command('situations.excursions.advance_activity')
def excursions_advance_activity(_connection=None):
    situations = services.get_zone_situation_manager().running_situations()
    excursion_situation = None
    for situation in situations:
        if isinstance(situation, ExcursionSituation):
            excursion_situation = situation
            break

    if excursion_situation is None:
        sims4.commands.output('FAILURE: No Excursion Situation is currently running.', _connection)
        return False
    else:
        success = excursion_situation.debug_advance_activity()
        if success:
            sims4.commands.output('Success: Situation {} advanced to next activity.'.format(str(excursion_situation)), _connection)
        else:
            sims4.commands.output('FAILURE: Situation {} NOT advanced to next activity.'.format(str(excursion_situation)), _connection)
    return success


@sims4.commands.Command('situations.excursions.goto_activity')
def excursions_goto_activity(activity_key, _connection=None):
    situations = services.get_zone_situation_manager().running_situations()
    excursion_situation = None
    for situation in situations:
        if isinstance(situation, ExcursionSituation):
            excursion_situation = situation
            break

    if excursion_situation is None:
        sims4.commands.output('FAILURE: No Excursion Situation is currently running.', _connection)
        return False
    else:
        success = excursion_situation.debug_goto_activity(activity_key)
        if success:
            sims4.commands.output('Success: Situation {} set to activity {}.'.format(str(excursion_situation), activity_key), _connection)
        else:
            sims4.commands.output('FAILURE: Situation {} NOT set to activity {}'.format(str(excursion_situation), activity_key), _connection)
    return success


@sims4.commands.Command('situations.save_load_test')
def situation_save_load_seed_test(_connection=None):
    seeds = []
    situation_manager = services.get_zone_situation_manager()
    for situation in situation_manager.running_situations():
        seed = situation.save_situation()
        if seed is not None:
            seeds.append(seed)

    situation_manager.reset(create_system_situations=False)
    for seed in seeds:
        situation_manager.create_situation_from_seed(seed)


@sims4.commands.Command('situations.jobs')
def jobs_for_situation(situation_type: TunableInstanceParam(sims4.resources.Types.SITUATION), _connection=None):
    jobs = situation_type._get_tuned_jobs()
    for job in jobs:
        sims4.commands.output(str(job), _connection)


def _list_jobs(situation, _connection=None):
    sims4.commands.output('Default job:', _connection)
    sims4.commands.output('   {} '.format(situation.default_job()), _connection)
    sims4.commands.output('All jobs: ({})'.format(len(situation._jobs)), _connection)
    sims4.commands.output('    count{:>50} : {:<50}'.format('Job Name', 'Default Role'), _connection)
    index = 0
    for job_data in situation._jobs.values():
        count = situation.get_num_sims_in_job(job_data.get_job_type())
        sims4.commands.output(' {:2} {:3}  {:>50} : {:<50}'.format(index, count, job_data.get_job_type(), job_data.default_role_state_type), _connection)
        index = index + 1


def _list_sims_in_jobs(situation, _connection=None):
    sims4.commands.output('All jobs: ({})'.format(len(situation._jobs)), _connection)
    sims4.commands.output('    count{:>50} : {:<50}'.format('Job Name', 'Default Role'), _connection)
    index = 0
    for job_data in situation._jobs.values():
        count = situation.get_num_sims_in_job(job_data.get_job_type())
        job_name = job_data.get_job_type().__name__
        default_role_name = job_data.default_role_state_type.__name__
        sims4.commands.output(' {:2} {:3}  {:>50} : {:<50}'.format(index, count, job_name, default_role_name), _connection)
        index = index + 1
        for sim in situation.all_sims_in_job_gen(job_data.get_job_type()):
            sim_id = sim.sim_id
            role_name = situation.get_current_role_state_for_sim(sim).__name__
            sims4.commands.output('        {:>50}  : {:<50}'.format(sim_id, role_name), _connection)
            sims4.commands.automation_output('ListJobs; sim_id:{}, job_name:{}, role_name:{}, default_role_name:{}'.format(sim_id, job_name, role_name, default_role_name), _connection)


def _list_phases(situation, _connection=None):
    sims4.commands.output('Current phase: ({:3}/{:3})'.format(situation._phase_index, len(situation._phases)), _connection)
    sims4.commands.output('      {} '.format(situation._phase), _connection)
    sims4.commands.output('All phases:', _connection)
    count = 0
    for phase in situation._phases:
        sims4.commands.output(' {:3}: {} '.format(count, phase), _connection)
        count = count + 1


def _list_situations(sit_man, _connection=None):
    sims4.commands.output('Situation: ', _connection)
    situations = list(sit_man._objects.values())
    if not situations:
        sims4.commands.output('   None', _connection)
    else:
        for sit in situations:
            sims4.commands.output('   {}  {} '.format(sit.id, sit), _connection)


@sims4.commands.Command('situations.list_jobs')
def list_situation_jobs(situation_id: int=None, _connection=None):
    sit_man = services.get_zone_situation_manager()
    if situation_id is None:
        sims4.commands.output('You must specify a valid situation id', _connection)
        sims4.commands.automation_output('ListJobs; Success:False, Reason:No situation id specified', _connection)
        return
    sit = sit_man.get(situation_id)
    if sit is None:
        sims4.commands.output('Invalid situation id.  Valid options are: ', _connection)
        _list_situations(sit_man, _connection=_connection)
        sims4.commands.automation_output('ListJobs; Success:False, Reason:Invalid situation id', _connection)
        return
    sims4.commands.output('===========================================================================', _connection)
    sims4.commands.output('{} '.format(sit), _connection)
    _list_sims_in_jobs(sit, _connection)
    sims4.commands.output('===========================================================================', _connection)
    sims4.commands.automation_output('ListJobs; Success:True', _connection)


@sims4.commands.Command('situations.show')
def list_active_situations(situation_id: int=None, _connection=None):
    sit_man = services.get_zone_situation_manager()
    if situation_id is None:
        sims4.commands.output('===========================================================================', _connection)
        _list_situations(sit_man, _connection)
        sims4.commands.output('For info about a particular situation, provide the id as an argument.', _connection)
        sims4.commands.output('===========================================================================', _connection)
        return
    sit = sit_man.get(situation_id)
    if sit is None:
        sims4.commands.output('Invalid situation id.  Valid options are: ', _connection)
        _list_situations(sit_man, _connection=_connection)
        return
    sims4.commands.output('===========================================================================', _connection)
    sims4.commands.output('Name:        {} '.format(sit), _connection)
    sims4.commands.output('ID:          {} '.format(sit.id), _connection)
    sims4.commands.output('Sim count:   {} '.format(len(sit._situation_sims)), _connection)
    sims4.commands.output('Level|Score: {}|{}'.format(sit.get_level(), sit.score), _connection)
    sims4.commands.output('Phase/State: {} '.format(sit.get_phase_state_name_for_gsi()), _connection)
    sims4.commands.output('===============================', _connection)
    _list_jobs(sit, _connection)
    sims4.commands.output('===============================', _connection)


@sims4.commands.Command('qa.situations.num_sims_in_role_state', command_type=(sims4.commands.CommandType.Automation))
def automation_get_num_sims_in_role_state(situation_id: int, role_state_type: TunableInstanceParam(sims4.resources.Types.ROLE_STATE), _connection=None):
    situation_manager = services.get_zone_situation_manager()
    situation = situation_manager.get(situation_id)
    if situation is None:
        sims4.commands.automation_output('NumInRoleState; Number:0', _connection)
        return
    if role_state_type is None:
        sims4.commands.automation_output('NumInRoleState; Number:0', _connection)
    count = situation.get_num_sims_in_role_state(role_state_type)
    sims4.commands.automation_output('NumInRoleState; Number:{}'.format(count), _connection)


@sims4.commands.Command('qa.situations.info', command_type=(sims4.commands.CommandType.Automation))
def automation_list_active_situations(situation_id: int=None, _connection=None):
    sit_man = services.get_zone_situation_manager()
    sit = sit_man.get(situation_id)
    if sit is None:
        sims4.commands.automation_output('SituationInfo; Exists:No', _connection)
        return
    sims4.commands.output('SituationInfo; Exists:Yes, Id:{}, ClassName:{}, NumSims:{}, Level:{}, Score:{}, State:{} '.format(sit.id, sit.__class__.__name__, len(sit._situation_sims), int(sit.get_level()), sit.score, sit.get_phase_state_name_for_gsi()), _connection)
    sims4.commands.automation_output('SituationInfo; Exists:Yes, Id:{}, ClassName:{}, NumSims:{}, Level:{}, Score:{}, State:{}'.format(sit.id, sit.__class__.__name__, len(sit._situation_sims), int(sit.get_level()), sit.score, sit.get_phase_state_name_for_gsi()), _connection)


@sims4.commands.Command('situations.get_sim_score')
def get_sim_score_in_situation(sim_id: OptionalSimInfoParam, situation_id: int=None, _connection=None):
    sim = get_optional_target(sim_id, _connection, target_type=OptionalSimInfoParam)
    if situation_id is None or sim is None:
        sims4.commands.output('Invalid arguments provided.  Syntax:', _connection)
        sims4.commands.output('    |situations.get_sim_score <sim_id> <situation_id>', _connection)
        sims4.commands.output('         <sim_id>: Ctrl+click on a sim in the window to paste their sim_id into the command prompt', _connection)
        sims4.commands.output('         <situation_id>: id to situation ', _connection)
        return
    sit_man = services.get_zone_situation_manager()
    sit = sit_man.get(situation_id)
    if sit is None:
        sims4.commands.output('Invalid situation id.  Valid options are: ', _connection)
        _list_situations(sit_man, _connection=_connection)
        return
    sims4.commands.output('Score in situation: {}'.format(sit.get_sim_total_score(sim)), _connection)


@sims4.commands.Command('situations.update_sim_score')
def update_sim_score(sim_id: OptionalSimInfoParam, situation_id: int=None, delta: int=None, _connection=None):
    sim = get_optional_target(sim_id, _connection, target_type=OptionalSimInfoParam)
    if situation_id is None or sim is None or delta is None:
        sims4.commands.output('Invalid arguments provided.  Syntax:', _connection)
        sims4.commands.output('    |situations.get_sim_score <sim_id> <situation_id> <int>', _connection)
        sims4.commands.output('         <sim_id>: Ctrl+click on a sim in the window to paste their sim_id into the command prompt', _connection)
        sims4.commands.output('         <situation_id>: id to situation ', _connection)
        sims4.commands.output("         <int>: delta to apply to sim's score ", _connection)
        return
    sit_man = services.get_zone_situation_manager()
    sit = sit_man.get(situation_id)
    if sit is None:
        sims4.commands.output('Invalid situation id.  Valid options are: ', _connection)
        _list_situations(sit_man, _connection=_connection)
        return
    sit.sim_score_update(sim, delta)
    sims4.commands.output('Score in situation: {}'.format(sit.get_sim_total_score(sim)), _connection)


@sims4.commands.Command('situations.set_situation_score')
def set_situation_score(situation_id: int=None, score: int=None, _connection=None):
    if situation_id is None or score is None:
        sims4.commands.output('Invalid arguments provided.  Syntax:', _connection)
        sims4.commands.output('    |situations.set_situation_score <situation_id> <score>', _connection)
        sims4.commands.output('         <situation_id>: id to situation ', _connection)
        sims4.commands.output('         <score> : Override the score of the entire situation', _connection)
        return
    sit_man = services.get_zone_situation_manager()
    sit = sit_man.get(situation_id)
    if sit is None:
        sims4.commands.output('Invalid situation id.  Valid options are: ', _connection)
        _list_situations(sit_man, _connection=_connection)
        return
    sit.debug_set_overall_score(score)
    sims4.commands.output('Situation Score: {}'.format(sit.score), _connection)


@sims4.commands.Command('situations.set_situation_medal')
def set_situation_medal(situation_id: int=None, medal: SituationMedal=None, _connection=None):
    if situation_id is None or medal is None:
        sims4.commands.output('Invalid arguments provided.  Syntax:', _connection)
        sims4.commands.output('    |situations.set_situation_medal <situation_id> <TIN/BRONZE/SILVER/GOLD>', _connection)
        return
    else:
        sit_man = services.get_zone_situation_manager()
        situation = sit_man.get(situation_id)
        if situation is None:
            sims4.commands.output('Invalid situation id.', _connection)
            return
        situation.should_track_score or sims4.commands.output('Invalid non-scoring situation {}'.format(situation), _connection)
        return
    score = 0
    for m in SituationMedal:
        data = situation.get_level_data(m)
        if data is not None:
            score += data.score_delta
        else:
            if m == medal:
                sims4.commands.output('Situation {} has no tuning data for the required medal {}.'.format(situation, medal), _connection)
                return
        if m == medal:
            break

    situation.debug_set_overall_score(score)
    sims4.commands.output('Situation Score: {} and Medal: {}'.format(situation.score, medal), _connection)


@sims4.commands.Command('situations.add_score')
def add_score(situation_id: int, delta: int, _connection=None):
    sit_man = services.get_zone_situation_manager()
    situation = sit_man.get(situation_id)
    if situation is None:
        sims4.commands.output('Invalid situation id.', _connection)
        return
    if not situation.should_track_score:
        sims4.commands.output('Invalid non-scoring situation {}'.format(situation), _connection)
        return
    situation.score_update(delta)
    sims4.commands.output('Resulting Situation Score: {}'.format(situation.score), _connection)


@sims4.commands.Command('situations.add_score_to_all')
def add_score_to_all(delta: int, _connection=None):
    for situation in services.get_zone_situation_manager().get_all():
        if not situation.should_track_score:
            continue
        old_score = situation.score
        situation.score_update(delta)
        sims4.commands.output('Changed {} score from {} to {}'.format(str(situation), old_score, situation.score), _connection)


@sims4.commands.Command('situations.set_constrained_goal_list')
def set_constrained_goal_list(*goal_names: str, _connection=None):
    constrained_goals = set()
    for goal_name in goal_names:
        goal_type = get_tunable_instance(sims4.resources.Types.SITUATION_GOAL, goal_name)
        if goal_type is None:
            sims4.commands.output('Invalid goal name: {} skipping.'.format(goal_name), _connection)
            sims4.commands.automation_output('SetConstrainedGoal; Success:False, Message:Invalid goal name {}'.format(goal_name), _connection)
            continue
        constrained_goals.add(goal_type)

    situations.situation_goal_tracker.SituationGoalTracker.constrained_goals = constrained_goals
    sims4.commands.automation_output('SetConstrainedGoal; Success:True', _connection)


@sims4.commands.Command('situations.test_end_score_callback')
def test_end_score_callback(situation_id: int, _connection=None):
    situation_manager = services.get_zone_situation_manager()
    situation_manager.register_for_callback(situation_id, SituationCallbackOption.END_OF_SITUATION_SCORING, _end_score_callback)


def _end_score_callback(situation_id, option, end_score_data):
    logger.debug('data {}', end_score_data)


@sims4.commands.Command('situations.test_situation_available')
def test_situation_available(situation_type: TunableInstanceParam(sims4.resources.Types.SITUATION), opt_sim: OptionalSimInfoParam=None, target_sim_id: int=0, _connection=None):
    sim = get_optional_target(opt_sim, _connection, target_type=OptionalSimInfoParam)
    if sim is None:
        sims4.commands.output('Invalid sim: {} provided.'.format(opt_sim), _connection)
        return
    else:
        situation_name = str(situation_type)
        if situation_type.is_situation_available(sim, target_sim_id):
            sims4.commands.output('Situation {} with initiating sim {} and target sim {} is available.'.format(situation_name, sim, target_sim_id), _connection)
        else:
            sims4.commands.output('Situation {} with initiating sim {} and target sim {} is not available.'.format(situation_name, sim, target_sim_id), _connection)


@sims4.commands.Command('situations.reset')
def reset(_connection=None):
    services.get_zone_situation_manager().reset()
    for sim in services.sim_info_manager().instanced_sims_gen():
        try:
            sim.reset_role_tracker()
        except Exception:
            logger.error('Error while resetting role tracker for sim {}', sim)


@sims4.commands.Command('situations.pre_destroy_user_facing_situation', command_type=(sims4.commands.CommandType.Live))
def pre_destroy_user_facing_situation(situation_id: int=None, _connection=None):
    sit_man = services.get_zone_situation_manager()
    if situation_id is None:
        for situation in tuple(sit_man.get_user_facing_situations_gen()):
            sit_man.pre_destroy_situation_by_id(situation.id)

        return
    situation = sit_man.get(situation_id)
    if not (situation is None or situation.is_user_facing):
        sims4.commands.output('Invalid player facing situation id.', _connection)
        return
    sit_man.pre_destroy_situation_by_id(situation.id)


@sims4.commands.Command('situations.destroy_user_facing_situation', command_type=(sims4.commands.CommandType.Live))
def destroy_user_facing_situation(situation_id: int=None, _connection=None):
    sit_man = services.get_zone_situation_manager()
    if situation_id is None:
        for situation in tuple(sit_man.get_user_facing_situations_gen()):
            sit_man.destroy_situation_by_id(situation.id)

        return
    situation = sit_man.get(situation_id)
    if not (situation is None or situation.is_user_facing):
        sims4.commands.output('Invalid player facing situation id.', _connection)
        return
    sit_man.destroy_situation_by_id(situation.id)


@sims4.commands.Command('situations.change_user_facing_situation_duration', command_type=(sims4.commands.CommandType.DebugOnly))
def change_user_facing_situation_duration(situation_id: int, duration: int, _connection=None):
    sit_man = services.get_zone_situation_manager()
    situation = sit_man.get(situation_id)
    if not (situation is None or situation.is_user_facing):
        sims4.commands.output('Invalid player facing situation id.', _connection)
        return
    situation.change_duration(duration)


@sims4.commands.Command('situations.force_loot_actions')
def force_loot_actions(loot_actions_type: TunableInstanceParam(sims4.resources.Types.ACTION), _connection=None):
    BaseSituation.constrained_emotional_loot = loot_actions_type


@sims4.commands.Command('situations.churn_jobs')
def churn_jobs(_connection=None):
    situation_manager = services.get_zone_situation_manager()
    for situation in situation_manager.running_situations():
        situation.churn_jobs()


@sims4.commands.Command('situations.shift_change')
def shift_change(_connection=None):
    situation_manager = services.get_zone_situation_manager()
    for situation in situation_manager.running_situations():
        situation.shift_change_jobs()


@sims4.commands.Command('situations.blacklist')
def show_blacklist(_connection=None):
    situation_manager = services.get_zone_situation_manager()
    blacklist = situation_manager.get_auto_fill_blacklist()
    for sim_id in blacklist:
        sim = services.sim_info_manager().get(sim_id)
        if sim is not None:
            blacklist_info = situation_manager.get_blacklist_info(sim.id)
            for bi in blacklist_info:
                sims4.commands.output('Sim: {} Tag: {} Time remaining: {}'.format(sim, bi[0], bi[1]), _connection)


@sims4.commands.Command('situations.set_npc_soft_cap', 'sim_spawner_service.set_npc_soft_cap', command_type=(sims4.commands.CommandType.Automation))
def set_npc_soft_cap(soft_cap: int, _connection=None):
    services.sim_spawner_service().set_npc_soft_cap_override(soft_cap)
    sims4.commands.output('Npc soft cap override set to {}'.format(soft_cap), _connection)


@sims4.commands.Command('situations.enable_perf_cheats', 'sim_spawner_service.enable_perf_cheats', command_type=(sims4.commands.CommandType.Automation))
def enable_perf_cheats(enable: bool=True, _connection=None):
    situation_manager = services.get_zone_situation_manager()
    situation_manager.enable_perf_cheat(enable)
    services.sim_spawner_service().enable_perf_cheat(enable)
    TravelInteraction.set_npc_leave_enabled(not enable)
    sims4.commands.output('Perf cheats={}'.format(enable), _connection)


@sims4.commands.Command('situations.make_greeted', command_type=(sims4.commands.CommandType.Live))
def make_greeted(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection, target_type=OptionalSimInfoParam)
    if sim is None:
        sims4.commands.output('Invalid sim: {} provided.'.format(opt_sim), _connection)
        return
    situation_manager = services.get_zone_situation_manager()
    situation_manager.make_waiting_player_greeted(sim)


@sims4.commands.Command('situations.start_situation_creation', command_type=(sims4.commands.CommandType.Live))
def start_situation_creation(opt_sim: OptionalSimInfoParam=None, creation_time: int=None, situation_category: SituationCategoryUid=SituationCategoryUid.DEFAULT, _connection=None):
    sim = get_optional_target(opt_sim, _connection, target_type=OptionalSimInfoParam)
    if sim is None:
        sims4.commands.output('Invalid sim: {} provided.'.format(opt_sim), _connection)
        return
    situation_manager = services.get_zone_situation_manager()
    situation_manager.send_situation_start_ui(sim, creation_time=creation_time, situation_category=situation_category)


@sims4.commands.Command('situations.start_situation_creation_for_edit', command_type=(sims4.commands.CommandType.Live))
def start_situation_creation_for_edit(opt_sim: OptionalSimInfoParam=None, drama_node_uid: int=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection, target_type=OptionalSimInfoParam)
    if sim is None:
        sims4.commands.output('Invalid sim: {} provided.'.format(opt_sim), _connection)
        return
    situation_manager = services.get_zone_situation_manager()
    situation_manager.send_situation_start_ui_for_edit(sim, drama_node_uid)


@sims4.commands.Command('situations.push_make_sim_leave_now_situation', command_type=(sims4.commands.CommandType.DebugOnly))
def push_make_sim_leave_now_situation(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection, target_type=OptionalSimInfoParam)
    if sim is None:
        sims4.commands.output('Invalid sim: {} provided.'.format(opt_sim), _connection)
        return
    situation_manager = services.get_zone_situation_manager()
    situation_manager.make_sim_leave_now_must_run(sim)


@sims4.commands.Command('situations.enable_welcome_wagon', command_type=(sims4.commands.CommandType.Automation))
def enable_welcome_wagon(enable: bool=True, _connection=None):
    npc_hosted_situation_service = services.npc_hosted_situation_service()
    if npc_hosted_situation_service is not None:
        if enable:
            npc_hosted_situation_service.resume_welcome_wagon()
        else:
            npc_hosted_situation_service.suspend_welcome_wagon()


SITUATION_EXIT_BUTTON_CLICKED = 'OnExitButtonClicked'
SITUATION_EXIT_END_DIALOG_EXIT_CONFIRMED = 'OnExitSituationConfirmed'
SITUATION_EXIT_END_DIALOG_STAY_LATE_CONFIRMED = 'OnStayLateConfirmed'
SITUATION_EXIT_END_DIALOG_PRE_DESTROY_CONFIRMED = 'OnPreDestroySituationConfirmed'
SITUATION_EXIT_END_DIALOG_CANCELED = 'OnExitSituationCanceled'

@sims4.commands.Command('situations.show_end_situation_dialog', command_type=(sims4.commands.CommandType.Live))
def show_end_situation_dialog(situation_id, user_facing_type, has_stayed_late=False, sim_token=None, time_token=None, _connection=None):
    client = services.client_manager().get(_connection)
    situation_manager = services.get_zone_situation_manager()
    situation_to_end = situation_manager.get(situation_id)
    if not (situation_to_end is None or situation_to_end.is_user_facing):
        sims4.commands.output('Invalid player facing situation id.', _connection)
        return
    active_sim_available = situation_to_end.is_situation_available(client.active_sim)

    def _show_end_situation_dialog_response(dialog):
        msg = Situations_pb2.SituationCallbackResponse()
        msg.situation_id = situation_id
        if situation_to_end.is_user_facing:
            if dialog.accepted:
                if user_facing_type <= SituationUserFacingType.ACTING_CAREER_EVENT:
                    msg.situation_callback = SITUATION_EXIT_END_DIALOG_EXIT_CONFIRMED
                if user_facing_type == SituationUserFacingType.UNIVERSITY_HOUSING_KICK_OUT_EVENT:
                    msg.situation_callback = SITUATION_EXIT_END_DIALOG_PRE_DESTROY_CONFIRMED
            if dialog.accepted_alt:
                if user_facing_type == SituationUserFacingType.CAREER_EVENT:
                    msg.situation_callback = SITUATION_EXIT_END_DIALOG_STAY_LATE_CONFIRMED
            if dialog.canceled or dialog.closed:
                msg.situation_callback = SITUATION_EXIT_END_DIALOG_CANCELED
            situation_to_end.add_situation_callback_response_op(msg)

    if situation_to_end.end_situation_dialog is not None and situation_manager.is_user_facing_situation_running() and active_sim_available:
        dialog = situation_to_end.end_situation_dialog(owner=(client.active_sim), resolver=(SingleSimResolver(client.active_sim)),
          disable_alt=has_stayed_late)
        dialog_kwargs = {'on_response': _show_end_situation_dialog_response}
        if user_facing_type == SituationUserFacingType.CAREER_EVENT or user_facing_type == SituationUserFacingType.ACTING_CAREER_EVENT:
            dialog_kwargs['additional_tokens'] = (time_token,)
        (dialog.show_dialog)(**dialog_kwargs)
    else:
        sims4.commands.output('End Situation dialog is not tuned for situation_id {} : Fallback to old method...'.format(situation_id), _connection)
        untuned_msg = Situations_pb2.SituationCallbackResponse()
        untuned_msg.situation_id = situation_id
        untuned_msg.situation_callback = SITUATION_EXIT_BUTTON_CLICKED
        situation_to_end.add_situation_callback_response_op(untuned_msg)


@sims4.commands.Command('situations.get_situation_id', command_type=(sims4.commands.CommandType.Automation))
def get_situation_id(situation_type: TunableInstanceParam(sims4.resources.Types.SITUATION), _connection=None):
    matching_situation_id = 0
    situation_manager = services.get_zone_situation_manager()
    for situation_id in situation_manager:
        situation = situation_manager.get(situation_id)
        if situation.guid64 == situation_type.guid64:
            matching_situation_id = situation_id
            break

    sims4.commands.output('GetSitId; SitId:{}'.format(matching_situation_id), _connection)
    sims4.commands.automation_output('GetSitId; SitId:{}'.format(matching_situation_id), _connection)