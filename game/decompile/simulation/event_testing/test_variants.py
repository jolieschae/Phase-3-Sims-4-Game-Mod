# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\test_variants.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 289657 bytes
import itertools
from aspirations.aspiration_types import AspriationType
from bucks.bucks_enums import BucksType
from build_buy import FloorFeatureType
from careers.career_enums import GigResult, CareerCategory
from crafting.photography_enums import PhotoStyleType
from event_testing import TargetIdTypes
from event_testing.resolver import RESOLVER_PARTICIPANT, SingleSimResolver
from event_testing.results import TestResult, TestResultNumeric
from event_testing.test_events import TestEvent
from gameplay_scenarios.scenario_tests import ScenarioRoleTest
from caches import cached_test
from interactions import ParticipantType, ParticipantTypeActorTargetSim, ParticipantTypeSingle, TargetType, ParticipantTypeSingleSim, ParticipantTypeObject, ParticipantTypeCASPart, ParticipantTypeSim
from interactions.context import InteractionSource
from objects import ALL_HIDDEN_REASONS
from objects.components.portal_locking_enums import LockPriority, LockType
from relationships.relationship_tests import RelationshipTestBasedScore
from sims.household_utilities.utility_types import Utilities
from sims.sim_info_tests import SimInfoTest
from sims.sim_info_types import Gender
from sims4.math import Operator
from sims4.resources import Types
from sims4.tuning.tunable import TunableFactory, TunableEnumEntry, TunableSingletonFactory, Tunable, OptionalTunable, TunableList, TunableTuple, TunableThreshold, TunableSet, TunableReference, TunableVariant, HasTunableSingletonFactory, AutoFactoryInit, TunableInterval, TunableEnumFlags, TunableEnumSet, TunableRange, TunablePackSafeReference, TunableEnumWithFilter, TunableCasPart
from sims4.utils import flexproperty
from singletons import DEFAULT
from situations.situation_serialization import GLOBAL_SITUATION_LINKED_SIM_ID
from situations.situation_types import SituationMedal
from socials.social_tests import SocialContextTest
from tag import Tag
from tunable_utils.tunable_white_black_list import TunableWhiteBlackList
import build_buy, caches, clock, date_and_time, enum, event_testing.event_data_const, event_testing.test_base, objects.collection_manager, objects.components.statistic_types, scheduler_utils, services, sims.bills_enums, sims.sim_info_types, sims4.tuning.tunable, snippets, tunable_time
logger = sims4.log.Logger('Tests')

class CollectionThresholdTest(event_testing.test_base.BaseTest):
    test_events = (
     TestEvent.CollectionChanged,)

    @TunableFactory.factory_option
    def participant_type_override(participant_type_enum, participant_type_default):
        return {'who': TunableEnumEntry(participant_type_enum, participant_type_default, description='Who or what to apply this test to')}

    FACTORY_TUNABLES = {'description':'Tests for a provided amount of a given collection type.', 
     'who':TunableEnumEntry(description='\n            Who or what to apply this test to\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'collection_type':TunableEnumEntry(description='\n            The collection we are checking on.  If collection type is\n            unidentified then we will look through all collections.\n            ',
       tunable_type=objects.collection_manager.CollectionIdentifier,
       default=objects.collection_manager.CollectionIdentifier.Unindentified), 
     'complete_collection':Tunable(description='\n            Setting this to True (checked) will override the threshold and\n            check for collection completed\n            ',
       tunable_type=bool,
       default=False), 
     'threshold':TunableThreshold(description='\n            Threshold for which the Sim experiences motive failure\n            ',
       value=Tunable(description='\n                The value of the threshold that the collection is compared\n                against.\n                ',
       tunable_type=int,
       default=1),
       default=sims4.math.Threshold(1, sims4.math.Operator.GREATER_OR_EQUAL.function)), 
     'specific_items':OptionalTunable(description='\n            If enabled then the collection threshold test will check for\n            specific items within the collection.  When enabled both the\n            Collection Type and Complete Collection tuning will be ignored.\n            ',
       tunable=TunableList(description='\n                List of allowed objects within a collection that we want to\n                check.\n                ',
       tunable=TunableReference(description='\n                    Object reference to each collectible object.\n                    ',
       manager=(services.definition_manager()))))}

    def __init__(self, who, collection_type, complete_collection, threshold, specific_items, **kwargs):
        (super().__init__)(safe_to_skip=True, **kwargs)
        self.who = who
        self.collection_type = collection_type
        self.complete_collection = complete_collection
        self.threshold = threshold
        if specific_items is not None:
            self.specific_items = set((specific_item.id for specific_item in specific_items))
        else:
            self.specific_items = None

    def get_expected_args(self):
        return {'test_targets': self.who}

    @cached_test
    def __call__--- This code section failed: ---

 L. 150         0  LOAD_FAST                'test_targets'
                2  LOAD_CONST               None
                4  COMPARE_OP               is
                6  POP_JUMP_IF_FALSE    18  'to 18'

 L. 151         8  LOAD_GLOBAL              TestResult
               10  LOAD_CONST               False
               12  LOAD_STR                 'Test Targets are None, valid during zone load.'
               14  CALL_FUNCTION_2       2  '2 positional arguments'
               16  RETURN_VALUE     
             18_0  COME_FROM             6  '6'

 L. 153        18  LOAD_CONST               0
               20  STORE_FAST               'curr_value'

 L. 154     22_24  SETUP_LOOP          300  'to 300'
               26  LOAD_FAST                'test_targets'
               28  GET_ITER         
            30_32  FOR_ITER            298  'to 298'
               34  STORE_FAST               'target'

 L. 155        36  LOAD_FAST                'target'
               38  LOAD_ATTR                household
               40  STORE_FAST               'household'

 L. 156        42  LOAD_FAST                'household'
               44  LOAD_CONST               None
               46  COMPARE_OP               is
               48  POP_JUMP_IF_FALSE    60  'to 60'

 L. 157        50  LOAD_GLOBAL              TestResult
               52  LOAD_CONST               False
               54  LOAD_STR                 'Household is None when running test, valid during zone load.'
               56  CALL_FUNCTION_2       2  '2 positional arguments'
               58  RETURN_VALUE     
             60_0  COME_FROM            48  '48'

 L. 159        60  LOAD_FAST                'household'
               62  LOAD_ATTR                collection_tracker
               64  STORE_FAST               'collection_tracker'

 L. 161        66  LOAD_FAST                'self'
               68  LOAD_ATTR                specific_items
               70  LOAD_CONST               None
               72  COMPARE_OP               is-not
               74  POP_JUMP_IF_FALSE    94  'to 94'

 L. 162        76  LOAD_FAST                'curr_value'
               78  LOAD_FAST                'collection_tracker'
               80  LOAD_METHOD              get_num_of_collected_items_by_definition_ids
               82  LOAD_FAST                'self'
               84  LOAD_ATTR                specific_items
               86  CALL_METHOD_1         1  '1 positional argument'
               88  INPLACE_ADD      
               90  STORE_FAST               'curr_value'
               92  JUMP_BACK            30  'to 30'
             94_0  COME_FROM            74  '74'

 L. 163        94  LOAD_FAST                'self'
               96  LOAD_ATTR                complete_collection
               98  POP_JUMP_IF_FALSE   190  'to 190'

 L. 164       100  LOAD_FAST                'self'
              102  LOAD_ATTR                collection_type
              104  LOAD_GLOBAL              objects
              106  LOAD_ATTR                collection_manager
              108  LOAD_ATTR                CollectionIdentifier
              110  LOAD_ATTR                Unindentified
              112  COMPARE_OP               ==
              114  POP_JUMP_IF_FALSE   168  'to 168'

 L. 165       116  SETUP_LOOP          188  'to 188'
              118  LOAD_GLOBAL              objects
              120  LOAD_ATTR                collection_manager
              122  LOAD_ATTR                CollectionIdentifier
              124  GET_ITER         
            126_0  COME_FROM           152  '152'
            126_1  COME_FROM           142  '142'
              126  FOR_ITER            164  'to 164'
              128  STORE_FAST               'collection_id'

 L. 166       130  LOAD_FAST                'collection_id'
              132  LOAD_GLOBAL              objects
              134  LOAD_ATTR                collection_manager
              136  LOAD_ATTR                CollectionIdentifier
              138  LOAD_ATTR                Unindentified
              140  COMPARE_OP               !=
              142  POP_JUMP_IF_FALSE   126  'to 126'

 L. 167       144  LOAD_FAST                'collection_tracker'
              146  LOAD_METHOD              check_collection_complete_by_id
              148  LOAD_FAST                'collection_id'
              150  CALL_METHOD_1         1  '1 positional argument'
              152  POP_JUMP_IF_FALSE   126  'to 126'

 L. 168       154  LOAD_FAST                'curr_value'
              156  LOAD_CONST               1
              158  INPLACE_ADD      
              160  STORE_FAST               'curr_value'
              162  JUMP_BACK           126  'to 126'
              164  POP_BLOCK        
              166  JUMP_FORWARD        188  'to 188'
            168_0  COME_FROM           114  '114'

 L. 170       168  LOAD_FAST                'collection_tracker'
              170  LOAD_METHOD              check_collection_complete_by_id
              172  LOAD_FAST                'self'
              174  LOAD_ATTR                collection_type
              176  CALL_METHOD_1         1  '1 positional argument'
              178  POP_JUMP_IF_FALSE   188  'to 188'

 L. 171       180  LOAD_FAST                'curr_value'
              182  LOAD_CONST               1
              184  INPLACE_ADD      
              186  STORE_FAST               'curr_value'
            188_0  COME_FROM           178  '178'
            188_1  COME_FROM           166  '166'
            188_2  COME_FROM_LOOP      116  '116'
              188  JUMP_BACK            30  'to 30'
            190_0  COME_FROM            98  '98'

 L. 173       190  LOAD_FAST                'self'
              192  LOAD_ATTR                collection_type
              194  LOAD_GLOBAL              objects
              196  LOAD_ATTR                collection_manager
              198  LOAD_ATTR                CollectionIdentifier
              200  LOAD_ATTR                Unindentified
              202  COMPARE_OP               ==
          204_206  POP_JUMP_IF_FALSE   268  'to 268'

 L. 174       208  SETUP_LOOP          296  'to 296'
              210  LOAD_GLOBAL              objects
              212  LOAD_ATTR                collection_manager
              214  LOAD_ATTR                CollectionIdentifier
              216  GET_ITER         
            218_0  COME_FROM           234  '234'
              218  FOR_ITER            264  'to 264'
              220  STORE_FAST               'collection_id'

 L. 175       222  LOAD_FAST                'collection_id'
              224  LOAD_GLOBAL              objects
              226  LOAD_ATTR                collection_manager
              228  LOAD_ATTR                CollectionIdentifier
              230  LOAD_ATTR                Unindentified
              232  COMPARE_OP               !=
              234  POP_JUMP_IF_FALSE   218  'to 218'

 L. 176       236  LOAD_FAST                'collection_tracker'
              238  LOAD_METHOD              get_num_collected_items_per_collection_id
              240  LOAD_FAST                'collection_id'
              242  CALL_METHOD_1         1  '1 positional argument'
              244  UNPACK_SEQUENCE_2     2 
              246  STORE_FAST               'base_count'
              248  STORE_FAST               'bonus_count'

 L. 177       250  LOAD_FAST                'curr_value'
              252  LOAD_FAST                'base_count'
              254  LOAD_FAST                'bonus_count'
              256  BINARY_ADD       
              258  INPLACE_ADD      
              260  STORE_FAST               'curr_value'
              262  JUMP_BACK           218  'to 218'
              264  POP_BLOCK        
              266  JUMP_BACK            30  'to 30'
            268_0  COME_FROM           204  '204'

 L. 179       268  LOAD_FAST                'collection_tracker'
              270  LOAD_METHOD              get_num_collected_items_per_collection_id
              272  LOAD_FAST                'self'
              274  LOAD_ATTR                collection_type
              276  CALL_METHOD_1         1  '1 positional argument'
              278  UNPACK_SEQUENCE_2     2 
              280  STORE_FAST               'base_count'
              282  STORE_FAST               'bonus_count'

 L. 180       284  LOAD_FAST                'curr_value'
              286  LOAD_FAST                'base_count'
              288  LOAD_FAST                'bonus_count'
              290  BINARY_ADD       
              292  INPLACE_ADD      
              294  STORE_FAST               'curr_value'
            296_0  COME_FROM_LOOP      208  '208'
              296  JUMP_BACK            30  'to 30'
              298  POP_BLOCK        
            300_0  COME_FROM_LOOP       22  '22'

 L. 182       300  LOAD_FAST                'self'
              302  LOAD_ATTR                threshold
              304  LOAD_METHOD              compare
              306  LOAD_FAST                'curr_value'
              308  CALL_METHOD_1         1  '1 positional argument'
          310_312  POP_JUMP_IF_FALSE   320  'to 320'

 L. 183       314  LOAD_GLOBAL              TestResult
              316  LOAD_ATTR                TRUE
              318  RETURN_VALUE     
            320_0  COME_FROM           310  '310'

 L. 185       320  LOAD_GLOBAL              Operator
              322  LOAD_METHOD              from_function
              324  LOAD_FAST                'self'
              326  LOAD_ATTR                threshold
              328  LOAD_ATTR                comparison
              330  CALL_METHOD_1         1  '1 positional argument'
              332  LOAD_ATTR                symbol
              334  STORE_FAST               'operator_symbol'

 L. 186       336  LOAD_GLOBAL              TestResultNumeric
              338  LOAD_CONST               False
              340  LOAD_STR                 '{} failed collection check: {} {} {}'

 L. 187       342  LOAD_FAST                'self'
              344  LOAD_ATTR                who
              346  LOAD_ATTR                name

 L. 188       348  LOAD_FAST                'curr_value'

 L. 189       350  LOAD_FAST                'operator_symbol'

 L. 190       352  LOAD_FAST                'self'
              354  LOAD_ATTR                threshold
              356  LOAD_ATTR                value

 L. 191       358  LOAD_FAST                'curr_value'

 L. 192       360  LOAD_FAST                'self'
              362  LOAD_ATTR                threshold
              364  LOAD_ATTR                value

 L. 193       366  LOAD_CONST               False

 L. 194       368  LOAD_FAST                'self'
              370  LOAD_ATTR                tooltip
              372  LOAD_CONST               ('current_value', 'goal_value', 'is_money', 'tooltip')
              374  CALL_FUNCTION_KW_10    10  '10 total positional and keyword args'
              376  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM' instruction at offset 190_0

    def goal_value(self):
        if self.complete_collection:
            return 1
        return self.threshold.value


TunableCollectionThresholdTest = TunableSingletonFactory.create_auto_factory(CollectionThresholdTest)

class CollectedItemTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = (
     TestEvent.CollectedItem,)
    COLLECTION_TYPE = 0
    SPECIFIC_ITEMS = 1
    FACTORY_TUNABLES = {'test_type': TunableVariant(description='\n            The type of test that will be run.\n            ',
                    collection_type=TunableTuple(description='\n                If selected we will check that the collected item is from the\n                collection that we are looking for.\n                ',
                    collection_types=TunableList(description='\n                    A list of collections to check against.  The test will pass if it\n                    is a part of any of them.  If this list is empty, then it will pass if\n                    it is part of any collection.\n                    ',
                    tunable=TunableEnumEntry(description='\n                        The collection we are checking against.\n                        ',
                    tunable_type=(objects.collection_manager.CollectionIdentifier),
                    default=(objects.collection_manager.CollectionIdentifier.Unindentified),
                    invalid_enums=(
                   objects.collection_manager.CollectionIdentifier.Unindentified,))),
                    locked_args={'test_type': COLLECTION_TYPE}),
                    specific_items=TunableTuple(description='\n                If selected we will check that the collected item is from a\n                specific list of collectable items that we are looking for.\n                ',
                    specific_items=TunableList(description='\n                    List of allowed objects within a collection that we want to\n                    check.\n                    ',
                    tunable=TunableReference(description='\n                        Object reference to each collectible object.\n                        ',
                    manager=(services.definition_manager()))),
                    locked_args={'test_type': SPECIFIC_ITEMS}),
                    default='collection_type')}

    def get_expected_args(self):
        return {'collection_id':event_testing.test_constants.FROM_EVENT_DATA, 
         'collected_item_id':event_testing.test_constants.FROM_EVENT_DATA}

    @cached_test
    def __call__(self, collection_id=None, collected_item_id=None):
        if self.test_type.test_type == self.COLLECTION_TYPE:
            if collection_id is None:
                return TestResult(False, 'Collected Item is None, valid during zone load.')
            if self.test_type.collection_types and collection_id not in self.test_type.collection_types:
                return TestResult(False, 'Collected Item is of wrong collection type.')
        elif self.test_type.test_type == self.SPECIFIC_ITEMS:
            if collected_item_id is None:
                return TestResult(False, 'Collected Item is None, valid during zone load.')
            if collected_item_id not in set((specific_item.id for specific_item in self.test_type.specific_items)):
                return TestResult(False, 'Collected item is not in in the list of collected items that we are looking for.')
        return TestResult.TRUE


class TopicTest(event_testing.test_base.BaseTest):
    test_events = ()
    FACTORY_TUNABLES = {'description':'Gate topics of the actor or target Sim.', 
     'subject':TunableEnumEntry(ParticipantType, ParticipantType.Actor, description='Who or what to apply this test to'), 
     'target_sim':TunableEnumEntry(ParticipantType, ParticipantType.Invalid, description='Set if topic needs a specfic target.  If no target, keep as Invalid.'), 
     'whitelist_topics':TunableList(TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.TOPIC))), description='The Sim must have any topic in this list to pass this test.'), 
     'blacklist_topics':TunableList(TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.TOPIC))), description='The Sim cannot have any topic contained in this list to pass this test.')}

    def __init__(self, subject, target_sim, whitelist_topics, blacklist_topics, **kwargs):
        (super().__init__)(safe_to_skip=True, **kwargs)
        self.subject = subject
        self.target_sim = target_sim
        self.whitelist_topics = whitelist_topics
        self.blacklist_topics = blacklist_topics

    def get_expected_args(self):
        if self.target_sim == ParticipantType.Invalid:
            return {'subjects': self.subject}
        return {'subjects':self.subject,  'targets_to_match':self.target_sim}

    def _topic_exists(self, sim, target):
        if self.whitelist_topics:
            if any((t.topic_exist_in_sim(sim, target=target) for t in self.whitelist_topics)):
                return TestResult.TRUE
            return TestResult(False, "{} doesn't have any topic in white list", sim, tooltip=(self.tooltip))
        if self.blacklist_topics:
            if any((t.topic_exist_in_sim(sim, target=target) for t in self.blacklist_topics)):
                return TestResult(False, '{} has topic in black list', sim, tooltip=(self.tooltip))
        return TestResult.TRUE

    @cached_test
    def __call__(self, subjects=None, targets_to_match=None):
        for subject in subjects:
            if subject.is_sim:
                if subject.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS) is None:
                    return TestResult(False, '{} failed topic check: It is not an instantiated sim.', subject, tooltip=(self.tooltip))
                subject = subject.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if targets_to_match is not None:
                for target_to_match in targets_to_match:
                    result = self._topic_exists(subject, target_to_match)
                    if not result:
                        return result

            else:
                result = self._topic_exists(subject, None)
                return result or result

        return TestResult.TRUE


TunableTopicTest = TunableSingletonFactory.create_auto_factory(TopicTest)

class UseDefaultOfflotToleranceFactory(TunableSingletonFactory):

    @staticmethod
    def factory():
        return objects.components.statistic_types.StatisticComponentGlobalTuning.DEFAULT_OFF_LOT_TOLERANCE

    FACTORY_TYPE = factory


class LotOwnerTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = ()
    FACTORY_TUNABLES = {'subject':TunableEnumEntry(description='\n            Who or what to apply this test to\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'owns_lot':Tunable(description='\n            If checked and subject owns the current lot then this test will\n            pass. If unchecked, subject does not own lot, this test will pass.\n            ',
       tunable_type=bool,
       default=True), 
     'consider_rented_lot_as_owned':Tunable(description='\n            If checked, rented lots are considered owned. If unchecked, rented\n            lots are considered unowned.\n            ',
       tunable_type=bool,
       default=True), 
     'consider_business_lot_as_owned':Tunable(description='\n            If checked, business lots are considered owned. If unchecked, business\n            lots are considered unowned.\n            ',
       tunable_type=bool,
       default=True), 
     'invert':Tunable(description='\n            If checked, this test will return the opposite of what it\'s tuned to\n            return. For instance, if this test is tuned to return True if the\n            active household owns the lot, but "Invert" is checked, it will\n            actually return False.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'test_targets': self.subject}

    def _is_lot_owner(self, zone, target):
        if target.household.home_zone_id == zone.id:
            return True
            if self.consider_rented_lot_as_owned:
                if target.is_renting_zone(zone.id):
                    return True
        elif self.consider_business_lot_as_owned:
            if zone.lot is not None and zone.lot.owner_household_id == target.household_id:
                return True
        return False

    @cached_test
    def __call__(self, test_targets=None):
        current_zone = services.current_zone()
        for target in test_targets:
            if self._is_lot_owner(current_zone, target) and not self.owns_lot:
                if self.invert:
                    return TestResult.TRUE
                    return TestResult(False, '{} owns the lot, but is not supposed to.', target, tooltip=(self.tooltip))
                elif self.owns_lot:
                    if self.invert:
                        return TestResult.TRUE
                    return TestResult(False, '{} does not own the lot, but is supposed to.', target, tooltip=(self.tooltip))

        if self.invert:
            return TestResult(False, 'Test passed but is tuned to invert the result.')
        return TestResult.TRUE


class HasLotOwnerTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = ()
    FACTORY_TUNABLES = {'description':'\n            Test to check if the lot has an owner or not.\n            ', 
     'has_owner':Tunable(description='\n                If checked then the test will return true if the lot has an\n                owner.\n                If unchecked then the test will return true if the lot does not\n                have an owner.\n                ',
       tunable_type=bool,
       default=True), 
     'consider_rented_lot_as_owned':Tunable(description='\n                If unchecked, test will not consider, renting as ownership. If\n                checked and a sim is renting the current lot then the test will\n                treat being rented as having an owner.  If unchecked and a sim\n                is renting the current lot then the test will not treat this\n                lot as having an owner.\n                ',
       tunable_type=bool,
       default=True)}

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        lot = services.active_lot()
        if not lot:
            return TestResult(False, 'HasLotOwnerTest: No active lot found.',
              tooltip=(self.tooltip))
        has_lot_owner = lot.owner_household_id != 0
        if not has_lot_owner:
            if self.consider_rented_lot_as_owned:
                has_lot_owner = services.travel_group_manager().is_current_zone_rented()
        if self.has_owner:
            if not has_lot_owner:
                return TestResult(False, 'HasLotOwnerTest: Trying to check if the lot has an owner, but the lot does not have an owner.',
                  tooltip=(self.tooltip))
        if not self.has_owner:
            if has_lot_owner:
                return TestResult(False, 'HasLotOwnerTest: Trying to check if the lot does not have an owner, but the lot has an owner.',
                  tooltip=(self.tooltip))
        return TestResult.TRUE


class DuringWorkHoursTest(event_testing.test_base.BaseTest):
    test_events = ()
    FACTORY_TUNABLES = {'description':'Returns True if run during a time that the subject Sim should be at work.', 
     'subject':TunableEnumEntry(description='\n            Who or what to apply this test to.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'is_during_work':Tunable(description='\n            Check to return True if during work hours.\n            ',
       tunable_type=bool,
       default=False), 
     'fail_if_taking_day_off_during_work':Tunable(description="\n            If checked, this test will fail if the Sim is taking\n            PTO/vacation/sick day during work hours and is_during_work is\n            checked. If not checked, this test won't care about whether or not\n            the Sim is taking the day off.\n            ",
       tunable_type=bool,
       default=False), 
     'career':OptionalTunable(description='\n            If tuned, this test will run against a specific career instead of \n            against any career.\n            ',
       tunable=TunablePackSafeReference(description='\n                The specific career to test against.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.CAREER))))}

    def __init__(self, subject, is_during_work, fail_if_taking_day_off_during_work, career, **kwargs):
        (super().__init__)(**kwargs)
        self.subject = subject
        self.is_during_work = is_during_work
        self.fail_if_taking_day_off_during_work = fail_if_taking_day_off_during_work
        self.career = career

    def get_expected_args(self):
        return {'subjects': self.subject}

    @cached_test
    def __call__(self, subjects=()):
        is_work_time = False
        taking_day_off = False
        for subject in subjects:
            career_tracker = subject.career_tracker
            if self.career is not None:
                career = career_tracker.get_career_by_uid(self.career.guid64)
                if not career_tracker.career_during_work_hours(career):
                    continue
            else:
                career = career_tracker.career_currently_within_hours
                if career is None:
                    continue
            is_work_time = True
            taking_day_off = career.taking_day_off
            break

        if is_work_time:
            if self.is_during_work:
                return self.fail_if_taking_day_off_during_work and taking_day_off or TestResult.TRUE
            return TestResult(False, 'Current time is within career work hours.', tooltip=(self.tooltip))
        if self.is_during_work:
            return TestResult(False, 'Current time is not within career work hours.', tooltip=(self.tooltip))
        return TestResult.TRUE


TunableDuringWorkHoursTest = TunableSingletonFactory.create_auto_factory(DuringWorkHoursTest)

class AtWorkTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = (
     TestEvent.WorkdayStart,)
    FACTORY_TUNABLES = {'subject':TunableEnumEntry(description='\n            Who or what to apply this test to.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'is_at_work':Tunable(description='\n            Check to return True if any of the subjects are at work.\n            ',
       tunable_type=bool,
       default=True), 
     'active_work_restriction':OptionalTunable(description='\n            If enabled, if this is set the test will only pass if the Sim is at\n            an active event. If not set, the test will instead only pass if the\n            Sim is not at an active event.\n            ',
       tunable=Tunable(tunable_type=bool,
       default=True))}

    def get_expected_args(self):
        return {'subjects': self.subject}

    @cached_test
    def __call__(self, subjects=(), **kwargs):
        for subject in subjects:
            career = subject.career_tracker.get_currently_at_work_career()
            if career is not None:
                break
        else:
            career = None

        if career is not None and not self.is_at_work:
            return TestResult(False, 'Sim is at work {}', career, tooltip=(self.tooltip))
            if self.active_work_restriction is not None:
                if career.is_at_active_event != self.active_work_restriction:
                    return TestResult(False, '{} does not meet active work restriction: {}', career,
                      (self.active_work_restriction), tooltip=(self.tooltip))
                else:
                    if self.is_at_work:
                        return TestResult(False, 'Sim is not at work', tooltip=(self.tooltip))
        return TestResult.TRUE


class AssignmentActiveFactory(TunableFactory, AutoFactoryInit):

    @staticmethod
    def factory(career):
        if career is None:
            return False
        return career.on_assignment

    FACTORY_TYPE = factory


class AssignmentSpecificFactory(TunableFactory):

    @staticmethod
    def factory(career, assignment):
        return career is None or career.on_assignment or False
        return assignment.guid64 in career.active_assignments

    FACTORY_TYPE = factory

    def __init__(self, **kwargs):
        super().__init__(assignment=sims4.tuning.tunable.TunableReference(description='\n                Aspiration that needs to be completed for satisfying the\n                daily assignment.\n                ',
          manager=(services.get_instance_manager(sims4.resources.Types.ASPIRATION)),
          class_restrictions='AspirationAssignment',
          pack_safe=True))


class CareerAssignmentTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = (
     TestEvent.WorkdayStart,)
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            Who or what to apply this test to.\n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'test_type':TunableVariant(description='\n            Type of assignment test we want to run.\n            \n            in_assignment will return True if the Sim is on any type of \n            asignment for its current career.\n            \n            in_specific_assignment will return True only if the current\n            active assignment matches the assignment specified.\n            ',
       in_assignment=AssignmentActiveFactory(),
       in_specific_assignment=AssignmentSpecificFactory(),
       default='in_assignment'), 
     'negate':Tunable(description='\n            If checked, test will pass if the Sim is not on an assignment.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'test_targets': self.participant}

    @cached_test
    def __call__(self, test_targets, **kwargs):
        for sim in test_targets:
            career = sim.career_tracker.get_on_assignment_career()
            if career is not None:
                break
        else:
            career = None

        if career is not None:
            if self.test_type is not None:
                if self.test_type(career):
                    if self.negate:
                        return TestResult(False, 'Sim has an assignment', tooltip=(self.tooltip))
                    return TestResult.TRUE
        if self.negate:
            return TestResult.TRUE
        return TestResult(False, 'Sim has no assignment', tooltip=(self.tooltip))


class CareerDailyTaskCompletedTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = (
     TestEvent.WorkDailyTaskProgress,)
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            Who or what to apply this test to.\n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'career':OptionalTunable(description='\n            If tuned, this test will run against a specific career instead of \n            against any career.\n            ',
       tunable=TunablePackSafeReference(description='\n                The specific career to test against.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.CAREER))))}

    def get_expected_args(self):
        return {'test_targets': self.participant}

    @cached_test
    def __call__(self, test_targets, **kwargs):
        for sim in test_targets:
            if not sim.careers:
                if not sim.has_custom_career:
                    return TestResult(False, '{0} does not currently have a career.', sim,
                      tooltip=(self.tooltip))
            if sim.careers:
                for career in sim.careers.values():
                    if self.career is None or self.career.guid64 == career.guid64:
                        metrics = career.current_level_tuning.performance_metrics
                        for metric in metrics.statistic_metrics:
                            stat = sim.get_statistic((metric.statistic), add=False)
                            progress_value = stat.get_value()
                            if progress_value >= 100:
                                return TestResult.TRUE

                return TestResult(False, 'Daily assignment not complete.', tooltip=(self.tooltip))

        return TestResult(False, 'Sim has no career.', tooltip=(self.tooltip))


class CareerGigCustomerLotTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            Who or what to apply this test to.\n            ',
       tunable_type=ParticipantTypeSim,
       default=ParticipantTypeSim.Actor), 
     'career':TunablePackSafeReference(description='\n            The career to test for the gig\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CAREER))}

    def get_expected_args(self):
        return {'test_targets': self.participant}

    @cached_test
    def __call__(self, test_targets, **kwargs):
        if self.career is None:
            return TestResult(False, "No career is tuned or career isn't available ", tooltip=(self.tooltip))
        tested_career_uid = self.career.guid64
        current_zone_id = services.current_zone_id()
        for sim in test_targets:
            career = sim.career_tracker.get_career_by_uid(tested_career_uid)
            if career is None:
                continue
            if career.get_current_gig() is None:
                continue
            if career.get_customer_lot_id() == current_zone_id:
                return TestResult.TRUE

        return TestResult(False, "Sim is not at gig's customer lot", tooltip=(self.tooltip))


class CareerGigResultTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            Who or what to apply this test to.\n            ',
       tunable_type=ParticipantTypeSim,
       default=ParticipantTypeSim.Actor), 
     'career':TunablePackSafeReference(description='\n            The career to hold the gig.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CAREER)), 
     'gig_result':TunableEnumEntry(description='\n            The gig result to test to\n            ',
       tunable_type=GigResult,
       default=GigResult.SUCCESS)}

    def get_expected_args(self):
        return {'test_targets': self.participant}

    @cached_test
    def __call__(self, test_targets, **kwargs):
        if self.career is None:
            return TestResult(False, "No career is tuned or career isn't available ", tooltip=(self.tooltip))
        tested_career_uid = self.career.guid64
        for sim in test_targets:
            career = sim.career_tracker.get_career_by_uid(tested_career_uid)
            if career is None:
                continue
            if career.get_current_gig() is None:
                continue
            if career.get_current_gig().gig_result == self.gig_result:
                return TestResult.TRUE

        return TestResult(False, 'Gig result does not match', tooltip=(self.tooltip))


class CareerGigTestTypeBase(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'active_objective':OptionalTunable(description='\n            If enabled, this objective is also required to be active on any of\n            the tuned Gigs.\n            ',
       tunable=sims4.tuning.tunable.TunableReference(description='\n                The objective that needs to be active on the gig.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.OBJECTIVE)),
       pack_safe=True)), 
     'before_photos':OptionalTunable(description='\n            If enabled, test against the existence of before photos. If disabled, ignore.\n            ',
       tunable=Tunable(description='\n                If True, pass only if the the gig has before photos. If False,\n                pass if the gig does not have any before photos.\n                ',
       tunable_type=bool,
       default=True)), 
     'after_photos':OptionalTunable(description='\n            If enabled, test against the existence of after photos. If disabled, ignore.\n            ',
       tunable=Tunable(description='\n                If True, pass only if the the gig has after photos. If False,\n                pass if the gig does not have any after photos.\n                ',
       tunable_type=bool,
       default=True)), 
     'selected_photo_pairs':OptionalTunable(description='\n            If enabled, test against the existence of selected photo pairs. If disabled, ignore.\n            ',
       tunable=Tunable(description='\n                If True, pass only if the the active gig has a stored gig history and selected\n                photo pairs. If False, pass if the gig does not have any selected photos.\n                ',
       tunable_type=bool,
       default=False))}

    def test(self, career):
        if career is None:
            return False
            current_gigs = career.get_current_gigs()
            if not current_gigs:
                return False
            if self.active_objective is not None:
                for gig in current_gigs:
                    if gig.is_objective_active(self.active_objective):
                        return True

                return False
        else:
            current_gig = career.get_current_gig()
            if current_gig is not None:
                gig_history_key = current_gig.get_gig_history_key()
                career_sim_info = career.sim_info
                gig_history = career_sim_info.career_tracker.get_gig_history_by_key(gig_history_key)
                if self.before_photos is not None:
                    if gig_history is None or self.before_photos == (len(gig_history.before_photos) == 0):
                        return False
                if self.after_photos is not None:
                    if gig_history is None or self.after_photos == (len(gig_history.after_photos) == 0):
                        return False
                if self.selected_photo_pairs is not None and not gig_history is None:
                    if self.selected_photo_pairs == (len(gig_history.selected_photos) == 0):
                        return False
        return True


class GigActiveFactory(CareerGigTestTypeBase):
    pass


class GigSpecificFactory(CareerGigTestTypeBase):
    FACTORY_TUNABLES = {'gigs': TunableList(description="\n           A list of gigs. If any tuned gig is the sim's current gig, this test\n           will return True.\n           ",
               tunable=sims4.tuning.tunable.TunableReference(description='\n                Aspiration that needs to be completed for satisfying the\n                daily assignment.\n                ',
               manager=(services.get_instance_manager(sims4.resources.Types.CAREER_GIG)),
               pack_safe=True),
               minlength=1)}

    def test(self, career):
        if not super().test(career):
            return False
        else:
            if career is None:
                return False
            current_gigs = career.get_current_gigs()
            return current_gigs or False
        for current_gig in current_gigs:
            current_gig_id = current_gig.guid64
            if any((gig.guid64 == current_gig_id for gig in self.gigs)):
                return True

        return False


class CareerMaxGigFactory(CareerGigTestTypeBase):

    def test(self, career):
        if career is None:
            return False
        else:
            current_gigs = career.get_current_gigs()
            return current_gigs or False
        if len(current_gigs) == career.current_gig_limit:
            return True
        return False


class CareerGigTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            Who or what to apply this test to.\n            ',
       tunable_type=ParticipantTypeSim,
       default=ParticipantTypeSim.Actor), 
     'test_type':TunableVariant(description='\n            The test to perform. Can check a specific list of gigs, if any gig \n            is currently scheduled, or if the Sim already has the max number of\n            gigs for the career.\n            ',
       any_gig=GigActiveFactory.TunableFactory(description='\n                Return True if any gig is scheduled for the career.\n                '),
       specific_gigs=GigSpecificFactory.TunableFactory(description='\n                Return True if any of the tuned gigs is scheduled for the\n                career.\n                '),
       has_max_gigs=CareerMaxGigFactory.TunableFactory(description='\n                Return True if the participant already has the max number of \n                gigs allowed for the career.\n                '),
       default='any_gig'), 
     'career':TunablePackSafeReference(description='\n            The career to test for gigs\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CAREER)), 
     'negate':Tunable(description='\n            If checked, test will pass if the Sim does not have the gigs.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'test_targets': self.participant}

    @cached_test
    def __call__(self, test_targets, **kwargs):
        if self.career is None:
            if self.negate:
                return TestResult.TRUE
            return TestResult(False, "No career is tuned or career isn't available ", tooltip=(self.tooltip))
        tested_career_uid = self.career.guid64
        has_career_gig = False
        for sim in test_targets:
            career = sim.career_tracker.get_career_by_uid(tested_career_uid)
            if career is None:
                continue
            result = self.test_type.test(career)
            if result:
                has_career_gig = True
                break

        if self.negate:
            if has_career_gig:
                return TestResult(False, 'Sim has gig', tooltip=(self.tooltip))
            return TestResult.TRUE
        if has_career_gig:
            return TestResult.TRUE
        return TestResult(False, 'Sim does not have gig', tooltip=(self.tooltip))
        return TestResult(False, 'No test targets', tooltip=(self.tooltip))


class GigHistoryCustomerFactory(HasTunableSingletonFactory, AutoFactoryInit):

    def get_expected_args(self):
        return {'targets': ParticipantType.TargetSim}

    def test(self, subject, target, min_gig_result, max_gig_result, include_active_gig):
        if target is None:
            return False
        else:
            gig_history = subject.career_tracker.get_gig_history_by_customer(target.id)
            if gig_history is None:
                return False
            if not include_active_gig:
                if subject.career_tracker.is_gig_history_active(gig_history):
                    return False
        return gig_history.gig_result.within_range(min_gig_result, max_gig_result)


class GigHistoryLotFactory(HasTunableSingletonFactory, AutoFactoryInit):

    def get_expected_args(self):
        return {}

    def test(self, subject, target, min_gig_result, max_gig_result, include_active_gig):
        zone_id = services.current_zone_id()
        career_tracker = subject.career_tracker
        for gig_history in career_tracker.gig_history.values():
            if not (zone_id != gig_history.lot_id or include_active_gig):
                if career_tracker.is_gig_history_active(gig_history):
                    continue
            if gig_history.gig_result.within_range(min_gig_result, max_gig_result):
                return True

        return False


class GigHistoryAnyFactory(HasTunableSingletonFactory, AutoFactoryInit):

    def get_expected_args(self):
        return {}

    def test(self, subject, target, min_gig_result, max_gig_result, include_active_gig):
        return subject.career_tracker.has_gig_history_with_result(min_gig_result, max_gig_result, include_active_gig=include_active_gig)


class GigHistorySelectedPhotosCustomer(HasTunableSingletonFactory, AutoFactoryInit):

    def get_expected_args(self):
        return {'targets': ParticipantType.TargetSim}

    def test(self, subject, target, min_gig_result, max_gig_result, include_active_gig):
        if target is None:
            return False
        gig_history = subject.career_tracker.get_gig_history_by_customer(target.id)
        if gig_history is None:
            return False
        return subject.career_tracker.has_selected_photos(gig_history)


class GigHistorySelectedPhotosLot(HasTunableSingletonFactory, AutoFactoryInit):

    def get_expected_args(self):
        return {}

    def test(self, subject, target, min_gig_result, max_gig_result, include_active_gig):
        zone_id = services.current_zone_id()
        career_tracker = subject.career_tracker
        gig_history = career_tracker.get_gig_history_by_venue(zone_id)
        if gig_history is None:
            return False
        return subject.career_tracker.has_selected_photos(gig_history)


class GigHistorySelectedPhotosAny(HasTunableSingletonFactory, AutoFactoryInit):

    def get_expected_args(self):
        return {}

    def test(self, subject, target, min_gig_result, max_gig_result, include_active_gig):
        return subject.career_tracker.has_any_selected_photos()


class GigHistoryBeforePhotosAny(HasTunableSingletonFactory, AutoFactoryInit):

    def get_expected_args(self):
        return {}

    def test(self, subject, target, min_gig_result, max_gig_result, include_active_gig):
        return subject.career_tracker.has_any_before_photos()


class GigHistoryAfterPhotosAny(HasTunableSingletonFactory, AutoFactoryInit):

    def get_expected_args(self):
        return {}

    def test(self, subject, target, min_gig_result, max_gig_result, include_active_gig):
        return subject.career_tracker.has_any_after_photos()


class CareerGigHistoryTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'has_gig_history':Tunable(description="\n            If checked, the test must find a valid gig in the subject's history.\n            If not checked, the test must not find a valid gig in the subject's history.\n            ",
       tunable_type=bool,
       default=True), 
     'test_type':TunableVariant(description='\n            The test to perform. Can check for gig histories based on customer, lot, or any available.\n            ',
       has_selected_photos_customer=GigHistorySelectedPhotosCustomer.TunableFactory(),
       has_selected_photos_lot=GigHistorySelectedPhotosLot.TunableFactory(),
       has_selected_photos_any=GigHistorySelectedPhotosAny.TunableFactory(),
       has_before_photos_any=GigHistoryBeforePhotosAny.TunableFactory(),
       has_after_photos_any=GigHistoryAfterPhotosAny.TunableFactory(),
       any_gig_history=GigHistoryAnyFactory.TunableFactory(),
       gig_history_customer=GigHistoryCustomerFactory.TunableFactory(),
       gig_history_lot=GigHistoryLotFactory.TunableFactory(),
       default='any_gig_history'), 
     'min_gig_result':TunableEnumEntry(description='\n            The worst acceptable gig result to pass.\n            ',
       tunable_type=GigResult,
       default=GigResult.CRITICAL_FAILURE), 
     'max_gig_result':TunableEnumEntry(description='\n            The best acceptable gig result to pass.\n            ',
       tunable_type=GigResult,
       default=GigResult.GREAT_SUCCESS), 
     'include_active_gig':Tunable(description="\n            If checked, the test can pass on the gig history for the active gig.\n            If not checked, test must find a valid gig history that doesn't match the customer & type of the active gig.\n            ",
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        expected_args = {'subjects': ParticipantType.Actor}
        test_args = self.test_type.get_expected_args()
        expected_args.update(test_args)
        return expected_args

    @cached_test
    def __call__(self, subjects, targets=None, **kwargs):
        for subject in subjects:
            if targets:
                for target in targets:
                    result = self.test_type.test(subject, target, self.min_gig_result, self.max_gig_result, self.include_active_gig)
                    if result == self.has_gig_history:
                        return TestResult.TRUE

            else:
                result = self.test_type.test(subject, None, self.min_gig_result, self.max_gig_result, self.include_active_gig)
                if result == self.has_gig_history:
                    return TestResult.TRUE

        return TestResult(False, 'No valid gig history found.')


class CareerPreviousCareerTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'career':TunablePackSafeReference(description="\n            The career to check against subject's previous career.\n            ",
       manager=services.get_instance_manager(sims4.resources.Types.CAREER)), 
     'career_category':OptionalTunable(description="\n            Specify what category of careers to look within to get the sim's\n            previous career. If not tuned, will return the last sim's career from all careers. \n            ",
       tunable=TunableEnumEntry(description='\n                The career category to look within for previous career. \n                ',
       tunable_type=CareerCategory,
       default=(CareerCategory.Invalid))), 
     'subject':TunableEnumEntry(description='\n            The participant to check their previous career of. \n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'negate':Tunable(description='\n            If checked, negate the outcome such that if it would pass it will\n            now fail and vice-versa.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'subjects': self.subject}

    def __call__(self, subjects):
        for subject in subjects:
            if self.career is None:
                return TestResult(False, 'Tuned career is None, field is a pack safe reference.', subject, tooltip=(self.tooltip))
                previous_career_id = subject.career_tracker.get_previous_career_id(self.career_category)
                if previous_career_id is None:
                    if self.negate:
                        return TestResult.TRUE
                    if self.career_category is None:
                        return TestResult(False, 'Sim {} has no previous career.', subject, tooltip=(self.tooltip))
                    return TestResult(False, 'Sim {} has no previous career in career category {}.', subject, (self.career_category), tooltip=(self.tooltip))
                if self.career.guid64 != previous_career_id:
                    if self.negate:
                        return TestResult.TRUE
                    return TestResult(False, 'Previous career {} does not match tuned career for {}', previous_career_id,
                      subject,
                      tooltip=(self.tooltip))

        if self.negate:
            return TestResult(False, "Tuned career matched sim's previous career, but result was negated.", tooltip=(self.tooltip))
        return TestResult.TRUE


class SimoleonsTestEvents(enum.Int):
    AllSimoloenEvents = 0
    OnExitBuildBuy = TestEvent.OnExitBuildBuy
    SimoleonsEarned = TestEvent.SimoleonsEarned


class _SimoleonTestValueContextBase(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'subject': TunableEnumEntry(description='\n            Who to examine for Simoleon values.\n            ',
                  tunable_type=ParticipantTypeSingleSim,
                  default=(ParticipantType.Actor),
                  invalid_enums=(
                 ParticipantTypeSingleSim.Invalid,))}

    def test(self, resolver):
        return TestResult.TRUE

    def get_value(self, resolver):
        subject = resolver.get_participant(self.subject)
        return self._get_value(subject)

    def _get_value(self, subject):
        raise NotImplementedError


class _SimoleonTestValueContextNetWorth(_SimoleonTestValueContextBase):

    def _get_value(self, subject):
        household = services.household_manager().get_by_sim_id(subject.sim_id)
        return household.household_net_worth()


class _SimoleonTestValueContextPropertyOnly(_SimoleonTestValueContextBase):

    def _get_value(self, subject):
        household = services.household_manager().get_by_sim_id(subject.sim_id)
        return household.get_property_value()


class _SimoleonTestValueContextTotalCash(_SimoleonTestValueContextBase):

    def _get_value(self, subject):
        household = services.household_manager().get_by_sim_id(subject.sim_id)
        return household.funds.money


class _SimoleonTestValueContextCurrentValue(_SimoleonTestValueContextBase):
    FACTORY_TUNABLES = {'subject': TunableEnumEntry(description='\n            Who to examine for Simoleon values.\n            ',
                  tunable_type=ParticipantTypeObject,
                  default=(ParticipantType.Object))}

    def _get_value(self, subject):
        return getattr(subject, 'current_value', 0)


class _SimoleonTestValueContextRetailFunds(_SimoleonTestValueContextBase):

    def test(self, resolver):
        sim = resolver.get_participant(self.subject)
        if sim is None:
            return TestResultNumeric(False, 'Subject {} could not be resolved in the SimoleonValueTest.', (self.subject), current_value=0, goal_value=0)
        if services.business_service().get_business_manager_for_zone():
            return TestResult.TRUE
        return TestResultNumeric(False, "Current lot is either not a business lot or the Sim {} doesn't own it.", sim, current_value=0, goal_value=0)

    def _get_value(self, _):
        business_manager = services.business_service().get_business_manager_for_zone()
        if business_manager:
            return business_manager.funds.money
        return 0


class SimoleonsTest(event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'value_context':TunableVariant(description='\n            The context against which to test the value.\n            ',
       net_worth=_SimoleonTestValueContextNetWorth.TunableFactory(),
       property_only=_SimoleonTestValueContextPropertyOnly.TunableFactory(),
       total_cash=_SimoleonTestValueContextTotalCash.TunableFactory(),
       current_value=_SimoleonTestValueContextCurrentValue.TunableFactory(),
       retail_funds=_SimoleonTestValueContextRetailFunds.TunableFactory(),
       default='net_worth'), 
     'is_apartment':OptionalTunable(description='\n                If checked, test will pass if the zone is an apartment. If\n                unchecked, test passes if the zone is NOT an apartment. Useful\n                 in aspiration tuning, to discriminate between property\n                types in tests of lot value. Allows "Own a House worth X" and\n                "Own an Apartment worth X"\n                ',
       disabled_name="Don't_Test",
       enabled_name='Is_or_is_not_apartment_zone',
       tunable=TunableTuple(description='\n                    Test whether the zone is an apartment or not.\n                    ',
       is_apartment=Tunable(description='\n                        If checked, test will pass if the zone is an apartment.\n                        If unchecked, test passes if the zone is NOT an\n                        apartment.\n                        ',
       tunable_type=bool,
       default=True),
       consider_penthouse_an_apartment=Tunable(description='\n                        If enabled, we will consider penthouses to be\n                        apartments when testing them against the apartment\n                        check.\n                        ',
       tunable_type=bool,
       default=True))), 
     'value_threshold':TunableThreshold(description='\n            Amounts in Simoleons required to pass\n            '), 
     'test_event':TunableEnumEntry(description='\n            The event that we want to trigger this instance of the tuned test on. NOTE: OnClientConnect is\n            still used as a trigger regardless of this choice in order to update the UI.\n            ',
       tunable_type=SimoleonsTestEvents,
       default=SimoleonsTestEvents.AllSimoloenEvents)}

    def __init__(self, value_context, is_apartment, value_threshold, test_event, **kwargs):
        (super().__init__)(**kwargs)
        self.value_context = value_context
        self.is_apartment = is_apartment
        self.value_threshold = value_threshold
        if test_event == SimoleonsTestEvents.AllSimoloenEvents:
            self.test_events = (
             TestEvent.SimoleonsEarned, TestEvent.OnExitBuildBuy)
        else:
            self.test_events = (test_event,)

    def get_expected_args(self):
        return {'resolver': RESOLVER_PARTICIPANT}

    @cached_test
    def __call__(self, resolver):
        if self.is_apartment is not None:
            zone_id = services.current_zone_id()
            is_zone_apartment = services.get_plex_service().is_zone_an_apartment(zone_id, consider_penthouse_an_apartment=(self.is_apartment.consider_penthouse_an_apartment))
            if self.is_apartment.is_apartment != is_zone_apartment:
                return TestResult(False, 'Zone failed apartment test', tooltip=(self.tooltip))
        else:
            test_result = self.value_context.test(resolver)
            if not test_result:
                test_result.goal_value = self.value_threshold.value
                test_result.tooltip = self.tooltip
                return test_result
            if resolver.get_participant(self.value_context.subject) is None:
                return TestResult(False, 'Participant is None')
            value = self.value_context.get_value(resolver)
            operator_symbol = self.value_threshold.compare(value) or Operator.from_function(self.value_threshold.comparison).symbol
            return TestResultNumeric(False,
              'Failed value check: {} {} {} (current value: {})',
              (self.value_context),
              operator_symbol,
              (self.value_threshold.value),
              value,
              current_value=value,
              goal_value=(self.value_threshold.value),
              is_money=True,
              tooltip=(self.tooltip))
        return TestResultNumeric(True, current_value=value, goal_value=(self.value_threshold.value), is_money=True)

    def goal_value(self):
        return self.value_threshold.value

    @property
    def is_goal_value_money(self):
        return True


TunableSimoleonsTest = TunableSingletonFactory.create_auto_factory(SimoleonsTest)

class PartySizeTest(event_testing.test_base.BaseTest):
    test_events = ()
    FACTORY_TUNABLES = {'description':'Require the party size of the subject sim to match a threshold.', 
     'subject':TunableEnumEntry(ParticipantType, ParticipantType.Actor, description='The subject of this party size test.'), 
     'threshold':TunableThreshold(description='The party size threshold for this test.')}

    def __init__(self, subject, threshold, **kwargs):
        (super().__init__)(safe_to_skip=True, **kwargs)
        self.subject = subject
        self.threshold = threshold

    def get_expected_args(self):
        return {'test_targets': self.subject}

    @cached_test
    def __call__(self, test_targets=None):
        for target in test_targets:
            if target is None:
                return TestResult(False, 'Party Size test failed because subject is not set.', tooltip=(self.tooltip))
                if target.is_sim:
                    if target.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS) is None:
                        return TestResult(False, '{} failed topic check: It is not an instantiated sim.', target, tooltip=(self.tooltip))
                    target = target.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
                main_group = target.get_main_group()
                if main_group is None:
                    return TestResult(False, 'Party Size test failed because subject has no party attribute.', tooltip=(self.tooltip))
                group_size = len(main_group)
                return self.threshold.compare(group_size) or TestResult(False, 'Party Size Failed.', tooltip=(self.tooltip))

        return TestResult.TRUE


TunablePartySizeTest = TunableSingletonFactory.create_auto_factory(PartySizeTest)

class PartyAgeTest(event_testing.test_base.BaseTest):
    test_events = ()
    FACTORY_TUNABLES = {'description':'Require all sims in the party meet with the age requirement.', 
     'subject':TunableEnumEntry(description='\n            The subject of this party age test.',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'ages_allowed':TunableEnumSet(description='\n            All valid ages.',
       enum_type=sims.sim_info_types.Age,
       enum_default=sims.sim_info_types.Age.ADULT,
       default_enum_list=[
      sims.sim_info_types.Age.TEEN,
      sims.sim_info_types.Age.YOUNGADULT, sims.sim_info_types.Age.ADULT,
      sims.sim_info_types.Age.ELDER]), 
     'check_ensemble':Tunable(description="\n            If enabled then we will check against the subject's rally ensemble\n            instead.\n            ",
       tunable_type=bool,
       default=False), 
     'threshold':TunableThreshold(description='\n            The number of sims that must pass these tests per group to pass the\n            test.\n            ',
       default=sims4.math.Threshold(1, sims4.math.Operator.GREATER_OR_EQUAL.function))}

    def __init__(self, subject, ages_allowed, check_ensemble, threshold, **kwargs):
        (super().__init__)(safe_to_skip=True, **kwargs)
        self.subject = subject
        self.ages_allowed = ages_allowed
        self.check_ensemble = check_ensemble
        self.threshold = threshold

    def get_expected_args(self):
        return {'test_targets': self.subject}

    @cached_test
    def __call__(self, test_targets=None):
        for target in test_targets:
            if target is None:
                return TestResult(False, 'Party Age test failed because subject is not set.', tooltip=(self.tooltip))
                if target.is_sim:
                    if target.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS) is None:
                        return TestResult(False, '{} failed topic check: It is not an instantiated sim.', target, tooltip=(self.tooltip))
                    target = target.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
                elif self.check_ensemble:
                    party = services.ensemble_service().get_ensemble_sims_for_rally(target)
                else:
                    party = target.get_main_group()
                if not party:
                    return TestResult(False, 'Party Age test failed because subject has no party attribute.', tooltip=(self.tooltip))
                passing_sims = sum((1 for sim in party if sim.age in self.ages_allowed))
                return self.threshold.compare(passing_sims) or TestResult(False, "Party has members that age doesn't meet with the requirement", tooltip=(self.tooltip))

        return TestResult.TRUE


TunablePartyAgeTest = TunableSingletonFactory.create_auto_factory(PartyAgeTest)

class TotalSimoleonsEarnedTest(event_testing.test_base.BaseTest):
    test_events = (
     TestEvent.SimoleonsEarned,)
    USES_DATA_OBJECT = True
    FACTORY_TUNABLES = {'description':'This test is specifically for account based Achievements, upon         event/situation completion testing if the players account has earned enough Simoleons         from event rewards to pass a threshold.', 
     'threshold':TunableThreshold(description='The simoleons threshold for this test.'), 
     'earned_source':TunableEnumEntry(event_testing.event_data_const.SimoleonData,
       event_testing.event_data_const.SimoleonData.TotalMoneyEarned,
       description='The individual source that we want to track the simoleons from.')}

    def __init__(self, threshold, earned_source, **kwargs):
        (super().__init__)(safe_to_skip=True, **kwargs)
        self.threshold = threshold
        self.earned_source = earned_source

    def get_expected_args(self):
        return {'data_object':event_testing.test_constants.FROM_DATA_OBJECT, 
         'objective_guid64':event_testing.test_constants.OBJECTIVE_GUID64}

    @cached_test
    def __call__(self, data_object=None, objective_guid64=None):
        simoleons_earned = data_object.get_simoleons_earned(self.earned_source)
        if simoleons_earned is None:
            simoleons_earned = 0
        else:
            relative_start_value = data_object.get_starting_values(objective_guid64)
            if relative_start_value is not None:
                simoleons = 0
                simoleons_earned -= relative_start_value[simoleons]
            return self.threshold.compare(simoleons_earned) or TestResultNumeric(False, 'TotalEventsSimoleonsEarnedTest: not enough Simoleons.', current_value=simoleons_earned,
              goal_value=(self.threshold.value),
              is_money=True)
        return TestResult.TRUE

    def save_relative_start_values(self, objective_guid64, data_object):
        data_object.set_starting_values(objective_guid64, [data_object.get_simoleons_earned(self.earned_source)])

    def validate_tuning_for_objective(self, objective):
        if self.threshold == 0:
            logger.error('Error in objective {}. Threshold has value of 0.', objective)

    def goal_value(self):
        return self.threshold.value

    @property
    def is_goal_value_money(self):
        return True


TunableTotalSimoleonsEarnedTest = TunableSingletonFactory.create_auto_factory(TotalSimoleonsEarnedTest)

class TotalTimePlayedTest(event_testing.test_base.BaseTest):
    test_events = (
     TestEvent.TestTotalTime,)
    USES_DATA_OBJECT = True
    FACTORY_TUNABLES = {'description':'This test is specifically for account based Achievements, upon         client connect testing if the players account has played the game long enough         in either sim time or server time to pass a threshold of sim or server minutes, respectively.        NOTE: The smallest ', 
     'use_sim_time':Tunable(bool, False, description='Whether to use sim time, or server time.'), 
     'threshold':TunableThreshold(description='The amount of time played to pass, measured         in the specified unit of time.'), 
     'time_unit':TunableEnumEntry(date_and_time.TimeUnit, date_and_time.TimeUnit.MINUTES, description='The unit of time         used for testing')}

    def __init__(self, use_sim_time, threshold, time_unit, **kwargs):
        (super().__init__)(safe_to_skip=True, **kwargs)
        self.use_sim_time = use_sim_time
        self.threshold = threshold
        self.treshold_value_in_time_units = threshold.value
        self.time_unit = time_unit
        if use_sim_time:
            threshold_value = clock.interval_in_sim_time(threshold.value, time_unit)
        else:
            threshold_value = clock.interval_in_real_time(threshold.value, time_unit)
            self.threshold.value = threshold_value.in_ticks()

    def get_expected_args(self):
        return {'data':event_testing.test_constants.FROM_DATA_OBJECT,  'objective_guid64':event_testing.test_constants.OBJECTIVE_GUID64}

    @cached_test
    def __call__(self, data=None, objective_guid64=None):
        if data is None:
            return TestResult(False, 'Data object is None, valid during zone load.')
        else:
            if self.use_sim_time:
                value_to_test = data.get_time_data(event_testing.event_data_const.TimeData.SimTime)
            else:
                value_to_test = data.get_time_data(event_testing.event_data_const.TimeData.ServerTime)
            relative_start_value = data.get_starting_values(objective_guid64)
            if relative_start_value is not None:
                time = 0
                value_to_test -= relative_start_value[time]
            value_in_time_units = self.threshold.compare(value_to_test) or date_and_time.ticks_to_time_unit(value_to_test, self.time_unit, self.use_sim_time)
            return TestResultNumeric(False, 'TotalTimePlayedTest: not enough time played.', current_value=(int(value_in_time_units)),
              goal_value=(self.goal_value()),
              is_money=False)
        return TestResult.TRUE

    def save_relative_start_values(self, objective_guid64, data_object):
        if self.use_sim_time:
            value_to_test = data_object.get_time_data(event_testing.event_data_const.TimeData.SimTime)
        else:
            value_to_test = data_object.get_time_data(event_testing.event_data_const.TimeData.ServerTime)
        data_object.set_starting_values(objective_guid64, [value_to_test])

    def goal_value(self):
        return int(self.treshold_value_in_time_units)


TunableTotalTimePlayedTest = TunableSingletonFactory.create_auto_factory(TotalTimePlayedTest)

class RoutabilityTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = ()
    FACTORY_TUNABLES = {'subject':TunableEnumEntry(description='\n            The subject of the test.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'target':TunableEnumEntry(description='\n            The target of the test.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Object), 
     'negate':Tunable(description='\n            If checked, passes the test if the sim does NOT have permissions\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'subjects':self.subject, 
         'targets':self.target}

    def __call__(self, subjects=(), targets=()):
        for subject in subjects:
            if not subject.is_sim:
                return TestResult(False, "subject of routability test isn't sim.", tooltip=(self.tooltip))
                subject_household_home_zone_id = subject.household.home_zone_id
                for target in targets:
                    if target.is_sim:
                        target = target.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
                    if not target:
                        if self.negate:
                            return TestResult(True)
                        return TestResult(False, "target of routability test isn't instantiated", tooltip=(self.tooltip))
                    if target.is_on_active_lot():
                        target_zone_id = target.zone_id
                        if subject_household_home_zone_id == target_zone_id:
                            continue
                        if subject.is_renting_zone(target_zone_id):
                            continue
                        subject_instance = subject.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
                        if not subject_instance:
                            if self.negate:
                                return TestResult(True)
                            return TestResult(False, "subject of routability test isn't instantiated, and not their home lot, and target not in open streets", tooltip=(self.tooltip))
                        for role in subject_instance.autonomy_component.active_roles():
                            if role.has_full_permissions or self.negate:
                                return TestResult(True)
                                return TestResult(False, "subject of routability test's roll doesn't have full permissions.", tooltip=(self.tooltip))

        if self.negate:
            return TestResult(False, 'subject has permission to route to target', tooltip=(self.tooltip))
        return TestResult(True)


class PostureTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = ()

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, value):
        if not value.target is None or value.container_supports is not None or any((posture.multi_sim for posture in value.required_postures)):
            logger.error('Posture Test in {} for multi-Sim postures requires a target participant.', source, owner='rmccord')
        else:
            if value.target is not None:
                if value.container_supports is None:
                    if not any((posture.multi_sim for posture in value.required_postures)):
                        logger.error('Posture Test in {} has target tuned but does not reference multi sim postures.', source, owner='rmccord')

    FACTORY_TUNABLES = {'description':'\n            Require the participants of this interaction to pass certain posture\n            tests.\n            ', 
     'subject':TunableEnumEntry(description='\n            The subject of this posture test.\n            ',
       tunable_type=ParticipantTypeActorTargetSim,
       default=ParticipantType.Actor), 
     'target':OptionalTunable(description='\n            If checking for multi sim postures, this is the linked Sim\n            participant to check for. This must be tuned if container supports\n            is enabled or if a multi sim posture exists in the list of required\n            postures.\n            ',
       tunable=TunableEnumEntry(description=',\n                The target of multi Sim postures.\n                ',
       tunable_type=ParticipantTypeActorTargetSim,
       default=(ParticipantTypeActorTargetSim.TargetSim))), 
     'required_postures':TunableList(description='\n            If this list is not empty, the subject is required to be\n            in at least one of the postures specified here.\n            \n            Note: If a multi Sim posture is tuned in this list, target must\n            also be tuned.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.POSTURE)))), 
     'prohibited_postures':TunableList(description='\n            The test will fail if the subject is in any of these postures.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.POSTURE)),
       pack_safe=True)), 
     'container_supports':OptionalTunable(description="\n            Test whether or not the subject's current posture's container\n            supports the specified posture.\n            ",
       tunable=TunableReference(description="\n                The posture that the container of the subject's current posture\n                must support.\n                ",
       manager=(services.get_instance_manager(sims4.resources.Types.POSTURE)))), 
     'verify_tunable_callback':_verify_tunable_callback}

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, safe_to_skip=True, **kwargs)

    def get_expected_args(self):
        required_args = {'actors': self.subject}
        if self.target is not None:
            required_args['targets'] = self.target
        return required_args

    @cached_test
    def __call__(self, actors, targets=None):
        subject_sim = next(iter(actors), None)
        target_sim = next(iter(targets), None) if targets is not None else None
        if subject_sim is None:
            return TestResult(False, 'Posture test failed because the actor is None.')
        subject_sim = subject_sim.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if subject_sim is None:
            return TestResult(False, 'Posture test failed because the actor is non-instantiated.', tooltip=(self.tooltip))
        if target_sim is not None:
            target_sim = target_sim.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if self.required_postures:
            for aspect in subject_sim.posture_state.aspects:
                if any((aspect.posture_type is required_posture and (not required_posture.multi_sim or aspect.linked_sim is target_sim) for required_posture in self.required_postures)):
                    break
            else:
                return TestResult(False, '{} is not in any of the required postures.', subject_sim, tooltip=(self.tooltip))

        if self.prohibited_postures:
            for posture_aspect in subject_sim.posture_state.aspects:
                if any((posture_aspect.posture_type is prohibited_posture for prohibited_posture in self.prohibited_postures)):
                    return TestResult(False, '{} is in a prohibited posture ({})', subject_sim, posture_aspect, tooltip=(self.tooltip))

        if self.container_supports is not None:
            container = subject_sim.posture.target
            return container is None or container.is_part or TestResult(False, 'Posture container for {} is None or not a part', (subject_sim.posture), tooltip=(self.tooltip))
            parts = {
             container}
            parts.update(container.get_overlapping_parts())
            if not any((p.supports_posture_type(self.container_supports) for p in parts)):
                return TestResult(False, 'Posture container {} does not support {}', container, (self.container_supports), tooltip=(self.tooltip))
            if self.container_supports.multi_sim:
                if target_sim is None:
                    return TestResult(False, 'Posture test failed because the target is None')
                if target_sim is None:
                    return TestResult(False, 'Posture test failed because the target is non-instantiated.')
                if not container.has_adjacent_part(target_sim):
                    return TestResult(False, 'Posture container {} requires an adjacent part for {} since {} is multi-Sim', container, target_sim, (self.container_supports), tooltip=(self.tooltip))
        return TestResult.TRUE


class IdentityTest(AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = ()
    FACTORY_TUNABLES = {'description':'\n            Require the specified participants to be the same, or,\n            alternatively, require them to be different.\n            ', 
     'subject_a':TunableEnumEntry(description='\n            The participant to be compared to subject_b.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Actor), 
     'subject_b':TunableEnumEntry(description='\n            The participant to be compared to subject_a.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Object), 
     'subjects_match':Tunable(description='\n            If True, subject_a must match subject_b. If False, they must not.\n            ',
       tunable_type=bool,
       default=False), 
     'use_definition':Tunable(description='\n            If checked, the two subjects will only compare definition. Not the\n            instance. This will mean two different types of chairs, for\n            instance, can return True if they use the same chair object\n            definition.\n            ',
       tunable_type=bool,
       default=False), 
     'use_part_owner':Tunable(description='\n            If checked, the two subjects will compare based on the part owner\n            if either are a part. \n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'subject_a':self.subject_a, 
         'subject_b':self.subject_b, 
         'affordance':ParticipantType.Affordance, 
         'context':ParticipantType.InteractionContext}

    @cached_test
    def __call__(self, subject_a=None, subject_b=None, affordance=None, context=None):
        subject_a = next(iter(subject_a), None)
        subject_b = next(iter(subject_b), None)
        if affordance is not None:
            if affordance.target_type == TargetType.ACTOR:
                if subject_a is None:
                    if self.subject_a == ParticipantType.TargetSim or self.subject_a == ParticipantType.Object:
                        subject_a = context.sim.sim_info
                if subject_b is None:
                    if self.subject_b == ParticipantType.TargetSim or self.subject_b == ParticipantType.Object:
                        subject_b = context.sim.sim_info
        if self.use_definition:
            subject_a = subject_a.definition
            subject_b = subject_b.definition
        if self.use_part_owner:
            if subject_a is not None:
                if not subject_a.is_sim:
                    if subject_a.is_part:
                        subject_a = subject_a.part_owner
            if subject_b is not None:
                if not subject_b.is_sim:
                    if subject_b.is_part:
                        subject_b = subject_b.part_owner
        if self.subjects_match:
            if subject_a is not subject_b:
                return TestResult(False, '{} must match {}, but {} is not {}', (self.subject_a), (self.subject_b), subject_a, subject_b, tooltip=(self.tooltip))
        else:
            if subject_a is subject_b:
                return TestResult(False, '{} must not match {}, but {} is {}', (self.subject_a), (self.subject_b), subject_a, subject_b, tooltip=(self.tooltip))
            return TestResult.TRUE


TunableIdentityTest = TunableSingletonFactory.create_auto_factory(IdentityTest)

class SituationRunningTestEvents(enum.Int):
    SituationEnded = event_testing.test_events.TestEvent.SituationEnded
    SituationStarted = event_testing.test_events.TestEvent.SituationStarted


class SituationRunningTest(AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'description':'\n            A test to see if the participant is part of any situations that are\n            running that satisfy the conditions of the test.\n            ', 
     'participant':OptionalTunable(tunable=TunableEnumEntry(description='\n                The subject of this situation test.\n                ',
       tunable_type=ParticipantType,
       default=(ParticipantType.Actor))), 
     'situation_whitelist':OptionalTunable(TunableSet(description='\n            Only whitelisted situations, specified by this set of references or\n            by tags in Tag Whitelist, can cause this test to pass. If no\n            situations are specified in this whitelist, all situations are\n            considered whitelisted.\n            ',
       tunable=TunableReference((services.get_instance_manager(sims4.resources.Types.SITUATION)),
       pack_safe=True))), 
     'situation_blacklist':OptionalTunable(description='\n            Blacklisted situations, specified by this set of references or by\n            tag in Tag Blacklist, will cause this test to fail.\n            ',
       tunable=TunableSet(tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.SITUATION)),
       pack_safe=True))), 
     'tag_whitelist':OptionalTunable(description='\n            Only whitelisted situations, specified by this set of tags or by\n            references in Situation Whitelist, can cause this test to pass. If\n            this whitelist is not enabled, all situations are considered\n            whitelisted.\n            ',
       tunable=TunableSet(tunable=TunableEnumWithFilter(tunable_type=Tag,
       filter_prefixes=('situation', ),
       default=(Tag.INVALID),
       pack_safe=True))), 
     'tag_blacklist':TunableSet(description='\n            Blacklisted situations, specified by this set of tags or by\n            references in Situation Tag Blacklist, will cause this test to\n            fail.\n            ',
       tunable=TunableEnumWithFilter(tunable_type=Tag,
       filter_prefixes=('situation', ),
       default=(Tag.INVALID),
       pack_safe=True)), 
     'level':OptionalTunable(tunable=TunableThreshold(description='\n                A check for the level of the situation we are checking.\n                ')), 
     'check_for_initiating_sim':Tunable(description='\n            If checked, the situation must be initiated by the tuned Participant.\n            ',
       tunable_type=bool,
       default=False), 
     'test_event':TunableEnumEntry(description='\n            The test event that this test will run on when tuned within an\n            objective or the main goal trigger of a sitaution.\n            \n            If you are tuning this on an interaction then it will do nothing.\n            ',
       tunable_type=SituationRunningTestEvents,
       default=SituationRunningTestEvents.SituationEnded)}

    @property
    def test_events(self):
        return (self.test_event,)

    def get_expected_args(self):
        if self.participant is not None:
            return {'test_targets':self.participant, 
             'situation':event_testing.test_constants.FROM_EVENT_DATA}
        return {'situation': event_testing.test_constants.FROM_EVENT_DATA}

    def _check_situations(self, situations, target):
        if not situations:
            if self.situation_whitelist is None:
                if self.tag_whitelist is None:
                    if self.situation_blacklist is not None or self.tag_blacklist:
                        if not self.level:
                            if not self.check_for_initiating_sim:
                                return TestResult.TRUE
        else:
            return TestResult(False, 'SituationTest: No situation matches criteria.', tooltip=(self.tooltip))
            if any((situation.tags & self.tag_blacklist for situation in situations)):
                return TestResult(False, 'SituationTest: blacklisted by tag.', tooltip=(self.tooltip))
            if self.situation_blacklist is not None and any((type(situation) in self.situation_blacklist for situation in situations)):
                return TestResult(False, 'SituationTest: blacklisted by reference.', tooltip=(self.tooltip))
        for situation in situations:
            if self.tag_whitelist is not None:
                if not situation.tags & self.tag_whitelist:
                    continue
            else:
                if self.situation_whitelist is not None:
                    if type(situation) not in self.situation_whitelist:
                        continue
                    elif self.level is not None:
                        level = situation.get_level()
                        if not (level is None or self.level.compare(level)):
                            continue
                    if self.check_for_initiating_sim and situation.initiating_sim_info is not target:
                        continue
            return TestResult.TRUE

        return TestResult(False, 'SituationRunningTest: No situation matching test criteria found.', tooltip=(self.tooltip))

    @cached_test
    def __call__(self, test_targets=None, situation=None):
        if test_targets is not None:
            for target in test_targets:
                if not target.is_sim:
                    return TestResult(False, 'SituationTest: Target {} is not a sim.', target, tooltip=(self.tooltip))
                elif target.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS) is None:
                    return TestResult(False, 'SituationTest: uninstantiated sim {} cannot be in any situations.', target, tooltip=(self.tooltip))
                    target_sim = target.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
                    if target_sim is None:
                        return TestResult(False, 'SituationTest: uninstantiated sim {} cannot be in any situations.', target, tooltip=(self.tooltip))
                    if situation is None:
                        situations = services.get_zone_situation_manager().get_situations_sim_is_in(target_sim)
                else:
                    situations = (
                     situation,)
                return self._check_situations(situations, target)

        else:
            if situation is None:
                situations = services.get_zone_situation_manager().running_situations()
            else:
                situations = (
                 situation,)
            return self._check_situations(situations, None)


TunableSituationRunningTest = TunableSingletonFactory.create_auto_factory(SituationRunningTest)

class CanCreateUserFacingSituationTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'allow_non_prestige_is_exempt':Tunable(description='\n            If checked, this test will return True if all the situations that\n            are running allow non-prestige events to be started.\n            ',
       tunable_type=bool,
       default=False), 
     'negate':Tunable(description="\n            If checked then this test will pass if the milestone is not\n            complete otherwise it will pass if it's been earned.\n            ",
       tunable_type=bool,
       default=False), 
     'subject':OptionalTunable(description='\n            If enabled, then this test ignores any situations that are linked to sims other than the specified subjects.\n            ',
       tunable=TunableEnumEntry(description='\n                The subject who can have a global situation created for him.\n                ',
       tunable_type=ParticipantTypeSim,
       default=(ParticipantType.Actor)))}

    def get_expected_args(self):
        if self.subject is not None:
            return {'subjects': self.subject}
        return {}

    @cached_test
    def __call__(self, subjects=None):
        for situation in services.get_zone_situation_manager().get_user_facing_situations_gen():
            if situation.linked_sim_id != GLOBAL_SITUATION_LINKED_SIM_ID and subjects:
                for subject in subjects:
                    if subject.sim_id == situation.linked_sim_id:
                        break
                else:
                    continue

                if not self.allow_non_prestige_is_exempt:
                    if self.negate:
                        return True
                    return TestResult(False, 'CanCreateUserFacingSituationTest: Cannot                                       create a user facing situation as another                                       one is already running.',
                      tooltip=(self.tooltip))
                if situation.allow_non_prestige_events or self.negate:
                    return True
                return TestResult(False, 'CanCreateUserFacingSituationTest: Cannot                                       create a user facing situation as another                                       user facing situation that does not allow                                       non-prestige events to be created is running.',
                  tooltip=(self.tooltip))

        if self.negate:
            return TestResult(False, 'CanCreateUserFacingSituationTest: Able to create a user-facing situation                               (and the result is negated).',
              tooltip=(self.tooltip))
        return TestResult.TRUE


class UserFacingSituationRunningTest(event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'description':'\n            Test to see if there is a user facing situation running or not.\n            ', 
     'is_running':Tunable(description='\n            If checked then this test will return true if a user facing\n            situation is running in the current zone.  If not checked then\n            this test will return false if a user facing situation is\n            running in this zone.\n            ',
       tunable_type=bool,
       default=False)}

    def __init__(self, is_running, **kwargs):
        (super().__init__)(**kwargs)
        self.is_running = is_running

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        is_user_facing_situation_running = services.get_zone_situation_manager().is_user_facing_situation_running()
        if self.is_running:
            if is_user_facing_situation_running:
                return TestResult.TRUE
            return TestResult(False, 'UserFacingSituationRunningTest: A user facing situation is not running.', tooltip=(self.tooltip))
        else:
            if is_user_facing_situation_running:
                return TestResult(False, 'UserFacingSituationRunningTest: A user facing situation is running.', tooltip=(self.tooltip))
            return TestResult.TRUE


TunableUserFacingSituationRunningTest = TunableSingletonFactory.create_auto_factory(UserFacingSituationRunningTest)

class SituationJobTest(event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'description':'\n            Require the tuned participant to have a specific situation job.\n            If multiple participants, ALL participants must have the required\n            job to pass.\n            ', 
     'participant':TunableEnumEntry(description='\n                The subject of this situation job test.\n                ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'situation_jobs':TunableSet(description='\n                The participant must have this job in this list or a job that\n                matches the role_tags.\n                ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)),
       pack_safe=True)), 
     'role_tags':TunableSet(description='\n                The  participant must have a job that matches the role_tags or\n                have the situation_job.\n                ',
       tunable=TunableEnumEntry(tunable_type=Tag,
       default=(Tag.INVALID),
       pack_safe=True)), 
     'negate':Tunable(description='\n                If checked then the test result will be reversed, so it will\n                test to see if they are not in a job or not in role state\n                that has matching tags.\n                ',
       tunable_type=bool,
       default=False)}

    def __init__(self, participant, situation_jobs, role_tags, negate, **kwargs):
        (super().__init__)(**kwargs)
        self.participant = participant
        self.situation_jobs = situation_jobs
        self.role_tags = role_tags
        self.negate = negate

    def get_expected_args(self):
        return {'test_targets': self.participant}

    @cached_test
    def __call__(self, test_targets=None):
        if not test_targets:
            return TestResult(False, 'SituationJobTest: No test targets to check.')
        for target in test_targets:
            if not target.is_sim:
                return TestResult(False, 'SituationJobTest: Test being run on target {} that is not a sim.', target, tooltip=(self.tooltip))
                if isinstance(target, sims.sim_info.SimInfo):
                    if target.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS) is None:
                        return TestResult(False, 'SituationJobTest: {} is not an instantiated sim.', target, tooltip=(self.tooltip))
                    target = target.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
                sim_has_job = False
                for situation in services.get_zone_situation_manager().get_situations_sim_is_in(target):
                    current_job_type = situation.get_current_job_for_sim(target)
                    if current_job_type in self.situation_jobs:
                        sim_has_job = True
                        break
                    elif self.role_tags & situation.get_role_tags_for_sim(target):
                        sim_has_job = True
                        break

                if self.negate:
                    if sim_has_job:
                        return TestResult(False, "SituationJobTest: Sim has the required jobs when it shouldn't.", tooltip=(self.tooltip))
                else:
                    return sim_has_job or TestResult(False, 'SituationJobTest: Sim does not have required situation job.', tooltip=(self.tooltip))

        return TestResult.TRUE


TunableSituationJobTest = TunableSingletonFactory.create_auto_factory(SituationJobTest)

class SituationAvailabilityTest(event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'description':"Test whether it's possible for this Sim to host a particular Situation.", 
     'situation':TunableReference(description='\n            The Situation to test against\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION))}

    def __init__(self, situation, **kwargs):
        (super().__init__)(**kwargs)
        self.situation = situation

    def get_expected_args(self):
        return {'hosts':ParticipantType.Actor, 
         'targets':ParticipantType.TargetSim}

    @cached_test
    def __call__(self, hosts, targets=None):
        for host in hosts:
            if self.situation.cost() > host.household.funds.money:
                return TestResult(False, 'Cannot afford this Situation.', tooltip=(self.tooltip))
            for target in targets:
                target_sim_id = 0 if target is None else target.id
                if not self.situation.is_situation_available(host, target_sim_id):
                    return TestResult(False, 'Sim not allowed to host this Situation or Target not allowed to come.')

        return TestResult.TRUE


TunableSituationAvailabilityTest = TunableSingletonFactory.create_auto_factory(SituationAvailabilityTest)

class SituationInJoinableStateTest(event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'description':"Test whether it's possible for this Sim to host a particular Situation.", 
     'situation':TunableReference(description='\n            The Situation to test against\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION),
       allow_none=True), 
     'situation_tags':TunableSet(description='\n            Tags for arbitrary groupings of situation types.\n            ',
       tunable=TunableEnumWithFilter(tunable_type=Tag,
       filter_prefixes=[
      'situation'],
       default=(Tag.INVALID),
       pack_safe=True))}

    def __init__(self, situation, situation_tags, **kwargs):
        (super().__init__)(**kwargs)
        self.situation = situation
        self.situation_tags = situation_tags

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        situation_to_test = []
        situation_manager = services.get_zone_situation_manager()
        if self.situation is not None:
            running_situation = situation_manager.get_situation_by_type(self.situation)
            if running_situation is not None:
                situation_to_test.append(running_situation)
        else:
            if self.situation_tags:
                situation_to_test.extend(situation_manager.get_situations_by_tags(self.situation_tags))
            return situation_to_test or TestResult(False, ('No running situation found for situation {} or situation_tag {}.'.format(self.situation, self.situation_tags)), tooltip=(self.tooltip))
        for situation in situation_to_test:
            if not situation.is_in_joinable_state():
                return TestResult(False, ('Situation {} is not in running state.'.format(situation)), tooltip=(self.tooltip))

        return TestResult.TRUE


TunableSituationInJoinableStateTest = TunableSingletonFactory.create_auto_factory(SituationInJoinableStateTest)

class SituationCountTest(event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'situation':TunablePackSafeReference(description='\n            A reference to the type of situation to test.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION)), 
     'additional_situations':TunableList(description='\n            References to additional situations to test.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.SITUATION)),
       pack_safe=True)), 
     'test':TunableThreshold(description='\n            A Threshold test that specifies the allowed values for the count\n            of the tuned situation.\n            ')}

    def __init__(self, situation, additional_situations, test, **kwargs):
        (super().__init__)(**kwargs)
        self._situations = additional_situations
        if situation is not None:
            self._situations = self._situations + (situation,)
        self._test = test

    def get_expected_args(self):
        return {}

    def __call__(self):
        if not self._situations:
            return TestResult(False, 'There are no tuned situations loaded, so fail.')
        situation_manager = services.get_zone_situation_manager()
        situations = [situation for situation in situation_manager.get_all() if type(situation) in self._situations]
        if self._test.compare(len(situations)):
            return TestResult.TRUE
        return TestResult(False, 'Not enough situations of the tuned types in the zone.', tooltip=(self.tooltip))


TunableSituationCountTest = TunableSingletonFactory.create_auto_factory(SituationCountTest)

class BillsTest(event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'description':"Require the participant's bill status to match the specified conditions.", 
     'participant':TunableEnumEntry(description='\n            The subject whose household is the object of this delinquency test.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'delinquency_states':OptionalTunable(TunableList(TunableTuple(description='\n            Tuple containing a utility and its required delinquency state.\n            ',
       utility=(TunableEnumEntry(Utilities, None)),
       is_delinquent=Tunable(description='\n                Whether this utility is required to be delinquent or not delinquent.\n                ',
       tunable_type=bool,
       default=True)))), 
     'additional_bills_delinquency_states':OptionalTunable(TunableList(TunableTuple(description='\n            Tuple containing an AdditionalBillSource and its required\n            delinquency state. EX: This interaction requires that the\n            Maid_Service bill source not be delinquent.\n            ',
       bill_source=(TunableEnumEntry(sims.bills_enums.AdditionalBillSource, None)),
       is_delinquent=Tunable(description='\n                Whether this AdditionalBillSource is required to be delinquent or not delinquent.\n                ',
       tunable_type=bool,
       default=True)))), 
     'payment_due':OptionalTunable(description='\n            Whether or not the participant is required to have a bill payment due.\n            ',
       tunable=TunableTuple(description='\n                Whether or not the participant is required to have a bill payment due.\n                ',
       is_due=Tunable(description="\n                    Whether this bill's payment is required to be due or not due.\n                    ",
       tunable_type=bool,
       default=True),
       utility_consumption_threshold=OptionalTunable(description="\n                    Tests to see if the bill's net consumption of utilities passes the threshold. \n                    Only tested if the bill's payment is currently due (and is required to be due).\n                    ",
       tunable=TunableThreshold(description='\n                        Minimum amount needed to pass this test (if bill is due).\n                        ')))), 
     'test_participant_owned_households':Tunable(description="\n            If checked, this test will check the delinquency states of all the\n            participant's households.  If unchecked, this test will check the\n            delinquency states of the owning household of the active lot.\n            ",
       tunable_type=bool,
       default=False), 
     'is_repo_man_due':OptionalTunable(description='\n            If enabled we will only pass this test if the bill is delinquent enough to require the repo man to\n            show up.\n            ',
       tunable=Tunable(description='\n                Check if the repo man is due to collect bad bills or not.\n                ',
       tunable_type=bool,
       default=True))}

    def __init__(self, participant, delinquency_states, additional_bills_delinquency_states, payment_due, test_participant_owned_households, is_repo_man_due, **kwargs):
        (super().__init__)(**kwargs)
        self.participant = participant
        self.delinquency_states = delinquency_states
        self.additional_bills_delinquency_states = additional_bills_delinquency_states
        self.payment_due = payment_due
        self.test_participant_owned_households = test_participant_owned_households
        self.is_repo_man_due = is_repo_man_due

    def get_expected_args(self):
        return {'test_targets': self.participant}

    @cached_test
    def __call__(self, test_targets=None):
        if not self.test_participant_owned_households:
            target_households = [
             services.owning_household_of_active_lot()]
        else:
            target_households = []
            for target in test_targets:
                target_households.append(services.household_manager().get_by_sim_id(target.id))

        for household in target_households:
            if self.delinquency_states is not None:
                for state in self.delinquency_states:
                    if household is None:
                        if state.is_delinquent:
                            return TestResult(False, 'BillsTest: Required {} to be delinquent, but there is no active household.', (state.utility), tooltip=(self.tooltip))
                        elif household.bills_manager.is_utility_delinquent(state.utility) != state.is_delinquent:
                            return TestResult(False, "BillsTest: Participant's delinquency status for the {} utility is not correct.", (state.utility), tooltip=(self.tooltip))

            else:
                if self.additional_bills_delinquency_states is not None:
                    for state in self.additional_bills_delinquency_states:
                        if household is None:
                            if state.is_delinquent:
                                return TestResult(False, 'BillsTest: Required {} to be delinquent, but there is no active household.', (state.bill_source), tooltip=(self.tooltip))
                            elif household.bills_manager.is_additional_bill_source_delinquent(state.bill_source) != state.is_delinquent:
                                return TestResult(False, "BillsTest: Participant's delinquency status for the {} additional bill source is not correct.", (state.bill_source), tooltip=(self.tooltip))

                if self.payment_due is not None:
                    if household is not None:
                        household_payment_due = household.bills_manager.mailman_has_delivered_bills()
                    else:
                        household_payment_due = False
                    if household_payment_due != self.payment_due.is_due:
                        return TestResult(False, "BillsTest: Participant's active bill status does not match the specified active bill status.", tooltip=(self.tooltip))
                    if self.payment_due.is_due and household_payment_due and self.payment_due.utility_consumption_threshold is not None:
                        total_net_consumption = household.bills_manager.get_utility_bill_total_net_production()
                        if not self.payment_due.utility_consumption_threshold.compare(total_net_consumption):
                            return TestResult(False, "BillsTest: Participant's net utility consumption did not pass the threshold.", tooltip=(self.tooltip))
            if self.is_repo_man_due is not None:
                if self.is_repo_man_due:
                    if not household.bills_manager.is_repo_man_due:
                        return TestResult(False, 'Checking if the repo man is due and they are not.', tooltip=(self.tooltip))
                elif household.bills_manager.is_repo_man_due:
                    return TestResult(False, 'Checking if the repo man is not due and they are.', tooltip=(self.tooltip))

        return TestResult.TRUE


TunableBillsTest = TunableSingletonFactory.create_auto_factory(BillsTest)

class HouseholdCanPostAlertTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'subject': TunableEnumEntry(description='\n            The subject whose household to check.\n            ',
                  tunable_type=ParticipantTypeSingle,
                  default=(ParticipantTypeSingle.Actor))}

    def get_expected_args(self):
        return {'test_targets': self.subject}

    def __call__(self, test_targets=None):
        for target in test_targets:
            if target.is_sim:
                household = target.household
                if household.missing_pet_tracker.alert_posted:
                    return TestResult(False, 'HouseholdCanPostAlertTest: Household with id {} has already posted an alert.', (household.id), tooltip=(self.tooltip))
                return TestResult.TRUE
            else:
                return TestResult(False, 'HouseholdCanPostAlertTest: Test target {} is not a Sim.', target)

        return TestResult.TRUE


class HouseholdMissingPetTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'subject': TunableEnumEntry(description='\n            The subject whose household to check.\n            ',
                  tunable_type=ParticipantTypeSingle,
                  default=(ParticipantTypeSingle.Actor))}

    def get_expected_args(self):
        return {'test_targets': self.subject}

    def __call__(self, test_targets=None):
        for target in test_targets:
            if target.is_sim:
                household = target.household
                if household.missing_pet_tracker.missing_pet_id != 0:
                    return TestResult.TRUE
                return TestResult(False, 'HouseholdMissingPetTest: Household with id {} has no missing pets.', household.id)
            else:
                return TestResult(False, 'HouseholdMissingPetTest: Test target {} is not a Sim.', target)

        return TestResult.TRUE


class HouseholdSizeTest(event_testing.test_base.BaseTest, HasTunableSingletonFactory):
    test_events = (
     TestEvent.HouseholdChanged,)
    COUNT_FROM_PARTICIPANT = 0
    COUNT_EXPLICIT = 1
    COUNT_ACTUAL_SIZE = 2
    COUNT_TESTED_SIM_INFOS = 3
    FACTORY_TUNABLES = {'description':"\n            Require the specified participant's household to have a specified\n            number of free Sim slots.\n            ", 
     'participant':TunableEnumEntry(description='\n            The subject whose household is the object of this test.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'test_type':TunableVariant(description='\n            The type of test to \n            ',
       participant=TunableTuple(description="\n                Use this option when you're testing a specific Sim being added\n                to the household.\n                ",
       locked_args={'count_type': COUNT_FROM_PARTICIPANT},
       participant=TunableEnumEntry(description='\n                    The participant whose required slot count we consider.\n                    ',
       tunable_type=ParticipantType,
       default=(ParticipantType.TargetSim))),
       count=TunableTuple(description="\n                Use this option when you're testing for a specific number of\n                free slots in the household.\n                ",
       locked_args={'count_type': COUNT_EXPLICIT},
       count=TunableThreshold(description='\n                    The number of required free slots for the specified\n                    household.\n                    ',
       value=Tunable(description='\n                        The value of a threshold.\n                        ',
       tunable_type=int,
       default=1),
       default=(sims4.math.Threshold(1, sims4.math.Operator.GREATER_OR_EQUAL.function)))),
       actual_size=TunableTuple(description="\n                Use this option when you're testing the actual number of sims\n                in a household.  This should not be used for testing if you\n                are able to add a sim to the household and should only be used\n                for functionality that depents on the actual household members\n                being there and not counting reserved slots.\n                ex. Achievement for having a household of 8 sims.\n                ",
       locked_args={'count_type': COUNT_ACTUAL_SIZE},
       count=TunableThreshold(description='\n                    The number of household members.\n                    ',
       value=Tunable(description='\n                        The value of a threshold.\n                        ',
       tunable_type=int,
       default=1),
       default=(sims4.math.Threshold(1, sims4.math.Operator.GREATER_OR_EQUAL.function)))),
       test_sim_infos=TunableTuple(description="\n                Use this option when you're testing that a number of sims\n                in a household pass some tuned test.\n                ex. At least three sims in household are toddlers.\n                ",
       locked_args={'count_type': COUNT_TESTED_SIM_INFOS},
       count=TunableThreshold(description='\n                    The number of household members.\n                    ',
       value=Tunable(description='\n                        The value of a threshold.\n                        ',
       tunable_type=int,
       default=1),
       default=(sims4.math.Threshold(1, sims4.math.Operator.GREATER_OR_EQUAL.function))),
       test=TunableVariant(description='\n                    A test to apply to each sim in the household. If the test\n                    passes for a given sim, that will count toward the total.\n                    ',
       sim_info=SimInfoTest.TunableFactory(locked_args={'tooltip':None, 
      'who':ParticipantType.Actor}),
       scenario_role=ScenarioRoleTest.TunableFactory(locked_args={'tooltip':None, 
      'target_sim':ParticipantType.Actor}),
       default='sim_info')),
       default='count')}

    def __init__(self, participant, test_type, **kwargs):
        (super().__init__)(**kwargs)
        self.participant = participant
        self._sub_test = None
        self.count_type = test_type.count_type
        if self.count_type == self.COUNT_FROM_PARTICIPANT:
            self._expected_args = {'participants':self.participant, 
             'targets':test_type.participant}
        else:
            if self.count_type == self.COUNT_EXPLICIT:
                self._expected_args = {'participants': self.participant}
                self._count = test_type.count
            else:
                if self.count_type == self.COUNT_ACTUAL_SIZE:
                    self._expected_args = {'participants': self.participant}
                    self._count = test_type.count
                else:
                    if self.count_type == self.COUNT_TESTED_SIM_INFOS:
                        self._expected_args = {'participants': self.participant}
                        self._count = test_type.count
                        self._sub_test = test_type.test

    def get_expected_args(self):
        return self._expected_args

    @cached_test
    def __call__(self, participants={}, targets={}):
        for participant in participants:
            if not participant.is_sim:
                return TestResult(False, 'Participant {} is not a sim.', participant, tooltip=(self.tooltip))
                if self.count_type == self.COUNT_FROM_PARTICIPANT:
                    if not targets:
                        return TestResult(False, 'No targets found for HouseholdSizeTest when it requires them.',
                          tooltip=(self.tooltip))
                    for target in targets:
                        if not target.is_sim:
                            return TestResult(False, 'Target {} is not a sim.', target, tooltip=(self.tooltip))
                            return participant.household.can_add_sim_info(target) or TestResult(False, 'Cannot add {} to {}', target, (participant.household), tooltip=(self.tooltip))

                elif self.count_type == self.COUNT_EXPLICIT:
                    free_slot_count = participant.household.free_slot_count
                    if not self._count.compare(free_slot_count):
                        return TestResult(False, "Household doesn't meet free slot count requirement.", tooltip=(self.tooltip))
                elif self.count_type == self.COUNT_ACTUAL_SIZE:
                    household_size = participant.household.household_size
                    if not self._count.compare(household_size):
                        return TestResult(False, "Household doesn't meet size requirements.",
                          tooltip=(self.tooltip))
                elif self.count_type == self.COUNT_TESTED_SIM_INFOS:
                    count = 0
                    for sim_info in participant.household:
                        resolver = SingleSimResolver(sim_info)
                        if resolver(self._sub_test):
                            count += 1

                    return self._count.compare(count) or TestResult(False, "Household doesn't meet tested size requirements.",
                      tooltip=(self.tooltip))

        return TestResult.TRUE


class ServiceNpcHiredTest(event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'description':"\n            Tests on the state of service npc requests of the participant's household.\n             EX whether a maid was requested or has been cancelled\n             ", 
     'participant':TunableEnumEntry(description="\n            The subject of this test. We will use the subject's household\n            to test if the household has requested a service\n            ",
       tunable_type=ParticipantTypeActorTargetSim,
       default=ParticipantTypeActorTargetSim.Actor), 
     'service':TunableReference(description='\n            The service tuning to perform the test against\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SERVICE_NPC),
       pack_safe=True), 
     'hired':Tunable(description="\n            Whether to test if service is hired or not hired.\n            EX: If True, we test that you have hired the tuned service.\n            If False, we test that you don't have the service hired.\n            ",
       tunable_type=bool,
       default=True)}

    def __init__(self, participant, service, hired, **kwargs):
        (super().__init__)(**kwargs)
        self.participant = participant
        self.service = service
        self.hired = hired

    def get_expected_args(self):
        return {'test_targets': self.participant}

    @cached_test
    def __call__(self, test_targets=None):
        if self.service is None:
            if not self.hired:
                return TestResult.TRUE
            return TestResult(False, 'Service was not found, most likely due to pack safeness.', tooltip=(self.tooltip))
        for target in test_targets:
            if not target.is_sim:
                return TestResult(False, '{} is not a sim.', target, tooltip=(self.tooltip))
            household = target.household
            service_record = household.get_service_npc_record((self.service.guid64), add_if_no_record=False)
            if self.hired:
                if not service_record is None:
                    return service_record.hired or TestResult(False, '{} has not hired service {}.', household, (self.service), tooltip=(self.tooltip))
                elif service_record is not None:
                    if service_record.hired:
                        return TestResult(False, '{} has already hired service {}.', household, (self.service), tooltip=(self.tooltip))

        return TestResult.TRUE


TunableServiceNpcHiredTest = TunableSingletonFactory.create_auto_factory(ServiceNpcHiredTest)

class UserRunningInteractionTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, value):
        if value.test_for_not_running:
            if value.all_participants_running:
                logger.error('Test for not running and all participants running cannot both be true', owner='nbaker')

    FACTORY_TUNABLES = {'description':'\n            A test that verifies if any of the users of the selected participant are\n            running a specific interaction.\n            ', 
     'participant':TunableEnumEntry(description='\n            The participant of the interaction used to fetch the users against\n            which the test is run.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Object), 
     'affordances':TunableList(TunableReference(description='\n            If any of the participants are running any of these affordances,\n            this test will pass.\n            ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       class_restrictions='SuperInteraction',
       pack_safe=True)), 
     'affordance_lists':TunableList(description='\n            If any of the participants are running any of the affordances in\n            these lists, this test will pass.\n            ',
       tunable=snippets.TunableAffordanceListReference()), 
     'test_for_not_running':Tunable(description='\n            Changes this test to check for the opposite case, as in verifying that this interaction is not running.\n            ',
       tunable_type=bool,
       default=False), 
     'all_participants_running':Tunable(description='\n            Returns true only if *all* valid particpants are running a valid \n            affordance.\n            \n            Incompatible with test for not running being true',
       tunable_type=bool,
       default=False), 
     'verify_tunable_callback':_verify_tunable_callback}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.update_all_affordances()

    def update_all_affordances(self):
        self.all_affordances = set(self.affordances)
        for affordance_list in self.affordance_lists:
            self.all_affordances.update(affordance_list)

    def get_expected_args(self):
        return {'test_targets': self.participant}

    def matching_interaction_in_si_state(self, si_state):
        return any((si.get_interaction_type() in self.all_affordances for si in si_state))

    @cached_test
    def __call__(self, test_targets=()):
        interaction_is_running = False
        for target in test_targets:
            if target.is_sim:
                if target.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS) is None:
                    return TestResult(False, '{} is not an instanced object', target, tooltip=(self.tooltip))
                target = target.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
                if self.matching_interaction_in_si_state(target.si_state):
                    interaction_is_running = True
                else:
                    if self.all_participants_running:
                        return TestResult(False, 'Target sim is not running one of {} and test specifies all participants running', (self.all_affordances), tooltip=(self.tooltip))
            if target.is_part:
                target = target.part_owner
            for user in target.get_users(sims_only=True):
                if self.matching_interaction_in_si_state(user.si_state):
                    interaction_is_running = True
                    if not self.all_participants_running:
                        break
                    elif self.all_participants_running:
                        return TestResult(False, 'user {} is not running one of {} and test specifies all participants running', user, (self.all_affordances), tooltip=(self.tooltip))

            if interaction_is_running and not self.all_participants_running:
                break

        if self.test_for_not_running:
            if interaction_is_running:
                return TestResult(False, 'User is running one of {}', (self.all_affordances), tooltip=(self.tooltip))
            return TestResult.TRUE
        if interaction_is_running:
            return TestResult.TRUE
        return TestResult(False, 'No user found running one of {}', (self.all_affordances), tooltip=(self.tooltip))


class ParticipantRunningInteractionTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            The participant of the interaction to test. The test will pass if any participant\n            is running any of the affordances.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'affordances':TunableList(TunableReference(description='\n            The affordances to test.  The test will pass if any participant is running any of \n            the affordances.\n            ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       class_restrictions='SuperInteraction',
       pack_safe=True)), 
     'affordance_lists':TunableList(description='\n            The affordances to test.  The test will pass if any participant is running any of \n            the affordances.\n            ',
       tunable=snippets.TunableAffordanceListReference()), 
     'test_for_not_running':Tunable(description='\n            Changes this test to check for the opposite case, as in verifying that none of these \n            affordances are being run by any of the participants.',
       tunable_type=bool,
       default=False), 
     'test_interaction_queue':Tunable(description="\n            Besides SI states, also check interactions pending in the sim's interaction queue.\n            ",
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'test_targets': self.participant}

    @cached_test
    def __call__(self, test_targets=()):
        all_affordances = set(self.affordances)
        for affordance_list in self.affordance_lists:
            all_affordances.update(affordance_list)

        found_sim = False
        for sim_info in test_targets:
            if not sim_info.is_sim:
                continue
            found_sim = True
            sim = sim_info.get_sim_instance()
            if sim is None:
                continue
            iterable_interactions = itertools.chain(sim.si_state, sim.queue) if self.test_interaction_queue else sim.si_state
            for interaction in iterable_interactions:
                if interaction.is_finishing:
                    continue
                if interaction.get_interaction_type() in all_affordances:
                    if self.test_for_not_running:
                        return TestResult(False, 'Sim {} is running one of {}', sim, all_affordances, tooltip=(self.tooltip))
                    return TestResult.TRUE

            transition_controller = sim.transition_controller
            if transition_controller is not None:
                if transition_controller.interaction is not None and transition_controller.interaction.get_interaction_type() in all_affordances:
                    if self.test_for_not_running:
                        return TestResult(False, 'Sim {} is transitioning to one of {}', sim, all_affordances, tooltip=(self.tooltip))
                return TestResult.TRUE

        if not found_sim:
            return TestResult(False, 'No sim found in participant type: {}', test_targets, tooltip=(self.tooltip))
        if self.test_for_not_running:
            return TestResult.TRUE
        return TestResult(False, 'No sim was running one of {}', all_affordances, tooltip=(self.tooltip))


class AchievementEarnedFactory(TunableFactory):

    @staticmethod
    def factory(sim, tooltip, unlocked, achievement, negate=False):
        if achievement is None:
            if hasattr(unlocked, 'aspiration_type'):
                return TestResult(False,
                  'UnlockedTest: non-achievement object {} passed to AchievementEarnedFactory.',
                  unlocked,
                  tooltip=tooltip)
            return TestResult.TRUE
        milestone_unlocked = sim.account.achievement_tracker.milestone_completed(achievement)
        if milestone_unlocked != negate:
            return TestResult.TRUE
        return TestResult(False, 'UnlockedTest: Sim has not unlocked achievement {} or unexpectedly did so.', achievement, tooltip=tooltip)

    FACTORY_TYPE = factory

    def __init__(self, **kwargs):
        (super().__init__)(description='\n            This option tests for completion of a tuned Achievement.\n            ', 
         achievement=TunableReference(description='\n                The achievement we want to test.\n                ',
  manager=(services.get_instance_manager(sims4.resources.Types.ACHIEVEMENT))), 
         negate=Tunable(description='\n                If enabled, we will require that the achievement is NOT unlocked.\n                ',
  tunable_type=bool,
  default=False), **kwargs)


class AspirationEarnedFactory(TunableFactory):

    @staticmethod
    def factory(sim_info, tooltip, unlocked, aspiration, negate=False):
        if sim_info.aspiration_tracker is None:
            return TestResult(False,
              'UnlockedTest: aspiration tracker not present on Sim info {}.',
              sim_info,
              tooltip=tooltip)
        milestone_unlocked = sim_info.aspiration_tracker.milestone_completed(aspiration)
        if milestone_unlocked != negate:
            return TestResult.TRUE
        return TestResult(False, 'UnlockedTest: Sim has not unlocked aspiration {} or unexpectedly did so.', aspiration, tooltip=tooltip)

    FACTORY_TYPE = factory

    def __init__(self, **kwargs):
        (super().__init__)(description='\n            This option tests for completion of a tuned Aspiration.\n            ', 
         aspiration=TunableReference(description='\n                The aspiration we want to test.\n                ',
  manager=(services.get_instance_manager(sims4.resources.Types.ASPIRATION))), 
         negate=Tunable(description='\n                If enabled, we will require that the aspiration is NOT unlocked.\n                ',
  tunable_type=bool,
  default=False), **kwargs)


class TestHouseholdMilestoneEarned(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'household_milestone':TunableReference(description='\n            The household milestone to check unlock status against. \n            ',
       pack_safe=True,
       manager=services.get_instance_manager(sims4.resources.Types.HOUSEHOLD_MILESTONE)), 
     'negate':Tunable(description="\n            If checked then this test will pass if the milestone is not\n            complete otherwise it will pass if it's been earned.\n            ",
       tunable_type=bool,
       default=False)}

    def __call__(self, sim_info, tooltip, unlocked):
        if self.household_milestone is None:
            return TestResult(False, 'Tuned milestone on {} cannot be None.', self, tooltip=tooltip)
        if sim_info.household is not None:
            if sim_info.household.household_milestone_tracker is not None:
                milestone_unlocked = sim_info.household.household_milestone_tracker.milestone_completed(self.household_milestone)
                if milestone_unlocked == self.negate:
                    return TestResult(False, 'UnlockedTest: milestone ({}) has an unlocked status of ({}), which is not the required value.', (self.household_milestone), milestone_unlocked, tooltip=tooltip)
        return TestResult.TRUE


class TestAspirationUnlock(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'check_aspiration_type':OptionalTunable(description='\n            If enabled then we will check the aspiration type of the aspiration\n            that was just unlocked.\n            ',
       tunable=TunableEnumEntry(description='\n                The aspiration type that we are checking if it just completed.\n                ',
       tunable_type=AspriationType,
       default=(AspriationType.FULL_ASPIRATION))), 
     'check_complete_only_in_sequence':OptionalTunable(description='\n            If enabled then we will check that the aspiration that was just\n            unlocked has a specific value of complete only in sequence set.\n            ',
       tunable=Tunable(description='\n                If complete only in sequence should be also be set or not.\n                ',
       tunable_type=bool,
       default=True))}

    def __call__(self, sim_info, tooltip, unlocked):
        if unlocked is None:
            return TestResult(False, 'UnlockedTest: No aspiration Unlocked.',
              tooltip=tooltip)
            aspiration_type = getattr(unlocked, 'aspiration_type', None)
            if aspiration_type is None:
                return TestResult(False, 'UnlockedTest: non-aspiration object {} passed to TestAspirationUnlock.',
                  unlocked,
                  tooltip=tooltip)
        else:
            if self.check_aspiration_type is not None:
                if aspiration_type != self.check_aspiration_type:
                    return TestResult(False, "UnlockedTest: aspiration object {} passed in isn't of type {}.",
                      unlocked,
                      (self.check_aspiration_type),
                      tooltip=tooltip)
            if self.check_complete_only_in_sequence is not None and unlocked.do_not_register_events_on_load != self.check_complete_only_in_sequence:
                return TestResult(False, 'UnlockedTest: aspiration object {} does not have do_not_register_events_on_load equal to {}.',
                  unlocked,
                  (self.check_complete_only_in_sequence),
                  tooltip=tooltip)
        return TestResult.TRUE


class TestAspirationsAvailable(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'negate': Tunable(description='\n            If checked then this test will pass if all aspirations are\n            complete otherwise it will pass if there is a still an aspiration\n            that can be unlocked.\n            ',
                 tunable_type=bool,
                 default=False)}

    def __call__(self, sim_info, tooltip, unlocked):
        if sim_info.is_toddler_or_younger:
            return TestResult(False, "Todders and below can't have primary aspirations.",
              tooltip=tooltip)
        aspiration_tracker = sim_info.aspiration_tracker
        for aspiration_track in services.get_instance_manager(sims4.resources.Types.ASPIRATION_TRACK).types.values():
            if not aspiration_track.is_valid_for_sim(sim_info):
                continue
            for aspiration in aspiration_track.aspirations.values():
                if aspiration_tracker.milestone_completed(aspiration) or self.negate:
                    return TestResult(False, 'TestAspirationsAvailable: There is an aspiration {} that has not been completed.',
                      aspiration,
                      tooltip=tooltip)
                    return TestResult.TRUE

        if self.negate:
            return TestResult.TRUE
        return TestResult(False, 'TestAspirationsAvailable: There are no aspirations still to unlock.',
          tooltip=tooltip)


class TestBuildBuyRewardEarned(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'object_definition':TunableReference(description='\n            Tests if the specified Object Definition has been unlocked in Build/Buy.\n            \n            This test will NOT work for Build Buy objects that are always unlocked.\n            It needs to have been locked before and unlocked through something like\n            a Build Buy Object Reward.\n            ',
       manager=services.definition_manager()), 
     'negate':Tunable(description='\n            If checked, the test will pass if the Build/Buy object is still locked.\n            ',
       tunable_type=bool,
       default=False)}

    def _get_resource_key(self):
        return sims4.resources.Key(Types.OBJCATALOG, self.object_definition.id)

    def __call__(self, sim_info, tooltip, unlocked):
        has_key = self._get_resource_key() in sim_info.household.build_buy_unlocks
        if has_key != self.negate:
            return TestResult.TRUE
        return TestResult(False, 'UnlockedTest: Build/Buy object ({}) has an unlocked status of ({}), which is not the required value.',
          (self.object_definition),
          has_key,
          tooltip=tooltip)


class UnlockedTest(event_testing.test_base.BaseTest):
    test_events = (
     TestEvent.UnlockEvent,)
    USES_EVENT_DATA = True

    @TunableFactory.factory_option
    def unlock_type_override(allow_achievment=True):
        kwargs = {}
        default = 'aspiration'
        kwargs['aspiration'] = AspirationEarnedFactory()
        kwargs['aspiration_unlocked'] = TestAspirationUnlock.TunableFactory()
        kwargs['aspirations_available'] = TestAspirationsAvailable.TunableFactory()
        kwargs['build_buy_reward_earned'] = TestBuildBuyRewardEarned.TunableFactory()
        kwargs['household_milestone_earned'] = TestHouseholdMilestoneEarned.TunableFactory()
        if allow_achievment:
            default = 'achievement'
            kwargs['achievement'] = AchievementEarnedFactory()
        return {'unlock_to_test':TunableVariant(description='\n            The unlocked aspiration, career, achievement, or milestone want to test for.\n            ', 
          default=default, **kwargs), 
         'participant':TunableEnumEntry(ParticipantType, ParticipantType.Actor, description='The subject of this test.')}

    def __init__(self, *, unlock_to_test, participant, **kwargs):
        (super().__init__)(**kwargs)
        self.unlock_to_test = unlock_to_test
        self.participant = participant

    def get_expected_args(self):
        return {'sims':self.participant, 
         'unlocked':event_testing.test_constants.FROM_EVENT_DATA}

    @cached_test
    def __call__(self, sims=None, unlocked=None):
        for sim in sims:
            return self.unlock_to_test(sim, self.tooltip, unlocked)


TunableUnlockedTest = TunableSingletonFactory.create_auto_factory(UnlockedTest)

class DayTimeTest(event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'description':'\n            Test to see if the current time falls within the tuned range\n            and/or is on a valid day.\n            ', 
     'days_available':OptionalTunable(scheduler_utils.TunableDayAvailability()), 
     'time_range':OptionalTunable(TunableTuple(description='\n            The time the test is valid.  If days_available is tuned and the\n            time range spans across two days with the second day tuned as\n            unavailable, the test will pass for that day until time range is\n            invalid.  Example: Time range 20:00 - 4:00, Monday is valid,\n            Tuesday is invalid.  Tuesday at 2:00 the test passes.  Tuesday at\n            4:01 the test fails.\n            ',
       begin_time=tunable_time.TunableTimeOfDay(default_hour=0),
       duration=tunable_time.TunableTimeOfDay(default_hour=1))), 
     'is_day':OptionalTunable(description="\n            If enabled, allows you to only pass the test if it's either day or\n            night, as per the Region's tuned sunrise and sunset times.\n            ",
       tunable=Tunable(description="\n                If checked, this test will only pass if all other criteria are\n                met and it's currently day time (between the sunrise and sunset\n                times tuned for the current region).\n                \n                If unchecked, this test will only pass if all other criteria are\n                met and it's currently night time (between the sunset and\n                sunrise times tune for the current region).\n                ",
       tunable_type=bool,
       default=True))}

    def __init__(self, days_available, time_range, is_day, **kwargs):
        (super().__init__)(**kwargs)
        self.days_available = days_available
        self.time_range = time_range
        self.is_day = is_day
        self.weekly_schedule = set()
        if days_available:
            if time_range is not None:
                for day in days_available:
                    if days_available[day]:
                        days_as_time_span = date_and_time.create_time_span(days=day)
                        start_time = self.time_range.begin_time + days_as_time_span
                        end_time = start_time + date_and_time.create_time_span(hours=(self.time_range.duration.hour()), minutes=(self.time_range.duration.minute()))
                        self.weekly_schedule.add((start_time, end_time))

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        if self.is_day is not None:
            if services.time_service().is_day_time() != self.is_day:
                return TestResult(False, 'Day and Time Test: Test wants it to be {} but it currently is not.', ('day' if self.is_day else 'night'), tooltip=(self.tooltip))
        current_time = services.time_service().sim_now
        if self.weekly_schedule:
            for times in self.weekly_schedule:
                if current_time.time_between_week_times(times[0], times[1]):
                    return TestResult.TRUE

            return TestResult(False, 'Day and Time Test: Current time and/or day is invalid.', tooltip=(self.tooltip))
        if self.days_available is not None:
            day = current_time.day()
            if self.days_available[day]:
                return TestResult.TRUE
            return TestResult(False, 'Day and Time Test: {} is not a valid day.', (tunable_time.Days(day)), tooltip=(self.tooltip))
        if self.time_range is not None:
            begin = self.time_range.begin_time
            end = begin + date_and_time.create_time_span(hours=(self.time_range.duration.hour()), minutes=(self.time_range.duration.minute()))
            if current_time.time_between_day_times(begin, end):
                return TestResult.TRUE
            return TestResult(False, 'Day and Time Test: Current time outside of tuned time range of {} - {}.', begin, end, tooltip=(self.tooltip))
        return TestResult.TRUE


TunableDayTimeTest = TunableSingletonFactory.create_auto_factory(DayTimeTest)

class SocialGroupTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = ()
    FACTORY_TUNABLES = {'description':"Require a Sim to be part of a specified social group type, and optionally if that group's size is within a tunable threshold.", 
     'subject':TunableEnumEntry(description='\n            The subject of this social group test.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'social_group_type':OptionalTunable(description='\n            If enabled, the participant must have this type of group available.\n            If this is disabled, any group will work.\n            ',
       tunable=TunableReference(description='\n                The required social group type.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SOCIAL_GROUP))),
       disabled_name='Any_Group'), 
     'threshold':OptionalTunable(description="\n            If enabled, tests the group size to ensure it's within a threshold.\n            ",
       tunable=TunableThreshold(description='\n                Optional social group size threshold test.\n                ')), 
     'check_if_entire_group_is_active':OptionalTunable(description='\n                If enabled then this test will check to see if the entire group\n                is active or not.\n                ',
       tunable=Tunable(description='\n                    If checked then the test will pass if the entire social\n                    group is active.  If unchecked then the test will pass\n                    if there are sims in the social group that are not active.\n                    ',
       tunable_type=bool,
       default=True)), 
     'additional_participant':OptionalTunable(description='\n                Test if this participant is or is not in the same social group\n                as Subject.\n                ',
       tunable=TunableTuple(participant=TunableEnumEntry(description='\n                        The participant that must also be or not be in the social group.\n                        ',
       tunable_type=ParticipantType,
       default=(ParticipantType.Actor)),
       in_group=Tunable(description="\n                        If enabled, this additional participant must be in the group.\n                        If disabled, this additional participant can't be in the group.\n                        ",
       tunable_type=bool,
       default=True)))}

    def get_expected_args(self):
        expected_args = {'test_targets': self.subject}
        if self.additional_participant is not None:
            expected_args['additional_targets'] = self.additional_participant.participant
        return expected_args

    @cached_test
    def __call__(self, test_targets=None, additional_targets=None):
        for target in test_targets:
            if target is None:
                continue
            if target.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS) is None:
                return TestResult(False, 'Social Group test failed: {} is not an instantiated sim.', target, tooltip=(self.tooltip))
            target = target.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            for group in target.get_groups_for_sim_gen():
                if not self.social_group_type is None:
                    if type(group) is self.social_group_type:
                        group_size = group.get_active_sim_count()
                        if self.threshold is not None:
                            if not self.threshold.compare(group_size):
                                return TestResult(False, 'Social Group test failed: group size not within threshold.', tooltip=(self.tooltip))
                        if self.check_if_entire_group_is_active is not None:
                            if len(group) == group_size:
                                return self.check_if_entire_group_is_active or TestResult(False, 'Social Group test failed: Social group is entirey active but we are checking for it not to be.',
                                  tooltip=(self.tooltip))
                            else:
                                if self.check_if_entire_group_is_active:
                                    return TestResult(False, 'Social Group test failed: Social group is not entirely active but we are checking for it to be.',
                                      tooltip=(self.tooltip))
                        if additional_targets is not None:
                            group_sim_ids = set(group.member_sim_ids_gen())
                            if self.additional_participant.in_group:
                                if any((sim.sim_id not in group_sim_ids for sim in additional_targets)):
                                    return TestResult(False, 'Social Group test failed: Additional participant not in group.',
                                      tooltip=(self.tooltip))
                            elif any((sim.sim_id in group_sim_ids for sim in additional_targets)):
                                return TestResult(False, 'Social Group test failed: Additional participant in group.',
                                  tooltip=(self.tooltip))
                    return TestResult.TRUE

        return TestResult(False, "Social Group test failed: subject not part of a '{}' social group.", (self.social_group_type), tooltip=(self.tooltip))


class InteractionRestoredFromLoadTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = ()
    FACTORY_TUNABLES = {'description':'Test whether an interaction was pushed from load or from normal gameplay.', 
     'from_load':Tunable(description='\n            If checked, this test will pass if the interaction was restored from\n            save load (restored interactions are pushed behind the loading screen).\n            If not checked, this test will only pass if the interaction was pushed\n            during normal gameplay.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'context': ParticipantType.InteractionContext}

    def __call__(self, context=None):
        if context is not None:
            if context.restored_from_load != self.from_load:
                return TestResult(False, 'InteractionRestoredFromLoadTest failed. We wanted interaction restored from load to be {}.', (self.from_load),
                  tooltip=(self.tooltip))
        return TestResult.TRUE


class SocialBoredomTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'threshold': TunableThreshold(description="\n            The test will fail if the affordance's boredom does not satisfy this\n            threshold.\n            ")}

    def get_expected_args(self):
        return {'affordance':ParticipantType.Affordance, 
         'social_group':ParticipantType.SocialGroup, 
         'subject':ParticipantType.Actor, 
         'target':ParticipantType.TargetSim}

    @cached_test
    def __call__(self, affordance=None, social_group=None, subject=None, target=None):
        subject = next(iter(subject), None)
        target = next(iter(target), None)
        social_group = next(iter(social_group), None)
        if subject is not None:
            subject = subject.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        else:
            if target is not None:
                target = target.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if subject is None or target is None:
                return TestResult(False, '{} does not target instantiated Sims', affordance)
            if social_group is None:
                return TestResult(False, 'There is no social group associated with {}', affordance)
            boredom = social_group.get_boredom(subject, target, affordance)
            return self.threshold.compare(boredom) or TestResult(False, 'Failed threshold test {} {}', boredom, (self.threshold), tooltip=(self.tooltip))
        return TestResult.TRUE


class CareerHighestLevelAchievedTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'career_blacklist':TunableSet(description='\n            A set of careers that will not be looked at.\n            ',
       tunable=TunableReference(description='\n                The career we will not check.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.CAREER)),
       pack_safe=True)), 
     'careers_to_check':OptionalTunable(description='\n            If enabled then we will only look at the careers listed in this.\n            set.  Otherwise will will look at all careers.\n            ',
       tunable=TunableSet(description='\n                A set of careers that will be looked at.\n                ',
       tunable=TunableReference(description='\n                    The career we will check.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.CAREER)),
       pack_safe=True))), 
     'passing_threshold':TunableThreshold(description='\n            Threshold for determining if a career is considered passing for\n            this test.\n            '), 
     'careers_to_find':TunableRange(description='\n            The number of careers that need to match the passing threshold for\n            this test to pass.\n            ',
       tunable_type=int,
       default=1,
       minimum=1)}

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self, subjects, targets=None, tooltip=None):
        highest_level = 0
        for subject in subjects:
            found_careers = 0
            if self.careers_to_check is not None:
                careers_to_check = self.careers_to_check
            else:
                careers_to_check = services.get_instance_manager(sims4.resources.Types.CAREER).types.values()
            for career in careers_to_check:
                if career in self.career_blacklist:
                    continue
                level_reached = subject.career_tracker.get_highest_level_reached(career.guid64)
                if level_reached > highest_level:
                    highest_level = level_reached
                if not self.passing_threshold.compare(level_reached):
                    continue
                found_careers += 1
                if found_careers >= self.careers_to_find:
                    break

            if found_careers < self.careers_to_find:
                if self.careers_to_find > 1:
                    current_value = found_careers
                    goal_value = self.careers_to_find
                else:
                    current_value = highest_level
                    goal_value = self.passing_threshold.value
                return TestResultNumeric(False, 'CareerHighestLevelAchievedTest: Not enough careers found passing the threshold.',
                  current_value=current_value,
                  goal_value=goal_value,
                  is_money=False,
                  tooltip=tooltip)

        return TestResult.TRUE

    def goal_value(self):
        if self.careers_to_find > 1:
            return self.careers_to_find
        return self.passing_threshold.value


class CareerAttendedFirstDay(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'career': TunablePackSafeReference(description='\n            The career to see if the Sim has gone to work for.\n            ',
                 manager=(services.get_instance_manager(sims4.resources.Types.CAREER)))}

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self, subjects, targets=None, tooltip=None):
        for subject in subjects:
            if self.career is None:
                return TestResult(False, 'Career is None, probably due to packsafeness.', subject, tooltip=tooltip)
                career = subject.careers.get(self.career.guid64, None)
                if career is None:
                    return TestResult(False, '{} does not have career {}', subject, (self.career), tooltip=tooltip)
                return career.has_attended_first_day or TestResult(False, '{} has not attended first day of {}', subject, (self.career), tooltip=tooltip)

        return TestResult.TRUE


class _TargetSpecificCareer(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'career': TunablePackSafeReference(description='\n            The career to test against.\n            ',
                 manager=(services.get_instance_manager(sims4.resources.Types.CAREER)))}

    def run_check(self, subject, check_to_run, tooltip):
        if self.career is None:
            return TestResult(False, 'Career is None, probably due to packsafeness.', subject, tooltip=tooltip)
        career = subject.careers.get(self.career.guid64, None)
        if career is None:
            return TestResult(False, '{} does not have career {}', subject, (self.career), tooltip=tooltip)
        return check_to_run(subject, career)


class _TargetAllCareers(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'all_must_pass': Tunable(description='\n            If checked, will fail if any career fails, even if others pass.\n            ',
                        tunable_type=bool,
                        default=False)}

    def run_check(self, subject, check_to_run, tooltip):
        if len(subject.careers) <= 0:
            return TestResult(False, 'Subject {} has no careers', subject, tooltip=tooltip)
        for career in subject.careers.values():
            result = check_to_run(subject, career)
            if not self.all_must_pass or result:
                if self.all_must_pass or result:
                    return result

        if self.all_must_pass:
            return TestResult.TRUE
        return TestResult(False, "None of subject {}'s careers passed test {}",
          subject,
          check_to_run,
          tooltip=tooltip)


class _TargetSomeCareers(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'careers':TunableSet(description='\n            The set of careers to test against.\n            ',
       tunable=TunablePackSafeReference(description='\n                The career to test against.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.CAREER))),
       minlength=1), 
     'all_must_pass':Tunable(description='\n            If checked, will fail if any career fails, even if others pass.\n            ',
       tunable_type=bool,
       default=False)}

    def run_check(self, subject, check_to_run, tooltip):
        if len(subject.careers) <= 0:
            return TestResult(False, 'Subject {} has no careers', subject, tooltip=tooltip)
        for career_def in self.careers:
            career = subject.careers.get(career_def.guid64, None)
            if career is None:
                if self.all_must_pass:
                    return TestResult(False, 'Subject {} was missing career {}',
                      subject,
                      career_def,
                      tooltip=tooltip)
                    continue
                result = check_to_run(subject, career)
                if not self.all_must_pass or result:
                    if self.all_must_pass or result:
                        return result

        if self.all_must_pass:
            return TestResult.TRUE
        return TestResult(False, "None of subject {}'s careers passed test {}",
          subject,
          check_to_run,
          tooltip=tooltip)


class _CareerSourceTunable(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'career_source': TunableVariant(description='\n            Which career(s) to test against.\n            ',
                        all_careers=_TargetAllCareers.TunableFactory(description='\n                Test against all careers on the subject.\n                '),
                        single_career=_TargetSpecificCareer.TunableFactory(description='\n                Test against a single, specific career.\n                '),
                        some_careers=_TargetSomeCareers.TunableFactory(description='\n                Test against a subset of careers.\n                '),
                        default='single_career')}

    def run_check(self, subject, check_to_run, tooltip):
        return self.career_source.run_check(subject, check_to_run, tooltip)


class CareerDaysWorked(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'career_source':_CareerSourceTunable.TunableFactory(description='\n            Which career(s) to test against.\n            '), 
     'threshold':TunableThreshold(description='\n            Threshold test for days worked.\n            '), 
     'active_only':Tunable(description='\n            If checked, only workdays that the player has actively played will\n            count.\n            ',
       tunable_type=bool,
       default=True)}

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self, subjects, tooltip=None):
        for subject in subjects:
            result = self.career_source.run_check(subject, self.test_days_worked_for_career, tooltip)
            if not result:
                return result

        return TestResult.TRUE

    def get_days_worked(self, career):
        if self.active_only:
            return career.active_days_worked_statistic.get_value()
        return career.days_worked_statistic.get_value()

    def test_days_worked_for_career(self, subject, career, tooltip=None):
        if not self.threshold.compare(self.get_days_worked(career)):
            return TestResult(False, 'Threshold not met. Sim: {}, Career: {}, Threshold: {}',
              subject,
              career,
              (self.threshold),
              tooltip=tooltip)
        return TestResult.TRUE


class CareerStoryProgressionModificationType(enum.Int):
    JOIN = 1
    QUIT = 2
    RETIRE = 3


class HasCareerTestFactory(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'has_career':Tunable(description='\n            If true all subjects must have a career for the test to pass. If False then none of the subjects \n            can have a career for the test to pass.\n            ',
       tunable_type=bool,
       default=True), 
     'story_progression_requirement':OptionalTunable(description='\n            If Has Career is tuned to true, the subjects must have a career that allows for the specified modification\n            by the story progression system.  If Has Career is tuned to false, this field is ignored.\n            ',
       tunable=TunableEnumEntry(tunable_type=CareerStoryProgressionModificationType,
       default=(CareerStoryProgressionModificationType.JOIN)))}

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self, subjects, targets=None, tooltip=None):
        for subject in subjects:
            if self.has_career:
                if not subject.careers:
                    if not subject.has_custom_career:
                        return TestResult(False, '{0} does not currently have a career.', subject,
                          tooltip=tooltip)
                if subject.careers:
                    visible_career_found = False
                    story_progression_requirements_met = self.story_progression_requirement is None
                    for career in subject.careers.values():
                        if career.is_visible_career:
                            visible_career_found = True
                        if self._check_story_progression_requirement(subject, career):
                            story_progression_requirements_met = True

                    if not visible_career_found:
                        return TestResult(False, '{0} does not currently have a visible career.', subject,
                          tooltip=tooltip)
                        if not story_progression_requirements_met:
                            return TestResult(False, '{0} does not currently have a career that supports {1} modifications by the story progression system.', subject,
                              (self.story_progression_requirement), tooltip=tooltip)
                    else:
                        if subject.has_custom_career:
                            return TestResult(False, ('{0} currently has a career'.format(subject)), tooltip=tooltip)
                        if subject.careers:
                            for career in subject.careers.values():
                                if career.is_visible_career:
                                    return TestResult(False, ('{0} currently has a career'.format(subject)), tooltip=tooltip)

        return TestResult.TRUE

    def _check_story_progression_requirement(self, subject, career):
        if self.story_progression_requirement is None:
            return True
        else:
            resolver = SingleSimResolver(subject)
            multipliers = None
            if self.story_progression_requirement == CareerStoryProgressionModificationType.JOIN:
                multipliers = career.career_story_progression.joining
            else:
                if self.story_progression_requirement == CareerStoryProgressionModificationType.QUIT:
                    multipliers = career.career_story_progression.quitting
                else:
                    if self.story_progression_requirement == CareerStoryProgressionModificationType.RETIRE:
                        multipliers = career.career_story_progression.retiring
        if multipliers is not None:
            return multipliers.get_multiplier(resolver)
        return False


class QuittableCareerTestFactory(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'has_quittable_career': Tunable(description='\n            If True then all of the subjects must have a quittable career in \n            order for the test to pass. If False then none of the subjects \n            can have a quittable career in order to pass.\n            ',
                               tunable_type=bool,
                               default=True)}

    def get_expected_args(self):
        return {}

    @caches.cached
    def __call__(self, subjects, targets=None, tooltip=None):
        for subject in subjects:
            if self.has_quittable_career:
                if not any((c.can_quit for c in subject.careers.values())):
                    return TestResult(False, '{0} does not have any quittable careers', subject,
                      tooltip=tooltip)
                elif any((c.can_quit for c in subject.careers.values())):
                    return TestResult(False, '{0} has at least one career that is quittable', subject,
                      tooltip=tooltip)

        return TestResult.TRUE

    def goal_value(self):
        return 1


class SpecifiedCareerMixin:
    FACTORY_TUNABLES = {'fallback_to_picker': Tunable(description='\n            If the tuned career is not set, should we expect the career to\n            be passed in via PickedItemIds?\n            ',
                             tunable_type=bool,
                             default=True)}

    @property
    def tuned_career(self):
        raise NotImplementedError

    def get_expected_args(self):
        if self.fallback_to_picker:
            if self.tuned_career is None:
                return {'career_pick': ParticipantType.PickedItemId}
        return {}

    def do_test(self, subjects, career_id, tooltip):
        raise NotImplementedError

    @caches.cached
    def __call__(self, subjects, career_pick=None, targets=None, tooltip=None):
        career_id = None
        if self.tuned_career is None:
            if career_pick:
                career_id = career_pick[0]
        else:
            career_id = self.career.guid64
        return self.do_test(subjects, career_id, tooltip)

    def get_target_id(self, subjects, career_pick=None, targets=None, tooltip=None, id_type=None):
        if not career_pick:
            return
        if id_type == TargetIdTypes.DEFAULT or id_type == TargetIdTypes.DEFINITION:
            return career_pick[0]
        if id_type == TargetIdTypes.INSTANCE:
            for subject in subjects:
                this_career = subject.careers.get(career_pick[0])
                if this_career is not None:
                    return this_career.id

        logger.error('Unique target ID type: {} is not supported for test: {}', id_type, self)

    def goal_value(self):
        return 1


class CareerTimeUntilWorkTestFactory(SpecifiedCareerMixin, HasTunableSingletonFactory, AutoFactoryInit):
    UNIQUE_TARGET_TRACKING_AVAILABLE = True
    FACTORY_TUNABLES = {'career':TunableReference(description='\n            The career to test the next start time of.\n           \n            If None, will expect career passed in via PickedItemIds (i.e. via picker).\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CAREER),
       allow_none=True), 
     'hours_till_work':TunableInterval(description='\n            Threshold test for how long \'till the "next" start time.  It will\n            test up to one hour past the start time, at which point it will test\n            against the next start time.\n            ',
       tunable_type=float,
       default_lower=-1,
       default_upper=23,
       minimum=-23,
       maximum=168), 
     'check_all_careers':Tunable(description='\n            If checked then we will check all careers rather than just the one defined\n            in the career tunable.  The test will fail if any career fails.\n            ',
       tunable_type=bool,
       default=False)}

    @property
    def tuned_career(self):
        return self.career

    def do_test--- This code section failed: ---

 L.4451       0_2  SETUP_LOOP          292  'to 292'
                4  LOAD_FAST                'subjects'
                6  GET_ITER         
             8_10  FOR_ITER            290  'to 290'
               12  STORE_FAST               'subject'

 L.4452        14  LOAD_FAST                'self'
               16  LOAD_ATTR                check_all_careers
               18  POP_JUMP_IF_FALSE    48  'to 48'

 L.4453        20  LOAD_FAST                'subject'
               22  LOAD_ATTR                careers
               24  LOAD_METHOD              values
               26  CALL_METHOD_0         0  '0 positional arguments'
               28  STORE_FAST               'careers_to_check'

 L.4454        30  LOAD_FAST                'careers_to_check'
               32  POP_JUMP_IF_TRUE     94  'to 94'

 L.4455        34  LOAD_GLOBAL              TestResult
               36  LOAD_CONST               False
               38  LOAD_STR                 '{} does not have any career to check if there is time to work.'
               40  LOAD_FAST                'subject'
               42  CALL_FUNCTION_3       3  '3 positional arguments'
               44  RETURN_VALUE     
               46  JUMP_FORWARD         94  'to 94'
             48_0  COME_FROM            18  '18'

 L.4457        48  LOAD_FAST                'subject'
               50  LOAD_ATTR                careers
               52  LOAD_METHOD              get
               54  LOAD_FAST                'career_id'
               56  CALL_METHOD_1         1  '1 positional argument'
               58  STORE_FAST               'this_career'

 L.4458        60  LOAD_FAST                'this_career'
               62  LOAD_CONST               None
               64  COMPARE_OP               is
               66  POP_JUMP_IF_FALSE    88  'to 88'

 L.4459        68  LOAD_GLOBAL              TestResult
               70  LOAD_CONST               False
               72  LOAD_STR                 '{0} does not have the career needed for this interaction: {1}:{2}'
               74  LOAD_FAST                'subject'
               76  LOAD_FAST                'self'
               78  LOAD_ATTR                career
               80  LOAD_FAST                'self'
               82  LOAD_ATTR                hours_till_work
               84  CALL_FUNCTION_5       5  '5 positional arguments'
               86  RETURN_VALUE     
             88_0  COME_FROM            66  '66'

 L.4460        88  LOAD_FAST                'this_career'
               90  BUILD_TUPLE_1         1 
               92  STORE_FAST               'careers_to_check'
             94_0  COME_FROM            46  '46'
             94_1  COME_FROM            32  '32'

 L.4461        94  SETUP_LOOP          288  'to 288'
               96  LOAD_FAST                'careers_to_check'
               98  GET_ITER         
              100  FOR_ITER            286  'to 286'
              102  STORE_FAST               'career'

 L.4462       104  LOAD_CONST               None
              106  STORE_FAST               'hours'

 L.4463       108  LOAD_FAST                'career'
              110  LOAD_ATTR                is_work_time
              112  POP_JUMP_IF_FALSE   154  'to 154'

 L.4464       114  LOAD_FAST                'career'
              116  LOAD_ATTR                start_time
              118  LOAD_GLOBAL              services
              120  LOAD_METHOD              time_service
              122  CALL_METHOD_0         0  '0 positional arguments'
              124  LOAD_ATTR                sim_now
              126  BINARY_SUBTRACT  
              128  STORE_FAST               'elapsed'

 L.4465       130  LOAD_FAST                'elapsed'
              132  LOAD_METHOD              in_hours
              134  CALL_METHOD_0         0  '0 positional arguments'
              136  STORE_FAST               'hours'

 L.4466       138  LOAD_FAST                'hours'
              140  LOAD_FAST                'self'
              142  LOAD_ATTR                hours_till_work
              144  LOAD_ATTR                lower_bound
              146  COMPARE_OP               <
              148  POP_JUMP_IF_FALSE   154  'to 154'

 L.4467       150  LOAD_CONST               None
              152  STORE_FAST               'hours'
            154_0  COME_FROM           148  '148'
            154_1  COME_FROM           112  '112'

 L.4468       154  LOAD_FAST                'hours'
              156  LOAD_CONST               None
              158  COMPARE_OP               is
              160  POP_JUMP_IF_FALSE   220  'to 220'

 L.4469       162  LOAD_FAST                'career'
              164  LOAD_METHOD              get_next_work_time
              166  CALL_METHOD_0         0  '0 positional arguments'
              168  UNPACK_SEQUENCE_3     3 
              170  STORE_FAST               'time_span'
              172  STORE_FAST               '_'
              174  STORE_FAST               '_'

 L.4470       176  LOAD_FAST                'time_span'
              178  LOAD_CONST               None
              180  COMPARE_OP               is
              182  POP_JUMP_IF_FALSE   212  'to 212'

 L.4471       184  LOAD_GLOBAL              TestResultNumeric
              186  LOAD_CONST               False

 L.4472       188  LOAD_STR                 '{0} does not currently have any hours scheduled in career {1}'

 L.4473       190  LOAD_FAST                'subject'

 L.4474       192  LOAD_FAST                'career'

 L.4475       194  LOAD_CONST               -1

 L.4476       196  LOAD_FAST                'self'
              198  LOAD_ATTR                hours_till_work
              200  LOAD_ATTR                lower_bound

 L.4477       202  LOAD_CONST               False

 L.4478       204  LOAD_FAST                'tooltip'
              206  LOAD_CONST               ('current_value', 'goal_value', 'is_money', 'tooltip')
              208  CALL_FUNCTION_KW_8     8  '8 total positional and keyword args'
              210  RETURN_VALUE     
            212_0  COME_FROM           182  '182'

 L.4479       212  LOAD_FAST                'time_span'
              214  LOAD_METHOD              in_hours
              216  CALL_METHOD_0         0  '0 positional arguments'
              218  STORE_FAST               'hours'
            220_0  COME_FROM           160  '160'

 L.4480       220  LOAD_FAST                'self'
              222  LOAD_ATTR                hours_till_work
              224  LOAD_ATTR                lower_bound
              226  LOAD_FAST                'hours'
              228  DUP_TOP          
              230  ROT_THREE        
              232  COMPARE_OP               <=
              234  POP_JUMP_IF_FALSE   248  'to 248'
              236  LOAD_FAST                'self'
              238  LOAD_ATTR                hours_till_work
              240  LOAD_ATTR                upper_bound
              242  COMPARE_OP               <=
              244  POP_JUMP_IF_FALSE   254  'to 254'
              246  JUMP_BACK           100  'to 100'
            248_0  COME_FROM           234  '234'
              248  POP_TOP          
              250  JUMP_FORWARD        254  'to 254'

 L.4481       252  CONTINUE            100  'to 100'
            254_0  COME_FROM           250  '250'
            254_1  COME_FROM           244  '244'

 L.4482       254  LOAD_GLOBAL              TestResultNumeric
              256  LOAD_CONST               False
              258  LOAD_STR                 '{0} does not currently have the correct hours till work in career ({1},{2}) required to pass this test'

 L.4483       260  LOAD_FAST                'subject'
              262  LOAD_FAST                'career'
              264  LOAD_FAST                'self'
              266  LOAD_ATTR                hours_till_work

 L.4484       268  LOAD_FAST                'hours'

 L.4485       270  LOAD_FAST                'self'
              272  LOAD_ATTR                hours_till_work
              274  LOAD_ATTR                lower_bound

 L.4486       276  LOAD_CONST               False

 L.4487       278  LOAD_FAST                'tooltip'
              280  LOAD_CONST               ('current_value', 'goal_value', 'is_money', 'tooltip')
              282  CALL_FUNCTION_KW_9     9  '9 total positional and keyword args'
              284  RETURN_VALUE     
              286  POP_BLOCK        
            288_0  COME_FROM_LOOP       94  '94'
              288  JUMP_BACK             8  'to 8'
              290  POP_BLOCK        
            292_0  COME_FROM_LOOP        0  '0'

 L.4489       292  LOAD_GLOBAL              TestResult
              294  LOAD_ATTR                TRUE
              296  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `POP_TOP' instruction at offset 248


class CareerPTOAmountTestFactory(SpecifiedCareerMixin, HasTunableSingletonFactory, AutoFactoryInit):
    UNIQUE_TARGET_TRACKING_AVAILABLE = True
    FACTORY_TUNABLES = {'career':TunableReference(description='\n            The career to test for how much PTO the sim has.\n          \n            If None, will expect career passed in via PickedItemIds (i.e. via picker).\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CAREER),
       allow_none=True), 
     'required_pto_available':TunableThreshold(description='\n            Threshold test for how much PTO is required\n            ')}

    @property
    def tuned_career(self):
        return self.career

    def do_test(self, subjects, career_id, tooltip):
        for subject in subjects:
            this_career = subject.careers.get(career_id)
            if this_career is None:
                return TestResult(False, '{0} does not have the career needed for this interaction: {1}:{2}', subject, self.career, self.required_pto_available)
            pto_available = this_career.pto
            if self.required_pto_available.compare(pto_available):
                continue
            return TestResultNumeric(False, '{0} does not currently have the correct amount of PTO in career ({1},{2}) required to pass this test', subject,
              (self.career), (self.required_pto_available), current_value=pto_available,
              goal_value=(self.required_pto_available.value),
              is_money=False,
              tooltip=tooltip)

        return TestResult.TRUE


class CareerHasIconOverrideTest(SpecifiedCareerMixin, HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'career': TunableReference(description='\n            The career to check whether it has an icon override on the subject. \n            ',
                 manager=(services.get_instance_manager(sims4.resources.Types.CAREER)),
                 pack_safe=True)}

    @property
    def tuned_career(self):
        return self.career

    def do_test(self, subjects, career_id, tooltip):
        for subject in subjects:
            this_career = subject.careers.get(career_id)
            if this_career is None:
                return TestResult(False, '{0} does not have the career needed for icon override: {1}', subject, self.career)
                icon_override = this_career.icon_override
                if icon_override is not None:
                    return TestResult.TRUE

        return TestResult(False, 'No career icon override is selected for: {}', this_career, tooltip=tooltip)


class CareerHasAssignmentTestFactory(SpecifiedCareerMixin, HasTunableSingletonFactory, AutoFactoryInit):
    UNIQUE_TARGET_TRACKING_AVAILABLE = True
    FACTORY_TUNABLES = {'career': TunableReference(description='\n            The career to test for having an available assignment.\n           \n            If None, will expect career passed in via PickedItemIds (i.e. via picker).\n            ',
                 manager=(services.get_instance_manager(sims4.resources.Types.CAREER)),
                 allow_none=True)}

    @property
    def tuned_career(self):
        return self.career

    def do_test(self, subjects, career_id, tooltip):
        for subject in subjects:
            this_career = subject.careers.get(career_id)
            if this_career is None:
                return TestResult(False, '{0} does not have the career needed for this interaction: {1}', subject, self.career)
                return this_career.get_assignments_to_offer(just_accepted=False) or TestResult(False, '{0} does not currently have an available assignment in career {1}', subject,
                  (self.career), tooltip=tooltip)

        return TestResult.TRUE


class CareerAvailabilityTestFactory(HasTunableSingletonFactory, AutoFactoryInit):
    UNIQUE_TARGET_TRACKING_AVAILABLE = False
    FACTORY_TUNABLES = {'careers_to_consider': TunableWhiteBlackList(description='\n            The set of careers to consider and the threshold for passing.\n            ',
                              tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.CAREER)),
                              pack_safe=True))}

    def get_expected_args(self):
        return {}

    def __call__(self, subjects, tooltip=None):
        for career in services.get_career_service().get_career_list():
            if not self.careers_to_consider.test_item(career):
                continue
            for subject in subjects:
                sim_info = subject.sim_info
                if subject.career_tracker.has_career_by_uid(career.guid64) or career.is_valid_career(sim_info=sim_info, from_join=True):
                    return TestResult.TRUE

        return TestResult(False, 'No career in consideration is available for any subject', tooltip=tooltip)


class CareerTimeOffTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self, subjects, tooltip=None):
        for sim_info in subjects:
            careers = sim_info.careers.values()
            if not careers:
                return TestResult(False, '{} does not have any careers', sim_info, tooltip=tooltip)
                if all((c.requested_day_off or c.taking_day_off for c in careers)):
                    return TestResult(False, '{} is taking time off for all careers', sim_info, tooltip=tooltip)

        return TestResult.TRUE


class CareerReferenceTestFactory(HasTunableSingletonFactory, AutoFactoryInit):
    UNIQUE_TARGET_TRACKING_AVAILABLE = True
    FACTORY_TUNABLES = {'career':OptionalTunable(description='\n            The career to test for on the Sim. When set by itself it will pass\n            if the subject simply has this career. When set with user level it\n            will only pass if the subjects user level passes the threshold\n            test.\n            ',
       tunable=TunablePackSafeReference(manager=(services.get_instance_manager(sims4.resources.Types.CAREER))),
       disabled_value=DEFAULT,
       disabled_name='all_careers',
       enabled_name='specific_career'), 
     'career_list':TunableSet(description="\n            Should be another option in 'career', as if both are set, will be\n            a validation error. Instead of checking if just one career is present,\n            this will check if any one of the given careers are present.\n            ",
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.CAREER)),
       pack_safe=True)), 
     'blacklist':TunableSet(description='\n            Should be called "Ignore List".  Set of careers that will be ignored\n            on the Sim.  If the Sim only had these careers, it would be like having no careers.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.CAREER)),
       pack_safe=True)), 
     'user_level':OptionalTunable(TunableInterval(description='\n            Threshold test for the current user value of a career. If user_level\n            is set without career then it will pass if any of their careers \n            pass the threshold test. If set along with career then it will only\n            pass if the specified career passes the threshold test for user \n            level. \n            \n            The min and max for the user level are inclusive. So the Sim\n            can have any career level that meets the following equation and it\n            will pass.\n            \n            min <= current career level <= max.\n            ',
       tunable_type=int,
       default_lower=1,
       default_upper=11,
       minimum=0,
       maximum=11)), 
     'allow_invisible_careers':Tunable(description='\n            If checked, this test will also allow non-visible careers (such as\n            Odd Jobs) to tested against.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {}

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, value):
        if value.career is not None:
            if len(value.career_list) > 0:
                logger.error("Career Test in {} cannot have both 'career' and 'career_list' set.", source, owner='mjuskelis')

    def _should_test_career(self, career):
        if type(career) in self.blacklist:
            return False
        if self.allow_invisible_careers:
            return True
        return career.is_visible_career

    def _is_career_valid_list(self, career):
        return type(career) in self.career_list

    def _is_career_valid_singular(self, career):
        return self.career is DEFAULT or isinstance(career, self.career)

    def _is_valid_user_level(self, career):
        if not self.user_level:
            return True
        return self.user_level.lower_bound <= career.user_level <= self.user_level.upper_bound

    @caches.cached
    def __call__(self, subjects, tooltip=None, **kwargs):
        if self.career_list is not None and len(self.career_list) > 0:
            career_test_variant = self._is_career_valid_list
        else:
            if self.career is not None:
                career_test_variant = self._is_career_valid_singular
            else:
                return TestResult(False, '{0} are testing for non-existent careers, probably in a different pack.', subjects)
        for subject in subjects:
            subject_careers = subject.careers.values()
            if not subject_careers:
                return TestResult(False,
                  '{0} does not currently have any careers and a career is needed for this test: {1}/{2}:{3}.',
                  subject,
                  (self.career),
                  (self.career_list),
                  (self.user_level),
                  tooltip=tooltip)
                current_user_level = 0
                for career in subject_careers:
                    if self._should_test_career(career):
                        if career_test_variant(career):
                            if self._is_valid_user_level(career):
                                break
                        current_user_level = career.user_level
                else:
                    if current_user_level:
                        return TestResultNumeric(False,
                          '{0} does not currently have the correct career/user level ({1},{2}) required to pass this test.',
                          subject,
                          (self.career),
                          (self.user_level),
                          current_value=current_user_level,
                          goal_value=(self.user_level.lower_bound),
                          is_money=False,
                          tooltip=tooltip)
                    return TestResult(False,
                      '{0} does not currently have the correct career/user level ({1},{2}) required to pass this test.',
                      subject,
                      (self.career),
                      (self.user_level),
                      tooltip=tooltip)

        return TestResult.TRUE

    def get_target_id(self, subjects, career=None, targets=None, tooltip=None, id_type=None):
        if career is None:
            return
        if id_type == TargetIdTypes.DEFAULT or id_type == TargetIdTypes.DEFINITION:
            return career.guid64
        if id_type == TargetIdTypes.INSTANCE:
            return career.id
        logger.error('Unique target ID type: {} is not supported for test: {}', id_type, self)

    def goal_value(self):
        if self.user_level:
            return self.user_level.lower_bound
        return 1


class CareerTrackTestFactory(HasTunableSingletonFactory, AutoFactoryInit):
    UNIQUE_TARGET_TRACKING_AVAILABLE = False
    FACTORY_TUNABLES = {'career_track':TunablePackSafeReference(description='\n            A reference to the career track that each subject must have in at\n            least one career in order for this test to pass.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CAREER_TRACK)), 
     'user_level':OptionalTunable(TunableInterval(description='\n           Interval test for the current user value of a career. Career track\n           must also be specified for this check to work properly.\n           ',
       tunable_type=int,
       default_lower=1,
       default_upper=10,
       minimum=0,
       maximum=10))}

    def get_expected_args(self):
        return {}

    @caches.cached
    def __call__(self, subjects, targets=None, tooltip=None):
        if self.career_track is None:
            return TestResult(False, '{0} is testing for a non-existant career track, probably in a different pack.', self)
        for subject in subjects:
            for career in subject.careers.values():
                if career.current_track_tuning == self.career_track:
                    if self.user_level:
                        if career.user_level >= self.user_level.lower_bound:
                            if not career.user_level <= self.user_level.upper_bound:
                                continue
                    break
            else:
                return TestResult(False, '{0} is not currently in career track {1} in any of their current careers', subject,
                  (self.career_track), tooltip=tooltip)

        return TestResult.TRUE

    def goal_value(self):
        return 1


class CareerLevelTestFactory(HasTunableSingletonFactory, AutoFactoryInit):
    UNIQUE_TARGET_TRACKING_AVAILABLE = False
    FACTORY_TUNABLES = {'career_level': TunableReference(description='\n            A reference to career level tuning that each subject must have in \n            at least one career in order for this test to pass.\n            ',
                       manager=(services.get_instance_manager(sims4.resources.Types.CAREER_LEVEL)),
                       needs_tuning=True)}

    def get_expected_args(self):
        return {}

    @caches.cached
    def __call__(self, subjects, targets=None, tooltip=None):
        for subject in subjects:
            for career in subject.careers.values():
                if career.current_level_tuning == self.career_level:
                    break
            else:
                return TestResult(False, '{0} is not currently in career level {1} in any of their current careers', subject,
                  (self.career_level), tooltip=tooltip)

        return TestResult.TRUE

    def goal_value(self):
        return 1


class SameCareerAtUserLevelTestFactory(HasTunableSingletonFactory, AutoFactoryInit):
    UNIQUE_TARGET_TRACKING_AVAILABLE = False
    FACTORY_TUNABLES = {'user_level': TunableThreshold(description='User level to test for.')}

    def get_expected_args(self):
        return {}

    @caches.cached
    def __call__(self, subjects, targets=None, tooltip=None):
        common_careers = None
        for subject in subjects:
            subject_careers = set(((type(career), career.user_level) for career in subject.careers.values()))
            if common_careers is None:
                common_careers = subject_careers
            else:
                common_careers &= subject_careers

        if not common_careers:
            return TestResult(False, '{} do not have any common careers at the same user level.', subjects,
              tooltip=tooltip)
        return TestResult.TRUE

    def goal_value(self):
        return 1


class IsRetiredTestFactory(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'career': TunableReference(description='\n            The retired career to test for on the subjects. If left unset, the\n            test will pass if the Sim is retired from any career.\n            ',
                 manager=(services.get_instance_manager(sims4.resources.Types.CAREER)))}

    def get_expected_args(self):
        return {}

    @caches.cached
    def __call__(self, subjects, targets=None, tooltip=None):
        for subject in subjects:
            retired_career_uid = subject.career_tracker.retired_career_uid
            if not retired_career_uid:
                return TestResult(False, '{0} is not retired from a career.', subject,
                  tooltip=tooltip)
                if self.career is not None and self.career.guid64 != retired_career_uid:
                    return TestResult(False, '{0} is retired from {}, which is not {}', subject,
                      (self.career), tooltip=tooltip)

        return TestResult.TRUE

    def goal_value(self):
        return 1


class HasCareerOutfit(HasTunableSingletonFactory, AutoFactoryInit):

    def get_expected_args(self):
        return {}

    @caches.cached
    def __call__(self, subjects, targets=None, tooltip=None):
        for subject in subjects:
            if not subject.career_tracker.has_career_outfit():
                return TestResult(False, '{} does not have a career outfit', subject, tooltip=tooltip)

        return TestResult.TRUE

    def goal_value(self):
        return 1


class TunableCommonCareerTestsVariant(TunableVariant):
    UNIQUE_TARGET_TRACKING_AVAILABLE = False

    def __init__(self, **kwargs):
        super().__init__(career_reference=(CareerReferenceTestFactory.TunableFactory()), career_track=(CareerTrackTestFactory.TunableFactory()),
          career_level=(CareerLevelTestFactory.TunableFactory()),
          same_career_at_user_level=(SameCareerAtUserLevelTestFactory.TunableFactory()),
          default='career_reference')


class CareerCommonTestFactory(HasTunableSingletonFactory, AutoFactoryInit):
    UNIQUE_TARGET_TRACKING_AVAILABLE = False
    FACTORY_TUNABLES = {'targets':TunableEnumFlags(description='\n            tuning for the targets to check for the same common career on.\n            ',
       enum_type=ParticipantType,
       default=ParticipantType.Listeners), 
     'test_type':TunableCommonCareerTestsVariant()}

    def get_expected_args(self):
        return {'targets': self.targets}

    @caches.cached
    def __call__(self, subjects, targets=(), tooltip=None):
        all_sims = tuple(set(subjects) | set(targets))
        if not self.test_type(all_sims, tooltip=tooltip):
            return TestResult(False, '{} do not have any common careers', subjects, tooltip=tooltip)
        return TestResult.TRUE

    def goal_value(self):
        return 1


class CareerIsElectiveCourseTest(SpecifiedCareerMixin, HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'career': TunablePackSafeReference(description='\n            The career slot to test for associated elective course data on the \n            subjects. \n            ',
                 manager=(services.get_instance_manager(sims4.resources.Types.CAREER)),
                 class_restrictions='UniversityCourseCareerSlot')}

    @property
    def tuned_career(self):
        return self.career

    def do_test(self, subjects, career_id, tooltip):
        for subject in subjects:
            this_career = subject.careers.get(career_id)
            if this_career is None:
                return TestResult(False, '{0} does not have the career needed for this interaction: {1}', subject, self.career)
                if self.career is None:
                    return TestResult(False, "{0}'s career {1} is None, probably due to packsafeness.", subject, (self.career), tooltip=tooltip)
                degree_tracker = subject.degree_tracker
                if degree_tracker is None:
                    return TestResult(False, '{} has no degree tracker.', subject, tooltip=tooltip)
                course_data = degree_tracker.get_course_data(self.career.guid64)
                if course_data is None:
                    return TestResult(False, '{0} has course data associated with the specified career {1}.', subject, (self.career), tooltip=tooltip)
                return course_data.is_elective or TestResult(False, "{0}'s career {1} is not an elective.", subject, (self.career), tooltip=tooltip)

        return TestResult.TRUE


class CareerEventTest(HasTunableSingletonFactory, AutoFactoryInit):
    UNIQUE_TARGET_TRACKING_AVAILABLE = False
    FACTORY_TUNABLES = {'career_event': OptionalTunable(description='\n            The career event to test for.\n            ',
                       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.CAREER_EVENT))),
                       disabled_name='any',
                       enabled_name='specific_CareerEvent')}

    def get_expected_args(self):
        return {}

    def __call__(self, subjects, tooltip=None):
        for subject in subjects:
            sim_info = subject.sim_info
            for career in sim_info.career_tracker:
                career_event_manager = career.career_event_manager
                if career_event_manager is None:
                    continue
                if self.career_event is None or career_event_manager.is_top_career_event(self.career_event):
                    return TestResult.TRUE

        return TestResult(False, 'Not in specified career event.', tooltip=tooltip)


class TunableCareerTestVariant(TunableVariant):

    def __init__(self, **kwargs):
        tunables = {'attended_first_day':CareerAttendedFirstDay.TunableFactory(), 
         'days_worked':CareerDaysWorked.TunableFactory(), 
         'has_career':HasCareerTestFactory.TunableFactory(), 
         'has_quittable_career':QuittableCareerTestFactory.TunableFactory(), 
         'has_available_assignment':CareerHasAssignmentTestFactory.TunableFactory(), 
         'can_join_career':CareerAvailabilityTestFactory.TunableFactory(), 
         'career_reference':CareerReferenceTestFactory.TunableFactory(), 
         'career_track':CareerTrackTestFactory.TunableFactory(), 
         'career_level':CareerLevelTestFactory.TunableFactory(), 
         'common_career':CareerCommonTestFactory.TunableFactory(), 
         'is_retired':IsRetiredTestFactory.TunableFactory(), 
         'has_career_outfit':HasCareerOutfit.TunableFactory(), 
         'time_until_work':CareerTimeUntilWorkTestFactory.TunableFactory(), 
         'pto_amount':CareerPTOAmountTestFactory.TunableFactory(), 
         'time_off':CareerTimeOffTest.TunableFactory(), 
         'highest_level_achieved':CareerHighestLevelAchievedTest.TunableFactory(), 
         'is_elective_course':CareerIsElectiveCourseTest.TunableFactory(), 
         'in_career_event':CareerEventTest.TunableFactory(), 
         'has_career_icon_override':CareerHasIconOverrideTest.TunableFactory(), 
         'default':'career_reference'}
        kwargs.update(tunables)
        (super().__init__)(**kwargs)


class TunableCareerTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = (
     TestEvent.CareerEvent,)

    @flexproperty
    def UNIQUE_TARGET_TRACKING_AVAILABLE(cls, inst):
        if inst != None:
            return inst.test_type.UNIQUE_TARGET_TRACKING_AVAILABLE
        return False

    FACTORY_TUNABLES = {'subjects':TunableEnumEntry(description='\n            The participant to run the career test on.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'test_type':TunableCareerTestVariant(), 
     'negate':Tunable(description='If this is true then it will negate \n        the result of the test type. For instance if this is true and the test\n        would return true for whether or not a sim has a particular career\n        False will be returned instead.\n        ',
       tunable_type=bool,
       default=False)}
    __slots__ = ('test_type', 'subjects', 'negate')

    def get_expected_args(self):
        expected_args = {'subjects': self.subjects}
        if self.test_type:
            test_args = self.test_type.get_expected_args()
            expected_args.update(test_args)
        return expected_args

    @cached_test
    def __call__(self, *args, **kwargs):
        result = (self.test_type)(args, tooltip=self.tooltip, **kwargs)
        if self.negate:
            if not result:
                return TestResult.TRUE
            return TestResult(False, 'Career test passed but the result was negated.', tooltip=(self.tooltip))
        return result

    def get_target_id(self, *args, **kwargs):
        if self.test_type:
            if self.test_type.UNIQUE_TARGET_TRACKING_AVAILABLE:
                return (self.test_type.get_target_id)(args, tooltip=self.tooltip, **kwargs)
        return (super().get_target_id)(*args, **kwargs)

    def goal_value(self):
        return self.test_type.goal_value()


class _CareerEventOriginTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    USES_EVENT_DATA = True
    FACTORY_TUNABLES = {'event_origin_careers': TunableWhiteBlackList(description='\n            The goal test will only pass for career events originating from careers validated against the \n            whitelist/blacklist.\n            ',
                               tunable=TunableReference(description='\n                Allowed and Disallowed Careers.\n                ',
                               manager=(services.get_instance_manager(sims4.resources.Types.CAREER)),
                               pack_safe=True))}

    def get_expected_args(self):
        return {'career': event_testing.test_constants.FROM_EVENT_DATA}

    @cached_test
    def __call__(self, career=None):
        if career is None:
            return TestResult(False, 'No career was passed in to the test.', tooltip=(self.tooltip))
        else:
            return self.event_origin_careers.test_item(type(career)) or TestResult(False, 'Career {} does not pass the White/Black list', career, tooltip=(self.tooltip))
        return TestResult.TRUE


class CareerPromotedTest(_CareerEventOriginTest):
    test_events = (
     TestEvent.CareerPromoted,)


class CareerChangedTest(_CareerEventOriginTest):
    test_events = (
     TestEvent.CareerEvent,)


class GreetedTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = ()
    FACTORY_TUNABLES = {'test_for_greeted_status': Tunable(description="\n                If checked then this test will pass if the player is considered\n                greeted on the current lot.  If unchecked the test will pass\n                If the player is considered ungreeted on the current lot.\n                If the current lot doesn't require visitation rights the player\n                will never be considered greeted.\n                ",
                                  tunable_type=bool,
                                  default=True)}

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        if services.get_zone_situation_manager().is_player_greeted() != self.test_for_greeted_status:
            if self.test_for_greeted_status:
                return TestResult(False, 'Player sim is ungreeted when we are looking for them being greeted.',
                  tooltip=(self.tooltip))
            return TestResult(False, 'Player sim is greeted when we are looking for them being ungreeted.',
              tooltip=(self.tooltip))
        return TestResult.TRUE


class RequiresVisitationRightsTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = ()
    FACTORY_TUNABLES = {'test_for_visitation_rights': Tunable(description="\n                If checked then this test will pass if the the current lot's\n                venue type requires visitation rights.  If unchecked then the\n                test will pass if it does not require visitation rights.\n                ",
                                     tunable_type=bool,
                                     default=True)}

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        if services.current_zone().venue_service.active_venue.requires_visitation_rights != self.test_for_visitation_rights:
            if self.test_for_visitation_rights:
                return TestResult(False, "The current lot's venue type doesn't require visitation rights.",
                  tooltip=(self.tooltip))
            return TestResult(False, "The current lot's venue type requires visitation rights.",
              tooltip=(self.tooltip))
        return TestResult.TRUE


class RewardPartTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):

    @TunableFactory.factory_option
    def participant_type_override(participant_type_enum, participant_type_default):
        return {'subject': TunableEnumEntry(description='\n                    Who or what to apply this test to\n                    ',
                      tunable_type=participant_type_enum,
                      default=participant_type_default)}

    FACTORY_TUNABLES = {'subject':TunableEnumEntry(description='\n            Who or what to apply this test to\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'reward_parts':TunableList(description='\n            All the reward parts that \n            ',
       tunable=TunableCasPart()), 
     'reward_parts_from_object_participant':TunableEnumEntry(description='\n            A participant whose saved cas parts will be appended to any tuned\n            in reward_parts.\n            ',
       tunable_type=ParticipantTypeCASPart,
       default=ParticipantTypeCASPart.StoredCASPartsOnObject), 
     'invert':Tunable(description='\n            If checked, test will pass if any subject does NOT have the unlock.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'test_targets':self.subject, 
         'additional_reward_parts':self.reward_parts_from_object_participant}

    @cached_test
    def __call__(self, test_targets=(), additional_reward_parts=None):
        reward_parts = list(self.reward_parts)
        if additional_reward_parts:
            reward_parts.extend(additional_reward_parts)
        for target in test_targets:
            if not target.is_sim:
                return TestResult(False, 'Cannot test unlock on none_sim object {} as subject {}.',
                  target,
                  (self.subject),
                  tooltip=(self.tooltip))
                household = target.household
                if all((household.part_in_reward_inventory(reward_part) for reward_part in reward_parts)) or self.invert:
                    return TestResult.TRUE
                return TestResult(False, "Sim {} hasn't unlock {}.",
                  target,
                  (self.reward_parts),
                  tooltip=(self.tooltip))

        if self.invert:
            return TestResult(False, 'No subjects have {} locked',
              (self.reward_parts),
              tooltip=(self.tooltip))
        return TestResult.TRUE


class PhoneSilencedTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'is_silenced': Tunable(description='\n            If checked the test will return True if the phone is silenced.\n            ',
                      tunable_type=bool,
                      default=True)}

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        is_phone_silenced = services.ui_dialog_service().is_phone_silenced
        if is_phone_silenced:
            if not self.is_silenced:
                return TestResult(False, 'The phone is not silenced.',
                  tooltip=(self.tooltip))
        if not is_phone_silenced:
            if self.is_silenced:
                return TestResult(False, 'The phone is silenced.',
                  tooltip=(self.tooltip))
        return TestResult.TRUE


class FireTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'lot_on_fire':OptionalTunable(Tunable(description='\n            Whether you are testing for fire being present on the lot or not\n            present.\n            ',
       tunable_type=bool,
       default=True)), 
     'sim_on_fire':OptionalTunable(TunableTuple(subject=TunableEnumEntry(ParticipantType, (ParticipantType.Actor),
       description='\n                Check the selected participant for whether or not they are on fire.\n                '),
       on_fire=Tunable(description='Whether the sim needs to be on fire or not', tunable_type=bool,
       default=True)))}

    def get_expected_args(self):
        args = {}
        if self.sim_on_fire is not None:
            args['subject'] = self.sim_on_fire.subject
        return args

    @cached_test
    def __call__(self, subject=[]):
        if self.lot_on_fire is not None:
            fire_service = services.get_fire_service()
            if not self.lot_on_fire == fire_service.fire_is_active:
                return TestResult(False, 'Testing for lot on fire failed. Lot on Fire={}, Wanted: {}', (fire_service.fire_is_active),
                  (self.lot_on_fire),
                  tooltip=(self.tooltip))
        if self.sim_on_fire is not None:
            for sim in subject:
                if not sim.on_fire == self.sim_on_fire.on_fire:
                    return TestResult(False, 'Sim on fire test failed. Sim={}, On Fire={}', sim,
                      (self.sim_on_fire.on_fire), tooltip=(self.tooltip))

        return TestResult.TRUE


class DetectiveClueTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            The participant for which we are running the test.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'career_reference':TunableReference(description='\n            The career for which we need to check clue information.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CAREER),
       class_restrictions=('DetectiveCareer', )), 
     'threshold':TunableThreshold(description='\n            The number of clues required in order to pass this test.\n            ')}

    def get_expected_args(self):
        return {'test_targets': self.participant}

    @cached_test
    def __call__(self, test_targets=(), **kwargs):
        for target in test_targets:
            career = target.careers.get(self.career_reference.guid64)
            if career is None:
                return TestResult(False, '{} is missing career {}', (str(target)), (self.career_reference), tooltip=(self.tooltip))
                discovered_clues = len(career.get_discovered_clues())
                return self.threshold.compare(discovered_clues) or TestResult(False, '{} does not meet required discovered clue threshold: {} {}', (str(target)), discovered_clues, (self.threshold), tooltip=(self.tooltip))

        return TestResult.TRUE


class FrontDoorTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = ()
    FACTORY_TUNABLES = {'invert': Tunable(description='\n            If checked, test will pass if there is NO front door\n            ',
                 tunable_type=bool,
                 default=False)}

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        door_service = services.get_door_service()
        if self.invert:
            if not door_service.has_front_door():
                return TestResult.TRUE
            return TestResult(False, 'Active lot has a front door.', tooltip=(self.tooltip))
        if door_service.has_front_door():
            return TestResult.TRUE
        return TestResult(False, 'Active lot has no front door.', tooltip=(self.tooltip))


class LockedPortalCountTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'number_to_test':TunableThreshold(description='\n            The number of doors that need to be locked to pass this test.\n            '), 
     'lock_priority':OptionalTunable(description='\n            The priority of the locks we want to test. None means all priorities.\n            ',
       tunable=TunableEnumEntry(tunable_type=LockPriority,
       default=(LockPriority.PLAYER_LOCK)),
       disabled_name='all_priorities',
       enabled_name='specify_priority'), 
     'lock_types':OptionalTunable(description='\n            The type of the locks we want to test. None means all types.\n            ',
       tunable=TunableEnumSet(enum_type=LockType,
       enum_default=(LockType.LOCK_ALL_WITH_SIMID_EXCEPTION)),
       disabled_name='all_lock_types',
       enabled_name='specify_lock_type')}

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        object_manager = services.object_manager()
        number_of_locked_doors = sum((1 for portal in object_manager.portal_cache_gen() if portal.has_lock_data(self.lock_priority, self.lock_types)))
        if not self.number_to_test.compare(number_of_locked_doors):
            return TestResult(False, ('{} of doors locked, failed threshold {}:{}.'.format(number_of_locked_doors, self.number_to_test.comparison, self.number_to_test.value)),
              tooltip=(self.tooltip))
        return TestResult.TRUE


class PortalLockingTestData(TunableTuple):

    def __init__(self, **kwargs):
        (super().__init__)(subject=TunableEnumEntry(tunable_type=ParticipantType,
  default=(ParticipantType.Actor)), 
         lock_priority=TunableEnumEntry(tunable_type=LockPriority,
  default=(LockPriority.PLAYER_LOCK)), **kwargs)


class PortalLockedTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'test_data':TunableVariant(description='\n            Different condition we want the test to test against.\n            ',
       test_lock_exist=PortalLockingTestData(description='\n                Test if the door has any lock on it with the certain lock\n                priority.\n                ',
       locked_args={'subject': None}),
       test_lock_sim=PortalLockingTestData(description='\n                Test if the door will lock the sim in the subject.\n                ',
       locked_args={'lock_priority': None}),
       default='test_lock_exist'), 
     'targets':TunableEnumEntry(description='\n            The object(s) to test.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Object,
       invalid_enums=(
      ParticipantType.Invalid,)), 
     'require_locking_component':Tunable(description='\n            If checked, every object targeted by the test must have a locking\n            component. If unchecked, the test can continue without requiring\n            every object to have a locking component.\n            ',
       tunable_type=bool,
       default=True), 
     'negate':Tunable(description='\n            If checked, the test will pass if there is no lock on the object\n            (test_lock_exist selected) or the object is not locked to sim\n            (test_lock_sim selected).\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        result = {'target_list': self.targets}
        if self.test_data.subject is not None:
            result['sims_to_test'] = self.test_data.subject
        return result

    @cached_test
    def __call__(self, target_list=None, sims_to_test=None):
        if not target_list:
            return TestResult(False, "Target object doesn't exist or none provided.", tooltip=(self.tooltip))
        else:
            lock_exist = False
            for obj in target_list:
                if not obj.has_locking_component():
                    if not self.require_locking_component:
                        continue
                    return TestResult(False, ('{} does not have a locking component.'.format(obj)), tooltip=(self.tooltip))
                    if sims_to_test is None:
                        if obj.has_lock_data(lock_priority=(self.test_data.lock_priority)):
                            lock_exist = True
                else:
                    for sim_info in sims_to_test:
                        if not sim_info.is_sim:
                            return TestResult(False, ('{} is not a sim for subject {}'.format(sim_info, self.subject)), tooltip=(self.tooltip))
                            sim = sim_info.get_sim_instance()
                            if sim is None:
                                return TestResult(False, ('{} is not instanced.'.format(sim_info)), tooltip=(self.tooltip))
                            if obj.test_lock(sim):
                                lock_exist = True

            if lock_exist:
                if self.negate:
                    return TestResult(False, ('Object {} has lock, will not pass test with negate {}'.format(target_list[0], self.negate)), tooltip=(self.tooltip))
            if not lock_exist:
                if not self.negate:
                    return TestResult(False, ("Object {} doesn't have lock, will not pass test with negate {}".format(target_list[0], self.negate)), tooltip=(self.tooltip))
        return TestResult.TRUE


class HasPortalTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'portal_participant':TunableEnumEntry(description='\n            Object that should have valid portals. If more than one object are passed in, \n            The test will pass if all the objects have valid portals.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Object), 
     'who':OptionalTunable(description='\n            If enabled then we will test the sim can go through the portal or not. \n            Otherwise we will test the portal itself is valid or not.\n            ',
       tunable=TunableEnumEntry(description='\n                Sims that should go through the portal.\n                ',
       tunable_type=ParticipantType,
       default=(ParticipantType.Actor)))}

    def get_expected_args(self):
        return {'test_targets':self.portal_participant, 
         'sims_to_test':self.who}

    @cached_test
    def __call__(self, test_targets=None, sims_to_test=None):
        if not test_targets:
            return TestResult(False, 'Failed state check: no target object found!', tooltip=(self.tooltip))
        for target in test_targets:
            if target.portal_component is None:
                return TestResult(False, '{} does not have a portal component.', target, tooltip=(self.tooltip))
            for portal in target.get_portal_instances():
                if sims_to_test is not None:
                    for sim_info in sims_to_test:
                        if not sim_info.is_sim:
                            return TestResult(False, '{} is not a sim'.format(sims_to_test, tooltip=(self.tooltip)))
                            sim = sim_info.get_sim_instance()
                            if sim is None:
                                return TestResult(False, ('{} is not instanced.'.format(sims_to_test)), tooltip=(self.tooltip))
                            required_flags = portal.get_required_flags()
                            sim_flags = sim.get_routing_context().get_portal_key_mask()
                            return sim_flags & required_flags == required_flags or TestResult(False, "{} sim doesn't have required flags to go through this portal", target, tooltip=(self.tooltip))

                return TestResult.TRUE

            return TestResult(False, "{} doesn't have a valid portal.", target, tooltip=(self.tooltip))


class HasPhotoFilterTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            The participant for which we are running the test.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Object), 
     'photo_filter':TunableEnumEntry(description='\n            The photo filter that you want to test that this photo is using.\n            ',
       tunable_type=PhotoStyleType,
       default=PhotoStyleType.NORMAL), 
     'negate':Tunable(description='\n            If checked the test will fail if the photo is using the tuned photo filter.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'target_list': self.participant}

    @cached_test
    def __call__(self, target_list=None):
        for photo in target_list:
            canvas_component = photo.canvas_component
            if canvas_component is None:
                return TestResult(False, 'HasPhotoFilterTest is being called on an object which is missing a canvas component.', tooltip=(self.tooltip))
                has_same_filter = canvas_component.painting_effect == self.photo_filter
                if self.negate:
                    if has_same_filter:
                        return TestResult(False, 'This photo has the same filter type, and test was negated.', tooltip=(self.tooltip))
                else:
                    return has_same_filter or TestResult(False, 'This photo has a different filter type.', tooltip=(self.tooltip))

        return TestResult.TRUE


class LotHasFloorFeatureTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'terrain_feature': TunableEnumEntry(description='\n            Tune this to the floor feature type that needs to be present\n            ',
                          tunable_type=FloorFeatureType,
                          default=(FloorFeatureType.BURNT))}
    test_events = ()

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        lot = services.active_lot()
        if lot is not None:
            if build_buy.list_floor_features(self.terrain_feature):
                return TestResult.TRUE
            return TestResult(False, 'Active lot does not have the tuned floor feature.', tooltip=(self.tooltip))
        return TestResult(False, 'Active lot is None.', tooltip=(self.tooltip))


class RegionTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'whitelist':OptionalTunable(description='\n            If enabled then we will check a whitelist of regions in insure that\n            the sim is within one of them.\n            ',
       tunable=TunableSet(description='\n                A set of regions that the sim being tested must be within.\n                ',
       tunable=TunableReference(description='\n                    A region that the sim being tested in must be within.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.REGION)),
       pack_safe=True))), 
     'blacklist':OptionalTunable(description='\n            If enabled then we will check a blacklist of regions in insure that\n            the sim is not within one of them.\n            ',
       tunable=TunableSet(description='\n                A set of regions that the sim being tested must not be within.\n                ',
       tunable=TunableReference(description='\n                    A region that the sim being tested in must not be within.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.REGION)),
       pack_safe=True))), 
     'subject':OptionalTunable(description='\n            If enabled then we will test the region of the specified\n            participant type.  Otherwise we will test the current region.\n            ',
       tunable=TunableEnumEntry(description='\n                Who do we want to run this test on.\n                ',
       tunable_type=ParticipantTypeActorTargetSim,
       default=(ParticipantTypeActorTargetSim.Actor)))}
    test_events = ()

    def get_expected_args(self):
        if self.subject is None:
            return {}
        return {'sim_info_list': self.subject}

    def _check_region(self, region_to_test):
        if self.whitelist is not None:
            if region_to_test not in self.whitelist:
                return TestResult(False, 'RegionTest: {} not in region whitelist.',
                  region_to_test,
                  tooltip=(self.tooltip))
        if self.blacklist is not None:
            if region_to_test in self.blacklist:
                return TestResult(False, 'RegionTest: {} in region blacklist',
                  region_to_test,
                  tooltip=(self.tooltip))
        return TestResult.TRUE

    @cached_test
    def __call__(self, sim_info_list=None):
        if self.subject is None:
            current_region = services.current_region()
            return self._check_region(current_region)
        else:
            return sim_info_list or TestResult(False, 'RegionTest: sim_info_list is None when trying to check for regions.',
              tooltip=(self.tooltip))
        import world
        for sim_info in sim_info_list:
            region_to_test = world.region.get_region_instance_from_zone_id(sim_info.zone_id)
            test_result = self._check_region(region_to_test)
            if not test_result:
                return test_result

        return TestResult.TRUE


class BucksPerkTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            The participant whose household will be checked for the specified\n            Perk  If being used outside of an interaction, any Sim participant\n            types are not valid.  Consider using object in these circumstances.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Actor), 
     'bucks_perk':TunablePackSafeReference(description='\n            The specific Perk to check against.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.BUCKS_PERK)), 
     'test_if_unlocked':Tunable(description='\n            If checked, this test will check to see if the specified Perk is\n            unlocked. If unchecked, this test will check to see if the\n            specified Perk is locked.\n            ',
       tunable_type=bool,
       default=True), 
     'requires_same_club':OptionalTunable(description='\n            When enabled it requires that the tuned target be in the \n            associated club with the participant.\n            \n            For example, this can be used to require that the participant\n            and target be in the club associated with the secret handshake\n            interaction and that the correct perk for that handshake is \n            unlocked.\n            ',
       tunable=TunableEnumEntry(description='\n                The participant that must also have the perk unlocked in a \n                bucks tracker that they share in common with the tuned \n                participant.\n                ',
       tunable_type=ParticipantTypeSingle,
       default=(ParticipantTypeSingle.TargetSim))), 
     'invert':Tunable(description='\n            If checked, the results of the test will be inverted. \n            The truth table is as follows for sim with the perk:\n            test_if_unlocked is true and invert is false: True\n            test_if_unlocked is true and invert is true: False\n            test_if_unlocked is false and invert is false: False\n            test_if_unlocked is false and invert is true: True\n            ',
       tunable_type=bool,
       default=False)}
    test_events = (
     TestEvent.BucksPerkUnlocked,)

    def get_expected_args(self):
        args = {'participants': self.participant}
        if self.requires_same_club is not None:
            args['targets'] = self.requires_same_club
            args['clubs'] = ParticipantType.AssociatedClub
        return args

    @cached_test
    def __call__(self, participants, clubs=None, targets=()):
        invert = self.invert
        if self.bucks_perk is None:
            if self.invert:
                return TestResult.TRUE
        else:
            return TestResult(False, 'bucks_perk is tuned to None, which likely means the pack required for the perk is not installed.')
            if clubs is None:
                if targets:
                    return TestResult(False, 'Trying to tests if Target {} is a member of the same club as Participant {} and there is no associated club.', targets, participants)
            for participant in participants:
                unlocked_trackers = [bucks_tracker for bucks_tracker in participant.bucks_trackers_gen() if bucks_tracker if bucks_tracker.is_perk_unlocked(self.bucks_perk)]
                if clubs is not None:
                    for club in clubs:
                        if club.bucks_tracker not in unlocked_trackers and self.test_if_unlocked:
                            if not invert:
                                return TestResult(False, "Club {} doesn't have the required perk {}", club, self.bucks_perk)
                                return TestResult(True, "Club {} doesn't have the required perk {} and invert is set to be True", club, self.bucks_perk)
                            elif club.bucks_tracker in unlocked_trackers:
                                return self.test_if_unlocked or invert or TestResult(False, 'Club {} has unlocked perk {}, but it needs to be locked.', club, self.bucks_perk)
                                return TestResult(True, 'Club {} has unlocked perk {}, but it needs to be locked and invert is set to be True.', club, self.bucks_perk)
                            if targets is not None:
                                for target in targets:
                                    if target not in club.members:
                                        if not invert:
                                            return TestResult(False, 'Target {} is not in the club with {} that has the perk {} locked/unlocked', target, participant, self.bucks_perk)
                                        return TestResult(True, 'Target {} is not in the club with {} that has the perk {} locked/unlocked and invert is set to be True.', target, participant, self.bucks_perk)

                elif self.test_if_unlocked:
                    if not unlocked_trackers:
                        if not invert:
                            return TestResult(False, 'Participant {} does not have the required Perk {} unlocked', participant, (self.bucks_perk), tooltip=(self.tooltip))
                        return TestResult(True, 'Participant {} does not have the required Perk {} unlocked and invert is set to be True.', participant, self.bucks_perk)
                if self.test_if_unlocked or unlocked_trackers:
                    if not invert:
                        return TestResult(False, 'Participant {} has the specified Perk {} unlocked, but is required not to.', participant, (self.bucks_perk), tooltip=(self.tooltip))
                    return TestResult(True, 'Participant {} has the specified Perk {} unlocked, but is required not to and invert is set to be True.', participant, self.bucks_perk)

            return invert or TestResult.TRUE
        return TestResult(False, 'Participant {} passed this test for the specified Perk {} and invert is set to be True.', participant, (self.bucks_perk), tooltip=(self.tooltip))


ENSEMBLE_CHECK_ALL = 0
ENSEMBLE_CHECK_ALL_VISIBLE = 1
ENSEMBLE_CHECK_SUBSET = 2

class EnsembleTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            The participant of whos ensemble we want to look at.\n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'check_matching_ensemble':OptionalTunable(description='\n            If enabled then we will only check ensembles that the participant\n            and this tuned participant are in together.\n            ',
       tunable=TunableEnumEntry(description='\n                The participant of whos ensemble we want to look at.\n                ',
       tunable_type=ParticipantTypeSingleSim,
       default=(ParticipantTypeSingleSim.TargetSim))), 
     'invert':Tunable(description="\n            If checked then we will check to see if the participant isn't in\n            an ensemble of the chosen participant and option and threshold.\n            ",
       tunable_type=bool,
       default=False), 
     'ensemble_option':TunableVariant(description='\n            Which ensembles to check against when testing.  If any of these\n            ensembles pass the check then the test will pass.\n            ',
       check_all=TunableTuple(description='\n                Check against all ensembles that this sim is in.\n                ',
       locked_args={'check_type': ENSEMBLE_CHECK_ALL}),
       check_visible=TunableTuple(description='\n                Check only against the visible ensmebles that the sim is in.\n                ',
       locked_args={'check_type': ENSEMBLE_CHECK_ALL_VISIBLE}),
       check_subset=TunableTuple(description='\n                Check only the ensembles tuned that the sim is in.\n                ',
       locked_args={'check_type': ENSEMBLE_CHECK_SUBSET},
       ensemble_types=TunableSet(description='\n                    The ensembles to check against.\n                    ',
       tunable=TunableReference(description='\n                        The ensemble to check against.\n                        ',
       manager=(services.get_instance_manager(sims4.resources.Types.ENSEMBLE)),
       pack_safe=True))),
       default='check_visible'), 
     'threshold':TunableThreshold(description='\n            The number of sims in that ensemble to check against.\n            '), 
     'check_selectable_sims':Tunable(description='\n            If checked then we will apply the threshold against the number of\n            selectable sims that are in that ensemble.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        if self.check_matching_ensemble is None:
            return {'test_targets': self.participant}
        return {'test_targets':self.participant, 
         'other_participants':self.check_matching_ensemble}

    @cached_test
    def __call__(self, test_targets=(), other_participants=None):
        ensemble_service = services.ensemble_service()
        for target in test_targets:
            sim = target.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if sim is None:
                return TestResult(False, 'EnsembleTest: Sim {} is not instanced.',
                  target,
                  tooltip=(self.tooltip))
                if self.ensemble_option.check_type == ENSEMBLE_CHECK_ALL:
                    ensembles = ensemble_service.get_all_ensembles_for_sim(sim)
                else:
                    if self.ensemble_option.check_type == ENSEMBLE_CHECK_ALL_VISIBLE:
                        ensembles = [ensemble for ensemble in ensemble_service.get_all_ensembles_for_sim(sim) if ensemble.visible]
                    else:
                        if self.ensemble_option.check_type == ENSEMBLE_CHECK_SUBSET:
                            ensembles = [ensemble for ensemble in ensemble_service.get_all_ensembles_for_sim(sim) if type(ensemble) in self.ensemble_option.ensemble_types]
                        else:
                            logger.error('Trying to use EnsembleTest with an unhandled Ensemble Option {}', (self.ensemble_option.check_type),
                              owner='jjacobson')
                if other_participants:
                    for ensemble in tuple(ensembles):
                        for other_sim_info in other_participants:
                            other_sim = other_sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
                            if not ensemble.is_sim_in_ensemble(other_sim):
                                ensembles.remove(ensemble)

                for ensemble in ensembles:
                    if self.check_selectable_sims:
                        target_number = sum((1 for sim in ensemble if sim.is_selectable))
                    else:
                        target_number = len(ensemble)
                    if self.threshold.compare(target_number):
                        if self.invert:
                            return TestResult(False, 'EnsembleTest: Sim {} is in an ensemble {} that matches the tuned threshold.',
                              sim,
                              ensemble,
                              tooltip=(self.tooltip))
                        break
                else:
                    return self.invert or TestResult(False, 'EnsembleTest: Sim {} is not in an ensemble that matches tuned threshold.',
                      sim,
                      tooltip=(self.tooltip))

        return TestResult.TRUE


class PurchasePerkTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'bucks_type':TunableEnumEntry(description='\n            The participant of whos ensemble we want to look at.\n            ',
       tunable_type=BucksType,
       default=BucksType.INVALID,
       pack_safe=True), 
     'consider_existing_perks':Tunable(description='\n            If checked, this test will return true if the sim has already\n            purchased a perk with the tuned buck type.\n            ',
       tunable_type=bool,
       default=False)}
    test_events = (
     TestEvent.PerkPurchased,)

    def get_expected_args(self):
        return {'bucks_type':event_testing.test_constants.FROM_EVENT_DATA,  'perk':event_testing.test_constants.FROM_EVENT_DATA, 
         'participant':ParticipantType.Actor}

    def __call__(self, participant, bucks_type=BucksType.INVALID, perk=None):
        if self.consider_existing_perks:
            sim_info = participant[0]
            bucks_tracker = sim_info.get_bucks_tracker()
            if bucks_tracker is not None:
                if bucks_tracker.has_perk_unlocked_for_bucks_type(self.bucks_type):
                    return TestResult.TRUE
        if self.bucks_type != bucks_type:
            return TestResult(False, 'Perk was purchased using the wrong bucks type. {}', bucks_type)
        return TestResult.TRUE


class TotalClubBucksEarnedTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = (
     TestEvent.ClubBucksEarned,)
    USES_DATA_OBJECT = True
    FACTORY_TUNABLES = {'threshold': TunableThreshold(description='\n            Test for how may Club Bucks the Sim must earn to pass the test.\n            ',
                    tunable_type=int,
                    default=10)}

    def get_expected_args(self):
        return {'participant':ParticipantType.Actor, 
         'data_object':event_testing.test_constants.FROM_DATA_OBJECT}

    def __call__(self, participant, data_object):
        club_bucks_earned = data_object.get_total_club_bucks_earned()
        if not self.threshold.compare(club_bucks_earned):
            return TestResultNumeric(False, current_value=club_bucks_earned, goal_value=(self.threshold.value), tooltip=('{} has not earned enough club buck to satisfy {} test. Current total is {}'.format(participant, self.threshold, club_bucks_earned)))
        return TestResultNumeric(True, current_value=club_bucks_earned, goal_value=(self.threshold.value))

    def goal_value(self):
        return self.threshold.value


class TimeInClubGatheringsTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = (
     TestEvent.TimeInClubGathering,)
    USES_DATA_OBJECT = True
    FACTORY_TUNABLES = {'threshold': TunableThreshold(description='\n            Test for how may Sim minutes the sim must spend in a club gathering\n            to pass the test.\n            ',
                    tunable_type=int,
                    default=10)}

    def get_expected_args(self):
        return {'participant':ParticipantType.Actor, 
         'data_object':event_testing.test_constants.FROM_DATA_OBJECT}

    def __call__(self, participant, data_object):
        time_in_club_gatherings = data_object.get_total_time_in_club_gatherings()
        if not self.threshold.compare(time_in_club_gatherings):
            return TestResultNumeric(False, current_value=time_in_club_gatherings, goal_value=(self.threshold.value), tooltip=('{} has not spent enough time in Club Gatherings. Total time in sim minutes: {}, Required: {}'.format(participant, self.threshold, time_in_club_gatherings)))
        return TestResultNumeric(True, current_value=time_in_club_gatherings, goal_value=(self.threshold.value))

    def goal_value(self):
        return self.threshold.value


class EventRanSuccessfullyTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'test_events': TunableList(description='\n            List of events that this test wants to listen for. Whenever\n            these tests are processed this test will just return True.\n            ',
                      tunable=TunableEnumEntry(description='\n                An event type to listen for in order to satsify this test.\n                ',
                      tunable_type=TestEvent,
                      default=(TestEvent.Invalid)))}

    def get_expected_args(self):
        return {}

    def get_test_events_to_register(self):
        return self.test_events

    def __call__(self, *args, **kwargs):
        return TestResult.TRUE


class StyleActiveTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'gender':TunableEnumEntry(description='\n            The gender to use when checking for the presence of a style/trend.\n            ',
       tunable_type=Gender,
       default=Gender.MALE), 
     'negate':Tunable(description='\n            If checked then the result of the test will be negated.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {}

    def __call__(self, *args, **kwargs):
        style_service = services.get_style_service()
        if style_service is None:
            return TestResult(False, "There is no active style service which likely means that the correct pack isn't loaded.", tooltip=(self.tooltip))
        if not style_service.has_active_style_outfit(self.gender):
            if self.negate:
                return TestResult.TRUE
            return TestResult(False, 'The Style active test did not pass. There are currently zero style/trends active. Go create one.', tooltip=(self.tooltip))
        if self.negate:
            return TestResult(False, 'The Style active test did not pass. The test is negated which means there is currently and active style/trend.', tooltip=(self.tooltip))
        return TestResult.TRUE


class InteractionSourceTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'interaction_sources':TunableEnumSet(description='\n            A set of interaction sources we will check against.\n            ',
       enum_type=InteractionSource,
       enum_default=InteractionSource.PIE_MENU), 
     'invert':Tunable(description="\n            If checked then returns true if the interaction's source is not equal to any of the tuned value.\n            ",
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'context': ParticipantType.InteractionContext}

    def __call__(self, context=None):
        if context is None:
            return TestResult(False, 'Interaction Context is None. Make sure this test is Tuned on an Interaction.', tooltip=(self.tooltip))
        result = TestResult.TRUE
        if context.source not in self.interaction_sources:
            result = TestResult(False, 'InteractionSourceTest failed. Interaction source: {}, is not in the tuned set: {}',
              (context.source),
              (self.interaction_sources), tooltip=(self.tooltip))
        if self.invert:
            if result:
                return TestResult(False, 'InteractionSourceTest passed but invert is set to be True. Interaction source: {}, Tuned set: {}',
                  (context.source),
                  (self.interaction_sources), tooltip=(self.tooltip))
            return TestResult.TRUE
        return result


class TunableTestBasedScoreTestVariant(TunableVariant):

    def __init__(self, **kwargs):
        tunables = {'relationship_test_based_score':RelationshipTestBasedScore.TunableFactory(), 
         'social_context':SocialContextTest.TunableFactory()}
        kwargs.update(tunables)
        (super().__init__)(**kwargs)


class TunableSituationMedalTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'who':TunableEnumEntry(description='\n            The Sim who is involved in the situation you want to test the score of.\n            ',
       tunable_type=ParticipantTypeSim,
       default=ParticipantTypeSim.Actor), 
     'situation':TunableReference(description='\n            The situation you want to check the score for.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION)), 
     'threshold':TunableThreshold(description='\n            The threshold to use when comparing the medal in order to determine whether or not the\n            test should pass.\n            ',
       value=TunableEnumEntry(description='\n                The value to test against.\n                ',
       tunable_type=SituationMedal,
       default=(SituationMedal.TIN)))}

    def get_expected_args(self):
        return {'subjects': self.who}

    def __call__(self, *args, subjects=None, **kwargs):
        situation_manager = services.get_zone_situation_manager()
        for subject in subjects:
            sim = subject.get_sim_instance()
            if sim is None:
                continue
            for situation in situation_manager.get_situations_by_type(self.situation):
                if situation.is_sim_in_situation(sim):
                    level = situation.get_level()
                    if self.threshold.compare(level):
                        return TestResult.TRUE
                    return TestResult(False, 'The Sim ({}) has a medal of {} instead of {} in the {} situation', subject,
                      (str(level)), (self.threshold), (self.situation), tooltip=(self.tooltip))
            else:
                return TestResult(False, 'The Sim ({}) was not in any situations of type {}', subject, (self.situation),
                  tooltip=(self.tooltip))

        return TestResult(False, 'The subject Sims do not have a medal of {} in the {} situation.', (self.threshold),
          (self.situation), tooltip=(self.tooltip))