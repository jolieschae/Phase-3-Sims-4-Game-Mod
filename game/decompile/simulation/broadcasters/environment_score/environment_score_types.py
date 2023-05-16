# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\broadcasters\environment_score\environment_score_types.py
# Compiled at: 2014-06-11 19:40:18
# Size of source mod 2**32: 335 bytes
import enum

class EnvironmentScoreType(enum.Int):
    MOOD_SCORING = 1
    NEGATIVE_SCORING = 2
    POSITIVE_SCORING = 3