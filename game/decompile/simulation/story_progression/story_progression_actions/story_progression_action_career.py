# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_actions\story_progression_action_career.py
# Compiled at: 2022-03-10 20:35:10
# Size of source mod 2**32: 7701 bytes
import services, random
from abc import ABC
from event_testing.resolver import SingleSimResolver
from interactions import ParticipantTypeSavedStoryProgressionString
from sims4.random import weighted_random_item
from sims4.tuning.tunable import OptionalTunable, TunableEnumEntry
from story_progression.story_progression_actions.story_progression_action_base import BaseSimStoryProgressionAction
from story_progression.story_progression_result import StoryProgressionResult, StoryProgressionResultType

class BaseCareerStoryProgressionAction(BaseSimStoryProgressionAction, ABC):
    FACTORY_TUNABLES = {'store_career_name_participant':OptionalTunable(description='\n            If enabled we will store off the career name into the specified participant type for future use in tokens\n            or other resolvers.\n            ',
       tunable=TunableEnumEntry(tunable_type=ParticipantTypeSavedStoryProgressionString,
       default=(ParticipantTypeSavedStoryProgressionString.SavedStoryProgressionString1))), 
     'store_job_name_participant':OptionalTunable(description='\n            If enabled we will store off the job name into the specified participant type for future use in tokens\n            or other resolvers.\n            ',
       tunable=TunableEnumEntry(tunable_type=ParticipantTypeSavedStoryProgressionString,
       default=(ParticipantTypeSavedStoryProgressionString.SavedStoryProgressionString1)))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._target_career = None

    def _save_participants(self):
        super()._save_participants()
        if self._target_career is None:
            return
        job_token, career_token, _ = self._target_career.get_career_text_tokens()
        if self.store_career_name_participant is not None:
            self._owner_arc.store_participant(self.store_career_name_participant, career_token)
        if self.store_job_name_participant is not None:
            self._owner_arc.store_participant(self.store_job_name_participant, job_token)


class AddCareerStoryProgressionAction(BaseCareerStoryProgressionAction):

    def _career_multipliers_gen(self):
        career_service = services.get_career_service()
        sim_info = self._owner_arc.sim_info
        resolver = SingleSimResolver(sim_info)
        for career in career_service.get_career_list():
            if career.career_story_progression.joining is None:
                continue
            if not career.is_valid_career(sim_info=sim_info):
                continue
            if sim_info.career_tracker.has_career_by_uid(career.guid64):
                continue
            weight = career.career_story_progression.joining.get_multiplier(resolver)
            if weight <= 0:
                continue
            yield (
             weight, career)

    def setup_story_progression_action(self, **kwargs):
        for _ in self._career_multipliers_gen():
            return StoryProgressionResult(StoryProgressionResultType.SUCCESS)

        return StoryProgressionResult(StoryProgressionResultType.FAILED_TESTS, 'Cannot setup AddCareerStoryProgressionAction since Sim has no valid careers they can join.')

    def _run_story_progression_action(self):
        weights = list(self._career_multipliers_gen())
        if not weights:
            return StoryProgressionResult(StoryProgressionResultType.FAILED_ACTION, 'Cannot add career to Sim for AddCareerStoryProgressionAction since no careers are valid.')
        new_career = weighted_random_item(weights)
        max_user_level = new_career.get_max_user_level()
        user_level = random.randint(1, max_user_level)
        self._target_career = new_career(self._owner_arc.sim_info)
        self._owner_arc.sim_info.career_tracker.add_career((self._target_career), user_level_override=user_level, give_skipped_rewards=False)
        return StoryProgressionResult(StoryProgressionResultType.SUCCESS_MAKE_HISTORICAL)


class RemoveCareerStoryProgressionAction(BaseCareerStoryProgressionAction):

    def setup_story_progression_action(self, **kwargs):
        for career in self._owner_arc.sim_info.career_tracker:
            if not career.can_quit:
                continue
            if career.career_story_progression.quitting is None:
                continue
            return StoryProgressionResult(StoryProgressionResultType.SUCCESS)

        return StoryProgressionResult(StoryProgressionResultType.FAILED_TESTS, 'Cannot setup RemoveCareerStoryProgressionAction since Sim has no career.')

    def _run_story_progression_action(self):
        careers_quit = self._owner_arc.sim_info.career_tracker.quit_quittable_careers(num_careers_to_quit=1)
        if careers_quit:
            self._target_career = careers_quit[0][1]
            return StoryProgressionResult(StoryProgressionResultType.SUCCESS_MAKE_HISTORICAL)
        return StoryProgressionResult(StoryProgressionResultType.FAILED_ACTION, 'No careers quit while processing RemoveCareerStoryProgressionAction')


class RetireStoryProgressionAction(BaseCareerStoryProgressionAction):

    def _career_multipliers_gen(self):
        sim_info = self._owner_arc.sim_info
        resolver = SingleSimResolver(sim_info)
        for career in sim_info.career_tracker:
            if not career.can_quit:
                continue
            if career.career_story_progression.retiring is None:
                continue
            weight = career.career_story_progression.retiring.get_multiplier(resolver)
            if weight <= 0:
                continue
            yield (
             weight, career)

    def setup_story_progression_action(self, **kwargs):
        for _ in self._career_multipliers_gen():
            return StoryProgressionResult(StoryProgressionResultType.SUCCESS)

        return StoryProgressionResult(StoryProgressionResultType.FAILED_TESTS, 'Cannot setup RetireCareerStoryProgressionAction since Sim has no career.')

    def _run_story_progression_action(self):
        possible_careers = list(self._career_multipliers_gen())
        if not possible_careers:
            return StoryProgressionResult(StoryProgressionResultType.FAILED_ACTION, 'RetireCareerStoryProgressionAction: No careers can be retired.')
        self._target_career = weighted_random_item(possible_careers)
        self._owner_arc.sim_info.career_tracker.retire_career(self._target_career.guid64)
        return StoryProgressionResult(StoryProgressionResultType.SUCCESS_MAKE_HISTORICAL)