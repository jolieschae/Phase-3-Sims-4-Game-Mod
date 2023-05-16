# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\conditional_layers\conditional_layer_enums.py
# Compiled at: 2021-05-21 19:15:16
# Size of source mod 2**32: 514 bytes
import enum

class ConditionalLayerRequestSpeedType(enum.Int, export=False):
    GRADUALLY = ...
    IMMEDIATELY = ...


class ConditionalLayerRequestType(enum.Int, export=False):
    LOAD_LAYER = ...
    DESTROY_LAYER = ...