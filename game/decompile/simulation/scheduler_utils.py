# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\scheduler_utils.py
# Compiled at: 2019-09-11 14:40:52
# Size of source mod 2**32: 1308 bytes
from sims4.tuning.tunable import TunableSingletonFactory, Tunable
from tunable_time import Days

def convert_string_to_enum(**day_availability_mapping):
    day_availability_dict = {}
    for day in Days:
        name = '{} {}'.format(int(day), day.name)
        available = day_availability_mapping[name]
        day_availability_dict[day] = available

    return day_availability_dict


class TunableAvailableDays(TunableSingletonFactory):
    FACTORY_TYPE = staticmethod(convert_string_to_enum)


def TunableDayAvailability():
    day_availability_mapping = {}
    for day in Days:
        name = '{} {}'.format(int(day), day.name)
        day_availability_mapping[name] = Tunable(bool, False)

    day_availability = TunableAvailableDays(description='Which days of the week to include', **day_availability_mapping)
    return day_availability