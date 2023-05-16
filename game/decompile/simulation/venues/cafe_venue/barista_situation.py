# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\cafe_venue\barista_situation.py
# Compiled at: 2015-06-16 19:17:47
# Size of source mod 2**32: 947 bytes
from sims4.tuning.instances import lock_instance_tunables
from situations.bouncer.bouncer_types import BouncerExclusivityCategory
from situations.complex.staff_member_situation import StaffMemberSituation
from situations.situation import Situation
from situations.situation_types import SituationCreationUIOption

class BaristaSituation(StaffMemberSituation):
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES


lock_instance_tunables(BaristaSituation, exclusivity=(BouncerExclusivityCategory.VENUE_EMPLOYEE),
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  duration=0,
  _implies_greeted_status=False)