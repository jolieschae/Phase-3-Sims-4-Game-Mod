# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\lot_decoration\lot_decoration_picker.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 5808 bytes
from distributor.rollback import ProtocolBufferRollback
from distributor.shared_messages import build_icon_info_msg, IconInfoData
from interactions import ParticipantType
from interactions.base.picker_interaction import PickerSuperInteraction
from interactions.utils import display_name
from interactions.utils.tunable import TunableContinuation
from interactions.utils.tunable_icon import TunableIconFactory
from lot_decoration.lot_decoration_enums import DecorationLocation, DecorationPickerCategory
from sims4.localization import LocalizationHelperTuning, TunableLocalizedString
from sims4.resources import Types
from sims4.tuning.tunable import TunableEnumSet, TunableEnumEntry, TunableList, TunableTuple
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
from ui.ui_dialog_picker import ObjectPickerRow, UiObjectPicker
import services

class UiLotDecorationPicker(UiObjectPicker):
    FACTORY_TUNABLES = {'filter_categories': TunableList(description='\n            The categories to display in the dropdown for this picker.\n            ',
                            tunable=TunableTuple(decoration_category=TunableEnumEntry(tunable_type=DecorationPickerCategory,
                            default=(DecorationPickerCategory.ALL)),
                            icon=(TunableIconFactory()),
                            category_name=(TunableLocalizedString())))}

    def _build_customize_picker(self, picker_data):
        with ProtocolBufferRollback(picker_data.filter_data) as (filter_data_list):
            for category in self.filter_categories:
                with ProtocolBufferRollback(filter_data_list.filter_data) as (category_data):
                    category_data.tag_type = category.decoration_category
                    build_icon_info_msg(category.icon(None), None, category_data.icon_info)
                    category_data.description = category.category_name

            filter_data_list.use_dropdown_filter = self.use_dropdown_filter
        picker_data.object_picker_data.num_columns = self.num_columns
        for row in self.picker_rows:
            row_data = picker_data.object_picker_data.row_data.add()
            row.populate_protocol_buffer(row_data)


class LotDecorationPicker(PickerSuperInteraction):
    INSTANCE_TUNABLES = {'by_location':TunableEnumSet(description='\n            Filter for decorations available in any of these locations.\n            \n            If empty, this just returns all decorations.\n            ',
       enum_type=DecorationLocation), 
     'picker_dialog':UiLotDecorationPicker.TunableFactory(description='\n            The item picker dialog.\n            ',
       tuning_group=GroupNames.PICKERTUNING), 
     'actor_continuation':TunableContinuation(description='\n            If specified, a continuation to push on the actor when a picker \n            selection has been made.\n            ',
       locked_args={'actor': ParticipantType.Actor},
       tuning_group=GroupNames.PICKERTUNING)}

    def _run_interaction_gen(self, timeline):
        self._show_picker_dialog(self.sim)
        return True
        if False:
            yield None

    @classmethod
    def _items_gen(cls):
        if cls.by_location:
            for decoration in services.get_instance_manager(Types.LOT_DECORATION).types.values():
                if decoration.available_locations & cls.by_location:
                    yield decoration

        else:
            yield from services.get_instance_manager(Types.LOT_DECORATION).types.values()

    @flexmethod
    def picker_rows_gen(cls, inst, target, context, **kwargs):
        for item in cls._items_gen():
            display_name = LocalizationHelperTuning.get_raw_text(str(item.__name__)) if item.display_name is None else item.display_name
            row_tooltip = None if item.display_tooltip is None else (lambda *_, tooltip=item.display_tooltip: tooltip)
            row = ObjectPickerRow(name=display_name, icon=(item.display_icon),
              def_id=(item.decoration_resource),
              row_tooltip=row_tooltip,
              row_description=(item.display_description),
              tag_list=(item.picker_categories),
              tag=item,
              use_catalog_product_thumbnails=False)
            yield row

    def on_choice_selected(self, choice, **kwargs):
        if choice is not None:
            (self.push_tunable_continuation)(self.actor_continuation, picked_item_ids=(choice.guid64,), **kwargs)