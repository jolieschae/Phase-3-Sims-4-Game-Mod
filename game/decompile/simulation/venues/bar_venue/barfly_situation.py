# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\bar_venue\barfly_situation.py
# Compiled at: 2020-01-21 17:32:55
# Size of source mod 2**32: 2593 bytes
import random
from sims4.common import Pack, is_available_pack
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import OptionalTunable, TunableSimMinute, TunableEnumEntry
from situations.bouncer.bouncer_types import BouncerExclusivityCategory
from situations.situation import Situation
from situations.situation_complex import SituationState, SituationComplexCommon, TunableSituationJobAndRoleState, SituationStateData
from situations.situation_types import SituationCreationUIOption
import mtx

class _BarflySituationState(SituationState):
    pass


class BarflySituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'barfly_job_and_role':TunableSituationJobAndRoleState(description='\n            The job and role of the barfly.\n            '), 
     'starting_entitlement':OptionalTunable(description='\n            If enabled, this situation is locked by an entitlement. Otherwise,\n            this situation is available to all players.\n            ',
       tunable=TunableEnumEntry(description='\n                Pack required for this event to start.\n                ',
       tunable_type=Pack,
       default=(Pack.BASE_GAME)))}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classmethod
    def _states(cls):
        return (SituationStateData(1, _BarflySituationState),)

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.barfly_job_and_role.job, cls.barfly_job_and_role.role_state)]

    @classmethod
    def default_job(cls):
        pass

    @classmethod
    def situation_meets_starting_requirements(cls, **kwargs):
        if cls.starting_entitlement is None:
            return True
        return is_available_pack(cls.starting_entitlement)

    def start_situation(self):
        super().start_situation()
        self._change_state(_BarflySituationState())


lock_instance_tunables(BarflySituation, exclusivity=(BouncerExclusivityCategory.NORMAL),
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  _implies_greeted_status=False)