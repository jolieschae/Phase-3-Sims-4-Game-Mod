# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\slot_elements.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 9532 bytes
from event_testing.tests import TunableTestSet
from interactions import ParticipantType
from interactions.utils.interaction_elements import XevtTriggeredElement
from objects.gardening.gardening_tuning import GardeningTuning
from objects.slot_strategy import SlotStrategyVariant
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, OptionalTunable, Tunable, TunableLiteralOrRandomValue, TunableTuple
from tunable_utils.tunable_object_generator import TunableObjectGeneratorVariant
from ui.ui_dialog_notification import TunableUiDialogNotificationSnippet
import build_buy, random, services, sims4.log
logger = sims4.log.Logger('SlotElements', default_owner='rmccord')

class SlotObjectsFromInventory(XevtTriggeredElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'description':'\n            Transfer particpant objects into the target object available slots\n            of the tuned slot type. \n            ', 
     'slot_strategy':SlotStrategyVariant(description='\n            The slot strategy we want to use to place objects from the transfer\n            source into slots on the target.\n            '), 
     'slot_failure_notification':OptionalTunable(description='\n            If enabled, we will show a notification to the player when this\n            element runs and no objects are successfully slotted.\n            ',
       tunable=TunableUiDialogNotificationSnippet(description='\n                Notification to show if we fail to slot any objects.\n                '))}

    def _do_behavior(self):
        slot_strategy = self.slot_strategy(self.interaction.get_resolver())
        if not slot_strategy.slot_objects():
            if self.slot_failure_notification is not None:
                dialog = self.slot_failure_notification((self.interaction.sim), resolver=(self.interaction.get_resolver()))
                dialog.show_dialog()
        return True


class SlotItemTransfer(XevtTriggeredElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'objects_to_transfer':TunableObjectGeneratorVariant(description="\n            The objects whose slots will be checked for objects to be gathered\n            into the Sim's inventory.\n            ",
       participant_default=ParticipantType.Object), 
     'object_tests':TunableTestSet(description='\n            Tests that will run on each object, and will harvest the object\n            only if all the tests pass.\n            \n            The object will be the PickedObject participant type, so we can\n            preserve the interaction resolver.\n            '), 
     'fallback_to_household_inventory':Tunable(description="\n            If enabled, and we fail to add the object to the Sim's inventory,\n            we will attempt to add it to the household inventory.\n            ",
       tunable_type=bool,
       default=False), 
     'transfer_extra_objects':OptionalTunable(description="\n            If enabled, extra slot items will be transferred to the Sim's inventory\n            from each object we gathered.\n            \n            For example: If we gathered 3 apple trees, and set count as 2, then we\n            will harvest 3 * 2 = 6 extra apples from this interaction\n            ",
       tunable=TunableTuple(count=TunableLiteralOrRandomValue(description='\n                    The number of extra items to be transferred.\n                    ',
       tunable_type=int,
       default=1,
       minimum=0,
       maximum=10),
       tests=TunableTestSet(description='\n                    A set of tests that must pass in order for this extra transfer\n                    to be applied.\n                    '))), 
     'use_gardening_optimization':Tunable(description='\n            If enabled, we will precompact the objects prior to adding them\n            to inventory if the tuning ID and quality are the same regardless\n            of any other differences.\n            ',
       tunable_type=bool,
       default=False), 
     'transfer_object_children':Tunable(description="\n            If checked, transfer the objects' children. If unchecked, transfer\n            the objects themselves. \n            ",
       tunable_type=bool,
       default=True)}

    def _do_behavior(self):
        objects = self.objects_to_transfer.get_objects(self.interaction)
        if not objects:
            return False
        transfer_extra = self.transfer_extra_objects
        should_transfer_extra = False
        if transfer_extra:
            resolver = self.interaction.get_resolver()
            if transfer_extra.tests.run_tests(resolver):
                should_transfer_extra = True
        objects_to_transfer = []
        num_extra_objects = 0
        for obj in objects:
            has_extra_to_transfer = False
            if self.transfer_object_children:
                potential_objects_to_transfer = obj.children
            else:
                potential_objects_to_transfer = (
                 obj,)
            for potential_object in potential_objects_to_transfer:
                interaction_parameters = {'picked_item_ids': (potential_object.id,)}
                resolver = (self.interaction.get_resolver)(**interaction_parameters)
                if self.object_tests.run_tests(resolver):
                    objects_to_transfer.append(potential_object)
                    has_extra_to_transfer = True

            if should_transfer_extra and has_extra_to_transfer:
                num_extra_objects += transfer_extra.count.random_int()

        stacked_objects = self._stack_objects_transfer(objects_to_transfer, num_extra_objects)
        sim = self.interaction.sim
        sim_inventory = sim.inventory_component
        for obj, _ in stacked_objects:
            obj.update_ownership(sim)
            if sim_inventory.can_add(obj):
                if obj.live_drag_component is not None:
                    obj.live_drag_component.resolve_live_drag_household_permission()
                sim_inventory.player_try_add_object(obj)
            elif self.fallback_to_household_inventory:
                build_buy.move_object_to_household_inventory(obj)

    def _stack_objects_transfer(self, objects_to_harvest, num_extra_objects):
        obj_count = {}
        dupe_objects = []
        if self.use_gardening_optimization:
            unique_objects = []
            while objects_to_harvest:
                obj = objects_to_harvest.pop()
                quality_value = obj.get_state(GardeningTuning.QUALITY_STATE_VALUE) if obj.has_state(GardeningTuning.QUALITY_STATE_VALUE) else 0
                object_count_key = (obj.guid64, quality_value)
                curr_count = obj_count.get(object_count_key, 0)
                if curr_count == 0:
                    unique_objects.append((obj, quality_value))
                else:
                    dupe_objects.append(obj)
                curr_count = curr_count + 1
                obj_count[object_count_key] = curr_count

            for obj, quality_value in unique_objects:
                object_count_key = (obj.guid64, quality_value)
                curr_count = obj_count.get(object_count_key, 0)
                obj.set_stack_count(curr_count)

        else:
            unique_objects = [(obj, 0) for obj in objects_to_harvest]
        if unique_objects:
            while num_extra_objects > 0:
                obj, _ = random.choice(unique_objects)
                obj.update_stack_count(1)
                num_extra_objects -= 1

        if dupe_objects:
            services.get_reset_and_delete_service().trigger_batch_destroy(dupe_objects)
        return unique_objects