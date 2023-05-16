# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_actions\story_progression_action_family.py
# Compiled at: 2022-06-13 18:18:17
# Size of source mod 2**32: 9896 bytes
import services
from interactions import ParticipantTypeSavedStoryProgressionSim
from sims.pregnancy.pregnancy_tracker import PregnancyTracker
from sims.sim_spawner import SimSpawner
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, OptionalTunable, TunableEnumEntry, Tunable
from story_progression.story_progression_actions.story_progression_action_base import BaseSimStoryProgressionAction
from story_progression.story_progression_result import StoryProgressionResult, StoryProgressionResultType

class MakePregnantStoryProgressionAction(BaseSimStoryProgressionAction):
    FACTORY_TUNABLES = {'pregnancy_partner_filter':TunableReference(description='\n            The filter that we will use to find the pregnancy partner.\n            ',
       manager=services.get_instance_manager(Types.SIM_FILTER)), 
     'store_pregnancy_partner_participant':OptionalTunable(description='\n            If enabled we will store off pregnancy partner for future\n            use in tokens or other resolvers.\n            ',
       tunable=TunableEnumEntry(tunable_type=ParticipantTypeSavedStoryProgressionSim,
       default=(ParticipantTypeSavedStoryProgressionSim.SavedStoryProgressionSim1)))}
    PREGNANCY_PARTNER_TOKEN = 'pregnancy_partner'
    RESERVING_PREGNANCY_SLOT_TOKEN = 'reserving_pregnancy_slot'

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._reserving_slot = False
        self._pregnancy_partner_id = None

    @property
    def reserved_household_slots(self):
        if self._reserving_slot:
            return 1
        return 0

    def setup_story_progression_action(self, **kwargs):
        if self._owner_arc.sim_info.household.free_slot_count <= 0:
            return StoryProgressionResult(StoryProgressionResultType.FAILED_TESTS, 'Failed to setup the pregnancy story progression action on {} as the household is full.', self._owner_arc.sim_info)
        else:
            self._reserving_slot = True
            blacklist = {sim_info.id for sim_info in services.active_household()}
            blacklist.add(self._owner_arc.sim_info.id)
            results = services.sim_filter_service().submit_filter((self.pregnancy_partner_filter), None,
              requesting_sim_info=(self._owner_arc.sim_info),
              blacklist_sim_ids=blacklist,
              allow_yielding=False)
            self._reserving_slot = results or False
            return StoryProgressionResult(StoryProgressionResultType.FAILED_TESTS, 'Failed to setup the pregnancy story progression action on {} as no pregnancy partner could be found.', self._owner_arc.sim_info)
        self._pregnancy_partner_id = results[0].sim_info.id
        return StoryProgressionResult(StoryProgressionResultType.SUCCESS)

    def _run_story_progression_action(self):
        self._reserving_slot = False
        pregnancy_partner = services.sim_info_manager().get(self._pregnancy_partner_id)
        if pregnancy_partner is None:
            return StoryProgressionResult(StoryProgressionResultType.FAILED_TESTS, 'Failed to perfrom the pregnancy story progression action on {} as no pregnancy partner is None.', self._owner_arc.sim_info)
        self._owner_arc.sim_info.pregnancy_tracker.start_pregnancy(self._owner_arc.sim_info, pregnancy_partner)
        return StoryProgressionResult(StoryProgressionResultType.SUCCESS_MAKE_HISTORICAL)

    def _save_participants(self):
        super()._save_participants()
        if self._pregnancy_partner_id is None or self.store_pregnancy_partner_participant is None:
            return
        self._owner_arc.store_participant(self.store_pregnancy_partner_participant, self._pregnancy_partner_id)

    def save_custom_data(self, writer):
        if self._pregnancy_partner_id is not None:
            writer.write_uint64(self.PREGNANCY_PARTNER_TOKEN, self._pregnancy_partner_id)
        writer.write_bool(self.RESERVING_PREGNANCY_SLOT_TOKEN, self._reserving_slot)

    def load_custom_data(self, reader):
        self._pregnancy_partner_id = reader.read_uint64(self.PREGNANCY_PARTNER_TOKEN, None)
        self._reserving_slot = reader.read_bool(self.RESERVING_PREGNANCY_SLOT_TOKEN, False)

    def get_gsi_data(self):
        sim_info = services.sim_info_manager().get(self._pregnancy_partner_id)
        if sim_info is not None:
            pregnancy_partner = sim_info.full_name
        else:
            pregnancy_partner = str(self._pregnancy_partner_id)
        return [
         {'field':'Pregnancy Partner',  'data':pregnancy_partner}]


class AddFamilyMemberStoryProgressionAction(BaseSimStoryProgressionAction):
    FACTORY_TUNABLES = {'template':TunableReference(description='\n            The template we will use to create the Sim being added to the family.\n            ',
       manager=services.get_instance_manager(Types.SIM_TEMPLATE),
       class_restrictions=('TunableSimTemplate', )), 
     'add_adoption_relationships':Tunable(description='\n            If checked then we will add default adoption relationships like the Sim is normally getting adopted as\n            a child.\n            ',
       tunable_type=bool,
       default=True), 
     'use_adoptors_last_name':Tunable(description='\n            If checked then we will change the last name of the created Sim to the last name of the Sim adopting them.\n            ',
       tunable_type=bool,
       default=True), 
     'store_new_family_member_participant':OptionalTunable(description='\n            If enabled we will store off the new family member for future\n            use in tokens or other resolvers.\n            ',
       tunable=TunableEnumEntry(description='\n                The sim participant to save it into.\n                ',
       tunable_type=ParticipantTypeSavedStoryProgressionSim,
       default=(ParticipantTypeSavedStoryProgressionSim.SavedStoryProgressionSim1)))}
    RESERVING_FAMILY_MEMBER_SLOT_TOKEN = 'reserving_family_member_slot'
    NEW_FAMILY_MEMBER_ID = 'new_family_member_id'

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._reserving_slot = False
        self._new_family_member_id = None

    @property
    def reserved_household_slots(self):
        if self._reserving_slot:
            return 1
        return 0

    def setup_story_progression_action(self, **kwargs):
        if self._owner_arc.sim_info.household.free_slot_count <= 0:
            return StoryProgressionResult(StoryProgressionResultType.FAILED_TESTS, 'Failed to setup the add family member action on {} as the household is full.', self._owner_arc.sim_info)
        self._reserving_slot = True
        return StoryProgressionResult(StoryProgressionResultType.SUCCESS)

    def _run_story_progression_action(self):
        self._reserving_slot = False
        household = self._owner_arc.sim_info.household
        sim_creator = self.template.sim_creator
        if self.use_adoptors_last_name:
            sim_creator.last_name = self._owner_arc.sim_info.last_name
        sim_info_list, _ = SimSpawner.create_sim_infos((sim_creator,), sim_name_type=(sim_creator.sim_name_type),
          household=household)
        sim_info = sim_info_list[0]
        self.template.add_template_data_to_sim(sim_info, sim_creator=sim_creator)
        sim_info.inject_into_inactive_zone(household.home_zone_id)
        self._new_family_member_id = sim_info.sim_id
        if self.add_adoption_relationships:
            parent_a = self._owner_arc.sim_info
            parent_b = services.sim_info_manager().get(parent_a.spouse_sim_id)
            PregnancyTracker.initialize_sim_info(sim_info, parent_a, parent_b)
        return StoryProgressionResult(StoryProgressionResultType.SUCCESS_MAKE_HISTORICAL)

    def _save_participants(self):
        super()._save_participants()
        if self._new_family_member_id is None or self.store_new_family_member_participant is None:
            return
        self._owner_arc.store_participant(self.store_new_family_member_participant, self._new_family_member_id)

    def save_custom_data(self, writer):
        writer.write_bool(self.RESERVING_FAMILY_MEMBER_SLOT_TOKEN, self._reserving_slot)
        if self._new_family_member_id is not None:
            writer.write_uint64(self.NEW_FAMILY_MEMBER_ID, self._new_family_member_id)

    def load_custom_data(self, reader):
        self._reserving_slot = reader.read_bool(self.RESERVING_FAMILY_MEMBER_SLOT_TOKEN, False)
        self._new_family_member_id = reader.read_bool(self.NEW_FAMILY_MEMBER_ID, None)