# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\clubs\club_sim_picker_dialog.py
# Compiled at: 2015-07-21 19:47:59
# Size of source mod 2**32: 1454 bytes
from ui.ui_dialog_picker import UiSimPicker, SimPickerRow, ObjectPickerType

class ClubSimPickerRow(SimPickerRow):

    def __init__(self, *args, failed_criteria=None, **kwargs):
        (super().__init__)(args, is_enable=not failed_criteria, **kwargs)
        self.failed_criteria = failed_criteria

    def populate_protocol_buffer(self, sim_row_data):
        super().populate_protocol_buffer(sim_row_data)
        if self.failed_criteria is not None:
            sim_row_data.failed_criteria.extend(self.failed_criteria)


class UiClubSimPicker(UiSimPicker):

    def __init__(self, *args, club_building_info=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.picker_type = ObjectPickerType.SIM_CLUB
        self._club_building_info = club_building_info

    def _validate_row(self, row):
        return isinstance(row, ClubSimPickerRow)

    def _build_customize_picker(self, picker_data):
        if self._club_building_info is not None:
            picker_data.sim_picker_data.club_building_info = self._club_building_info
        return super()._build_customize_picker(picker_data)