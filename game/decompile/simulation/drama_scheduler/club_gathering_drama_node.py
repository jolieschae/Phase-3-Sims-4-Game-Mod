# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\club_gathering_drama_node.py
# Compiled at: 2020-02-07 16:50:40
# Size of source mod 2**32: 4129 bytes
import random
from clubs.club_tuning import ClubTunables
from drama_scheduler.drama_node import BaseDramaNode, CooldownOption, DramaNodeRunOutcome
from drama_scheduler.drama_node_types import DramaNodeType
from event_testing.results import TestResult
from gsi_handlers.drama_handlers import GSIRejectedDramaNodeScoringData
from sims4.tuning.instances import lock_instance_tunables
from sims4.utils import classproperty
import services

class ClubGatheringDramaNode(BaseDramaNode):

    @classproperty
    def drama_node_type(cls):
        return DramaNodeType.CLUB

    def _run(self):
        club_service = services.get_club_service()
        if club_service is None:
            return DramaNodeRunOutcome.FAILURE
        club = club_service.get_club_by_id(self._club_id)
        club.show_club_gathering_dialog((self._receiver_sim_info), flavor_text=(ClubTunables.CLUB_GATHERING_DIALOG_TEXT_DRAMA_NODE),
          sender_sim_info=(self._sender_sim_info))
        return DramaNodeRunOutcome.SUCCESS_NODE_COMPLETE

    def _test(self, resolver, skip_run_tests=False):
        if self._club_id is None:
            return TestResult(False, 'Cannot run because there is no chosen node.')
        else:
            if self._sender_sim_info is None:
                return TestResult(False, 'Cannot run because there is no sender sim info.')
            if not skip_run_tests:
                club_service = services.get_club_service()
                if club_service is None:
                    return TestResult(False, 'Club Service is None')
                club = club_service.get_club_by_id(self._club_id)
                if club is None:
                    return TestResult(False, 'Cannot run because the club no longer exists.')
                if club in club_service.clubs_to_gatherings_map:
                    return TestResult(False, 'Cannot run because the Club is already gathering')
                if self._sender_sim_info not in club.members:
                    return TestResult(False, 'Cannot run because the sender sim info is no longer in the chosen club.')
                if self._receiver_sim_info not in club.members:
                    return TestResult(False, 'Cannot run because the receiver sim info is no longer in the chosen club.')
        return super()._test(resolver, skip_run_tests=skip_run_tests)

    def _setup(self, *args, gsi_data=None, **kwargs):
        result = (super()._setup)(args, gsi_data=gsi_data, **kwargs)
        if not result:
            return result
        club_service = services.get_club_service()
        if club_service is None:
            if gsi_data is not None:
                gsi_data.rejected_nodes.append(GSIRejectedDramaNodeScoringData(type(self), 'Club service is None.'))
            return False
        available_clubs = {club for club in club_service.get_clubs_for_sim_info(self._receiver_sim_info)}
        available_clubs &= {club for club in club_service.get_clubs_for_sim_info(self._sender_sim_info)}
        if not available_clubs:
            if gsi_data is not None:
                gsi_data.rejected_nodes.append(GSIRejectedDramaNodeScoringData(type(self), 'No available clubs.'))
            return False
        chosen_club = random.choice(tuple(available_clubs))
        self._club_id = chosen_club.club_id
        return True