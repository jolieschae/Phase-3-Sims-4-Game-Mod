# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\club_invite_drama_node.py
# Compiled at: 2020-02-07 16:50:41
# Size of source mod 2**32: 7532 bytes
import random
from drama_scheduler.drama_node import BaseDramaNode, _DramaParticipant, CooldownOption, DramaNodeRunOutcome
from drama_scheduler.drama_node_types import DramaNodeType
from event_testing.results import TestResult
from gsi_handlers.drama_handlers import GSIRejectedDramaNodeScoringData
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import OptionalTunable, Tunable
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import classproperty
from ui.ui_dialog import UiDialogOkCancel
import services

class ClubInviteBaseDramaNode(BaseDramaNode):
    INSTANCE_TUNABLES = {'sender_sim_info':_DramaParticipant(description='\n            Specify who the sending Sim must be. This is the Sim that will "text"\n            the Drama Node owner.\n            ',
       excluded_options=('no_participant', ),
       tuning_group=GroupNames.PARTICIPANT), 
     'dialog':UiDialogOkCancel.TunableFactory(description='\n            The dialog that is displayed to the player Sim once this Drama Node\n            executes. Upon acceptance, the behavior specific to this Drama Node\n            executes.\n            ')}

    @classproperty
    def drama_node_type(cls):
        return DramaNodeType.CLUB

    def _setup(self, *args, gsi_data=None, **kwargs):
        result = (super()._setup)(args, gsi_data=gsi_data, **kwargs)
        if not result:
            return result
        club_service = services.get_club_service()
        if club_service is None:
            if gsi_data is not None:
                gsi_data.rejected_nodes.append(GSIRejectedDramaNodeScoringData(type(self), 'Club service is None.'))
            return False
        clubs = self._get_possible_clubs()
        if not clubs:
            if gsi_data is not None:
                gsi_data.rejected_nodes.append(GSIRejectedDramaNodeScoringData(type(self), 'No possible clubs found.'))
            return False
        club = random.choice(clubs)
        self._club_id = club.club_id
        return True

    def _get_possible_clubs(self):
        raise NotImplementedError

    def _test(self, resolver, skip_run_tests=False):
        if self._club_id is None:
            return TestResult(False, 'Cannot run because there is no chosen node.')
        elif self._sender_sim_info is None:
            return TestResult(False, 'Cannot run because there is no sender sim info.')
        else:
            club = skip_run_tests or services.get_club_service().get_club_by_id(self._club_id)
            if club is None:
                return TestResult(False, 'Cannot run because the club no longer exists.')
            result = self._test_club(club)
            return result or result
        return super()._test(resolver, skip_run_tests=skip_run_tests)

    def _test_club(self, club):
        raise NotImplementedError

    def _run(self):

        def on_response(dialog):
            if dialog.accepted:
                club = services.get_club_service().get_club_by_id(self._club_id)
                self._run_club_behavior(club)
            services.drama_scheduler_service().complete_node(self.uid)

        dialog = self.dialog((self._receiver_sim_info), target_sim_id=(self._sender_sim_info.id),
          resolver=(self._get_resolver()))
        club = services.get_club_service().get_club_by_id(self._club_id)
        dialog.show_dialog(on_response=on_response, additional_tokens=(club.name,))
        return DramaNodeRunOutcome.SUCCESS_NODE_INCOMPLETE

    def _run_club_behavior(self, club):
        raise NotImplementedError


class ClubInviteDramaNode(ClubInviteBaseDramaNode):

    def _get_possible_clubs(self):
        club_service = services.get_club_service()
        return tuple((club for club in club_service.get_clubs_for_sim_info(self._sender_sim_info) if self._test_club(club)))

    def _test_club(self, club):
        if self._sender_sim_info not in club.members:
            return TestResult(False, 'Cannot run because the sender Sim is no longer in the chosen Club.')
        else:
            return club.can_sim_info_join(self._receiver_sim_info) or TestResult(False, 'Cannot run because the receiver Sim can no longer join the chosen Club')
        return TestResult.TRUE

    def _run_club_behavior(self, club):
        if club.can_sim_info_join(self._receiver_sim_info):
            club.add_member(self._receiver_sim_info)


class ClubInviteRequestDramaNode(ClubInviteBaseDramaNode):
    INSTANCE_TUNABLES = {'invite_only': OptionalTunable(description='\n            If specified, then only Clubs of the appropriate invite exclusivity\n            type are valid for this Drama Node.\n            ',
                      tunable=Tunable(description='\n                If checked, only invite-only Clubs are valid. If unchecked, only\n                open membership Clubs are valid.\n                ',
                      tunable_type=bool,
                      default=True))}

    def _get_possible_clubs(self):
        club_service = services.get_club_service()
        return tuple((club for club in club_service.get_clubs_for_sim_info(self._receiver_sim_info) if self._test_club(club)))

    def _test_club(self, club):
        if self._receiver_sim_info is not club.leader:
            return TestResult(False, 'Cannot run because the receiver Sim is no longer the leader of the chosen Club')
        else:
            if not club.can_sim_info_join(self._sender_sim_info):
                return TestResult(False, 'Cannot run because the sender Sim can no longer join the chosen Club')
            if self.invite_only is not None and club.invite_only != self.invite_only:
                return TestResult(False, 'Cannot run because the chosen Club is not of the correct invite exclusivity type')
        return TestResult.TRUE

    def _run_club_behavior(self, club):
        if club.can_sim_info_join(self._sender_sim_info):
            club.add_member(self._sender_sim_info)