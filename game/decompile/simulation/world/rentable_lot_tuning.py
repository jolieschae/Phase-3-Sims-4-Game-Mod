# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\rentable_lot_tuning.py
# Compiled at: 2014-09-08 18:07:16
# Size of source mod 2**32: 925 bytes
from sims4.tuning.tunable import TunableTuple, Tunable
from sims4.tuning.tunable_base import ExportModes

class RentableZoneTuning:
    PRICE_MODIFIERS = TunableTuple(description='\n        Global price modifiers for all rentable zones.\n        ',
      add=Tunable(description='\n            Add modifier for the price to rent a lot.\n            ',
      tunable_type=float,
      default=0.0),
      multiply=Tunable(description='\n            Multiplier for the price to rent a lot.\n            ',
      tunable_type=float,
      default=1.0),
      export_class_name='TunablePriceModifiers',
      export_modes=(ExportModes.All))