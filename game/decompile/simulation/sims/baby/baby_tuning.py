# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\baby\baby_tuning.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 7025 bytes
import random
from objects.components.state import ObjectState, ObjectStateValue
from sims.occult.occult_enums import OccultType
from sims.sim_info_types import Gender
from sims4.tuning.tunable import TunableReference, TunableMapping, TunableEnumEntry, TunableSkinTone, TunableList, TunableTuple, Tunable
from sims4.tuning.tunable_base import ExportModes
from traits.traits import Trait
import enum, services

class BabyTuning:
    BABY_THUMBNAIL_DEFINITION = TunableReference(description='\n        The thumbnail definition for client use only.\n        ',
      manager=(services.definition_manager()),
      export_modes=(
     ExportModes.ClientBinary,))
    BABY_BASSINET_DEFINITION_MAP = TunableMapping(description='\n        The corresponding mapping for each definition pair of empty bassinet and\n        bassinet with baby inside. The reason we need to have two of definitions\n        is one is deletable and the other one is not.\n        ',
      key_name='Baby',
      key_type=TunableReference(description='\n            The definition of an object that is a bassinet containing a fully\n            functioning baby.\n            ',
      manager=(services.definition_manager()),
      pack_safe=True),
      value_name='EmptyBassinet',
      value_type=TunableReference(description='\n            The definition of an object that is an empty bassinet.\n            ',
      manager=(services.definition_manager()),
      pack_safe=True))
    BABY_DEFAULT_BASSINETS = TunableList(description='\n        A list of trait to default bassinet definitions. This is used when\n        generating default bassinets for specific babies. The list is evaluated\n        in order. Should no element be selected, an entry from\n        BABY_BASSINET_DEFINITION_MAP is selected instead.\n        ',
      tunable=TunableTuple(description='\n            Should the baby have any of the specified traits, select a bassinet\n            from the list of bassinets.\n            ',
      traits=TunableList(description='\n                This entry is selected should the Sim have any of these traits.\n                ',
      tunable=Trait.TunableReference(pack_safe=True)),
      bassinets=TunableList(description='\n                Should this entry be selected, a random bassinet from this list\n                is chosen.\n                ',
      tunable=TunableReference(manager=(services.definition_manager()),
      pack_safe=True))))
    BABY_CLOTH_STATE = ObjectState.TunableReference(description='\n        The object state that determines baby cloth value.\n        ')
    BABY_CLOTH_STATE_MAP = TunableMapping(description='\n        A mapping from current BABY_CLOTH_STATE value to cloth string.\n        ',
      key_type=ObjectStateValue.TunableReference(description='\n            The state value that will be looked for on the baby.\n            ',
      pack_safe=True),
      value_type=Tunable(description='\n            The cloth that will be used if the state value key is present.\n            ',
      tunable_type=str,
      default=''))
    BABY_DEFAULT_CLOTH = TunableTuple(description='\n        Tuning for the default cloth value for different babies.\n        ',
      boy=Tunable(description='\n            The cloth that will be used by default for a boy baby.\n            ',
      tunable_type=str,
      default=''),
      girl=Tunable(description='\n            The cloth that will be used by default for a girl baby.\n            ',
      tunable_type=str,
      default=''),
      alien=Tunable(description='\n            The cloth that will be used by default for an alien baby.\n            ',
      tunable_type=str,
      default=''))

    @staticmethod
    def get_default_definition(sim_info):
        for entry in BabyTuning.BABY_DEFAULT_BASSINETS:
            if not entry.bassinets:
                continue
            if not entry.traits or any((sim_info.has_trait(trait) for trait in entry.traits)):
                return random.choice(entry.bassinets)

        return next(iter(BabyTuning.BABY_BASSINET_DEFINITION_MAP), None)

    @staticmethod
    def get_corresponding_definition(definition):
        if definition in BabyTuning.BABY_BASSINET_DEFINITION_MAP:
            return BabyTuning.BABY_BASSINET_DEFINITION_MAP[definition]
        for baby_def, bassinet_def in BabyTuning.BABY_BASSINET_DEFINITION_MAP.items():
            if bassinet_def is definition:
                return baby_def

    @staticmethod
    def get_baby_cloth_info(sim_info):
        if sim_info.is_baby:
            cloth = None
            baby = services.object_manager().get(sim_info.sim_id)
            if baby is not None:
                cloth_state_value = baby.get_state(BabyTuning.BABY_CLOTH_STATE)
                cloth = BabyTuning.BABY_CLOTH_STATE_MAP.get(cloth_state_value, None)
            if cloth is None:
                if hasattr(sim_info, 'occult_tracker') and sim_info.occult_tracker is not None and sim_info.occult_tracker.has_occult_type(OccultType.ALIEN):
                    cloth = BabyTuning.BABY_DEFAULT_CLOTH.alien
                else:
                    if sim_info.gender == Gender.FEMALE:
                        cloth = BabyTuning.BABY_DEFAULT_CLOTH.girl
                    else:
                        if sim_info.gender == Gender.MALE:
                            cloth = BabyTuning.BABY_DEFAULT_CLOTH.boy
            return cloth
        return BabyTuning.BABY_DEFAULT_CLOTH.girl