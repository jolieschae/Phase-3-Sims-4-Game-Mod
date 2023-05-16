# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\change_sim_name_interaction.py
# Compiled at: 2021-02-02 20:26:49
# Size of source mod 2**32: 2012 bytes
from event_testing.resolver import DoubleSimResolver
from interactions.base.immediate_interaction import ImmediateSuperInteraction
from sims4.localization import LocalizationHelperTuning
from ui.ui_dialog_generic import UiDialogTextInputOkCancel
TEXT_INPUT_FIRSTNAME = 'first_name'
TEXT_INPUT_LASTNAME = 'last_name'

class ChangeSimNameInteraction(ImmediateSuperInteraction):
    INSTANCE_TUNABLES = {'rename_dialog': UiDialogTextInputOkCancel.TunableFactory(description='\n            The dialog to select a new Name for the Sim.\n            ',
                        text_inputs=(
                       TEXT_INPUT_FIRSTNAME, TEXT_INPUT_LASTNAME))}

    def _run_interaction_gen(self, timeline):
        target_sim = self.target
        if not target_sim.is_sim:
            return True
        target_sim_info = target_sim.sim_info

        def on_response(dialog_response):
            if not dialog_response.accepted:
                return
            first_name = dialog_response.text_input_responses.get(TEXT_INPUT_FIRSTNAME)
            last_name = dialog_response.text_input_responses.get(TEXT_INPUT_LASTNAME)
            target_sim_info.first_name = first_name
            target_sim_info.last_name = last_name

        text_input_overrides = {TEXT_INPUT_FIRSTNAME: lambda *_, **__: LocalizationHelperTuning.get_raw_text(target_sim_info.first_name), 
         TEXT_INPUT_LASTNAME: lambda *_, **__: LocalizationHelperTuning.get_raw_text(target_sim_info.last_name)}
        dialog = self.rename_dialog(target_sim_info, DoubleSimResolver(self.sim.sim_info, target_sim_info))
        dialog.show_dialog(on_response=on_response, text_input_overrides=text_input_overrides)
        return True
        if False:
            yield None