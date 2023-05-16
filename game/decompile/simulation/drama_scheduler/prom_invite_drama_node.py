# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\prom_invite_drama_node.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 15885 bytes
import services, sims4
from date_and_time import TimeSpan, create_time_span
from drama_scheduler.drama_enums import SenderSimInfoType, DramaNodeUiDisplayType
from drama_scheduler.npc_invite_situation_drama_node import NPCInviteSituationDramaNode
from event_testing.test_events import TestEvent
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableTuple, TunableReference, TunableRange
from sims4.tuning.tunable_base import GroupNames
from situations.bouncer.bouncer_types import RequestSpawningOption, BouncerRequestPriority
from situations.situation_guest_list import SituationGuestInfo, SituationGuestList
from ui.ui_dialog_picker import SimPickerRow
logger = sims4.log.Logger('PromInviteDramaNode', default_owner='skorman')

class PromInviteDramaNode(NPCInviteSituationDramaNode):
    INSTANCE_TUNABLES = {'teen_attendee_job':TunableReference(description='\n            Job for prom attendees. This is used for all sims that were at the \n            pre-prom party, as well as anyone with prom invite relbits.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION_JOB),
       tuning_group=GroupNames.PARTICIPANT), 
     'award_presenter':TunableTuple(description='\n            Award presenter for the prom situation. \n            ',
       sim_filter=TunableReference(description='\n                The sim filter used to find the award presenter.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER))),
       job=TunableReference(description='\n                The situation job for the award presenter.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB))),
       tuning_group=GroupNames.PARTICIPANT), 
     'prom_chaperones':TunableTuple(description='\n            Chaperones for the prom situation.\n            ',
       sim_filter=TunableReference(description='\n                The sim filter used to find the prom chaperones.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER))),
       number_to_find=TunableRange(description='\n                The number of chaperones to find.\n                ',
       tunable_type=int,
       default=1,
       minimum=0),
       job=TunableReference(description='\n                The situation job for the prom chaperone.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB))),
       tuning_group=GroupNames.PARTICIPANT)}
    REMOVE_INSTANCE_TUNABLES = ('receiver_sim', 'sender_sim_info', 'picked_sim_info',
                                '_NPC_hosted_situation_player_job')
    UPDATE_ON_CALENDAR_EVENTS = (
     TestEvent.HouseholdChanged, TestEvent.AgeDurationUpdated)

    def _add_adults_to_guest_list(self, guest_list):
        prom_service = services.get_prom_service()
        if prom_service is None:
            return
        blacklist_sim_ids = {sim_info.sim_id for sim_info in services.active_household()}
        award_presenter = services.sim_filter_service().submit_matching_filter(sim_filter=(self.award_presenter.sim_filter), callback=None,
          allow_yielding=False,
          blacklist_sim_ids=blacklist_sim_ids,
          gsi_source_fn=(self.get_sim_filter_gsi_name),
          allow_instanced_sims=True)
        if not award_presenter:
            logger.error('{} failed to setup guestlist for prom situation. No award presenter found.', self)
        award_presenter_id = award_presenter[0].sim_info.sim_id
        guest_list.add_guest_info(SituationGuestInfo(award_presenter_id, (self.award_presenter.job),
          (RequestSpawningOption.DONT_CARE),
          (BouncerRequestPriority.EVENT_VIP),
          expectation_preference=True))
        blacklist_sim_ids.add(award_presenter_id)
        results = services.sim_filter_service().submit_matching_filter(sim_filter=(self.prom_chaperones.sim_filter), number_of_sims_to_find=(self.prom_chaperones.number_to_find),
          callback=None,
          blacklist_sim_ids=blacklist_sim_ids,
          allow_yielding=False,
          gsi_source_fn=(self.get_sim_filter_gsi_name))
        for result in results:
            guest_id = result.sim_info.sim_id
            guest_list.add_guest_info(SituationGuestInfo(guest_id, (self.prom_chaperones.job),
              (RequestSpawningOption.DONT_CARE),
              (BouncerRequestPriority.EVENT_VIP),
              expectation_preference=True))

        return guest_list

    def _get_situation_guest_list(self, additional_sims_to_bring=()):
        prom_service = services.get_prom_service()
        if prom_service is None:
            return
        guest_list = SituationGuestList()
        if additional_sims_to_bring:
            additional_sims_job = self._chosen_dialog_data.dialog.bring_other_sims.situation_job
            for sim_info in additional_sims_to_bring:
                guest_list.add_guest_info(SituationGuestInfo((sim_info.id), additional_sims_job,
                  (RequestSpawningOption.DONT_CARE),
                  (BouncerRequestPriority.EVENT_VIP),
                  expectation_preference=True))

        sim_info_manager = services.sim_info_manager()
        additional_teen_attendees = prom_service.get_prom_teen_attendee_ids() - prom_service.get_prom_pact_sim_ids()
        invited_sims = tuple(guest_list.invited_sim_infos_gen())
        for sim_id in additional_teen_attendees:
            sim_info = sim_info_manager.get(sim_id)
            if not sim_info in invited_sims:
                if not sim_info.is_teen:
                    continue
                guest_list.add_guest_info(SituationGuestInfo(sim_id, (self.teen_attendee_job),
                  (RequestSpawningOption.DONT_CARE),
                  (BouncerRequestPriority.EVENT_AUTO_FILL),
                  expectation_preference=True))

        guest_list = self._add_adults_to_guest_list(guest_list)
        return guest_list

    def get_calendar_end_time(self):
        return self._selected_time + create_time_span(minutes=(self._situation_to_run.duration))

    @property
    def is_calendar_deletable(self):
        return False

    def handle_event(self, sim_info, event, resolver):
        active_household = services.active_household()
        if not active_household is None:
            if sim_info not in active_household or event not in self.UPDATE_ON_CALENDAR_EVENTS:
                return
            calendar_service = services.calendar_service()
            on_calendar = calendar_service.is_on_calendar(self.uid)
            if on_calendar:
                if self.get_calendar_sims():
                    calendar_service.update_on_calendar(self)
                else:
                    calendar_service.remove_on_calendar(self.uid)
        elif self.get_calendar_sims():
            calendar_service.mark_on_calendar(self)

    def schedule(self, resolver, specific_time=None, time_modifier=TimeSpan.ZERO, **setup_kwargs):
        success = (super().schedule)(resolver, specific_time, time_modifier, **setup_kwargs)
        if success:
            if self.ui_display_type != DramaNodeUiDisplayType.NO_UI:
                if self.get_calendar_sims():
                    services.calendar_service().mark_on_calendar(self)
        services.get_event_manager().register(self, self.UPDATE_ON_CALENDAR_EVENTS)
        return success

    def load(self, drama_node_proto, schedule_alarm=True):
        success = super().load(drama_node_proto, schedule_alarm)
        if success:
            if self.ui_display_type != DramaNodeUiDisplayType.NO_UI:
                if self.get_calendar_sims():
                    services.calendar_service().mark_on_calendar(self)
        services.get_event_manager().register(self, self.UPDATE_ON_CALENDAR_EVENTS)
        return success

    def get_calendar_sims(self):
        sims = set()
        if self._selected_time is None:
            return sims
        current_time = services.time_service().sim_now
        active_household = services.active_household()
        for sim_info in active_household:
            if sim_info.is_teen:
                if not sim_info.auto_aging_enabled or sim_info.days_until_ready_to_age() >= self.day - current_time.day():
                    sims.add(sim_info)

        return sims

    def cleanup(self, from_service_stop=False):
        services.get_event_manager().unregister(self, self.UPDATE_ON_CALENDAR_EVENTS)
        super().cleanup(from_service_stop=from_service_stop)
        prom_service = services.get_prom_service()
        if prom_service is None:
            return
        if not prom_service.cleanup_scheduled:
            if not services.current_zone().is_zone_shutting_down:
                prom_service.cleanup_prom()
                prom_service.handle_time_for_prom()

    def _create_situation(self, additional_sims_to_bring=()):
        prom_service = services.get_prom_service()
        if prom_service is None:
            return
        super()._create_situation(additional_sims_to_bring=additional_sims_to_bring)
        prom_service.on_prom_situation_created(self._situation_to_run, self._get_zone_id())

    def _populate_bring_sims_picker(self, picker_dialog):
        sim_infos = self._get_sim_infos_for_travel_picker()
        for sim_info in sim_infos:
            picker_dialog.add_row(SimPickerRow((sim_info.sim_id), tag=sim_info, select_default=True))


lock_instance_tunables(PromInviteDramaNode, _require_predefined_guest_list=False,
  _NPC_hosted_situation_use_player_sim_as_filter_requester=False,
  is_simless=True,
  _NPC_host_job=None,
  override_picked_sim_info_resolver=False,
  sender_sim_info_type=(SenderSimInfoType.UNINSTANCED_ONLY),
  spawn_sims_during_zone_spin_up=True)

class PrePromInviteDramaNode(NPCInviteSituationDramaNode):
    INSTANCE_TUNABLES = {'additional_party_goers': TunableTuple(description='\n            Additional party goers for the pre-prom situation. \n            ',
                                 sim_filter=TunableReference(description='\n                The sim filter used to find the additional party goers. These \n                will be requested by the drama node sender.\n                ',
                                 manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER))),
                                 number_to_find=TunableRange(description='\n                The number of additional party goers to find.\n                ',
                                 tunable_type=int,
                                 default=0,
                                 minimum=0),
                                 job=TunableReference(description='\n                The situation job for the additional party goers. \n                ',
                                 manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB))),
                                 tuning_group=(GroupNames.PARTICIPANT))}

    def _get_situation_guest_list(self, additional_sims_to_bring=()):
        guest_list = super()._get_situation_guest_list(additional_sims_to_bring=additional_sims_to_bring)
        if guest_list is None:
            return
        prom_service = services.get_prom_service()
        if prom_service is None:
            return
        blacklist = set(guest_list.guest_info_gen()) | prom_service.get_prom_pact_sim_ids()
        results = services.sim_filter_service().submit_matching_filter(sim_filter=(self.additional_party_goers.sim_filter), number_of_sims_to_find=(self.additional_party_goers.number_to_find),
          callback=None,
          requesting_sim_info=(self._sender_sim_info),
          blacklist_sim_ids=blacklist,
          allow_yielding=False,
          gsi_source_fn=(self.get_sim_filter_gsi_name))
        for result in results:
            guest_id = result.sim_info.sim_id
            guest_list.add_guest_info(SituationGuestInfo(guest_id, (self.additional_party_goers.job),
              (RequestSpawningOption.DONT_CARE),
              (BouncerRequestPriority.EVENT_AUTO_FILL),
              expectation_preference=True))
            prom_service.add_prom_teen_attendee_ids({guest_id})

        return guest_list