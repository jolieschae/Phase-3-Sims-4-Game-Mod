# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\owning_household_component.py
# Compiled at: 2020-11-20 04:44:26
# Size of source mod 2**32: 3319 bytes
from objects import ALL_HIDDEN_REASONS_EXCEPT_UNINITIALIZED
from objects.components import Component
from objects.components.types import OWNING_HOUSEOLD_COMPONENT
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableList, TunableReference
import services, sims4.log, sims4.resources
logger = sims4.log.Logger('Owning Household Component', default_owner='jjacobson')

class OwningHouseholdComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=OWNING_HOUSEOLD_COMPONENT):

    @staticmethod
    def _verify_tunable_callback(cls, tunable_name, source, commodity_to_add, **kwargs):
        for commodity in commodity_to_add:
            if commodity.persisted_tuning:
                logger.error('Commodity {} is set to persist and therefore cannot be added by the Owning Household Component.', commodity)

    FACTORY_TUNABLES = {'commodity_to_add':TunableList(description='\n            A list of commodities to add to the Sims of the owning household.\n            ',
       tunable=TunableReference(description='\n                A commodity to add to the Sim.  Commodities must not persist.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
       class_restrictions=('Commodity', )),
       unique_entries=True), 
     'verify_tunable_callback':_verify_tunable_callback}

    def _add_commodities_to_sims(self, sim):
        commodity_tracker = sim.commodity_tracker
        for commodity in self.commodity_to_add:
            commodity_tracker.add_statistic(commodity)

    def _on_sim_spawned(self, sim):
        if services.owning_household_id_of_active_lot() != sim.household_id:
            return
        self._add_commodities_to_sims(sim)

    def on_add(self, *_, **__):
        services.sim_spawner_service().register_sim_spawned_callback(self._on_sim_spawned)
        owning_household = services.owning_household_of_active_lot()
        if owning_household is None:
            return
        for sim in owning_household.instanced_sims_gen(allow_hidden_flags=ALL_HIDDEN_REASONS_EXCEPT_UNINITIALIZED):
            self._add_commodities_to_sims(sim)

    def on_remove(self, *_, **__):
        services.sim_spawner_service().unregister_sim_spawned_callback(self._on_sim_spawned)