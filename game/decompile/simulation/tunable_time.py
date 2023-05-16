# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\tunable_time.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 9341 bytes
import operator
from sims4.tuning.tunable import TunableRange, TunableMapping, HasTunableSingletonFactory, TunableFactory
import date_and_time, enum, sims4.tuning.tunable

class Days(enum.Int):
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6


def date_and_time_from_hours_minutes(hour, minute):
    return date_and_time.create_date_and_time(hours=hour, minutes=minute)


def date_and_time_from_days_hours_minutes(day, hour, minute):
    return date_and_time.create_date_and_time(days=day, hours=hour, minutes=minute)


def time_span_from_days_hours_minutes(days, hours, minutes):
    return date_and_time.create_time_span(days=days, hours=hours, minutes=minutes)


class TunableTimeOfDay(sims4.tuning.tunable.TunableSingletonFactory):
    __slots__ = ()
    FACTORY_TYPE = staticmethod(date_and_time_from_hours_minutes)

    def __init__(self, description='An Hour(24Hr) and Minute representing a time relative to the beginning of a day.', default_hour=12, default_minute=0, **kwargs):
        (super().__init__)(hour=sims4.tuning.tunable.TunableRange(int, default_hour, 0, 23, description='Hour of the day'), 
         minute=sims4.tuning.tunable.TunableRange(int, default_minute, 0, 59, description='Minute of Hour'), 
         description=description, **kwargs)


class TunableTimeOfWeek(sims4.tuning.tunable.TunableFactory):
    __slots__ = ()
    FACTORY_TYPE = staticmethod(date_and_time_from_days_hours_minutes)

    def __init__(self, description='A Day, Hour(24hr) and Minute representing a time relative to the beginning of a week.', default_day=Days.SUNDAY, default_hour=12, default_minute=0, **kwargs):
        (super().__init__)(day=sims4.tuning.tunable.TunableEnumEntry(Days, default_day, needs_tuning=True, description='Day of the week'), 
         hour=sims4.tuning.tunable.TunableRange(int, default_hour, 0, 23, description='Hour of the day'), 
         minute=sims4.tuning.tunable.TunableRange(int, default_minute, 0, 59, description='Minute of Hour'), 
         description=description, **kwargs)


class TunableTimeSpan(sims4.tuning.tunable.TunableFactory):
    __slots__ = ()
    FACTORY_TYPE = staticmethod(time_span_from_days_hours_minutes)

    def __init__(self, description='A duration that may be specified in weeks/days/hours/minutes.', default_days=0, default_hours=0, default_minutes=0, **kwargs):
        (super().__init__)(days=TunableRange(description='Number of days', tunable_type=int,
  default=default_days,
  minimum=0), 
         hours=TunableRange(description='Number of hours', tunable_type=int,
  default=default_hours,
  minimum=0,
  maximum=23), 
         minutes=TunableRange(description='Number of minutes', tunable_type=int,
  default=default_minutes,
  minimum=0,
  maximum=59), 
         description=description, **kwargs)


class TunableTimeSpanSingleton(sims4.tuning.tunable.TunableSingletonFactory):
    __slots__ = ()
    FACTORY_TYPE = staticmethod(time_span_from_days_hours_minutes)

    def __init__(self, description='A duration that may be specified in weeks/days/hours/minutes.', default_days=0, default_hours=0, default_minutes=0, **kwargs):
        (super().__init__)(days=TunableRange(description='Number of days', tunable_type=int,
  default=default_days,
  minimum=0), 
         hours=TunableRange(description='Number of hours', tunable_type=int,
  default=default_hours,
  minimum=0,
  maximum=23), 
         minutes=TunableRange(description='Number of minutes', tunable_type=int,
  default=default_minutes,
  minimum=0,
  maximum=59), 
         description=description, **kwargs)


class TimeOfDayMap:

    def __init__(self, hours, **kwargs):
        time_of_day_list = []
        for hour, minute_map in hours.items():
            for minute, entry in minute_map.items():
                time_of_day_list.append((date_and_time_from_hours_minutes(hour, minute), entry))

        time_of_day_list.sort(key=(operator.itemgetter(0)))
        self._time_of_day_map = tuple(time_of_day_list)

    def get_entry_data(self, time_of_day):
        time_of_current_day = time_of_day.time_of_day()
        found_entry = None
        current_time = date_and_time.DATE_AND_TIME_ZERO
        next_time = date_and_time.DATE_AND_TIME_ZERO + date_and_time.create_time_span(hours=24)
        for entry in self._time_of_day_map:
            if entry[0] <= time_of_current_day:
                found_entry = entry[1]
                current_time = entry[0]
            else:
                next_time = entry[0]
                break

        return (
         found_entry, current_time, next_time)


class TunableTimeOfDayMapping(HasTunableSingletonFactory):

    @TunableFactory.factory_option
    def hours(value_type='', value_name=None):
        return TunableMapping(description='\n                Hours of the map.\n                ',
          key_name='hour_of_day',
          key_type=TunableRange(tunable_type=int,
          default=0,
          minimum=0,
          maximum=23),
          value_name='Minute_of_hour',
          value_type=TunableMapping(description='\n                    Minutes of the map.\n                    ',
          key_name='minute_of_hour',
          key_type=TunableRange(tunable_type=int,
          default=0,
          minimum=0,
          maximum=59),
          value_name=value_name,
          value_type=value_type,
          minlength=1))

    def __init__(self, hours, **kwargs):
        time_of_day_list = []
        for hour, minute_map in hours.items():
            for minute, entry in minute_map.items():
                time_of_day_list.append((date_and_time_from_hours_minutes(hour, minute), entry))

        time_of_day_list.sort(key=(operator.itemgetter(0)))
        self._time_of_day_map = tuple(time_of_day_list)

    def get_entry_data(self, time_of_day):
        time_of_current_day = time_of_day.time_of_day()
        found_entry = None
        current_time = date_and_time.DATE_AND_TIME_ZERO
        next_time = date_and_time.DATE_AND_TIME_ZERO + date_and_time.create_time_span(hours=24)
        for entry_time_of_day, entry in self._time_of_day_map:
            if entry_time_of_day <= time_of_current_day:
                found_entry = entry
                current_time = entry_time_of_day
            else:
                next_time = entry_time_of_day
                break

        return (
         found_entry, current_time, next_time)