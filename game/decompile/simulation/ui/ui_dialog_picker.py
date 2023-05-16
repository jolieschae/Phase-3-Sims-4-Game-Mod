# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\ui\ui_dialog_picker.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 84646 bytes
import math
from protocolbuffers import Dialog_pb2, Consts_pb2, UI_pb2
from distributor.shared_messages import build_icon_info_msg, IconInfoData, create_icon_info_msg
from distributor.system import Distributor
from interactions import ParticipantTypeSingle, ParticipantTypeSingleSim
from interactions.utils.tunable_icon import TunableIconFactory
from objects.slots import SlotType
from sims.outfits.outfit_enums import OutfitCategory, REGULAR_OUTFIT_CATEGORIES
from sims4.localization import LocalizationHelperTuning, TunableLocalizedString, TunableLocalizedStringFactoryVariant, NULL_LOCALIZED_STRING_FACTORY, TunableLocalizedStringFactory
from sims4.math import MAX_INT16
from sims4.tuning.tunable import TunableEnumEntry, TunableList, OptionalTunable, Tunable, TunableResourceKey, TunableVariant, TunableTuple, HasTunableSingletonFactory, AutoFactoryInit, TunableRange, TunableReference, TunableEnumSet, TunableEnumFlags, TunableSet
from distributor.rollback import ProtocolBufferRollback
from sims4.utils import classproperty
from singletons import DEFAULT, EMPTY_SET
from snippets import define_snippet
from statistics.skill import Skill
from ui.ui_dialog import UiDialogOkCancel
from ui.ui_dialog_multi_picker import UiMultiPicker
import build_buy, distributor, enum, services, sims4.log, tag
logger = sims4.log.Logger('Dialog')

class ObjectPickerType(enum.Int, export=False):
    RECIPE = 1
    INTERACTION = 2
    SIM = 3
    OBJECT = 4
    PIE_MENU = 5
    CAREER = 6
    OUTFIT = 7
    PURCHASE = 8
    LOT = 9
    SIM_CLUB = 10
    ITEM = 11
    OBJECT_LARGE = 12
    DROPDOWN = 13
    OBJECT_SQUARE = 14
    ODD_JOBS = 15
    MISSIONS = 16
    LARGE_TEXT_FLAIR = 17
    SELL = 18
    QUESTS = 19
    PHOTO = 20
    OBJECT_TEXT = 21
    OBJECT_TEXT_ADD = 22
    FASHION_PURCHASE = 23
    CUSTOM = 99


class ObjectPickerTuningFlags(enum.IntFlags):
    NONE = 0
    RECIPE = 1
    INTERACTION = 2
    SIM = 4
    OBJECT = 8
    PIE_MENU = 16
    CAREER = 32
    OUTFIT = 64
    PURCHASE = 128
    LOT = 256
    MAP_VIEW = 512
    APARTMENT = 1024
    ITEM = 2048
    DROPDOWN = 4096
    SELL = 8192
    FASHION_PURCHASE = 16384
    ALL = RECIPE | INTERACTION | SIM | OBJECT | PIE_MENU | CAREER | OUTFIT | PURCHASE | LOT | MAP_VIEW | APARTMENT | ITEM | DROPDOWN | SELL | FASHION_PURCHASE


class RowMapType(enum.Int):
    NAME = 0
    ICON = 1
    SKILL_LEVEL = 2
    PRICE = 3
    INGREDIENTS = 4
    LOCKED_IN_CAS = 5


class ControlIdType(enum.Int):
    UNUSED = 0
    SELECTION_SEQUENCE = 1


class SimPickerCellType(enum.Int):
    DEFAULT = 0
    SITUATION = 1
    ADOPTION = 2
    SOCIAL_MEDIA = 3


ROW_MAP_NAMES = [
 "'name'", "'icon'", "'skill_level'", "'price'", "'ingredients'", "'locked_in_cas_icon_info'"]

class PickerColumn(HasTunableSingletonFactory, AutoFactoryInit):

    class ColumnType(enum.Int):
        TEXT = 1
        ICON = 2
        ICON_AND_TEXT = 3
        INGREDIENT_LIST = 4

    FACTORY_TUNABLES = {'column_type':TunableEnumEntry(description='\n            The type of column.\n            ',
       tunable_type=ColumnType,
       default=ColumnType.ICON_AND_TEXT), 
     'label':OptionalTunable(description='\n            If enabled, the text to show on the column. \n            ',
       tunable=TunableLocalizedString()), 
     'icon':OptionalTunable(description='\n            If enabled, the icon to show on the column.\n            ',
       tunable=TunableResourceKey(resource_types=(sims4.resources.CompoundTypes.IMAGE),
       default=None)), 
     'tooltip':OptionalTunable(description='\n            If enabled, the tooltip text for the column.\n            ',
       tunable=TunableLocalizedString()), 
     'width':Tunable(description='\n            The width of the column.\n            ',
       tunable_type=float,
       default=100), 
     'sortable':Tunable(description='\n            Whether or not we can sort the column.\n            ',
       tunable_type=bool,
       default=True), 
     'column_data_name':TunableEnumEntry(description='\n            The name of the data field inside the row to show in this column,\n            name/skill/price etc.\n            ',
       tunable_type=RowMapType,
       default=RowMapType.NAME), 
     'column_icon_name':TunableEnumEntry(description='\n            The name of the icon field inside the row to show in this column,\n            most likely should just be icon.\n            ',
       tunable_type=RowMapType,
       default=RowMapType.ICON)}

    def populate_protocol_buffer(self, column_data):
        column_data.type = self.column_type
        if self.column_data_name is not None:
            column_data.column_data_name = ROW_MAP_NAMES[self.column_data_name]
        if self.column_icon_name is not None:
            column_data.column_icon_name = ROW_MAP_NAMES[self.column_icon_name]
        if self.label is not None:
            column_data.label = self.label
        if self.icon is not None:
            column_data.icon.type = self.icon.type
            column_data.icon.group = self.icon.group
            column_data.icon.instance = self.icon.instance
        if self.tooltip is not None:
            column_data.tooltip = self.tooltip
        column_data.width = self.width
        column_data.sortable = self.sortable

    def __format__(self, fmt):
        dump_str = 'type: {}, label:{}, icon:{}, tooltip:{}, width:{}, sortable:{}'.format(self.column_type, self.label, self.icon, self.tooltip, self.width, self.sortable)
        return dump_str


class BasePickerRow:

    def __init__(self, option_id=None, is_enable=True, name=None, icon=None, row_description=None, row_tooltip=None, tag=None, icon_info=None, pie_menu_influence_by_active_mood=False, is_selected=False, tag_list=None, second_tag_list=None):
        self.option_id = option_id
        self.tag = tag
        self.is_enable = is_enable
        self.name = name
        self.icon = icon
        self.row_description = row_description
        self.row_tooltip = row_tooltip
        self.icon_info = icon_info
        self._pie_menu_influence_by_active_mood = pie_menu_influence_by_active_mood
        self.is_selected = is_selected
        self.tag_list = tag_list
        self.second_tag_list = second_tag_list

    def populate_protocol_buffer(self, base_row_data, name_override=DEFAULT):
        base_row_data.option_id = self.option_id
        base_row_data.is_enable = bool(self.is_enable)
        base_row_data.is_selected = bool(self.is_selected)
        if name_override is DEFAULT:
            name_override = self.name
        if name_override is not None:
            base_row_data.name = name_override
        if self.icon is not None:
            base_row_data.icon.type = self.icon.type
            base_row_data.icon.group = self.icon.group
            base_row_data.icon.instance = self.icon.instance
            if self.icon_info is None:
                build_icon_info_msg(IconInfoData(icon_resource=(self.icon)), None, base_row_data.icon_info)
        if self.icon_info is not None:
            build_icon_info_msg(self.icon_info, None, base_row_data.icon_info)
        if self.row_description is not None:
            base_row_data.description = self.row_description
        if self.row_tooltip:
            base_row_data.tooltip = self.row_tooltip()
        if self.tag_list is not None:
            base_row_data.tag_list.extend(self.tag_list)
        if self.second_tag_list is not None:
            base_row_data.second_tag_list.extend(self.second_tag_list)

    @property
    def available_as_pie_menu(self):
        return True

    @property
    def pie_menu_category(self):
        pass

    @property
    def pie_menu_influence_by_active_mood(self):
        return self._pie_menu_influence_by_active_mood

    def __repr__(self):
        return str(self.tag)

    def __format__(self, fmt):
        show_name = ''
        if self.tag is not None:
            show_name = '[{}]\t\t\t'.format(self.tag.__class__.__name__)
        dump_str = ' {}, enable:{}, '.format(show_name, self.is_enable)
        return dump_str


class RecipePickerRow(BasePickerRow):

    def __init__(self, price=0, skill_level=0, linked_recipe=None, display_name=DEFAULT, ingredients=None, price_with_ingredients=0, mtx_id=None, discounted_price=0, is_discounted=False, bucks_costs=None, locked_in_cas_icon=None, subrow_sort_id=0, group_recipe_override=None, ingredients_list=None, linked_recipe_override=None, **kwargs):
        (super().__init__)(**kwargs)
        self.price = price
        self.skill_level = skill_level
        self.linked_recipe = linked_recipe
        self.linked_option_ids = []
        self.display_name = display_name
        self.visible_as_subrow = self.tag.visible_as_subrow
        self._pie_menu_category = self.tag.base_recipe_category
        self.ingredients = ingredients
        self.price_with_ingredients = price_with_ingredients
        self.mtx_id = mtx_id
        self.discounted_price = discounted_price
        self.is_discounted = is_discounted
        self.bucks_costs = bucks_costs
        self.locked_in_cas_icon = locked_in_cas_icon
        self.subrow_sort_id = subrow_sort_id
        self.group_recipe_override = group_recipe_override
        self.ingredients_list = ingredients_list
        self.linked_recipe_override = linked_recipe_override

    def populate_protocol_buffer(self, recipe_row_data):
        super().populate_protocol_buffer(recipe_row_data.base_data)
        if self.display_name is not DEFAULT:
            recipe_row_data.serving_display_name = self.display_name
        if self.price != 0:
            price = abs(self.price)
            recipe_row_data.price = int(price)
        recipe_row_data.skill_level = int(self.skill_level)
        for linked_id in self.linked_option_ids:
            recipe_row_data.linked_option_ids.append(linked_id)

        recipe_row_data.visible_as_subrow = self.visible_as_subrow
        recipe_row_data.price_with_ingredients = self.price_with_ingredients
        if self.ingredients:
            for ingredient in self.ingredients:
                ingredient_data = recipe_row_data.ingredients.add()
                ingredient_data.ingredient_name = ingredient.ingredient_name
                ingredient_data.in_inventory = ingredient.is_in_inventory

        if self.mtx_id is not None:
            recipe_row_data.mtx_id = self.mtx_id
        recipe_row_data.discounted_price = int(self.discounted_price)
        recipe_row_data.is_discounted = self.is_discounted
        if self.bucks_costs:
            for buck_cost in self.bucks_costs:
                bucks_data = recipe_row_data.bucks_costs.add()
                bucks_data.bucks_type = buck_cost.bucks_type
                bucks_data.amount = buck_cost.amount

        if self.locked_in_cas_icon is not None:
            build_icon_info_msg(IconInfoData(icon_resource=(self.locked_in_cas_icon)), None, recipe_row_data.locked_in_cas_icon_info)
        if self.group_recipe_override is not None:
            recipe_row_data.group_override.skill_level = self.group_recipe_override.group_skill_level
            recipe_row_data.group_override.name = self.group_recipe_override.group_name()
            recipe_row_data.group_override.tooltip = self.group_recipe_override.group_tooltip()
        if self.ingredients_list is not None:
            recipe_row_data.ingredients_list = self.ingredients_list
        recipe_row_data.subrow_sort_id = self.subrow_sort_id

    @property
    def available_as_pie_menu(self):
        return self.visible_as_subrow

    @property
    def pie_menu_category(self):
        return self._pie_menu_category

    def __format__(self, fmt):
        super_dump_str = super().__format__(fmt)
        dump_str = 'RecipePickerRow({}, skill:{}, price:{}, linked rows[{}])'.format(super_dump_str, self.skill_level, self.price, len(self.linked_option_ids))
        return dump_str


class SimPickerRow(BasePickerRow):

    def __init__(self, sim_id=None, select_default=False, **kwargs):
        (super().__init__)(**kwargs)
        self.sim_id = sim_id
        self.select_default = select_default

    def populate_protocol_buffer(self, sim_row_data):
        super().populate_protocol_buffer(sim_row_data.base_data)
        if self.sim_id is not None:
            sim_row_data.sim_id = self.sim_id
            sim_row_data.select_default = self.select_default

    def __format__(self, fmt):
        dump_str = 'SimPickerRow(Sim id:{})'.format(self.sim_id)
        return dump_str


class ObjectPickerStyle(enum.Int):
    DEFAULT = 0
    NUMBERED = 1
    DELETE = 2


class ObjectPickerRow(BasePickerRow):

    def __init__(self, object_id=None, def_id=None, count=1, rarity_text=None, use_catalog_product_thumbnails=True, second_rarity_text=None, flair_icon=None, flair_name=None, object_picker_style=ObjectPickerStyle.DEFAULT, **kwargs):
        (super().__init__)(**kwargs)
        self.object_id = object_id
        self.def_id = def_id
        self.count = count
        self.rarity_text = rarity_text
        self.use_catalog_product_thumbnails = use_catalog_product_thumbnails
        self.second_rarity_text = second_rarity_text
        self.flair_icon = flair_icon
        self.flair_name = flair_name
        self.object_picker_style = object_picker_style

    def populate_protocol_buffer(self, object_row_data):
        super().populate_protocol_buffer(object_row_data.base_data)
        if self.object_id is not None:
            object_row_data.object_id = self.object_id
        if self.def_id is not None:
            object_row_data.def_id = self.def_id
        object_row_data.count = self.count
        object_row_data.object_picker_style = self.object_picker_style
        if self.rarity_text is not None:
            object_row_data.rarity_text = self.rarity_text
        if not self.use_catalog_product_thumbnails:
            object_row_data.use_catalog_product_thumbnails = False
        if self.second_rarity_text is not None:
            object_row_data.second_rarity_text = self.second_rarity_text
        if self.flair_icon is not None:
            if self.flair_name is not None:
                build_icon_info_msg(IconInfoData(icon_resource=(self.flair_icon)), self.flair_name, object_row_data.flair_icon)

    def __format__(self, fmt):
        super_dump_str = super().__format__(fmt)
        dump_str = 'ObjectPickerRow({}, object_id:{}, def_id:{})'.format(super_dump_str, self.object_id, self.def_id)
        return dump_str


class OddJobPickerRow(BasePickerRow):

    def __init__(self, customer_id=None, customer_description=None, customer_thumbnail_override=None, customer_background=None, tip_title=None, tip_text=None, tip_icon=None, customer_name=None, **kwargs):
        (super().__init__)(**kwargs)
        self.customer_id = customer_id
        self.customer_description = customer_description
        self.customer_thumbnail_override = customer_thumbnail_override
        self.customer_background = customer_background
        self.tip_title = tip_title
        self.tip_text = tip_text
        self.tip_icon = tip_icon
        self.customer_name = customer_name

    def populate_protocol_buffer(self, odd_job_picker_row, **kwargs):
        super().populate_protocol_buffer(odd_job_picker_row.base_data)
        odd_job_picker_row.customer_id = self.customer_id
        odd_job_picker_row.customer_description = self.customer_description
        odd_job_picker_row.tip_title = self.tip_title
        if self.customer_name:
            odd_job_picker_row.customer_name = self.customer_name
        if self.customer_thumbnail_override:
            build_icon_info_msg(IconInfoData(icon_resource=(self.customer_thumbnail_override)), None, odd_job_picker_row.customer_thumbnail_override)
        if self.customer_background:
            build_icon_info_msg(IconInfoData(icon_resource=(self.customer_background)), None, odd_job_picker_row.customer_background)
        build_icon_info_msg(IconInfoData(icon_resource=(self.tip_icon)), None, (odd_job_picker_row.tip_icon), desc=(self.tip_text))

    def __format__(self, fmt):
        super_dump_str = super().__format__(fmt)
        dump_str = 'OddJobPickerRow({})'.format(super_dump_str)
        return dump_str


class OutfitPickerRow(BasePickerRow):

    def __init__(self, outfit_sim_id, outfit_category, outfit_index, **kwargs):
        (super().__init__)(**kwargs)
        self._outfit_sim_id = outfit_sim_id
        self._outfit_category = outfit_category
        self._outfit_index = outfit_index

    def populate_protocol_buffer(self, outfit_row_data):
        super().populate_protocol_buffer(outfit_row_data.base_data)
        outfit_row_data.outfit_sim_id = self._outfit_sim_id
        outfit_row_data.outfit_category = self._outfit_category
        outfit_row_data.outfit_index = self._outfit_index

    def __format__(self, fmt):
        super_dump_str = super().__format__(fmt)
        dump_str = 'OutfitPickerRow({})'.format(super_dump_str)
        return dump_str


class PurchasePickerRow(BasePickerRow):

    def __init__(self, def_id=0, num_owned=0, tags=(), num_available=None, custom_price=None, fashion_trend=None, objects=EMPTY_SET, show_discount=False, icon_info_data_override=None, prediscounted_price=None, **kwargs):
        (super().__init__)(**kwargs)
        self.def_id = def_id
        self.num_owned = num_owned
        self.tags = tags
        self.num_available = num_available
        self.custom_price = custom_price
        self.fashion_trend = fashion_trend
        self.prediscounted_price = prediscounted_price
        self.objects = objects
        self.show_discount = show_discount
        self.icon_info_data_override = icon_info_data_override

    def populate_protocol_buffer(self, purchase_row_data):
        super().populate_protocol_buffer(purchase_row_data.base_data)
        purchase_row_data.def_id = self.def_id
        purchase_row_data.num_owned = self.num_owned
        purchase_row_data.tag_list.extend(self.tags)
        if self.num_available is not None:
            purchase_row_data.num_available = self.num_available
        if self.custom_price is not None:
            purchase_row_data.custom_price = self.custom_price
        if self.fashion_trend is not None:
            purchase_row_data.fashion_trend = self.fashion_trend
        if self.prediscounted_price is not None:
            purchase_row_data.prediscounted_price = self.prediscounted_price
        purchase_row_data.is_discounted = self.show_discount
        obj = next(iter(self.objects), None)
        if self.icon_info_data_override:
            build_icon_info_msg(self.icon_info_data_override, None, purchase_row_data.base_data.icon_info)
        else:
            if obj is not None:
                purchase_row_data.object_id = obj.id
                icon_info = obj.get_icon_info_data()
                build_icon_info_msg(icon_info, None, purchase_row_data.base_data.icon_info)
            else:
                if self.def_id is not None:
                    definition_tuning = services.definition_manager().get_object_tuning(self.def_id)
                    icon_override = definition_tuning.icon_override
                    if icon_override is not None:
                        icon_info = IconInfoData(icon_resource=icon_override)
                        build_icon_info_msg(icon_info, None, purchase_row_data.base_data.icon_info)

    def __format__(self, fmt):
        super_dump_str = super().__format__(fmt)
        dump_str = 'PurchasePickerRow({}, def_id: {}, num_owned: {})'.format(super_dump_str, self.def_id, self.num_owned)
        return dump_str


class LotPickerRow(BasePickerRow):

    def __init__(self, zone_data, **kwargs):
        (super().__init__)(**kwargs)
        self.zone_id = zone_data.zone_id
        self.name = zone_data.name
        self.world_id = zone_data.world_id
        self.lot_template_id = zone_data.lot_template_id
        self.lot_description_id = zone_data.lot_description_id
        venue_manager = services.get_instance_manager(sims4.resources.Types.VENUE)
        venue_tuning_id = build_buy.get_current_venue(zone_data.zone_id)
        if venue_tuning_id is not None:
            venue_tuning = venue_manager.get(venue_tuning_id)
            if venue_tuning is not None:
                self.venue_type_name = venue_tuning.display_name
        householdProto = services.get_persistence_service().get_household_proto_buff(zone_data.household_id)
        self.household_name = householdProto.name if householdProto is not None else None

    def populate_protocol_buffer(self, lot_row_data):
        super().populate_protocol_buffer((lot_row_data.base_data), name_override=(LocalizationHelperTuning.get_raw_text(self.name)))
        logger.assert_raise((self.zone_id is not None), 'No zone_id passed to lot picker row', owner='nbaker')
        lot_row_data.lot_info_item.zone_id = self.zone_id
        if self.name is not None:
            lot_row_data.lot_info_item.name = self.name
        if self.world_id is not None:
            lot_row_data.lot_info_item.world_id = self.world_id
        if self.lot_template_id is not None:
            lot_row_data.lot_info_item.lot_template_id = self.lot_template_id
        if self.lot_description_id is not None:
            lot_row_data.lot_info_item.lot_description_id = self.lot_description_id
        if self.venue_type_name is not None:
            lot_row_data.lot_info_item.venue_type_name = self.venue_type_name
        if self.household_name is not None:
            lot_row_data.lot_info_item.household_name = self.household_name

    def __format__(self, fmt):
        dump_str = 'LotPickerRow(Zone id:{})'.format(self.zone_id)
        return dump_str


class UiDialogObjectPicker(UiDialogOkCancel):

    class DialogDescriptionDisplay(enum.Int):
        DEFAULT = 0
        NO_DESCRIPTION = 1
        FULL_DESCRIPTION = 2
        SINGLE_LINE_DESCRIPTION = 3

    class _MaxSelectableAllButOne(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'selection_difference_threshold': TunableRange(description='\n                Max selectable is defined by: the number of selection options\n                minus the selection difference threshold.\n                \n                E.g., if there are ten options, and the selection difference threshold is\n                tuned to one, then max selectable is nine.\n                ',
                                             tunable_type=int,
                                             minimum=1,
                                             default=1)}

        def get_max_selectable(self, picker, resolver):
            max_selectable = len(picker.picker_rows) - self.selection_difference_threshold
            return max(0, max_selectable)

    class _MaxSelectableHouseholdSize(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'static_maximum': OptionalTunable(description='\n                    If enabled, the number of maximum selectable items is capped\n                    to this. The effective maximum could be lower if there are\n                    fewer than this many available household slots.\n                    ',
                             tunable=TunableRange(tunable_type=int,
                             minimum=1,
                             default=8),
                             disabled_value=MAX_INT16)}

        def get_max_selectable(self, picker, resolver):
            household = picker.owner.household
            return min(self.static_maximum, household.free_slot_count)

    class _MaxSelectableUnlimited(HasTunableSingletonFactory, AutoFactoryInit):

        def get_max_selectable(self, picker, resolver):
            return 0

    class _MaxSelectableSlotBasedCount(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'slot_type':SlotType.TunableReference(description=' \n                    A particular slot type to be tested.\n                    '), 
         'require_empty':Tunable(description='\n                    based on empty slots\n                    ',
           tunable_type=bool,
           default=True), 
         'delta':Tunable(description='\n                    offset from number of empty slots\n                    ',
           tunable_type=int,
           default=0), 
         'check_target_parent':Tunable(description="\n                    If enabled, will check against target object's parent of the slot.\n                    ",
           tunable_type=bool,
           default=False), 
         'check_part_owner':Tunable(description='\n                    If Enabled, and the slot check target object is a part, we\n                    would need to check the part owner.\n                    ',
           tunable_type=bool,
           default=False)}

        def get_max_selectable(self, picker, resolver):
            if picker.target is None:
                logger.error('attempting to use slot based picker without a target object for dialog: {}', self, owner='nbaker')
                return
                slot_target_object = picker.target if not self.check_target_parent else picker.target.parent
                if slot_target_object is None:
                    logger.error('attempting to use slot based picker without a target object for dialog: {}', self, owner='amohananey')
                    return
            else:
                if slot_target_object.is_part:
                    if self.check_part_owner:
                        slot_target_object = slot_target_object.part_owner
                get_slots = slot_target_object.get_runtime_slots_gen(slot_types={self.slot_type}, bone_name_hash=None)
                if self.require_empty:
                    picker_data_max_selectable = sum((1 for slot in get_slots if slot.empty))
                else:
                    picker_data_max_selectable = sum((1 for slot in get_slots if not slot.empty))
            picker_data_max_selectable += self.delta
            return picker_data_max_selectable

    class _MaxSelectableStatic(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'number_selectable':TunableRange(description='\n                    Maximum items selectable\n                    ',
           tunable_type=int,
           default=1,
           minimum=1), 
         'exclude_previously_selected':Tunable(description='\n                    If Enabled, number selectable is increased by number of\n                    pre-existing selections.\n                    ',
           tunable_type=bool,
           default=True)}

        def get_max_selectable(self, picker, resolver):
            max_selectable = self.number_selectable
            if self.exclude_previously_selected:
                max_selectable += sum((row.is_selected for row in picker.picker_rows))
            return max_selectable

    class _MaxSelectableUnusedParts(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n                The participant we want to examine the parts of.\n                ',
           tunable_type=ParticipantTypeSingle,
           default=ParticipantTypeSingle.Object), 
         'parts_of_interest':TunableSet(description='\n                The set of part definitions we are interested in.\n                The value returned will be the set of these parts on the object that are unused.\n                ',
           tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_PART)),
           pack_safe=True),
           minlength=1), 
         'maximum_use_count':OptionalTunable(description='\n                If set, num selectable can not exceed this amount after considering number of in-use parts.\n                ',
           tunable=TunableRange(tunable_type=int, default=1, minimum=1))}

        def get_max_selectable(self, picker, resolver):
            participant = resolver.get_participant(self.participant)
            part_owner = participant.part_owner if participant.is_part else participant
            parts = part_owner.parts
            if parts is None:
                logger.error('{}: {} has no Parts! Verify that the tuning is correct.', self, participant)
                return 0
            available = 0
            in_use = 0
            for part in parts:
                if part.part_definition not in self.parts_of_interest:
                    continue
                if part.in_use:
                    in_use += 1
                else:
                    available += 1

            if self.maximum_use_count is None:
                return available
            return max(self.maximum_use_count - in_use, 0)

    class _MaxSelectableCostPerItem(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n                The household funds of this participant will be used to\n                determine how many items can be picked based on their cost.\n                ',
           tunable_type=ParticipantTypeSingleSim,
           default=ParticipantTypeSingleSim.Actor), 
         'cost_per_item':TunableRange(description='\n                The cost of picking a single item in the picker. The max\n                selectable will be determined based on the number of items\n                the tuned particpants household can afford.\n                ',
           tunable_type=int,
           default=1,
           minimum=1), 
         'maximum_selectable':OptionalTunable(description='\n                If enabled, max selectable will be capped at this value even\n                if the household can afford more items.\n                ',
           tunable=Tunable(tunable_type=int, default=1))}

        def get_max_selectable(self, picker, resolver):
            participant = resolver.get_participant(self.participant)
            household_funds = participant.household.funds.money
            max_selectable = math.floor(household_funds / self.cost_per_item)
            max_selectable = max(max_selectable, 1)
            if self.maximum_selectable is None:
                return max_selectable
            return min(self.maximum_selectable, max_selectable)

    class _MaxSelectableAnimalHomeCapacity(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'participant': TunableEnumEntry(description='\n                The animal home participant.\n                ',
                          tunable_type=ParticipantTypeSingle,
                          default=(ParticipantTypeSingle.Object))}

        def get_max_selectable--- This code section failed: ---

 L. 929         0  LOAD_FAST                'resolver'
                2  LOAD_METHOD              get_participant
                4  LOAD_FAST                'self'
                6  LOAD_ATTR                participant
                8  CALL_METHOD_1         1  '1 positional argument'
               10  STORE_FAST               'participant'

 L. 930        12  LOAD_GLOBAL              services
               14  LOAD_METHOD              animal_service
               16  CALL_METHOD_0         0  '0 positional arguments'
               18  STORE_FAST               'animal_service'

 L. 931        20  LOAD_FAST                'participant'
               22  LOAD_CONST               None
               24  COMPARE_OP               is
               26  POP_JUMP_IF_TRUE     48  'to 48'
               28  LOAD_FAST                'animal_service'
               30  LOAD_CONST               None
               32  COMPARE_OP               is
               34  POP_JUMP_IF_TRUE     48  'to 48'
               36  LOAD_FAST                'animal_service'
               38  LOAD_METHOD              is_registered_home
               40  LOAD_FAST                'participant'
               42  LOAD_ATTR                id
               44  CALL_METHOD_1         1  '1 positional argument'
               46  POP_JUMP_IF_TRUE     64  'to 64'
             48_0  COME_FROM            34  '34'
             48_1  COME_FROM            26  '26'

 L. 932        48  LOAD_GLOBAL              logger
               50  LOAD_METHOD              error
               52  LOAD_STR                 '{}: Failed to retrieve max selectable picker objects.'
               54  LOAD_FAST                'self'
               56  CALL_METHOD_2         2  '2 positional arguments'
               58  POP_TOP          

 L. 933        60  LOAD_CONST               0
               62  RETURN_VALUE     
             64_0  COME_FROM            46  '46'

 L. 935        64  LOAD_FAST                'animal_service'
               66  LOAD_METHOD              get_animal_home_max_capacity
               68  LOAD_FAST                'participant'
               70  LOAD_ATTR                id
               72  CALL_METHOD_1         1  '1 positional argument'
               74  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `RETURN_VALUE' instruction at offset 74

    class _MaxSelectableStayoverCapacity(HasTunableSingletonFactory, AutoFactoryInit):

        def get_max_selectable(self, picker, resolver):
            return services.travel_group_manager().get_stayover_capacity(picker.owner.household)

    FACTORY_TUNABLES = {'text':OptionalTunable(description='\n            If enabled, this dialog will include text.\n            ',
       tunable=TunableLocalizedStringFactoryVariant(description="\n                The dialog's text.\n                "),
       disabled_value=NULL_LOCALIZED_STRING_FACTORY), 
     'max_selectable':TunableVariant(description='\n            Method of determining maximum selectable items.\n            ',
       static_count=_MaxSelectableStatic.TunableFactory(),
       unlimited=_MaxSelectableUnlimited.TunableFactory(),
       slot_based_count=_MaxSelectableSlotBasedCount.TunableFactory(),
       all_but_one=_MaxSelectableAllButOne.TunableFactory(),
       household_size=_MaxSelectableHouseholdSize.TunableFactory(),
       unused_parts=_MaxSelectableUnusedParts.TunableFactory(),
       cost_per_item=_MaxSelectableCostPerItem.TunableFactory(),
       animal_home_capacity=_MaxSelectableAnimalHomeCapacity.TunableFactory(),
       stayover_guests_capacity=_MaxSelectableStayoverCapacity.TunableFactory(),
       default='static_count'), 
     'min_selectable':TunableRange(description='\n           The minimum number of items that must be selected to treat the\n           dialog as accepted and push continuations. If 0, then multi-select\n           sim pickers will push continuations even if no items are selected.\n           ',
       tunable_type=int,
       default=1,
       minimum=0), 
     'min_choices':TunableRange(description='\n           The minimum number of items that must be available for the \n           picker to show up. Otherwise, it will consider it as if there are no\n           choices available.\n           ',
       tunable_type=int,
       default=0,
       minimum=0), 
     'help_tooltip':OptionalTunable(description='\n            The help tooltip to display if enabled\n            ',
       tunable=TunableLocalizedStringFactoryVariant(description="\n                The dialog's help tooltip.\n                "),
       disabled_value=NULL_LOCALIZED_STRING_FACTORY), 
     'is_sortable':Tunable(description='\n           Should list of items be presented sorted\n           ',
       tunable_type=bool,
       default=False), 
     'bubble_up_selected':Tunable(description='\n            Should list of items when sorted using is_sortable have pre-selected \n            items bubble up to the top of the picker list\n            ',
       tunable_type=bool,
       default=False), 
     'use_dropdown_filter':Tunable(description='\n           Should categories be presented in a dropdown\n           ',
       tunable_type=bool,
       default=False), 
     'row_description_display':TunableEnumEntry(description="\n            How to display the description.\n            \n            DEFAULT - Show the description in the default way. In some dialogs\n            (like object pickers) this will ellipsize the description if it's\n            too long.\n            \n            NO_DESCRIPTION - Don't show any description.\n            \n            FULL_DESCRIPTION - Show the full description, regardless of length.\n            In object pickers, this will cause the description field to grow\n            with the length of the description.\n            \n            SINGLE_LINE_DESCRIPTION - Only show the first line of the description\n            in the picker cell views, up to the first line break. \n            Shows the full description in a tooltip.\n            ",
       tunable_type=DialogDescriptionDisplay,
       default=DialogDescriptionDisplay.DEFAULT), 
     'hide_row_description':Tunable(description='\n            If set to True, we will not show the row description for this picker dialog.\n            ',
       tunable_type=bool,
       default=False), 
     'control_id_type':TunableEnumEntry(description='\n            Set the type of information to send back via the control id field on picker selection.\n            Talk with your UI Eng. for questions setting this field; should normally be UNUSED.\n            ',
       tunable_type=ControlIdType,
       default=ControlIdType.UNUSED), 
     'counter_label_text':OptionalTunable(description='\n            If enabled, display this text as the counter label in the  \n            GenericDoneFooter in the picker (if the picker has one).\n            ',
       tunable=TunableLocalizedString())}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.picker_rows = []
        self.picked_results = []
        self.target_sim = None
        self.target = None
        self.ingredient_check = None
        self.max_selectable_num = 1
        self.picked_def_ids = []
        self.picked_def_counts = []
        self.current_selected = 0
        self._created_object_ids = []

    @property
    def multi_select(self):
        return self.min_selectable < 1 or self.max_selectable_num > 1 or self.max_selectable_num == 0

    def add_row(self, row):
        if row is None:
            return
        else:
            return self._validate_row(row) or None
        if row.option_id is None:
            row.option_id = len(self.picker_rows)
        self._customize_add_row(row)
        self.picker_rows.append(row)

    def _validate_row(self, row):
        raise NotImplementedError

    def _customize_add_row(self, row):
        pass

    def set_target_sim(self, target_sim):
        self.target_sim = target_sim

    def set_target(self, target):
        self.target = target

    def pick_results(self, picked_results=[], control_ids=[], ingredient_check=None):
        option_ids = [picker_row.option_id for picker_row in self.picker_rows]
        for result in picked_results:
            if result not in option_ids:
                logger.error('Player choose {0} out of provided {1} for dialog {2}', picked_results, option_ids, self)
                return False

        self.picked_results = picked_results
        self.control_ids = control_ids
        self.ingredient_check = ingredient_check
        return True

    def pick_definitions_ids_and_counts(self, picked_definitions=[], object_ids=[], picked_counts=[], ingredient_check=None):
        if len(picked_definitions) != len(picked_counts) != len(object_ids):
            logger.error('Picked definitions, picked object ids, and picked counts are not the same length', self)
            return False
        self.picked_def_ids = picked_definitions
        self._created_object_ids = object_ids
        self.picked_def_counts = picked_counts
        self.ingredient_check = ingredient_check
        return True

    def get_result_rows(self):
        return [row for row in self.picker_rows if row.option_id in self.picked_results]

    def get_result_tags(self):
        return [row.tag for row in self.get_result_rows()]

    def get_result_definitions_and_counts(self):
        return (
         self.picked_def_ids, self.picked_def_counts)

    def get_created_objects_ids(self):
        return self._created_object_ids

    def get_single_result_tag(self):
        tags = self.get_result_tags()
        if not tags:
            return
        if len(tags) != 1:
            raise ValueError('Multiple selections not supported')
        return tags[0]

    def build_msg(self, **kwargs):
        msg = (super().build_msg)(**kwargs)
        msg.dialog_type = Dialog_pb2.UiDialogMessage.OBJECT_PICKER
        msg.picker_data = self.build_object_picker()
        return msg

    def _build_customize_picker(self, picker_data):
        raise NotImplementedError

    def build_object_picker(self):
        picker_data = Dialog_pb2.UiDialogPicker()
        picker_data.title = self._build_localized_string_msg(self.title)
        if self.picker_type is not None:
            picker_data.type = self.picker_type
        else:
            picker_data.min_selectable = self.min_selectable
            if isinstance(self.max_selectable, int):
                picker_data_max_selectable = self.max_selectable
            else:
                picker_data_max_selectable = self.max_selectable.get_max_selectable(self, self._resolver)
        if picker_data_max_selectable is not None:
            picker_data.max_selectable = picker_data_max_selectable
        if self.owner:
            picker_data.owner_sim_id = self.owner.sim_id
        if self.target_sim is not None:
            picker_data.target_sim_id = self.target_sim.sim_id
        self.max_selectable_num = picker_data.max_selectable
        picker_data.is_sortable = self.is_sortable
        picker_data.bubble_up_selected = self.bubble_up_selected
        if self.help_tooltip is not None:
            picker_data.help_tooltip = self._build_localized_string_msg(self.help_tooltip)
        picker_data.use_dropdown_filter = self.use_dropdown_filter
        picker_data.description_display = self.row_description_display
        picker_data.control_id_type = self.control_id_type
        if self.counter_label_text:
            picker_data.counter_label_text = self.counter_label_text
        picker_data.current_selected = self.current_selected
        self._build_customize_picker(picker_data)
        return picker_data


class UiRecipePicker(UiDialogObjectPicker):

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, column_sort_priorities=None, picker_columns=None, **kwargs):
        if column_sort_priorities is not None:
            length = len(picker_columns)
            if any((v >= length for v in column_sort_priorities)):
                logger.error('UiRecipePicker dialog in {} has invalid column sort priority. Valid values are 0-{}', instance_class, (length - 1), owner='cjiang')

    FACTORY_TUNABLES = {'skill':OptionalTunable(Skill.TunableReference(description='\n            The skill associated with the picker dialog.\n            ')), 
     'picker_columns':TunableList(description='\n            List of the column info\n            ',
       tunable=PickerColumn.TunableFactory()), 
     'column_sort_priorities':OptionalTunable(description='\n            If enabled, specifies column sorting.\n            ',
       tunable=TunableList(description='\n                The priority index for the column (column numbers are 0-based\n                index. So, if you wish to use the first column the id is 0).\n                ',
       tunable=int)), 
     'display_ingredient_check':Tunable(description='\n            If set to True, we will display the use ingredients checkbox on the\n            picker UI.\n            ',
       tunable_type=bool,
       default=True), 
     'display_full_subrows':Tunable(description='\n            If set to true, any linked recipe subrows will use the full column view\n            instead of the single text line.\n            ',
       tunable_type=bool,
       default=False), 
     'display_funds':Tunable(description='\n            If set to true, will show the household funds at the bottom.\n            ',
       tunable_type=bool,
       default=True), 
     'filter_categories':TunableList(description='\n           The categories to display in the filter for this picker.\n           ',
       tunable=TunableTuple(tag=TunableEnumEntry(tunable_type=(tag.Tag),
       default=(tag.Tag.INVALID)),
       icon=(TunableIconFactory()),
       category_name=(TunableLocalizedString()))), 
     'verify_tunable_callback':_verify_tunable_callback}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.picker_type = ObjectPickerType.RECIPE
        self._picker_columns_override = []

    def _customize_add_row(self, row):
        for picker_row in self.picker_rows:
            self._build_row_links(row, picker_row)
            self._build_row_links(picker_row, row)

    def _validate_row(self, row):
        return isinstance(row, RecipePickerRow)

    def set_picker_columns_override(self, columns):
        self._picker_columns_override = columns

    def _get_picker_columns_gen(self):
        if self._picker_columns_override:
            yield from self._picker_columns_override
            return
        yield from self.picker_columns
        if False:
            yield None

    @staticmethod
    def _build_row_links(row1, row2):
        row_link = row1.linked_recipe_override if row1.linked_recipe_override else row1.linked_recipe
        if row_link is not None:
            if row_link is row2.tag:
                row2.linked_option_ids.append(row1.option_id)

    def _build_customize_picker(self, picker_data):
        for column in self._get_picker_columns_gen():
            column_data = picker_data.recipe_picker_data.column_list.add()
            column.populate_protocol_buffer(column_data)

        if self.skill is not None:
            picker_data.recipe_picker_data.skill_id = self.skill.guid64
        if self.column_sort_priorities is not None:
            picker_data.recipe_picker_data.column_sort_list.extend(self.column_sort_priorities)
        with ProtocolBufferRollback(picker_data.filter_data) as (filter_data_list):
            for category in self.filter_categories:
                with ProtocolBufferRollback(filter_data_list.filter_data) as (category_data):
                    category_data.tag_type = category.tag
                    build_icon_info_msg(category.icon(None), None, category_data.icon_info)
                    category_data.description = category.category_name

            filter_data_list.use_dropdown_filter = self.use_dropdown_filter
        for row in self.picker_rows:
            row_data = picker_data.recipe_picker_data.row_data.add()
            row_data.show_full_subrows = self.display_full_subrows
            row.populate_protocol_buffer(row_data)

        picker_data.recipe_picker_data.display_ingredient_check = self.display_ingredient_check
        picker_data.recipe_picker_data.display_funds = self.display_funds


class UiSimPicker(UiDialogObjectPicker):
    FACTORY_TUNABLES = {'column_count':TunableRange(description='\n            Define the number of columns to display in the picker dialog.\n            ',
       tunable_type=int,
       default=3,
       minimum=1,
       maximum=8), 
     'should_show_names':Tunable(description="\n            If true then we will show the sim's names in the picker.\n            ",
       tunable_type=bool,
       default=True), 
     'cell_type':TunableEnumEntry(description='\n            The type of cell to use in the sim picker.\n            ',
       tunable_type=SimPickerCellType,
       default=SimPickerCellType.DEFAULT), 
     'display_filter':Tunable(description='\n            Whether to display the filter bar in the Sim Picker.\n            ',
       tunable_type=bool,
       default=True)}

    def __init__(self, *args, sim_filter=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.picker_type = ObjectPickerType.SIM

    def _validate_row(self, row):
        return isinstance(row, SimPickerRow)

    def _build_customize_picker(self, picker_data):
        for row in self.picker_rows:
            row_data = picker_data.sim_picker_data.row_data.add()
            row.populate_protocol_buffer(row_data)

        picker_data.sim_picker_data.should_show_names = self.should_show_names
        picker_data.sim_picker_data.column_count = self.column_count
        picker_data.sim_picker_data.cell_type = self.cell_type
        picker_data.sim_picker_data.display_filter = self.display_filter

    def sort_selected_items_to_front(self):
        self.picker_rows.sort(key=(lambda row: row.select_default), reverse=True)


class UiObjectPicker(UiDialogObjectPicker):

    class UiObjectPickerObjectPickerType(enum.Int):
        INTERACTION = ObjectPickerType.INTERACTION
        OBJECT = ObjectPickerType.OBJECT
        PIE_MENU = ObjectPickerType.PIE_MENU
        OBJECT_LARGE = ObjectPickerType.OBJECT_LARGE
        OBJECT_SQUARE = ObjectPickerType.OBJECT_SQUARE
        LARGE_TEXT_FLAIR = ObjectPickerType.LARGE_TEXT_FLAIR
        PHOTO = ObjectPickerType.PHOTO
        OBJECT_TEXT = ObjectPickerType.OBJECT_TEXT
        OBJECT_TEXT_ADD = ObjectPickerType.OBJECT_TEXT_ADD

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, picker_type, num_columns, **kwargs):
        if num_columns > 1:
            if picker_type != ObjectPickerType.OBJECT_LARGE:
                if picker_type != ObjectPickerType.OBJECT_SQUARE:
                    if picker_type != ObjectPickerType.OBJECT_TEXT_ADD:
                        if picker_type != ObjectPickerType.OBJECT_TEXT:
                            if picker_type != ObjectPickerType.PHOTO:
                                logger.error('Tuning error for {}: Only OBJECT_LARGE, OBJECT_TEXT, OBJECT_TEXT_ADD, PHOTO and OBJECT_SQUARE picker types can have more than 1 column.', instance_class,
                                  owner='yozhang')

    FACTORY_TUNABLES = {'picker_type':TunableEnumEntry(description='\n            Object picker type for the picker dialog.\n            ',
       tunable_type=UiObjectPickerObjectPickerType,
       default=UiObjectPickerObjectPickerType.OBJECT),  'num_columns':TunableRange(description='\n            Columns number of this picker, 1 by default. For now only picker type OBJECT_SQUARE\n            and OBJECT_LARGE can have more than 1 column.\n            ',
       tunable_type=int,
       default=1,
       minimum=1,
       maximum=10), 
     'filter_categories':TunableList(description='\n           The categories to display in the filter for this picker.\n           ',
       tunable=TunableTuple(tag=TunableEnumEntry(tunable_type=(tag.Tag),
       default=(tag.Tag.INVALID)),
       icon=(TunableIconFactory()),
       category_name=(TunableLocalizedString()))), 
     'add_all_category':Tunable(description='\n           Should the All category be added to the filters\n           ',
       tunable_type=bool,
       default=True), 
     'verify_tunable_callback':_verify_tunable_callback}

    def _validate_row(self, row):
        return isinstance(row, ObjectPickerRow)

    def _build_customize_picker(self, picker_data):
        with ProtocolBufferRollback(picker_data.filter_data) as (filter_data_list):
            for category in self.filter_categories:
                with ProtocolBufferRollback(filter_data_list.filter_data) as (category_data):
                    category_data.tag_type = category.tag
                    build_icon_info_msg(category.icon(None), None, category_data.icon_info)
                    category_data.description = category.category_name

            filter_data_list.use_dropdown_filter = self.use_dropdown_filter
            filter_data_list.add_all_category = self.add_all_category
        picker_data.object_picker_data.num_columns = self.num_columns
        for row in self.picker_rows:
            row_data = picker_data.object_picker_data.row_data.add()
            row.populate_protocol_buffer(row_data)


class UiOddJobPicker(UiDialogObjectPicker):

    class UiOddJobPickerType(enum.Int):
        ODD_JOBS = ObjectPickerType.ODD_JOBS
        MISSIONS = ObjectPickerType.MISSIONS
        QUESTS = ObjectPickerType.QUESTS

    FACTORY_TUNABLES = {'picker_type':TunableEnumEntry(description='\n            The Odd Job picker type to use for this dialog. This will indicate\n            which Row cell view the UI should use.\n            ',
       tunable_type=UiOddJobPickerType,
       default=UiOddJobPickerType.ODD_JOBS), 
     'picker_background':TunableResourceKey(description='\n            The background image for this dialog.\n            ',
       resource_types=sims4.resources.CompoundTypes.IMAGE), 
     'hide_star_rating':Tunable(description='\n            If enabled, the picker should hide the Star Rating component.\n            ',
       tunable_type=bool,
       default=False)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.star_ranking = 0

    def _validate_row(self, row):
        return isinstance(row, OddJobPickerRow)

    def _build_customize_picker(self, picker_data):
        picker_data.odd_job_picker_data.star_ranking = self.star_ranking
        picker_data.odd_job_picker_data.picker_background.type = self.picker_background.type
        picker_data.odd_job_picker_data.picker_background.group = self.picker_background.group
        picker_data.odd_job_picker_data.picker_background.instance = self.picker_background.instance
        picker_data.odd_job_picker_data.hide_star_rating = self.hide_star_rating
        for row in self.picker_rows:
            row_data = picker_data.odd_job_picker_data.row_data.add()
            row.populate_protocol_buffer(row_data)


class UiCareerPicker(UiDialogObjectPicker):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.picker_type = ObjectPickerType.CAREER

    def _validate_row(self, row):
        return isinstance(row, CareerPickerRow)

    def _build_customize_picker(self, picker_data):
        for row in self.picker_rows:
            row_data = picker_data.career_picker_data.row_data.add()
            row.populate_protocol_buffer(row_data)


class UiOutfitPicker(UiDialogObjectPicker):

    class _OutftiPickerThumbnailType(enum.Int):
        SIM_INFO = 1
        MANNEQUIN = 2

    FACTORY_TUNABLES = {'thumbnail_type':TunableEnumEntry(description='\n            Define how thumbnails are to be rendered.\n            ',
       tunable_type=_OutftiPickerThumbnailType,
       default=_OutftiPickerThumbnailType.SIM_INFO), 
     'outfit_categories':TunableEnumSet(description='\n            The categories to display.\n            ',
       enum_type=OutfitCategory,
       default_enum_list=REGULAR_OUTFIT_CATEGORIES), 
     'show_filter':Tunable(description='\n            If enabled, the outfit picker has buttons to filter on the tuned\n            outfit categories.\n            ',
       tunable_type=bool,
       default=True)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.picker_type = ObjectPickerType.OUTFIT
        self.outfit_category_filters = ()

    def _validate_row(self, row):
        return isinstance(row, OutfitPickerRow)

    def _build_customize_picker(self, picker_data):
        picker_data.outfit_picker_data.thumbnail_type = self.thumbnail_type
        picker_data.outfit_picker_data.outfit_category_filters.extend(self.outfit_category_filters)
        for row in self.picker_rows:
            row_data = picker_data.outfit_picker_data.row_data.add()
            row.populate_protocol_buffer(row_data)


class UiPurchasePicker(UiDialogObjectPicker):
    FACTORY_TUNABLES = {'categories':TunableList(description='\n            A list of categories that will be displayed in the picker.\n            ',
       tunable=TunableTuple(description='\n                Tuning for a single category in the picker.\n                ',
       tag=TunableEnumEntry(description='\n                    A single tag used for filtering items.  If an item\n                    in the picker has this tag then it will be displayed\n                    in this category.\n                    ',
       tunable_type=(tag.Tag),
       default=(tag.Tag.INVALID)),
       icon=TunableResourceKey(description='\n                    Icon that represents this category.\n                    ',
       default=None,
       resource_types=(sims4.resources.CompoundTypes.IMAGE)),
       tooltip=TunableLocalizedString(description='\n                    A localized string for the tooltip of the category.\n                    '),
       disabled_tooltip=OptionalTunable(description='\n                    If enabled then when there are no items in this category, the button will be disabled instead of \n                    hidden and will have this tooltip explaining why it is hidden.\n                    ',
       tunable=TunableLocalizedString(description='\n                        The string to display as a tooltip when the category button is disabled because it is empty.\n                        ')))), 
     'sub_total':OptionalTunable(TunableTuple(description='\n            An optional section to display above the "Total" section\n            on the bottom right of the purchase picker used to display an additional cost. Ex: Delivery Fee.\n            ',
       sub_total_text=TunableLocalizedString(description='\n                The text that is displayed for this section.\n                '),
       sub_total_cost=Tunable(description='\n                The amount to display for this section. This will be added to the total on the UI.\n                ',
       tunable_type=int,
       default=0)))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.picker_type = ObjectPickerType.PURCHASE
        self.object_id = 0
        self.inventory_object_id = 0
        self.show_description = 0
        self.show_cost = True
        self.max_selectable_in_row = 0
        self.max_selectable_rows = 0
        self.show_description_tooltip = 0
        self.use_dialog_pick_response = False
        self.right_custom_text = None
        self.delivery_method = None

    def _validate_row(self, row):
        return isinstance(row, PurchasePickerRow)

    def _build_customize_picker(self, picker_data):
        picker_data.shop_picker_data.object_id = self.object_id
        picker_data.shop_picker_data.inventory_object_id = self.inventory_object_id
        picker_data.shop_picker_data.show_description = self.show_description
        if self.delivery_method is not None:
            picker_data.shop_picker_data.delivery_method = self.delivery_method
        picker_data.shop_picker_data.show_cost = self.show_cost
        picker_data.shop_picker_data.max_selectable_in_row = self.max_selectable_in_row
        picker_data.shop_picker_data.max_selectable_rows = self.max_selectable_rows
        picker_data.shop_picker_data.show_description_tooltip = self.show_description_tooltip
        picker_data.shop_picker_data.use_dialog_pick_response = self.use_dialog_pick_response
        if self.right_custom_text is not None:
            picker_data.shop_picker_data.right_custom_text = self.right_custom_text
        if self.sub_total is not None:
            picker_data.shop_picker_data.sub_total_text = self.sub_total.sub_total_text
            picker_data.shop_picker_data.sub_total_cost = self.sub_total.sub_total_cost
        category_tags = []
        for row in self.picker_rows:
            row_data = picker_data.shop_picker_data.row_data.add()
            row.populate_protocol_buffer(row_data)
            for tag in row.tags:
                if tag not in category_tags:
                    category_tags.append(tag)

        for category in self.categories:
            disabled_tooltip = None
            if category.tag not in category_tags:
                if category.disabled_tooltip is not None:
                    disabled_tooltip = category.disabled_tooltip
                else:
                    continue
                category_data = picker_data.shop_picker_data.categories.add()
                category_data.tag_type = category.tag
                build_icon_info_msg(IconInfoData(icon_resource=(category.icon)), None, category_data.icon_info)
                category_data.description = category.tooltip
                if disabled_tooltip is not None:
                    category_data.disabled_tooltip = disabled_tooltip


class UiFashionPurchasePicker(UiPurchasePicker):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.picker_type = ObjectPickerType.FASHION_PURCHASE


class UiSellPicker(UiPurchasePicker):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.picker_type = ObjectPickerType.SELL
        self.ids_and_amounts_and_price = []
        self.source_inventory = None


class UiLotPicker(UiDialogObjectPicker):

    def __init__(self, *args, lot_filter=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.picker_type = ObjectPickerType.LOT

    def _validate_row(self, row):
        return isinstance(row, LotPickerRow)

    def _build_customize_picker(self, picker_data):
        for row in self.picker_rows:
            row_data = picker_data.lot_picker_data.row_data.add()
            row.populate_protocol_buffer(row_data)


class UiItemPicker(UiDialogObjectPicker):

    def __init__(self, *args, lot_filter=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.picker_type = ObjectPickerType.ITEM

    def _validate_row(self, row):
        return isinstance(row, BasePickerRow)

    def _build_customize_picker(self, picker_data):
        for row in self.picker_rows:
            row_data = picker_data.row_picker_data.add()
            row.populate_protocol_buffer(row_data)


class UiMapViewPicker(UiDialogObjectPicker):

    class MapViewMode(enum.Int):
        TRAVEL = UI_pb2.ShowMapView.TRAVEL
        VACATION = UI_pb2.ShowMapView.VACATION
        PURCHASE = UI_pb2.ShowMapView.PURCHASE

    FACTORY_TUNABLES = {'map_view_mode': TunableVariant(description='\n            Which view mode to use for this map view picker.\n            ',
                        travel=TunableTuple(description='\n                This picker is used for travel.\n                ',
                        locked_args={'mode': MapViewMode.TRAVEL}),
                        vacation=TunableTuple(description='\n                This picker is used to rent a lot for vacation.\n                ',
                        locked_args={'mode': MapViewMode.VACATION}),
                        purchase=TunableTuple(description='\n                This picker is used to purchase a lot. You must provide the\n                venue type that is valid to buy.\n                ',
                        locked_args={'mode': MapViewMode.PURCHASE},
                        venue_to_purchase=TunableReference(description='\n                    This is the type of venue the player is actually wanting.\n                    If the player chooses a lot that is not of this venue type,\n                    it will be changed to this venue type upon purchase.\n                    ',
                        manager=(services.get_instance_manager(sims4.resources.Types.VENUE))),
                        allowed_venues=TunableList(description='\n                    These are the venues that the map view will have available\n                    for purchase.\n                    ',
                        tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.VENUE))))),
                        default='travel')}

    def __init__(self, *args, traveling_sims=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.picker_type = ObjectPickerType.CUSTOM
        self.traveling_sims = traveling_sims

    def _validate_row(self, row):
        return isinstance(row, LotPickerRow)

    def distribute_dialog(self, _, dialog_msg, **kwargs):
        distributor_inst = Distributor.instance()
        op = distributor.shared_messages.create_message_op(dialog_msg, Consts_pb2.MSG_SHOW_MAP_VIEW)
        owner = self.owner
        if owner is not None:
            distributor_inst.add_op(owner, op)
        else:
            distributor_inst.add_op_with_no_owner(op)

    def build_msg(self, additional_tokens=(), icon_override=DEFAULT, event_id=None, **kwargs):
        msg = UI_pb2.ShowMapView()
        msg.actor_sim_id = self.owner.id
        if self.target_sim is not None:
            msg.target_sim_id = self.target_sim.id
        if self.traveling_sims is not None:
            msg.traveling_sim_ids.extend([sim.id for sim in self.traveling_sims])
        msg.lot_ids_for_travel.extend([row.zone_id for row in self.picker_rows])
        msg.dialog_id = self.dialog_id
        msg.mode = self.map_view_mode.mode
        if self.map_view_mode.mode == self.MapViewMode.PURCHASE:
            msg.purchase_venue_type = self.map_view_mode.venue_to_purchase.guid64
            msg.venue_types_allowed.extend([v.guid64 for v in self.map_view_mode.allowed_venues])
        return msg


class UiApartmentPicker(UiDialogObjectPicker):

    def __init__(self, *args, traveling_sims=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.picker_type = ObjectPickerType.CUSTOM
        self.traveling_sims = traveling_sims

    def _validate_row(self, row):
        return isinstance(row, LotPickerRow)

    def distribute_dialog(self, _, dialog_msg, **kwargs):
        distributor_inst = Distributor.instance()
        op = distributor.shared_messages.create_message_op(dialog_msg, Consts_pb2.MSG_SHOW_PLEX_VIEW)
        owner = self.owner
        if owner is not None:
            distributor_inst.add_op(owner, op)
        else:
            distributor_inst.add_op_with_no_owner(op)

    def build_msg(self, **kwargs):
        msg = UI_pb2.ShowPlexView()
        msg.actor_sim_id = self.owner.id
        if self.target_sim is not None:
            msg.target_sim_id = self.target_sim.id
        if self.traveling_sims is not None:
            msg.traveling_sim_ids.extend([sim.id for sim in self.traveling_sims])
        msg.lot_ids_for_travel.extend([row.zone_id for row in self.picker_rows])
        msg.dialog_id = self.dialog_id
        return msg


class UiDropdownPicker(UiDialogObjectPicker):

    class DropdownOptions(enum.IntFlags):
        NONE = 0
        HIDE_ICON_UNLESS_SELECTED = 1

    FACTORY_TUNABLES = {'default_item_text':TunableLocalizedStringFactory(description='\n            The text that appears in the drop down selection when no valid\n            selection is made.\n            '), 
     'default_item_icon':TunableIconFactory(), 
     'options':TunableEnumFlags(description='\n            The options to pass to the drop down picker.\n            ',
       enum_type=DropdownOptions,
       default=DropdownOptions.NONE)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.picker_type = ObjectPickerType.DROPDOWN

    def _validate_row(self, row):
        return isinstance(row, ObjectPickerRow)

    def _build_customize_picker(self, picker_data):
        for id, row in enumerate(self.picker_rows):
            row_data = picker_data.dropdown_picker_data.items.add()
            row_data.text = row.name
            row_data.icon_info = create_icon_info_msg(row.icon_info)
            row_data.id = id
            if row.is_selected:
                picker_data.dropdown_picker_data.selected_item_id = id

        default_item = Dialog_pb2.UiDialogDropdownItem()
        default_item.text = self.default_item_text()
        icon_info = self.default_item_icon(None)
        default_item.icon_info = create_icon_info_msg(icon_info)
        picker_data.dropdown_picker_data.default_item = default_item
        picker_data.dropdown_picker_data.options = self.options


class TunablePickerDialogVariant(TunableVariant):

    def __init__(self, description='A tunable picker dialog variant.', available_picker_flags=ObjectPickerTuningFlags.ALL, dialog_locked_args={}, **kwargs):
        if available_picker_flags & ObjectPickerTuningFlags.SIM:
            kwargs['sim_picker'] = UiSimPicker.TunableFactory(locked_args=dialog_locked_args)
        if available_picker_flags & (ObjectPickerTuningFlags.OBJECT | ObjectPickerTuningFlags.INTERACTION | ObjectPickerTuningFlags.PIE_MENU):
            kwargs['object_picker'] = UiObjectPicker.TunableFactory(locked_args=dialog_locked_args)
        if available_picker_flags & ObjectPickerTuningFlags.CAREER:
            kwargs['career_picker'] = UiCareerPicker.TunableFactory(locked_args=dialog_locked_args)
        if available_picker_flags & ObjectPickerTuningFlags.OUTFIT:
            kwargs['outfit_picker'] = UiOutfitPicker.TunableFactory(locked_args=dialog_locked_args)
        if available_picker_flags & ObjectPickerTuningFlags.RECIPE:
            kwargs['recipe_picker'] = UiRecipePicker.TunableFactory(locked_args=dialog_locked_args)
        if available_picker_flags & ObjectPickerTuningFlags.PURCHASE:
            kwargs['purchase_picker'] = UiPurchasePicker.TunableFactory(locked_args=dialog_locked_args)
        if available_picker_flags & ObjectPickerTuningFlags.LOT:
            kwargs['lot_picker'] = UiLotPicker.TunableFactory(locked_args=dialog_locked_args)
        if available_picker_flags & ObjectPickerTuningFlags.MAP_VIEW:
            kwargs['map_view_picker'] = UiMapViewPicker.TunableFactory(locked_args=dialog_locked_args)
        if available_picker_flags & ObjectPickerTuningFlags.ITEM:
            kwargs['item_picker'] = UiItemPicker.TunableFactory(locked_args=dialog_locked_args)
        if available_picker_flags & ObjectPickerTuningFlags.DROPDOWN:
            kwargs['dropdown'] = UiDropdownPicker.TunableFactory(locked_args=dialog_locked_args)
        if available_picker_flags & ObjectPickerTuningFlags.SELL:
            kwargs['sell_picker'] = UiSellPicker.TunableFactory(locked_args=dialog_locked_args)
        if available_picker_flags & ObjectPickerTuningFlags.FASHION_PURCHASE:
            kwargs['fashion_purchase_picker'] = UiFashionPurchasePicker.TunableFactory(locked_args=dialog_locked_args)
        (super().__init__)(description=description, **kwargs)


TunableUiOutfitPickerReference, TunableUiOutfitPickerSnippet = define_snippet('OutfitPicker', UiOutfitPicker.TunableFactory())