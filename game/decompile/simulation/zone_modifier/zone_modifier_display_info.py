# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\zone_modifier\zone_modifier_display_info.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 2820 bytes
from sims4.tuning.tunable import HasTunableReference, TunablePackSafeReference, TunableEnumEntry
from sims4.resources import Types
from sims4.tuning.tunable_base import ExportModes, GroupNames
from sims4.tuning.instances import HashedTunedInstanceMetaclass
import enum, services, sims4.resources
from sims4.localization import TunableLocalizedString
from interactions.utils.tunable_icon import TunableIcon

class ZoneModifierType(enum.Int):
    LOT_TRAIT = 0
    LOT_CHALLENGE = 1


class ZoneModifierDisplayInfo(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.USER_INTERFACE_INFO)):
    base_game_only = True
    INSTANCE_TUNABLES = {'zone_modifier_icon':TunableIcon(description="\n            The zone modifier's icon.\n            ",
       export_modes=ExportModes.All,
       tuning_group=GroupNames.UI), 
     'zone_modifier_name':TunableLocalizedString(description="\n            The zone modifier's name.\n            ",
       export_modes=ExportModes.All,
       tuning_group=GroupNames.UI), 
     'zone_modifier_description':TunableLocalizedString(description="\n            The zone modifier's description.\n            ",
       export_modes=ExportModes.All,
       tuning_group=GroupNames.UI), 
     'zone_modifier_reference':TunablePackSafeReference(description='\n            The zone modifier gameplay tuning reference ID.\n            \n            This ID will be what is persisted in save data and used\n            for any lookups.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.ZONE_MODIFIER),
       export_modes=ExportModes.All,
       tuning_group=GroupNames.UI), 
     'modifier_type':TunableEnumEntry(description='\n            The type of modifier that this zone modifier represents. For example, is this a lot trait or \n            a lot challenge.\n            ',
       tunable_type=ZoneModifierType,
       default=ZoneModifierType.LOT_TRAIT,
       export_modes=ExportModes.All,
       tuning_group=GroupNames.UI)}