# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\career_history.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 5808 bytes
from date_and_time import DateAndTime
import services, sims4.resources

class CareerHistory:

    def __init__(self, *, career_track, level, user_level, overmax_level, highest_level, time_of_leave, daily_pay, days_worked, active_days_worked, player_rewards_deferred, schedule_shift_type):
        self._career_track = career_track
        self._level = level
        self._user_level = user_level
        self._overmax_level = overmax_level
        self._highest_level = highest_level
        self._time_of_leave = time_of_leave
        self._daily_pay = daily_pay
        self._days_worked = days_worked
        self._active_days_worked = active_days_worked
        self._player_rewards_deferred = player_rewards_deferred
        self._schedule_shift_type = schedule_shift_type

    @property
    def career_track(self):
        return self._career_track

    @property
    def level(self):
        return self._level

    @property
    def user_level(self):
        return self._user_level

    @property
    def overmax_level(self):
        return self._overmax_level

    @property
    def highest_level(self):
        return self._highest_level

    @property
    def time_of_leave(self):
        return self._time_of_leave

    @property
    def daily_pay(self):
        return self._daily_pay

    @property
    def days_worked(self):
        return self._days_worked

    @property
    def active_days_worked(self):
        return self._active_days_worked

    @property
    def deferred_rewards(self):
        return self._player_rewards_deferred

    def save_career_history(self, career_history_proto):
        career_history_proto.track_level = self._level
        career_history_proto.user_display_level = self._user_level
        career_history_proto.overmax_level = self._overmax_level
        career_history_proto.highest_level = self._highest_level
        career_history_proto.time_left = self._time_of_leave.absolute_ticks()
        career_history_proto.daily_pay = self._daily_pay
        career_history_proto.days_worked = int(self._days_worked)
        career_history_proto.active_days_worked = int(self._active_days_worked)
        career_history_proto.player_rewards_deferred = self._player_rewards_deferred
        career_history_proto.schedule_shift_type = self._schedule_shift_type

    @staticmethod
    def load_career_history(sim_info, career_history_proto):
        career = services.get_instance_manager(sims4.resources.Types.CAREER).get(career_history_proto.career_uid)
        if career is None:
            return
        career_track = services.get_instance_manager(sims4.resources.Types.CAREER_TRACK).get(career_history_proto.track_uid)
        if career_track is None:
            return
        level = career_history_proto.track_level
        user_level = career_history_proto.user_display_level
        overmax_level = career_history_proto.overmax_level
        highest_level = career_history_proto.highest_level
        daily_pay = career_history_proto.daily_pay
        if daily_pay == 0:
            daily_pay = career.get_daily_pay(sim_info=sim_info, career_track=career_track, career_level=level,
              overmax_level=overmax_level)
        deferred_rewards = career_history_proto.player_rewards_deferred
        return CareerHistory(career_track=career_track, level=level,
          user_level=user_level,
          overmax_level=overmax_level,
          highest_level=highest_level,
          time_of_leave=(DateAndTime(career_history_proto.time_left)),
          daily_pay=daily_pay,
          days_worked=(career_history_proto.days_worked),
          active_days_worked=(career_history_proto.active_days_worked),
          player_rewards_deferred=deferred_rewards,
          schedule_shift_type=(career_history_proto.schedule_shift_type))