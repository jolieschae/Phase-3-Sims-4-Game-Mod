# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\tunable.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 55943 bytes
import collections, functools, weakref
from clock import ClockSpeedMode
from date_and_time import create_time_span
from element_utils import build_critical_section_with_finally
from event_testing.resolver import SingleSimResolver
from event_testing.tests import TunableTestSet
from interactions import ParticipantType, ParticipantTypeSingle
from interactions.context import InteractionContext, QueueInsertStrategy
from interactions.interaction_finisher import FinishingType
from interactions.liability import Liability
from interactions.priority import Priority
from interactions.utils.interaction_elements import XevtTriggeredElement
from interactions.utils.notification import NotificationElement
from objects import ALL_HIDDEN_REASONS
from objects.object_tests import CraftTaggedItemFactory
from sims.sim_info_types import Species
from sims4 import commands
from sims4.commands import get_command_restrictions, CommandRestrictionFlags, get_command_type, CommandType
from sims4.localization import TunableLocalizedStringFactory
from sims4.resources import Types
from sims4.tuning.tunable import TunableList, TunableReference, TunableFactory, Tunable, TunableEnumEntry, TunableTuple, TunableVariant, HasTunableFactory, TunableSimMinute, OptionalTunable, AutoFactoryInit, TunableMapping, TunableSet
from situations.situation_types import SituationCallbackOption
from statistics.statistic_ops import TunableStatisticChange, StatisticChangeOp
from tag import TunableTags, TunableTag
from ui.ui_dialog_notification import TunableUiDialogNotificationSnippet
from world.travel_group_tuning import TravelGroupTuning
import alarms, clock, random, services, sims4.log, sims4.resources
logger = sims4.log.Logger('Super Interactions')

class TunableAffordanceLinkList(TunableList):

    def __init__(self, class_restrictions=(), **kwargs):
        (super().__init__)(
         TunableReference((services.get_instance_manager(sims4.resources.Types.INTERACTION)), category='asm',
           description='Linked Affordance',
           class_restrictions=class_restrictions,
           pack_safe=True), **kwargs)


class TunableStatisticAdvertisements(TunableList):

    def __init__(self, **kwargs):
        (super().__init__)(
         TunableStatisticChange(locked_args={'subject':ParticipantType.Actor,  'advertise':True}, statistic_override=StatisticChangeOp.get_statistic_override(pack_safe=True)), **kwargs)


class TunableContinuation(TunableList):
    TAGGED_ITEM = 0
    ITEM_DEFINITION = 1
    ITEM_TUNING_ID = 2

    def __init__(self, target_default=ParticipantType.Object, locked_args={}, carry_target_default=ParticipantType.Object, class_restrictions=(), **kwargs):
        (super().__init__)(tunable=TunableTuple(description='\n                A continuation entry.\n                ',
                    affordance=TunableReference(description='\n                    The affordance to push as a continuation on the specified\n                    actor Sim.\n                    ',
                    manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
                    class_restrictions=class_restrictions,
                    pack_safe=True),
                    si_affordance_override=TunableReference(description="\n                When the tuned affordance is a mixer for a different SI, use\n                this to specify the mixer's appropriate SI. This is useful for\n                pushing socials.\n                ",
                    manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
                    allow_none=True),
                    actor=TunableEnumEntry(description='\n                The Sim on which the affordance is pushed.\n                ',
                    tunable_type=ParticipantType,
                    default=(ParticipantType.Actor)),
                    target=TunableEnumEntry(description='\n                The participant the affordance will target.\n                ',
                    tunable_type=ParticipantType,
                    default=target_default),
                    carry_target=OptionalTunable(description='\n                If enabled, specify a carry target for this continuation.\n                ',
                    tunable=TunableEnumEntry(description='\n                    The participant the affordance will set as a carry target.\n                    ',
                    tunable_type=ParticipantType,
                    default=carry_target_default)),
                    inventory_carry_target=TunableVariant(description='\n                Item in inventory (of continuations actor) to use as carry\n                target for continuation if carry target is None\n                ',
                    object_with_tag=CraftTaggedItemFactory(locked_args={'check_type': TunableContinuation.TAGGED_ITEM}),
                    object_with_definition=TunableTuple(definition=TunableReference(description='\n                        The exact object definition to look for inside\n                        inventory.\n                        ',
                    manager=(services.definition_manager())),
                    locked_args={'check_type': TunableContinuation.ITEM_DEFINITION}),
                    object_with_base_definition=TunableTuple(definition=TunableReference(description='\n                        The base definition to look for inside inventory.\n                        Objects that redirect (like counters) will match if base\n                        definition is the same.\n                        ',
                    manager=(services.definition_manager())),
                    locked_args={'check_type': TunableContinuation.ITEM_TUNING_ID}),
                    locked_args={'None': None},
                    default='None'),
                    preserve_preferred_object=Tunable(description="\n                If checked, the pushed interaction's preferred objects are\n                determined by the current preferred objects.\n                \n                If unchecked, the transition sequence would not award bonuses to\n                any specific part.\n                ",
                    tunable_type=bool,
                    default=True),
                    preserve_target_part=Tunable(description='\n                If checked, the pushed interaction will use the same target part\n                if applicable. Defaults to false because typically we will want\n                to let the transition select which part to use.\n                ',
                    tunable_type=bool,
                    default=False),
                    locked_args=locked_args), **kwargs)


class TimeoutLiability(Liability, HasTunableFactory):
    LIABILITY_TOKEN = 'TimeoutLiability'
    FACTORY_TUNABLES = {'description':'Establish a timeout for this affordance. If it has not run when the timeout hits, cancel and push timeout_affordance, if set.', 
     'timeout':TunableSimMinute(4, minimum=0, description='The time, in Sim minutes, after which the interaction is canceled and time_toute affordance is pushed, if set.'), 
     'timeout_affordance':TunableReference(manager=services.get_instance_manager(sims4.resources.Types.INTERACTION), allow_none=True,
       description='The affordance to push when the timeout expires. Can be unset, in which case the interaction will just be canceled.')}

    def __init__(self, interaction, *, timeout, timeout_affordance, **kwargs):
        (super().__init__)(**kwargs)

        def on_alarm(*_, **__):
            if interaction.running:
                return
            if interaction.transition is not None:
                if interaction.transition.running:
                    return
            if timeout_affordance is not None:
                context = interaction.context.clone_for_continuation(interaction)
                interaction.sim.push_super_affordance(timeout_affordance, interaction.target, context)
            interaction.cancel((FinishingType.LIABILITY), cancel_reason_msg=('Timeout after {} sim minutes.'.format(timeout)))

        time_span = clock.interval_in_sim_minutes(timeout)
        self._handle = alarms.add_alarm(self, time_span, on_alarm)

    def release(self):
        alarms.cancel_alarm(self._handle)

    def should_transfer(self, continuation):
        return False


class GameSpeedLiability(Liability, HasTunableFactory):
    LIABILITY_TOKEN = 'GameSpeedLiability'
    TIME_BETWEEN_CHECKS = 10
    FACTORY_TUNABLES = {'game_speed':TunableEnumEntry(description='\n            The speed to set the game. If Super Speed 3 is chosen, it will only\n            take effect if every Sim in the active household has also requested\n            Super Speed 3. When the interaction ends, the game speed will be\n            set back to whatever it was before the interaction ran. However,\n            when Super Speed 3 ends, the game will always go to Normal speed.\n            ',
       tunable_type=ClockSpeedMode,
       default=ClockSpeedMode.NORMAL), 
     'species_interaction_speed_requirements':TunableTuple(description='\n            Special behavior that will be pushes on Sims for a specific \n            species when super speed 3 is triggered.  \n            ',
       species_affordance_mapping=TunableMapping(description='\n                Mapping to allow for Sims of a specific species to not block\n                super speed 3 and instead, have an interaction pushed on them\n                when the super speed 3 request happens.\n                i.e. When a Sim goes to sleep, Dogs and Cats should go to sleep\n                too.\n                ',
       key_type=TunableEnumEntry(description='\n                    Species that will be pushed to run the specific affordance.\n                    ',
       tunable_type=Species,
       default=(Species.DOG),
       invalid_enums=(
      Species.INVALID,)),
       value_type=TunableReference(description='\n                    Affordance that will be pushed when a super speed 3 request\n                    happens and only Sims of the specified species are left \n                    on the lot.\n                    Affordance will be pushed on the Sim as a self interaction \n                    (same Sim as its target).\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       class_restrictions=('SuperInteraction', ),
       pack_safe=True)),
       speed_affordance_tags=TunableTags(description='\n                Interaction tags that interactions should have to not be \n                canceled by super speed 3 when pushing the affordance from\n                species_affordances_mapping.\n                ',
       filter_prefixes=('interaction', )),
       exempt_sim_buffs=TunableSet(description='\n                Set of buffs that will be added to the Sims that are considered\n                exempt from triggering SS3.  This buffs are usually autonomy\n                modifiers so they stop doing specific behaviors due the fact\n                that SS3 is triggered and these Sims may still try to do\n                something (like autonomy).\n                ',
       tunable=TunableReference(description='\n                    Buff that gets added to the Sim.\n                    ',
       manager=(services.get_instance_manager(Types.BUFF)),
       pack_safe=True)))}
    GLOBAL_EXEMPT_SIM_BUFFS = TunableSet(description='\n        Set of buffs that will be added to the Sims that are considered\n        exempt from triggering SS3.  This buffs are usually autonomy\n        modifiers so they stop doing specific behaviors due the fact\n        that SS3 is triggered and these Sims may still try to do\n        something (like autonomy).\n        ',
      tunable=TunableReference(description='\n            Buff that gets added to the Sim.\n            ',
      manager=(services.get_instance_manager(Types.BUFF)),
      pack_safe=True))
    GLOBAL_EXEMPT_SIM_TESTS = TunableTestSet(description='\n        Set of tests that, if passes (using single sim resolver), Sim will not\n        attempt to push SS3, but can have SS3 interactions (and buff) pushed on\n        them.\n        ')
    _ss3_requests = collections.defaultdict(set)

    def __init__(self, interaction, *, game_speed, species_interaction_speed_requirements, **kwargs):
        (super().__init__)(**kwargs)
        self.speed_request = None
        self._ss3_evaluate_timer = None
        self.new_game_speed = game_speed
        self.species_interaction_speed_requirements = species_interaction_speed_requirements
        self.special_case_sims = weakref.WeakKeyDictionary()
        self.situation_speed_request_data = {}

    def on_add(self, interaction):
        self.interaction = interaction

    def request_speed_change--- This code section failed: ---

 L. 340         0  LOAD_DEREF               'self'
                2  LOAD_ATTR                interaction
                4  LOAD_ATTR                sim
                6  STORE_FAST               'sim'

 L. 341         8  LOAD_DEREF               'self'
               10  LOAD_ATTR                new_game_speed
               12  LOAD_GLOBAL              ClockSpeedMode
               14  LOAD_ATTR                SUPER_SPEED3
               16  COMPARE_OP               ==
            18_20  POP_JUMP_IF_FALSE   266  'to 266'

 L. 342        22  LOAD_GLOBAL              services
               24  LOAD_METHOD              get_zone_situation_manager
               26  CALL_METHOD_0         0  '0 positional arguments'
               28  STORE_DEREF              'situation_manager'

 L. 344        30  LOAD_DEREF               'self'
               32  LOAD_ATTR                _ss3_requests
               34  LOAD_FAST                'sim'
               36  BINARY_SUBSCR    
               38  LOAD_METHOD              add
               40  LOAD_DEREF               'self'
               42  CALL_METHOD_1         1  '1 positional argument'
               44  POP_TOP          

 L. 345        46  LOAD_CONST               (None,)
               48  LOAD_CLOSURE             'self'
               50  LOAD_CLOSURE             'situation_manager'
               52  BUILD_TUPLE_2         2 
               54  LOAD_CODE                <code_object validity_check>
               56  LOAD_STR                 'GameSpeedLiability.request_speed_change.<locals>.validity_check'
               58  MAKE_FUNCTION_9          'default, closure'
               60  STORE_DEREF              'validity_check'

 L. 424        62  LOAD_DEREF               'self'
               64  LOAD_ATTR                interaction
               66  LOAD_METHOD              register_on_cancelled_callback
               68  LOAD_DEREF               'self'
               70  LOAD_ATTR                _remove_liability
               72  CALL_METHOD_1         1  '1 positional argument'
               74  POP_TOP          

 L. 427        76  SETUP_LOOP          130  'to 130'
               78  LOAD_GLOBAL              tuple
               80  LOAD_DEREF               'self'
               82  LOAD_ATTR                situation_speed_request_data
               84  LOAD_METHOD              values
               86  CALL_METHOD_0         0  '0 positional arguments'
               88  CALL_FUNCTION_1       1  '1 positional argument'
               90  GET_ITER         
               92  FOR_ITER            128  'to 128'
               94  UNPACK_SEQUENCE_3     3 
               96  STORE_FAST               'situation_id'
               98  STORE_FAST               'speed_request'
              100  STORE_FAST               'callback_fn'

 L. 428       102  LOAD_DEREF               'situation_manager'
              104  LOAD_METHOD              unregister_callback
              106  LOAD_FAST                'situation_id'
              108  LOAD_GLOBAL              SituationCallbackOption
              110  LOAD_ATTR                END_OF_SITUATION
              112  LOAD_FAST                'callback_fn'
              114  CALL_METHOD_3         3  '3 positional arguments'
              116  POP_TOP          

 L. 429       118  LOAD_DEREF               'self'
              120  LOAD_ATTR                situation_speed_request_data
              122  LOAD_FAST                'situation_id'
              124  DELETE_SUBSCR    
              126  JUMP_BACK            92  'to 92'
              128  POP_BLOCK        
            130_0  COME_FROM_LOOP       76  '76'

 L. 432       130  LOAD_CODE                <code_object situation_ended_callback>
              132  LOAD_STR                 'GameSpeedLiability.request_speed_change.<locals>.situation_ended_callback'
              134  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              136  STORE_FAST               'situation_ended_callback'

 L. 437       138  SETUP_LOOP          270  'to 270'
              140  LOAD_DEREF               'situation_manager'
              142  LOAD_METHOD              running_situations
              144  CALL_METHOD_0         0  '0 positional arguments'
              146  GET_ITER         
              148  FOR_ITER            262  'to 262'
              150  STORE_FAST               'situation'

 L. 439       152  LOAD_FAST                'situation'
              154  LOAD_ATTR                blocks_super_speed_three
              156  POP_JUMP_IF_TRUE    160  'to 160'

 L. 440       158  CONTINUE            148  'to 148'
            160_0  COME_FROM           156  '156'

 L. 442       160  LOAD_FAST                'situation'
              162  LOAD_ATTR                super_speed3_replacement_speed
              164  POP_JUMP_IF_TRUE    168  'to 168'

 L. 443       166  CONTINUE            148  'to 148'
            168_0  COME_FROM           164  '164'

 L. 445       168  LOAD_GLOBAL              services
              170  LOAD_METHOD              game_clock_service
              172  CALL_METHOD_0         0  '0 positional arguments'
              174  LOAD_ATTR                push_speed

 L. 446       176  LOAD_FAST                'situation'
              178  LOAD_ATTR                super_speed3_replacement_speed

 L. 447       180  LOAD_FAST                'situation'
              182  BUILD_TUPLE_1         1 
              184  LOAD_CLOSURE             'situation_manager'
              186  LOAD_CLOSURE             'validity_check'
              188  BUILD_TUPLE_2         2 
              190  LOAD_LAMBDA              '<code_object <lambda>>'
              192  LOAD_STR                 'GameSpeedLiability.request_speed_change.<locals>.<lambda>'
              194  MAKE_FUNCTION_9          'default, closure'

 L. 448       196  LOAD_STR                 'Situation alternate SS3 speed request'
              198  LOAD_CONST               ('validity_check', 'reason')
              200  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              202  STORE_FAST               'replacement_request'

 L. 450       204  LOAD_FAST                'situation'
              206  LOAD_ATTR                id
              208  STORE_FAST               'situation_id'

 L. 451       210  LOAD_GLOBAL              functools
              212  LOAD_ATTR                partial
              214  LOAD_FAST                'situation_ended_callback'

 L. 452       216  LOAD_FAST                'replacement_request'

 L. 453       218  LOAD_DEREF               'self'
              220  LOAD_ATTR                situation_speed_request_data
              222  LOAD_CONST               ('request', 'situation_speed_requests')
              224  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              226  STORE_FAST               'callback_fn'

 L. 455       228  LOAD_DEREF               'situation_manager'
              230  LOAD_METHOD              register_for_callback
              232  LOAD_FAST                'situation_id'

 L. 456       234  LOAD_GLOBAL              SituationCallbackOption
              236  LOAD_ATTR                END_OF_SITUATION

 L. 457       238  LOAD_FAST                'callback_fn'
              240  CALL_METHOD_3         3  '3 positional arguments'
              242  POP_TOP          

 L. 458       244  LOAD_FAST                'situation_id'
              246  LOAD_FAST                'replacement_request'
              248  LOAD_FAST                'callback_fn'
              250  BUILD_TUPLE_3         3 
              252  LOAD_DEREF               'self'
              254  LOAD_ATTR                situation_speed_request_data
              256  LOAD_FAST                'situation_id'
              258  STORE_SUBSCR     
              260  JUMP_BACK           148  'to 148'
              262  POP_BLOCK        
              264  JUMP_FORWARD        270  'to 270'
            266_0  COME_FROM            18  '18'

 L. 461       266  LOAD_CONST               None
              268  STORE_DEREF              'validity_check'
            270_0  COME_FROM           264  '264'
            270_1  COME_FROM_LOOP      138  '138'

 L. 462       270  LOAD_GLOBAL              services
              272  LOAD_METHOD              game_clock_service
              274  CALL_METHOD_0         0  '0 positional arguments'
              276  LOAD_ATTR                push_speed

 L. 463       278  LOAD_DEREF               'self'
              280  LOAD_ATTR                new_game_speed
              282  LOAD_DEREF               'validity_check'

 L. 464       284  LOAD_STR                 'SS3 interaction'
              286  LOAD_CONST               ('validity_check', 'reason')
              288  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              290  LOAD_DEREF               'self'
              292  STORE_ATTR               speed_request

Parse error at or near `MAKE_FUNCTION_9' instruction at offset 194

    def on_run(self):
        resolver = SingleSimResolver(self.interaction.sim.sim_info)
        if self.GLOBAL_EXEMPT_SIM_TESTS.run_tests(resolver):
            return
        if clock.GameClock.ignore_game_speed_requests:
            return
        self.request_speed_change()
        if self.new_game_speed == ClockSpeedMode.SUPER_SPEED3:
            if services.game_clock_service().clock_speed != ClockSpeedMode.SUPER_SPEED3:
                time_between_checks = create_time_span(minutes=(self.TIME_BETWEEN_CHECKS))
                self._ss3_evaluate_timer = alarms.add_alarm(self, time_between_checks, self._on_evaluate_timer_callback, True)

    def _on_evaluate_timer_callback(self, handle):
        clock = services.game_clock_service()
        if clock.clock_speed != ClockSpeedMode.SUPER_SPEED3:
            clock.remove_request(self.speed_request)
            self.request_speed_change()
        if clock.clock_speed == ClockSpeedMode.SUPER_SPEED3:
            handle.cancel()
            self._ss3_evaluate_timer = None

    def release(self):
        clock_service = services.game_clock_service()
        old_speed = clock_service.clock_speed
        sim = self.interaction.sim
        self._ss3_requests[sim].discard(self)
        if not self._ss3_requests[sim]:
            del self._ss3_requests[sim]
        if self.speed_request is not None:
            if not clock.GameClock.ignore_game_speed_requests:
                clock_service.remove_request(self.speed_request)
        situation_manager = services.get_zone_situation_manager()
        for situation_id, request, callback_fn in tuple(self.situation_speed_request_data.values()):
            services.game_clock_service().remove_request(request)
            situation_manager.unregister_callback(situation_id, SituationCallbackOption.END_OF_SITUATION, callback_fn)
            del self.situation_speed_request_data[situation_id]

        if old_speed == ClockSpeedMode.SUPER_SPEED3:
            if clock_service.clock_speed != ClockSpeedMode.SUPER_SPEED3:
                clock_service.set_clock_speed((ClockSpeedMode.NORMAL), reason='Exited SS3 interaction')
        if self._ss3_evaluate_timer is not None:
            self._ss3_evaluate_timer.cancel()
            self._ss3_evaluate_timer = None
        for affected_sim, run_affordance in self.special_case_sims.items():
            self._cancel_ss3_park_affordance(affected_sim, run_affordance)
            for buff in self.species_interaction_speed_requirements.exempt_sim_buffs:
                affected_sim.sim_info.remove_buff_by_type(buff.buff_type)

            for buff in self.GLOBAL_EXEMPT_SIM_BUFFS:
                affected_sim.sim_info.remove_buff_by_type(buff.buff_type)

    def _cancel_ss3_park_affordance--- This code section failed: ---

 L. 543         0  SETUP_LOOP          104  'to 104'
                2  LOAD_FAST                'affordance'
                4  LOAD_ATTR                affordance
                6  BUILD_SET_1           1 
                8  LOAD_FAST                'affordance'
               10  LOAD_ATTR                affordances
               12  BUILD_SET_UNPACK_2     2 
               14  GET_ITER         
               16  FOR_ITER            102  'to 102'
               18  STORE_FAST               'run_affordance'

 L. 544        20  LOAD_FAST                'affected_sim'
               22  LOAD_ATTR                si_state
               24  LOAD_METHOD              get_si_by_affordance
               26  LOAD_FAST                'run_affordance'
               28  CALL_METHOD_1         1  '1 positional argument'
               30  STORE_FAST               'si'

 L. 545        32  LOAD_FAST                'si'
               34  LOAD_CONST               None
               36  COMPARE_OP               is-not
               38  POP_JUMP_IF_FALSE    58  'to 58'

 L. 546        40  LOAD_FAST                'si'
               42  LOAD_ATTR                cancel
               44  LOAD_GLOBAL              FinishingType
               46  LOAD_ATTR                LIABILITY
               48  LOAD_STR                 'Game Speed Liability completed.'
               50  LOAD_CONST               ('cancel_reason_msg',)
               52  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
               54  POP_TOP          
               56  JUMP_BACK            16  'to 16'
             58_0  COME_FROM            38  '38'

 L. 549        58  SETUP_LOOP          100  'to 100'
               60  LOAD_FAST                'affected_sim'
               62  LOAD_ATTR                queue
               64  GET_ITER         
             66_0  COME_FROM            78  '78'
               66  FOR_ITER             98  'to 98'
               68  STORE_FAST               'interaction'

 L. 550        70  LOAD_FAST                'interaction'
               72  LOAD_ATTR                affordance
               74  LOAD_FAST                'run_affordance'
               76  COMPARE_OP               is
               78  POP_JUMP_IF_FALSE    66  'to 66'

 L. 551        80  LOAD_FAST                'interaction'
               82  LOAD_ATTR                cancel
               84  LOAD_GLOBAL              FinishingType
               86  LOAD_ATTR                LIABILITY
               88  LOAD_STR                 'Game Speed Liability completed.'
               90  LOAD_CONST               ('cancel_reason_msg',)
               92  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
               94  POP_TOP          
               96  JUMP_BACK            66  'to 66'
               98  POP_BLOCK        
            100_0  COME_FROM_LOOP       58  '58'
              100  JUMP_BACK            16  'to 16'
              102  POP_BLOCK        
            104_0  COME_FROM_LOOP        0  '0'

Parse error at or near `None' instruction at offset -1

    def merge(self, new_liability):
        if new_liability.interaction.sim is not self.interaction.sim:
            raise ValueError("Attempt to merge two different Sims' GameSpeedLiabilities.")
        if new_liability.__class__ != self.__class__:
            raise TypeError('Attempt to merge liabilities of different types.')
        self.new_game_speed = new_liability.new_game_speed
        return self

    def should_transfer(self, continuation):
        return False

    def _remove_liability(self, interaction):
        interaction.remove_liability(GameSpeedLiability.LIABILITY_TOKEN)

    def handle_special_case_sims(self):
        for sim, affordance in self.special_case_sims.items():
            already_pushed = False
            canceling_interactions = set()
            for si in sim.get_all_running_and_queued_interactions():
                if si.affordance.provided_posture_type is not None:
                    continue
                if si.affordance.interaction_category_tags & self.species_interaction_speed_requirements.speed_affordance_tags:
                    already_pushed = True
                else:
                    canceling_interactions.add(si)

            for si in canceling_interactions:
                si.cancel((FinishingType.LIABILITY), cancel_reason_msg='Super speed 3 SI cancelation.')

            if already_pushed:
                for buff in self.GLOBAL_EXEMPT_SIM_BUFFS:
                    if not sim.sim_info.has_buff(buff.buff_type):
                        sim.sim_info.add_buff(buff.buff_type)

                continue
            context = InteractionContext(sim, (InteractionContext.SOURCE_SCRIPT),
              (Priority.High),
              insert_strategy=(QueueInsertStrategy.NEXT))
            sim.push_super_affordance(affordance, sim, context)
            for buff in self.species_interaction_speed_requirements.exempt_sim_buffs:
                sim.sim_info.add_buff(buff.buff_type)

            for buff in self.GLOBAL_EXEMPT_SIM_BUFFS:
                sim.sim_info.add_buff(buff.buff_type)


class CriticalPriorityLiability(Liability, HasTunableFactory, AutoFactoryInit):
    LIABILITY_TOKEN = 'CriticalPriorityLiability'
    FACTORY_TUNABLES = {'priority_on_run':TunableEnumEntry(description='\n            The Priority you want to set the interactions priority to\n            when the interaction is run.\n            ',
       tunable_type=Priority,
       default=Priority.High), 
     'priority_on_push':TunableEnumEntry(description='\n            The Priority you want to set the interactions priority to\n            when the interaction is run.\n            ',
       tunable_type=Priority,
       default=Priority.Critical)}

    def __init__(self, interaction, *args, **kwargs):
        (super().__init__)(*args, **kwargs)

    def on_add(self, interaction):
        interaction.priority = self.priority_on_push
        interaction.run_priority = self.priority_on_run

    def transfer(self, interaction):
        interaction.priority = self.priority_on_push
        interaction.run_priority = self.priority_on_run


class SaveLockLiability(Liability, HasTunableFactory):
    LIABILITY_TOKEN = 'SaveLockLiability'
    FACTORY_TUNABLES = {'description':'\n            Prevent the user from saving or traveling while this interaction is\n            in the queue or running.\n            ', 
     'save_lock_tooltip':TunableLocalizedStringFactory(description='\n                The tooltip/message to show when the player tries to save the\n                game or return to the neighborhood view while the interaction\n                is running or in the queue.\n                '), 
     'should_transfer':Tunable(description='\n                If this liability should transfer to continuations.\n                ',
       tunable_type=bool,
       default=True)}

    def __init__(self, interaction, *, save_lock_tooltip, should_transfer, **kwargs):
        (super().__init__)(**kwargs)
        self._save_lock_tooltip = save_lock_tooltip
        self._should_transfer = should_transfer
        self._interaction = interaction
        self._is_save_locked = False

    def on_add(self, interaction):
        self._interaction = interaction
        if not self._is_save_locked:
            services.get_persistence_service().lock_save(self)
            self._is_save_locked = True

    def merge(self, interaction, key, new_liability):
        self.release()
        return super().merge(interaction, key, new_liability)

    def should_transfer(self, continuation):
        return self._should_transfer

    def release(self):
        services.get_persistence_service().unlock_save(self)

    def get_lock_save_reason(self):
        return self._interaction.create_localized_string(self._save_lock_tooltip)


class PushAffordanceOnRouteFailLiability(Liability, HasTunableFactory, AutoFactoryInit):
    LIABILITY_TOKEN = 'PushAffordanceOnRouteFailLiability'
    FACTORY_TUNABLES = {'actor':TunableEnumEntry(description='\n            The participant of this interaction that is going to have\n            the specified affordance pushed upon them.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'target':OptionalTunable(description="\n            If enabled, specify a participant to be used as the\n            interaction's target.\n            ",
       tunable=TunableEnumEntry(description="\n                The participant to be used as the interaction's\n                target.\n                ",
       tunable_type=ParticipantType,
       default=(ParticipantType.Object)),
       enabled_by_default=True), 
     'carry_target':OptionalTunable(description="\n            If enabled, specify a participant to be used as the\n            interaction's carry target.\n            If disabled carry_target will be set to None.\n            ",
       tunable=TunableEnumEntry(description="\n                The participant to be used as the interaction's\n                carry target.\n                ",
       tunable_type=ParticipantType,
       default=(ParticipantType.Object)),
       disabled_name='No_carry_target'), 
     'affordance':TunableReference(description='\n            When this interaction is cancelled because of route fail, this\n            interaction will be pushed.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION),
       class_restrictions=('SuperInteraction', )), 
     'push_affordance_on_reset':Tunable(description='\n            If set to True, affordances will be pushed after interaction is resetted.\n            ',
       tunable_type=bool,
       default=False), 
     'push_affordance_on_cancel':Tunable(description='\n            If set to True, affordances will be pushed after interaction is cancelled.\n            ',
       tunable_type=bool,
       default=False)}

    def __init__(self, interaction, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._interaction = interaction

    def on_add(self, interaction):
        self._interaction = interaction

    def transfer(self, interaction):
        self._interaction = interaction

    def release(self):
        if (self._interaction.transition_failed or self).push_affordance_on_cancel:
            if self._interaction.has_been_canceled:
                self._push_affordance()
        if self.push_affordance_on_reset:
            if self._interaction.has_been_reset:
                self._interaction.sim.on_start_up.append(self._push_affordance)
        super().release()

    def _push_affordance(self, *args, **kwargs):
        affordance_target = self._interaction.get_participant(self.target) if self.target is not None else None
        for actor in self._interaction.get_participants(self.actor):
            if actor is self._interaction.sim:
                context = self._interaction.context.clone_for_concurrent_context()
            else:
                context = self._interaction.context.clone_for_sim(actor)
            if self.carry_target is not None:
                context.carry_target = self._interaction.get_participants(self.carry_target)
            else:
                context.carry_target = None
            for aop in self.affordance.potential_interactions(affordance_target, context):
                aop.test_and_execute(context)

            start_up_callbacks = self._interaction.sim.on_start_up
            if self._push_affordance in start_up_callbacks:
                start_up_callbacks.remove(self._push_affordance)


def set_sim_sleeping(interaction, sequence=None):
    sim = interaction.sim

    def set_sleeping(_):
        sim.sleeping = True

    def set_awake(_):
        sim.sleeping = False

    return build_critical_section_with_finally(set_sleeping, sequence, set_awake)


class TunableSetSimSleeping(TunableFactory):
    FACTORY_TYPE = staticmethod(set_sim_sleeping)


class TunableSetClockSpeed(XevtTriggeredElement):
    FACTORY_TUNABLES = {'description':'Change the game clock speed as part of an interaction.', 
     'game_speed':TunableVariant(description='\n            The speed to set for the game. If you want to super speed 3, use a\n            GameSpeedLiability so that super speed 3 will be tied to the\n            lifetime of an interaction.\n            ',
       locked_args={'PAUSED':ClockSpeedMode.PAUSED, 
      'NORMAL':ClockSpeedMode.NORMAL, 
      'SPEED2':ClockSpeedMode.SPEED2, 
      'SPEED3':ClockSpeedMode.SPEED3},
       default='NORMAL')}

    def _do_behavior(self):
        if clock.GameClock.ignore_game_speed_requests:
            return
        services.game_clock_service().set_clock_speed(self.game_speed)


class ServiceNpcRequest(XevtTriggeredElement):
    MINUTES_ADD_TO_SERVICE_ARRIVAL = 5
    HIRE = 1
    CANCEL = 2
    FACTORY_TUNABLES = {'description':'\n        Request a service NPC as part of an interaction. Note for timing field:\n        Only beginning and end will work because xevents will trigger\n        immediately on the server for service requests\n        ', 
     'request_type':TunableVariant(description='\n                Specify the type of service NPC Request. You can hire, dismiss,\n                fire, or cancel a service npc.',
       hire=TunableTuple(description='\n                A reference to the tuned service npc instance that will be\n                requested at the specified time.',
       locked_args={'request_type': HIRE},
       service=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.SERVICE_NPC)))),
       cancel=TunableTuple(locked_args={'request_type': CANCEL}, service=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.SERVICE_NPC))),
       description='A reference to the tuned service that will be cancelled. This only really applies to recurring services where a cancelled service will never have any service npcs show up again until re-requested.'),
       default='hire'), 
     'notification':OptionalTunable(description='\n                When enabled, display a notification when the service npc is \n                successfully hired/cancelled.\n                If hired, last token is DateAndTime when service npc will\n                arrive. (usually this is 1)\n                ',
       tunable=NotificationElement.TunableFactory(locked_args={'timing': XevtTriggeredElement.LOCKED_AT_BEGINNING}))}

    def __init__(self, interaction, *args, request_type, notification, sequence=(), **kwargs):
        (super().__init__)(interaction, *args, request_type=request_type, notification=notification, sequence=sequence, **kwargs)
        self._request_type = request_type
        self.notification = notification
        self._household = interaction.sim.household
        self._hiring_sim_id = None if interaction.sim is None else interaction.sim.id
        self._service_npc_user_specified_data_id = None
        self._service_npc_user_specified_selections = None
        self._recurring = False
        (self._read_interaction_parameters)(**interaction.interaction_parameters)

    def _read_interaction_parameters(self, service_npc_user_specified_data_id=None, service_npc_recurring_request=False, service_npc_user_specified_selections=None, **kwargs):
        self._service_npc_user_specified_data_id = service_npc_user_specified_data_id
        self._service_npc_user_specified_selections = service_npc_user_specified_selections
        self._recurring = service_npc_recurring_request

    def _do_behavior(self):
        request_type = self._request_type.request_type
        service_npc = self._request_type.service
        if service_npc is None:
            return
            service_npc_service = services.current_zone().service_npc_service
            if request_type == self.HIRE:
                finishing_time = service_npc_service.request_service((self._household), service_npc,
                  user_specified_data_id=(self._service_npc_user_specified_data_id),
                  user_specified_selections=(self._service_npc_user_specified_selections),
                  hiring_sim_id=(self._hiring_sim_id),
                  is_recurring=(self._recurring))
                if self.notification is not None and finishing_time is not None:
                    finishing_time = finishing_time + create_time_span(minutes=(self.MINUTES_ADD_TO_SERVICE_ARRIVAL))
                    notification_element = self.notification(self.interaction)
                    notification_element.show_notification(additional_tokens=(finishing_time,))
        elif request_type == self.CANCEL:
            service_npc_service.cancel_service(self._household, service_npc)
            if self.notification is not None:
                notification_element = self.notification(self.interaction)
                notification_element._do_behavior()


class DoCommand(XevtTriggeredElement, HasTunableFactory):
    ARG_TYPE_PARTICIPANT = 0
    ARG_TYPE_LITERAL = 1
    ARG_TYPE_TAG = 3

    @staticmethod
    def _verify_tunable_callback(source, *_, command, **__):
        command_name = command.split(' ', 1)[0]
        command_restrictions = get_command_restrictions(command_name)
        command_type = get_command_type(command_name)
        if command_restrictions is None or command_type is None:
            logger.error('Command {} specified in {} does not exist.', command_name, source)
        else:
            if command_restrictions & CommandRestrictionFlags.RESTRICT_SAVE_UNLOCKED:
                if source.allow_while_save_locked:
                    logger.error('Command {} specified in {} is unavailable during save lock. The interaction should not be available during save lock either.', command_name, source)
            else:
                if command_type != CommandType.Live:
                    if not source.debug:
                        if not source.cheat:
                            logger.error('Command {} is {} command tuned on non-debug interaction {}. The command type should be CommandType.Live.', command_name, command_type, source)
                if command_type < CommandType.Cheat and source.cheat:
                    logger.error('Command {} is {} command tuned on cheat interaction {}. The command type should be CommandType.Cheat or above.', command_name, command_type, source)

    FACTORY_TUNABLES = {'command':Tunable(description='\n            The command to run.\n            ',
       tunable_type=str,
       default=None), 
     'arguments':TunableList(description="\n            The arguments for this command. Arguments will be added after the\n            command in the order they're listed here.\n            ",
       tunable=TunableVariant(description='\n                The argument to use. In most cases, the ID of the participant\n                will be used.\n                ',
       participant=TunableTuple(description='\n                    An argument that is a participant in the interaction. The\n                    ID will be used as the argument for the command.\n                    ',
       argument=TunableEnumEntry(description='\n                        The participant argument. The ID will be used in the\n                        command.\n                        ',
       tunable_type=ParticipantType,
       default=(ParticipantTypeSingle.Object)),
       locked_args={'arg_type': ARG_TYPE_PARTICIPANT}),
       string=TunableTuple(description="\n                    An argument that's a string.\n                    ",
       argument=Tunable(description='\n                        The string argument.\n                        ',
       tunable_type=str,
       default=None),
       locked_args={'arg_type': ARG_TYPE_LITERAL}),
       number=TunableTuple(description='\n                    An argument that is a number. This can be a float or an int.\n                    ',
       argument=Tunable(description='\n                        The number argument.\n                        ',
       tunable_type=float,
       default=0),
       locked_args={'arg_type': ARG_TYPE_LITERAL}),
       tag=TunableTuple(description='\n                    An argument that is a tag.\n                    ',
       argument=TunableTag(description='\n                        The tag argument.\n                        '),
       locked_args={'arg_type': ARG_TYPE_TAG}),
       boolean=TunableTuple(description='\n                    An argument that is a boolean.\n                    ',
       argument=Tunable(description='\n                        The number argument.\n                        ',
       tunable_type=bool,
       default=True),
       locked_args={'arg_type': ARG_TYPE_LITERAL}))), 
     'verify_tunable_callback':_verify_tunable_callback}

    def _do_behavior(self):
        full_command = self.command
        for arg in self.arguments:
            if arg.arg_type == self.ARG_TYPE_PARTICIPANT:
                for participant in self.interaction.get_participants(arg.argument):
                    if hasattr(participant, 'id'):
                        full_command += ' {}'.format(participant.id)
                    else:
                        full_command += ' {}'.format(participant)

            elif arg.arg_type == self.ARG_TYPE_LITERAL:
                full_command += ' {}'.format(arg.argument)
            elif arg.arg_type == self.ARG_TYPE_TAG:
                full_command += ' {}'.format(int(arg.argument))
            else:
                logger.error('Trying to run the Do Command element with an invalid arg type, {}.', (arg.arg_type), owner='trevor')
                return False

        client_id = services.client_manager().get_first_client_id()
        commands.execute(full_command, client_id)
        return True


class SetGoodbyeNotificationElement(XevtTriggeredElement):
    NEVER_USE_NOTIFICATION_NO_MATTER_WHAT = 'never_use_notification_no_matter_what'
    FACTORY_TUNABLES = {'description':'Set the notification that a Sim will display when they leave.', 
     'participant':TunableEnumEntry(description='\n            The participant of the interaction who will have their "goodbye"\n            notification set.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'goodbye_notification':TunableVariant(description='\n                The "goodbye" notification that will be set on this Sim. This\n                notification will be displayed when this Sim leaves the lot\n                (unless it gets overridden later).\n                ',
       notification=TunableUiDialogNotificationSnippet(),
       locked_args={'no_notification':None, 
      'never_use_notification_no_matter_what':NEVER_USE_NOTIFICATION_NO_MATTER_WHAT},
       default='no_notification'), 
     'only_set_if_notification_already_set':Tunable(description="\n                If the Sim doesn't have a goodbye notification already set and\n                this checkbox is checked, leave the goodbye notification unset.\n                ",
       tunable_type=bool,
       default=True)}

    def _do_behavior(self):
        participants = self.interaction.get_participants(self.participant)
        for participant in participants:
            if participant.sim_info.goodbye_notification is None:
                if self.only_set_if_notification_already_set:
                    continue
            participant.sim_info.try_to_set_goodbye_notification(self.goodbye_notification)