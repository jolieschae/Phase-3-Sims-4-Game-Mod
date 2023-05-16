# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\base\state_picker_interaction.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 2458 bytes
from interactions.base.picker_interaction import PickerSuperInteraction
from objects.components.state_references import TunableStateTypeReference
from sims4.localization import LocalizationHelperTuning
from sims4.utils import flexmethod
from ui.ui_dialog_picker import ObjectPickerRow

class StatePickerSuperInteraction(PickerSuperInteraction):
    INSTANCE_TUNABLES = {'state': TunableStateTypeReference(description='\n            The state type used to populate the picker.\n            ')}

    @classmethod
    def _get_valid_state_values_gen(cls):
        for state_value in cls.state.values:
            if state_value.display_name is not None:
                yield state_value

    def on_choice_selected(self, state_value, **kwargs):
        if state_value is None:
            return
        self.target.set_state(self.state, state_value)

    @flexmethod
    def picker_rows_gen(cls, inst, target, context, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        for state_value in inst_or_cls._get_valid_state_values_gen():
            if state_value._display_data is not None:
                state_name = state_value.display_name or LocalizationHelperTuning.get_raw_text(state_value.__name__)
                row_tooltip = None if state_value.display_description is None else (lambda *_, tooltip=state_value.display_description: tooltip)
                yield ObjectPickerRow(name=state_name, row_description=(state_value.display_description), icon=(state_value.display_icon),
                  tag=state_value,
                  row_tooltip=row_tooltip)

    def _run_interaction_gen(self, timeline):
        self._show_picker_dialog(self.sim)
        return True
        if False:
            yield None