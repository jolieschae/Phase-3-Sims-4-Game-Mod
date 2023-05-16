# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\zone_modifier\zone_modifier_component.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 6787 bytes
import enum, services
from event_testing.resolver import SingleObjectResolver
from event_testing.state_tests import WhiteBlackStateTest
from objects.components import Component, types
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableFactory, TunableMapping, TunableReference, AutoFactoryInit, HasTunableSingletonFactory, TunableVariant, TunableList

class ZoneModifierCriteriaType(enum.Int, export=False):
    STATE_VALUE = 0


class _ZoneModifierObjectCriteriaBase(HasTunableSingletonFactory, AutoFactoryInit):

    @property
    def criteria_type(self):
        raise NotImplemented

    def can_provide(self, resolver):
        raise NotImplemented


class ZoneModifierCriteriaObjectStateValue(_ZoneModifierObjectCriteriaBase):
    FACTORY_TUNABLES = {'state_value_test': WhiteBlackStateTest.TunableFactory(locked_args={'tooltip': None})}

    @property
    def criteria_type(self):
        return ZoneModifierCriteriaType.STATE_VALUE

    def can_provide(self, resolver):
        return resolver(self.state_value_test)


class ZoneModifierComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=types.ZONE_MODIFIER_COMPONENT):
    FACTORY_TUNABLES = {'zone_modifiers': TunableMapping(description='\n            A mapping of zone modifiers and under what conditions they should be enabled\n            for this object.\n            ',
                         key_type=TunableReference(description='\n                The zone modifier to be set.\n                ',
                         manager=(services.get_instance_manager(Types.ZONE_MODIFIER)),
                         pack_safe=True),
                         value_type=TunableList(description='\n                List of criteria that must pass for this to be applied.\n                ',
                         tunable=TunableVariant(state=(ZoneModifierCriteriaObjectStateValue.TunableFactory()),
                         default='state')))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._provided_zone_modifiers = set()

    def on_add(self):
        object_manager = services.object_manager()
        object_manager.add_zone_modifier_object(self.owner.id)
        zone = services.current_zone()
        if zone.is_zone_loading:
            return
        self._calculate_zone_modifiers()
        self._update_zone_modifier_service()

    def on_remove(self):
        object_manager = services.object_manager()
        object_manager.remove_zone_modifier_object(self.owner.id)
        self._provided_zone_modifiers.clear()
        self._update_zone_modifier_service()

    def on_finalize_load(self):
        self._calculate_zone_modifiers()

    def on_state_changed(self, state, old_value, new_value, from_init):
        zone = services.current_zone()
        if zone.is_zone_loading:
            return
        trigger_calculate = False
        for zone_modifier, criteria in self.zone_modifiers.items():
            if not criteria:
                continue
            for criterion in criteria:
                if criterion.criteria_type == ZoneModifierCriteriaType.STATE_VALUE:
                    state_test = criterion.state_value_test.states
                    old_passes = state_test.test_item(old_value)
                    new_passes = state_test.test_item(new_value)
                    trigger_calculate = old_passes != new_passes
                if trigger_calculate:
                    break

            if trigger_calculate:
                break

        if trigger_calculate:
            self._calculate_zone_modifiers()
            if services.current_zone().is_zone_running:
                self._update_zone_modifier_service()

    def component_zone_modifiers_gen(self):
        yield from self._provided_zone_modifiers
        if False:
            yield None

    def _calculate_zone_modifiers(self):
        self._provided_zone_modifiers.clear()
        resolver = SingleObjectResolver(self.owner)
        for zone_modifier, criteria in self.zone_modifiers.items():
            if not criteria:
                self._provided_zone_modifiers.add(zone_modifier)
                continue
            if all((criterion.can_provide(resolver) for criterion in criteria)):
                self._provided_zone_modifiers.add(zone_modifier)

    def _update_zone_modifier_service(self):
        current_zone_id = services.current_zone_id()
        services.get_zone_modifier_service().check_for_and_apply_new_zone_modifiers(current_zone_id)