# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\object_routing\object_routing_priority.py
# Compiled at: 2020-10-21 14:55:11
# Size of source mod 2**32: 2444 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
from sims4.tuning.tunable import TunableMapping, TunableRange, TunableEnumEntry

class ObjectRoutingPriority(DynamicEnum):
    NONE = 0
    CRITICAL = 1

    @staticmethod
    def compare(x, y):
        if x == y:
            return 0
        if x == ObjectRoutingPriority.CRITICAL or y == ObjectRoutingPriority.NONE:
            return -1
        if x == ObjectRoutingPriority.NONE or y == ObjectRoutingPriority.CRITICAL:
            return 1
        value_map = ObjectRoutingPriorityTuning.PRIORITY_SCORE_VALUE
        return value_map[y] - value_map[x]

    @staticmethod
    def get_priority_value_string(priority):
        if priority is ObjectRoutingPriority.NONE:
            return 'Min'
        if priority is ObjectRoutingPriority.CRITICAL:
            return 'Max'
        return str(ObjectRoutingPriorityTuning.PRIORITY_SCORE_VALUE[priority])


class ObjectRoutingPriorityTuning:
    PRIORITY_SCORE_VALUE = TunableMapping(description='\n        A mapping of ObjectRoutingPriority to a numerical value.\n        ',
      key_type=TunableEnumEntry(tunable_type=ObjectRoutingPriority,
      default=(ObjectRoutingPriority.NONE),
      invalid_enums=(
     ObjectRoutingPriority.NONE, ObjectRoutingPriority.CRITICAL)),
      value_type=TunableRange(description='\n            The value associated with this ObjectRoutingPriority. ObjectRoutingBehaviors with a higher value\n            priority will be allowed to route more often when at the routing SoftCap.\n            ',
      tunable_type=float,
      default=1,
      minimum=0))