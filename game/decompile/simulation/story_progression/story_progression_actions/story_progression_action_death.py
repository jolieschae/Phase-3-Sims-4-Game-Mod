# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_actions\story_progression_action_death.py
# Compiled at: 2022-03-10 20:35:10
# Size of source mod 2**32: 5776 bytes
import services, sims4
from event_testing.resolver import SingleSimResolver
from interactions import ParticipantTypeSavedStoryProgressionString
from interactions.utils.death import DeathType
from sims4.common import Pack, is_available_pack
from sims4.random import weighted_random_item
from sims4.tuning.tunable import TunableList, TunableTuple, TunableEnumEntry, OptionalTunable
from story_progression.story_progression_actions.story_progression_action_base import BaseSimStoryProgressionAction
from story_progression.story_progression_result import StoryProgressionResult, StoryProgressionResultType
from story_progression.story_progression_tuning import StoryProgTunables
from tunable_multiplier import TunableMultiplier
logger = sims4.log.Logger('StoryProgressionActionDeath', default_owner='bnguyen')

class DeathStoryProgressionAction(BaseSimStoryProgressionAction):
    FACTORY_TUNABLES = {'death_types':TunableList(description='\n            A list of death types and the weight of it being chosen for the\n            death of this Sim.\n            ',
       tunable=TunableTuple(description='\n                A collection of data for the death of a Sim.\n                ',
       weight=TunableMultiplier.TunableFactory(description='\n                    The weight that this death type will be chosen.\n                    '),
       additional_pack_requirement=OptionalTunable(description='\n                    If enabled then this death type requires an additional pack\n                    installed in order for the death to take place.\n                    ',
       tunable=TunableEnumEntry(description='\n                        The content associated with a given death type.  The\n                        death type will not be chosen unless that content is\n                        installed.\n                        ',
       tunable_type=Pack,
       default=(Pack.BASE_GAME),
       invalid_enums=(
      Pack.BASE_GAME,))),
       death_type=TunableEnumEntry(description='\n                    The death type that will be used to kill the Sim.\n                    ',
       tunable_type=DeathType,
       default=(DeathType.NONE),
       invalid_enums=(
      DeathType.NONE,)))), 
     'store_death_type_discovery_string_participant':OptionalTunable(description='\n            If enabled we will store off the death type string for future\n            use in tokens or other resolvers.\n            ',
       tunable=TunableEnumEntry(tunable_type=ParticipantTypeSavedStoryProgressionString,
       default=(ParticipantTypeSavedStoryProgressionString.SavedStoryProgressionString1)))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._death_type = None
        self._affected_household = None

    @property
    def affected_household(self):
        return self._affected_household

    def setup_story_progression_action(self, **kwargs):
        if self._owner_arc.sim_info.is_death_disabled():
            return StoryProgressionResult(StoryProgressionResultType.FAILED_TESTS, 'Cannot kill Sim that is unkillable.')
        return StoryProgressionResult(StoryProgressionResultType.SUCCESS)

    def _run_story_progression_action(self):
        possible_death_types = []
        if self._owner_arc.sim_info.is_death_disabled():
            return StoryProgressionResult(StoryProgressionResultType.FAILED_TESTS, 'Cannot kill Sim that is unkillable.')
        resolver = SingleSimResolver(self._owner_arc.sim_info)
        for death_type_info in self.death_types:
            if death_type_info.additional_pack_requirement is not None:
                if not is_available_pack(death_type_info.additional_pack_requirement):
                    continue
            weight = death_type_info.weight.get_multiplier(resolver)
            if weight > 0:
                possible_death_types.append((weight, death_type_info.death_type))

        self._death_type = weighted_random_item(possible_death_types)
        sim_info = self._owner_arc.sim_info
        self._affected_household = sim_info.household
        sim_info.death_tracker.set_death_type((self._death_type), is_off_lot_death=True)
        self._affected_household.handle_adultless_household()
        return StoryProgressionResult(StoryProgressionResultType.SUCCESS_MAKE_HISTORICAL)

    def _save_participants(self):
        super()._save_participants()
        if self._death_type is None or self.store_death_type_discovery_string_participant is None:
            return
        string_map = StoryProgTunables.HISTORY.death_type_discovery_string_map
        string = string_map.get(self._death_type)
        if string is None:
            logger.warn('Death type {0} not tuned in story progression death type discovery string map, using default string', self._death_type)
            string = string_map.get(DeathType.NONE)
        if string is not None:
            self._owner_arc.store_participant(self.store_death_type_discovery_string_participant, string())

    def get_gsi_data(self):
        return [
         {'field':'Death Type', 
          'data':str(self._death_type)}]