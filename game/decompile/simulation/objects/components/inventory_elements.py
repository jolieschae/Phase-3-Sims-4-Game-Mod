# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\inventory_elements.py
# Compiled at: 2021-04-29 11:56:30
# Size of source mod 2**32: 17768 bytes
from build_buy import ObjectOriginLocation
from event_testing.resolver import SingleActorAndObjectResolver, DoubleObjectResolver
from event_testing.test_events import TestEvent
from event_testing.tests import TunableTestSet
from interactions import ParticipantType
from interactions.utils.interaction_elements import XevtTriggeredElement
from objects.components.inventory_enums import InventoryType
from objects.components.inventory_type_tuning import InventoryTypeTuning
from objects.components.utils.inventory_helpers import transfer_object_to_lot_or_object_inventory, get_object_or_lot_inventory
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableVariant, TunableEnumEntry, TunableReference, TunableRange, TunableList, Tunable, OptionalTunable
import build_buy, event_testing, services, sims4.log
logger = sims4.log.Logger('Inventory', default_owner='tingyul')

def transfer_entire_inventory(source, recipient, interaction=None, object_tests=None, household_id=None, selected_objects_only=False, backup_recipient=None):
    if source is None or recipient is None:
        raise ValueError('Attempt to transfer items from {} to {}.'.format(source, recipient))
    else:
        lot = services.active_lot()
        if isinstance(source, InventoryType):
            source_inventories = lot.get_object_inventories(source)
        else:
            source_inventories = (
             source.inventory_component,)
    if len(source_inventories) == 0 or None in source_inventories:
        raise ValueError('Failed to find inventory component for source of inventory transfer: {}'.format(source))
    recipient_is_inventory_type = isinstance(recipient, InventoryType)
    recipient_object = None if recipient_is_inventory_type else recipient
    recipient_inventory = get_object_or_lot_inventory(recipient, household_id=household_id)
    if backup_recipient is not None:
        backup_recipient_is_inventory_type = isinstance(backup_recipient, InventoryType)
        backup_recipient_object = None if backup_recipient_is_inventory_type else backup_recipient
        backup_recipient_inventory = get_object_or_lot_inventory(backup_recipient, household_id=household_id)
    else:
        backup_recipient_inventory = None
        backup_recipient_object = None
    selected_objects = interaction.interaction_parameters.get('picked_item_ids', None) if interaction is not None else None
    for source_inventory in source_inventories:
        for obj in list(source_inventory):
            if selected_objects_only:
                if selected_objects is None or obj.id not in selected_objects:
                    continue
                else:
                    if interaction is not None:
                        if object_tests:
                            interaction.interaction_parameters['picked_item_ids'] = frozenset((obj.id,))
                            resolver = interaction.get_resolver()
                            if not object_tests.run_tests(resolver):
                                continue
                    source_inventory.try_remove_object_by_id((obj.id), count=(obj.stack_count())) or logger.warn('Failed to remove object {} from {} inventory', obj, source)
                    continue
                transfer_object_to_lot_or_object_inventory(obj, recipient_inventory, recipient_object=recipient_object, backup_recipient_inventory=backup_recipient_inventory,
                  backup_recipient_object=backup_recipient_object)


class InventoryTransfer(XevtTriggeredElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'description':'\n            Transfer all objects with a specified inventory type from the\n            specified inventory to the inventory of a specified participant.\n            ', 
     'source':TunableVariant(description='\n            The source of the inventory objects being transferred.\n            ',
       lot_inventory_type=TunableEnumEntry(description='\n                The inventory from which the objects will be transferred.\n                ',
       tunable_type=InventoryType,
       default=(InventoryType.UNDEFINED),
       invalid_enums=(
      InventoryType.UNDEFINED,)),
       participant=TunableEnumEntry(description='\n                The participant of the interaction whose inventory objects will\n                be transferred to the specified inventory.\n                ',
       tunable_type=ParticipantType,
       default=(ParticipantType.Object),
       invalid_enums=(
      ParticipantType.Invalid,))), 
     'recipient':TunableVariant(description='\n            The inventory that will receive the objects being transferred.\n            ',
       lot_inventory_type=TunableEnumEntry(description='\n                The inventory into which the objects will be transferred.\n                ',
       tunable_type=InventoryType,
       default=(InventoryType.UNDEFINED),
       invalid_enums=(
      InventoryType.UNDEFINED,)),
       participant=TunableEnumEntry(description='\n                The participant of the interaction who will receive the objects \n                being transferred.\n                ',
       tunable_type=ParticipantType,
       default=(ParticipantType.Object),
       invalid_enums=(
      ParticipantType.Invalid,))), 
     'backup_recipient':OptionalTunable(description='\n            Optionally set a backup inventory that will receive the objects being transferred\n            if the object cannot be stored on the recipient.\n            ',
       tunable=TunableVariant(description='\n                The inventory that will receive the objects being transferred as a backup.\n                ',
       lot_inventory_type=TunableEnumEntry(description='\n                    The inventory into which the objects will be transferred.\n                    ',
       tunable_type=InventoryType,
       default=(InventoryType.UNDEFINED),
       invalid_enums=(
      InventoryType.UNDEFINED,)),
       participant=TunableEnumEntry(description='\n                    The participant of the interaction who will receive the objects \n                    being transferred.\n                    ',
       tunable_type=ParticipantType,
       default=(ParticipantType.Object),
       invalid_enums=(
      ParticipantType.Invalid,)))), 
     'transfer_selected_objects_only':Tunable(description='\n            If checked then transfer only those items that are found in "picked_item_ids" from the source to the \n            recipient.\n            \n            This will only work if the picked_item_ids are set on the interaction running this element. If no\n            picked_item_ids are found then nothing will be transfered.\n            ',
       tunable_type=bool,
       default=False), 
     'object_tests':TunableTestSet(description='\n            Tests that will run on each object, and will transfer the object\n            only if all the tests pass.\n            \n            The object will be the PickedObject participant type, so we can\n            preserve the interaction resolver.\n            ')}

    def _do_behavior(self):
        if isinstance(self.source, ParticipantType):
            source = self.interaction.get_participant(self.source)
        else:
            source = self.source
        if isinstance(self.recipient, ParticipantType):
            recipient = self.interaction.get_participant(self.recipient)
        else:
            recipient = self.recipient
        if isinstance(self.backup_recipient, ParticipantType):
            backup_recipient = self.interaction.get_participant(self.backup_recipient)
        else:
            backup_recipient = self.backup_recipient
        transfer_entire_inventory(source, recipient, interaction=(self.interaction), object_tests=(self.object_tests), selected_objects_only=(self.transfer_selected_objects_only),
          backup_recipient=backup_recipient)


class InventoryTransferFakePerform(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'description':'\n            Transfer all objects with a specified inventory type from the\n            specified inventory to the inventory of a specified participant.\n            ', 
     'source':TunableEnumEntry(description='\n            The inventory from which the objects will be transferred.\n            ',
       tunable_type=InventoryType,
       default=InventoryType.UNDEFINED), 
     'recipient':TunableEnumEntry(description='\n            The inventory into which the objects will be transferred.\n            ',
       tunable_type=InventoryType,
       default=InventoryType.UNDEFINED)}

    def _do_behavior(self):
        household = services.owning_household_of_active_lot()
        household_id = None
        if household is not None:
            household_id = household.id
        transfer_entire_inventory((self.source), (self.recipient), interaction=None, household_id=household_id)


class PutObjectInMail(XevtTriggeredElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'description':'\n            Create an object of the specified type and place it in the hidden\n            inventory of the active lot so that it will be delivered along with\n            the mail.\n            ', 
     'object_to_be_mailed':TunableReference(description='\n            A reference to the type of object which will be sent to the hidden\n            inventory to be mailed.\n            ',
       manager=services.definition_manager(),
       pack_safe=True)}

    def _do_behavior(self):
        lot = services.active_lot()
        if lot is None:
            return
        lot.create_object_in_hidden_inventory(self.object_to_be_mailed.id)


class DeliverBill(XevtTriggeredElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'description': '\n            Let the bills manager know that a bill has been delivered and\n            trigger appropriate bill-specific functionality.\n            '}

    def _do_behavior(self):
        household = services.owning_household_of_active_lot()
        if household is None:
            return
        else:
            return household.bills_manager.can_deliver_bill or None
        household.bills_manager.trigger_bill_notifications_from_delivery()
        services.get_event_manager().process_events_for_household(TestEvent.BillsDelivered, household)


class DeliverBillFakePerform(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'description': '\n            Let the bills manager know that a bill has been delivered and\n            trigger appropriate bill-specific functionality.\n            '}

    def _do_behavior(self):
        household = services.owning_household_of_active_lot()
        if household is None:
            return
        else:
            return household.bills_manager.can_deliver_bill or None
        household.bills_manager.trigger_bill_notifications_from_delivery()
        services.get_event_manager().process_events_for_household(TestEvent.BillsDelivered, household)


class DestroySpecifiedObjectsFromTargetInventory(XevtTriggeredElement, HasTunableFactory, AutoFactoryInit):
    ALL = 'ALL'
    FACTORY_TUNABLES = {'description':'\n            Destroy every object in the target inventory that passes the tuned\n            tests.\n            ', 
     'inventory_owner':TunableEnumEntry(description='\n            The participant of the interaction whose inventory will be checked\n            for objects to destroy.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Object), 
     'object_tests':TunableTestSet(description='\n            A list of tests to apply to all objects in the target inventory.\n            Every object that passes these tests will be destroyed.\n            '), 
     'count':TunableVariant(description="\n            The max number of objects to destroy. For example: A Sim has 2\n            red guitars and 1 blue guitar, and we're destroying guitars with\n            count = 2. Possible destroyed objects are: 2 red guitars, or 1 red\n            guitar and 1 blue guitar.\n            ",
       number=TunableRange(tunable_type=int, default=1, minimum=0),
       locked_args={'all': ALL},
       default='all'), 
     'loots_to_run_before_destroy':TunableList(description='\n            A list of loots to be run before destroying the object. The loots\n            will have the tuned participant as the Actor and the object being\n            destroyed as the target.\n            ',
       tunable=TunableReference(description='\n                A reference to a loot to run against the object being destroyed.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.ACTION))))}

    def _do_behavior(self):
        participant = self.interaction.get_participant(self.inventory_owner)
        inventory = participant.inventory_component
        if inventory is None:
            logger.error('Participant {} does not have an inventory to check for objects to destroy.', participant,
              owner='tastle')
            return
        objects_to_destroy = set()
        for obj in inventory:
            single_object_resolver = event_testing.resolver.SingleObjectResolver(obj)
            if not self.object_tests.run_tests(single_object_resolver):
                continue
            objects_to_destroy.add(obj)

        num_destroyed = 0
        for obj in objects_to_destroy:
            if self.count == self.ALL:
                count = obj.stack_count()
            else:
                count = min(self.count - num_destroyed, obj.stack_count())
            resolver = SingleActorAndObjectResolver(participant.sim_info, obj, self) if participant.is_sim else DoubleObjectResolver(obj, self)
            for loot in self.loots_to_run_before_destroy:
                loot.apply_to_resolver(resolver)

            if not inventory.try_destroy_object(obj, count=count, source=inventory, cause='Destroying specified objects from target inventory extra.'):
                logger.error('Error trying to destroy object {}.', obj, owner='tastle')
            num_destroyed += count
            if self.count != self.ALL and num_destroyed >= self.count:
                break

        objects_to_destroy.clear()