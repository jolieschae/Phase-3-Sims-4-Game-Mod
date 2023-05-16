# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\career_event.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 24604 bytes
from protocolbuffers import SimObjectAttributes_pb2
from careers.career_event_zone_director import CareerEventZoneDirector
from careers.career_event_zone_requirement import RequiredCareerEventZoneTunableVariant
from event_testing.resolver import SingleSimResolver
from event_testing.tests import TunableTestSet
from interactions.utils.loot import LootActions
from sims4.localization import TunableLocalizedStringFactory, LocalizationHelperTuning
from sims4.protocol_buffer_utils import has_field
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, OptionalTunable, TunableReference, TunableTuple, TunableRange, TunableList
from tunable_multiplier import TunableMultiplier
from tunable_time import TunableTimeSpan
from ui.ui_dialog_notification import TunableUiDialogNotificationSnippet
from venues.venue_service import ZoneDirectorRequestType
from venues.weekly_schedule_zone_director import WeeklyScheduleZoneDirector
import enum, services, sims4
logger = sims4.log.Logger('Careers', default_owner='tingyul')

class MedalPayout(TunableTuple):

    def __init__(self, *args, **kwargs):
        (super().__init__)(work_performance=TunableMultiplier.TunableFactory(description='\n                Multiplier on the base full day work performance (tunable at\n                CareerLevel -> Performance Metrics -> Base Performance).\n                '), 
         money=TunableMultiplier.TunableFactory(description='\n                Multiplier on full day pay, determined by hourly wage (tunable\n                at Career Level -> Simoleons Per Hour), multiplied by work day\n                length (tunable at Career Level -> Work Scheduler), modified by\n                any additional multipliers (e.g. tuning on Career Level ->\n                Simolean Trait Bonus, Career Track -> Overmax, etc.).\n                '), 
         text=TunableLocalizedStringFactory(description='\n                Text shown at end of event notification/dialog if the Sim\n                finishes at this medal.\n                \n                0 param - Sim in the career\n                '), 
         additional_loots=TunableList(description='\n                Any additional loot needed on this medal payout. Currently, this\n                is used to award additional drama nodes/dialogs on this level.\n                ',
  tunable=LootActions.TunableReference(description='\n                    The loot action applied.\n                    ',
  pack_safe=True)), **kwargs)


class CareerEventState(enum.Int, export=False):
    CREATED = 0
    REQUESTED = 1
    RUNNING = 2
    STOPPED = 3


class CareerEvent(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.CAREER_EVENT)):
    INSTANCE_TUNABLES = {'required_zone':RequiredCareerEventZoneTunableVariant(description='\n            The required zone for this career event (e.g. the hospital lot for\n            a doctor career event). The Sim involved in this event will\n            automatically travel to this zone at the beginning of the work\n            shift. The Sim will in general be prohibited from leaving this zone\n            without work -- the lone exception is the Sim is allowed to travel\n            for a career sub-event (e.g. a detective Sim running a career event\n            requiring the police station lot is allowed to initiate the sub-\n            event of investigating the crime scene at a commercial lot).\n            '), 
     'zone_director':OptionalTunable(description='\n            An optional zone director to apply to the zone the career event\n            takes place.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ZONE_DIRECTOR)),
       pack_safe=True,
       class_restrictions=(
      CareerEventZoneDirector, WeeklyScheduleZoneDirector))), 
     'scorable_situation':OptionalTunable(description='\n            A situation which the player must complete. Work performance for\n            the Sim will depend on how much the Sim accomplishes. This should\n            be enabled for main events and disabled for sub events. Example:\n            \n            Detective Career. The career event that starts at the beginning of\n            the work shift, going to the police station, will have a scorable\n            situation. The sub event to go to the crime scene will not, as the\n            career event will not be scored against it.\n            ',
       tunable=TunableTuple(situation=TunableReference(description='\n                    Situation which the Sim in the career event will be scored by.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION)),
       allow_none=True,
       class_restrictions=('CareerEventSituation', )),
       medal_payout_tin=MedalPayout(description='\n                    Work performance and money payout if scorable situation\n                    ends with a tin medal.\n                    '),
       medal_payout_bronze=MedalPayout(description='\n                    Work performance and money payout if scorable situation\n                    ends with a bronze medal.\n                    '),
       medal_payout_silver=MedalPayout(description='\n                    Work performance and money payout if scorable situation\n                    ends with a silver medal.\n                    '),
       medal_payout_gold=MedalPayout(description='\n                    Work performance and money payout if scorable situation\n                    ends with a gold medal.\n                    '),
       no_situation_payout=OptionalTunable(description='\n                    Work performance and money payout if scorable situation\n                    is not tuned.\n                    ',
       tunable=(MedalPayout()))),
       enabled_by_default=True,
       disabled_value=None,
       disabled_name='sub_event',
       enabled_name='main_event'), 
     'tests':TunableTestSet(description='\n            Tests for if this career event is available to the Sim\n            ParticipantType.Actor.\n            '), 
     'loot_on_request':LootActions.TunableReference(description='\n            Loot applied when the career event is requested to start. Happens\n            before traveling.\n            \n            Example 1: A detective is at home and goes to work. This loot\n            applies while the detective is still on the home lot, right before\n            the travel to the police station happens.\n            \n            Example 2: A detective at the police station travels to a crime\n            scene. This loot for the crime scene sub event applies while the\n            detective is still at the police station, right before the travel.\n            ',
       allow_none=True), 
     'loot_on_start':LootActions.TunableReference(description='\n            Loot applied when the career event starts. Happens after travel.\n            \n            Example 1: A detective is at home and goes to work. This loot \n            applies at the police station, right after traveling.\n            \n            Example 2: A detective at the police station travels to a crime\n            scene. This loot for the crime scene sub event applies at the\n            crime scene lot, right after traveling.\n            ',
       allow_none=True), 
     'loots_on_end':TunableList(description='\n            Loots applied when the career event ends.\n            ',
       tunable=LootActions.TunableReference(description='\n                A loot applied when the career event ends.\n                ',
       allow_none=True,
       pack_safe=True)), 
     'loots_on_cleanup':TunableList(description='\n            Loots that are applied after the career event has been completely shut down. Not the same as loot on end\n            which is processed while shutting down. Loot on cleanup will happen after the loot on end.\n            ',
       tunable=LootActions.TunableReference(description='\n                A loot applied on cleanup of the career event.\n                ')), 
     'cooldown':TunableRange(description='\n            How many work days before this career event will be offered again.\n            ',
       tunable_type=int,
       minimum=0,
       default=0), 
     'subvenue':OptionalTunable(description='\n            If enabled, the zones venue will be changed to the specified subvenue\n            at the start of the event, and returned to the primary venue at the\n            end of the event.  Returning to the primary venue at the end of the event\n            will occur immediately if the zone is not currently the active zone,\n            otherwise it will will be delayed by the specified time in order\n            to give the player time to leave the lot prior to being hit by the\n            venue change loadscreen.\n            ',
       tunable=TunableTuple(venue=TunableReference(description='\n                    The subvenue to change to.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.VENUE))),
       delay=TunableTimeSpan(description='\n                    How long to delay the restoration to the default venue type as\n                    long as the zone remains active.\n                    ',
       default_hours=1))), 
     'end_of_day_reports':OptionalTunable(description='\n            This is the end of shift performance report for an active career. This will be built\n            using a string from each of the Sims that happens to be in the same active career event\n            that are ending their shift at the same time. A header will be displayed along with a \n            bulleted list of the performance of each Sim.\n            ',
       tunable=TunableTuple(description='\n                The data used to form the end of career event performance string. This will show for\n                all sims in an active career event that matches this career event and ending at the\n                same time.\n                ',
       notification=TunableUiDialogNotificationSnippet(description='\n                    The tuning for the actual notification that shows up.\n    \n                    In order to get the string that is built for the performances you need to use\n                    token 0. {0.String} will get you the string with the header and the bulleted\n                    list together.\n                    '),
       leave_early_notification=OptionalTunable(description='\n                    Optional alternate version of the notification\n                    for when the sim leaves early.\n                    ',
       tunable=TunableUiDialogNotificationSnippet(description='\n                        The tuning for the notification that shows up when a sim leaves early.\n    \n                        Uses a single sim resolver, with the sim leaving early as the sim, so if no tokens are \n                        specified the first token is the sim. Also has the string that contains the performance \n                        bullet points as am additional token, e.g. The performance bullet points and header, \n                        (should you choose to include them) will be {1.String}.\n                        ')),
       header_string=OptionalTunable(description='\n                    When enabled a header string will appear above the performance strings. This is\n                    not the same as the Title of the Notification which appears at the top of the \n                    notification that appears.\n                    ',
       tunable=TunableLocalizedStringFactory(description="\n                        The string to act as the header to the performance string. This won't change at\n                        all based on the Sim, it will just be a summary for what the report means.\n                        ")),
       performance_strings=TunableList(description='\n                    A List of tests and localized strings. The string associated with the first test\n                    that passes for the Sim in the career event will be added to the end of day\n                    reports to show the result of that Sim.\n    \n                    Token 0 is the Sim whose performance you are reporting.\n                    ',
       tunable=TunableTuple(description='\n                        A pair of tests and a localized string. If the tests pass then the localized\n                        string will be added to the performance string.\n                        ',
       tests=TunableTestSet(description='\n                            These tests must pass for the asscoiated string to be shown. The tests run\n                            with Actor as the Sim who is currently in the career event being tested.    \n                            '),
       individual_string=TunableLocalizedStringFactory(description="\n                            The performance string for the Sim for today's shift in an active career.\n                            ")))))}

    def __init__(self, career):
        self._career = career
        self._required_zone_id = None
        self._event_situation_id = 0
        self._state = CareerEventState.CREATED
        self.end_of_day_results_reported = False

    @property
    def sim_info(self):
        return self._career.sim_info

    @property
    def career(self):
        return self._career

    def on_career_event_requested(self):
        self._advance_state(CareerEventState.REQUESTED)
        self._required_zone_id = self.required_zone.get_required_zone_id(self.sim_info)
        if self.subvenue:
            services.get_career_service().start_career_event_subvenue(self, self._required_zone_id, self.subvenue.venue)
        if self.loot_on_request is not None:
            resolver = SingleSimResolver(self._career.sim_info)
            self.loot_on_request.apply_to_resolver(resolver)

    def on_career_event_start(self):
        self._advance_state(CareerEventState.RUNNING)
        if self.loot_on_start is not None:
            resolver = SingleSimResolver(self._career.sim_info)
            self.loot_on_start.apply_to_resolver(resolver)

    def on_career_event_stop(self):
        if self._state == CareerEventState.STOPPED:
            logger.error('Attempting to call on_career_event_stop on {} for a second time. This should not happen.Please look into what is having on_career_event_stop called for a second time on the event.', self)
            return
        else:
            if self.subvenue:
                services.get_career_service().stop_career_event_subvenue(self, self._required_zone_id, self.subvenue.delay)
            else:
                self._advance_state(CareerEventState.STOPPED)
                resolver = SingleSimResolver(self._career.sim_info)
                for loot in self.loots_on_end:
                    if loot is not None:
                        loot.apply_to_resolver(resolver)

                venue_service = services.venue_service()
                curr_zone_director = venue_service.get_zone_director()
                return curr_zone_director and self.zone_director or None
            if self.zone_director.guid64 != curr_zone_director.guid64:
                return
            curr_zone_director.on_career_event_stop(self)
            if curr_zone_director.has_career_events():
                return self.loots_on_cleanup
            return self._career.is_multi_sim_active or self.loots_on_cleanup
        if type(curr_zone_director) is venue_service.active_venue.zone_director:
            return self.loots_on_cleanup
        new_zone_director = venue_service.active_venue.zone_director()
        venue_service.change_zone_director(new_zone_director, True)
        return self.loots_on_cleanup

    def request_zone_director(self):
        if self.zone_director is not None:
            zone_director = self.zone_director(career_event=self)
            venue_service = services.venue_service()
            prior_zone_director = venue_service.get_zone_director()
            if prior_zone_director is not None:
                if self.career.is_multi_sim_active:
                    if prior_zone_director.guid64 == zone_director.guid64:
                        prior_zone_director.add_career_event(self)
                        return
                venue_service.change_zone_director(zone_director, True)
                return
            if self.career.is_multi_sim_active:
                requested_zone_director = venue_service.get_requested_zone_director(zone_director)
                if requested_zone_director:
                    requested_zone_director.add_career_event(self)
                    return
            preserve_state = self._state >= CareerEventState.RUNNING
            venue_service.request_zone_director(zone_director, (ZoneDirectorRequestType.CAREER_EVENT),
              preserve_state=preserve_state)

    def get_event_situation_id(self):
        return self._event_situation_id

    def set_event_situation_id(self, event_situation_id):
        self._event_situation_id = event_situation_id

    def get_required_zone_id(self):
        return self._required_zone_id

    def _advance_state(self, state):
        logger.assert_log(state > self._state, 'Going backwards when trying to advance state. Old: {}, New: {}', self._state, state)
        self._state = state

    def start_from_zone_spin_up(self):
        if self._state == CareerEventState.REQUESTED:
            self.on_career_event_start()

    def get_career_event_data_proto(self):
        proto = SimObjectAttributes_pb2.CareerEventData()
        proto.career_event_id = self.guid64
        proto.event_situation_id = self._event_situation_id
        if self._required_zone_id is not None:
            proto.required_zone_id = self._required_zone_id
        proto.state = self._state
        return proto

    def load_from_career_event_data_proto(self, proto):
        self._event_situation_id = proto.event_situation_id
        if has_field(proto, 'required_zone_id'):
            self._required_zone_id = proto.required_zone_id
        self._state = CareerEventState(proto.state)

    def get_end_of_day_result_string_for_active_career(self, sim_info):
        resolver = SingleSimResolver(sim_info)
        for entry in self.end_of_day_reports.performance_strings:
            if entry.tests.run_tests(resolver):
                return entry.individual_string

    def build_end_of_day_notification(self, sim_info, performance_strings, left_early):
        header_string = self.end_of_day_reports.header_string(sim_info) if self.end_of_day_reports.header_string is not None else None
        bulleted_list = (LocalizationHelperTuning.get_bulleted_list)(header_string, *performance_strings)
        if left_early and self.end_of_day_reports.leave_early_notification is not None:
            notification = self.end_of_day_reports.leave_early_notification(sim_info, resolver=(SingleSimResolver(sim_info)))
        else:
            notification = self.end_of_day_reports.notification(sim_info)
        notification.show_dialog(additional_tokens=(bulleted_list,))