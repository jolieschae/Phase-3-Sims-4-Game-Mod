# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\graduation_venue_event_drama_node.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 7153 bytes
import services, sims4
from drama_scheduler.drama_enums import DramaNodeUiDisplayType, DramaNodeRunOutcome
from event_testing.resolver import GlobalResolver
from event_testing.test_events import TestEvent
from random import randint
from sims4.tuning.tunable import TunableInterval, TunableReference, TunableEnumEntry, TunableSet
from venues.venue_event_drama_node import VenueEventDramaNode
logger = sims4.log.Logger('HighSchoolGraduation', default_owner='rfleig')
GRADUATION_GROUP = 'Graduation'

class GraduationVenueEventDramaNode(VenueEventDramaNode):
    INSTANCE_TUNABLES = {'range_of_graduating_sims_allowed':TunableInterval(description='\n            The minimum and maximum amount of Sims allowed to attend a graduation event.\n            ',
       tunable_type=int,
       minimum=1,
       default_lower=1,
       maximum=20,
       default_upper=5,
       tuning_group=GRADUATION_GROUP), 
     'graduating_npc_sim_filter':TunableReference(description='\n            Sim Filter used to identify Sims that are ready to be aged up for graduation.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SIM_FILTER),
       tuning_group=GRADUATION_GROUP), 
     'update_on_calendar_events':TunableSet(description='\n            When any of these events fire the calendar entry will be re-evaluated \n            and either removed if necessary or added/update otherwise.\n            ',
       tunable=TunableEnumEntry(tunable_type=TestEvent,
       default=(TestEvent.Invalid)))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        services.get_event_manager().register(self, self.update_on_calendar_events)

    def _setup(self, *args, zone_id=None, gsi_data=None, **kwargs):
        result = (super()._setup)(args, zone_id=zone_id, gsi_data=gsi_data, **kwargs)
        graduation_service = services.get_graduation_service()
        graduation_service.move_waiting_graduates_to_current()
        return result

    def _on_venue_event_complete(self, _):
        graduation_service = services.get_graduation_service()
        graduation_service.clear_current_graduates()
        super()._on_venue_event_complete(_)

    def cleanup(self, from_service_stop=False):
        super().cleanup(from_service_stop=from_service_stop)
        services.get_event_manager().unregister(self, self.update_on_calendar_events)

    def handle_event(self, sim_info, event, resolver):
        if self.ui_display_type == DramaNodeUiDisplayType.NO_UI:
            return
            graduating_sims = services.get_graduation_service().current_graduating_sims()
            if sim_info.is_selectable or sim_info in graduating_sims:
                calendar_service = services.calendar_service()
                on_calendar = calendar_service.is_on_calendar(self.uid)
                global_resolver = GlobalResolver()
                if self.visibility_tests.run_tests(global_resolver):
                    if on_calendar:
                        calendar_service.update_on_calendar(self)
                    else:
                        calendar_service.mark_on_calendar(self)
        elif on_calendar:
            calendar_service.remove_on_calendar(self.uid)

    def _run_venue_behavior(self):
        self._setup_graduation()
        return super()._run_venue_behavior()

    def _resume_venue_behavior(self):
        self._setup_graduation()
        return super()._resume_venue_behavior()

    def _setup_graduation(self):
        graduation_service = services.get_graduation_service()
        if graduation_service is None:
            return
        graduating_sim_count = graduation_service.graduating_sim_count()
        if graduating_sim_count < self.range_of_graduating_sims_allowed.lower_bound:
            total_sim_count = randint(self.range_of_graduating_sims_allowed.lower_bound, self.range_of_graduating_sims_allowed.upper_bound)
            self.graduate_sims(total_sim_count - graduating_sim_count)
        if not graduation_service.has_current_valedictorian():
            graduation_service.choose_random_valedictorian()

    def graduate_sims(self, num_to_grad):
        results = services.sim_filter_service().submit_matching_filter(number_of_sims_to_find=num_to_grad, sim_filter=(self.graduating_npc_sim_filter),
          allow_yielding=False,
          allow_instanced_sims=True,
          gsi_source_fn=(lambda: 'Teens For Graduation: {}'.format(num_to_grad)))
        if not results:
            return
        for result in results:
            sim_info = result.sim_info
            sim_info.advance_age()

    def get_calendar_sims(self):
        graduation_service = services.get_graduation_service()
        graduating_sims = graduation_service.current_graduating_sims()
        return graduating_sims