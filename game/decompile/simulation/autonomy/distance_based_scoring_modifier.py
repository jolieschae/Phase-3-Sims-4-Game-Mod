# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\autonomy\distance_based_scoring_modifier.py
# Compiled at: 2022-02-09 13:21:46
# Size of source mod 2**32: 1756 bytes
import sims4
logger = sims4.log.Logger('DistanceBasedScoringModifier', default_owner='uviswavasu')

class DistanceToObjectBasedScoringModifier:

    def __init__(self, modifier):
        self.object_tag = modifier.object_tag
        self._distance_to_multiplier_map = []
        for mapping in modifier.distance_to_multiplier_map:
            self._distance_to_multiplier_map.append(tuple((mapping.distance_threshold, mapping.multiplier)))

        self._distance_to_multiplier_map.sort()
        self._outside_threshold_multiplier = modifier.outside_threshold_multiplier
        self._reference_count = 1

    def get_multiplier_for_distance(self, dist):
        for distance, multiplier in self._distance_to_multiplier_map:
            if dist < distance:
                return multiplier ** self._reference_count

        return self._outside_threshold_multiplier ** self._reference_count

    def increase_ref_count(self):
        self._reference_count += 1

    def decrease_ref_count(self):
        self._reference_count -= 1

    def get_ref_count(self):
        return self._reference_count