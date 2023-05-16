# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\trends\trend_service.py
# Compiled at: 2018-07-31 19:05:09
# Size of source mod 2**32: 4505 bytes
from _collections import defaultdict
import operator, random
from date_and_time import TimeUnit
from persistence_error_types import ErrorCodes
from sims4.localization import LocalizationHelperTuning
from sims4.service_manager import Service
from sims4.utils import classproperty
from trends.trend_tuning import TrendTuning
import date_and_time, services

class TrendService(Service):

    def __init__(self):
        self._current_trends = []
        self._update_ticks = 0

    @classproperty
    def save_error_code(cls):
        return ErrorCodes.SERVICE_SAVE_FAILED_TREND_SERVICE

    def save(self, save_slot_data=None, **kwargs):
        trend_data = save_slot_data.gameplay_data.trend_service
        trend_data.Clear()
        trend_data.current_trend_tags.extend(self.get_current_trend_tags())
        trend_data.next_update_ticks = self._update_ticks

    def load(self, zone_data=None):
        save_slot_data = services.get_persistence_service().get_save_slot_proto_buff()
        msg = save_slot_data.gameplay_data.trend_service
        self._current_trends.extend([datum for datum in TrendTuning.TREND_DATA if datum.trend_tag in msg.current_trend_tags])
        self._update_ticks = msg.next_update_ticks

    def _update_trends(self):
        now_ticks = services.time_service().sim_now.absolute_ticks()
        if now_ticks >= self._update_ticks:
            self._pick_new_trends()
            self._update_ticks = now_ticks + TrendTuning.TREND_REFRESH_COOLDOWN().in_ticks()

    def _pick_new_trends(self):
        new_trends = []
        potential_trends = [trend_datum for trend_datum in TrendTuning.TREND_DATA if trend_datum.trend_tag not in self._current_trends]
        new_trends.append(potential_trends.pop(random.randint(0, len(potential_trends) - 1)))
        trends_by_type = defaultdict(list)
        for trend_datum in potential_trends:
            trends_by_type[trend_datum.trend_type].append(trend_datum)

        for trend_data in trends_by_type.values():
            new_trends.append(random.choice(trend_data))

        self._current_trends = new_trends

    def _get_description_string(self):
        now_ticks = services.time_service().sim_now.absolute_ticks()
        hours_remaining = date_and_time.ticks_to_time_unit(self._update_ticks - now_ticks, TimeUnit.HOURS, True)
        sorted_thresholds = sorted((TrendTuning.TREND_TIME_REMAINING_DESCRIPTION.items()), key=(operator.itemgetter(0)))
        for threshold, loc_string in sorted_thresholds:
            if threshold <= hours_remaining:
                continue
            return loc_string

    def get_current_trends_loc_string(self):
        self._update_trends()
        trend_list = (LocalizationHelperTuning.get_bulleted_list)(*(None, ), *(trend.trend_name for trend in self._current_trends))
        return LocalizationHelperTuning.get_new_line_separated_strings(trend_list, self._get_description_string())

    def get_current_trend_tags(self):
        self._update_trends()
        return [trend.trend_tag for trend in self._current_trends]