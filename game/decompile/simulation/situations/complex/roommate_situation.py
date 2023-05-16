# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\roommate_situation.py
# Compiled at: 2019-02-13 12:34:49
# Size of source mod 2**32: 2516 bytes
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import classproperty
from situations.bouncer.bouncer_types import BouncerExclusivityCategory
from situations.situation import Situation
from situations.situation_complex import SituationComplexCommon, TunableSituationJobAndRoleState, SituationStateData, SituationState
from situations.situation_types import SituationSerializationOption, SituationCreationUIOption

class _RoommateSituationState(SituationState):
    pass


class RoommateSituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'roommate_situation_job_and_role_state': TunableSituationJobAndRoleState(description='\n            The Situation Job and Role State for the Roommate Sim..\n            ',
                                                tuning_group=(GroupNames.ROLES))}
    REMOVE_INSTANCE_TUNABLES = ('recommended_job_object_notification', 'recommended_job_object_text',
                                'targeted_situation', '_resident_job', '_relationship_between_job_members') + Situation.SITUATION_SCORING_REMOVE_INSTANCE_TUNABLES + Situation.SITUATION_START_FROM_UI_REMOVE_INSTANCE_TUNABLES
    DOES_NOT_CARE_MAX_SCORE = -1

    @classproperty
    def situation_serialization_option(cls):
        return SituationSerializationOption.DONT

    @classmethod
    def _states(cls):
        return (SituationStateData(1, _RoommateSituationState),)

    @classmethod
    def default_job(cls):
        return cls.roommate_situation_job_and_role_state.job

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.roommate_situation_job_and_role_state.job, cls.roommate_situation_job_and_role_state.role_state)]

    def start_situation(self):
        super().start_situation()
        self._change_state(_RoommateSituationState())


lock_instance_tunables(RoommateSituation, exclusivity=(BouncerExclusivityCategory.ROOMMATE),
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  duration=0,
  force_invite_only=True,
  _implies_greeted_status=True)