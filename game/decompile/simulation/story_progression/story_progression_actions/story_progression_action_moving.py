# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_actions\story_progression_action_moving.py
# Compiled at: 2022-03-10 20:35:10
# Size of source mod 2**32: 7124 bytes
import services
from interactions import ParticipantTypeSavedStoryProgressionZone
from objects import ALL_HIDDEN_REASONS
from sims4.random import weighted_random_item
from sims4.resources import Types
from sims4.tuning.tunable import TunableEnumEntry, OptionalTunable
from story_progression.story_progression_actions.story_progression_action_base import BaseHouseholdStoryProgressionAction
from story_progression.story_progression_lot_selection import StoryProgressionLotSelection
from story_progression.story_progression_result import StoryProgressionResult, StoryProgressionResultType
from venues.venue_enums import VenueTypes

class MoveInStoryProgressionAction(BaseHouseholdStoryProgressionAction):
    FACTORY_TUNABLES = {'store_zone_participant': OptionalTunable(description='\n            If enabled we will store off the zone id participant for future\n            use in tokens or other resolvers.\n            ',
                                 tunable=TunableEnumEntry(description='\n                The zone participant to save it into.\n                ',
                                 tunable_type=ParticipantTypeSavedStoryProgressionZone,
                                 default=(ParticipantTypeSavedStoryProgressionZone.SavedStoryProgressionZone1)))}
    ZONE_ID_TOKEN = 'zone_id_to_move_into'

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._zone_id_to_move_into = None

    @property
    def target_zone_id(self):
        return self._zone_id_to_move_into

    def setup_story_progression_action(self, zone_candidate=None, **kwargs):
        if zone_candidate is None:
            possible_zones = []
            persistence_service = services.get_persistence_service()
            venue_manager = services.get_instance_manager(Types.VENUE)
            household_manager = services.household_manager()
            for neighborhood_proto in persistence_service.get_neighborhoods_proto_buf_gen():
                for lot_owner_info in neighborhood_proto.lots:
                    for lot_owner in lot_owner_info.lot_owner:
                        if lot_owner.household_id > 0:
                            household = household_manager.get(lot_owner.household_id)
                            if household is None:
                                continue
                            break
                    else:
                        venue_tuning = venue_manager.get(lot_owner_info.venue_key)
                        if venue_tuning is not None:
                            if venue_tuning.venue_type != VenueTypes.RESIDENTIAL:
                                continue
                        if lot_owner_info.lot_template_id == 0:
                            continue
                        templates_and_bed_data = StoryProgressionLotSelection.get_household_templates_and_bed_data(lot_owner_info.zone_instance_id)
                        total_beds, lot_has_double_bed, lot_has_kid_bed = templates_and_bed_data
                        weight = StoryProgressionLotSelection.get_household_weight(self.affected_household, total_beds, lot_has_double_bed, lot_has_kid_bed)
                        if weight > 0:
                            possible_zones.append((weight, lot_owner_info.zone_instance_id))

            if not possible_zones:
                StoryProgressionResult(StoryProgressionResultType.FAILED_TESTS, 'Failed to setup story progression Move In since there is no valid zone for that Sim to move into.')
            zone_candidate = weighted_random_item(possible_zones)
        self._zone_id_to_move_into = zone_candidate
        return StoryProgressionResult(StoryProgressionResultType.SUCCESS)

    def _run_story_progression_action(self):
        zone_data_proto = services.get_persistence_service().get_zone_proto_buff(self._zone_id_to_move_into)
        if zone_data_proto is not None:
            if zone_data_proto.household_id != 0:
                return StoryProgressionResult(StoryProgressionResultType.FAILED_ACTION, 'Zone Id {} already has a household moved in so the action cannot be completed.', self._zone_id_to_move_into)
        self.affected_household.set_household_lot_ownership(zone_id=(self._zone_id_to_move_into))
        return StoryProgressionResult(StoryProgressionResultType.SUCCESS_MAKE_HISTORICAL)

    def _save_participants(self):
        super()._save_participants()
        if self._zone_id_to_move_into is None or self.store_zone_participant is None:
            return
        self._owner_arc.store_participant(self.store_zone_participant, self._zone_id_to_move_into)

    def get_gsi_data(self):
        return [
         {'field':'Zone Id To Move Into', 
          'data':str(self._zone_id_to_move_into)}]

    def save_custom_data(self, writer):
        if self._zone_id_to_move_into is not None:
            writer.write_uint64(self.ZONE_ID_TOKEN, self._zone_id_to_move_into)

    def load_custom_data(self, reader):
        self._zone_id_to_move_into = reader.read_uint64(self.ZONE_ID_TOKEN, None)


class MoveOutStoryProgressionAction(BaseHouseholdStoryProgressionAction):
    ZONE_ID_TOKEN = 'zone_id_moved_out_of'

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._zone_id_moved_out_of = None

    @property
    def target_zone_id(self):
        return self._zone_id_moved_out_of

    def _run_story_progression_action(self):
        self._zone_id_moved_out_of = self.affected_household.home_zone_id
        household_manager = services.household_manager()
        household_manager.add_pending_transfer(self.affected_household.id, True, None)
        household_manager.move_household_out_of_lot(self.affected_household, True, 0)
        return StoryProgressionResult(StoryProgressionResultType.SUCCESS_MAKE_HISTORICAL)

    def save_custom_data(self, writer):
        if self._zone_id_moved_out_of is not None:
            writer.write_uint64(self.ZONE_ID_TOKEN, self._zone_id_moved_out_of)

    def load_custom_data(self, reader):
        self._zone_id_moved_out_of = reader.read_uint64(self.ZONE_ID_TOKEN, None)