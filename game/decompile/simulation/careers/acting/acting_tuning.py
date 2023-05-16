# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\acting\acting_tuning.py
# Compiled at: 2018-04-03 17:58:38
# Size of source mod 2**32: 504 bytes
from sims4.tuning.tunable import TunablePackSafeLotDescription

class ActingTuning:
    STUDIO_LOT_DESCRIPTION = TunablePackSafeLotDescription(description='\n        A reference to the lot description file for the acting studio lot. This\n        is used for easier zone ID lookups.\n        ')