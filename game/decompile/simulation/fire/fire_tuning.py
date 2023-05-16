# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\fire\fire_tuning.py
# Compiled at: 2017-04-21 15:24:14
# Size of source mod 2**32: 551 bytes
from sims4.tuning.tunable import TunableEnumWithFilter
from tag import Tag

class FireTuning:
    FLAMMABLE_TAG = TunableEnumWithFilter(description='\n        Define a tag that is automatically added to all objects that are\n        flammable.\n        ',
      tunable_type=Tag,
      default=(Tag.INVALID),
      invalid_enums=(
     Tag.INVALID,),
      filter_prefixes=('Fire', ))