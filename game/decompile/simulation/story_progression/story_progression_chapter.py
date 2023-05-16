# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_chapter.py
# Compiled at: 2022-03-10 20:35:10
# Size of source mod 2**32: 18126 bytes
import services
from date_and_time import DateAndTime
from default_property_stream_reader import DefaultPropertyStreamReader
from distributor.rollback import ProtocolBufferRollback
from event_testing.tests import TunableTestSet
from interactions import ParticipantTypeSavedStoryProgression
from sims4 import PropertyStreamWriter
from sims4.localization import TunableLocalizedStringFactoryVariant
from sims4.random import pop_weighted
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableReference, TunableList, TunableTuple, TunableVariant, OptionalTunable, TunableEnumEntry
from story_progression.story_progression_actions.story_progression_action_career import AddCareerStoryProgressionAction, RemoveCareerStoryProgressionAction, RetireStoryProgressionAction
from story_progression.story_progression_actions.story_progression_action_death import DeathStoryProgressionAction
from story_progression.story_progression_actions.story_progression_action_family import AddFamilyMemberStoryProgressionAction, MakePregnantStoryProgressionAction
from story_progression.story_progression_actions.story_progression_action_moving import MoveInStoryProgressionAction, MoveOutStoryProgressionAction
from story_progression.story_progression_result import StoryProgressionResult, StoryProgressionResultType
from tunable_multiplier import TunableMultiplier

class StoryProgressionLinkedChapters(TunableList):

    def __init__(self, class_restrictions=(), **kwargs):
        (super().__init__)(description='\n            A list of possible future chapters that are selected utilizing\n            a weighted random with tests.\n            ', 
         tunable=TunableTuple(possible_chapter=TunableReference(description='\n                    A possible future Chapter.\n                    ',
  manager=(services.get_instance_manager(Types.STORY_CHAPTER)),
  class_restrictions=class_restrictions),
  weight=TunableMultiplier.TunableFactory(description='\n                    A weight with testable multipliers that is used to \n                    determine how likely this entry is to be picked when \n                    selecting randomly.\n                    ')), **kwargs)


class BaseStoryChapter(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.STORY_CHAPTER)):
    INSTANCE_TUNABLES = {'preconditions':TunableTestSet(description='\n            A set of tests that need to pass before this chapter can progress.\n            '), 
     'loot_list':TunableList(description='\n            A list of loot that will be applied when chapter is complete.\n            This will be applied after the actions are applied.\n            ',
       tunable=TunableReference(description='\n                An individual loot that will be applied when the chapter\n                has been completed.\n                ',
       manager=(services.get_instance_manager(Types.ACTION)),
       class_restrictions=('LootActions', ),
       pack_safe=True)), 
     'discovery':OptionalTunable(description="\n            Tuning data for when this chapter's history is discovered by the player.\n            ",
       tunable=TunableTuple(string=TunableLocalizedStringFactoryVariant(description="\n                    String to display when this chapter's history is discovered by the player.\n                    "),
       token_participants=TunableList(description="\n                    Expected participants required to generate tokens used to localize this string.  The order of \n                    participants in this list will define the token indices starting from index 3 (this string is assumed\n                    to be triggered as interaction loot so 0 is used for the interaction actor sim, 1 is used for \n                    interaction target, 2 is used for the chapter's owning sim/household).  Tuning to define what data \n                    will be stored in each participant can be tuned in this chapter's actions.\n                    ",
       tunable=TunableEnumEntry(tunable_type=ParticipantTypeSavedStoryProgression,
       default=(ParticipantTypeSavedStoryProgression.SavedStoryProgressionSim1))))), 
     'drama_nodes':TunableList(description='\n            A list of additional drama nodes that we will score and schedule\n            when this chapter is complete.\n            ',
       tunable=TunableReference(description='\n                A drama node that we will score and schedule when this chapter is complete.\n                ',
       manager=(services.get_instance_manager(Types.DRAMA_NODE))))}
    INSTANCE_SUBCLASSES_ONLY = True

    def __init__(self, arc):
        self._arc = arc
        self._future_chapters = None
        self._is_active = False
        self._story_progression_actions = []
        self._completion_time = None

    @property
    def arc(self):
        return self._arc

    def _setup_future_chapters(self, **kwargs):
        if not self.linked_chapters:
            return StoryProgressionResult(StoryProgressionResultType.SUCCESS)
        self._future_chapters = []
        for index, chapter_data in enumerate(self.linked_chapters):
            potential_chapter = chapter_data.possible_chapter(self._arc)
            result = (potential_chapter.setup)(**kwargs)
            if not result:
                return result
                self._future_chapters.append((index, potential_chapter))

        return StoryProgressionResult(StoryProgressionResultType.SUCCESS)

    def on_set_current(self):
        self._is_active = True

    def on_removed_from_current(self):
        self._is_active = False

    def setup(self, **kwargs):
        result = (self._setup_future_chapters)(**kwargs)
        if not result:
            return result
        for action_factory in self.actions:
            action = action_factory(self._arc)
            result = (action.setup_story_progression_action)(**kwargs)
            if not result:
                return result
                self._story_progression_actions.append(action)

        return result

    def _can_update(self):
        raise NotImplementedError

    def update_story_chapter(self):
        result = self._can_update()
        if not result:
            return result
        else:
            resolver = self._arc.get_resolver()
            result = self.preconditions.run_tests(resolver)
            return result or StoryProgressionResult(StoryProgressionResultType.FAILED_PRECONDITIONS, result.reason)
        for action in self._story_progression_actions:
            result = action.run_story_progression_action()
            if not result:
                return result

        resolver = self._arc.get_resolver()
        for loot_action in self.loot_list:
            loot_action.apply_to_resolver(resolver)

        return StoryProgressionResult(StoryProgressionResultType.SUCCESS_MAKE_HISTORICAL)

    def get_next_chapter(self):
        if self._future_chapters is None:
            return (
             StoryProgressionResult(StoryProgressionResultType.SUCCESS_MAKE_HISTORICAL), None)
        else:
            resolver = self._arc.get_resolver()
            weighted_list = []
            for index, potential_chapter in self._future_chapters:
                weight = self.linked_chapters[index].weight.get_multiplier(resolver)
                if weight > 0:
                    weighted_list.append((weight, potential_chapter))

            return weighted_list or (
             StoryProgressionResult(StoryProgressionResultType.FAILED_NEXT_CHAPTER, 'Story Chapter {} has tuning for future chapters, but all future chapters tested out.', self), None)
        next_chapter = pop_weighted(weighted_list)
        return (StoryProgressionResult(StoryProgressionResultType.SUCCESS_MAKE_HISTORICAL), next_chapter)

    def get_completion_time(self):
        return self._completion_time

    def _cleanup_future_chapters(self):
        if self._future_chapters is None:
            return
        for _, possible_future_chapter in self._future_chapters:
            if possible_future_chapter._is_active:
                continue
            possible_future_chapter.cleanup()

        self._future_chapters = None

    def end_chapter(self):
        self._is_active = False
        self._cleanup_future_chapters()
        self._completion_time = services.time_service().sim_now

    def cleanup(self):
        self._is_active = False
        self._arc = None
        self._cleanup_future_chapters()

    def get_gsi_data(self):
        data = []
        for action in self._story_progression_actions:
            gsi_data = action.get_gsi_data()
            if gsi_data is None:
                continue
            data.extend(gsi_data)

        return data

    def get_csv_data(self):
        additional_data = None
        for action in self._story_progression_actions:
            gsi_data = action.get_gsi_data()
            if gsi_data is None:
                continue
            for data in gsi_data:
                if additional_data is None:
                    additional_data = ''
                else:
                    additional_data += '/'
                additional_data += f"{data['field']}:{data['data']}"

        return additional_data

    def save(self, chapter_msg):
        chapter_msg.type = self.guid64
        if self._future_chapters is not None:
            for index, future_chapter in self._future_chapters:
                with ProtocolBufferRollback(chapter_msg.future_chapters) as (future_chapter_msg):
                    future_chapter_msg.index = index
                    future_chapter.save(future_chapter_msg.future_chapter)

        if self._completion_time is not None:
            chapter_msg.completion_time = self._completion_time.absolute_ticks()
        writer = PropertyStreamWriter()
        for action in self._story_progression_actions:
            action.save_custom_data(writer)

        data = writer.close()
        if writer.count > 0:
            chapter_msg.action_data = data

    def load(self, chapter_msg):
        chapter_instance_manager = services.get_instance_manager(Types.STORY_CHAPTER)
        for future_chapter_msg in chapter_msg.future_chapters:
            future_chapter_type = chapter_instance_manager.get(future_chapter_msg.future_chapter.type)
            if future_chapter_type is None:
                continue
            if self._future_chapters is None:
                self._future_chapters = []
            future_chapter = future_chapter_type(self._arc)
            future_chapter.load(future_chapter_msg.future_chapter)
            self._future_chapters.append((future_chapter_msg.index, future_chapter))

        if chapter_msg.HasField('action_data'):
            reader = DefaultPropertyStreamReader(chapter_msg.action_data)
        else:
            reader = None
        for action_factory in self.actions:
            action = action_factory(self._arc)
            if reader is not None:
                action.load_custom_data(reader)
            self._story_progression_actions.append(action)

        if chapter_msg.HasField('completion_time'):
            self._completion_time = DateAndTime(chapter_msg.completion_time)


class SimStoryChapter(BaseStoryChapter):
    INSTANCE_TUNABLES = {'linked_chapters':StoryProgressionLinkedChapters(class_restrictions=('SimStoryChapter', )), 
     'actions':TunableList(description='\n            The actions that will be taken when this chapter runs.\n            ',
       tunable=TunableVariant(description='\n                The action that will be taken when this chapter runs.\n                ',
       add_family_member=(AddFamilyMemberStoryProgressionAction.TunableFactory()),
       career_add=(AddCareerStoryProgressionAction.TunableFactory()),
       career_remove=(RemoveCareerStoryProgressionAction.TunableFactory()),
       career_retire=(RetireStoryProgressionAction.TunableFactory()),
       death=(DeathStoryProgressionAction.TunableFactory()),
       pregnancy=(MakePregnantStoryProgressionAction.TunableFactory()),
       default='death'))}

    @property
    def sim_info(self):
        return self._arc.sim_info

    @property
    def reserved_household_slots(self):
        reserved_slots = sum((action.reserved_household_slots for action in self._story_progression_actions))
        if self._future_chapters is not None:
            reserved_slots += sum((future_chapter.reserved_household_slots for _, future_chapter in self._future_chapters))
        return reserved_slots

    def end_chapter(self):
        super().end_chapter()
        services.get_story_progression_service().cache_historical_arcs_sim_id(self.sim_info.id)

    def _can_update(self):
        if not self.sim_info.is_npc:
            return StoryProgressionResult(StoryProgressionResultType.FAILED_ROTATION, 'The chapter is on an Active Sim.')
        return StoryProgressionResult(StoryProgressionResultType.SUCCESS)


class HouseholdStoryChapter(BaseStoryChapter):
    INSTANCE_TUNABLES = {'linked_chapters':StoryProgressionLinkedChapters(class_restrictions=('HouseholdStoryChapter', )), 
     'actions':TunableList(description='\n            The actions that will be taken when this chapter runs.\n            ',
       tunable=TunableVariant(description='\n                The action that will be taken when this chapter runs.\n                ',
       move_in=(MoveInStoryProgressionAction.TunableFactory()),
       move_out=(MoveOutStoryProgressionAction.TunableFactory()),
       default='move_in'))}

    @property
    def household(self):
        return self._arc.household

    def end_chapter(self):
        super().end_chapter()
        services.get_story_progression_service().cache_historical_arcs_household_id(self.household.id)

    def _can_update(self):
        if self.household.is_active_household:
            return StoryProgressionResult(StoryProgressionResultType.FAILED_ROTATION, 'The chapter is on the Active Household.')
        return StoryProgressionResult(StoryProgressionResultType.SUCCESS)