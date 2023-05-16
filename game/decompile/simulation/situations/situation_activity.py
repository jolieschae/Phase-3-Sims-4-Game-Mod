# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_activity.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 1489 bytes
from holidays.holiday_tradition import HolidayTradition, TraditionType
from sims4.tuning.instances import lock_instance_tunables

class SituationActivity(HolidayTradition):
    REMOVE_INSTANCE_TUNABLES = ('pre_holiday_buffs', 'pre_holiday_buff_reason', 'holiday_buffs',
                                'holiday_buff_reason', 'drama_nodes_to_score', 'drama_nodes_to_run',
                                'additional_walkbys', 'preference', 'preference_reward_buff',
                                'lifecycle_actions', 'events', 'core_object_tags',
                                'deco_object_tags', 'business_cost_multiplier')