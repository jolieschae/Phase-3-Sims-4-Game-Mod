# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\developmental_milestones\developmental_milestone_tests.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 14262 bytes
import enum, event_testing.test_base, services, sims4
from caches import cached_test
from developmental_milestones.developmental_milestone_enums import DevelopmentalMilestoneStates
from event_testing.results import TestResult
from interactions import ParticipantTypeSingleSim
from relationships.relationship_bit import RelationshipBit
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunablePackSafeReference, Tunable, TunableList, TunableReference, OptionalTunable
from tunable_utils.tunable_white_black_list import TunableWhiteBlackList

class DevelopmentalMilestoneTestResult(enum.Int):
    FAIL = 0
    PASS = 1


class DevelopmentalMilestoneTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = ()
    FACTORY_TUNABLES = {'developmental_milestone':TunablePackSafeReference(description='\n            Milestone to test for.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.DEVELOPMENTAL_MILESTONE)), 
     'developmental_milestone_state':TunableEnumEntry(description='\n            The state of the given milestone to compare against. If the milestone is repeatable, the test will pass if\n            the tunable state is UNLOCKED and the repeatable milestone has any previous goals completed.\n            ',
       tunable_type=DevelopmentalMilestoneStates,
       default=DevelopmentalMilestoneStates.UNLOCKED), 
     'current_zone':OptionalTunable(description="\n            If checked, the current zone will be tested against the milestone's stored zone id. If any situation goal passes, this test passes.\n            ",
       tunable=Tunable(tunable_type=bool,
       default=False)), 
     'relationship_bits':OptionalTunable(description='\n            If checked, the relationship bits are tested against the subject and any secondary sim on the goal. If any situation goal passes, this test passes.\n            ',
       tunable=TunableList(description='\n                List of relationship bits to test against.\n                ',
       tunable=(RelationshipBit.TunableReference()))), 
     'subject':TunableEnumEntry(description='\n            The subject of this milestone test.\n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'support_low_lod':Tunable(description="\n            If checked, low-LOD Sims can pass this test based on their age progress and the milestone's tuned\n            'treat_unlocked_at_age_percentage' value.\n            ",
       tunable_type=bool,
       default=True), 
     'fallback_result':TunableEnumEntry(description="\n            Result to return if the pack for this milestone not installed.\n            Note that this does not take the 'invert' flag into account.\n            ",
       tunable_type=DevelopmentalMilestoneTestResult,
       default=DevelopmentalMilestoneTestResult.FAIL), 
     'invert':Tunable(description='\n            Whether or not to invert the results of this test.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'subjects': self.subject}

    @cached_test
    def __call__(self, subjects=(), **kwargs):
        subject = next(iter(subjects), None)
        if subject is None:
            return TestResult(False, 'Target is None.', tooltip=(self.tooltip))
        else:
            return subject.is_sim or TestResult(False, "Can't test developmental milestone when subject: {} is not a Sim.", subject,
              tooltip=(self.tooltip))
        milestone_tracker = subject.sim_info.developmental_milestone_tracker
        if milestone_tracker is None or self.developmental_milestone is None:
            if self.fallback_result is DevelopmentalMilestoneTestResult.PASS:
                return TestResult.TRUE
            elif milestone_tracker is None:
                return TestResult(False, 'Subject Sim {} does not have a developmental milestone tracker.', subject,
                  tooltip=(self.tooltip))
                return TestResult(False, 'Developmental Milestone referenced in test is not available, and fallback_result is FAIL.',
                  tooltip=(self.tooltip))
            else:
                if subject.sim_info.lod >= milestone_tracker._tracker_lod_threshold:
                    result = self._test_subject(milestone_tracker, subject)
                else:
                    if self.support_low_lod:
                        result = self._test_subject_low_lod(subject)
                    else:
                        return TestResult(False, 'Subject Sim {} is low-LOD and support_low_lod was not specified.', subject,
                          tooltip=(self.tooltip))
            if self.invert:
                if not result:
                    return TestResult.TRUE
                return TestResult(False, 'Developmental Milestone test would have passed for Sim {}, but result is inverted.', subject,
                  tooltip=(self.tooltip))
        else:
            return result

    def _test_subject(self, milestone_tracker, subject):
        milestone_state = milestone_tracker.get_milestone_state(self.developmental_milestone)
        if milestone_state != self.developmental_milestone_state:
            if not self.developmental_milestone.repeatable:
                return TestResult(False, 'Subject Sim {} does not have the required state {} for milestone {}.', subject,
                  (self.developmental_milestone_state), (self.developmental_milestone), tooltip=(self.tooltip))
        else:
            if self.developmental_milestone_state == DevelopmentalMilestoneStates.UNLOCKED:
                if not milestone_tracker.any_previous_goal_completed(self.developmental_milestone):
                    return TestResult(False, 'Subject Sim {} does not have any previous completions for the repeatable milestone {}.', subject,
                      (self.developmental_milestone), tooltip=(self.tooltip))
            else:
                situation_goals = milestone_tracker.get_milestone_goals(self.developmental_milestone)
                passes_zone_test = self.current_zone is None
                passes_relationship_test = self.relationship_bits is None
                sim_info = None
                secondary_sim_info = None
                for situation_goal in situation_goals:
                    if self.current_zone is not None:
                        situation_goal_zone_id = situation_goal.get_actual_zone_id()
                        if situation_goal_zone_id is not None:
                            if situation_goal_zone_id == services.current_zone_id():
                                passes_zone_test = True
                    if self.relationship_bits is not None:
                        sim_info = situation_goal.sim_info
                        secondary_sim_info = situation_goal.get_actual_target_sim_info()
                        if secondary_sim_info is not None and sim_info.relationship_tracker.has_bits(secondary_sim_info.id, self.relationship_bits):
                            passes_relationship_test = True

                return passes_zone_test or TestResult(False, "DevelopmentalMilestoneTest: The test's zone ID does not match the current zone ID.")
            return passes_relationship_test or TestResult(False, 'DevelopmentalMilestoneTest: The two sims ({},{}) do not have the tuned relationship bits ({}) in common', sim_info, secondary_sim_info, self.relationship_bits)
        return TestResult.TRUE

    def _test_subject_low_lod(self, subject):
        required_age_percentage = self.developmental_milestone.treat_unlocked_at_age_percentage
        if required_age_percentage is None:
            return TestResult(False, 'Subject Sim {} is low-LOD and treat_unlocked_at_age_percentage was not specified for milestone {}.', subject,
              (self.developmental_milestone), tooltip=(self.tooltip))
        if self.developmental_milestone_state == DevelopmentalMilestoneStates.ACTIVE:
            return TestResult(False, 'Testing for ACTIVE milestone {} but Subject Sim {} is low-LOD and we do not support treating milestones as active for low-LOD Sims.', (self.developmental_milestone),
              subject, tooltip=(self.tooltip))
        sim_age_percentage = subject.sim_info.age_progress_percentage
        if self.developmental_milestone_state == DevelopmentalMilestoneStates.UNLOCKED:
            if sim_age_percentage < required_age_percentage:
                return TestResult(False, 'Testing for UNLOCKED milestone {} but Subject Sim {} is low-LOD and does not meet the required age percentage {}.', (self.developmental_milestone),
                  subject, required_age_percentage, tooltip=(self.tooltip))
        if self.developmental_milestone_state == DevelopmentalMilestoneStates.LOCKED:
            if sim_age_percentage >= required_age_percentage:
                return TestResult(False, 'Testing for LOCKED milestone {} but Subject Sim {} is low-LOD and meets the required age percentage {}.', (self.developmental_milestone),
                  subject, required_age_percentage, tooltip=(self.tooltip))
        return TestResult.TRUE


class DevelopmentalMilestoneCompletionTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'developmental_milestones':TunableWhiteBlackList(description='\n           A white/blacklist for milestones to test against.\n           ',
       tunable=TunableReference(description='\n                Check for completion against this milestone list. A milestone is complete if it is unlocked or,\n                if repeatable, has any previous goals.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.DEVELOPMENTAL_MILESTONE)),
       pack_safe=True)), 
     'fallback_result':TunableEnumEntry(description="\n            Result to return if the pack for this milestone is not installed.\n            Note that this does not take the 'invert' flag into account.\n            ",
       tunable_type=DevelopmentalMilestoneTestResult,
       default=DevelopmentalMilestoneTestResult.FAIL), 
     'invert':Tunable(description='\n            Whether or not to invert the results of this test.\n            ',
       tunable_type=bool,
       default=False), 
     'subject':TunableEnumEntry(description='\n            The subject of this milestone test.\n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor)}

    def get_expected_args(self):
        return {'subjects': self.subject}

    @cached_test
    def __call__(self, subjects=(), **kwargs):
        subject = next(iter(subjects), None)
        if subject is None:
            return TestResult(False, 'Target is None.', tooltip=(self.tooltip))
        else:
            if not subject.is_sim:
                return TestResult(False, "Can't test developmental milestone when subject: {} is not a Sim.", subject,
                  tooltip=(self.tooltip))
            milestone_tracker = subject.sim_info.developmental_milestone_tracker
            if milestone_tracker is None:
                if self.fallback_result is DevelopmentalMilestoneTestResult.PASS:
                    return TestResult.TRUE
                return TestResult(False, 'Subject Sim {} does not have a developmental milestone tracker.', subject,
                  tooltip=(self.tooltip))
            completed_milestones = milestone_tracker.get_all_completed_milestones()
            result = self.developmental_milestones.test_collection(completed_milestones)
            if self.invert:
                if not result:
                    return TestResult.TRUE
                return TestResult(False, 'Developmental Milestone test would have passed for Sim {}, but result is inverted.', subject,
                  tooltip=(self.tooltip))
            return result or TestResult(False, 'Developmental Milestones completion state(s) for Sim{} do not pass.',
              subject,
              tooltip=(self.tooltip))
        return TestResult.TRUE