# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\sim_dialogs.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 13360 bytes
from protocolbuffers import Dialog_pb2
from protocolbuffers.DistributorOps_pb2 import Operation
from distributor.ops import GenericProtocolBufferOp
from distributor.system import Distributor
from interactions import ParticipantTypeSingleSim, ParticipantTypeSingle
from sims.sim_info_types import Gender
from sims4.localization import TunableLocalizedStringFactory
from sims4.resources import Types
from sims4.tuning.tunable import OptionalTunable, TunableList, TunableReference, TunableEnumEntry, TunableTuple
from ui.ui_dialog import UiDialogResponse, ButtonType, UiDialogStyle
from ui.ui_dialog_generic import UiDialogTextInput
import enum, services, sims4

class PersonalityAssignmentDialogStyle(enum.Int):
    DEFAULT = UiDialogStyle.DEFAULT
    TRAIT_REASSIGNMENT = UiDialogStyle.TRAIT_REASSIGNMENT


class SimPersonalityAssignmentDialog(UiDialogTextInput):
    FACTORY_TUNABLES = {'dialog_style':TunableEnumEntry(description='\n            The style overlay to apply to this dialog.\n            ',
       tunable_type=PersonalityAssignmentDialogStyle,
       default=PersonalityAssignmentDialogStyle.DEFAULT), 
     'secondary_title':TunableLocalizedStringFactory(description='\n                The secondary title of the dialog box.\n                ',
       allow_none=True), 
     'naming_title_text':OptionalTunable(description='\n                If enabled, this text will appear above the fields to rename\n                the sim.\n                ',
       tunable=TunableLocalizedStringFactory(description='\n                    Text that will appear above the fields to rename the sim.\n                    ')), 
     'aspirations_and_trait_assignment':OptionalTunable(description='\n                If enabled, we will show the aspiration and trait assignment\n                portion of the dialog.\n                ',
       tunable=TunableTuple(text=TunableLocalizedStringFactory(description='\n                        Text that will appear above aspiration and trait assignment.\n                        '),
       invalid_traits=TunableList(description='\n                        List of traits that are invalid to assign and will\n                        be hidden in this dialog.\n                        ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)), pack_safe=True)))), 
     'assign_participant':OptionalTunable(description='\n            The Sim to apply the changes to.  If disabled, this uses\n            the dialog owner.\n            ',
       tunable=TunableEnumEntry(tunable_type=ParticipantTypeSingleSim,
       default=(ParticipantTypeSingle.Actor)))}
    DIALOG_MSG_TYPE = Operation.MSG_SIM_PERSONALITY_ASSIGNMENT

    def __init__(self, *args, assignment_sim_info=None, assign_participant=None, **kwargs):
        (super().__init__)(args, assign_participant=None, **kwargs)
        if assignment_sim_info is None:
            self._assignment_sim_info = None
            if assign_participant is not None:
                if self._resolver is not None:
                    sim = self._resolver.get_participant(assign_participant)
                    if sim is not None:
                        self._assignment_sim_info = sim.sim_info
            if self._assignment_sim_info is None:
                self._assignment_sim_info = self.owner.sim_info
        else:
            self._assignment_sim_info = assignment_sim_info

    def get_text_input_reference_sim(self):
        return self._assignment_sim_info

    def build_msg(self, additional_tokens=(), trait_overrides_for_baby=None, gender_overrides_for_baby=None, previous_skills=None, previous_trait_guid=None, from_age_up=False, life_skill_trait_ids=None, age_up_reward_traits=None, age_up_reward_trait_text=None, **kwargs):
        msg = Dialog_pb2.SimPersonalityAssignmentDialog()
        msg.sim_id = self._assignment_sim_info.id
        dialog_msg = (super().build_msg)(additional_tokens=additional_tokens, **kwargs)
        msg.dialog = dialog_msg
        msg.secondary_title = (self._build_localized_string_msg)(self.secondary_title, *additional_tokens)
        msg.age_description = (self._build_localized_string_msg)(self.text, *additional_tokens)
        if self.naming_title_text is not None:
            msg.naming_title_text = (self._build_localized_string_msg)(self.naming_title_text, *additional_tokens)
        elif gender_overrides_for_baby is None:
            gender = self._assignment_sim_info.gender
        else:
            gender = gender_overrides_for_baby
        msg.is_female = gender == Gender.FEMALE
        if from_age_up:
            if age_up_reward_traits:
                for trait in age_up_reward_traits:
                    if self._assignment_sim_info.has_trait(trait):
                        msg.reward_trait_id = trait.guid64
                        if age_up_reward_trait_text is not None:
                            msg.age_up_reward_trait_text = (self._build_localized_string_msg)(age_up_reward_trait_text, *additional_tokens)
                        break

            if previous_trait_guid is not None:
                msg.replace_trait_id = previous_trait_guid
            if previous_skills is not None:
                for previous_skill, previous_skill_level in previous_skills.items():
                    if previous_skill.age_up_skill_transition_data.new_skill is not None:
                        msg.current_skill_ids.append(previous_skill.age_up_skill_transition_data.new_skill.guid64)
                        msg.previous_skill_ids.append(previous_skill.guid64)
                        msg.previous_skill_levels.append(previous_skill_level)

            if self.aspirations_and_trait_assignment is not None:
                msg.aspirations_and_trait_assignment_text = (self._build_localized_string_msg)(self.aspirations_and_trait_assignment.text, *additional_tokens)
                if trait_overrides_for_baby is None:
                    empty_slots = self._assignment_sim_info.trait_tracker.empty_slot_number
                    current_personality_traits = self._assignment_sim_info.trait_tracker.personality_traits
                else:
                    empty_slots = 0
                    current_personality_traits = trait_overrides_for_baby
                msg.available_trait_slots = empty_slots
                cas_personality_trait_count = self._assignment_sim_info.get_aging_data().get_cas_personality_trait_count(self._assignment_sim_info.age)
                for trait_index in range(min(cas_personality_trait_count, len(current_personality_traits))):
                    current_personality_trait = current_personality_traits[trait_index]
                    msg.current_personality_trait_ids.append(current_personality_trait.guid64)

                invalid_traits = self.aspirations_and_trait_assignment.invalid_traits
                if self.dialog_style == PersonalityAssignmentDialogStyle.TRAIT_REASSIGNMENT:
                    self._populate_valid_personality_traits(msg, invalid_traits=invalid_traits)
                    self._populate_current_aspiration(msg)
                    msg.available_trait_slots = self._assignment_sim_info.trait_tracker.equip_slot_number
        else:
            if empty_slots != 0:
                self._populate_valid_personality_traits(msg, traits_to_test_for_conflict=current_personality_traits, invalid_traits=invalid_traits)
            if not self._assignment_sim_info.is_child:
                if self._assignment_sim_info.is_teen or self._assignment_sim_info.is_young_adult:
                    aspiration_track_manager = services.get_instance_manager(sims4.resources.Types.ASPIRATION_TRACK)
                    aspiration_tracker = self._assignment_sim_info.aspiration_tracker
                    for aspiration_track in aspiration_track_manager.types.values():
                        if aspiration_tracker.is_aspiration_track_visible(aspiration_track) and aspiration_track.is_valid_for_sim(self._assignment_sim_info):
                            msg.available_aspiration_ids.append(aspiration_track.guid64)

            else:
                self._populate_current_aspiration(msg)
        if life_skill_trait_ids is not None:
            msg.unlocked_trait_ids.extend(life_skill_trait_ids)
        return msg

    def _populate_current_aspiration(self, msg):
        primary_aspiration = self._assignment_sim_info.primary_aspiration
        if primary_aspiration is not None:
            msg.current_aspiration_id = primary_aspiration.guid64
            primary_aspiration_trait = primary_aspiration.primary_trait
            if primary_aspiration_trait is not None:
                msg.current_aspiration_trait_id = primary_aspiration_trait.guid64

    def _populate_valid_personality_traits(self, msg, traits_to_test_for_conflict=(), invalid_traits=()):
        for trait in services.get_instance_manager(Types.TRAIT).types.values():
            if trait in invalid_traits:
                continue
            if not trait.is_personality_trait:
                continue
            if not trait.is_valid_trait(self._assignment_sim_info):
                continue
            if not any((t.guid64 == trait.guid64 or t.is_conflicting(trait) for t in traits_to_test_for_conflict)):
                msg.available_personality_trait_ids.append(trait.guid64)

    def distribute_dialog(self, dialog_type, dialog_msg, **kwargs):
        distributor = Distributor.instance()
        personality_assignement_op = GenericProtocolBufferOp(dialog_type, dialog_msg)
        distributor.add_op(self.owner, personality_assignement_op)

    @property
    def responses(self):
        return (
         UiDialogResponse(dialog_response_id=(ButtonType.DIALOG_RESPONSE_OK), ui_request=(UiDialogResponse.UiDialogUiRequest.NO_REQUEST)),)