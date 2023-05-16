# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_arc.py
# Compiled at: 2022-04-05 18:57:40
# Size of source mod 2**32: 25632 bytes
import random, services
from date_and_time import DateAndTime
from distributor.rollback import ProtocolBufferRollback
from event_testing.resolver import SingleSimResolver, HouseholdResolver, DoubleSimResolver, SingleSimAndHouseholdResolver
from gsi_handlers.drama_handlers import is_scoring_archive_enabled, GSIDramaScoringData, archive_drama_scheduler_scoring
from interactions import STORY_PROGRESSION_SIM_PARTICIPANTS, ParticipantType, STORY_PROGRESSION_ZONE_PARTICIPANTS, STORY_PROGRESSION_STRING_PARTICIPANTS, get_number_of_bit_shifts_by_participant_type
from protocolbuffers.Localization_pb2 import LocalizedString
from sims4.log import Logger
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableReference, TunableVariant, TunableList, TunableEnumEntry
from sims4.utils import classproperty, constproperty
from story_progression import StoryProgressionArcSeedReason, story_progression_telemetry
from story_progression.story_progression_candidate_selection import SelectSimCandidateFromDemographicListFunction, SelectSimCandidateFromFilterFunction, SelectHouseholdCandidateMatchingLotFromDemographicListFunction, SelectHouseholdWithHomeCandidateFromDemographicListBasedOnCullingScoreFunction
from story_progression.story_progression_enums import StoryType
from story_progression.story_progression_exclusivity import StoryProgressionExclusivityCategory
from story_progression.story_progression_log import log_story_progression_update
from story_progression.story_progression_result import StoryProgressionResultType, StoryProgressionResult
from story_progression.story_progression_tuning import StoryProgTunables
logger = Logger('StoryProgression', default_owner='jjacobson')

class BaseStoryArc(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.STORY_ARC)):
    INSTANCE_SUBCLASSES_ONLY = True
    INSTANCE_TUNABLES = {'required_rules':TunableList(description='\n            Sims/households must have these rules enabled in order to be chosen as a candidate for this arc.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(Types.USER_INTERFACE_INFO)),
       class_restrictions='StoryProgressionRuleDisplayInfo',
       pack_safe=True)), 
     'exclusivity_category':TunableEnumEntry(description='\n            The exclusivity category of this story progression arc.  Neutral means that this arc can be seeded with any\n            other arc already on the Sim/Household.  See story_progression_exclusivity for details of how this works.\n            ',
       tunable_type=StoryProgressionExclusivityCategory,
       default=StoryProgressionExclusivityCategory.NEUTRAL)}

    @classproperty
    def _initial_story_chapter(cls):
        raise NotImplementedError

    def __init__(self, tracker):
        self._tracker = tracker
        self._current_chapter = None
        self._historical_chapters = None
        self._stored_participants = None
        self._chapter_with_drama_nodes_to_schedule = None

    @property
    def historical_chapters(self):
        if self._historical_chapters is None:
            return tuple()
        return tuple(self._historical_chapters)

    @property
    def tracker(self):
        return self._tracker

    @classmethod
    def select_candidates(cls, demographic_sims, demographic_households, demographic_zones):
        return cls.candidate_selection_function(demographic_sims, demographic_households, demographic_zones, cls)

    def setup(self, **kwargs):
        initial_chapter = self._initial_story_chapter(self)
        try:
            result = (initial_chapter.setup)(**kwargs)
        except Exception as e:
            try:
                logger.exception('Exception while trying to setup story arc. {}', self)
                return StoryProgressionResult(StoryProgressionResultType.ERROR, 'Exception: {}', e)
            finally:
                e = None
                del e

        if result:
            if 'start_reason' in kwargs:
                self._set_current_chapter(initial_chapter, start_reason=(kwargs['start_reason']))
            else:
                self._set_current_chapter(initial_chapter)
        else:
            initial_chapter.cleanup()
        return result

    def _set_current_chapter(self, new_chapter, start_reason=StoryProgressionArcSeedReason.SYSTEM):
        old_chapter = self._current_chapter
        if old_chapter is not None:
            old_chapter.on_removed_from_current()
        self._current_chapter = new_chapter
        if self._current_chapter is not None:
            self._current_chapter.on_set_current()
            story_progression_telemetry.send_chapter_start_telemetry(self._current_chapter, start_reason)
        if old_chapter is not None:
            old_chapter.end_chapter()

    def update_story_arc(self):
        updated_chapter = self._current_chapter
        if self._current_chapter is None:
            result = StoryProgressionResult(StoryProgressionResultType.ERROR, 'Attempting to update Arc {} that has no current chapter.', self)
            log_story_progression_update(self.tracker, self, self._current_chapter, result)
            return (result, updated_chapter)
        current_chapter_result = self._current_chapter.update_story_chapter()
        log_story_progression_update(self.tracker, self, self._current_chapter, current_chapter_result)
        if current_chapter_result.result_type == StoryProgressionResultType.FAILED_PRECONDITIONS:
            return (
             current_chapter_result, updated_chapter)
        if current_chapter_result:
            if self._current_chapter.drama_nodes:
                self._chapter_with_drama_nodes_to_schedule = self._current_chapter
            else:
                new_chapter_result, next_chapter = self._current_chapter.get_next_chapter()
                if new_chapter_result.should_be_made_historical:
                    if self._historical_chapters is None:
                        self._historical_chapters = []
                    self._historical_chapters.append(self._current_chapter)
                new_chapter_result or self._set_current_chapter(None)
                return (new_chapter_result, updated_chapter)
            self._set_current_chapter(next_chapter)
            if self._current_chapter is None:
                return (
                 StoryProgressionResult(StoryProgressionResultType.SUCCESS_MAKE_HISTORICAL), updated_chapter)
            return (
             StoryProgressionResult(StoryProgressionResultType.SUCCESS), updated_chapter)
        self._set_current_chapter(None)
        return (current_chapter_result, updated_chapter)

    def schedule_drama_nodes_gen(self, timeline=None):
        if self._chapter_with_drama_nodes_to_schedule is not None:
            drama_scheduler = services.drama_scheduler_service()
            if is_scoring_archive_enabled():
                gsi_data = GSIDramaScoringData()
                gsi_data.bucket = f"Story Chapter: {self._chapter_with_drama_nodes_to_schedule}"
            else:
                gsi_data = None
            yield from drama_scheduler.score_and_schedule_nodes_gen((self._chapter_with_drama_nodes_to_schedule.drama_nodes), 1,
              timeline=timeline,
              resolver_resolver=(self._get_drama_node_resolver),
              gsi_data=gsi_data)
            if gsi_data is not None:
                archive_drama_scheduler_scoring(gsi_data)
            self._chapter_with_drama_nodes_to_schedule = None
        if False:
            yield None

    def cleanup(self):
        if self._current_chapter is not None:
            self._current_chapter.cleanup()
        self._tracker = None
        self._stored_participants = None

    def _get_additional_participants_for_resolver(self):
        if self._stored_participants is None:
            return {}
        additional_participants = {}
        sim_info_manager = services.sim_info_manager()
        for participant, obj in self._stored_participants.items():
            if participant & STORY_PROGRESSION_SIM_PARTICIPANTS:
                obj = sim_info_manager.get(obj)
                if obj is None:
                    continue
            additional_participants[participant] = (
             obj,)

        return additional_participants

    def get_resolver(self):
        raise NotImplementedError

    def _get_drama_node_resolver(self, actor_sim_info):
        raise NotImplementedError

    def store_participant(self, participant, obj):
        if obj is None:
            logger.error('Arc {} is attempting to store participant {} but obj is None.', self, participant)
            return
        else:
            isinstance(obj, (int, str, LocalizedString)) or logger.error('Arc {} is attempting to store participant {} object {} of unsupported type {}.', self, participant, obj, type(obj))
            return
        if self._stored_participants is None:
            self._stored_participants = {}
        if participant in self._stored_participants:
            logger.warn('Setting participant {} to {} which is already within the stored participants as {}.  This is fine if such overwriting of participants is expected.', participant, obj, self._stored_participants[participant])
        self._stored_participants[participant] = obj

    def get_gsi_data(self):
        if self._current_chapter is None:
            current_chapter = 'No Current Chapter'
            current_chapter_data = []
        else:
            current_chapter = str(self._current_chapter)
            current_chapter_data = self._current_chapter.get_gsi_data()
        historical_chapter_data = []
        if self._historical_chapters is not None:
            expiration_timespan = StoryProgTunables.HISTORY.chapter_history_lifetime()
            for chapter in self._historical_chapters:
                completion_time = chapter.get_completion_time()
                time_until_expiration = completion_time + expiration_timespan - services.time_service().sim_now
                historical_chapter_data.append({'chapter':str(chapter), 
                 'time_completed':str(completion_time), 
                 'time_until_expiration':str(time_until_expiration)})

        entry = {'arc_type':str(self), 
         'chapter_type':current_chapter, 
         'current_chapter_data':current_chapter_data, 
         'historical_chapter_data':historical_chapter_data}
        return entry

    def try_remove_historical_chapter(self, chapter):
        if self._historical_chapters is not None:
            if chapter in self._historical_chapters:
                self._historical_chapters.remove(chapter)
                return True
        return False

    def get_random_historical_chapter(self):
        if not self._historical_chapters:
            return (None, None)
        index = random.randint(0, len(self._historical_chapters) - 1)
        chapter = self._historical_chapters[index]
        tokens = [
         self.get_resolver().get_participant(self._actor_participant)]
        tokens += self._get_discovery_tokens(chapter)
        return (chapter, tokens)

    def _get_discovery_tokens(self, chapter):
        tokens = []
        if self._stored_participants is None or chapter.discovery is None:
            return tokens
        sim_info_manager = services.sim_info_manager()
        zone_manager = services.get_zone_manager()
        for participant_type in chapter.discovery.token_participants:
            obj = None
            value = self._stored_participants.get(participant_type)
            if value is not None:
                if participant_type & STORY_PROGRESSION_SIM_PARTICIPANTS:
                    obj = sim_info_manager.get(value)
                else:
                    if participant_type & STORY_PROGRESSION_ZONE_PARTICIPANTS:
                        obj = zone_manager.get(value)
                    else:
                        if participant_type & STORY_PROGRESSION_STRING_PARTICIPANTS:
                            obj = value
            if obj is None:
                logger.error('Stored participant type {0} not found for story progression arc {1}', participant_type, self)
            tokens.append(obj)

        return tokens

    def save(self, arc_msg):
        arc_msg.type = self.guid64
        if self._current_chapter is not None:
            self._current_chapter.save(arc_msg.current_chapter)
        if self._historical_chapters is not None:
            for historical_chapter in self._historical_chapters:
                with ProtocolBufferRollback(arc_msg.historical_chapters) as (historical_chapter_msg):
                    historical_chapter.save(historical_chapter_msg)

        if self._stored_participants is not None:
            for participant_type, participant in self._stored_participants.items():
                with ProtocolBufferRollback(arc_msg.saved_participants) as (participant_msg):
                    participant_msg.participant_type = get_number_of_bit_shifts_by_participant_type(participant_type)
                    if type(participant) is str:
                        participant_msg.participant_str = participant
                    else:
                        if type(participant) is int:
                            participant_msg.participant_id = int(participant)
                        else:
                            if isinstance(participant, LocalizedString):
                                participant_msg.participant_loc_str = participant
                            else:
                                raise RuntimeError('Arc {} is attempting to save unknown type for stored participant {}.'.format(self, participant))

    def load(self, arc_msg):
        chapter_instance_manager = services.get_instance_manager(Types.STORY_CHAPTER)
        if arc_msg.HasField('current_chapter'):
            chapter_type = chapter_instance_manager.get(arc_msg.current_chapter.type)
            if chapter_type is not None:
                chapter = chapter_type(self)
                chapter.load(arc_msg.current_chapter)
                self._current_chapter = chapter
                self._current_chapter.on_set_current()
        now = services.time_service().sim_now
        expiration_timespan = StoryProgTunables.HISTORY.chapter_history_lifetime()
        for historical_chapter_msg in arc_msg.historical_chapters:
            chapter_type = chapter_instance_manager.get(historical_chapter_msg.type)
            if chapter_type is None:
                continue
            if now - DateAndTime(historical_chapter_msg.completion_time) > expiration_timespan:
                continue
            if self._historical_chapters is None:
                self._historical_chapters = []
            chapter = chapter_type(self)
            chapter.load(historical_chapter_msg)
            self._historical_chapters.append(chapter)

        for participant_msg in arc_msg.saved_participants:
            if self._stored_participants is None:
                self._stored_participants = {}
            else:
                participant_type = ParticipantType(1 << participant_msg.participant_type)
                if participant_msg.HasField('participant_str'):
                    participant = participant_msg.participant_str
                else:
                    if participant_msg.HasField('participant_loc_str'):
                        if participant_msg.participant_loc_str.hash != 0:
                            participant = LocalizedString()
                            participant.MergeFrom(participant_msg.participant_loc_str)
                        else:
                            continue
                    else:
                        if participant_msg.HasField('participant_id'):
                            participant = participant_msg.participant_id
                        else:
                            logger.error('Arc {} is attempting to load unknown type for stored participant {}.', self, participant_msg)
                            continue
            self._stored_participants[participant_type] = participant

    def on_zone_load(self):
        raise NotImplementedError

    def remove_expired_historical_chapters(self):
        if not self._historical_chapters:
            return
        now = services.time_service().sim_now
        expiration_timespan = StoryProgTunables.HISTORY.chapter_history_lifetime()
        for historical_chapter in tuple(self._historical_chapters):
            completion_time = historical_chapter.get_completion_time()
            time_since_completion = now - completion_time
            if time_since_completion > expiration_timespan:
                historical_chapter.cleanup()
                self._historical_chapters.remove(historical_chapter)


class SimStoryArc(BaseStoryArc):
    INSTANCE_TUNABLES = {'starting_chapter':TunableReference(description='\n            The first chapter of this Story Arc.\n            ',
       manager=services.get_instance_manager(Types.STORY_CHAPTER),
       class_restrictions='SimStoryChapter'), 
     'candidate_selection_function':TunableVariant(description='\n            The function used to figure out the actual candidates to run the arcs on.\n            ',
       sim_from_demographic_list=SelectSimCandidateFromDemographicListFunction.TunableFactory(),
       sim_from_filter=SelectSimCandidateFromFilterFunction.TunableFactory(),
       default='sim_from_demographic_list')}

    @classproperty
    def _initial_story_chapter(cls):
        return cls.starting_chapter

    @constproperty
    def _actor_participant():
        return ParticipantType.Actor

    @constproperty
    def arc_type():
        return StoryType.SIM_BASED

    @property
    def sim_info(self):
        return self._tracker.sim_info

    @property
    def reserved_household_slots(self):
        if self._current_chapter is None:
            return 0
        return self._current_chapter.reserved_household_slots

    def get_resolver(self):
        return SingleSimResolver((self._tracker.sim_info), additional_participants=(self._get_additional_participants_for_resolver()))

    def _get_drama_node_resolver(self, actor_sim_info):
        return DoubleSimResolver(actor_sim_info, (self._tracker.sim_info), additional_participants=(self._get_additional_participants_for_resolver()))

    def load(self, arc_msg):
        super().load(arc_msg)
        if self._historical_chapters:
            services.get_story_progression_service().cache_historical_arcs_sim_id(self.sim_info.id)

    def on_zone_load(self):
        if self._historical_chapters:
            services.get_story_progression_service().cache_historical_arcs_sim_id(self.sim_info.id)


class HouseholdStoryArc(BaseStoryArc):
    INSTANCE_TUNABLES = {'starting_chapter':TunableReference(description='\n            The first chapter of this Story Arc.\n            ',
       manager=services.get_instance_manager(Types.STORY_CHAPTER),
       class_restrictions='HouseholdStoryChapter'), 
     'candidate_selection_function':TunableVariant(description='\n            The function used to figure out the actual candidates to run the arcs on.\n            ',
       household_and_livable_lot_from_demographic_list=SelectHouseholdCandidateMatchingLotFromDemographicListFunction.TunableFactory(),
       household_based_on_culling=SelectHouseholdWithHomeCandidateFromDemographicListBasedOnCullingScoreFunction.TunableFactory(),
       default='household_based_on_culling')}

    @classproperty
    def _initial_story_chapter(cls):
        return cls.starting_chapter

    @constproperty
    def _actor_participant():
        return ParticipantType.ActorHousehold

    @constproperty
    def arc_type():
        return StoryType.HOUSEHOLD_BASED

    @property
    def household(self):
        return self._tracker.household

    def get_resolver(self):
        return HouseholdResolver((self._tracker.household), additional_participants=(self._get_additional_participants_for_resolver()))

    def _get_drama_node_resolver(self, actor_sim_info):
        return SingleSimAndHouseholdResolver(actor_sim_info, (self._tracker.household), additional_participants=(self._get_additional_participants_for_resolver()))

    def load(self, arc_msg):
        super().load(arc_msg)
        if self._historical_chapters:
            services.get_story_progression_service().cache_historical_arcs_household_id(self.household.id)

    def on_zone_load(self):
        if self._historical_chapters:
            services.get_story_progression_service().cache_historical_arcs_household_id(self.household.id)