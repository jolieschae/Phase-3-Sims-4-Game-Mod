# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\household_inventory_management.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 9567 bytes
from interactions import ParticipantType
from interactions.interaction_finisher import FinishingType
from interactions.utils.interaction_elements import XevtTriggeredElement
from sims4.tuning.tunable import HasTunableFactory, TunableEnumEntry, Tunable, TunableVariant, TunableTuple
import build_buy, services, sims4.log
logger = sims4.log.Logger('SendToInventory', default_owner='stjulien')

class SendToInventory(XevtTriggeredElement, HasTunableFactory):
    PARTICIPANT_INVENTORY = 'inventory_participant'
    HOUSEHOLD_INVENTORY = 'inventory_household'
    MAILBOX_INVENTORY = 'inventory_mailbox'
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            The participant(s) of the interaction who will be sent to the specified\n            inventory.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Object), 
     'inventory':TunableVariant(description='\n            The inventory location we want to send the participant to. \n            ',
       participant_inventory=TunableTuple(description="\n                Send the object to a participant's inventory. If the inventory\n                participant is a Sim, we will set the owner of the participant\n                to the Sim's household.\n                ",
       participant=TunableEnumEntry(description='\n                    The participant whose inventory we want to use.\n                    ',
       tunable_type=ParticipantType,
       default=(ParticipantType.Actor)),
       fallback_to_household=Tunable(description='\n                    If enabled and the object fails to add to the participant\n                    inventory, we will fallback to the owning household\n                    inventory.\n                    ',
       tunable_type=bool,
       default=False),
       locked_args={'inventory_type': PARTICIPANT_INVENTORY}),
       household_inventory=TunableTuple(description='\n                Send the object to the household inventory of its owner.\n                ',
       locked_args={'inventory_type': HOUSEHOLD_INVENTORY}),
       mailbox_inventory=TunableTuple(description='\n                Send the object to the hidden inventory of the owners home lot, to be later delivered to the mailbox.\n                ',
       locked_args={'inventory_type': MAILBOX_INVENTORY}),
       default='participant_inventory'), 
     'give_sim_ownership':Tunable(description='\n            If True and the recipient of this transfer is a sim inventory, we\n            will also transfer sim ownership of the object as well as household\n            ownership. This can be used if we want to change the OwnerSim of\n            the object.\n            ',
       tunable_type=bool,
       default=False), 
     'give_sim_inventory_ownership':Tunable(description='\n            Behaves like give sim ownership, but for all the objects in the target objects inventory.\n            ',
       tunable_type=bool,
       default=False)}

    def _do_behavior(self):
        sim = self.interaction.sim
        targets = [target for target in self.interaction.get_participants(self.participant) if target is not None]
        if not targets:
            return False
        for target in targets:
            if target.is_in_inventory():
                inventory = target.get_inventory()
                inventory.try_remove_object_by_id(target.id)

        if self.inventory.inventory_type == SendToInventory.MAILBOX_INVENTORY:
            inventory_participant = sim
            if not inventory_participant.is_sim:
                logger.error('Trying to add item(s) to a mailbox but the participant [{}] is not a sim', inventory_participant)
                return False
            zone = services.get_zone(inventory_participant.household.home_zone_id)
            if zone is None:
                logger.error('Trying to add item(s) to a mailbox but the provided sim [{}] has no home zone.', inventory_participant)
                return False
            lot_hidden_inventory = zone.lot.get_hidden_inventory()
            if lot_hidden_inventory is None:
                logger.error("Trying to add item(s) to the lot's hidden inventory but the provided sim [{}] has no hidden inventory for their lot.", inventory_participant)
                return False
            for target in targets:
                target.set_household_owner_id(inventory_participant.household_id)
                lot_hidden_inventory.system_add_object(target)
                for interaction in tuple(target.interaction_refs):
                    if not interaction.running:
                        if interaction.is_finishing:
                            continue
                        interaction.cancel((FinishingType.OBJECT_CHANGED), cancel_reason_msg='Object moved to inventory')

            return True
        for target in targets:
            should_fallback = False
            inventory_participant = sim
            if self.inventory.inventory_type == SendToInventory.PARTICIPANT_INVENTORY:
                inventory_participant = self.interaction.get_participant(self.inventory.participant)
                if inventory_participant.is_sim:
                    target.update_ownership(inventory_participant, make_sim_owner=(self.give_sim_ownership),
                      make_sim_inventory_owner=(self.give_sim_inventory_ownership))
                else:
                    inventory_participant.try_split_object_from_stack()
                inventory_component = inventory_participant.inventory_component
                if not inventory_component.player_try_add_object(target):
                    should_fallback = self.inventory.fallback_to_household
                else:
                    for interaction in tuple(target.interaction_refs):
                        if interaction.running or interaction.is_finishing:
                            continue
                        if inventory_participant.is_sim:
                            if not interaction.allow_from_sim_inventory:
                                interaction.cancel((FinishingType.OBJECT_CHANGED), cancel_reason_msg='Object moved to inventory')
                        else:
                            interaction.allow_from_object_inventory or interaction.cancel((FinishingType.OBJECT_CHANGED), cancel_reason_msg='Object moved to inventory')

            if not self.inventory.inventory_type == SendToInventory.HOUSEHOLD_INVENTORY:
                if should_fallback:

                    def on_reservation_change(*_, **__):
                        if not target.in_use:
                            target.unregister_on_use_list_changed(on_reservation_change)
                            build_buy.move_object_to_household_inventory(target)

                    if target is self.interaction.target:
                        self.interaction.set_target(None)
                if inventory_participant is not None:
                    if inventory_participant.is_sim:
                        target.set_household_owner_id(inventory_participant.household_id)
                    target.remove_from_client(fade_duration=(target.FADE_DURATION))
                    if target.in_use:
                        target.register_on_use_list_changed(on_reservation_change)
                else:
                    build_buy.move_object_to_household_inventory(target)