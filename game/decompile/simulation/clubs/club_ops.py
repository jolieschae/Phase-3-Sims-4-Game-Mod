# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\clubs\club_ops.py
# Compiled at: 2015-10-21 18:30:07
# Size of source mod 2**32: 1503 bytes
from clubs.club_enums import ClubGatheringVibe
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import TunableEnumEntry
import services

class SetClubGatheringVibe(BaseLootOperation):
    FACTORY_TUNABLES = {'vibe': TunableEnumEntry(description='\n            The vibe to set the gathering to.\n            ',
               tunable_type=ClubGatheringVibe,
               default=(ClubGatheringVibe.NO_VIBE))}

    def __init__(self, vibe, **kwargs):
        (super().__init__)(**kwargs)
        self._vibe = vibe

    def _apply_to_subject_and_target(self, subject, target, resolver):
        club_service = services.get_club_service()
        if club_service is None:
            return
        subject_sim = subject.get_sim_instance()
        if subject_sim is None:
            return
        gathering = club_service.sims_to_gatherings_map.get(subject_sim)
        if gathering is None:
            return
        gathering.set_club_vibe(self._vibe)