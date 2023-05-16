# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\resolver.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 79334 bytes
import random, sys, time
from event_testing.results import TestResult
from interactions import ParticipantType, ParticipantTypeSituationSims
from performance.test_profiling import TestProfileRecord, ProfileMetrics, record_profile_metrics
from sims4.utils import classproperty
from singletons import DEFAULT
import caches, event_testing.test_constants, services, sims4.log, sims4.reload
logger = sims4.log.Logger('Resolver')
with sims4.reload.protected(globals()):
    RESOLVER_PARTICIPANT = 'resolver'
    test_profile = None
SINGLE_TYPES = frozenset((ParticipantType.Affordance,
 ParticipantType.InteractionContext,
 event_testing.test_constants.FROM_DATA_OBJECT,
 event_testing.test_constants.OBJECTIVE_GUID64,
 event_testing.test_constants.FROM_EVENT_DATA))

class Resolver:

    def __init__(self, skip_safe_tests=False, search_for_tooltip=False, additional_metric_key_data=None):
        self._skip_safe_tests = skip_safe_tests
        self._search_for_tooltip = search_for_tooltip
        self._additional_metric_key_data = additional_metric_key_data

    @property
    def skip_safe_tests(self):
        return self._skip_safe_tests

    @property
    def search_for_tooltip(self):
        return self._search_for_tooltip

    @property
    def interaction(self):
        pass

    def get_resolved_args(self, expected):
        if expected is None:
            raise ValueError('Expected arguments from test instance get_expected_args are undefined: {}'.format(expected))
        ret = {}
        for event_key, participant_type in expected.items():
            if participant_type in SINGLE_TYPES:
                value = self.get_participant(participant_type, event_key=event_key)
            else:
                value = self.get_participants(participant_type, event_key=event_key)
            ret[event_key] = value

        return ret

    @property
    def profile_metric_key(self):
        pass

    def set_additional_metric_key_data(self, additional_metric_key_data):
        self._additional_metric_key_data = additional_metric_key_data

    def __call__(self, test):
        global test_profile
        if test.expected_kwargs is None:
            expected_args = test.get_expected_args()
            if expected_args:
                test.expected_kwargs = tuple(expected_args.items())
            else:
                test.expected_kwargs = ()
        elif test_profile is not None:
            start_time = time.perf_counter()
        else:
            resolved_args = {}
            for event_key, participant_type in test.expected_kwargs:
                if participant_type in SINGLE_TYPES:
                    value = self.get_participants(participant_type, event_key=event_key)
                    resolved_args[event_key] = value[0] if value else None
                else:
                    resolved_args[event_key] = self.get_participants(participant_type, event_key=event_key)

            if test_profile is not None:
                resolve_end_time = time.perf_counter()
            result = test(**resolved_args)
            if test_profile is not None:
                test_end_time = time.perf_counter()
                resolve_time = resolve_end_time - start_time
                test_time = test_end_time - resolve_end_time
                from event_testing.tests import TestSetInstance
                from event_testing.test_based_score_threshold import TestBasedScoreThresholdTest
                is_test_set = isinstance(test, type) and issubclass(test, TestSetInstance)
                test_name = '[TS]{}'.format(test.__name__) if is_test_set else test.__class__.__name__
                if isinstance(test, TestBasedScoreThresholdTest):
                    is_test_set = True
                resolver_name = type(self).__name__
                key_name = self.profile_metric_key
                try:
                    record_profile_metrics(test_profile, test_name, resolver_name, key_name, resolve_time,
                      test_time, is_test_set=is_test_set)
                except Exception as e:
                    try:
                        logger.exception('Resetting test_profile due to an exception {}.', e, owner='manus')
                        test_profile = None
                    finally:
                        e = None
                        del e

        return result

    def get_participant(self, participant_type, **kwargs):
        participants = (self.get_participants)(participant_type, **kwargs)
        if not participants:
            return
        if len(participants) > 1:
            raise ValueError('Too many participants returned for {}!'.format(participant_type))
        return next(iter(participants))

    def get_participants(self, participant_type, **kwargs):
        raise NotImplementedError('Attempting to use the Resolver base class, use sub-classes instead.')

    def _get_participants_base(self, participant_type, **kwargs):
        if participant_type == RESOLVER_PARTICIPANT:
            return self
        return Resolver.get_particpants_shared(participant_type)

    def get_target_id(self, test, id_type=None):
        expected_args = test.get_expected_args()
        resolved_args = self.get_resolved_args(expected_args)
        resolved_args['id_type'] = id_type
        return (test.get_target_id)(**resolved_args)

    def get_posture_id(self, test):
        expected_args = test.get_expected_args()
        resolved_args = self.get_resolved_args(expected_args)
        return (test.get_posture_id)(**resolved_args)

    def get_tags(self, test):
        expected_args = test.get_expected_args()
        resolved_args = self.get_resolved_args(expected_args)
        return (test.get_tags)(**resolved_args)

    def get_localization_tokens(self, *args, **kwargs):
        return ()

    @staticmethod
    def get_particpants_shared(participant_type):
        if participant_type == ParticipantType.Lot:
            return (
             services.active_lot(),)
        if participant_type == ParticipantType.LotOwners:
            owning_household = services.owning_household_of_active_lot()
            if owning_household is not None:
                return tuple((sim_info for sim_info in owning_household.sim_info_gen()))
            return ()
        if participant_type == ParticipantType.LotOwnersOrRenters:
            owning_household = services.owning_household_of_active_lot()
            if owning_household is not None:
                return tuple((sim_info for sim_info in owning_household.sim_info_gen()))
            current_zone = services.current_zone()
            travel_group = services.travel_group_manager().get_travel_group_by_zone_id(current_zone.id)
            if travel_group is not None:
                return tuple((sim_info for sim_info in travel_group.sim_info_gen()))
            return ()
        if participant_type == ParticipantType.LotOwnerSingleAndInstanced:
            owning_household = services.owning_household_of_active_lot()
            if owning_household is not None:
                for sim_info in owning_household.sim_info_gen():
                    if sim_info.is_instanced():
                        return (
                         sim_info,)

            return ()
        if participant_type == ParticipantType.ActiveHousehold:
            active_household = services.active_household()
            if active_household is not None:
                return tuple(active_household.sim_info_gen())
            return ()
        if participant_type == ParticipantType.AllInstancedActiveHouseholdSims:
            active_household = services.active_household()
            if active_household is not None:
                return tuple(active_household.instanced_sims_gen())
            return ()
        if participant_type == ParticipantType.CareerEventSim:
            career = services.get_career_service().get_career_in_career_event()
            if career is not None:
                return (
                 career.sim_info.get_sim_instance() or career.sim_info,)
            return ()
        if participant_type == ParticipantType.AllInstancedSims:
            return tuple(services.sim_info_manager().instanced_sims_gen())
        if participant_type == ParticipantType.Street:
            street = services.current_zone().street
            street_service = services.street_service()
            if street_service is None:
                return ()
            street_civic_policy_provider = street_service.get_provider(street)
            if street_civic_policy_provider is None:
                return ()
            return (
             street_civic_policy_provider,)
        if participant_type == ParticipantType.VenuePolicyProvider:
            venue_service = services.venue_service()
            if venue_service.source_venue is None or venue_service.source_venue.civic_policy_provider is None:
                return ()
            return (
             venue_service.source_venue.civic_policy_provider,)
        if participant_type == ParticipantType.CurrentRegion:
            region_inst = services.current_region_instance()
            if region_inst is None:
                return ()
            return (
             region_inst,)
        if participant_type == ParticipantType.FashionTrends:
            fashion_trend_service = services.fashion_trend_service()
            if fashion_trend_service is None:
                return ()
            return (
             fashion_trend_service,)

    def _get_lot_level_from_object(self, obj):
        if obj is None:
            return ()
        if getattr(obj, 'is_lot_level', False):
            return (
             obj,)
        lot = services.active_lot()
        if lot is None:
            return ()
        lot_level = lot.get_lot_level_instance(obj.routing_surface.secondary_id)
        if lot_level is None:
            return ()
        return (
         lot_level,)

    def _get_animal_home_from_object(self, obj):
        if obj is None:
            return ()
        animal_service = services.animal_service()
        if animal_service is None:
            return ()
        animal_home = animal_service.get_animal_home_obj(obj)
        if animal_home is None:
            return ()
        return (
         animal_home,)

    def _get_animal_home_assignees(self, home_obj):
        if home_obj is None:
            return ()
        else:
            animal_service = services.animal_service()
            if animal_service is None:
                return ()
            assignees = animal_service.get_animal_home_assignee_objs(home_obj)
            return assignees or ()
        return tuple(assignees)


class GlobalResolver(Resolver):

    def __init__(self, additional_metric_key_data=None):
        super().__init__(additional_metric_key_data=additional_metric_key_data)

    def get_participants(self, participant_type, **kwargs):
        result = (self._get_participants_base)(participant_type, **kwargs)
        if result is not None:
            return result
        if participant_type == event_testing.test_constants.FROM_EVENT_DATA:
            return ()
        raise ValueError('Trying to use GlobalResolver with type that is not supported by GlobalResolver: {}'.format(participant_type))


class AffordanceResolver(Resolver):

    def __init__(self, affordance, actor):
        super().__init__(skip_safe_tests=False, search_for_tooltip=False)
        self.affordance = affordance
        self.actor = actor

    def __repr__(self):
        return 'AffordanceResolver: affordance: {}, actor {}'.format(self.affordance, self.actor)

    def get_participants(self, participant_type, **kwargs):
        if participant_type == event_testing.test_constants.FROM_DATA_OBJECT:
            return ()
        if participant_type == event_testing.test_constants.OBJECTIVE_GUID64:
            return ()
        if participant_type == event_testing.test_constants.FROM_EVENT_DATA:
            return ()
        if participant_type == event_testing.test_constants.SIM_INSTANCE or participant_type == ParticipantType.Actor:
            if self.actor is not None:
                result = _to_sim_info(self.actor)
                if result:
                    return (
                     result,)
            return ()
        if participant_type == 0:
            logger.error('Calling get_participants with no flags on {}.', self)
            return ()
        if participant_type == ParticipantType.Affordance:
            return (
             self.affordance,)
        if participant_type == ParticipantType.AllRelationships:
            return (
             ParticipantType.AllRelationships,)
        return (self._get_participants_base)(participant_type, **kwargs)

    def __call__(self, test):
        if not test.supports_early_testing():
            return True
        if test.participants_for_early_testing is None:
            test.participants_for_early_testing = tuple(test.get_expected_args().values())
        for participant in test.participants_for_early_testing:
            if self.get_participants(participant) is None:
                return TestResult.TRUE

        return super().__call__(test)


class InteractionResolver(Resolver):

    def __init__(self, affordance, interaction, target=DEFAULT, context=DEFAULT, custom_sim=None, super_interaction=None, skip_safe_tests=False, search_for_tooltip=False, **interaction_parameters):
        super().__init__(skip_safe_tests, search_for_tooltip)
        self.affordance = affordance
        self._interaction = interaction
        self.target = interaction.target if target is DEFAULT else target
        self.context = interaction.context if context is DEFAULT else context
        self.custom_sim = custom_sim
        self.super_interaction = super_interaction
        self.interaction_parameters = interaction_parameters

    def __repr__(self):
        return 'InteractionResolver: affordance: {}, interaction:{}, target: {}, context: {}, si: {}'.format(self.affordance, self.interaction, self.target, self.context, self.super_interaction)

    @property
    def interaction(self):
        return self._interaction

    @property
    def profile_metric_key(self):
        if self.affordance is None:
            return 'NoAffordance'
        return self.affordance.__name__

    def get_participants--- This code section failed: ---

 L. 485         0  LOAD_FAST                'participant_type'
                2  LOAD_GLOBAL              event_testing
                4  LOAD_ATTR                test_constants
                6  LOAD_ATTR                SIM_INSTANCE
                8  COMPARE_OP               ==
               10  POP_JUMP_IF_FALSE    18  'to 18'

 L. 486        12  LOAD_GLOBAL              ParticipantType
               14  LOAD_ATTR                Actor
               16  STORE_FAST               'participant_type'
             18_0  COME_FROM            10  '10'

 L. 489        18  LOAD_FAST                'participant_type'
               20  LOAD_GLOBAL              ParticipantType
               22  LOAD_ATTR                Actor
               24  COMPARE_OP               ==
               26  POP_JUMP_IF_FALSE    74  'to 74'

 L. 490        28  LOAD_FAST                'self'
               30  LOAD_ATTR                context
               32  LOAD_ATTR                sim
               34  STORE_FAST               'sim'

 L. 495        36  LOAD_FAST                'sim'
               38  LOAD_CONST               None
               40  COMPARE_OP               is-not
               42  POP_JUMP_IF_FALSE    70  'to 70'

 L. 496        44  LOAD_GLOBAL              _to_sim_info
               46  LOAD_FAST                'sim'
               48  CALL_FUNCTION_1       1  '1 positional argument'
               50  STORE_FAST               'result'

 L. 497        52  LOAD_FAST                'result'
               54  LOAD_CONST               None
               56  COMPARE_OP               is-not
               58  POP_JUMP_IF_FALSE    66  'to 66'

 L. 498        60  LOAD_FAST                'result'
               62  BUILD_TUPLE_1         1 
               64  RETURN_VALUE     
             66_0  COME_FROM            58  '58'

 L. 499        66  LOAD_CONST               ()
               68  RETURN_VALUE     
             70_0  COME_FROM            42  '42'
            70_72  JUMP_FORWARD        870  'to 870'
             74_0  COME_FROM            26  '26'

 L. 500        74  LOAD_FAST                'participant_type'
               76  LOAD_GLOBAL              ParticipantType
               78  LOAD_ATTR                Object
               80  COMPARE_OP               ==
               82  POP_JUMP_IF_FALSE   122  'to 122'

 L. 501        84  LOAD_FAST                'self'
               86  LOAD_ATTR                target
               88  LOAD_CONST               None
               90  COMPARE_OP               is-not
               92  POP_JUMP_IF_FALSE   118  'to 118'

 L. 502        94  LOAD_GLOBAL              _to_sim_info
               96  LOAD_FAST                'self'
               98  LOAD_ATTR                target
              100  CALL_FUNCTION_1       1  '1 positional argument'
              102  STORE_FAST               'result'

 L. 503       104  LOAD_FAST                'result'
              106  LOAD_CONST               None
              108  COMPARE_OP               is-not
              110  POP_JUMP_IF_FALSE   118  'to 118'

 L. 504       112  LOAD_FAST                'result'
              114  BUILD_TUPLE_1         1 
              116  RETURN_VALUE     
            118_0  COME_FROM           110  '110'
            118_1  COME_FROM            92  '92'

 L. 505       118  LOAD_CONST               ()
              120  RETURN_VALUE     
            122_0  COME_FROM            82  '82'

 L. 506       122  LOAD_FAST                'participant_type'
              124  LOAD_GLOBAL              ParticipantType
              126  LOAD_ATTR                ObjectIngredients
              128  COMPARE_OP               ==
              130  POP_JUMP_IF_FALSE   184  'to 184'

 L. 507       132  LOAD_FAST                'self'
              134  LOAD_ATTR                target
              136  LOAD_CONST               None
              138  COMPARE_OP               is-not
              140  POP_JUMP_IF_FALSE   180  'to 180'

 L. 508       142  LOAD_FAST                'self'
              144  LOAD_ATTR                target
              146  LOAD_ATTR                crafting_component
              148  POP_JUMP_IF_FALSE   180  'to 180'

 L. 509       150  LOAD_FAST                'self'
              152  LOAD_ATTR                target
              154  LOAD_METHOD              get_crafting_process
              156  CALL_METHOD_0         0  '0 positional arguments'
              158  STORE_FAST               'target_crafting_process'

 L. 510       160  LOAD_FAST                'target_crafting_process'
              162  LOAD_CONST               None
              164  COMPARE_OP               is-not
              166  POP_JUMP_IF_FALSE   180  'to 180'

 L. 511       168  LOAD_GLOBAL              tuple
              170  LOAD_FAST                'target_crafting_process'
              172  LOAD_METHOD              get_ingredients_object_definitions
              174  CALL_METHOD_0         0  '0 positional arguments'
              176  CALL_FUNCTION_1       1  '1 positional argument'
              178  RETURN_VALUE     
            180_0  COME_FROM           166  '166'
            180_1  COME_FROM           148  '148'
            180_2  COME_FROM           140  '140'

 L. 512       180  LOAD_CONST               ()
              182  RETURN_VALUE     
            184_0  COME_FROM           130  '130'

 L. 513       184  LOAD_FAST                'participant_type'
              186  LOAD_GLOBAL              ParticipantType
              188  LOAD_ATTR                ObjectTrendiOutfitTrend
              190  COMPARE_OP               ==
              192  POP_JUMP_IF_TRUE    206  'to 206'

 L. 514       194  LOAD_FAST                'participant_type'
              196  LOAD_GLOBAL              ParticipantType
              198  LOAD_ATTR                ObjectTrendiOutfitTrendTag
              200  COMPARE_OP               ==
          202_204  POP_JUMP_IF_FALSE   320  'to 320'
            206_0  COME_FROM           192  '192'

 L. 515       206  LOAD_FAST                'self'
              208  LOAD_ATTR                target
              210  LOAD_CONST               None
              212  COMPARE_OP               is-not
          214_216  POP_JUMP_IF_FALSE   316  'to 316'

 L. 516       218  LOAD_GLOBAL              services
              220  LOAD_METHOD              fashion_trend_service
              222  CALL_METHOD_0         0  '0 positional arguments'
              224  STORE_FAST               'fashion_trend_service'

 L. 517       226  LOAD_FAST                'fashion_trend_service'
              228  LOAD_CONST               None
              230  COMPARE_OP               is-not
          232_234  POP_JUMP_IF_FALSE   316  'to 316'

 L. 518       236  LOAD_FAST                'participant_type'
              238  LOAD_GLOBAL              ParticipantType
              240  LOAD_ATTR                ObjectTrendiOutfitTrend
              242  COMPARE_OP               ==
          244_246  POP_JUMP_IF_FALSE   276  'to 276'

 L. 519       248  LOAD_FAST                'fashion_trend_service'
              250  LOAD_METHOD              get_outfit_prevalent_trend
              252  LOAD_FAST                'self'
              254  LOAD_ATTR                target
              256  CALL_METHOD_1         1  '1 positional argument'
              258  STORE_FAST               'outfit_trend'

 L. 520       260  LOAD_FAST                'outfit_trend'
              262  LOAD_CONST               None
              264  COMPARE_OP               is-not
          266_268  POP_JUMP_IF_FALSE   276  'to 276'

 L. 521       270  LOAD_FAST                'outfit_trend'
              272  BUILD_TUPLE_1         1 
              274  RETURN_VALUE     
            276_0  COME_FROM           266  '266'
            276_1  COME_FROM           244  '244'

 L. 522       276  LOAD_FAST                'participant_type'
              278  LOAD_GLOBAL              ParticipantType
              280  LOAD_ATTR                ObjectTrendiOutfitTrendTag
              282  COMPARE_OP               ==
          284_286  POP_JUMP_IF_FALSE   316  'to 316'

 L. 523       288  LOAD_FAST                'fashion_trend_service'
              290  LOAD_METHOD              get_outfit_prevalent_trend_tag
              292  LOAD_FAST                'self'
              294  LOAD_ATTR                target
              296  CALL_METHOD_1         1  '1 positional argument'
              298  STORE_FAST               'outfit_trend_tag'

 L. 524       300  LOAD_FAST                'outfit_trend_tag'
              302  LOAD_CONST               None
              304  COMPARE_OP               is-not
          306_308  POP_JUMP_IF_FALSE   316  'to 316'

 L. 525       310  LOAD_FAST                'outfit_trend_tag'
              312  BUILD_TUPLE_1         1 
              314  RETURN_VALUE     
            316_0  COME_FROM           306  '306'
            316_1  COME_FROM           284  '284'
            316_2  COME_FROM           232  '232'
            316_3  COME_FROM           214  '214'

 L. 526       316  LOAD_CONST               ()
              318  RETURN_VALUE     
            320_0  COME_FROM           202  '202'

 L. 527       320  LOAD_FAST                'participant_type'
              322  LOAD_GLOBAL              ParticipantType
              324  LOAD_ATTR                TargetSim
              326  COMPARE_OP               ==
          328_330  POP_JUMP_IF_FALSE   384  'to 384'

 L. 528       332  LOAD_FAST                'self'
              334  LOAD_ATTR                target
              336  LOAD_CONST               None
              338  COMPARE_OP               is-not
          340_342  POP_JUMP_IF_FALSE   380  'to 380'
              344  LOAD_FAST                'self'
              346  LOAD_ATTR                target
              348  LOAD_ATTR                is_sim
          350_352  POP_JUMP_IF_FALSE   380  'to 380'

 L. 529       354  LOAD_GLOBAL              _to_sim_info
              356  LOAD_FAST                'self'
              358  LOAD_ATTR                target
              360  CALL_FUNCTION_1       1  '1 positional argument'
              362  STORE_FAST               'result'

 L. 530       364  LOAD_FAST                'result'
              366  LOAD_CONST               None
              368  COMPARE_OP               is-not
          370_372  POP_JUMP_IF_FALSE   380  'to 380'

 L. 531       374  LOAD_FAST                'result'
              376  BUILD_TUPLE_1         1 
              378  RETURN_VALUE     
            380_0  COME_FROM           370  '370'
            380_1  COME_FROM           350  '350'
            380_2  COME_FROM           340  '340'

 L. 532       380  LOAD_CONST               ()
              382  RETURN_VALUE     
            384_0  COME_FROM           328  '328'

 L. 533       384  LOAD_FAST                'participant_type'
              386  LOAD_GLOBAL              ParticipantType
              388  LOAD_ATTR                ActorPostureTarget
              390  COMPARE_OP               ==
          392_394  POP_JUMP_IF_FALSE   452  'to 452'

 L. 534       396  LOAD_FAST                'self'
              398  LOAD_ATTR                interaction
              400  LOAD_CONST               None
              402  COMPARE_OP               is-not
          404_406  POP_JUMP_IF_FALSE   422  'to 422'

 L. 535       408  LOAD_FAST                'self'
              410  LOAD_ATTR                interaction
              412  LOAD_ATTR                get_participants
              414  LOAD_FAST                'participant_type'
              416  LOAD_CONST               ('participant_type',)
              418  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              420  RETURN_VALUE     
            422_0  COME_FROM           404  '404'

 L. 536       422  LOAD_FAST                'self'
              424  LOAD_ATTR                super_interaction
              426  LOAD_CONST               None
              428  COMPARE_OP               is-not
          430_432  POP_JUMP_IF_FALSE   870  'to 870'

 L. 537       434  LOAD_FAST                'self'
              436  LOAD_ATTR                super_interaction
              438  LOAD_ATTR                get_participants
              440  LOAD_FAST                'participant_type'
              442  LOAD_CONST               ('participant_type',)
              444  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              446  RETURN_VALUE     
          448_450  JUMP_FORWARD        870  'to 870'
            452_0  COME_FROM           392  '392'

 L. 538       452  LOAD_FAST                'participant_type'
              454  LOAD_GLOBAL              ParticipantType
              456  LOAD_ATTR                AssociatedClub
              458  COMPARE_OP               ==
          460_462  POP_JUMP_IF_TRUE    488  'to 488'

 L. 539       464  LOAD_FAST                'participant_type'
              466  LOAD_GLOBAL              ParticipantType
              468  LOAD_ATTR                AssociatedClubLeader
              470  COMPARE_OP               ==
          472_474  POP_JUMP_IF_TRUE    488  'to 488'

 L. 540       476  LOAD_FAST                'participant_type'
              478  LOAD_GLOBAL              ParticipantType
              480  LOAD_ATTR                AssociatedClubMembers
              482  COMPARE_OP               ==
          484_486  POP_JUMP_IF_FALSE   598  'to 598'
            488_0  COME_FROM           472  '472'
            488_1  COME_FROM           460  '460'

 L. 541       488  LOAD_FAST                'self'
              490  LOAD_ATTR                interaction_parameters
              492  LOAD_METHOD              get
              494  LOAD_STR                 'associated_club'
              496  CALL_METHOD_1         1  '1 positional argument'
              498  STORE_FAST               'associated_club'

 L. 542       500  LOAD_FAST                'self'
              502  LOAD_ATTR                interaction
              504  LOAD_CONST               None
              506  COMPARE_OP               is
          508_510  POP_JUMP_IF_FALSE   524  'to 524'
              512  LOAD_FAST                'self'
              514  LOAD_ATTR                super_interaction
              516  LOAD_CONST               None
              518  COMPARE_OP               is
          520_522  POP_JUMP_IF_TRUE    534  'to 534'
            524_0  COME_FROM           508  '508'

 L. 543       524  LOAD_FAST                'associated_club'
              526  LOAD_CONST               None
              528  COMPARE_OP               is-not
          530_532  POP_JUMP_IF_FALSE   870  'to 870'
            534_0  COME_FROM           520  '520'

 L. 544       534  LOAD_FAST                'participant_type'
              536  LOAD_GLOBAL              ParticipantType
              538  LOAD_ATTR                AssociatedClubLeader
              540  COMPARE_OP               ==
          542_544  POP_JUMP_IF_FALSE   554  'to 554'

 L. 545       546  LOAD_FAST                'associated_club'
              548  LOAD_ATTR                leader
              550  BUILD_TUPLE_1         1 
              552  RETURN_VALUE     
            554_0  COME_FROM           542  '542'

 L. 546       554  LOAD_FAST                'participant_type'
              556  LOAD_GLOBAL              ParticipantType
              558  LOAD_ATTR                AssociatedClub
              560  COMPARE_OP               ==
          562_564  POP_JUMP_IF_FALSE   572  'to 572'

 L. 547       566  LOAD_FAST                'associated_club'
              568  BUILD_TUPLE_1         1 
              570  RETURN_VALUE     
            572_0  COME_FROM           562  '562'

 L. 548       572  LOAD_FAST                'participant_type'
              574  LOAD_GLOBAL              ParticipantType
              576  LOAD_ATTR                AssociatedClubMembers
              578  COMPARE_OP               ==
          580_582  POP_JUMP_IF_FALSE   870  'to 870'

 L. 549       584  LOAD_GLOBAL              tuple
              586  LOAD_FAST                'associated_club'
              588  LOAD_ATTR                members
              590  CALL_FUNCTION_1       1  '1 positional argument'
              592  RETURN_VALUE     
          594_596  JUMP_FORWARD        870  'to 870'
            598_0  COME_FROM           484  '484'

 L. 550       598  LOAD_FAST                'participant_type'
              600  LOAD_GLOBAL              ParticipantType
              602  LOAD_ATTR                ObjectCrafter
              604  COMPARE_OP               ==
          606_608  POP_JUMP_IF_FALSE   692  'to 692'

 L. 551       610  LOAD_FAST                'self'
              612  LOAD_ATTR                target
              614  LOAD_CONST               None
              616  COMPARE_OP               is
          618_620  POP_JUMP_IF_TRUE    636  'to 636'
              622  LOAD_FAST                'self'
              624  LOAD_ATTR                target
              626  LOAD_ATTR                crafting_component
              628  LOAD_CONST               None
              630  COMPARE_OP               is
          632_634  POP_JUMP_IF_FALSE   640  'to 640'
            636_0  COME_FROM           618  '618'

 L. 552       636  LOAD_CONST               ()
              638  RETURN_VALUE     
            640_0  COME_FROM           632  '632'

 L. 553       640  LOAD_FAST                'self'
              642  LOAD_ATTR                target
              644  LOAD_METHOD              get_crafting_process
              646  CALL_METHOD_0         0  '0 positional arguments'
              648  STORE_FAST               'crafting_process'

 L. 554       650  LOAD_FAST                'crafting_process'
              652  LOAD_CONST               None
              654  COMPARE_OP               is
          656_658  POP_JUMP_IF_FALSE   664  'to 664'

 L. 555       660  LOAD_CONST               ()
              662  RETURN_VALUE     
            664_0  COME_FROM           656  '656'

 L. 556       664  LOAD_FAST                'crafting_process'
              666  LOAD_METHOD              get_crafter_sim_info
              668  CALL_METHOD_0         0  '0 positional arguments'
              670  STORE_FAST               'crafter_sim_info'

 L. 557       672  LOAD_FAST                'crafter_sim_info'
              674  LOAD_CONST               None
              676  COMPARE_OP               is
          678_680  POP_JUMP_IF_FALSE   686  'to 686'

 L. 558       682  LOAD_CONST               ()
              684  RETURN_VALUE     
            686_0  COME_FROM           678  '678'

 L. 559       686  LOAD_FAST                'crafter_sim_info'
              688  BUILD_TUPLE_1         1 
              690  RETURN_VALUE     
            692_0  COME_FROM           606  '606'

 L. 560       692  LOAD_FAST                'participant_type'
              694  LOAD_GLOBAL              ParticipantTypeSituationSims
              696  COMPARE_OP               in
          698_700  POP_JUMP_IF_FALSE   820  'to 820'

 L. 561       702  LOAD_CONST               None
              704  STORE_FAST               'provider_source'

 L. 562       706  LOAD_FAST                'self'
              708  LOAD_ATTR                _interaction
              710  LOAD_CONST               None
              712  COMPARE_OP               is-not
          714_716  POP_JUMP_IF_FALSE   726  'to 726'

 L. 563       718  LOAD_FAST                'self'
              720  LOAD_ATTR                _interaction
              722  STORE_FAST               'provider_source'
              724  JUMP_FORWARD        764  'to 764'
            726_0  COME_FROM           714  '714'

 L. 564       726  LOAD_FAST                'self'
              728  LOAD_ATTR                super_interaction
              730  LOAD_CONST               None
              732  COMPARE_OP               is-not
          734_736  POP_JUMP_IF_FALSE   746  'to 746'

 L. 565       738  LOAD_FAST                'self'
              740  LOAD_ATTR                super_interaction
              742  STORE_FAST               'provider_source'
              744  JUMP_FORWARD        764  'to 764'
            746_0  COME_FROM           734  '734'

 L. 566       746  LOAD_FAST                'self'
              748  LOAD_ATTR                affordance
              750  LOAD_CONST               None
              752  COMPARE_OP               is-not
          754_756  POP_JUMP_IF_FALSE   764  'to 764'

 L. 567       758  LOAD_FAST                'self'
              760  LOAD_ATTR                affordance
              762  STORE_FAST               'provider_source'
            764_0  COME_FROM           754  '754'
            764_1  COME_FROM           744  '744'
            764_2  COME_FROM           724  '724'

 L. 569       764  LOAD_FAST                'provider_source'
              766  LOAD_CONST               None
              768  COMPARE_OP               is-not
          770_772  POP_JUMP_IF_FALSE   870  'to 870'

 L. 570       774  LOAD_FAST                'provider_source'
              776  LOAD_METHOD              get_situation_participant_provider
              778  CALL_METHOD_0         0  '0 positional arguments'
              780  STORE_FAST               'provider'

 L. 571       782  LOAD_FAST                'provider'
              784  LOAD_CONST               None
              786  COMPARE_OP               is-not
          788_790  POP_JUMP_IF_FALSE   804  'to 804'

 L. 572       792  LOAD_FAST                'provider'
              794  LOAD_METHOD              get_participants
              796  LOAD_FAST                'participant_type'
              798  LOAD_FAST                'self'
              800  CALL_METHOD_2         2  '2 positional arguments'
              802  RETURN_VALUE     
            804_0  COME_FROM           788  '788'

 L. 574       804  LOAD_GLOBAL              logger
              806  LOAD_METHOD              error
              808  LOAD_STR                 "Requesting {} in {} that doesn't have a SituationSimParticipantProviderLiability"
              810  LOAD_FAST                'participant_type'
              812  LOAD_FAST                'provider_source'
              814  CALL_METHOD_3         3  '3 positional arguments'
              816  POP_TOP          
              818  JUMP_FORWARD        870  'to 870'
            820_0  COME_FROM           698  '698'

 L. 575       820  LOAD_FAST                'participant_type'
              822  LOAD_GLOBAL              ParticipantType
              824  LOAD_ATTR                ObjectLotLevel
              826  COMPARE_OP               ==
          828_830  POP_JUMP_IF_FALSE   844  'to 844'

 L. 576       832  LOAD_FAST                'self'
              834  LOAD_METHOD              _get_lot_level_from_object
              836  LOAD_FAST                'self'
              838  LOAD_ATTR                target
              840  CALL_METHOD_1         1  '1 positional argument'
              842  RETURN_VALUE     
            844_0  COME_FROM           828  '828'

 L. 577       844  LOAD_FAST                'participant_type'
              846  LOAD_GLOBAL              ParticipantType
              848  LOAD_ATTR                ActorLotLevel
              850  COMPARE_OP               ==
          852_854  POP_JUMP_IF_FALSE   870  'to 870'

 L. 578       856  LOAD_FAST                'self'
              858  LOAD_METHOD              _get_lot_level_from_object
              860  LOAD_FAST                'self'
              862  LOAD_ATTR                context
              864  LOAD_ATTR                sim
              866  CALL_METHOD_1         1  '1 positional argument'
              868  RETURN_VALUE     
            870_0  COME_FROM           852  '852'
            870_1  COME_FROM           818  '818'
            870_2  COME_FROM           770  '770'
            870_3  COME_FROM           594  '594'
            870_4  COME_FROM           580  '580'
            870_5  COME_FROM           530  '530'
            870_6  COME_FROM           448  '448'
            870_7  COME_FROM           430  '430'
            870_8  COME_FROM            70  '70'

 L. 580       870  LOAD_FAST                'participant_type'
              872  LOAD_CONST               0
              874  COMPARE_OP               ==
          876_878  POP_JUMP_IF_FALSE   896  'to 896'

 L. 581       880  LOAD_GLOBAL              logger
              882  LOAD_METHOD              error
              884  LOAD_STR                 'Calling get_participants with no flags on {}.'
              886  LOAD_FAST                'self'
              888  CALL_METHOD_2         2  '2 positional arguments'
              890  POP_TOP          

 L. 582       892  LOAD_CONST               ()
              894  RETURN_VALUE     
            896_0  COME_FROM           876  '876'

 L. 583       896  LOAD_FAST                'self'
              898  LOAD_ATTR                _get_participants_base
              900  LOAD_FAST                'participant_type'
              902  BUILD_TUPLE_1         1 
              904  LOAD_FAST                'kwargs'
              906  CALL_FUNCTION_EX_KW     1  'keyword and positional arguments'
              908  STORE_FAST               'result'

 L. 584       910  LOAD_FAST                'result'
              912  LOAD_CONST               None
              914  COMPARE_OP               is-not
          916_918  POP_JUMP_IF_FALSE   924  'to 924'

 L. 585       920  LOAD_FAST                'result'
              922  RETURN_VALUE     
            924_0  COME_FROM           916  '916'

 L. 590       924  LOAD_FAST                'participant_type'
              926  LOAD_GLOBAL              event_testing
              928  LOAD_ATTR                test_constants
              930  LOAD_ATTR                FROM_DATA_OBJECT
              932  COMPARE_OP               ==
          934_936  POP_JUMP_IF_FALSE   942  'to 942'

 L. 591       938  LOAD_CONST               ()
              940  RETURN_VALUE     
            942_0  COME_FROM           934  '934'

 L. 592       942  LOAD_FAST                'participant_type'
              944  LOAD_GLOBAL              event_testing
              946  LOAD_ATTR                test_constants
              948  LOAD_ATTR                OBJECTIVE_GUID64
              950  COMPARE_OP               ==
          952_954  POP_JUMP_IF_FALSE   960  'to 960'

 L. 593       956  LOAD_CONST               ()
              958  RETURN_VALUE     
            960_0  COME_FROM           952  '952'

 L. 594       960  LOAD_FAST                'participant_type'
              962  LOAD_GLOBAL              event_testing
              964  LOAD_ATTR                test_constants
              966  LOAD_ATTR                FROM_EVENT_DATA
              968  COMPARE_OP               ==
          970_972  POP_JUMP_IF_FALSE   978  'to 978'

 L. 595       974  LOAD_CONST               ()
              976  RETURN_VALUE     
            978_0  COME_FROM           970  '970'

 L. 597       978  LOAD_FAST                'participant_type'
              980  LOAD_GLOBAL              ParticipantType
              982  LOAD_ATTR                Affordance
              984  COMPARE_OP               ==
          986_988  POP_JUMP_IF_FALSE   998  'to 998'

 L. 598       990  LOAD_FAST                'self'
              992  LOAD_ATTR                affordance
              994  BUILD_TUPLE_1         1 
              996  RETURN_VALUE     
            998_0  COME_FROM           986  '986'

 L. 599       998  LOAD_FAST                'participant_type'
             1000  LOAD_GLOBAL              ParticipantType
             1002  LOAD_ATTR                InteractionContext
             1004  COMPARE_OP               ==
         1006_1008  POP_JUMP_IF_FALSE  1018  'to 1018'

 L. 600      1010  LOAD_FAST                'self'
             1012  LOAD_ATTR                context
             1014  BUILD_TUPLE_1         1 
             1016  RETURN_VALUE     
           1018_0  COME_FROM          1006  '1006'

 L. 601      1018  LOAD_FAST                'participant_type'
             1020  LOAD_GLOBAL              ParticipantType
             1022  LOAD_ATTR                CustomSim
             1024  COMPARE_OP               ==
         1026_1028  POP_JUMP_IF_FALSE  1062  'to 1062'

 L. 602      1030  LOAD_FAST                'self'
             1032  LOAD_ATTR                custom_sim
             1034  LOAD_CONST               None
             1036  COMPARE_OP               is-not
         1038_1040  POP_JUMP_IF_FALSE  1052  'to 1052'

 L. 603      1042  LOAD_FAST                'self'
             1044  LOAD_ATTR                custom_sim
             1046  LOAD_ATTR                sim_info
             1048  BUILD_TUPLE_1         1 
             1050  RETURN_VALUE     
           1052_0  COME_FROM          1038  '1038'

 L. 605      1052  LOAD_GLOBAL              ValueError
             1054  LOAD_STR                 'Trying to use CustomSim without passing a custom_sim in InteractionResolver.'
             1056  CALL_FUNCTION_1       1  '1 positional argument'
             1058  POP_TOP          
             1060  JUMP_FORWARD       1082  'to 1082'
           1062_0  COME_FROM          1026  '1026'

 L. 606      1062  LOAD_FAST                'participant_type'
             1064  LOAD_GLOBAL              ParticipantType
             1066  LOAD_ATTR                AllRelationships
             1068  COMPARE_OP               ==
         1070_1072  POP_JUMP_IF_FALSE  1082  'to 1082'

 L. 610      1074  LOAD_GLOBAL              ParticipantType
             1076  LOAD_ATTR                AllRelationships
             1078  BUILD_TUPLE_1         1 
             1080  RETURN_VALUE     
           1082_0  COME_FROM          1070  '1070'
           1082_1  COME_FROM          1060  '1060'

 L. 612      1082  LOAD_FAST                'participant_type'
             1084  LOAD_GLOBAL              ParticipantType
             1086  LOAD_ATTR                PickedItemId
             1088  COMPARE_OP               ==
         1090_1092  POP_JUMP_IF_FALSE  1120  'to 1120'

 L. 613      1094  LOAD_FAST                'self'
             1096  LOAD_ATTR                interaction_parameters
             1098  LOAD_METHOD              get
             1100  LOAD_STR                 'picked_item_ids'
             1102  CALL_METHOD_1         1  '1 positional argument'
             1104  STORE_FAST               'picked_item_ids'

 L. 614      1106  LOAD_FAST                'picked_item_ids'
             1108  LOAD_CONST               None
             1110  COMPARE_OP               is-not
         1112_1114  POP_JUMP_IF_FALSE  1120  'to 1120'

 L. 615      1116  LOAD_FAST                'picked_item_ids'
             1118  RETURN_VALUE     
           1120_0  COME_FROM          1112  '1112'
           1120_1  COME_FROM          1090  '1090'

 L. 618      1120  LOAD_FAST                'self'
             1122  LOAD_ATTR                interaction
             1124  LOAD_CONST               None
             1126  COMPARE_OP               is-not
         1128_1130  POP_JUMP_IF_FALSE  1170  'to 1170'

 L. 619      1132  LOAD_FAST                'self'
             1134  LOAD_ATTR                interaction
             1136  LOAD_ATTR                get_participants
             1138  BUILD_TUPLE_0         0 
             1140  LOAD_FAST                'participant_type'

 L. 620      1142  LOAD_FAST                'self'
             1144  LOAD_ATTR                context
             1146  LOAD_ATTR                sim
             1148  LOAD_FAST                'self'
             1150  LOAD_ATTR                target

 L. 621      1152  LOAD_CONST               False
             1154  LOAD_CONST               ('participant_type', 'sim', 'target', 'listener_filtering_enabled')
             1156  BUILD_CONST_KEY_MAP_4     4 

 L. 622      1158  LOAD_FAST                'self'
             1160  LOAD_ATTR                interaction_parameters
             1162  BUILD_MAP_UNPACK_WITH_CALL_2     2 
             1164  CALL_FUNCTION_EX_KW     1  'keyword and positional arguments'
             1166  STORE_FAST               'participants'
             1168  JUMP_FORWARD       1274  'to 1274'
           1170_0  COME_FROM          1128  '1128'

 L. 623      1170  LOAD_FAST                'self'
             1172  LOAD_ATTR                super_interaction
             1174  LOAD_CONST               None
             1176  COMPARE_OP               is-not
         1178_1180  POP_JUMP_IF_FALSE  1226  'to 1226'

 L. 629      1182  LOAD_FAST                'self'
             1184  LOAD_ATTR                super_interaction
             1186  LOAD_ATTR                get_participants
             1188  BUILD_TUPLE_0         0 
             1190  LOAD_FAST                'participant_type'

 L. 630      1192  LOAD_FAST                'self'
             1194  LOAD_ATTR                context
             1196  LOAD_ATTR                sim
             1198  LOAD_FAST                'self'
             1200  LOAD_ATTR                target

 L. 631      1202  LOAD_CONST               False

 L. 632      1204  LOAD_FAST                'self'
             1206  LOAD_ATTR                affordance
             1208  LOAD_ATTR                target_type
             1210  LOAD_CONST               ('participant_type', 'sim', 'target', 'listener_filtering_enabled', 'target_type')
             1212  BUILD_CONST_KEY_MAP_5     5 

 L. 633      1214  LOAD_FAST                'self'
             1216  LOAD_ATTR                interaction_parameters
             1218  BUILD_MAP_UNPACK_WITH_CALL_2     2 
             1220  CALL_FUNCTION_EX_KW     1  'keyword and positional arguments'
             1222  STORE_FAST               'participants'
             1224  JUMP_FORWARD       1274  'to 1274'
           1226_0  COME_FROM          1178  '1178'

 L. 635      1226  LOAD_FAST                'self'
             1228  LOAD_ATTR                affordance
             1230  LOAD_ATTR                get_participants
             1232  BUILD_TUPLE_0         0 
             1234  LOAD_FAST                'participant_type'

 L. 636      1236  LOAD_FAST                'self'
             1238  LOAD_ATTR                context
             1240  LOAD_ATTR                sim
             1242  LOAD_FAST                'self'
             1244  LOAD_ATTR                target

 L. 637      1246  LOAD_FAST                'self'
             1248  LOAD_ATTR                context
             1250  LOAD_ATTR                carry_target

 L. 638      1252  LOAD_CONST               False

 L. 639      1254  LOAD_FAST                'self'
             1256  LOAD_ATTR                affordance
             1258  LOAD_ATTR                target_type
             1260  LOAD_CONST               ('participant_type', 'sim', 'target', 'carry_target', 'listener_filtering_enabled', 'target_type')
             1262  BUILD_CONST_KEY_MAP_6     6 

 L. 640      1264  LOAD_FAST                'self'
             1266  LOAD_ATTR                interaction_parameters
             1268  BUILD_MAP_UNPACK_WITH_CALL_2     2 
             1270  CALL_FUNCTION_EX_KW     1  'keyword and positional arguments'
             1272  STORE_FAST               'participants'
           1274_0  COME_FROM          1224  '1224'
           1274_1  COME_FROM          1168  '1168'

 L. 641      1274  LOAD_GLOBAL              set
             1276  CALL_FUNCTION_0       0  '0 positional arguments'
             1278  STORE_FAST               'resolved_participants'

 L. 642      1280  SETUP_LOOP         1310  'to 1310'
             1282  LOAD_FAST                'participants'
             1284  GET_ITER         
             1286  FOR_ITER           1308  'to 1308'
             1288  STORE_FAST               'participant'

 L. 643      1290  LOAD_FAST                'resolved_participants'
             1292  LOAD_METHOD              add
             1294  LOAD_GLOBAL              _to_sim_info
             1296  LOAD_FAST                'participant'
             1298  CALL_FUNCTION_1       1  '1 positional argument'
             1300  CALL_METHOD_1         1  '1 positional argument'
             1302  POP_TOP          
         1304_1306  JUMP_BACK          1286  'to 1286'
             1308  POP_BLOCK        
           1310_0  COME_FROM_LOOP     1280  '1280'

 L. 645      1310  LOAD_GLOBAL              tuple
             1312  LOAD_FAST                'resolved_participants'
             1314  CALL_FUNCTION_1       1  '1 positional argument'
             1316  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `RETURN_VALUE' instruction at offset 1316

    def get_localization_tokens(self, *args, **kwargs):
        return (self.interaction.get_localization_tokens)(*args, **kwargs)


@caches.clearable_barebones_cache
def _to_sim_info(participant):
    sim_info = getattr(participant, 'sim_info', None)
    if sim_info is None or sim_info.is_baby:
        return participant
    return sim_info


class AwayActionResolver(Resolver):
    VALID_AWAY_ACTION_PARTICIPANTS = ParticipantType.Actor | ParticipantType.TargetSim | ParticipantType.Lot

    def __init__(self, away_action, skip_safe_tests=False, search_for_tooltip=False, **away_action_parameters):
        super().__init__(skip_safe_tests, search_for_tooltip)
        self.away_action = away_action
        self.away_action_parameters = away_action_parameters

    def __repr__(self):
        return 'AwayActionResolver: away_action: {}'.format(self.away_action)

    @property
    def sim(self):
        return self.get_participant(ParticipantType.Actor)

    def get_participants(self, participant_type, **kwargs):
        if participant_type == 0:
            logger.error('Calling get_participants with no flags on {}.', self)
            return ()
        if participant_type == ParticipantType.Lot:
            return (self.away_action.get_participants)(participant_type=participant_type, **self.away_action_parameters)
        result = self._get_participants_base(participant_type)
        if result is not None:
            return result
        if participant_type == event_testing.test_constants.FROM_DATA_OBJECT:
            return ()
        if participant_type == event_testing.test_constants.OBJECTIVE_GUID64:
            return ()
        if participant_type == event_testing.test_constants.FROM_EVENT_DATA:
            return ()
        if participant_type & AwayActionResolver.VALID_AWAY_ACTION_PARTICIPANTS:
            return (self.away_action.get_participants)(participant_type=participant_type, **self.away_action_parameters)
        raise ValueError('Trying to use AwayActionResolver without a valid type: {}'.format(participant_type))

    def get_localization_tokens(self, *args, **kwargs):
        return (self.interaction.get_localization_tokens)(*args, **kwargs)


class SingleSimResolver(Resolver):

    def __init__(self, sim_info_to_test, additional_participants={}, additional_localization_tokens=(), additional_metric_key_data=None):
        super().__init__(additional_metric_key_data=additional_metric_key_data)
        self.sim_info_to_test = sim_info_to_test
        self._additional_participants = additional_participants
        self._additional_localization_tokens = additional_localization_tokens
        self._source = None
        if event_testing.resolver.test_profile is not None:
            frame = sys._getframe(self.profile_metric_stack_depth)
            qualified_name = frame.f_code.co_filename
            unqualified_name = qualified_name.split('\\')[-1]
            self._source = unqualified_name

    def __repr__(self):
        return 'SingleSimResolver: sim_to_test: {}'.format(self.sim_info_to_test)

    @property
    def profile_metric_key(self):
        return '{}:{}'.format(self._source, self._additional_metric_key_data)

    @classproperty
    def profile_metric_stack_depth(cls):
        return 1

    def get_participants(self, participant_type, **kwargs):
        if participant_type == ParticipantType.Actor or participant_type == ParticipantType.CustomSim:
            return (
             self.sim_info_to_test,)
        if participant_type == ParticipantType.ActorHouseholdMembers:
            if self.sim_info_to_test is not None:
                if self.sim_info_to_test.household is not None:
                    return tuple(self.sim_info_to_test.household)
        if participant_type == ParticipantType.SignificantOtherActor:
            significant_other = self.sim_info_to_test.get_significant_other_sim_info()
            if significant_other is not None:
                return (significant_other,)
            return ()
        if participant_type == ParticipantType.PregnancyPartnerActor:
            pregnancy_partner = self.sim_info_to_test.pregnancy_tracker.get_partner()
            if pregnancy_partner is not None:
                return (pregnancy_partner,)
            return ()
        if participant_type == ParticipantType.AllRelationships:
            if self.sim_info_to_test:
                if self.sim_info_to_test.relationship_tracker:
                    infos = []
                    for sim_id in self.sim_info_to_test.relationship_tracker.target_sim_gen():
                        sim = services.sim_info_manager().get(sim_id)
                        infos.append(sim)

                    return tuple(infos)
            return ParticipantType.AllRelationships
        if participant_type == ParticipantType.ActorFeudTarget:
            feud_target = self.sim_info_to_test.get_feud_target()
            if feud_target is not None:
                return (feud_target,)
            return ()
        if participant_type == event_testing.test_constants.FROM_EVENT_DATA:
            return ()
        if participant_type == ParticipantType.InteractionContext or participant_type == ParticipantType.Affordance:
            return ()
        if participant_type == event_testing.test_constants.SIM_INSTANCE:
            return (
             self.sim_info_to_test,)
        if participant_type == ParticipantType.Familiar:
            return self._get_familiar_for_sim_info(self.sim_info_to_test)
        if participant_type in self._additional_participants:
            return self._additional_participants[participant_type]
        if participant_type == ParticipantType.PickedZoneId:
            return frozenset()
        if participant_type == ParticipantType.ActorLot:
            sim_home_lot = self.sim_info_to_test.get_home_lot()
            if sim_home_lot is None:
                return ()
            return (sim_home_lot,)
        if participant_type == ParticipantType.RoutingSlaves:
            sim_inst = self.sim_info_to_test.get_sim_instance()
            routing_slave_data = sim_inst.get_routing_slave_data() if sim_inst is not None else None
            if routing_slave_data is None:
                return ()
            return tuple({data.slave for data in routing_slave_data})
        if participant_type == ParticipantType.StoredCASPartsOnObject:
            return ()
        if participant_type == ParticipantType.ActorLotLevel:
            return self._get_lot_level_from_object(self.sim_info_to_test.get_sim_instance())
        if participant_type == ParticipantType.ActorClanLeader:
            clan_service = services.clan_service()
            if clan_service is None:
                return ()
            clan_leader = clan_service.get_clan_leader(self.sim_info_to_test)
            if clan_leader is None:
                return ()
            return (clan_leader,)
        if participant_type == ParticipantType.GraduatesCurrent:
            graduation_service = services.get_graduation_service()
            if graduation_service is None:
                return tuple()
            return tuple(graduation_service.current_graduating_sims())
        if participant_type == ParticipantType.GraduatesWaiting:
            graduation_service = services.get_graduation_service()
            if graduation_service is None:
                return tuple()
            return tuple(graduation_service.waiting_to_graduate_sims())
        if participant_type == ParticipantType.ActorHouseholdMembers and not self.sim_info_to_test is None:
            if self.sim_info_to_test.household is None:
                return tuple()
            return tuple(self.sim_info_to_test.household)
            if participant_type == ParticipantType.ActorBassinet:
                baby_bassinet = services.object_manager().get(self.sim_info_to_test.sim_id)
                return baby_bassinet is None or baby_bassinet.is_bassinet or ()
                return (baby_bassinet,)
            result = (self._get_participants_base)(participant_type, **kwargs)
            if result is not None:
                return result
        raise ValueError('Trying to use {} with unsupported participant: {}'.format(type(self).__name__, participant_type))

    def _get_familiar_for_sim_info(self, sim_info):
        familiar_tracker = self.sim_info_to_test.familiar_tracker
        if familiar_tracker is None:
            return ()
        familiar = familiar_tracker.get_active_familiar()
        if familiar is None:
            return ()
        if familiar.is_sim:
            return (
             familiar.sim_info,)
        return (
         familiar,)

    def get_localization_tokens(self, *args, **kwargs):
        return (
         self.sim_info_to_test,) + self._additional_localization_tokens

    def set_additional_participant(self, participant_type, value):
        self._additional_participants[participant_type] = value


class DoubleSimResolver(SingleSimResolver):

    def __init__(self, sim_info, target_sim_info, **kwargs):
        (super().__init__)(sim_info, **kwargs)
        self.target_sim_info = target_sim_info

    def __repr__(self):
        return 'DoubleSimResolver: sim: {} target_sim: {}'.format(self.sim_info_to_test, self.target_sim_info)

    @classproperty
    def profile_metric_stack_depth(cls):
        return 2

    def get_participants(self, participant_type, **kwargs):
        if participant_type == ParticipantType.TargetSim or participant_type == ParticipantType.Object:
            return (
             self.target_sim_info,)
        else:
            if participant_type == ParticipantType.TargetHouseholdMembers:
                if self.target_sim_info is not None:
                    if self.target_sim_info.household is not None:
                        return tuple(self.target_sim_info.household)
            if participant_type == ParticipantType.SignificantOtherTargetSim:
                return (
                 self.target_sim_info.get_significant_other_sim_info(),)
            if participant_type == ParticipantType.FamiliarOfTarget:
                return self._get_familiar_for_sim_info(self.target_sim_info)
            if participant_type == ParticipantType.TargetClanLeader and self.target_sim_info is not None:
                clan_service = services.clan_service()
                if clan_service is None:
                    return ()
                clan_leader = clan_service.get_clan_leader(self.target_sim_info)
                if clan_leader is None:
                    return ()
                return (clan_leader,)
        if participant_type == ParticipantType.TargetBassinet:
            baby_bassinet = services.object_manager().get(self.target_sim_info.sim_id)
            return baby_bassinet is None or baby_bassinet.is_bassinet or ()
            return (baby_bassinet,)
        return (super().get_participants)(participant_type, **kwargs)

    def get_localization_tokens(self, *args, **kwargs):
        return (
         self.sim_info_to_test, self.target_sim_info) + self._additional_localization_tokens


class SingleSimAndHouseholdResolver(SingleSimResolver):

    def __init__(self, sim_info, target_household, **kwargs):
        (super().__init__)(sim_info, **kwargs)
        self.target_household = target_household

    def __repr__(self):
        return 'SingleSimAndHouseholdResolver: sim: {} household: {}'.format(self.sim_info_to_test, self.target_household)

    @classproperty
    def profile_metric_stack_depth(cls):
        return 2

    def get_participants(self, participant_type, **kwargs):
        if participant_type == ParticipantType.TargetHousehold:
            return (
             self.target_household,)
        if participant_type == ParticipantType.TargetHouseholdMembers:
            return tuple(self.target_household)
        return (super().get_participants)(participant_type, **kwargs)


class DataResolver(Resolver):

    def __init__(self, sim_info, event_kwargs=None, custom_keys=(), additional_metric_key_data=None):
        super().__init__(additional_metric_key_data=additional_metric_key_data)
        self.sim_info = sim_info
        if event_kwargs is not None:
            self._interaction = event_kwargs.get('interaction', None)
            self.on_zone_load = event_kwargs.get('init', False)
        else:
            self._interaction = None
            self.on_zone_load = False
        self.event_kwargs = event_kwargs
        self.data_object = None
        self.objective_guid64 = None
        self.custom_keys = custom_keys

    def __repr__(self):
        return 'DataResolver: participant: {}'.format(self.sim_info)

    def __call__(self, test, data_object=None, objective_guid64=None):
        if data_object is not None:
            self.data_object = data_object
            self.objective_guid64 = objective_guid64
        return super().__call__(test)

    @property
    def interaction(self):
        return self._interaction

    @property
    def profile_metric_key(self):
        interaction_name = None
        if self._interaction is not None:
            interaction_name = self._interaction.aop.affordance.__name__
        objective_name = 'Invalid'
        additional_metric_key_str = 'Invalid'
        if self.objective_guid64 is not None:
            objective_manager = services.get_instance_manager(sims4.resources.Types.OBJECTIVE)
            objective = objective_manager.get(self.objective_guid64)
            objective_name = objective.__name__
        if self._additional_metric_key_data is not None:
            return 'objective:{} (interaction:{}) (additional_metric_key_data:{})'.formatobjective_nameinteraction_nameself._additional_metric_key_data
        return 'objective:{} (interaction:{})'.format(objective_name, interaction_name)

    def get_resolved_arg(self, key):
        return self.event_kwargs.get(key, None)

    def get_participants(self, participant_type, event_key=None):
        result = self._get_participants_base(participant_type, event_key=event_key)
        if result is not None:
            return result
        if participant_type == event_testing.test_constants.SIM_INSTANCE:
            return (
             self.sim_info,)
        if participant_type == event_testing.test_constants.FROM_DATA_OBJECT:
            return (
             self.data_object,)
        if participant_type == event_testing.test_constants.OBJECTIVE_GUID64:
            return (
             self.objective_guid64,)
        if participant_type == event_testing.test_constants.FROM_EVENT_DATA:
            if not self.event_kwargs:
                return ()
            return (
             self.event_kwargs.get(event_key),)
        if self._interaction is not None:
            return tuple((getattr(participant, 'sim_info', participant) for participant in self._interaction.get_participants(participant_type)))
        if participant_type == ParticipantType.Actor:
            return (
             self.sim_info,)
        if participant_type == ParticipantType.AllRelationships:
            sim_mgr = services.sim_info_manager()
            relations = set((sim_mgr.get(relations.get_other_sim_id(self.sim_info.sim_id)) for relations in self.sim_info.relationship_tracker))
            return tuple(relations)
        if participant_type == ParticipantType.TargetSim:
            if not self.event_kwargs:
                return ()
            target_sim_id = self.event_kwargs.get(event_testing.test_constants.TARGET_SIM_ID)
            if target_sim_id is None:
                return ()
            return (
             services.sim_info_manager().get(target_sim_id),)
        if participant_type == ParticipantType.ActiveHousehold:
            active_household = services.active_household()
            if active_household is not None:
                return tuple(active_household.sim_info_gen())
        if self.on_zone_load:
            return ()
        raise ValueError('Trying to use DataResolver with type that is not supported by DataResolver: {}'.format(participant_type))


class SingleObjectResolver(Resolver):

    def __init__(self, obj):
        super().__init__()
        self._obj = obj

    def __repr__(self):
        return 'SingleObjectResolver: object: {}'.format(self._obj)

    def get_participants(self, participant_type, **kwargs):
        if participant_type == ParticipantType.Object:
            return (
             self._obj,)
        if participant_type == ParticipantType.ObjectIngredients:
            if self._obj.crafting_component:
                crafting_process = self._obj.get_crafting_process()
                if crafting_process is not None:
                    return tuple(crafting_process.get_ingredients_object_definitions())
            return ()
        if participant_type == ParticipantType.ObjectTrendiOutfitTrend or participant_type == ParticipantType.ObjectTrendiOutfitTrendTag:
            if self._obj is not None:
                fashion_trend_service = services.fashion_trend_service()
                if fashion_trend_service is not None:
                    if participant_type == ParticipantType.ObjectTrendiOutfitTrend:
                        outfit_trend = fashion_trend_service.get_outfit_prevalent_trend(self._obj)
                        if outfit_trend is not None:
                            return (
                             outfit_trend,)
                    if participant_type == ParticipantType.ObjectTrendiOutfitTrendTag:
                        outfit_trend_tag = fashion_trend_service.get_outfit_prevalent_trend_tag(self._obj)
                        if outfit_trend_tag is not None:
                            return (
                             outfit_trend_tag,)
            return ()
        if participant_type == ParticipantType.Actor:
            return (
             self._obj,)
        if participant_type == ParticipantType.StoredSim:
            stored_sim_info = self._obj.get_stored_sim_info()
            return (stored_sim_info,)
        if participant_type == ParticipantType.StoredSim2:
            stored_sim_info2 = self._obj.get_secondary_stored_sim_info()
            return (stored_sim_info2,)
        if participant_type == ParticipantType.StoredSimOrNameData:
            stored_sim_name_data = self._obj.get_stored_sim_info_or_name_data()
            return (stored_sim_name_data,)
        if participant_type == ParticipantType.StoredSimOrNameDataList:
            stored_sim_name_data_list = self._obj.get_stored_sim_info_or_name_data_list()
            if len(stored_sim_name_data_list) != 0:
                return tuple(stored_sim_name_data_list)
            return ()
        if participant_type == ParticipantType.OwnerSim:
            owner_sim_info_id = self._obj.get_sim_owner_id()
            owner_sim_info = services.sim_info_manager().get(owner_sim_info_id)
            return (owner_sim_info,)
        if participant_type == ParticipantType.ObjectParent and not self._obj is None:
            if self._obj.parent is None:
                return ()
            return (
             self._obj.parent,)
            if participant_type == ParticipantType.ObjectChildren:
                if self._obj is None:
                    return ()
                if self._obj.is_part:
                    return tuple(self._obj.part_owner.children_recursive_gen())
                return tuple(self._obj.children_recursive_gen())
            if participant_type == ParticipantType.RandomInventoryObject:
                return (
                 random.choice(tuple(self._obj.inventory_component.visible_storage)),)
        if participant_type == ParticipantType.PickedObject or participant_type == ParticipantType.CarriedObject or participant_type == ParticipantType.LiveDragActor:
            if self._obj.is_sim:
                return (
                 self._obj.sim_info,)
            return (
             self._obj,)
        if participant_type == ParticipantType.RoutingOwner:
            routing_owner = self._obj.get_routing_owner()
            if routing_owner is None:
                return ()
            if routing_owner.is_sim:
                return (
                 routing_owner.sim_info,)
            return (routing_owner,)
        else:
            if participant_type == ParticipantType.RoutingTarget:
                routing_target = self._obj.get_routing_target()
                if routing_target is None:
                    return ()
                if routing_target.is_sim:
                    return (
                     routing_target.sim_info,)
                return (routing_target,)
            else:
                if participant_type == ParticipantType.StoredCASPartsOnObject:
                    stored_cas_parts = self._obj.get_stored_cas_parts()
                    if stored_cas_parts is None:
                        return ()
                    return tuple(iter(self._obj.get_stored_cas_parts()))
                if participant_type == ParticipantType.ObjectLotLevel or participant_type == ParticipantType.ActorLotLevel:
                    return self._get_lot_level_from_object(self._obj)
                if participant_type == ParticipantType.ObjectAnimalHome:
                    return self._get_animal_home_from_object(self._obj)
                if participant_type == ParticipantType.AnimalHomeAssignees:
                    return self._get_animal_home_assignees(self._obj)
                if participant_type == ParticipantType.ObjectRelationshipsComponent:
                    sim_ids = () if self._obj.objectrelationship_component is None else self._obj.objectrelationship_component.relationships.keys()
                    sim_info_manager = services.sim_info_manager()
                    relations = set((sim_info_manager.get(sim_id) for sim_id in sim_ids))
                    return tuple(relations)
                if participant_type == ParticipantType.GraduatesCurrent:
                    graduation_service = services.get_graduation_service()
                    if graduation_service is None:
                        return tuple()
                    return tuple(graduation_service.current_graduating_sims())
                if participant_type == ParticipantType.GraduatesWaiting:
                    graduation_service = services.get_graduation_service()
                    if graduation_service is None:
                        return tuple()
                    return tuple(graduation_service.waiting_to_graduate_sims())
                result = (self._get_participants_base)(participant_type, **kwargs)
                if result is not None:
                    return result
                if participant_type == event_testing.test_constants.FROM_EVENT_DATA:
                    return ()
                raise ValueError('Trying to use SingleObjectResolver with something that is not an Object: {}'.format(participant_type))

    def get_localization_tokens(self, *args, **kwargs):
        return (
         self._obj,)


class DoubleObjectResolver(Resolver):

    def __init__(self, source_obj, target_obj):
        super().__init__()
        self._source_obj = source_obj
        self._target_obj = target_obj

    def __repr__(self):
        return 'DoubleObjectResolver: actor_object: {}, target_object:{}'.format(self._source_obj, self._target_obj)

    def get_participants--- This code section failed: ---

 L.1267         0  LOAD_FAST                'self'
                2  LOAD_ATTR                _get_participants_base
                4  LOAD_FAST                'participant_type'
                6  BUILD_TUPLE_1         1 
                8  LOAD_FAST                'kwargs'
               10  CALL_FUNCTION_EX_KW     1  'keyword and positional arguments'
               12  STORE_FAST               'result'

 L.1268        14  LOAD_FAST                'result'
               16  LOAD_CONST               None
               18  COMPARE_OP               is-not
               20  POP_JUMP_IF_FALSE    26  'to 26'

 L.1269        22  LOAD_FAST                'result'
               24  RETURN_VALUE     
             26_0  COME_FROM            20  '20'

 L.1271        26  LOAD_FAST                'participant_type'
               28  LOAD_GLOBAL              ParticipantType
               30  LOAD_ATTR                Actor
               32  COMPARE_OP               ==
               34  POP_JUMP_IF_TRUE     66  'to 66'

 L.1272        36  LOAD_FAST                'participant_type'
               38  LOAD_GLOBAL              ParticipantType
               40  LOAD_ATTR                PickedObject
               42  COMPARE_OP               ==
               44  POP_JUMP_IF_TRUE     66  'to 66'

 L.1273        46  LOAD_FAST                'participant_type'
               48  LOAD_GLOBAL              ParticipantType
               50  LOAD_ATTR                CarriedObject
               52  COMPARE_OP               ==
               54  POP_JUMP_IF_TRUE     66  'to 66'

 L.1274        56  LOAD_FAST                'participant_type'
               58  LOAD_GLOBAL              ParticipantType
               60  LOAD_ATTR                LiveDragActor
               62  COMPARE_OP               ==
               64  POP_JUMP_IF_FALSE    92  'to 92'
             66_0  COME_FROM            54  '54'
             66_1  COME_FROM            44  '44'
             66_2  COME_FROM            34  '34'

 L.1275        66  LOAD_FAST                'self'
               68  LOAD_ATTR                _source_obj
               70  LOAD_ATTR                is_sim
               72  POP_JUMP_IF_FALSE    84  'to 84'

 L.1276        74  LOAD_FAST                'self'
               76  LOAD_ATTR                _source_obj
               78  LOAD_ATTR                sim_info
               80  BUILD_TUPLE_1         1 
               82  RETURN_VALUE     
             84_0  COME_FROM            72  '72'

 L.1277        84  LOAD_FAST                'self'
               86  LOAD_ATTR                _source_obj
               88  BUILD_TUPLE_1         1 
               90  RETURN_VALUE     
             92_0  COME_FROM            64  '64'

 L.1279        92  LOAD_FAST                'participant_type'
               94  LOAD_GLOBAL              ParticipantType
               96  LOAD_ATTR                Listeners
               98  COMPARE_OP               ==
              100  POP_JUMP_IF_TRUE    132  'to 132'

 L.1280       102  LOAD_FAST                'participant_type'
              104  LOAD_GLOBAL              ParticipantType
              106  LOAD_ATTR                Object
              108  COMPARE_OP               ==
              110  POP_JUMP_IF_TRUE    132  'to 132'

 L.1281       112  LOAD_FAST                'participant_type'
              114  LOAD_GLOBAL              ParticipantType
              116  LOAD_ATTR                TargetSim
              118  COMPARE_OP               ==
              120  POP_JUMP_IF_TRUE    132  'to 132'

 L.1282       122  LOAD_FAST                'participant_type'
              124  LOAD_GLOBAL              ParticipantType
              126  LOAD_ATTR                LiveDragTarget
              128  COMPARE_OP               ==
              130  POP_JUMP_IF_FALSE   158  'to 158'
            132_0  COME_FROM           120  '120'
            132_1  COME_FROM           110  '110'
            132_2  COME_FROM           100  '100'

 L.1283       132  LOAD_FAST                'self'
              134  LOAD_ATTR                _target_obj
              136  LOAD_ATTR                is_sim
              138  POP_JUMP_IF_FALSE   150  'to 150'

 L.1284       140  LOAD_FAST                'self'
              142  LOAD_ATTR                _target_obj
              144  LOAD_ATTR                sim_info
              146  BUILD_TUPLE_1         1 
              148  RETURN_VALUE     
            150_0  COME_FROM           138  '138'

 L.1285       150  LOAD_FAST                'self'
              152  LOAD_ATTR                _target_obj
              154  BUILD_TUPLE_1         1 
              156  RETURN_VALUE     
            158_0  COME_FROM           130  '130'

 L.1287       158  LOAD_FAST                'participant_type'
              160  LOAD_GLOBAL              event_testing
              162  LOAD_ATTR                test_constants
              164  LOAD_ATTR                FROM_EVENT_DATA
              166  COMPARE_OP               ==
              168  POP_JUMP_IF_FALSE   174  'to 174'

 L.1288       170  LOAD_CONST               ()
              172  RETURN_VALUE     
            174_0  COME_FROM           168  '168'

 L.1291       174  LOAD_FAST                'participant_type'
              176  LOAD_GLOBAL              ParticipantType
              178  LOAD_ATTR                LinkedPostureSim
              180  COMPARE_OP               ==
              182  POP_JUMP_IF_FALSE   218  'to 218'

 L.1292       184  LOAD_FAST                'self'
              186  LOAD_ATTR                _source_obj
              188  LOAD_ATTR                is_sim
              190  POP_JUMP_IF_FALSE   218  'to 218'

 L.1293       192  LOAD_FAST                'self'
              194  LOAD_ATTR                _source_obj
              196  LOAD_ATTR                posture
              198  STORE_FAST               'posture'

 L.1294       200  LOAD_FAST                'posture'
              202  LOAD_ATTR                multi_sim
              204  POP_JUMP_IF_FALSE   218  'to 218'

 L.1295       206  LOAD_FAST                'posture'
              208  LOAD_ATTR                linked_posture
              210  LOAD_ATTR                sim
              212  LOAD_ATTR                sim_info
              214  BUILD_TUPLE_1         1 
              216  RETURN_VALUE     
            218_0  COME_FROM           204  '204'
            218_1  COME_FROM           190  '190'
            218_2  COME_FROM           182  '182'

 L.1298       218  LOAD_FAST                'participant_type'
              220  LOAD_GLOBAL              ParticipantType
              222  LOAD_ATTR                SignificantOtherTargetSim
              224  COMPARE_OP               ==
              226  POP_JUMP_IF_FALSE   250  'to 250'

 L.1299       228  LOAD_FAST                'self'
              230  LOAD_ATTR                _target_obj
              232  LOAD_ATTR                is_sim
              234  POP_JUMP_IF_FALSE   250  'to 250'

 L.1300       236  LOAD_FAST                'self'
              238  LOAD_ATTR                _target_obj
              240  LOAD_ATTR                sim_info
              242  LOAD_METHOD              get_significant_other_sim_info
              244  CALL_METHOD_0         0  '0 positional arguments'
              246  BUILD_TUPLE_1         1 
              248  RETURN_VALUE     
            250_0  COME_FROM           234  '234'
            250_1  COME_FROM           226  '226'

 L.1302       250  LOAD_FAST                'participant_type'
              252  LOAD_GLOBAL              ParticipantType
              254  LOAD_ATTR                ObjectParent
              256  COMPARE_OP               ==
          258_260  POP_JUMP_IF_FALSE   302  'to 302'

 L.1303       262  LOAD_FAST                'self'
              264  LOAD_ATTR                _target_obj
              266  LOAD_CONST               None
              268  COMPARE_OP               is
          270_272  POP_JUMP_IF_TRUE    288  'to 288'
              274  LOAD_FAST                'self'
              276  LOAD_ATTR                _target_obj
              278  LOAD_ATTR                parent
              280  LOAD_CONST               None
              282  COMPARE_OP               is
          284_286  POP_JUMP_IF_FALSE   292  'to 292'
            288_0  COME_FROM           270  '270'

 L.1304       288  LOAD_CONST               ()
              290  RETURN_VALUE     
            292_0  COME_FROM           284  '284'

 L.1305       292  LOAD_FAST                'self'
              294  LOAD_ATTR                _target_obj
              296  LOAD_ATTR                parent
              298  BUILD_TUPLE_1         1 
              300  RETURN_VALUE     
            302_0  COME_FROM           258  '258'

 L.1307       302  LOAD_FAST                'participant_type'
              304  LOAD_GLOBAL              ParticipantType
              306  LOAD_ATTR                RoutingOwner
              308  COMPARE_OP               ==
          310_312  POP_JUMP_IF_FALSE   354  'to 354'

 L.1308       314  LOAD_FAST                'self'
              316  LOAD_ATTR                _source_obj
              318  LOAD_METHOD              get_routing_owner
              320  CALL_METHOD_0         0  '0 positional arguments'
              322  LOAD_ATTR                is_sim
          324_326  POP_JUMP_IF_FALSE   342  'to 342'

 L.1309       328  LOAD_FAST                'self'
              330  LOAD_ATTR                _source_obj
              332  LOAD_METHOD              get_routing_owner
              334  CALL_METHOD_0         0  '0 positional arguments'
              336  LOAD_ATTR                sim_info
              338  BUILD_TUPLE_1         1 
              340  RETURN_VALUE     
            342_0  COME_FROM           324  '324'

 L.1311       342  LOAD_FAST                'self'
              344  LOAD_ATTR                _source_obj
              346  LOAD_METHOD              get_routing_owner
              348  CALL_METHOD_0         0  '0 positional arguments'
              350  BUILD_TUPLE_1         1 
              352  RETURN_VALUE     
            354_0  COME_FROM           310  '310'

 L.1312       354  LOAD_FAST                'participant_type'
              356  LOAD_GLOBAL              ParticipantType
              358  LOAD_ATTR                RoutingTarget
              360  COMPARE_OP               ==
          362_364  POP_JUMP_IF_FALSE   406  'to 406'

 L.1313       366  LOAD_FAST                'self'
              368  LOAD_ATTR                _source_obj
              370  LOAD_METHOD              get_routing_target
              372  CALL_METHOD_0         0  '0 positional arguments'
              374  LOAD_ATTR                is_sim
          376_378  POP_JUMP_IF_FALSE   394  'to 394'

 L.1314       380  LOAD_FAST                'self'
              382  LOAD_ATTR                _source_obj
              384  LOAD_METHOD              get_routing_target
              386  CALL_METHOD_0         0  '0 positional arguments'
              388  LOAD_ATTR                sim_info
              390  BUILD_TUPLE_1         1 
              392  RETURN_VALUE     
            394_0  COME_FROM           376  '376'

 L.1316       394  LOAD_FAST                'self'
              396  LOAD_ATTR                _source_obj
              398  LOAD_METHOD              get_routing_target
              400  CALL_METHOD_0         0  '0 positional arguments'
              402  BUILD_TUPLE_1         1 
              404  RETURN_VALUE     
            406_0  COME_FROM           362  '362'

 L.1317       406  LOAD_FAST                'participant_type'
              408  LOAD_GLOBAL              ParticipantType
              410  LOAD_ATTR                ActorLotLevel
              412  COMPARE_OP               ==
          414_416  POP_JUMP_IF_FALSE   430  'to 430'

 L.1318       418  LOAD_FAST                'self'
              420  LOAD_METHOD              _get_lot_level_from_object
              422  LOAD_FAST                'self'
              424  LOAD_ATTR                _source_obj
              426  CALL_METHOD_1         1  '1 positional argument'
              428  RETURN_VALUE     
            430_0  COME_FROM           414  '414'

 L.1319       430  LOAD_FAST                'participant_type'
              432  LOAD_GLOBAL              ParticipantType
              434  LOAD_ATTR                ObjectLotLevel
              436  COMPARE_OP               ==
          438_440  POP_JUMP_IF_FALSE   454  'to 454'

 L.1320       442  LOAD_FAST                'self'
              444  LOAD_METHOD              _get_lot_level_from_object
              446  LOAD_FAST                'self'
              448  LOAD_ATTR                _target_obj
              450  CALL_METHOD_1         1  '1 positional argument'
              452  RETURN_VALUE     
            454_0  COME_FROM           438  '438'

 L.1321       454  LOAD_FAST                'participant_type'
              456  LOAD_GLOBAL              ParticipantType
              458  LOAD_ATTR                ObjectAnimalHome
              460  COMPARE_OP               ==
          462_464  POP_JUMP_IF_FALSE   478  'to 478'

 L.1322       466  LOAD_FAST                'self'
              468  LOAD_METHOD              _get_animal_home_from_object
              470  LOAD_FAST                'self'
              472  LOAD_ATTR                _source_obj
              474  CALL_METHOD_1         1  '1 positional argument'
              476  RETURN_VALUE     
            478_0  COME_FROM           462  '462'

 L.1324       478  LOAD_FAST                'participant_type'
              480  LOAD_GLOBAL              ParticipantType
              482  LOAD_ATTR                ActorClanLeader
              484  COMPARE_OP               ==
          486_488  POP_JUMP_IF_FALSE   556  'to 556'

 L.1325       490  LOAD_GLOBAL              services
              492  LOAD_METHOD              clan_service
              494  CALL_METHOD_0         0  '0 positional arguments'
              496  STORE_FAST               'clan_service'

 L.1326       498  LOAD_FAST                'self'
              500  LOAD_ATTR                _source_obj
              502  LOAD_ATTR                is_sim
          504_506  POP_JUMP_IF_FALSE   518  'to 518'
              508  LOAD_FAST                'clan_service'
              510  LOAD_CONST               None
              512  COMPARE_OP               is
          514_516  POP_JUMP_IF_FALSE   522  'to 522'
            518_0  COME_FROM           504  '504'

 L.1327       518  LOAD_CONST               ()
              520  RETURN_VALUE     
            522_0  COME_FROM           514  '514'

 L.1328       522  LOAD_FAST                'clan_service'
              524  LOAD_METHOD              get_clan_leader
              526  LOAD_FAST                'self'
              528  LOAD_ATTR                _source_obj
              530  LOAD_ATTR                sim_info
              532  CALL_METHOD_1         1  '1 positional argument'
              534  STORE_FAST               'clan_leader'

 L.1329       536  LOAD_FAST                'clan_leader'
              538  LOAD_CONST               None
              540  COMPARE_OP               is
          542_544  POP_JUMP_IF_FALSE   550  'to 550'
              546  LOAD_CONST               ()
              548  RETURN_VALUE     
            550_0  COME_FROM           542  '542'
              550  LOAD_FAST                'clan_leader'
              552  BUILD_TUPLE_1         1 
              554  RETURN_VALUE     
            556_0  COME_FROM           486  '486'

 L.1331       556  LOAD_FAST                'participant_type'
              558  LOAD_GLOBAL              ParticipantType
              560  LOAD_ATTR                TargetClanLeader
              562  COMPARE_OP               ==
          564_566  POP_JUMP_IF_FALSE   634  'to 634'

 L.1332       568  LOAD_GLOBAL              services
              570  LOAD_METHOD              clan_service
              572  CALL_METHOD_0         0  '0 positional arguments'
              574  STORE_FAST               'clan_service'

 L.1333       576  LOAD_FAST                'self'
              578  LOAD_ATTR                _target_obj
              580  LOAD_ATTR                is_sim
          582_584  POP_JUMP_IF_FALSE   596  'to 596'
              586  LOAD_FAST                'clan_service'
              588  LOAD_CONST               None
              590  COMPARE_OP               is
          592_594  POP_JUMP_IF_FALSE   600  'to 600'
            596_0  COME_FROM           582  '582'

 L.1334       596  LOAD_CONST               ()
              598  RETURN_VALUE     
            600_0  COME_FROM           592  '592'

 L.1335       600  LOAD_FAST                'clan_service'
              602  LOAD_METHOD              get_clan_leader
              604  LOAD_FAST                'self'
              606  LOAD_ATTR                _target_obj
              608  LOAD_ATTR                sim_info
              610  CALL_METHOD_1         1  '1 positional argument'
              612  STORE_FAST               'clan_leader'

 L.1336       614  LOAD_FAST                'clan_leader'
              616  LOAD_CONST               None
              618  COMPARE_OP               is
          620_622  POP_JUMP_IF_FALSE   628  'to 628'
              624  LOAD_CONST               ()
              626  RETURN_VALUE     
            628_0  COME_FROM           620  '620'
              628  LOAD_FAST                'clan_leader'
              630  BUILD_TUPLE_1         1 
              632  RETURN_VALUE     
            634_0  COME_FROM           564  '564'

 L.1338       634  LOAD_GLOBAL              ValueError
              636  LOAD_STR                 'Trying to use DoubleObjectResolver with something that is not supported: Participant {} for objects {} and {}, Resolver {}'
              638  LOAD_METHOD              format
              640  LOAD_FAST                'participant_type'

 L.1339       642  LOAD_FAST                'self'
              644  LOAD_ATTR                _source_obj

 L.1340       646  LOAD_FAST                'self'
              648  LOAD_ATTR                _target_obj

 L.1341       650  LOAD_FAST                'self'
              652  CALL_METHOD_4         4  '4 positional arguments'
              654  CALL_FUNCTION_1       1  '1 positional argument'
              656  RAISE_VARARGS_1       1  'exception instance'

Parse error at or near `CALL_FUNCTION_1' instruction at offset 654

    def get_localization_tokens(self, *args, **kwargs):
        return (
         self._source_obj, self._target_obj)


class SingleActorAndObjectResolver(Resolver):

    def __init__(self, actor_sim_info, obj, source):
        super().__init__()
        self._sim_info = actor_sim_info
        self._obj = obj
        self._source = source

    def __repr__(self):
        return 'SingleActorAndObjectResolver: sim_info: {}, object: {}'.format(self._sim_info, self._obj)

    @property
    def profile_metric_key(self):
        return 'source:{} object:{}'.format(self._source, self._obj)

    def get_participants(self, participant_type, **kwargs):
        result = (self._get_participants_base)(participant_type, **kwargs)
        if result is not None:
            return result
        if participant_type == ParticipantType.Actor or participant_type == ParticipantType.CustomSim or participant_type == event_testing.test_constants.SIM_INSTANCE:
            return (
             self._sim_info,)
        if participant_type == ParticipantType.Object:
            return (
             self._obj,)
        if participant_type == ParticipantType.ObjectIngredients:
            if self._obj.crafting_component:
                crafting_process = self._obj.get_crafting_process()
                if crafting_process is not None:
                    return tuple(crafting_process.get_ingredients_object_definitions())
            return ()
        if participant_type == ParticipantType.ObjectTrendiOutfitTrend or participant_type == ParticipantType.ObjectTrendiOutfitTrendTag:
            if self._obj is not None:
                fashion_trend_service = services.fashion_trend_service()
                if fashion_trend_service is not None:
                    if participant_type == ParticipantType.ObjectTrendiOutfitTrend:
                        outfit_trend = fashion_trend_service.get_outfit_prevalent_trend(self._obj)
                        if outfit_trend is not None:
                            return (
                             outfit_trend,)
                    if participant_type == ParticipantType.ObjectTrendiOutfitTrendTag:
                        outfit_trend_tag = fashion_trend_service.get_outfit_prevalent_trend_tag(self._obj)
                        if outfit_trend_tag is not None:
                            return (
                             outfit_trend_tag,)
            return ()
        if participant_type == ParticipantType.ObjectParent and not self._obj is None:
            if self._obj.parent is None:
                return ()
            return (
             self._obj.parent,)
            if participant_type == ParticipantType.StoredSim:
                stored_sim_info = self._obj.get_stored_sim_info()
                return (stored_sim_info,)
            if participant_type == ParticipantType.StoredSim2:
                stored_sim_info2 = self._obj.get_secondary_stored_sim_info()
                return (stored_sim_info2,)
            if participant_type == ParticipantType.StoredCASPartsOnObject:
                stored_cas_parts = self._obj.get_stored_cas_parts()
                if stored_cas_parts is None:
                    return ()
                return tuple(iter(self._obj.get_stored_cas_parts()))
            if participant_type == ParticipantType.OwnerSim:
                owner_sim_info_id = self._obj.get_sim_owner_id()
                owner_sim_info = services.sim_info_manager().get(owner_sim_info_id)
                return (owner_sim_info,)
            if participant_type == ParticipantType.Affordance or participant_type == ParticipantType.InteractionContext or participant_type == event_testing.test_constants.FROM_EVENT_DATA:
                return ()
            if participant_type == ParticipantType.ObjectLotLevel:
                return self._get_lot_level_from_object(self._obj)
            if participant_type == ParticipantType.ActorLotLevel:
                return self._get_lot_level_from_object(self._sim_info.get_sim_instance())
        raise ValueError('Trying to use SingleActorAndObjectResolver with something that is not supported: {}'.format(participant_type))

    def get_localization_tokens(self, *args, **kwargs):
        return (
         self._sim_info, self._obj)


class DoubleSimAndObjectResolver(Resolver):

    def __init__(self, actor_sim_info, target_sim_info, obj, source):
        super().__init__()
        self._actor_sim_info = actor_sim_info
        self._target_sim_info = target_sim_info
        self._obj = obj
        self._source = source

    def __repr__(self):
        return f"DoubleActorAndObjectResolver: actor_sim_info: {self._actor_sim_info}, target_sim_info: {self._target_sim_info}, object: {self._obj}"

    @property
    def profile_metric_key(self):
        return f"source:{self._source} object:{self._obj}"

    def get_participants(self, participant_type, **kwargs):
        result = (self._get_participants_base)(participant_type, **kwargs)
        if result is not None:
            return result
        if participant_type == ParticipantType.Actor or participant_type == ParticipantType.CustomSim or participant_type == event_testing.test_constants.SIM_INSTANCE:
            return (
             self._actor_sim_info,)
        if participant_type == ParticipantType.ActorHouseholdMembers:
            if self._actor_sim_info is not None:
                if self._actor_sim_info.household is not None:
                    return tuple(self._actor_sim_info.household)
        if participant_type == ParticipantType.TargetSim:
            return (
             self._target_sim_info,)
        if participant_type == ParticipantType.TargetHouseholdMembers:
            if self._target_sim_info is not None:
                if self._target_sim_info.household is not None:
                    return tuple(self._target_sim_info.household)
        if participant_type == ParticipantType.SignificantOtherTargetSim:
            return (
             self._target_sim_info.get_significant_other_sim_info(),)
        if participant_type == ParticipantType.Object:
            return (
             self._obj,)
        if participant_type == ParticipantType.ObjectIngredients:
            if self._obj.crafting_component:
                crafting_process = self._obj.get_crafting_process()
                if crafting_process is not None:
                    return tuple(crafting_process.get_ingredients_object_definitions())
            return ()
        if participant_type == ParticipantType.ObjectTrendiOutfitTrend or participant_type == ParticipantType.ObjectTrendiOutfitTrendTag:
            if self._obj is not None:
                fashion_trend_service = services.fashion_trend_service()
                if fashion_trend_service is not None:
                    if participant_type == ParticipantType.ObjectTrendiOutfitTrend:
                        outfit_trend = fashion_trend_service.get_outfit_prevalent_trend(self._obj)
                        if outfit_trend is not None:
                            return (
                             outfit_trend,)
                    if participant_type == ParticipantType.ObjectTrendiOutfitTrendTag:
                        outfit_trend_tag = fashion_trend_service.get_outfit_prevalent_trend_tag(self._obj)
                        if outfit_trend_tag is not None:
                            return (
                             outfit_trend_tag,)
            return ()
        if participant_type == ParticipantType.ObjectParent and not self._obj is None:
            if self._obj.parent is None:
                return ()
            return (
             self._obj.parent,)
            if participant_type == ParticipantType.StoredSim:
                stored_sim_info = self._obj.get_stored_sim_info()
                return (stored_sim_info,)
            if participant_type == ParticipantType.StoredSim2:
                stored_sim_info2 = self._obj.get_secondary_stored_sim_info()
                return (stored_sim_info2,)
            if participant_type == ParticipantType.StoredCASPartsOnObject:
                stored_cas_parts = self._obj.get_stored_cas_parts()
                if stored_cas_parts is None:
                    return ()
                return tuple(iter(self._obj.get_stored_cas_parts()))
            if participant_type == ParticipantType.OwnerSim:
                owner_sim_info_id = self._obj.get_sim_owner_id()
                owner_sim_info = services.sim_info_manager().get(owner_sim_info_id)
                return (owner_sim_info,)
            if participant_type == ParticipantType.Affordance:
                return ()
            if participant_type == ParticipantType.InteractionContext:
                return ()
            if participant_type == event_testing.test_constants.FROM_EVENT_DATA:
                return ()
            if participant_type == ParticipantType.ObjectLotLevel:
                return self._get_lot_level_from_object(self._obj)
            if participant_type == ParticipantType.ActorLotLevel:
                return self._get_lot_level_from_object(self._actor_sim_info.get_sim_instance())
        raise ValueError(f"Trying to use DoubleActorAndObjectResolver with something that is not supported: {participant_type}")

    def get_localization_tokens(self, *args, **kwargs):
        return (
         self._sim_info, self._target_sim_info, self._obj)


class PhotoResolver(SingleActorAndObjectResolver):

    def __init__(self, photographer, photo_object, photo_targets, source):
        super().__init__photographerphoto_objectsource
        self._photo_targets = photo_targets

    def __repr__(self):
        return 'PhotoResolver: photographer: {}, photo_object:{}, photo_targets:{}'.formatself._sim_infoself._objself._photo_targets

    def get_participants(self, participant_type, **kwargs):
        if participant_type == ParticipantType.PhotographyTargets:
            return self._photo_targets
        return (super().get_participants)(participant_type, **kwargs)


class ZoneResolver(GlobalResolver):

    def __init__(self, zone_id, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._zone_id = zone_id

    def __repr__(self):
        return 'ZoneResolver: zone_id: {}'.format(self._zone_id)

    def get_participants(self, participant_type, **kwargs):
        if participant_type == ParticipantType.PickedZoneId:
            return (
             self._zone_id,)
        return (super().get_participants)(participant_type, **kwargs)


class StreetResolver(GlobalResolver):

    def __init__(self, street, **kwargs):
        (super().__init__)(**kwargs)
        self._street = street

    def get_participants(self, participant_type, **kwargs):
        if participant_type == ParticipantType.Street:
            street_service = services.street_service()
            if street_service is None:
                return ()
            street_civic_policy_provider = street_service.get_provider(self._street)
            if street_civic_policy_provider is None:
                return ()
            return (
             street_civic_policy_provider,)
        return (super().get_participants)(participant_type, **kwargs)


class VenuePolicyProviderResolver(GlobalResolver):

    def __init__(self, venue_policy_provider, **kwargs):
        (super().__init__)(**kwargs)
        self._venue_policy_provider = venue_policy_provider

    def get_participants(self, participant_type, **kwargs):
        if participant_type == ParticipantType.VenuePolicyProvider:
            return (
             self._venue_policy_provider,)
        return (super().get_participants)(participant_type, **kwargs)


class LotResolver(GlobalResolver):

    def __init__(self, lot, **kwargs):
        (super().__init__)(**kwargs)
        self._lot = lot

    def get_participants(self, participant_type, **kwargs):
        if participant_type == ParticipantType.Lot:
            return (
             self._lot,)
        return (super().get_participants)(participant_type, **kwargs)


class HouseholdResolver(Resolver):

    def __init__(self, household, additional_participants={}, **kwargs):
        (super().__init__)(**kwargs)
        self._household = household
        self._additional_participants = additional_participants

    def get_participants(self, participant_type, **kwargs):
        if participant_type == ParticipantType.ActorHousehold:
            return (
             self._household,)
        if participant_type == ParticipantType.ActorHouseholdMembers:
            return tuple(self._household)
        if participant_type in self._additional_participants:
            return self._additional_participants[participant_type]
        return (super().get_participants)(participant_type, **kwargs)