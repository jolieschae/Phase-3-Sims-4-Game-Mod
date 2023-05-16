# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\awareness\awareness_enums.py
# Compiled at: 2016-07-25 15:29:27
# Size of source mod 2**32: 1449 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
import enum

class AwarenessChannel(DynamicEnum, dynamic_max_length=10, dynamic_offset=1000):
    PROXIMITY = 0
    AUDIO_VOLUME = 1

    def get_type_name(self):
        return str(self).split('.')[-1].lower()


class AwarenessChannelEvaluationType(enum.Int):
    PEAK = 0
    AVERAGE = 1
    SUM = 2