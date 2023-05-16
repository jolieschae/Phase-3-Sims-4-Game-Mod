# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\gameplay_object_preference_loot.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 1683 bytes
from interactions.utils.loot_basic_op import BaseTargetedLootOperation
from sims4.tuning.tunable import TunableEnumEntry, TunableReference
from traits.preference_enums import GameplayObjectPreferenceTypes
import sims4.resources, services

class AddGameplayObjectPreferenceLootOp(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'description':'\n            This loot will add the specified Gameplay Object Preference.\n            ', 
     'gameplay_object_preference':TunableReference(description='\n            The Gameplay Object Preference to be added.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.TRAIT),
       class_restrictions=('GameplayObjectPreference', )), 
     'preference_type':TunableEnumEntry(description='\n            The type (unsure, dislike, like, love) associated with this Gameplay Object Preference.\n            ',
       tunable_type=GameplayObjectPreferenceTypes,
       default=GameplayObjectPreferenceTypes.UNSURE)}

    def __init__(self, gameplay_object_preference, preference_type, **kwargs):
        (super().__init__)(**kwargs)
        self._gameplay_object_preference = gameplay_object_preference
        self._preference_type = preference_type

    def _apply_to_subject_and_target(self, subject, target, resolver):
        target.trait_tracker.add_gameplay_object_preference(self._gameplay_object_preference, self._preference_type)