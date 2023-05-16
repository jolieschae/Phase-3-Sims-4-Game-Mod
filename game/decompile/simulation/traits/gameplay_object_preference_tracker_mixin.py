# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\gameplay_object_preference_tracker_mixin.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 4273 bytes
from distributor.rollback import ProtocolBufferRollback
from protocolbuffers import SimObjectAttributes_pb2 as protocols
from sims4.localization import TunableLocalizedString
from sims4.tuning.tunable import TunableMapping
from traits.preference_enums import GameplayObjectPreferenceTypes

class GameplayObjectPreferenceTrackerMixin:
    PREFERENCE_TYPE_STRING_MAP = TunableMapping(description='\n        A mapping of Gameplay Object Preference Type to a string to be displayed to the user.\n        ',
      key_name='Gameplay Object Preference Type',
      key_type=GameplayObjectPreferenceTypes,
      value_name='Displayable Gameplay Object Preference Type',
      value_type=(TunableLocalizedString()))

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._gameplay_object_to_preference = {}
        self._object_to_gameplay_object_preference_type = {}

    def get_gameplay_object_preferences(self):
        raise NotImplementedError

    def get_gameplay_object_preference_type(self, trait):
        return self._gameplay_object_to_preference.get(trait, GameplayObjectPreferenceTypes.NONE)

    def get_gameplay_object_preference_type_from_object_as_string(self, gameplay_object):
        gameplay_object_preference_type = self._object_to_gameplay_object_preference_type.get(gameplay_object, GameplayObjectPreferenceTypes.NONE)
        return GameplayObjectPreferenceTrackerMixin.PREFERENCE_TYPE_STRING_MAP[gameplay_object_preference_type]

    def add_gameplay_object_preference(self, trait, preference_type, **kwargs):
        raise NotImplementedError

    def remove_gameplay_object_preference(self, trait, **kwargs):
        raise NotImplementedError

    def remove_all_gameplay_object_preferences(self):
        raise NotImplementedError

    def save_gameplay_object_preferences(self, data):
        for trait, preference_type in self._gameplay_object_to_preference.items():
            with ProtocolBufferRollback(data.gameplay_object_preference_map) as (preference_map):
                preference_map.gameplay_object_preference_id = trait.guid64
                preference_map.gameplay_object_preference_type = preference_type

    def load_gameplay_object_preferences(self, trait_manager, data):
        for gameplay_object_preference in data.gameplay_object_preference_map:
            trait = trait_manager.get(gameplay_object_preference.gameplay_object_preference_id)
            if trait is not None:
                self._gameplay_object_to_preference[trait] = GameplayObjectPreferenceTypes(gameplay_object_preference.gameplay_object_preference_type)
                self._object_to_gameplay_object_preference_type[trait.preference_item] = GameplayObjectPreferenceTypes(gameplay_object_preference.gameplay_object_preference_type)