# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\gameplay_object_preference.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 1878 bytes
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableReference, TunableEnumEntry
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import constproperty
from traits.base_preference import BasePreference
from traits.trait_type import TraitType
import enum, sims4, sims4.log, services
logger = sims4.log.Logger('Gameplay Object Preference', default_owner='micfisher')

class TraitTypeGameplayObjectPreference(enum.Int):
    GAMEPLAY_OBJECT_PREFERENCE = TraitType.GAMEPLAY_OBJECT_PREFERENCE


class GameplayObjectPreference(BasePreference):
    INSTANCE_TUNABLES = {'preference_item':TunableReference(description='\n            The item marked by the preference of the owner.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.OBJECT),
       tuning_group=GroupNames.SPECIAL_CASES), 
     'trait_type':TunableEnumEntry(description='\n            The trait type for Gameplay Object Preferences.\n            ',
       tunable_type=TraitTypeGameplayObjectPreference,
       default=TraitTypeGameplayObjectPreference.GAMEPLAY_OBJECT_PREFERENCE,
       export_modes=sims4.tuning.tunable_base.ExportModes.All)}

    @constproperty
    def is_gameplay_object_preference_trait():
        return True