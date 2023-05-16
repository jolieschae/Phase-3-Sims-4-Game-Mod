# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\venue_event_drama_node.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 26828 bytes
from date_and_time import create_time_span, TimeSpan
from distributor.shared_messages import build_icon_info_msg, IconInfoData
from drama_scheduler.drama_node import BaseDramaNode, DramaNodeUiDisplayType, TimeSelectionOption, DramaNodeRunOutcome
from drama_scheduler.drama_node_types import DramaNodeType
from event_testing.resolver import GlobalResolver
from event_testing.results import TestResult
from event_testing.tests import TunableGlobalTestSet
from gsi_handlers.drama_handlers import GSIRejectedDramaNodeScoringData
from interactions.utils.display_mixin import get_display_mixin
from objects import ALL_HIDDEN_REASONS_EXCEPT_UNINITIALIZED
from organizations.organization_ops import OrgEventInfo
from server.pick_info import PickInfo, PickType
from sims4.localization import TunableLocalizedString
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableSimMinute, OptionalTunable, TunableReference, TunableList, TunablePackSafeReference, TunableTuple, Tunable
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import classproperty, flexmethod
from tunable_utils.tunable_white_black_list import TunableWhiteBlackList
from tunable_time import TunableTimeSpan
from ui.ui_dialog_notification import UiDialogNotification
from venues.venue_service import VenueService
import alarms, build_buy, elements, interactions, services, sims4.log
logger = sims4.log.Logger('DramaNode', default_owner='jjacobson')
ZONE_ID_TOKEN = 'zone_id'
SHOWN_NOTIFICATION_TOKEN = 'shown_notification'
DURATION_TOKEN = 'duration'
VenueEventDramaNodeDisplayMixin = get_display_mixin(has_icon=True, has_description=True)

class VenueEventDramaNode(VenueEventDramaNodeDisplayMixin, BaseDramaNode):
    GO_TO_VENUE_ZONE_INTERACTION = TunablePackSafeReference(description='\n        Reference to the interaction used to travel the Sims to the zone of the venue.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)))
    INSTANCE_TUNABLES = {'duration':TunableSimMinute(description='\n            The duration that this drama node will run for.\n            ',
       minimum=1,
       default=1), 
     'zone_director':OptionalTunable(description='\n            If enabled then this drama node will override the zone director\n            of the lot.\n            ',
       tunable=TunableReference(description='\n                The zone director that we will override onto the lot.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.ZONE_DIRECTOR)))), 
     'notification':OptionalTunable(description='\n            If enabled then we will display a notification when this venue\n            event occurs.\n            ',
       tunable=UiDialogNotification.TunableFactory()), 
     'away_notification':OptionalTunable(description='\n            If enabled then we will display a notification when this venue\n            event occurs if player is not on the lot.\n            Additional Tokens:\n            Zone Name\n            Venue Name\n            ',
       tunable=UiDialogNotification.TunableFactory()), 
     'ending_notification':OptionalTunable(description='\n            If enabled then we will display a notification when this venue\n            event ends if the player is on the current lot that the event is\n            taking place on.\n            ',
       tunable=UiDialogNotification.TunableFactory()), 
     'zone_modifier_requirements':TunableWhiteBlackList(description='\n            A requirement on zone modifiers which must be true on both\n            scheduling and running.\n            ',
       tunable=TunableReference(description='\n                Allowed and disallowed zone modifiers\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.ZONE_MODIFIER)),
       pack_safe=True)), 
     'additional_drama_nodes':TunableList(description='\n            A list of additional drama nodes that we will score and schedule\n            when this drama node is run.  Only 1 drama node is run.\n            ',
       tunable=TunableReference(description='\n                A drama node that we will score and schedule when this drama\n                node is run.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)))), 
     'subvenue':OptionalTunable(description='\n            If enabled, the zones venue will be changed to the specified subvenue\n            at the start of the event, and returned to the primary venue at the\n            end of the event.  Returning to the primary venue at the end of the event\n            will occur immediately if the zone is not currently the active zone,\n            otherwise it will will be delayed by the specified time in order\n            to give the player time to leave the lot prior to being hit by the\n            venue change loadscreen.\n            ',
       tunable=TunableTuple(venue=TunableReference(description='\n                    The subvenue to change to.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.VENUE))),
       delay=TunableTimeSpan(description='\n                    How long to delay the restoration to the default venue type as\n                    long as the zone remains active.\n                    ',
       default_hours=1))), 
     'visibility_tests':TunableGlobalTestSet(description='\n            Tests that must pass in order for this drama node to be marked on the calendar.\n            '), 
     'advance_notice_time':OptionalTunable(description='\n            When enabled allows you to schedule a calendar alert to show up at the tuned number of minutes before event \n            begins.\n            ',
       tunable=TunableTimeSpan(description='\n                The amount of time, in Sim Minutes, before the scheduled drama node that the player should be notified.\n                ')), 
     'show_go_to_button':Tunable(description='\n            When checked the calendar entry for this drama node will have a Go To Event button that the user can\n            click to travel to the event. If this is unchecked that button will be hidden from the UI.\n            ',
       tunable_type=bool,
       default=True,
       tuning_group=GroupNames.UI)}

    @classmethod
    def _verify_tuning_callback(cls):
        if cls.subvenue:
            subvenue = cls.subvenue.venue
            source_venue_type = VenueService.get_variable_venue_source_venue(subvenue)
            if source_venue_type is None:
                logger.error("Venue event drama node {} tuned with subvenue {} that isn't part of a variable venue.", cls, subvenue)
                return
            if source_venue_type.variable_venues.enable_civic_policy_support:
                logger.error('Venue event drama node {} tuned with subvenue {} that is under the control of a civic policy.', cls, subvenue)

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._duration_alarm_handle = None
        self._zone_id = None
        self._shown_notification = False
        self._additional_nodes_processor = None
        self._duration_override = None

    @classproperty
    def drama_node_type(cls):
        return DramaNodeType.VENUE_EVENT

    @classproperty
    def persist_when_active(cls):
        return True

    @classproperty
    def simless(cls):
        return True

    @property
    def zone_id(self):
        return self._zone_id

    @property
    def is_calendar_deletable(self):
        return False

    def get_calendar_end_time(self):
        return self.get_calendar_start_time() + create_time_span(minutes=(self.duration))

    @property
    def zone_director_override(self):
        if services.current_zone_id() == self._zone_id:
            return self.zone_director

    def _setup(self, *args, zone_id=None, gsi_data=None, **kwargs):
        result = (super()._setup)(args, gsi_data=gsi_data, **kwargs)
        if not result:
            return result
        self._zone_id = zone_id
        if self._zone_id is None:
            if gsi_data is not None:
                gsi_data.rejected_nodes.append(GSIRejectedDramaNodeScoringData(type(self), "Failed to setup drama node because it wasn't given a zone id to run in."))
            return False
        return True

    def cleanup(self, from_service_stop=False):
        super().cleanup(from_service_stop=from_service_stop)
        if self._duration_alarm_handle is not None:
            self._duration_alarm_handle.cancel()
            self._duration_alarm_handle = None

    def _test(self, *args, **kwargs):
        if self._zone_id is None:
            return TestResult(False, 'Cannot run Venue Event Drama Node with no zone id set.')
        else:
            zone_modifiers = services.get_zone_modifier_service().get_zone_modifiers(self._zone_id)
            return self.zone_modifier_requirements.test_collection(zone_modifiers) or TestResult(False, 'Incompatible zone modifiers tuned on venue.')
        return (super()._test)(*args, **kwargs)

    def _end_venue_behavior(self):
        if self.zone_director is not None:
            venue_service = services.venue_service()
            if type(venue_service.get_zone_director()) is self.zone_director:
                if self.ending_notification is not None:
                    dialog = self.ending_notification(services.active_sim_info())
                    dialog.show_dialog()
                venue_service.change_zone_director(venue_service.active_venue.zone_director(), True)
        elif self.ending_notification is not None:
            dialog = self.ending_notification(services.active_sim_info())
            dialog.show_dialog()

    def _show_notification(self):
        if self.notification is None:
            return
        if self._shown_notification:
            return
        dialog = self.notification(services.active_sim_info())
        dialog.show_dialog()
        self._shown_notification = True

    def _run_venue_behavior(self):
        if self.zone_director is not None:
            services.venue_service().change_zone_director(self.zone_director(), True)
        self._show_notification()

    def _resume_venue_behavior(self):
        self._show_notification()

    def _on_venue_event_complete(self, _):
        if services.current_zone_id() == self._zone_id:
            self._end_venue_behavior()
        else:
            services.drama_scheduler_service().complete_node(self._uid)
            if self.subvenue is not None:
                venue_game_service = services.venue_game_service()
                if venue_game_service is not None:
                    venue_game_service.restore_venue_type(self._zone_id, self.subvenue.delay())
                else:
                    logger.error("Venue event drama node tuned with subvenue but VenueGameService isn't running.")

    def _show_away_notification(self):
        if self.away_notification is None:
            return
        zone_data = services.get_persistence_service().get_zone_proto_buff(self._zone_id)
        if zone_data is None:
            return
        venue_tuning_id = build_buy.get_current_venue(self._zone_id)
        venue_manager = services.get_instance_manager(sims4.resources.Types.VENUE)
        venue_tuning = venue_manager.get(venue_tuning_id)
        if venue_tuning is None:
            return
        dialog = self.away_notification(services.active_sim_info())
        dialog.show_dialog(additional_tokens=(zone_data.name, venue_tuning.display_name))

    def _process_scoring_gen(self, timeline):
        try:
            try:
                yield from services.drama_scheduler_service().score_and_schedule_nodes_gen((self.additional_drama_nodes), 1,
                  zone_id=(self._zone_id),
                  timeline=timeline)
            except GeneratorExit:
                raise
            except Exception as exception:
                try:
                    logger.exception('Exception while scoring DramaNodes: ', exc=exception,
                      level=(sims4.log.LEVEL_ERROR))
                finally:
                    exception = None
                    del exception

        finally:
            self._additional_nodes_processor = None

        if False:
            yield None

    def _validate_venue_tuning(self):
        venue_tuning_id = build_buy.get_current_venue(self._zone_id)
        venue_manager = services.get_instance_manager(sims4.resources.Types.VENUE)
        venue_tuning = venue_manager.get(venue_tuning_id)
        if venue_tuning is None:
            return False
        if self.subvenue:
            subvenue = self.subvenue.venue
            venue_game_service = services.venue_game_service()
            if venue_game_service is None:
                logger.error("Venue event drama node {} tuned with a subvenue but VenueGameService isn't running.", self)
                return False
            venue_service = services.venue_service()
            source_venue_type = venue_service.get_variable_venue_source_venue(subvenue)
            if source_venue_type is None:
                logger.error("Venue event drama node {} tuned with subvenue {} that isn't part of a variable venue.", self, subvenue)
                return False
            if source_venue_type.variable_venues.enable_civic_policy_support:
                logger.error('Venue event drama node {} tuned with subvenue {} that is under the control of a civic policy.', self, subvenue)
                return False
            if venue_tuning is subvenue:
                return True
        if type(self) not in venue_tuning.drama_node_events:
            return False
        return True

    def _run(self):
        if not self._validate_venue_tuning():
            return DramaNodeRunOutcome.FAILURE
        self._duration_alarm_handle = alarms.add_alarm(self, create_time_span(minutes=(self.duration)), self._on_venue_event_complete)
        if self.subvenue is not None:
            services.venue_game_service().change_venue_type(self._zone_id, self.subvenue.venue)
        if services.current_zone_id() == self._zone_id:
            self._run_venue_behavior()
            return DramaNodeRunOutcome.SUCCESS_NODE_INCOMPLETE
        self._show_away_notification()
        if self.additional_drama_nodes:
            sim_timeline = services.time_service().sim_timeline
            self._additional_nodes_processor = sim_timeline.schedule(elements.GeneratorElement(self._process_scoring_gen))
        return DramaNodeRunOutcome.SUCCESS_NODE_INCOMPLETE

    def schedule_duration_alarm(self, callback, cross_zone=False):
        if self._duration_override is not None:
            time_span = TimeSpan(self._duration_override)
        else:
            time_span = create_time_span(minutes=(self.duration))
        return alarms.add_alarm(self, time_span,
          callback,
          cross_zone=cross_zone)

    def should_resume(self):
        if self.subvenue:
            venue_tuning = services.venue_service().get_venue_tuning(self._zone_id)
            if venue_tuning is not self.subvenue.venue:
                return False
        return True

    def resume(self):
        if not self.should_resume():
            return
        if services.current_zone_id() == self._zone_id:
            self._resume_venue_behavior()
        self._duration_alarm_handle = self.schedule_duration_alarm(self._on_venue_event_complete)

    def _save_custom_data(self, writer):
        writer.write_uint64(ZONE_ID_TOKEN, self._zone_id)
        writer.write_bool(SHOWN_NOTIFICATION_TOKEN, self._shown_notification)
        if self._duration_alarm_handle is not None:
            writer.write_uint64(DURATION_TOKEN, int(self._duration_alarm_handle.get_remaining_time().in_ticks()))

    def _load_custom_data(self, reader):
        self._zone_id = reader.read_uint64(ZONE_ID_TOKEN, None)
        if self._zone_id is None:
            return False
        self._shown_notification = reader.read_bool(SHOWN_NOTIFICATION_TOKEN, False)
        self._duration_override = reader.read_uint64(DURATION_TOKEN, None)
        return True

    @flexmethod
    def get_destination_lot_id(cls, inst):
        inst_or_cls = cls if inst is None else inst
        if inst_or_cls._zone_id is None:
            logger.error('Failed to travel to venue')
            return
        return services.get_persistence_service().get_lot_id_from_zone_id(inst_or_cls._zone_id)

    @flexmethod
    def get_travel_interaction(cls, inst):
        return VenueEventDramaNode.GO_TO_VENUE_ZONE_INTERACTION

    def load(self, drama_node_proto, schedule_alarm=True):
        super_success = super().load(drama_node_proto, schedule_alarm=schedule_alarm)
        if not super_success:
            return False
        else:
            return self._validate_venue_tuning() or False
        if self.ui_display_type != DramaNodeUiDisplayType.NO_UI:
            resolver = GlobalResolver()
            if self.visibility_tests.run_tests(resolver):
                advance_notice_time = None if self.advance_notice_time is None else self.advance_notice_time()
                services.calendar_service().mark_on_calendar(self, advance_notice_time=advance_notice_time)
        return True

    def schedule(self, resolver, specific_time=None, time_modifier=TimeSpan.ZERO, **kwargs):
        success = (super().schedule)(resolver, specific_time=specific_time, time_modifier=time_modifier, **kwargs)
        if success:
            if self.ui_display_type != DramaNodeUiDisplayType.NO_UI:
                global_resolver = GlobalResolver()
                if self.visibility_tests.run_tests(global_resolver):
                    advance_notice_time = None if self.advance_notice_time is None else self.advance_notice_time()
                    services.calendar_service().mark_on_calendar(self, advance_notice_time=advance_notice_time)
        return success

    def create_calendar_entry(self):
        calendar_entry = super().create_calendar_entry()
        calendar_entry.zone_id = self._zone_id
        build_icon_info_msg(IconInfoData(icon_resource=(self._display_data.instance_display_icon)), self._display_data.instance_display_name, calendar_entry.icon_info)
        calendar_entry.scoring_enabled = False
        calendar_entry.show_go_to_event_button = self.show_go_to_button
        return calendar_entry

    def create_calendar_alert(self):
        calendar_alert = super().create_calendar_alert()
        build_icon_info_msg(IconInfoData(icon_resource=(self.display_icon)), self.display_name, calendar_alert.calendar_icon)
        calendar_alert.zone_id = self._zone_id
        calendar_alert.show_go_to_button = True
        return calendar_alert


lock_instance_tunables(VenueEventDramaNode, ui_display_data=None)

class OrganizationEventDramaNode(VenueEventDramaNode):
    INSTANCE_TUNABLES = {'fake_duration':TunableSimMinute(description="\n            The amount of time in Sim minutes that is used by UI to display the\n            drama node's activity's duration.  When the event actually runs the\n            open street director determines actual end-time.\n            ",
       default=60,
       minimum=1), 
     'organization':TunableReference(description='\n            The organization for which this drama node is scheduling venue events.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SNIPPET),
       class_restrictions='Organization'), 
     'location':TunableLocalizedString(description="\n            The string used to populate UI's location field in the \n            organization events panel.\n            ")}

    @classmethod
    def _verify_tuning_callback(cls):
        if cls._display_data.instance_display_name is None:
            logger.error('Display data from Drama Node ({}) is sent to UI, but                             has a display name of None value, which cannot be True.', cls)
        if cls._display_data.instance_display_description is None:
            logger.error('Display data from Drama Node ({}) is sent to UI, but                            has a display description of None value, which cannot be True.', cls)
        if cls.time_option.option != TimeSelectionOption.SINGLE_TIME:
            logger.error('Drama Node ({}) need a single time tuned in order to schedule,                          but does not. It will not schedule.', cls)

    def _validate_venue_tuning(self):
        return True

    def load(self, *args, **kwargs):
        if not (super().load)(*args, **kwargs):
            return False
        org_service = services.organization_service()
        icon_info = IconInfoData(icon_resource=(self._display_data.instance_display_icon))
        org_event_info = OrgEventInfo(drama_node=self, schedule=(self._selected_time),
          fake_duration=(self.fake_duration),
          icon_info=icon_info,
          name=(self._display_data.instance_display_name),
          description=(self._display_data.instance_display_description),
          location=(self.location),
          zone_id=(self._zone_id))
        org_service.add_venue_event_update(self.organization.guid64, org_event_info, self.uid, str(type(self)))
        return True

    def should_resume(self):
        return services.organization_service().validate_venue_event(self)

    def schedule(self, *args, **kwargs):
        success = (super().schedule)(*args, **kwargs)
        if success:
            icon_info = IconInfoData(icon_resource=(self._display_data.instance_display_icon))
            org_event_info = OrgEventInfo(drama_node=self, schedule=(self._selected_time),
              fake_duration=(self.fake_duration),
              icon_info=icon_info,
              name=(self._display_data.instance_display_name),
              description=(self._display_data.instance_display_description),
              location=(self.location),
              zone_id=(self.zone_id))
            services.organization_service().add_venue_event_update(self.organization.guid64, org_event_info, self.uid, str(type(self)))
        return success


lock_instance_tunables(OrganizationEventDramaNode, subvenue=None)