# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\ensemble\ensemble_component.py
# Compiled at: 2016-07-25 15:29:31
# Size of source mod 2**32: 2836 bytes
from objects.components import Component, types, componentmethod_with_fallback
from sims4.tuning.tunable import AutoFactoryInit, HasTunableFactory, TunableMapping, TunableReference
import services, sims4.resources

class EnsembleComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=types.ENSEMBLE_COMPONENT):
    FACTORY_TUNABLES = {'_rel_bit_ensembles': TunableMapping(description='\n            A mapping of relationship bit to ensemble. A Sim will generate an\n            ensemble with a Sim with this particular bit.\n            \n            e.g.\n                A dog might want to form an ensemble with one of their owners.\n                Dogs who chose to form an ensemble with the same Sim will share\n                an ensemble.\n            ',
                             key_type=TunableReference(description='\n                The relationship bit driving the behavior.\n                ',
                             manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)),
                             class_restrictions=('RelationshipBit', ),
                             pack_safe=True),
                             value_type=TunableReference(description='\n                The ensemble to form.\n                ',
                             manager=(services.get_instance_manager(sims4.resources.Types.ENSEMBLE)),
                             pack_safe=True))}

    @componentmethod_with_fallback((lambda: None))
    def create_auto_ensembles(self):
        ensemble_service = services.ensemble_service()
        rel_tracker = self.owner.relationship_tracker
        for relationship_bit, ensemble_type in self._rel_bit_ensembles.items():
            target_sims = []
            for target in rel_tracker.get_target_sim_infos():
                if target is None:
                    continue
                target_instance = target.get_sim_instance()
                if target_instance is None:
                    continue
                if not rel_tracker.has_bit(target.sim_id, relationship_bit):
                    continue
                target_sims.append(target_instance)

            if not target_sims:
                continue
            target_sim = max(target_sims, key=(lambda s: ensemble_service.get_ensemble_for_sim(ensemble_type, s) is not None))
            ensemble_service.create_ensemble(ensemble_type, (self.owner, target_sim))