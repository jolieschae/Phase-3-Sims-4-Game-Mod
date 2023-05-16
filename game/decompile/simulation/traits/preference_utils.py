# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\preference_utils.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 701 bytes
import services, sims4.resources
from traits.preference_enums import PreferenceTypes

def preferences_gen():
    trait_manager = services.get_instance_manager(sims4.resources.Types.TRAIT)
    if trait_manager is None:
        return
    for trait in trait_manager.types.values():
        if trait.is_preference_trait:
            yield trait


def get_preferences_by_category(category):
    return [p for p in preferences_gen() if p.preference_category is category]