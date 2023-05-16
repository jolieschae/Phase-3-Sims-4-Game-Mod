# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\lot_decoration\lot_decoration_enums.py
# Compiled at: 2018-03-07 14:29:55
# Size of source mod 2**32: 566 bytes
import enum
from sims4.tuning.dynamic_enum import DynamicEnum

class DecorationLocation(enum.Int):
    FOUNDATIONS = 0
    EAVES = 1
    FRIEZES = 2
    FENCES = 3
    SPANDRELS = 4
    COLUMNS = 5


class DecorationPickerCategory(DynamicEnum):
    ALL = 0


LOT_DECORATION_DEFAULT_ID = 0