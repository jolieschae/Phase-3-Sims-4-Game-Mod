# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\formation\formation_liability.py
# Compiled at: 2017-10-06 20:49:24
# Size of source mod 2**32: 727 bytes
from interactions.liability import ReplaceableLiability

class RoutingFormationLiability(ReplaceableLiability):
    LIABILITY_TOKEN = 'RoutingFormationLiability'

    def __init__(self, routing_formation_data, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._routing_formation_data = routing_formation_data

    def release(self):
        self._routing_formation_data.release_formation_data()