# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_service.py
# Compiled at: 2022-04-20 20:37:17
# Size of source mod 2**32: 35664 bytes
from collections import defaultdict
import enum, random
from date_and_time import TimeSpan, create_time_span
from elements import SleepElement, GeneratorElement
from gsi_handlers.story_progression_handlers import is_story_progression_pass_archive_enabled, GSIStoryProgressionPassData, archive_story_progression_pass_data, GSIStoryProgressionArcData
from interactions.utils.death import DeathType
from scheduling import Timeline
from sims4.localization import TunableLocalizedStringFactoryVariant
from sims4.resources import Types
from sims4.service_manager import Service
from sims4.tuning.tunable import TunableList, TunableRealSecond, TunableTuple, TunableReference, TunableRange, TunableEnumEntry, TunableVariant, TunablePercent, TunableInterval, Tunable, TunableMapping
from sims4.utils import classproperty
from story_progression import StoryProgressionFlags, StoryProgressionArcSeedReason, story_progression_telemetry
from story_progression.actions import TunableStoryProgressionActionVariant
import alarms, clock, persistence_error_types, services, sims, sims4.random, sims4.log, zone_types
from story_progression.story_progression_demographics import SimTestDemographicFunction, TotalSimDemographicFunction, ResidentialLotDemographicFunction
from story_progression.story_progression_enums import StoryType
from story_progression.story_progression_result import StoryProgressionResult, StoryProgressionResultType
from story_progression.story_progression_rule_set import StoryProgressionRuleSet
from story_progression.story_progression_log import log_story_progression_demographics
from story_progression.story_progression_tuning import StoryProgTunables
from tunable_time import TunableTimeOfDay, TunableTimeSpan
logger = sims4.log.Logger('StoryProgression')

class StoryProgressionPassType(enum.Int):
    GLOBAL = 0
    PER_WORLD = 1


class StoryProgressionService(Service):
    INTERVAL = TunableRealSecond(description='\n        The time between Story Progression actions. A lower number will\n        impact performance.\n        ',
      default=5)
    ACTIONS = TunableList(description='\n        A list of actions that are available to Story Progression.\n        ',
      tunable=(TunableStoryProgressionActionVariant()))
    FEATURE_KEY = 14347699396486965923

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, value):
        for pass_data in value:
            previous_value = None
            for demographic_data in pass_data.demographic_data:
                if previous_value is not None:
                    if previous_value >= demographic_data.maximum_range:
                        logger.error('Maximum range values in demographic data within pass {} must be in increasing order: {} > {}', pass_data.debug_pass_name, previous_value * 100, demographic_data.maximum_range * 100)
                        break
                previous_value = demographic_data.maximum_range
            else:
                if previous_value < 1:
                    logger.error('Maximum range value within pass {} does not reach 100.  This means there is a hole in the data that must be filled.', pass_data.debug_pass_name)

    STORY_PROGRESSION_PASSES = TunableList(description='\n        A list of the different Story Progression Passes that\n        are used to attempt to seed new Story Arcs upon Sims.\n        ',
      tunable=TunableTuple(description='\n            Data related to a single Story Progression Pass.\n            ',
      pass_type=TunableEnumEntry(description='\n                The different type of pass this is.\n                GLOBAL: This pass will run a single time and interact\n                with Sims/Households/Lots across the entire game.\n                PER_WORLD: This pass will run multiple times, once\n                per world and only interact with Sims/Households/Lots on\n                that world.\n                ',
      tunable_type=StoryProgressionPassType,
      default=(StoryProgressionPassType.GLOBAL)),
      potential_arcs=TunableList(description='\n                A weighted list of the potential story arcs\n                to try and seed.\n                ',
      tunable=TunableTuple(description='\n                    A pair of a potential story arc and the\n                    weight of that story arc being selected.\n                    ',
      story_arc=TunableReference(description='\n                        The story arc that might be chosen.\n                        ',
      manager=(services.get_instance_manager(Types.STORY_ARC)),
      pack_safe=True),
      weight=TunableRange(description='\n                        The chance that this story arc will be chosen.\n                        ',
      tunable_type=int,
      default=1,
      minimum=1))),
      demographic_function=TunableVariant(description='\n                The different demographic function that we will use in order to\n                determine the chance of one of these arcs being seeded.\n                \n                Each of these functions will return a percentage of sims/households/lots\n                that fit the question out of a total.  This percentage is then used with\n                the demographic data to determine exactly what to do.\n                ',
      sim_test=(SimTestDemographicFunction.TunableFactory()),
      total_sim=(TotalSimDemographicFunction.TunableFactory()),
      residential_lot=(ResidentialLotDemographicFunction.TunableFactory()),
      default='sim_test'),
      demographic_data=TunableList(description='\n                A grouping of the different instructions of what this pass should do at\n                every demographic value given by the demographic function.\n                ',
      tunable=TunableTuple(description='\n                    A group of demographic data.  Each set of demographic data should have a maximum range\n                    higher than the previous one.\n                    ',
      maximum_range=TunablePercent(description='\n                        The maximum value of this range of demographic data within the pass tuning.\n                        Each maximum range should be larger than the one before it in order to create\n                        the ranges where each set of demographic data is used.  The demographic function\n                        ends up returning a percentage which we then use these values to determine which\n                        data set we want to use based on that percentage.\n                        ',
      default=100),
      chance_of_occurrence=TunablePercent(description='\n                        The chance that we attempt to seed an arc at all during this pass\n                        at this demographic level.\n                        ',
      default=100),
      number_to_seed=TunableInterval(description='\n                        The number of arcs to seed.  A random value between min and max will be chosen\n                        as the number we will seed.\n                        ',
      tunable_type=int,
      default_lower=1,
      default_upper=3,
      minimum=0))),
      debug_pass_name=Tunable(description='\n                Name of this pass for use within logs and the GSI for easier debugging.\n                ',
      tunable_type=str,
      default='')),
      verify_tunable_callback=_verify_tunable_callback)
    UPDATE_TIME = TunableTimeOfDay(description='\n        The time of day that the story progression service\n        will seed new arcs and update the existing ones.\n        ')

    def __init__(self):
        self._alarm_handle = None
        self._next_action_index = 0
        self._story_progression_flags = StoryProgressionFlags.DISABLED
        self._demographics = None
        self._timeline = None
        self._timeline_update = None
        self._timeline_multiplier = 1
        self._update_story_progression_element = None
        self._sim_story_progression_trackers = set()
        self._historical_sim_story_progression_trackers = set()
        self._household_story_progression_trackers = set()
        self._historical_household_story_progression_trackers = set()
        self.protected_households_rule_set = None
        self.unprotected_households_rule_set = None
        self._story_progression_enabled_in_options = True
        self._story_progression_enabled_via_killswitch = True

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_STORY_PROGRESSION_SERVICE

    @property
    def story_progression_enabled(self):
        return self._story_progression_enabled_in_options and self._story_progression_enabled_via_killswitch

    def load_options(self, options_proto):
        if options_proto is None:
            return
        self._story_progression_enabled_in_options = options_proto.story_progression_effects_enabled

    def setup(self, save_slot_data=None, **kwargs):
        if save_slot_data is not None:
            sims.global_gender_preference_tuning.GlobalGenderPreferenceTuning.enable_autogeneration_same_sex_preference = save_slot_data.gameplay_data.enable_autogeneration_same_sex_preference
            story_progression_data = save_slot_data.gameplay_data.story_progression_service
            for action in StoryProgressionService.ACTIONS:
                action.load(story_progression_data)

    def save(self, save_slot_data=None, **kwargs):
        if save_slot_data is not None:
            save_slot_data.gameplay_data.enable_autogeneration_same_sex_preference = sims.global_gender_preference_tuning.GlobalGenderPreferenceTuning.enable_autogeneration_same_sex_preference
            story_progression_data = save_slot_data.gameplay_data.story_progression_service
            for action in StoryProgressionService.ACTIONS:
                action.save(story_progression_data)

    def load(self, zone_data=None):
        save_game_proto = services.get_persistence_service().get_save_game_data_proto()
        self.protected_households_rule_set = StoryProgressionRuleSet(save_game_proto.protected_households_story_progression_rule_set)
        self.unprotected_households_rule_set = StoryProgressionRuleSet(save_game_proto.unprotected_households_story_progression_rule_set)

    def on_all_households_and_sim_infos_loaded(self, client):
        self.update()
        sim_timeline = services.time_service().sim_timeline
        now = sim_timeline.now
        when = now.time_of_next_day_time(self.UPDATE_TIME)
        self._update_story_progression_element = sim_timeline.schedule((GeneratorElement(self._update_gen)), when=when)
        return super().on_all_households_and_sim_infos_loaded(client)

    def enable_story_progression_flag(self, story_progression_flag):
        self._story_progression_flags |= story_progression_flag

    def disable_story_progression_flag(self, story_progression_flag):
        self._story_progression_flags &= ~story_progression_flag

    def is_story_progression_flag_enabled(self, story_progression_flag):
        return self._story_progression_flags & story_progression_flag

    def on_client_connect(self, client):
        current_zone = services.current_zone()
        current_zone.refresh_feature_params(feature_key=(self.FEATURE_KEY))
        current_zone.register_callback(zone_types.ZoneState.RUNNING, self._initialize_alarm)
        current_zone.register_callback(zone_types.ZoneState.SHUTDOWN_STARTED, self._on_zone_shutdown)

    def _on_zone_shutdown(self):
        current_zone = services.current_zone()
        if self._alarm_handle is not None:
            alarms.cancel_alarm(self._alarm_handle)
        current_zone.unregister_callback(zone_types.ZoneState.SHUTDOWN_STARTED, self._on_zone_shutdown)
        if self._update_story_progression_element is not None:
            self._update_story_progression_element.trigger_hard_stop()
            self._update_story_progression_element = None

    def _initialize_alarm(self):
        current_zone = services.current_zone()
        current_zone.unregister_callback(zone_types.ZoneState.RUNNING, self._initialize_alarm)
        time_span = clock.interval_in_sim_minutes(self.INTERVAL)
        self._alarm_handle = alarms.add_alarm(self, time_span,
          (self._process_next_action),
          repeating=True)

    def _process_next_action(self, _):
        self.process_action_index(self._next_action_index)
        self._next_action_index += 1
        if self._next_action_index >= len(self.ACTIONS):
            self._next_action_index = 0

    def process_action_index(self, index):
        if index >= len(self.ACTIONS):
            logger.error('Trying to process index {} where max index is {}', index, len(self.ACTIONS) - 1)
            return
        action = self.ACTIONS[index]
        if action.should_process(self._story_progression_flags):
            action.process_action(self._story_progression_flags)

    def process_all_actions(self):
        for i in range(len(self.ACTIONS)):
            self.process_action_index(i)

    def set_time_multiplier(self, time_multiplier):
        if time_multiplier < 0:
            logger.error('Unable to set Story Progression time multiplier to {}', time_multiplier)
            return
        self._timeline_multiplier = time_multiplier

    def update(self):
        current_time = services.time_service().sim_now
        if self._timeline is None:
            self._timeline = Timeline(current_time)
        if self._timeline_update is None:
            self._timeline_update = current_time
            return
        delta_time = current_time - self._timeline_update
        self._timeline_update = current_time
        delta_time *= self._timeline_multiplier
        self._timeline.simulate(self._timeline.now + delta_time)

    def set_story_progression_enabled_in_options(self, enabled):
        self._story_progression_enabled_in_options = enabled

    def set_story_progression_enabled_via_killswitch(self, enabled):
        self._story_progression_enabled_via_killswitch = enabled

    def _seed_arcs_from_pass_and_neighborhood_gen--- This code section failed: ---

 L. 407         0  LOAD_FAST                'pass_tuning'
                2  LOAD_ATTR                potential_arcs
                4  POP_JUMP_IF_TRUE     32  'to 32'

 L. 408         6  LOAD_FAST                'gsi_data'
                8  LOAD_CONST               None
               10  COMPARE_OP               is-not
               12  POP_JUMP_IF_FALSE    28  'to 28'

 L. 409        14  LOAD_GLOBAL              StoryProgressionResult
               16  LOAD_GLOBAL              StoryProgressionResultType
               18  LOAD_ATTR                FAILED_NO_ARCS

 L. 410        20  LOAD_STR                 'No potential arcs.  All arcs must not be installed or no arcs have been tuned.'
               22  CALL_FUNCTION_2       2  '2 positional arguments'
               24  LOAD_FAST                'gsi_data'
               26  STORE_ATTR               result
             28_0  COME_FROM            12  '12'

 L. 411        28  LOAD_CONST               None
               30  RETURN_VALUE     
             32_0  COME_FROM             4  '4'

 L. 413        32  LOAD_FAST                'pass_tuning'
               34  LOAD_ATTR                demographic_function
               36  LOAD_FAST                'gsi_data'
               38  LOAD_FAST                'neighborhood_proto'
               40  LOAD_CONST               ('neighborhood_proto_buff',)
               42  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
               44  UNPACK_SEQUENCE_4     4 
               46  STORE_FAST               'demographic_result'
               48  STORE_FAST               'sim_infos'
               50  STORE_FAST               'household_ids'
               52  STORE_FAST               'zone_ids'

 L. 414        54  LOAD_FAST                'demographic_result'
               56  LOAD_CONST               None
               58  COMPARE_OP               is
               60  POP_JUMP_IF_FALSE   114  'to 114'

 L. 415        62  LOAD_FAST                'timeline'
               64  LOAD_CONST               None
               66  COMPARE_OP               is-not
               68  POP_JUMP_IF_FALSE    88  'to 88'

 L. 416        70  LOAD_FAST                'timeline'
               72  LOAD_METHOD              run_child
               74  LOAD_GLOBAL              SleepElement
               76  LOAD_GLOBAL              TimeSpan
               78  LOAD_ATTR                ZERO
               80  CALL_FUNCTION_1       1  '1 positional argument'
               82  CALL_METHOD_1         1  '1 positional argument'
               84  YIELD_VALUE      
               86  POP_TOP          
             88_0  COME_FROM            68  '68'

 L. 417        88  LOAD_FAST                'gsi_data'
               90  LOAD_CONST               None
               92  COMPARE_OP               is-not
               94  POP_JUMP_IF_FALSE   110  'to 110'

 L. 418        96  LOAD_GLOBAL              StoryProgressionResult
               98  LOAD_GLOBAL              StoryProgressionResultType
              100  LOAD_ATTR                FAILED_DEMOGRAPHICS

 L. 419       102  LOAD_STR                 'No demographic result generated.'
              104  CALL_FUNCTION_2       2  '2 positional arguments'
              106  LOAD_FAST                'gsi_data'
              108  STORE_ATTR               result
            110_0  COME_FROM            94  '94'

 L. 420       110  LOAD_CONST               None
              112  RETURN_VALUE     
            114_0  COME_FROM            60  '60'

 L. 423       114  LOAD_FAST                'gsi_data'
              116  LOAD_CONST               None
              118  COMPARE_OP               is-not
              120  POP_JUMP_IF_FALSE   128  'to 128'

 L. 424       122  LOAD_FAST                'demographic_result'
              124  LOAD_FAST                'gsi_data'
              126  STORE_ATTR               demographic_percentage
            128_0  COME_FROM           120  '120'

 L. 425       128  SETUP_LOOP          208  'to 208'
              130  LOAD_FAST                'pass_tuning'
              132  LOAD_ATTR                demographic_data
              134  GET_ITER         
            136_0  COME_FROM           148  '148'
              136  FOR_ITER            158  'to 158'
              138  STORE_FAST               'potential_demographic_data'

 L. 426       140  LOAD_FAST                'demographic_result'
              142  LOAD_FAST                'potential_demographic_data'
              144  LOAD_ATTR                maximum_range
              146  COMPARE_OP               <=
              148  POP_JUMP_IF_FALSE   136  'to 136'

 L. 427       150  LOAD_FAST                'potential_demographic_data'
              152  STORE_FAST               'demographic_data'

 L. 428       154  BREAK_LOOP       
              156  JUMP_BACK           136  'to 136'
              158  POP_BLOCK        

 L. 430       160  LOAD_GLOBAL              logger
              162  LOAD_METHOD              error
              164  LOAD_STR                 'Attempting to use demographic data for pass {} that does not have any data for value {}'

 L. 431       166  LOAD_FAST                'pass_tuning'
              168  LOAD_ATTR                debug_pass_name

 L. 432       170  LOAD_FAST                'demographic_result'
              172  CALL_METHOD_3         3  '3 positional arguments'
              174  POP_TOP          

 L. 433       176  LOAD_FAST                'gsi_data'
              178  LOAD_CONST               None
              180  COMPARE_OP               is-not
              182  POP_JUMP_IF_FALSE   204  'to 204'

 L. 434       184  LOAD_GLOBAL              StoryProgressionResult
              186  LOAD_GLOBAL              StoryProgressionResultType
              188  LOAD_ATTR                ERROR

 L. 435       190  LOAD_STR                 'Attempting to use demographic data for pass {} that does not have any data for value {}'

 L. 436       192  LOAD_FAST                'pass_tuning'
              194  LOAD_ATTR                debug_pass_name

 L. 437       196  LOAD_FAST                'demographic_result'
              198  CALL_FUNCTION_4       4  '4 positional arguments'
              200  LOAD_FAST                'gsi_data'
              202  STORE_ATTR               result
            204_0  COME_FROM           182  '182'

 L. 438       204  LOAD_CONST               None
              206  RETURN_VALUE     
            208_0  COME_FROM_LOOP      128  '128'

 L. 441       208  LOAD_FAST                'debug_seed_all_arcs'
          210_212  POP_JUMP_IF_TRUE    286  'to 286'
              214  LOAD_GLOBAL              random
              216  LOAD_METHOD              random
              218  CALL_METHOD_0         0  '0 positional arguments'
              220  LOAD_FAST                'demographic_data'
              222  LOAD_ATTR                chance_of_occurrence
              224  COMPARE_OP               >
          226_228  POP_JUMP_IF_FALSE   286  'to 286'

 L. 442       230  LOAD_FAST                'timeline'
              232  LOAD_CONST               None
              234  COMPARE_OP               is-not
          236_238  POP_JUMP_IF_FALSE   258  'to 258'

 L. 443       240  LOAD_FAST                'timeline'
              242  LOAD_METHOD              run_child
              244  LOAD_GLOBAL              SleepElement
              246  LOAD_GLOBAL              TimeSpan
              248  LOAD_ATTR                ZERO
              250  CALL_FUNCTION_1       1  '1 positional argument'
              252  CALL_METHOD_1         1  '1 positional argument'
              254  YIELD_VALUE      
              256  POP_TOP          
            258_0  COME_FROM           236  '236'

 L. 444       258  LOAD_FAST                'gsi_data'
              260  LOAD_CONST               None
              262  COMPARE_OP               is-not
          264_266  POP_JUMP_IF_FALSE   282  'to 282'

 L. 445       268  LOAD_GLOBAL              StoryProgressionResult
              270  LOAD_GLOBAL              StoryProgressionResultType
              272  LOAD_ATTR                FAILED_DEMOGRAPHICS

 L. 446       274  LOAD_STR                 'Failed demographic chance of occurrence.'
              276  CALL_FUNCTION_2       2  '2 positional arguments'
              278  LOAD_FAST                'gsi_data'
              280  STORE_ATTR               result
            282_0  COME_FROM           264  '264'

 L. 447       282  LOAD_CONST               None
              284  RETURN_VALUE     
            286_0  COME_FROM           226  '226'
            286_1  COME_FROM           210  '210'

 L. 449       286  LOAD_FAST                'debug_seed_all_arcs'
          288_290  POP_JUMP_IF_FALSE   304  'to 304'

 L. 450       292  LOAD_GLOBAL              len
              294  LOAD_FAST                'pass_tuning'
              296  LOAD_ATTR                potential_arcs
              298  CALL_FUNCTION_1       1  '1 positional argument'
              300  STORE_FAST               'number_to_seed'
              302  JUMP_FORWARD        352  'to 352'
            304_0  COME_FROM           288  '288'

 L. 452       304  LOAD_FAST                'demographic_data'
              306  LOAD_ATTR                number_to_seed
              308  LOAD_METHOD              random_int
              310  CALL_METHOD_0         0  '0 positional arguments'
              312  STORE_FAST               'number_to_seed'

 L. 453       314  LOAD_FAST                'number_to_seed'
              316  LOAD_CONST               0
              318  COMPARE_OP               ==
          320_322  POP_JUMP_IF_FALSE   352  'to 352'

 L. 454       324  LOAD_FAST                'gsi_data'
              326  LOAD_CONST               None
              328  COMPARE_OP               is-not
          330_332  POP_JUMP_IF_FALSE   348  'to 348'

 L. 455       334  LOAD_GLOBAL              StoryProgressionResult
              336  LOAD_GLOBAL              StoryProgressionResultType
              338  LOAD_ATTR                FAILED_DEMOGRAPHICS

 L. 456       340  LOAD_STR                 'Demographics decided to seed 0 arcs.'
              342  CALL_FUNCTION_2       2  '2 positional arguments'
              344  LOAD_FAST                'gsi_data'
              346  STORE_ATTR               result
            348_0  COME_FROM           330  '330'

 L. 457       348  LOAD_CONST               None
              350  RETURN_VALUE     
            352_0  COME_FROM           320  '320'
            352_1  COME_FROM           302  '302'

 L. 459       352  LOAD_LISTCOMP            '<code_object <listcomp>>'
              354  LOAD_STR                 'StoryProgressionService._seed_arcs_from_pass_and_neighborhood_gen.<locals>.<listcomp>'
              356  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'

 L. 460       358  LOAD_FAST                'pass_tuning'
              360  LOAD_ATTR                potential_arcs
              362  GET_ITER         
              364  CALL_FUNCTION_1       1  '1 positional argument'
              366  STORE_FAST               'potential_arcs'

 L. 461   368_370  SETUP_LOOP          950  'to 950'
              372  LOAD_GLOBAL              range
              374  LOAD_FAST                'number_to_seed'
              376  CALL_FUNCTION_1       1  '1 positional argument'
              378  GET_ITER         
          380_382  FOR_ITER            948  'to 948'
              384  STORE_FAST               'i'

 L. 463   386_388  SETUP_LOOP          944  'to 944'
              390  LOAD_FAST                'potential_arcs'
          392_394  POP_JUMP_IF_FALSE   902  'to 902'

 L. 464       396  LOAD_FAST                'debug_seed_all_arcs'
          398_400  POP_JUMP_IF_FALSE   434  'to 434'

 L. 465       402  LOAD_FAST                'i'
              404  STORE_FAST               'chosen_arc_index'

 L. 466       406  LOAD_FAST                'chosen_arc_index'
              408  LOAD_GLOBAL              len
              410  LOAD_FAST                'potential_arcs'
              412  CALL_FUNCTION_1       1  '1 positional argument'
              414  COMPARE_OP               >=
          416_418  POP_JUMP_IF_FALSE   446  'to 446'

 L. 467       420  LOAD_GLOBAL              logger
              422  LOAD_METHOD              error
              424  LOAD_STR                 'One of the arcs failed when attempting to seed all arcs.  Not all arcs will have been seeded.'
              426  CALL_METHOD_1         1  '1 positional argument'
              428  POP_TOP          

 L. 468       430  BREAK_LOOP       
              432  JUMP_FORWARD        446  'to 446'
            434_0  COME_FROM           398  '398'

 L. 470       434  LOAD_GLOBAL              sims4
              436  LOAD_ATTR                random
              438  LOAD_METHOD              weighted_random_index
              440  LOAD_FAST                'potential_arcs'
              442  CALL_METHOD_1         1  '1 positional argument'
              444  STORE_FAST               'chosen_arc_index'
            446_0  COME_FROM           432  '432'
            446_1  COME_FROM           416  '416'

 L. 471       446  LOAD_FAST                'potential_arcs'
              448  LOAD_FAST                'chosen_arc_index'
              450  BINARY_SUBSCR    
              452  LOAD_CONST               1
              454  BINARY_SUBSCR    
              456  STORE_FAST               'potential_arc'

 L. 472       458  LOAD_FAST                'potential_arc'
              460  LOAD_METHOD              select_candidates
              462  LOAD_FAST                'sim_infos'

 L. 473       464  LOAD_FAST                'household_ids'

 L. 474       466  LOAD_FAST                'zone_ids'
              468  CALL_METHOD_3         3  '3 positional arguments'
              470  UNPACK_SEQUENCE_3     3 
              472  STORE_FAST               'sim_candidate'
              474  STORE_FAST               'household_candidate'
              476  STORE_FAST               'zone_candidate'

 L. 475       478  LOAD_CONST               None
              480  STORE_FAST               'chosen_candidate'

 L. 476       482  LOAD_FAST                'sim_candidate'
              484  LOAD_CONST               None
              486  COMPARE_OP               is-not
          488_490  POP_JUMP_IF_FALSE   518  'to 518'
              492  LOAD_FAST                'potential_arc'
              494  LOAD_ATTR                arc_type
              496  LOAD_GLOBAL              StoryType
              498  LOAD_ATTR                SIM_BASED
              500  COMPARE_OP               ==
          502_504  POP_JUMP_IF_FALSE   518  'to 518'

 L. 477       506  LOAD_FAST                'sim_candidate'
              508  LOAD_ATTR                story_progression_tracker
              510  STORE_FAST               'story_progression_tracker'

 L. 478       512  LOAD_FAST                'sim_candidate'
              514  STORE_FAST               'chosen_candidate'
              516  JUMP_FORWARD        582  'to 582'
            518_0  COME_FROM           502  '502'
            518_1  COME_FROM           488  '488'

 L. 479       518  LOAD_FAST                'household_candidate'
              520  LOAD_CONST               None
              522  COMPARE_OP               is-not
          524_526  POP_JUMP_IF_FALSE   572  'to 572'
              528  LOAD_FAST                'potential_arc'
              530  LOAD_ATTR                arc_type
              532  LOAD_GLOBAL              StoryType
              534  LOAD_ATTR                HOUSEHOLD_BASED
              536  COMPARE_OP               ==
          538_540  POP_JUMP_IF_FALSE   572  'to 572'

 L. 480       542  LOAD_GLOBAL              services
              544  LOAD_METHOD              household_manager
              546  CALL_METHOD_0         0  '0 positional arguments'
              548  STORE_FAST               'household_manager'

 L. 481       550  LOAD_FAST                'household_manager'
              552  LOAD_METHOD              get
              554  LOAD_FAST                'household_candidate'
              556  CALL_METHOD_1         1  '1 positional argument'
              558  STORE_FAST               'household'

 L. 482       560  LOAD_FAST                'household'
              562  LOAD_ATTR                story_progression_tracker
              564  STORE_FAST               'story_progression_tracker'

 L. 483       566  LOAD_FAST                'household_candidate'
              568  STORE_FAST               'chosen_candidate'
              570  JUMP_FORWARD        582  'to 582'
            572_0  COME_FROM           538  '538'
            572_1  COME_FROM           524  '524'

 L. 490       572  LOAD_FAST                'potential_arcs'
              574  LOAD_FAST                'chosen_arc_index'
              576  DELETE_SUBSCR    

 L. 491   578_580  CONTINUE            390  'to 390'
            582_0  COME_FROM           570  '570'
            582_1  COME_FROM           516  '516'

 L. 493       582  LOAD_FAST                'story_progression_tracker'
              584  LOAD_CONST               None
              586  COMPARE_OP               is
          588_590  POP_JUMP_IF_FALSE   616  'to 616'

 L. 494       592  LOAD_GLOBAL              logger
              594  LOAD_METHOD              error
              596  LOAD_STR                 'Candidate {} had no StoryProgressionTracker when trying to seed story progression arc: {}'

 L. 495       598  LOAD_FAST                'chosen_candidate'
              600  LOAD_FAST                'potential_arc'
              602  CALL_METHOD_3         3  '3 positional arguments'
              604  POP_TOP          

 L. 496       606  LOAD_FAST                'potential_arcs'
              608  LOAD_FAST                'chosen_arc_index'
              610  DELETE_SUBSCR    

 L. 497   612_614  CONTINUE            390  'to 390'
            616_0  COME_FROM           588  '588'

 L. 499       616  LOAD_FAST                'story_progression_tracker'
              618  LOAD_ATTR                add_arc
              620  LOAD_FAST                'potential_arc'
              622  LOAD_FAST                'zone_candidate'
              624  LOAD_CONST               ('zone_candidate',)
              626  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              628  STORE_FAST               'result'

 L. 502       630  LOAD_FAST                'result'
          632_634  POP_JUMP_IF_TRUE    662  'to 662'

 L. 503       636  LOAD_GLOBAL              logger
              638  LOAD_METHOD              warn
              640  LOAD_STR                 'Attempting to seed arc {} failed during setup: {}'

 L. 504       642  LOAD_FAST                'potential_arc'

 L. 505       644  LOAD_FAST                'result'
              646  LOAD_ATTR                reason
              648  CALL_METHOD_3         3  '3 positional arguments'
              650  POP_TOP          

 L. 506       652  LOAD_FAST                'potential_arcs'
              654  LOAD_FAST                'chosen_arc_index'
              656  DELETE_SUBSCR    

 L. 507   658_660  CONTINUE            390  'to 390'
            662_0  COME_FROM           632  '632'

 L. 508       662  LOAD_FAST                'gsi_data'
              664  LOAD_CONST               None
              666  COMPARE_OP               is-not
          668_670  POP_JUMP_IF_FALSE   758  'to 758'

 L. 509       672  LOAD_GLOBAL              GSIStoryProgressionArcData
              674  CALL_FUNCTION_0       0  '0 positional arguments'
              676  STORE_FAST               'arc_gsi_data'

 L. 510       678  LOAD_FAST                'potential_arc'
              680  LOAD_FAST                'arc_gsi_data'
              682  STORE_ATTR               arc

 L. 511       684  LOAD_FAST                'potential_arc'
              686  LOAD_ATTR                arc_type
              688  LOAD_GLOBAL              StoryType
              690  LOAD_ATTR                SIM_BASED
              692  COMPARE_OP               ==
          694_696  POP_JUMP_IF_FALSE   716  'to 716'

 L. 512       698  LOAD_FAST                'sim_candidate'
              700  LOAD_ATTR                id
              702  LOAD_FAST                'arc_gsi_data'
              704  STORE_ATTR               item_id

 L. 513       706  LOAD_FAST                'sim_candidate'
              708  LOAD_ATTR                full_name
              710  LOAD_FAST                'arc_gsi_data'
              712  STORE_ATTR               item_name
              714  JUMP_FORWARD        732  'to 732'
            716_0  COME_FROM           694  '694'

 L. 515       716  LOAD_FAST                'household'
              718  LOAD_ATTR                id
              720  LOAD_FAST                'arc_gsi_data'
              722  STORE_ATTR               item_id

 L. 516       724  LOAD_FAST                'household'
              726  LOAD_ATTR                name
              728  LOAD_FAST                'arc_gsi_data'
              730  STORE_ATTR               item_name
            732_0  COME_FROM           714  '714'

 L. 517       732  LOAD_FAST                'gsi_data'
              734  LOAD_ATTR                arc_data
              736  LOAD_METHOD              append
              738  LOAD_FAST                'arc_gsi_data'
              740  CALL_METHOD_1         1  '1 positional argument'
              742  POP_TOP          

 L. 518       744  LOAD_FAST                'gsi_data'
              746  DUP_TOP          
              748  LOAD_ATTR                arcs_seeded
              750  LOAD_CONST               1
              752  INPLACE_ADD      
              754  ROT_TWO          
              756  STORE_ATTR               arcs_seeded
            758_0  COME_FROM           668  '668'

 L. 519       758  LOAD_FAST                'zone_candidate'
              760  LOAD_CONST               None
              762  COMPARE_OP               is-not
          764_766  POP_JUMP_IF_FALSE   788  'to 788'
              768  LOAD_FAST                'zone_candidate'
              770  LOAD_FAST                'zone_ids'
              772  COMPARE_OP               in
          774_776  POP_JUMP_IF_FALSE   788  'to 788'

 L. 520       778  LOAD_FAST                'zone_ids'
              780  LOAD_METHOD              remove
              782  LOAD_FAST                'zone_candidate'
              784  CALL_METHOD_1         1  '1 positional argument'
              786  POP_TOP          
            788_0  COME_FROM           774  '774'
            788_1  COME_FROM           764  '764'

 L. 521       788  LOAD_FAST                'potential_arc'
              790  LOAD_ATTR                arc_type
              792  LOAD_GLOBAL              StoryType
              794  LOAD_ATTR                SIM_BASED
              796  COMPARE_OP               ==
          798_800  POP_JUMP_IF_FALSE   852  'to 852'

 L. 522       802  LOAD_FAST                'sim_candidate'
              804  LOAD_ATTR                id
              806  LOAD_FAST                'self'
              808  LOAD_ATTR                _sim_story_progression_trackers
              810  COMPARE_OP               not-in
          812_814  POP_JUMP_IF_FALSE   830  'to 830'

 L. 523       816  LOAD_FAST                'self'
              818  LOAD_ATTR                _sim_story_progression_trackers
              820  LOAD_METHOD              add
              822  LOAD_FAST                'sim_candidate'
              824  LOAD_ATTR                id
              826  CALL_METHOD_1         1  '1 positional argument'
              828  POP_TOP          
            830_0  COME_FROM           812  '812'

 L. 527       830  LOAD_FAST                'sim_candidate'
              832  LOAD_FAST                'sim_infos'
              834  COMPARE_OP               in
          836_838  POP_JUMP_IF_FALSE   896  'to 896'

 L. 528       840  LOAD_FAST                'sim_infos'
              842  LOAD_METHOD              remove
              844  LOAD_FAST                'sim_candidate'
              846  CALL_METHOD_1         1  '1 positional argument'
              848  POP_TOP          
              850  JUMP_FORWARD        896  'to 896'
            852_0  COME_FROM           798  '798'

 L. 530       852  LOAD_FAST                'household_candidate'
              854  LOAD_FAST                'self'
              856  LOAD_ATTR                _household_story_progression_trackers
              858  COMPARE_OP               not-in
          860_862  POP_JUMP_IF_FALSE   876  'to 876'

 L. 531       864  LOAD_FAST                'self'
              866  LOAD_ATTR                _household_story_progression_trackers
              868  LOAD_METHOD              add
              870  LOAD_FAST                'household_candidate'
              872  CALL_METHOD_1         1  '1 positional argument'
              874  POP_TOP          
            876_0  COME_FROM           860  '860'

 L. 534       876  LOAD_FAST                'household_candidate'
              878  LOAD_FAST                'household_ids'
              880  COMPARE_OP               in
          882_884  POP_JUMP_IF_FALSE   896  'to 896'

 L. 535       886  LOAD_FAST                'household_ids'
              888  LOAD_METHOD              remove
              890  LOAD_FAST                'household_candidate'
              892  CALL_METHOD_1         1  '1 positional argument'
              894  POP_TOP          
            896_0  COME_FROM           882  '882'
            896_1  COME_FROM           850  '850'
            896_2  COME_FROM           836  '836'

 L. 536       896  BREAK_LOOP       
          898_900  JUMP_BACK           390  'to 390'
            902_0  COME_FROM           392  '392'
              902  POP_BLOCK        

 L. 539       904  LOAD_GLOBAL              logger
              906  LOAD_METHOD              info
              908  LOAD_STR                 'All arcs in pass {} failed to find candidates.'

 L. 540       910  LOAD_FAST                'pass_tuning'
              912  LOAD_ATTR                debug_pass_name
              914  CALL_METHOD_2         2  '2 positional arguments'
              916  POP_TOP          

 L. 541       918  LOAD_FAST                'gsi_data'
              920  LOAD_CONST               None
              922  COMPARE_OP               is-not
          924_926  POP_JUMP_IF_FALSE   942  'to 942'

 L. 542       928  LOAD_GLOBAL              StoryProgressionResult
              930  LOAD_GLOBAL              StoryProgressionResultType
              932  LOAD_ATTR                FAILED_NO_ARCS

 L. 543       934  LOAD_STR                 'All arcs failed to find candidates.'
              936  CALL_FUNCTION_2       2  '2 positional arguments'
              938  LOAD_FAST                'gsi_data'
              940  STORE_ATTR               result
            942_0  COME_FROM           924  '924'

 L. 544       942  BREAK_LOOP       
            944_0  COME_FROM_LOOP      386  '386'
          944_946  JUMP_BACK           380  'to 380'
              948  POP_BLOCK        
            950_0  COME_FROM_LOOP      368  '368'

 L. 545       950  LOAD_FAST                'timeline'
              952  LOAD_CONST               None
              954  COMPARE_OP               is-not
          956_958  POP_JUMP_IF_FALSE   978  'to 978'

 L. 546       960  LOAD_FAST                'timeline'
              962  LOAD_METHOD              run_child
              964  LOAD_GLOBAL              SleepElement
              966  LOAD_GLOBAL              TimeSpan
              968  LOAD_ATTR                ZERO
              970  CALL_FUNCTION_1       1  '1 positional argument'
              972  CALL_METHOD_1         1  '1 positional argument'
              974  YIELD_VALUE      
              976  POP_TOP          
            978_0  COME_FROM           956  '956'

Parse error at or near `COME_FROM_LOOP' instruction at offset 944_0

    def seed_new_story_arcs_gen(self, timeline=None, debug_seed_all_arcs=False):
        for pass_tuning in self.STORY_PROGRESSION_PASSES:
            if pass_tuning.pass_type == StoryProgressionPassType.GLOBAL:
                neighborhood_protos = (None, )
            else:
                neighborhood_protos = services.get_persistence_service().get_neighborhoods_proto_buf_gen()
            for neighborhood_proto in neighborhood_protos:
                if is_story_progression_pass_archive_enabled():
                    gsi_data = GSIStoryProgressionPassData()
                    gsi_data.story_progression_pass = pass_tuning.debug_pass_name
                else:
                    gsi_data = None
                yield from self._seed_arcs_from_pass_and_neighborhood_gen(pass_tuning, neighborhood_proto, timeline, gsi_data, debug_seed_all_arcs=debug_seed_all_arcs)
                if gsi_data is not None:
                    archive_story_progression_pass_data(gsi_data)
                if debug_seed_all_arcs:
                    break

        if False:
            yield None

    def _update_story_progression_trackers_gen(self, tracker_list, manager, timeline=None):
        for story_progression_obj_id in tuple(tracker_list):
            story_progression_obj = manager.get(story_progression_obj_id)
            if story_progression_obj is None:
                tracker_list.remove(story_progression_obj_id)
                continue
            story_progression_tracker = story_progression_obj.story_progression_tracker
            if story_progression_tracker is None:
                tracker_list.remove(story_progression_obj_id)
                continue
            yield from story_progression_tracker.update_arcs_gen(timeline=timeline)
            if not story_progression_tracker.has_arcs:
                tracker_list.remove(story_progression_obj_id)
            if timeline is not None:
                yield timeline.run_child(SleepElement(TimeSpan.ZERO))

    def update_story_progression_trackers_gen(self, timeline=None):
        yield from self._update_story_progression_trackers_gen((self._sim_story_progression_trackers), (services.sim_info_manager()),
          timeline=timeline)
        yield from self._update_story_progression_trackers_gen((self._household_story_progression_trackers), (services.household_manager()),
          timeline=timeline)
        if False:
            yield None

    def _update_gen(self, timeline):
        while True:
            reschedule = True
            try:
                try:
                    if self.story_progression_enabled:
                        yield from self.seed_new_story_arcs_gen(timeline=timeline)
                        yield from self.update_story_progression_trackers_gen(timeline=timeline)
                except GeneratorExit:
                    reschedule = False
                    raise
                except Exception as exception:
                    try:
                        logger.exception('Exception while updating story progression service.: ', exc=exception)
                    finally:
                        exception = None
                        del exception

            finally:
                if reschedule:
                    log_story_progression_demographics()
                    time_span = timeline.now.time_till_next_day_time(self.UPDATE_TIME)
                    if time_span <= TimeSpan(0):
                        time_span = create_time_span(days=1)
                    yield timeline.run_child(SleepElement(time_span))

    def cache_active_arcs_sim_id(self, sim_id):
        self._sim_story_progression_trackers.add(sim_id)

    def cache_active_arcs_household_id(self, household_id):
        self._household_story_progression_trackers.add(household_id)

    def cache_historical_arcs_sim_id(self, sim_id):
        self._historical_sim_story_progression_trackers.add(sim_id)

    def cache_historical_arcs_household_id(self, household_id):
        self._historical_household_story_progression_trackers.add(household_id)

    def get_discovery_string--- This code section failed: ---

 L. 659         0  LOAD_GLOBAL              services
                2  LOAD_METHOD              sim_info_manager
                4  CALL_METHOD_0         0  '0 positional arguments'
                6  STORE_DEREF              'sim_info_manager'

 L. 660         8  LOAD_GLOBAL              services
               10  LOAD_METHOD              household_manager
               12  CALL_METHOD_0         0  '0 positional arguments'
               14  STORE_DEREF              'household_manager'

 L. 661        16  LOAD_CLOSURE             'self'
               18  LOAD_CLOSURE             'sim_info_manager'
               20  BUILD_TUPLE_2         2 
               22  LOAD_LISTCOMP            '<code_object <listcomp>>'
               24  LOAD_STR                 'StoryProgressionService.get_discovery_string.<locals>.<listcomp>'
               26  MAKE_FUNCTION_8          'closure'
               28  LOAD_DEREF               'self'
               30  LOAD_ATTR                _historical_sim_story_progression_trackers
               32  GET_ITER         
               34  CALL_FUNCTION_1       1  '1 positional argument'
               36  STORE_FAST               'trackers'

 L. 662        38  LOAD_FAST                'trackers'
               40  LOAD_METHOD              extend
               42  LOAD_CLOSURE             'household_manager'
               44  LOAD_CLOSURE             'self'
               46  BUILD_TUPLE_2         2 
               48  LOAD_GENEXPR             '<code_object <genexpr>>'
               50  LOAD_STR                 'StoryProgressionService.get_discovery_string.<locals>.<genexpr>'
               52  MAKE_FUNCTION_8          'closure'
               54  LOAD_DEREF               'self'
               56  LOAD_ATTR                _historical_household_story_progression_trackers
               58  GET_ITER         
               60  CALL_FUNCTION_1       1  '1 positional argument'
               62  CALL_METHOD_1         1  '1 positional argument'
               64  POP_TOP          

 L. 663        66  SETUP_LOOP          234  'to 234'
               68  LOAD_FAST                'trackers'
               70  POP_JUMP_IF_FALSE   232  'to 232'

 L. 664        72  LOAD_FAST                'trackers'
               74  LOAD_METHOD              pop
               76  LOAD_GLOBAL              random
               78  LOAD_METHOD              randint
               80  LOAD_CONST               0
               82  LOAD_GLOBAL              len
               84  LOAD_FAST                'trackers'
               86  CALL_FUNCTION_1       1  '1 positional argument'
               88  LOAD_CONST               1
               90  BINARY_SUBTRACT  
               92  CALL_METHOD_2         2  '2 positional arguments'
               94  CALL_METHOD_1         1  '1 positional argument'
               96  UNPACK_SEQUENCE_3     3 
               98  STORE_FAST               'manager'
              100  STORE_FAST               'historical_tracker_list'
              102  STORE_FAST               'tracker_id'

 L. 665       104  LOAD_FAST                'manager'
              106  LOAD_METHOD              get
              108  LOAD_FAST                'tracker_id'
              110  CALL_METHOD_1         1  '1 positional argument'
              112  STORE_FAST               'tracker_owner'

 L. 666       114  LOAD_FAST                'tracker_owner'
              116  LOAD_CONST               None
              118  COMPARE_OP               is-not
              120  POP_JUMP_IF_FALSE   128  'to 128'
              122  LOAD_FAST                'tracker_owner'
              124  LOAD_ATTR                story_progression_tracker
              126  JUMP_FORWARD        130  'to 130'
            128_0  COME_FROM           120  '120'
              128  LOAD_CONST               None
            130_0  COME_FROM           126  '126'
              130  STORE_FAST               'tracker'

 L. 667       132  LOAD_FAST                'tracker'
              134  LOAD_CONST               None
              136  COMPARE_OP               is
              138  POP_JUMP_IF_FALSE   152  'to 152'

 L. 668       140  LOAD_FAST                'historical_tracker_list'
              142  LOAD_METHOD              remove
              144  LOAD_FAST                'tracker_id'
              146  CALL_METHOD_1         1  '1 positional argument'
              148  POP_TOP          

 L. 669       150  CONTINUE             68  'to 68'
            152_0  COME_FROM           138  '138'

 L. 670       152  SETUP_LOOP          230  'to 230'

 L. 671       154  LOAD_FAST                'tracker'
              156  LOAD_METHOD              get_random_historical_chapter
              158  CALL_METHOD_0         0  '0 positional arguments'
              160  UNPACK_SEQUENCE_2     2 
              162  STORE_FAST               'chapter'
              164  STORE_FAST               'tokens'

 L. 672       166  LOAD_FAST                'chapter'
              168  LOAD_CONST               None
              170  COMPARE_OP               is
              172  POP_JUMP_IF_FALSE   186  'to 186'

 L. 673       174  LOAD_FAST                'historical_tracker_list'
              176  LOAD_METHOD              remove
              178  LOAD_FAST                'tracker_id'
              180  CALL_METHOD_1         1  '1 positional argument'
              182  POP_TOP          

 L. 674       184  BREAK_LOOP       
            186_0  COME_FROM           172  '172'

 L. 675       186  LOAD_DEREF               'self'
              188  LOAD_METHOD              _clear_chapter_history
              190  LOAD_FAST                'chapter'
              192  CALL_METHOD_1         1  '1 positional argument'
              194  POP_TOP          

 L. 676       196  LOAD_FAST                'chapter'
              198  LOAD_ATTR                discovery
              200  LOAD_CONST               None
              202  COMPARE_OP               is
              204  POP_JUMP_IF_FALSE   208  'to 208'

 L. 677       206  CONTINUE            154  'to 154'
            208_0  COME_FROM           204  '204'

 L. 678       208  LOAD_GLOBAL              story_progression_telemetry
              210  LOAD_METHOD              send_chapter_discovered_telemetry
              212  LOAD_FAST                'chapter'
              214  CALL_METHOD_1         1  '1 positional argument'
              216  POP_TOP          

 L. 679       218  LOAD_FAST                'chapter'
              220  LOAD_ATTR                discovery
              222  LOAD_ATTR                string
              224  LOAD_FAST                'tokens'
              226  BUILD_TUPLE_2         2 
              228  RETURN_VALUE     
            230_0  COME_FROM_LOOP      152  '152'
              230  JUMP_BACK            68  'to 68'
            232_0  COME_FROM            70  '70'
              232  POP_BLOCK        
            234_0  COME_FROM_LOOP       66  '66'

 L. 681       234  LOAD_GLOBAL              StoryProgTunables
              236  LOAD_ATTR                HISTORY
              238  LOAD_ATTR                no_history_discovery_string
              240  BUILD_LIST_0          0 
              242  BUILD_TUPLE_2         2 
              244  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM' instruction at offset 232_0

    def _clear_chapter_history(self, chapter):
        arc = chapter.arc
        arc.try_remove_historical_chapter(chapter)
        if arc.historical_chapters:
            return
        else:
            tracker = arc.tracker
            tracker.try_remove_historical_arc(arc)
            if tracker.historical_arcs:
                return
                if tracker.tracker_type is StoryType.SIM_BASED:
                    self._historical_sim_story_progression_trackers.remove(tracker.sim_info.id)
            elif tracker.tracker_type is StoryType.HOUSEHOLD_BASED:
                self._historical_household_story_progression_trackers.remove(tracker.household.id)