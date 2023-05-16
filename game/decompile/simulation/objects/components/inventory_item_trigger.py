# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\inventory_item_trigger.py
# Compiled at: 2015-06-26 18:54:05
# Size of source mod 2**32: 4145 bytes
from objects.components.state import ObjectStateValue
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableEnumEntry
import enum

class InventoryItemStateTriggerOp(enum.Int):
    NONE = 0
    ANY = 1
    ALL = 2


class ItemStateTrigger(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'description':'\n            When Item inside the inventory has certain state value, it will trigger\n            corresponding state value on the inventory component owner.\n            ', 
     'item_state_value':ObjectStateValue.TunableReference(description='\n            The state value to monitor on the inventory item.\n            '), 
     'owner_state_value':ObjectStateValue.TunableReference(description='\n            The state value to apply on owner object if the condition satisfied.\n            '), 
     'trigger_condition':TunableEnumEntry(description='\n            NONE means if none of the object has the state value, the trigger will happen.\n            ANY means if any of the object has the state value, the trigger will happen.\n            ALL means all the objects inside has to have the value, the trigger will happen.\n            ',
       tunable_type=InventoryItemStateTriggerOp,
       default=InventoryItemStateTriggerOp.ANY)}

    def __init__(self, inventory, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._inventory = inventory
        self._total_obj_count = 0
        self._obj_with_state_count = 0

    def on_object_added(self, added_obj):
        self._total_obj_count += 1
        state_component = added_obj.state_component
        if state_component is not None:
            if state_component.state_value_active(self.item_state_value):
                self._obj_with_state_count += 1
        self._check_trigger_state()

    def on_obj_removed(self, removed_obj):
        self._total_obj_count -= 1
        state_component = removed_obj.state_component
        if state_component is not None:
            if state_component.state_value_active(self.item_state_value):
                self._obj_with_state_count -= 1
        self._check_trigger_state()

    def obj_state_changed(self, old_state, new_state):
        if old_state is self.item_state_value:
            self._obj_with_state_count -= 1
        if new_state is self.item_state_value:
            self._obj_with_state_count += 1
        self._check_trigger_state()

    def _check_trigger_state(self):
        if self.trigger_condition == InventoryItemStateTriggerOp.NONE:
            if self._obj_with_state_count == 0:
                self._set_owner_object_state(self.owner_state_value)
        elif self.trigger_condition == InventoryItemStateTriggerOp.ANY:
            if self._obj_with_state_count > 0:
                self._set_owner_object_state(self.owner_state_value)
        elif self.trigger_condition == InventoryItemStateTriggerOp.ALL:
            if self._obj_with_state_count == self._total_obj_count:
                self._set_owner_object_state(self.owner_state_value)

    def _set_owner_object_state(self, state_value):
        obj = self._inventory.owner
        if obj.state_component is not None:
            obj.set_state(state_value.state, state_value)