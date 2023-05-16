# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\outfits\outfit_tests.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 19152 bytes
import services, tag
from cas.cas import get_caspart_bodytype, get_tags_from_outfit
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from caches import cached_test
from interactions import ParticipantType, ParticipantTypeSingle, ParticipantTypeSim
from sims.outfits.outfit_enums import BodyType, OutfitCategory
from sims.outfits.outfit_utils import get_maximum_outfits_for_category
from sims4.tuning.tunable import TunableEnumEntry, HasTunableSingletonFactory, AutoFactoryInit, TunableTuple, Tunable, OptionalTunable, TunableVariant, TunableEnumSet, TunableInterval
from tunable_utils.tunable_white_black_list import TunableWhiteBlackList
import sims4.log
logger = sims4.log.Logger('OutfitTests', default_owner='rmccord')

class OutfitBodyTypeTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'subject':TunableEnumEntry(description='\n            The Sim we want to test the body type outfit for.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'outfit_override':OptionalTunable(description="\n            If enabled, specify a particular outfit to check the body types of.\n            Otherwise we check the subject's current outfit.\n            ",
       tunable=TunableTuple(description='\n                The outfit we want to check the body types of.\n                ',
       outfit_category=TunableEnumEntry(description='\n                    The outfit category.\n                    ',
       tunable_type=OutfitCategory,
       default=(OutfitCategory.EVERYDAY)),
       index=Tunable(description='\n                    The outfit index.\n                    ',
       tunable_type=int,
       default=0))), 
     'body_types':TunableWhiteBlackList(description='\n            The allowed and disallowed body types required to pass this test.\n            All CAS parts of the subject will be used to determine success or\n            failure.\n            ',
       tunable=TunableEnumEntry(description='\n                The body type we want the CAS part to support or not support.\n                ',
       tunable_type=BodyType,
       default=(BodyType.FULL_BODY),
       invalid_enums=(BodyType.NONE)))}

    def get_expected_args(self):
        return {'subjects': self.subject}

    @cached_test
    def __call__(self, subjects, *args, **kwargs):
        for subject in subjects:
            if not subject is None:
                if not subject.is_sim:
                    return TestResult(False, 'OutfitBodyTypeTest cannot test {}.', subject, tooltip=(self.tooltip))
                outfit_category_and_index = subject.get_current_outfit() if self.outfit_override is None else (self.outfit_override.outfit_category, self.outfit_override.index)
                if not subject.has_outfit(outfit_category_and_index):
                    return TestResult(False, 'OutfitBodyTypeTest cannot test {} since they do not have the requested outfit {}.', subject, outfit_category_and_index, tooltip=(self.tooltip))
                outfit = (subject.get_outfit)(*outfit_category_and_index)
                return self.body_types.test_collection(outfit.body_types) or TestResult(False, 'OutfitBodyTypeTest subject {} failed list of body types for outfit {}.', subject, outfit_category_and_index, tooltip=(self.tooltip))

        return TestResult.TRUE


class OutfitCASPartTagsTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):

    class _FromPreferenceTraits(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'use_likes': Tunable(description='\n                If checked, the test will use likes tags. If not checked, the test\n                will use dislikes tags.\n                ',
                        tunable_type=bool,
                        default=True)}

        def get_tags(self, sim, **kwargs):
            if sim is None:
                return
            pref_tags = set()
            preferences = sim.trait_tracker.likes if self.use_likes else sim.trait_tracker.dislikes
            for preference_trait in preferences:
                if preference_trait is None:
                    continue
                item_tags = preference_trait.preference_item.get_any_tags()
                if item_tags is not None:
                    pref_tags = pref_tags.union(item_tags)

            return pref_tags

    class _FromGenericTags(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'tags': tag.TunableTags(description="\n                A list of tags to test against. The test will pass if the sim's CAS parts match any of the tags.\n                ")}

        def get_tags(self, **kwargs):
            return self.tags

    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            Who or what to apply this test to.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Actor), 
     'body_type':OptionalTunable(description="\n            Enable this if we want to search a specific body part for a tag,\n            disable if doesn't apply.\n            ",
       tunable=TunableEnumEntry(description='\n                Which Body Type to search for tags.\n                ',
       tunable_type=BodyType,
       default=(BodyType.NONE),
       invalid_enums=(
      BodyType.NONE,))), 
     'tags_source':TunableVariant(description='\n            The source of the tags to test against\n            ',
       from_preference_traits=_FromPreferenceTraits.TunableFactory(description='\n                The tags will come from preference traits.\n                '),
       from_generic_tags=_FromGenericTags.TunableFactory(description='\n                The tags will come from generic tags.\n                '),
       default='from_generic_tags'), 
     'invert':Tunable(description='\n            If checked, the test will pass if we did NOT find the tag.\n            ',
       tunable_type=bool,
       default=False), 
     'tags_needed':TunableInterval(description="\n            Number of tags needed to count as 'passed'; having less than lower or more than upper will fail.\n            Checked before invert.\n            ",
       tunable_type=int,
       default_lower=1,
       default_upper=100,
       minimum=1)}

    def get_expected_args(self):
        return {'test_targets': self.participant}

    @cached_test
    def __call__(self, test_targets, **kwargs):
        result = TestResult(False, 'Sim has no matching tags', tooltip=(self.tooltip))
        sim = next(iter(test_targets))
        try:
            caspartid_tags_dic = get_tags_from_outfit(sim._base, *(sim.get_current_outfit()), **{'body_type_filter': self.body_type or BodyType.NONE})
        except Exception as exc:
            try:
                logger.error('Failed to calculate CAS Tags for Sim {} with current outfit: {}\nException: {}', sim,
                  (sim.get_current_outfit()), exc, owner='mbilello',
                  trigger_breakpoint=True)
                return TestResult(False, 'Failed to calculate CAS Tags for Sim ', tooltip=(self.tooltip))
            finally:
                exc = None
                del exc

        tags_to_look_for = self.tags_source.get_tags(sim=sim)
        match_count = 0
        if self.body_type is None:
            flattened_tags = list((item for entry in caspartid_tags_dic.values() for item in entry))
            for t in tags_to_look_for:
                match_count += flattened_tags.count(t)

        else:
            for key, value in caspartid_tags_dic.items():
                if value.intersection(tags_to_look_for):
                    match_count += 1

        if self.tags_needed.lower_bound <= match_count <= self.tags_needed.upper_bound:
            result = TestResult.TRUE
        else:
            result = TestResult(False, 'Sim does not have enough matching tags', tooltip=(self.tooltip))
        if self.invert:
            if result:
                return TestResult(False, 'Sim has enough matching tags', tooltip=(self.tooltip))
            return TestResult.TRUE
        return result


class OutfitTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    OUTFIT_CURRENT = 0
    OUTFIT_PREVIOUS = 1
    TEST_CAN_ADD = 0
    TEST_CANNOT_ADD = 1

    class _OutfitCategoryFromEnum(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'outfit_category': TunableEnumEntry(description='\n                The outfit category for which we must be able to add an outfit.\n                ',
                              tunable_type=OutfitCategory,
                              default=(OutfitCategory.EVERYDAY))}

        def get_expected_args(self):
            return {}

        def get_outfit_category(self, **kwargs):
            return self.outfit_category

    class _OutfitCategoryFromParticipant(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'participant': TunableEnumEntry(description='\n                The participant whose current outfit will determine the\n                resulting outfit category.\n                ',
                          tunable_type=ParticipantTypeSingle,
                          default=(ParticipantTypeSingle.Actor))}

        def get_expected_args(self):
            return {'outfit_category_targets': self.participant}

        def get_outfit_category(self, outfit_category_targets=(), **kwargs):
            outfit_category_target = next(iter(outfit_category_targets), None)
            if outfit_category_target is not None:
                outfit = outfit_category_target.get_current_outfit()
                return outfit[0]

    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            The participant against which to run this outfit test.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'outfit':TunableVariant(description='\n            The outfit to use for the blacklist/whitelist tests.\n            ',
       locked_args={'current_outfit':OUTFIT_CURRENT, 
      'previous_outfits':OUTFIT_PREVIOUS},
       default='current_outfit'), 
     'blacklist_outfits':TunableEnumSet(description="\n            If the specified participant's outfit matches any of these\n            categories, the test will fail.\n            ",
       enum_type=OutfitCategory), 
     'whitelist_outfits':TunableEnumSet(description="\n            If set, then the participant's outfit must match any of these\n            entries, or the test will fail.\n            ",
       enum_type=OutfitCategory), 
     'outfit_addition_test':OptionalTunable(description='\n            If enabled, then the test will verify whether or not the specified\n            participant can add an outfit to a specific category.\n            ',
       tunable=TunableTuple(description='\n                Tunables controlling the nature of this test.\n                ',
       outfit_category=TunableVariant(description='\n                    Define the outfit category for which we need to test addition.\n                    ',
       from_enum=(_OutfitCategoryFromEnum.TunableFactory()),
       from_participant=(_OutfitCategoryFromParticipant.TunableFactory()),
       default='from_enum'),
       test_type=TunableVariant(description='\n                    The condition to test for.\n                    ',
       locked_args={'can_add':TEST_CAN_ADD, 
      'cannot_add':TEST_CANNOT_ADD},
       default='can_add')))}

    def get_expected_args(self):
        expected_args = {'test_targets': self.participant}
        if self.outfit_addition_test is not None:
            expected_args.update(self.outfit_addition_test.outfit_category.get_expected_args())
        return expected_args

    @cached_test
    def __call__(self, test_targets=(), **kwargs):
        for target in test_targets:
            if self.outfit == self.OUTFIT_CURRENT:
                outfit = target.get_current_outfit()
            else:
                if self.outfit == self.OUTFIT_PREVIOUS:
                    outfit = target.get_previous_outfit()
                else:
                    if any((outfit[0] == blacklist_category for blacklist_category in self.blacklist_outfits)):
                        return TestResult(False, '{} is wearing a blacklisted outfit category', target, tooltip=(self.tooltip))
                    if self.whitelist_outfits:
                        return any((outfit[0] == whitelist_category for whitelist_category in self.whitelist_outfits)) or TestResult(False, '{} is not wearing any whitelisted outfit category', target, tooltip=(self.tooltip))
                outfit_addition_test = self.outfit_addition_test
            if outfit_addition_test is not None:
                outfit_category = (outfit_addition_test.outfit_category.get_outfit_category)(**kwargs)
                outfits = target.get_outfits()
                outfits_in_category = outfits.get_outfits_in_category(outfit_category)
                if outfit_addition_test.test_type == self.TEST_CAN_ADD:
                    if outfits_in_category is not None:
                        if len(outfits_in_category) >= get_maximum_outfits_for_category(outfit_category):
                            return TestResult(False, '{} cannot add a new {} outfit, but is required to be able to', target, outfit_category, tooltip=(self.tooltip))
                elif not outfit_addition_test.test_type == self.TEST_CANNOT_ADD or outfits_in_category is None or len(outfits_in_category) < get_maximum_outfits_for_category(outfit_category):
                    return TestResult(False, '{} can add a new {} outfit, but is required not to not be able to', target, outfit_category, tooltip=(self.tooltip))

        return TestResult.TRUE


class OutfitPrevalentTrendTagTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            Who or what to apply this test to.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Actor), 
     'trend_tags':tag.TunableTags(description="\n            A list of tags to test against. The test will pass if the sim's CAS \n            parts match the prevalent trend tag for the outfit.\n            ",
       filter_prefixes=('style', )), 
     'invert':Tunable(description='\n            If checked, the test will pass if we did NOT find the tag.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'test_targets': self.participant}

    @cached_test
    def __call__(self, test_targets, **kwargs):
        sim = next(iter(test_targets))
        try:
            current_outfit_data = (sim.get_outfit)(*sim.get_current_outfit())
        except Exception as exc:
            try:
                logger.error('Failed to current outfit for Sim {}: {}\nException: {}', sim,
                  (sim.get_current_outfit()), exc, owner='anchavez',
                  trigger_breakpoint=True)
                return TestResult(False, 'Failed to get current outfit for Sim ', tooltip=(self.tooltip))
            finally:
                exc = None
                del exc

        fashion_trend_service = services.fashion_trend_service()
        if fashion_trend_service is None:
            return TestResult(False, 'Could not access fashion trend service', tooltip=(self.tooltip))
        else:
            prevalent_trend = fashion_trend_service.get_outfit_trend(current_outfit_data)
            if prevalent_trend in self.trend_tags:
                result = TestResult.TRUE
            else:
                result = TestResult(False, "Sim's outfit doesn't match any tags", tooltip=(self.tooltip))
        if self.invert:
            if result:
                return TestResult(False, "Sim's outfit has matching tags", tooltip=(self.tooltip))
            return TestResult.TRUE
        return result