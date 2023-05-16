# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\hidden_inventory_tuning.py
# Compiled at: 2018-07-12 21:24:19
# Size of source mod 2**32: 1848 bytes
from interactions.utils.loot_basic_op import BaseTargetedLootOperation
from sims4.tuning.tunable import HasTunableSingletonFactory, TunableVariant

class MoveToHiddenInventory(HasTunableSingletonFactory):

    def _run(self, obj):
        inventory = obj.get_inventory()
        if inventory is not None:
            inventory.try_move_object_to_hidden_inventory(obj)


class MoveFromHiddenInventory(HasTunableSingletonFactory):

    def _run(self, obj):
        inventory = obj.get_inventory()
        if inventory is not None:
            inventory.try_move_hidden_object_to_inventory(obj)


class HiddenInventoryTransferLoot(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'transfer_type': TunableVariant(description='\n            The type of hidden inventory transfer to perform.\n            ',
                        move_to_hidden_inventory=(MoveToHiddenInventory.TunableFactory()),
                        move_from_hidden_inventory=(MoveFromHiddenInventory.TunableFactory()),
                        default='move_to_hidden_inventory')}

    def __init__(self, *args, transfer_type, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.transfer_type = transfer_type

    def _apply_to_subject_and_target(self, subject, target, resolver):
        self.transfer_type._run(target)