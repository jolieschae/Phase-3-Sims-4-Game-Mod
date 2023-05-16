# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\portals\portal_data_object_ladders.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 1046 bytes
from routing.portals.portal_data_build_ladders import _PortalTypeDataBuildLadders

class _PortalTypeDataObjectLadders(_PortalTypeDataBuildLadders):

    def _get_num_rungs(self, ladder):
        rung_start = self.climb_up_locations.location_start(ladder).position.y
        rung_end = self.climb_up_locations.location_end(ladder).position.y - self.ladder_rung_distance
        return (rung_end - rung_start) // self.ladder_rung_distance + 1

    def _get_top_and_bottom_levels(self, obj):
        obj_level = obj.location.level
        return (obj_level, obj_level)

    def _get_blocked_alignment_flags(self, obj):
        return 0