# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\laundry\laundry_loots.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 2759 bytes
import services, sims4
from event_testing.tests import TunableTestSet
from interactions.utils.loot_basic_op import BaseLootOperation
from objects.components.state_references import TunableStateValueReference
from sims4.tuning.tunable import TunableReference, TunableList, TunableTuple, OptionalTunable
from singletons import UNSET, DEFAULT

class GenerateClothingPile(BaseLootOperation):
    FACTORY_TUNABLES = {'initial_states_for_hamper':OptionalTunable(description='\n            If enabled, we apply this list of states to generated clothing piles for the hamper instead of \n            the initial states set on laundry_tuning.put_clothing_pile_on_hamper.clothing_pile.initial_states.\n            ',
       tunable=TunableList(tunable=TunableTuple(description='\n                    The state to apply and optional test set to decide if the state \n                    should be applied.\n                    ',
       state=TunableStateValueReference(pack_safe=True),
       tests=(TunableTestSet())))), 
     'ground_pile_loot':OptionalTunable(description='\n            If enabled, we apply this loot on generating clothing piles on the ground instead of the loot\n            set on laundry_tuning.generate_clothing_pile.loot_to_apply.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', ),
       pack_safe=True))}

    def __init__(self, initial_states_for_hamper, ground_pile_loot, **kwargs):
        (super().__init__)(**kwargs)
        self._initial_states_for_hamper = initial_states_for_hamper
        self._ground_pile_loot = ground_pile_loot

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not subject.is_sim:
            return
        sim = subject.get_sim_instance()
        if sim is None:
            return
        laundry_service = services.get_laundry_service()
        if laundry_service is None:
            return
        if laundry_service.is_sim_eligible_for_laundry(sim):
            initial_states = self._initial_states_for_hamper or DEFAULT
            ground_pile_loot = self._ground_pile_loot or DEFAULT
            laundry_service.generate_clothing_pile(sim, resolver, initial_states=initial_states,
              ground_pile_loot=ground_pile_loot)