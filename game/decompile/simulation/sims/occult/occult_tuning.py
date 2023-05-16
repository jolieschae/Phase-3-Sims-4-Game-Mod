# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\occult\occult_tuning.py
# Compiled at: 2016-08-22 18:48:09
# Size of source mod 2**32: 402 bytes
from traits.traits import Trait

class OccultTuning:
    NO_OCCULT_TRAIT = Trait.TunableReference(description='\n        The trait that indicates a sim has no occult type.\n        ')