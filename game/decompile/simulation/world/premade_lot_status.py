# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\premade_lot_status.py
# Compiled at: 2015-02-11 19:32:15
# Size of source mod 2**32: 535 bytes
import enum

class PremadeLotStatus(enum.Int):
    NOT_TRACKED = 0
    IS_PREMADE = 1
    NOT_PREMADE = 2
    export = False