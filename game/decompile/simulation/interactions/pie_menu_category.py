# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\pie_menu_category.py
# Compiled at: 2022-06-13 18:18:17
# Size of source mod 2**32: 4242 bytes
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableReference, Tunable, TunableResourceKey, TunableEnumEntry, TunableMapping, TunableTuple
from sims4.tuning.tunable_base import ExportModes
import enum, services, sims4.resources

class SpecialPieMenuCategoryType(enum.Int):
    NO_CATEGORY = 0
    MORE_CATEGORY = 1


class PieMenuCategory(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.PIE_MENU_CATEGORY)):
    INSTANCE_TUNABLES = {'_display_name':TunableLocalizedStringFactory(description='\n            Localized name of this category',
       export_modes=ExportModes.All), 
     '_icon':TunableResourceKey(description='\n            Icon to be displayed in the pie menu\n            ',
       resource_types=sims4.resources.CompoundTypes.IMAGE,
       default=None,
       allow_none=True,
       export_modes=ExportModes.All), 
     '_collapsible':Tunable(description='\n            If enabled, when this category only has one item inside, that item will show on the pie menu without going through this category.\n            If disabled, the user will always go through this category, regardless of the number of entries within.',
       tunable_type=bool,
       default=True,
       export_modes=ExportModes.All), 
     '_parent':TunableReference(description='\n            Parent category.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.PIE_MENU_CATEGORY),
       allow_none=True,
       export_modes=ExportModes.All), 
     '_special_category':TunableEnumEntry(description='\n            Designate this category as a special category.  Most will be NO_CATEGORY.\n            ',
       tunable_type=SpecialPieMenuCategoryType,
       default=SpecialPieMenuCategoryType.NO_CATEGORY,
       export_modes=ExportModes.All), 
     '_display_priority':Tunable(description='\n            The display priority of this category.\n            ',
       tunable_type=int,
       default=1,
       export_modes=ExportModes.All), 
     'mood_overrides':TunableMapping(description='\n            If sim matches mood, tooltip and display name of category will\n            be updated with tuned values.\n            ',
       key_type=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.MOOD))),
       value_type=TunableTuple(name_override=TunableLocalizedStringFactory(description='\n                   Localized name of this category\n                   ',
       allow_none=True),
       tooltip=TunableLocalizedStringFactory(description='\n                   Tooltip for the new category.\n                   ',
       allow_none=True),
       export_class_name='text_overrides'),
       key_value_type=None,
       key_name='mood',
       value_name='override_data',
       tuple_name='mood_to_override_data',
       export_modes=(
      ExportModes.ClientBinary,)), 
     'always_show_disabled_interactions':Tunable(description='\n            If enabled, display all disabled interactions under this category, \n            even if they all have the same disabled tooltip.\n            ',
       tunable_type=bool,
       default=False,
       export_modes=ExportModes.All)}