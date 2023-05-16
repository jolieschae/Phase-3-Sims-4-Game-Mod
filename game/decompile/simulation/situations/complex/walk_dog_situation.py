# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\walk_dog_situation.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 23276 bytes
import operator, random
from carry.carry_utils import get_carried_objects_gen
from event_testing.results import TestResult
from interactions.context import InteractionContext, QueueInsertStrategy
from interactions.interaction_finisher import FinishingType
from interactions.priority import Priority
from sims4.math import Threshold
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunablePackSafeReference, TunableInterval, TunableSimMinute, TunableRange, TunableTuple, TunableReference, Tunable, TunableList, TunableEnumWithFilter
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import classproperty
from situations.bouncer.bouncer_types import BouncerExclusivityCategory
from situations.situation import Situation
from situations.situation_complex import SituationComplexCommon, TunableSituationJobAndRoleState, CommonSituationState, CommonInteractionCompletedSituationState, SituationStateData, SituationState
from situations.situation_types import SituationCreationUIOption
from statistics.commodity import Commodity
from tag import TunableTags, Tag
import enum, interactions, services, sims4.log, sims4.math, situations, tag
logger = sims4.log.Logger('Situations', default_owner='rmccord')

class WalkDogProgress(enum.Int, export=False):
    WALK_DOG_NOT_STARTED = 0
    WALK_DOG_WALKING = ...
    WALK_DOG_FINISHING = ...
    WALK_DOG_DONE = ...


class WaitForSimJobs(SituationState):
    pass


class WalkState(CommonInteractionCompletedSituationState):
    FACTORY_TUNABLES = {'attractor_node_affordance':TunablePackSafeReference(description='\n            The affordance that the dog walker runs on the next attractor point\n            object.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION)), 
     'max_attempts':TunableRange(description='\n            The maximum number of attempts we will try to walk to a node before\n            walking to the next node.\n            ',
       tunable_type=int,
       default=3,
       minimum=1), 
     'time_between_attempts':TunableSimMinute(description='\n            The time in sim minutes between attempts to walk to the current\n            attractor point.\n            ',
       default=5)}
    RETRY_ALARM_NAME = 'retry_walk'

    def __init__(self, attractor_id, *args, attractor_node_affordance=None, max_attempts=1, time_between_attempts=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.attractor_node_affordance = attractor_node_affordance
        self.max_attempts = max_attempts
        self.time_between_attempts = time_between_attempts
        self._attractor_point = services.object_manager().get(attractor_id)
        self._attempts = 0
        self._walk_interaction = None

    def push_walk_affordance(self, alarm_handle):
        sim = self.owner.get_walker()
        if sim.has_any_interaction_running_or_queued_of_types((self.attractor_node_affordance,)):
            return
        for _, carry_posture, carry_target in get_carried_objects_gen(sim):
            if carry_target.transient and carry_posture.source_interaction.running:
                break
        else:
            return

        self._cancel_alarm(WalkState.RETRY_ALARM_NAME)
        self._attempts += 1
        if self._attempts > self.max_attempts:
            self.owner.walk_onward()
            return
        context = InteractionContext(sim, (InteractionContext.SOURCE_SCRIPT),
          (Priority.High),
          run_priority=(Priority.Low),
          insert_strategy=(QueueInsertStrategy.NEXT))
        walk_aop = interactions.aop.AffordanceObjectPair(self.attractor_node_affordance, self._attractor_point, self.attractor_node_affordance, None)
        test_result = walk_aop.test(context)
        if test_result:
            execute_result = walk_aop.execute(context)
            if execute_result:
                self._walk_interaction = execute_result[1]
        self._create_or_load_alarm((WalkState.RETRY_ALARM_NAME), (self.time_between_attempts), (self.push_walk_affordance), repeating=True)

    def on_activate(self, reader=None):
        super().on_activate(reader=reader)
        if self._attractor_point is None:
            self.owner.walk_onward()
            return
        self.push_walk_affordance(None)
        self._create_or_load_alarm((WalkState.RETRY_ALARM_NAME), 1, (self.push_walk_affordance), repeating=True)

    def on_deactivate(self):
        self._cancel_alarm(WalkState.RETRY_ALARM_NAME)
        if self._walk_interaction is not None:
            self._walk_interaction.cancel(FinishingType.SITUATIONS, "Walk Dog Situation Ended. Don't continue to walk.")
            self._walk_interaction = None
        super().on_deactivate()

    def _additional_tests(self, sim_info, event, resolver):
        return sim_info.id == self.owner.get_walker().id

    def _on_interaction_of_interest_complete(self, **kwargs):
        self._walk_interaction = None
        self.owner.wait_around(self._attractor_point)


class WaitAroundState(CommonSituationState):
    FACTORY_TUNABLES = {'wait_stat_and_value': TunableTuple(description='\n            The stat and initial value on the dog that decides when we should\n            walk to the next node in the situation. The timer for this state is\n            a fallback if the Sim and dog end up taking too long.\n            ',
                              stat=Commodity.TunableReference(description='\n                The stat we track on the Dog, to notify us when the Sim should attempt to walk\n                to the next attractor point.\n                \n                When the stat reaches its convergence value, we enter the walk state.\n                '),
                              initial_value=Tunable(description='\n                The initial value we should set on the Dog to decide when they should walk again. \n                ',
                              tunable_type=float,
                              default=5))}

    def __init__(self, *args, wait_stat_and_value=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.wait_stat_and_value = wait_stat_and_value
        self.wait_listener = None

    def on_activate(self, reader=None):
        super().on_activate(reader=reader)
        pet = self.owner.get_pet()
        wait_stat = pet.commodity_tracker.get_statistic((self.wait_stat_and_value.stat), add=True)
        wait_stat.set_value(self.wait_stat_and_value.initial_value)
        op = operator.le if wait_stat.get_decay_rate() <= 0 else operator.ge
        threshold = Threshold(wait_stat.convergence_value, op)
        if threshold.compare(wait_stat.get_value()):
            self.on_wait_stat_zero(wait_stat)
        else:
            self.wait_listener = wait_stat.create_and_add_callback_listener(threshold, self.on_wait_stat_zero)

    def remove_wait_listener(self):
        pet = self.owner.get_pet()
        if pet is not None:
            if self.wait_listener is not None:
                pet.commodity_tracker.remove_listener(self.wait_listener)
            pet.commodity_tracker.remove_statistic(self.wait_stat_and_value.stat)
        self.wait_listener = None

    def on_deactivate(self):
        self.remove_wait_listener()
        super().on_deactivate()

    def on_wait_stat_zero(self, stat):
        self.remove_wait_listener()
        self.owner.walk_onward()

    def timer_expired(self):
        self.owner.walk_onward()


class FinishWalkState(CommonInteractionCompletedSituationState):
    FACTORY_TUNABLES = {'go_home_affordance': TunableReference(description='\n            The affordance that the dog walker runs to go home.\n            ',
                             manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)))}

    def __init__(self, *args, go_home_affordance=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.go_home_affordance = go_home_affordance

    def on_activate(self, reader=None):
        super().on_activate(reader=reader)
        walker = self.owner.get_walker()
        if not (walker is None or walker.sim_info.lives_here):
            self.owner.walk_onward()
        context = InteractionContext(walker, (InteractionContext.SOURCE_SCRIPT), (Priority.High), insert_strategy=(QueueInsertStrategy.NEXT))
        aop = interactions.aop.AffordanceObjectPair(self.go_home_affordance, walker, self.go_home_affordance, None)
        aop.test_and_execute(context)

    def _additional_tests(self, sim_info, event, resolver):
        walker = self.owner.get_walker()
        return walker is None or sim_info.id == walker.id or False
        return True

    def _on_interaction_of_interest_complete(self, **kwargs):
        self.owner.walk_onward()

    def timer_expired(self):
        self.owner.walk_onward()


class WalkDogSituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'walker_job_and_role_state':TunableSituationJobAndRoleState(description='\n            Job and Role State for the Sim walking the dog. Pre-populated as\n            the actor of the Situation.\n            '), 
     'dog_job_and_role_state':TunableSituationJobAndRoleState(description='\n            Job and Role State for the dog being walked. Pre-populated as the\n            target of the Situation.\n            '), 
     'walk_nodes':TunableInterval(description='\n            How many nodes in the world we want to traverse for our walk.\n            Currently this will only affect fallback attractor points. We will\n            try to use ALL of the attractor points returned by search tags.\n            ',
       tunable_type=int,
       default_lower=5,
       default_upper=6,
       minimum=1), 
     'finish_walk_state':FinishWalkState.TunableFactory(tuning_group=GroupNames.STATE), 
     'walk_state':WalkState.TunableFactory(tuning_group=GroupNames.STATE), 
     'wait_around_state':WaitAroundState.TunableFactory(tuning_group=GroupNames.STATE), 
     'attractor_point_tags':TunableTuple(description='\n            Tags that are used to select objects and attractor points for our\n            path.\n            ',
       fallback_tags=TunableTags(description="\n                Tags to use if we don't find any objects with the search tags.\n                This is primarily so we can have a separate list for pre-\n                patched worlds where there are no hand-placed attractor points.\n                ",
       filter_prefixes=('AtPo', ),
       minlength=1),
       search_tags=TunableList(description="\n                A list of path tags to look for in order. This will search for\n                objects with each tag, find the closest object, and use it's\n                matching tag to find others for a full path. \n                \n                Example: Short_1, Short_2 are in the list. We would search for \n                all objects with either of those tags, and grab the closest \n                one. If the object has Short_1 tag on it, we find all objects \n                with Short_1 to create our path.\n                ",
       tunable=TunableEnumWithFilter(description='\n                    A set of attractor point tags we use to pull objects from when\n                    searching for attractor points to create a walking path from.\n                    ',
       tunable_type=Tag,
       default=(Tag.INVALID),
       invalid_enums=(
      Tag.INVALID,),
       filter_prefixes=('AtPo', )),
       unique_entries=True))}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classmethod
    def _verify_tuning_callback(cls):
        super()._verify_tuning_callback()
        if cls.attractor_point_tags.fallback_tags.issubset(cls.attractor_point_tags.search_tags):
            logger.error('Walk Dog Situation {} fallback tags are a subset of search tags. You need at least one tag to be different in fallback tags.', cls)

    @classmethod
    def _states(cls):
        return (SituationStateData(0, WalkState),
         SituationStateData(1, WaitAroundState),
         SituationStateData(2, FinishWalkState))

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.walker_job_and_role_state.job, cls.walker_job_and_role_state.role_state),
         (
          cls.dog_job_and_role_state.job, cls.dog_job_and_role_state.role_state)]

    @classmethod
    def default_job(cls):
        pass

    @classmethod
    def get_prepopulated_job_for_sims(cls, sim, target_sim_id=None):
        prepopulate = [(sim.id, cls.walker_job_and_role_state.job.guid64)]
        if target_sim_id is not None:
            prepopulate.append((target_sim_id, cls.dog_job_and_role_state.job.guid64))
        return prepopulate

    @classmethod
    def has_walk_nodes(cls):
        object_manager = services.object_manager()
        found_objects = object_manager.get_objects_matching_tags((set(cls.attractor_point_tags.search_tags) | cls.attractor_point_tags.fallback_tags), match_any=True)
        if found_objects:
            return True
        return False

    @classmethod
    def get_walk_nodes(cls):
        object_manager = services.object_manager()

        def get_objects(tag_set):
            found_objects = set()
            for tag in tag_set:
                found_objects.update(object_manager.get_objects_matching_tags({tag}))

            return found_objects

        attractor_objects = get_objects(cls.attractor_point_tags.search_tags)
        if not attractor_objects:
            return (get_objects(cls.attractor_point_tags.fallback_tags), True)
        return (
         attractor_objects, False)

    @classmethod
    def is_situation_available(cls, *args, **kwargs):
        result = cls.has_walk_nodes()
        if not result:
            return TestResult(False, 'Not enough attractor points to walk the dog.')
        return (super().is_situation_available)(*args, **kwargs)

    @classproperty
    def situation_serialization_option(cls):
        return situations.situation_types.SituationSerializationOption.DONT

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._walker = None
        self._dog = None
        self._path_index = 0
        self._path_obj_ids = []
        self.walk_dog_progress = WalkDogProgress.WALK_DOG_NOT_STARTED

    def _on_remove_sim_from_situation(self, sim):
        if sim is self.get_walker() or sim is self.get_pet():
            self._self_destruct()
        super()._on_remove_sim_from_situation

    def _on_add_sim_to_situation(self, *args, **kwargs):
        (super()._on_add_sim_to_situation)(*args, **kwargs)
        if self.get_walker() is not None:
            if self.get_pet() is not None:
                self._build_walking_path()
                if not self._path_obj_ids:
                    self._self_destruct()
                    return
                self.walk_onward()

    def get_walker(self):
        if self._walker is None:
            self._walker = next(iter(self.all_sims_in_job_gen(self.walker_job_and_role_state.job)), None)
        return self._walker

    def get_pet(self):
        if self._dog is None:
            self._dog = next(iter(self.all_sims_in_job_gen(self.dog_job_and_role_state.job)), None)
        return self._dog

    def _build_walking_path--- This code section failed: ---

 L. 468         0  LOAD_FAST                'self'
                2  LOAD_METHOD              get_walk_nodes
                4  CALL_METHOD_0         0  '0 positional arguments'
                6  UNPACK_SEQUENCE_2     2 
                8  STORE_FAST               'attractor_objects'
               10  STORE_FAST               'is_fallback'

 L. 469        12  LOAD_FAST                'attractor_objects'
               14  POP_JUMP_IF_TRUE     32  'to 32'

 L. 470        16  LOAD_GLOBAL              logger
               18  LOAD_METHOD              warn
               20  LOAD_STR                 'Could not build a path for {}'
               22  LOAD_FAST                'self'
               24  CALL_METHOD_2         2  '2 positional arguments'
               26  POP_TOP          

 L. 471        28  LOAD_CONST               None
               30  RETURN_VALUE     
             32_0  COME_FROM            14  '14'

 L. 473        32  LOAD_FAST                'self'
               34  LOAD_METHOD              get_walker
               36  CALL_METHOD_0         0  '0 positional arguments'
               38  JUMP_IF_TRUE_OR_POP    46  'to 46'
               40  LOAD_FAST                'self'
               42  LOAD_METHOD              get_pet
               44  CALL_METHOD_0         0  '0 positional arguments'
             46_0  COME_FROM            38  '38'
               46  STORE_FAST               'sim'

 L. 475        48  LOAD_FAST                'sim'
               50  LOAD_ATTR                position
               52  STORE_DEREF              'sim_position'

 L. 476        54  LOAD_LISTCOMP            '<code_object <listcomp>>'
               56  LOAD_STR                 'WalkDogSituation._build_walking_path.<locals>.<listcomp>'
               58  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
               60  LOAD_FAST                'attractor_objects'
               62  GET_ITER         
               64  CALL_FUNCTION_1       1  '1 positional argument'
               66  STORE_FAST               'all_obj_and_pos_list'

 L. 477        68  LOAD_GLOBAL              min
               70  LOAD_FAST                'all_obj_and_pos_list'
               72  LOAD_CLOSURE             'sim_position'
               74  BUILD_TUPLE_1         1 
               76  LOAD_LAMBDA              '<code_object <lambda>>'
               78  LOAD_STR                 'WalkDogSituation._build_walking_path.<locals>.<lambda>'
               80  MAKE_FUNCTION_8          'closure'
               82  LOAD_CONST               ('key',)
               84  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
               86  LOAD_CONST               0
               88  BINARY_SUBSCR    
               90  STORE_FAST               'min_dist_obj'

 L. 479        92  BUILD_LIST_0          0 
               94  STORE_FAST               'obj_and_pos_list'

 L. 481        96  LOAD_FAST                'is_fallback'
               98  POP_JUMP_IF_TRUE    170  'to 170'

 L. 483       100  LOAD_FAST                'min_dist_obj'
              102  LOAD_METHOD              get_tags
              104  CALL_METHOD_0         0  '0 positional arguments'
              106  STORE_DEREF              'tags'

 L. 484       108  LOAD_CLOSURE             'tags'
              110  BUILD_TUPLE_1         1 
              112  LOAD_SETCOMP             '<code_object <setcomp>>'
              114  LOAD_STR                 'WalkDogSituation._build_walking_path.<locals>.<setcomp>'
              116  MAKE_FUNCTION_8          'closure'
              118  LOAD_FAST                'self'
              120  LOAD_ATTR                attractor_point_tags
              122  LOAD_ATTR                search_tags
              124  GET_ITER         
              126  CALL_FUNCTION_1       1  '1 positional argument'
              128  STORE_FAST               'matching_tags'

 L. 485       130  SETUP_LOOP          174  'to 174'
              132  LOAD_FAST                'all_obj_and_pos_list'
              134  GET_ITER         
            136_0  COME_FROM           152  '152'
              136  FOR_ITER            166  'to 166'
              138  STORE_FAST               'obj_pos'

 L. 486       140  LOAD_FAST                'obj_pos'
              142  LOAD_CONST               0
              144  BINARY_SUBSCR    
              146  LOAD_METHOD              has_any_tag
              148  LOAD_FAST                'matching_tags'
              150  CALL_METHOD_1         1  '1 positional argument'
              152  POP_JUMP_IF_FALSE   136  'to 136'

 L. 487       154  LOAD_FAST                'obj_and_pos_list'
              156  LOAD_METHOD              append
              158  LOAD_FAST                'obj_pos'
              160  CALL_METHOD_1         1  '1 positional argument'
              162  POP_TOP          
              164  JUMP_BACK           136  'to 136'
              166  POP_BLOCK        
              168  JUMP_FORWARD        174  'to 174'
            170_0  COME_FROM            98  '98'

 L. 489       170  LOAD_FAST                'all_obj_and_pos_list'
              172  STORE_FAST               'obj_and_pos_list'
            174_0  COME_FROM           168  '168'
            174_1  COME_FROM_LOOP      130  '130'

 L. 492       174  LOAD_LISTCOMP            '<code_object <listcomp>>'
              176  LOAD_STR                 'WalkDogSituation._build_walking_path.<locals>.<listcomp>'
              178  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              180  LOAD_FAST                'obj_and_pos_list'
              182  GET_ITER         
              184  CALL_FUNCTION_1       1  '1 positional argument'
              186  STORE_FAST               'positions'

 L. 493       188  LOAD_GLOBAL              sum
              190  LOAD_FAST                'positions'
              192  LOAD_GLOBAL              sims4
              194  LOAD_ATTR                math
              196  LOAD_ATTR                Vector3
              198  LOAD_METHOD              ZERO
              200  CALL_METHOD_0         0  '0 positional arguments'
              202  CALL_FUNCTION_2       2  '2 positional arguments'
              204  LOAD_GLOBAL              len
              206  LOAD_FAST                'positions'
              208  CALL_FUNCTION_1       1  '1 positional argument'
              210  BINARY_TRUE_DIVIDE
              212  STORE_DEREF              'center'

 L. 494       214  LOAD_FAST                'obj_and_pos_list'
              216  LOAD_ATTR                sort
              218  LOAD_CLOSURE             'center'
              220  BUILD_TUPLE_1         1 
              222  LOAD_LAMBDA              '<code_object <lambda>>'
              224  LOAD_STR                 'WalkDogSituation._build_walking_path.<locals>.<lambda>'
              226  MAKE_FUNCTION_8          'closure'
              228  LOAD_CONST               True
              230  LOAD_CONST               ('key', 'reverse')
              232  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              234  POP_TOP          

 L. 497       236  LOAD_CONST               0
              238  STORE_FAST               'start_index'

 L. 498       240  SETUP_LOOP          278  'to 278'
              242  LOAD_FAST                'obj_and_pos_list'
              244  GET_ITER         
              246  FOR_ITER            276  'to 276'
              248  UNPACK_SEQUENCE_2     2 
              250  STORE_FAST               'obj'
              252  STORE_FAST               '_'

 L. 499       254  LOAD_FAST                'obj'
              256  LOAD_FAST                'min_dist_obj'
              258  COMPARE_OP               is
          260_262  POP_JUMP_IF_FALSE   266  'to 266'

 L. 500       264  BREAK_LOOP       
            266_0  COME_FROM           260  '260'

 L. 501       266  LOAD_FAST                'start_index'
              268  LOAD_CONST               1
              270  INPLACE_ADD      
              272  STORE_FAST               'start_index'
              274  JUMP_BACK           246  'to 246'
              276  POP_BLOCK        
            278_0  COME_FROM_LOOP      240  '240'

 L. 503       278  LOAD_FAST                'is_fallback'
          280_282  POP_JUMP_IF_TRUE    294  'to 294'

 L. 504       284  LOAD_GLOBAL              len
              286  LOAD_FAST                'obj_and_pos_list'
              288  CALL_FUNCTION_1       1  '1 positional argument'
              290  STORE_FAST               'num_nodes'
              292  JUMP_FORWARD        342  'to 342'
            294_0  COME_FROM           280  '280'

 L. 505       294  LOAD_FAST                'self'
              296  LOAD_ATTR                walk_nodes
              298  LOAD_ATTR                lower_bound
              300  LOAD_FAST                'self'
              302  LOAD_ATTR                walk_nodes
              304  LOAD_ATTR                upper_bound
              306  COMPARE_OP               ==
          308_310  POP_JUMP_IF_FALSE   322  'to 322'

 L. 506       312  LOAD_FAST                'self'
              314  LOAD_ATTR                walk_nodes
              316  LOAD_ATTR                lower_bound
              318  STORE_FAST               'num_nodes'
              320  JUMP_FORWARD        342  'to 342'
            322_0  COME_FROM           308  '308'

 L. 508       322  LOAD_GLOBAL              random
              324  LOAD_METHOD              randrange
              326  LOAD_FAST                'self'
              328  LOAD_ATTR                walk_nodes
              330  LOAD_ATTR                lower_bound
              332  LOAD_FAST                'self'
              334  LOAD_ATTR                walk_nodes
              336  LOAD_ATTR                upper_bound
              338  CALL_METHOD_2         2  '2 positional arguments'
              340  STORE_FAST               'num_nodes'
            342_0  COME_FROM           320  '320'
            342_1  COME_FROM           292  '292'

 L. 510       342  LOAD_GLOBAL              random
              344  LOAD_METHOD              randint
              346  LOAD_CONST               2
              348  LOAD_CONST               4
              350  CALL_METHOD_2         2  '2 positional arguments'
              352  LOAD_CONST               2
              354  BINARY_MODULO    
          356_358  POP_JUMP_IF_FALSE   364  'to 364'
              360  LOAD_CONST               1
              362  JUMP_FORWARD        366  'to 366'
            364_0  COME_FROM           356  '356'
              364  LOAD_CONST               -1
            366_0  COME_FROM           362  '362'
              366  STORE_FAST               'clockwise'

 L. 511       368  LOAD_FAST                'start_index'
              370  STORE_FAST               'index'

 L. 512       372  SETUP_LOOP          468  'to 468'
              374  LOAD_GLOBAL              range
              376  LOAD_FAST                'num_nodes'
              378  CALL_FUNCTION_1       1  '1 positional argument'
              380  GET_ITER         
              382  FOR_ITER            466  'to 466'
              384  STORE_FAST               '_'

 L. 514       386  LOAD_FAST                'index'
              388  LOAD_GLOBAL              len
              390  LOAD_FAST                'obj_and_pos_list'
              392  CALL_FUNCTION_1       1  '1 positional argument'
              394  COMPARE_OP               >=
          396_398  POP_JUMP_IF_FALSE   406  'to 406'

 L. 515       400  LOAD_CONST               0
              402  STORE_FAST               'index'
              404  JUMP_FORWARD        428  'to 428'
            406_0  COME_FROM           396  '396'

 L. 516       406  LOAD_FAST                'index'
              408  LOAD_CONST               0
              410  COMPARE_OP               <
          412_414  POP_JUMP_IF_FALSE   428  'to 428'

 L. 517       416  LOAD_GLOBAL              len
              418  LOAD_FAST                'obj_and_pos_list'
              420  CALL_FUNCTION_1       1  '1 positional argument'
              422  LOAD_CONST               1
              424  BINARY_SUBTRACT  
              426  STORE_FAST               'index'
            428_0  COME_FROM           412  '412'
            428_1  COME_FROM           404  '404'

 L. 518       428  LOAD_FAST                'obj_and_pos_list'
              430  LOAD_FAST                'index'
              432  BINARY_SUBSCR    
              434  UNPACK_SEQUENCE_2     2 
              436  STORE_FAST               'node'
              438  STORE_FAST               '_'

 L. 519       440  LOAD_FAST                'self'
              442  LOAD_ATTR                _path_obj_ids
              444  LOAD_METHOD              append
              446  LOAD_FAST                'node'
              448  LOAD_ATTR                id
              450  CALL_METHOD_1         1  '1 positional argument'
              452  POP_TOP          

 L. 520       454  LOAD_FAST                'index'
              456  LOAD_FAST                'clockwise'
              458  INPLACE_ADD      
              460  STORE_FAST               'index'
          462_464  JUMP_BACK           382  'to 382'
              466  POP_BLOCK        
            468_0  COME_FROM_LOOP      372  '372'

 L. 523       468  LOAD_FAST                'self'
              470  LOAD_ATTR                _path_obj_ids
              472  LOAD_CONST               -1
              474  BINARY_SUBSCR    
              476  LOAD_FAST                'min_dist_obj'
              478  LOAD_ATTR                id
              480  COMPARE_OP               !=
          482_484  POP_JUMP_IF_FALSE   500  'to 500'

 L. 524       486  LOAD_FAST                'self'
              488  LOAD_ATTR                _path_obj_ids
              490  LOAD_METHOD              append
              492  LOAD_FAST                'min_dist_obj'
              494  LOAD_ATTR                id
              496  CALL_METHOD_1         1  '1 positional argument'
              498  POP_TOP          
            500_0  COME_FROM           482  '482'

Parse error at or near `LOAD_SETCOMP' instruction at offset 112

    def walk_onward(self):
        if self._path_index < len(self._path_obj_ids):
            self.walk_dog_progress = WalkDogProgress.WALK_DOG_WALKING
            self._change_state(self.walk_state(self._path_obj_ids[self._path_index]))
            self._path_index += 1
            return
        if self.walk_dog_progress == WalkDogProgress.WALK_DOG_WALKING:
            self.walk_dog_progress = WalkDogProgress.WALK_DOG_FINISHING
            self._change_state(self.finish_walk_state())
            return
        if self.walk_dog_progress >= WalkDogProgress.WALK_DOG_FINISHING:
            self.walk_dog_progress = WalkDogProgress.WALK_DOG_DONE
            self._self_destruct()
            return

    def wait_around(self, attractor_point):
        self._change_state(self.wait_around_state())


lock_instance_tunables(WalkDogSituation, exclusivity=(BouncerExclusivityCategory.NEUTRAL),
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  _implies_greeted_status=False)