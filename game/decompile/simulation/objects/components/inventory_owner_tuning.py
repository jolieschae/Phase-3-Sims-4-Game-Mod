# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\inventory_owner_tuning.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 532 bytes
from objects.components.state_references import TunableStateValueReference
from sims4.tuning.tunable import TunableList

class InventoryTuning:
    INVALID_ACCESS_STATES = TunableList(TunableStateValueReference(description='\n        If an inventory owner is in any of the states tuned here, it will not\n        be available to grab objects out of.\n        ',
      pack_safe=True))