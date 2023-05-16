# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\gym_zone_director.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 518 bytes
from situations.complex.yoga_class import YogaClassScheduleMixin
from venues.scheduling_zone_director import SchedulingZoneDirector
from venues.visitor_situation_on_arrival_zone_director_mixin import VisitorSituationOnArrivalZoneDirectorMixin

class GymZoneDirector(VisitorSituationOnArrivalZoneDirectorMixin, SchedulingZoneDirector):
    pass