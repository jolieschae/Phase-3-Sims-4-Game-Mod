# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\buffs\burnout_buff.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 1649 bytes
import itertools, sims4
from buffs.buff import Buff
from buffs.buff_display_type import BuffDisplayType
from careers.career_enums import CareerCategory
logger = sims4.log.Logger('BurnoutBuff', default_owner='jsampson')

class BurnoutBuff(Buff):

    @property
    def display_type(self):
        return BuffDisplayType.BURNOUT

    def on_add(self, *args, **kwargs):
        (super().on_add)(*args, **kwargs)
        self._send_career_update_message()

    def on_remove(self, *args, **kwargs):
        (super().on_remove)(*args, **kwargs)
        self._send_career_update_message()

    def _send_career_update_message(self):
        career_tracker = self._owner.career_tracker
        if career_tracker is None:
            return
        careers_work_gen = career_tracker.get_careers_by_category_gen(CareerCategory.Work)
        careers_adult_part_time_gen = career_tracker.get_careers_by_category_gen(CareerCategory.AdultPartTime)
        careers = list(itertools.chain(careers_work_gen, careers_adult_part_time_gen))
        if len(careers) == 0:
            return
        careers[0].resend_career_data()