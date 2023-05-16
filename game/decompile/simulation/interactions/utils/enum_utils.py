# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\enum_utils.py
# Compiled at: 2014-11-13 16:48:39
# Size of source mod 2**32: 311 bytes


class FlagField:

    def __init__(self, initial_value=0):
        self.flags = initial_value