# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\chalet_garden\chalet_garden_zone_director.py
# Compiled at: 2016-09-27 18:15:23
# Size of source mod 2**32: 484 bytes
from venues.scheduling_zone_director import SchedulingZoneDirector
from venues.visitor_situation_on_arrival_zone_director_mixin import VisitorSituationOnArrivalZoneDirectorMixin

class ChaletGardenZoneDirector(VisitorSituationOnArrivalZoneDirectorMixin, SchedulingZoneDirector):
    pass