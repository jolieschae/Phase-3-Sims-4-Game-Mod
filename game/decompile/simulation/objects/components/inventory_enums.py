# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\inventory_enums.py
# Compiled at: 2018-11-26 22:20:18
# Size of source mod 2**32: 2927 bytes
from sims4.tuning.dynamic_enum import DynamicEnumLocked, DynamicEnum
import enum, sims4.log
logger = sims4.log.Logger('Inventory Enums')

class InventoryType(DynamicEnumLocked):
    UNDEFINED = 0
    SIM = 1
    HIDDEN = 2
    FISHBOWL = 3
    MAILBOX = 4
    FRIDGE = 5
    BOOKSHELF = 6
    TOYBOX = 7
    COMPUTER = 8
    TRASHCAN = 9
    SINK = 10
    COLLECTION_ELEMENT_SHELVE = 11
    RETAIL_FRIDGE = 12
    RETAIL_SHELF = 13
    BAKING_WARMINGRACK = 14
    AQUARIUM_STANDARD = 15
    STORAGE_CHEST = 16
    COLLECTION_SKULL_DISPLAY = 17
    CRAFT_SALES_TABLE_EP03 = 18
    CRAFT_SALES_TABLE_PAINTINGS_EP03 = 19
    SACK_GP05 = 20
    HIDINGSPOT_GP05 = 21
    PET_TOYBOX = 22
    AUTOPETFEEDER = 23
    MEDICINESTATION = 24
    VET_MEDICINE_VENDING_MACHINE = 25
    LAUNDRY_STORAGE = 26


class StackScheme(DynamicEnum):
    NONE = ...
    VARIANT_GROUP = ...
    DEFINITION = ...


class ObjectShareability(enum.Int):
    NOT_SHARED = ...
    SHARED_IF_NOT_IN_APARTMENT = ...
    SHARED = ...


class InventoryItemClaimStatus(enum.Int, export=False):
    UNCLAIMED = 0
    CLAIMED = 1