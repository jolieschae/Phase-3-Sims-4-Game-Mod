# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\base\cheat_interaction.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 6951 bytes
from date_and_time import create_time_span
from distributor.shared_messages import IconInfoData
from interactions.aop import AffordanceObjectPair
from interactions.base.immediate_interaction import ImmediateSuperInteraction
from interactions.base.picker_interaction import PickerSuperInteraction
from interactions.interaction_finisher import FinishingType
from scheduler import AlarmData
from sims4.tuning.tunable import Tunable
from sims4.utils import flexmethod
from singletons import DEFAULT
from situations.service_npcs.service_npc_manager import ServiceNpcSituationCreationParams
from statistics.skill import Skill
from ui.ui_dialog_generic import UiDialogTextInputOkCancel
from ui.ui_dialog_picker import ObjectPickerRow
import services, sims4
TEXT_INPUT_SKILL_LEVEL = 'skill_level'

class CheatSetSkillSuperInteraction(PickerSuperInteraction):
    INSTANCE_TUNABLES = {'skill_level_dialog':UiDialogTextInputOkCancel.TunableFactory(description="\n                The dialog that is displayed (and asks for the user to enter\n                the skill level).\n                \n                An additional token is passed in: the selected stat's name. \n                ",
       text_inputs=(
      TEXT_INPUT_SKILL_LEVEL,)), 
     'set_almost_level_up':Tunable(description='\n                True means this interaction will set the skill to the value\n                that almost level up the skill level passed in. False means it\n                will set the skill directly to the level',
       tunable_type=bool,
       default=False)}

    def _run_interaction_gen(self, timeline):
        self._show_picker_dialog((self.target), target_sim=(self.target))
        return True
        if False:
            yield None

    @flexmethod
    def picker_rows_gen(cls, inst, target, context, **kwargs):
        skill_manager = services.get_instance_manager(sims4.resources.Types.STATISTIC)
        for skill in skill_manager.all_skills_gen():
            if not skill.can_add(target):
                continue
            row = ObjectPickerRow(name=(skill.stat_name), icon=(skill.icon),
              row_description=(skill.skill_description(context.sim)),
              tag=skill)
            yield row

    def on_choice_selected(self, choice_tag, **kwargs):
        if choice_tag is None:
            return
        skill = choice_tag
        sim = self.target

        def on_response(level_dialog):
            if not level_dialog.accepted:
                self.cancel((FinishingType.DIALOG), cancel_reason_msg='Set Skill level dialog timed out from client.')
                return
                level = level_dialog.text_input_responses.get(TEXT_INPUT_SKILL_LEVEL)
                if not level:
                    self.cancel((FinishingType.DIALOG), cancel_reason_msg='Empty skill level returned from client.')
                    return
                try:
                    level = int(level)
                except:
                    self.cancel((FinishingType.DIALOG), cancel_reason_msg='Invalid skill level returned from client.')
                    return
                else:
                    tracker = sim.get_tracker(skill)
                    stat = tracker.get_statistic(skill, add=True)
                    if stat is None:
                        self.cancel((FinishingType.FAILED_TESTS), cancel_reason_msg='Unable to add Skill due to entitlement restriction.')
                        return
                    if self.set_almost_level_up:
                        skill_value = stat.get_skill_value_for_level(level) - 50
                        tracker.set_value(skill, skill_value)
            else:
                tracker.set_user_value(skill, level)

        dialog = self.skill_level_dialog(sim, self.get_resolver())
        dialog.show_dialog(on_response=on_response, additional_tokens=(skill.stat_name,), icon_override=IconInfoData(icon_resource=(skill.icon)))


class CheatRequestServiceNpcSuperInteraction(ImmediateSuperInteraction):

    def __init__(self, aop, context, service_tuning=None, **kwargs):
        (super().__init__)(aop, context, **kwargs)
        self._service_tuning = service_tuning

    def _run_interaction_gen(self, timeline):
        sim = self.sim
        end_time = services.time_service().sim_now + create_time_span(hours=8)
        fake_alarm_data = AlarmData(None, end_time, None, False)
        default_user_specified_data_id = self._service_tuning.get_default_user_specified_data_id()
        creation_data = ServiceNpcSituationCreationParams((sim.household), (self._service_tuning), user_specified_data_id=default_user_specified_data_id,
          is_recurring=False,
          user_specified_selections=None,
          hiring_sim_id=(sim.id))
        services.current_zone().service_npc_service._send_service_npc(None, fake_alarm_data, creation_data)
        return True
        if False:
            yield None

    @flexmethod
    def _get_name(cls, inst, target=DEFAULT, context=DEFAULT, service_tuning=None, outfit_index=None, **interaction_parameters):
        if inst is not None:
            return inst._service_tuning.display_name
        return service_tuning.display_name

    @classmethod
    def potential_interactions(cls, target, context, **kwargs):
        for service_tuning in services.get_instance_manager(sims4.resources.Types.SERVICE_NPC).types.values():
            yield AffordanceObjectPair(cls, target, cls, None, service_tuning=service_tuning, **kwargs)