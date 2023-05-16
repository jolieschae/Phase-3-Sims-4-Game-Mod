# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\preference_tests.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 8592 bytes
import services, sims4.log, sims4.resources
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from caches import cached_test
from interactions import ParticipantType, ParticipantTypeObject, ParticipantTypeSingleSim
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableEnumEntry, Tunable, TunableReference, TunableVariant, TunableList
from traits.preference_enums import PreferenceTypes, PreferenceSubject
logger = sims4.log.Logger('PreferenceTests', default_owner='trevor')

class ObjectPreferenceTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'sims':TunableEnumEntry(description='\n            The Sim(s) to test.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'targets':TunableEnumEntry(description='\n            The object(s) to test.\n            ',
       tunable_type=ParticipantTypeObject,
       default=ParticipantType.Object), 
     'preference_type':TunableEnumEntry(description='\n            The preference-value to check for the existence of on the Sim for the object.\n            ',
       tunable_type=PreferenceTypes,
       default=PreferenceTypes.LIKE), 
     'preference_subjects':TunableList(description='\n            The list of preference subjects to validate the\n            target object against. \n            \n            For example, a sim can have a preference for defined object sets,\n            or they can have a preference for a decor style. \n            ',
       tunable=TunableEnumEntry(description='\n                The Preference Subject to consider.\n                ',
       tunable_type=PreferenceSubject,
       default=(PreferenceSubject.OBJECT)))}

    def get_expected_args(self):
        return {'sims':self.sims, 
         'targets':self.targets}

    @cached_test
    def __call__(self, sims, targets):
        for sim in sims:
            preferences = sim.trait_tracker.get_preferences_for_subjects((self.preference_type,), self.preference_subjects)
            for preference in preferences:
                for target in targets:
                    if preference.preference_item.target_is_preferred(target):
                        return TestResult.TRUE

        return TestResult(False, "The target object {} does not match Sim {}'s preference: {}", targets, sims, self.preference_type)


class GigPreferenceTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):

    class _GigPreferenceTestCategory(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'preference_category':TunableReference(description='\n                The preference category to test against.\n                ',
           manager=services.get_instance_manager(sims4.resources.Types.CAS_PREFERENCE_CATEGORY),
           pack_safe=True), 
         'known':Tunable(description='\n                If checked, this test will pass if the sim knows a preference from\n                the tuned category. If unchecked, this test will pass if the sim\n                does not know a preference from the tune category.\n                ',
           tunable_type=bool,
           default=True)}

        def run_test(self, gig):
            if not hasattr(gig, 'get_known_client_preferences'):
                logger.error("Gig {} doesn't use preferences.", gig)
                return TestResult(False, "Trying to run a gig preference test on a gig that doesn't use preferences.")
            known_preferences = gig.get_known_client_preferences()
            trait_manager = services.get_instance_manager(sims4.resources.Types.TRAIT)
            for preference_id in known_preferences:
                preference_trait = trait_manager.get(preference_id)
                if preference_trait.preference_category is self.preference_category:
                    if self.known:
                        return TestResult.TRUE
                    return TestResult(False, "Sim knows a preference in the tuned category and the test is tuned to pass if they don't know.")

            if self.known:
                return TestResult(False, 'Sim does not know any preference in the tuned category.')
            return TestResult.TRUE

    class _GigPreferenceTestCompletion(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'discovered_all_preferences': Tunable(description='\n                If checked, this test will pass if the Sim has discovered all of\n                the preferences for the gig. If unchecked, the test will pass if\n                the Sim has not discovered all of the preferences for the gig.\n                ',
                                         tunable_type=bool,
                                         default=True)}

        def run_test(self, gig):
            if not hasattr(gig, 'all_preferences_revealed'):
                logger.error("Gig {} doesn't use preferences.", gig)
                return TestResult(False, "Trying to run a gig preference test on a gig that doesn't use preferences.")
            if gig.all_preferences_revealed():
                if self.discovered_all_preferences:
                    return TestResult.TRUE
                return TestResult(False, "The sim discovered all the preferences but the test is tuned to pass if they're not all discovered.")
            if self.discovered_all_preferences:
                return TestResult(False, 'The sim has not discovered all the preferences.')
            return TestResult.TRUE

    FACTORY_TUNABLES = {'sim':TunableEnumEntry(description='\n            The Sim to test against.\n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'career':TunableReference(description='\n            The career to look at for gig preferences. As of now, this is only\n            used for the Decorator career.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CAREER)), 
     'preference_test':TunableVariant(description="\n            The type of test to run against the current Gig's preferences.\n            ",
       preference_category=_GigPreferenceTestCategory.TunableFactory(),
       preference_completion=_GigPreferenceTestCompletion.TunableFactory())}

    def get_expected_args(self):
        return {'sim': self.sim}

    @cached_test
    def __call__(self, sim):
        if len(sim) != 1:
            logger.error('Running a Gig Preference and got {} sims. Only 1 sim should have been found.', len(sim))
            return TestResult(False, 'Got the incorrect number of Sims.')
        current_sim = sim[0]
        career = current_sim.career_tracker.get_career_by_uid(self.career.guid64)
        if career is None:
            logger.error('Running a Gig Preference test but the Sim {} does have the career {}.', current_sim, self.career)
            return TestResult(False, "Sim doesn't have the tuned career.")
        gig = career.get_current_gig()
        if gig is None:
            logger.error("Running a Gig Preference test but the Sim {} doesn't have any gig in the career {}.", current_sim, self.career)
            return TestResult(False, 'Sim has no current gig.')
        return self.preference_test.run_test(gig)