# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\holidays\holiday_loot_ops.py
# Compiled at: 2021-05-13 21:21:00
# Size of source mod 2**32: 1192 bytes
import services, sims4
from drama_scheduler.drama_node_types import DramaNodeType
from interactions.utils.loot_basic_op import BaseTargetedLootOperation
logger = sims4.log.Logger('HolidayLootOps', default_owner='amwu')

class HolidaySearchLootOp(BaseTargetedLootOperation):

    def _apply_to_subject_and_target(self, subject, target, resolver):
        active_household = services.active_household()
        if active_household is None:
            return
        active_holiday_id = active_household.holiday_tracker.active_holiday_id
        if active_holiday_id is None:
            return
        for drama_node in services.drama_scheduler_service().active_nodes_gen():
            if drama_node.drama_node_type != DramaNodeType.HOLIDAY:
                continue
            if drama_node.holiday_id != active_holiday_id:
                continue
            if drama_node.drama_node_type == DramaNodeType.HOLIDAY:
                drama_node.search_obj(target.id)
                break