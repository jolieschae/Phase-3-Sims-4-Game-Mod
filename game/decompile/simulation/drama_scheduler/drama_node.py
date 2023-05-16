# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\drama_node.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 80473 bytes
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
from _collections import defaultdict
from distributor.rollback import ProtocolBufferRollback
from protocolbuffers import UI_pb2, Dialog_pb2
from protocolbuffers.DistributorOps_pb2 import Operation
import alarms, date_and_time, interactions, services, sims4.resources
from careers.career_ops import CareerTimeOffReason
from clubs import UnavailableClubError
from date_and_time import create_time_span, DateAndTime, date_and_time_from_week_time, DATE_AND_TIME_ZERO, TimeSpan
from default_property_stream_reader import DefaultPropertyStreamReader
from distributor.ops import GenericProtocolBufferOp
from distributor.shared_messages import build_icon_info_msg, IconInfoData
from distributor.system import Distributor
from drama_scheduler.drama_enums import DramaNodeRunOutcome, DramaNodeUiDisplayType, DramaNodeScoringBucket, WeeklySchedulingGroup, DramaNodeParticipantOption, TimeSelectionOption, CooldownOption, CooldownGroup, SenderSimInfoType
from drama_scheduler.drama_node_types import DramaNodeType
from event_testing.resolver import DoubleSimResolver, SingleSimResolver
from event_testing.results import TestResult
from event_testing.tests import TunableTestSet
from gsi_handlers.drama_handlers import GSIRejectedDramaNodeScoringData, is_drama_node_log_enabled, log_drama_node_scoring, DramaNodeLogActions
from interactions import ParticipantType, ParticipantTypeSingleSim, STORY_PROGRESSION_SIM_PARTICIPANTS, ParticipantTypeSavedStoryProgression, get_number_of_bit_shifts_by_participant_type, ParticipantTypeSim
from interactions.utils.tunable_icon import TunableIcon
from objects import ALL_HIDDEN_REASONS, ALL_HIDDEN_REASONS_EXCEPT_UNINITIALIZED
from protocolbuffers import UI_pb2, Dialog_pb2
from protocolbuffers.DistributorOps_pb2 import Operation
from scheduler_utils import TunableDayAvailability
from server.pick_info import PickInfo, PickType
from sims.sim_info_lod import SimInfoLODLevel
from sims4 import random
from sims4.callback_utils import CallableList
from sims4.common import Pack
from sims4.localization import TunableLocalizedString
from sims4.math import POS_INFINITY
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableRange, Tunable, TunableList, TunableTuple, TunableVariant, TunableEnumEntry, TunableReference, TunableInterval, OptionalTunable, HasTunableReference, TunableMapping
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import classproperty, flexmethod
from tunable_time import TunableTimeOfDay, TunableTimeOfWeek
logger = sims4.log.Logger('DramaNode', default_owner='jjacobson')
NODE_COOLDOWN = 0
GROUP_COOLDOWN = 1

class _DramaNodeCooldown(TunableTuple):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, duration=OptionalTunable(description='\n                If this drama node will be put on cooldown for a duration or put on cooldown permanently.\n                ',
  tunable=TunableRange(description='\n                    The amount of time in hours after being given this node from\n                    scoring that it will not be chosen.\n                    ',
  tunable_type=float,
  default=1,
  minimum=0),
  enabled_name='duration',
  disabled_name='permanent',
  enabled_by_default=True), 
         cooldown_option=TunableEnumEntry(description='\n                When this drama node should be put on cooldown.\n                ',
  tunable_type=CooldownOption,
  default=(CooldownOption.ON_RUN)), **kwargs)


class _DramaParticipant(TunableVariant):

    def __init__(self, description='A drama participant', default='participant_type', excluded_options=(), **kwargs):
        options = {'no_participant':TunableTuple(description=',\n                There is no participant for this drama participant.\n                ',
           locked_args={'type': DramaNodeParticipantOption.DRAMA_PARTICIPANT_OPTION_NONE}), 
         'participant_type':TunableTuple(description='\n                Use a specific participant type from the system that called\n                this drama node to resolve this drama participant.\n                ',
           participant_type=TunableEnumEntry(description="\n                    The participant type to use to resolve the drama node's\n                    participant.\n                    ",
           tunable_type=ParticipantType,
           default=(ParticipantType.Actor)),
           locked_args={'type': DramaNodeParticipantOption.DRAMA_PARTICIPANT_OPTION_PARTICIPANT_TYPE}), 
         'sim_filter':TunableTuple(description='\n                Use a sim filter relative to specific participant of the system\n                that called this drama node.  Usually this participant type\n                will be the same as the participant that is used for the\n                receiving sim, but there can be exceptions.  Ex. If a sim dies\n                you might want a sim who is a friend of the person who died to\n                send the message rather than a person who is a friend of the\n                player sim that will receive this message. \n                ',
           participant_type=TunableEnumEntry(description='\n                    The participant type to use to request the filter.\n                    ',
           tunable_type=ParticipantType,
           default=(ParticipantType.Actor)),
           sim_filter=TunableReference(description="\n                    The sim filter that we will use to find the sim that will\n                    be used for this drama node's participant.\n                    ",
           manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER))),
           blacklist_participants=TunableList(description='\n                    A list of participants that will be blacklisted from the\n                    filter.\n                    ',
           tunable=TunableEnumEntry(description='\n                        The participant type to blacklist for the filter.\n                        ',
           tunable_type=ParticipantTypeSim,
           default=(ParticipantTypeSim.Actor))),
           constrained_sims=OptionalTunable(description='\n                    If enabled then we will also constrain the filter being run to the Sims within\n                    this participant.\n                    ',
           tunable=TunableEnumEntry(description='\n                        The participant that will be used as the constrained Sims.\n                        ',
           tunable_type=ParticipantTypeSim,
           default=(ParticipantTypeSim.Actor))),
           locked_args={'type': DramaNodeParticipantOption.DRAMA_PARTICIPANT_OPTION_FILTER})}
        for key in excluded_options:
            del options[key]

        kwargs.update(options)
        (super().__init__)(description=description, default=default, **kwargs)


class BaseDramaNode(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)):
    COOLDOWN_GROUPS = TunableMapping(key_type=TunableEnumEntry(description='\n            The cooldown group that this cooldown is a part of.\n            ',
      tunable_type=CooldownGroup,
      default=(CooldownGroup.INVALID),
      invalid_enums=(
     CooldownGroup.INVALID,)),
      value_type=(_DramaNodeCooldown()))
    INSTANCE_SUBCLASSES_ONLY = True
    INSTANCE_TUNABLES = {'min_and_max_times':TunableInterval(description="\n            The minimum and maximum times in hours that this node will run from the point that it is scheduled.\n            A random value between them, that's also valid for Time Option is needed for it to be scheduled.\n            For example: Minimum time 5 - Maximum time 12. 5 hours after the node is scheduled (at 3 am), there will \n            be a 7 hour window in which the node can be started. Our time option sets up a window of 8 hours after 9 am.\n            So, our valid window is between 9 am, and 3pm, since that's the only range valid for both tunables.\n            ",
       tunable_type=float,
       default_lower=1.0,
       default_upper=2.0,
       minimum=0.0,
       tuning_group=GroupNames.TIME), 
     'time_option':TunableVariant(description='\n            How we want to try and schedule this drama node based on time. \n            Look at Min and Max times for more information on how a valid time is chosen.\n            ',
       schedule=TunableTuple(description='\n                Schedule this node based on a schedule.  We will pick any time\n                valid within the schedule. \n                The time picked also needs to be valid for the range defined in min and max times.\n                ',
       valid_times=TunableList(description='\n                    The valid times that this node can be scheduled.\n                    ',
       tunable=TunableTuple(description='\n                        The days, start time, and duration that this node is\n                        valid.\n                        ',
       days_available=(TunableDayAvailability()),
       start_time=TunableTimeOfDay(default_hour=9),
       duration=TunableRange(description='\n                            The duration that this this node is available in\n                            hours.\n                            ',
       tunable_type=float,
       default=1,
       minimum=0))),
       locked_args={'option': TimeSelectionOption.SCHEDULE}),
       single_time=TunableTuple(description='\n                Only a single possible time can be selected.\n                The time picked also needs to be valid for the range defined in min and max times.\n                ',
       valid_time=TunableTimeOfWeek(description='\n                    A single time of the week that this drama node will be\n                    available.\n                    '),
       locked_args={'option': TimeSelectionOption.SINGLE_TIME}),
       default='schedule',
       tuning_group=GroupNames.TIME), 
     'allow_during_work_hours':Tunable(description="\n            If this node can be scheduled during a Sim's work hours.\n            ",
       tunable_type=bool,
       default=True,
       tuning_group=GroupNames.TIME), 
     'receiver_sim':TunableEnumEntry(description='\n            The participant type to use to find who will be the receiving\n            Sim for this DramaNode.\n            \n            The receiving Sim will be the one that receives the DramaNode.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor,
       tuning_group=GroupNames.PARTICIPANT), 
     'receiver_sim_pretests':TunableTestSet(description='\n            A set of tests to run on the receiving Sim before attempting to\n            even setup the drama node.\n            '), 
     'sender_sim_info':_DramaParticipant(description='\n            Tuning for selecting the sending Sim.\n            \n            The sending Sim is considered the Sim who will be sending this\n            DramaNode.\n            ',
       tuning_group=GroupNames.PARTICIPANT), 
     'sender_sim_info_type':TunableEnumEntry(description='\n            The type of sender sim info allowed for the drama node.\n            ',
       tunable_type=SenderSimInfoType,
       default=SenderSimInfoType.UNINSTANCED_ONLY,
       tuning_group=GroupNames.PARTICIPANT), 
     'picked_sim_info':_DramaParticipant(description='\n            An optional Sim that acts as ParticipantType.PickedSim if supplied.\n            Useful for if a third Sim is involved, e.g. a text message drama\n            node that says "Hey, my sister <Sender\'s sister\'s Sim name> likes\n            your hair!"\n            ',
       default='no_participant',
       tuning_group=GroupNames.PARTICIPANT), 
     'override_picked_sim_info_resolver':Tunable(description='\n            If true, override the resolver used when determining the Picked Sim Info to be a DoubleSimResolver where\n            the Actor is the Receiver Sim Info, and the TargetSim is the Sender Sim Info. This should be used if the\n            Picked Sim Info needs to be determined based on the result of the Receiver Sim Info or Sender Sim Info,\n            instead of the active Sim. e.g. a phone call drama node that says "Hey, should I ask <Sender\'s friend\'s\n            Sim name> out on a date?".\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.PARTICIPANT), 
     'scoring':OptionalTunable(description='\n            If enabled this DramaNode will be scored and chosen by the drama\n            service.\n            If there are multiple nodes for the same scoring bucket, they will be scored relative to each other.\n            If obtained through loot or any other systems this should be disabled. If this is scheduled by another\n            drama node, it needs to use the special scoring bucket.\n            Ask your GPE partner if you have any questions if scoring should be enabled or not.\n            ',
       tunable=TunableTuple(description='\n                Data related to scoring this DramaNode.\n                ',
       base_score=TunableRange(description='\n                    The base score of this drama node.  This score will be\n                    multiplied by the score of the different filter results\n                    used to find the Sims for this DramaNode to find the final\n                    result.\n                    ',
       tunable_type=int,
       default=1,
       minimum=1),
       bucket=TunableEnumEntry(description="\n                    Which scoring bucket should these drama nodes be scored as\n                    part of.  Only Nodes in the same bucket are scored against\n                    each other.\n                    \n                    Change different bucket settings within the Drama Node's\n                    module tuning.\n                    ",
       tunable_type=DramaNodeScoringBucket,
       default=(DramaNodeScoringBucket.DEFAULT)),
       receiving_sim_scoring_filter=OptionalTunable(description='\n                    If enabled then we will generate a score for for the\n                    receiving  Sim to be factored into the scoring of this\n                    DramaNode.\n                    ',
       tunable=TunableReference(description='\n                        The filter that we will use to generate a score for the\n                        receiving Sim.\n                        ',
       manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER))))),
       tuning_group=GroupNames.SCORING), 
     'weekly_scheduling_rules':OptionalTunable(description='\n            If enabled this DramaNode will be scheduled in a weekly basis.\n            This scheduler is separate from scoring hence will ignore scoring rules, mix max times, cooldowns etc.\n            We are planning to eventually obsolete scoring and use weekly scheduler instead for nodes like festivals. \n            ',
       tunable=TunableTuple(description='\n                Data related to scheduling this DramaNode weekly.\n                ',
       weight=TunableRange(description='\n                    Since we are scheduling nodes rotationally so each node will be scheduled\n                    sooner or later.\n                    But nodes with higher weight will be scheduled first at the beginning of the game.\n                    ',
       tunable_type=int,
       default=1,
       minimum=1),
       scheduling_group=TunableEnumEntry(description='\n                    Which weekly scoring group should these drama nodes be in.\n                    Nodes in a same group will be scheduled weekly and rotationally using\n                    the rule defined on that group.\n                    Change different group settings within the drama_scheduler module tuning.\n                    ',
       tunable_type=WeeklySchedulingGroup,
       default=(WeeklySchedulingGroup.DEFAULT))),
       tuning_group=GroupNames.TIME), 
     'run_tests':TunableTestSet(description='\n            A set of specific tests that will run on the target Sim to see if\n            they are valid for this DramaNode.  These tests will only be run\n            when the drama node is about to be run. \n            '), 
     'tests_failed_loot':TunableList(description='\n            A list of loot actions to apply if the tests that run when the\n            drama node is about to be run fail. This includes both the tuned\n            run_tests as well as any tests in the code.\n            ',
       tunable=TunableReference(description='\n                Loot action to apply if the run tests fail.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', ))), 
     'pretests':TunableTestSet(description='\n            A set of specific tests that will run on the target Sim to see if\n            they are valid for this DramaNode.  These tests will be run both\n            when scheduling the drama node and when it is about to be run.\n            '), 
     'additional_pack':OptionalTunable(description='\n            If enabled, this drama node is only available if you have a\n            specific pack.  This should only be used if two packs are required\n            to see the content and to have it actually function.\n            ',
       tunable=TunableEnumEntry(description='\n                Pack required for this drama node to run.\n                ',
       tunable_type=Pack,
       default=(Pack.BASE_GAME))), 
     'ui_display_type':TunableEnumEntry(description='\n            How Calendar should display this type of drama node.\n            ',
       tunable_type=DramaNodeUiDisplayType,
       default=DramaNodeUiDisplayType.NO_UI,
       tuning_group=GroupNames.UI), 
     'ui_display_data':OptionalTunable(description='\n            Information for what should show up on the calendar\n            ',
       tunable=TunableTuple(name=(TunableLocalizedString()),
       icon=(TunableIcon())),
       tuning_group=GroupNames.UI), 
     'cooldown_data':TunableVariant(description='\n            The different types of cooldowns that can be applied to this drama node.\n            ',
       node_cooldown=_DramaNodeCooldown(description='\n                Put the drama node on cooldown for itself.\n                ',
       locked_args={'cooldown_type': NODE_COOLDOWN}),
       group_cooldown=TunableTuple(description='\n                Put the drama node on cooldown based on a group.\n                ',
       group=TunableEnumEntry(description='\n                    The cooldown group that this drama node is a part of.\n                    ',
       tunable_type=CooldownGroup,
       default=(CooldownGroup.INVALID),
       invalid_enums=(
      CooldownGroup.INVALID,)),
       locked_args={'cooldown_type': GROUP_COOLDOWN})), 
     'reschedule_on_failed_tests':OptionalTunable(description='\n            If this node should be rescheduled to be attempted to run again if the drama node fails\n            to run due to failed tests.  This will use a seperate min and max time.\n            ',
       tunable=TunableInterval(description='\n                The minimum and maximum times for rescheduling this node.  A random\n                valid time between these two values will be selected for the actual\n                time that this node is rescheduled.\n                ',
       tunable_type=float,
       default_lower=1.0,
       default_upper=2.0,
       minimum=0.0),
       enabled_name='reschedule',
       disabled_name='do_not_reschedule')}

    def __init__(self, uid=None, **kwargs):
        self._uid = uid
        self._sender_sim_info = None
        self._sender_sim_info_score = None
        self._receiver_sim_info = None
        self._receiver_sim_info_score = None
        self._picked_sim_info = None
        self._selected_time = None
        self._alarm_handle = None
        self._setup_complete = False
        self._club_id = None
        self._callbacks_on_complete = CallableList()
        self._callbacks_on_cleanup = CallableList()
        self._story_progression_participants = None

    def __repr__(self):
        return '{}:{}'.format(self.__class__.__name__, self.selected_time)

    @classproperty
    def cooldown(cls):
        if cls.cooldown_data is None:
            return
        if cls.cooldown_data.cooldown_type == GROUP_COOLDOWN:
            return BaseDramaNode.COOLDOWN_GROUPS[cls.cooldown_data.group]
        return cls.cooldown_data

    @classproperty
    def drama_node_type(cls):
        return DramaNodeType.DEFAULT

    @classproperty
    def persist_when_active(cls):
        return False

    @classproperty
    def simless(cls):
        return False

    @classmethod
    def get_debug_valid_time_strings(cls):
        valid_time_strings = defaultdict(list)
        if cls.time_option.option == TimeSelectionOption.SCHEDULE:
            for valid_time in cls.time_option.valid_times:
                start_tick = valid_time.start_time.absolute_ticks()
                end_tick = start_tick + date_and_time.create_time_span(hours=(valid_time.duration)).in_ticks()
                end_time = DateAndTime(end_tick)
                valid_hour_period = '{:02}:{:02}-{:02}:{:02}'.format(valid_time.start_time.hour(), valid_time.start_time.minute(), end_time.hour(), end_time.minute())
                for day, day_enabled in valid_time.days_available.items():
                    if day_enabled:
                        valid_time_strings[day].append(valid_hour_period)

        return valid_time_strings

    @property
    def _require_instanced_sim(self):
        return True

    @property
    def uid(self):
        return self._uid

    @property
    def zone_director_override(self):
        pass

    @property
    def selected_time(self):
        return self._selected_time

    @property
    def day(self):
        return int(self._selected_time.absolute_days())

    def debug_set_selected_time(self, time):
        self._selected_time = time

    def get_receiver_sim_info(self):
        return self._receiver_sim_info

    def get_sender_sim_info(self):
        return self._sender_sim_info

    def get_picked_sim_info(self):
        return self._picked_sim_info

    def get_time_remaining(self):
        if self._alarm_handle is None:
            return TimeSpan.ZERO
        return self._alarm_handle.get_remaining_time()

    def get_time_off_reason(self, sim_info, career_category, end_time):
        return CareerTimeOffReason.NO_TIME_OFF

    def get_situation_seed(self):
        pass

    def create_calendar_entry(self):
        calendar_entry = UI_pb2.CalendarEntry()
        calendar_entry.entry_id = self.uid
        calendar_entry.entry_guid = self.guid64
        calendar_entry.entry_type = self.ui_display_type
        calendar_entry.start_time = self.get_calendar_start_time().absolute_ticks()
        node_end_time = self.get_calendar_end_time()
        calendar_entry.end_time = node_end_time.absolute_ticks() if node_end_time is not None else 0
        calendar_entry.scoring_enabled = self.score is not None
        calendar_entry.deletable = self.is_calendar_deletable
        calendar_entry.in_progress = False
        if self.ui_display_data:
            build_icon_info_msg(IconInfoData(icon_resource=(self.ui_display_data.icon)), self.ui_display_data.name, calendar_entry.icon_info)
        calendar_sims = self.get_calendar_sims()
        if calendar_sims is not None:
            for sim_info in calendar_sims:
                if not sim_info.is_npc:
                    calendar_entry.household_sim_ids.append(sim_info.id)

        return calendar_entry

    def create_calendar_alert(self):
        calendar_alert = Dialog_pb2.UiCalendarMessage()
        calendar_alert.event_type = self.ui_display_type
        calendar_alert.start_time = self.get_calendar_start_time().absolute_ticks()
        calendar_alert.drama_node_guid = self.guid64
        calendar_sims = self.get_calendar_sims()
        if calendar_sims is not None:
            for sim_info in calendar_sims:
                if not sim_info.is_npc:
                    calendar_alert.sim_ids.append(sim_info.id)

        return calendar_alert

    def get_calendar_start_time(self):
        return self.selected_time

    def get_calendar_end_time(self):
        pass

    def get_calendar_sims(self):
        pass

    @property
    def is_calendar_deletable(self):
        return True

    def create_picker_row(self, **kwargs):
        pass

    def get_picker_schedule_time(self):
        pass

    def _get_resolver(self):
        additional_participants = {}
        additional_localization_tokens = []
        if self._picked_sim_info is not None:
            additional_participants[ParticipantType.PickedSim] = (
             self._picked_sim_info,)
            additional_localization_tokens.append(self._picked_sim_info)
        if self._club_id is not None:
            chosen_club = services.get_club_service().get_club_by_id(self._club_id)
            if chosen_club is None:
                raise UnavailableClubError
            additional_participants[ParticipantType.AssociatedClub] = (
             chosen_club,)
            additional_localization_tokens.append(chosen_club.name)
        if self._story_progression_participants is not None:
            sim_info_manager = services.sim_info_manager()
            for participant_type, participant in self._story_progression_participants.items():
                if participant_type & STORY_PROGRESSION_SIM_PARTICIPANTS:
                    participant = sim_info_manager.get(participant)
                    if participant is None:
                        continue
                additional_participants[participant_type] = (
                 participant,)
                additional_localization_tokens.append(participant)

        return DoubleSimResolver((self._receiver_sim_info), (self._sender_sim_info), additional_participants=additional_participants,
          additional_localization_tokens=(tuple(additional_localization_tokens)))

    def _setup(self, resolver, gsi_data=None, **kwargs):
        if not self.simless:
            self._receiver_sim_info = resolver.get_participant(self.receiver_sim)
            if self._receiver_sim_info is None:
                if gsi_data is not None:
                    gsi_data.rejected_nodes.append(GSIRejectedDramaNodeScoringData(type(self), "Failed to setup drama node because it couldn't find receiver sim info of participant {}", self.receiver_sim))
                return False
            reciever_sim_resolver = SingleSimResolver(self._receiver_sim_info)
            if not self.receiver_sim_pretests.run_tests(reciever_sim_resolver):
                if gsi_data is not None:
                    gsi_data.rejected_nodes.append(GSIRejectedDramaNodeScoringData(type(self), 'Failed to setup drama node because receiver sim info {} does not pass the receiver sim pretests.', self.receiver_sim))
                return False
            success, self._sender_sim_info, self._sender_sim_info_score = self._resolve_drama_participant(self.sender_sim_info, resolver)
            if not success:
                if gsi_data is not None:
                    gsi_data.rejected_nodes.append(GSIRejectedDramaNodeScoringData(type(self), "Failed to setup drama node because it couldn't find a valid sender sim"))
                return False
            picked_sim_resolver = resolver
            if self.override_picked_sim_info_resolver:
                picked_sim_resolver = DoubleSimResolver(self._receiver_sim_info, self._sender_sim_info)
            success, self._picked_sim_info, _ = self._resolve_drama_participant(self.picked_sim_info, picked_sim_resolver)
            if not success:
                if gsi_data is not None:
                    gsi_data.rejected_nodes.append(GSIRejectedDramaNodeScoringData(type(self), "Failed to setup drama node because it couldn't find a valid picked sim"))
                return False
        else:
            try:
                club = resolver.get_participant(ParticipantType.AssociatedClub)
                if club is not None:
                    self._club_id = club.club_id
            except ValueError:
                self._club_id = None

        for participant_type in ParticipantTypeSavedStoryProgression:
            try:
                participant = resolver.get_participant(participant_type)
                if participant is None:
                    continue
                if self._story_progression_participants is None:
                    self._story_progression_participants = {}
                if participant_type & STORY_PROGRESSION_SIM_PARTICIPANTS:
                    participant = participant.sim_id
                self._story_progression_participants[participant_type] = participant
            except ValueError:
                continue

        return True

    def _resolve_drama_participant(self, drama_participant, resolver):
        if drama_participant.type == DramaNodeParticipantOption.DRAMA_PARTICIPANT_OPTION_NONE:
            return (True, None, None)
        else:
            if drama_participant.type == DramaNodeParticipantOption.DRAMA_PARTICIPANT_OPTION_PARTICIPANT_TYPE:
                sim_info = resolver.get_participant(drama_participant.participant_type)
                if sim_info is None:
                    return (False, None, None)
                    return (True, sim_info, None)
                    if drama_participant.type == DramaNodeParticipantOption.DRAMA_PARTICIPANT_OPTION_FILTER:
                        requesting_sim_info = resolver.get_participant(drama_participant.participant_type)
                        if requesting_sim_info is None:
                            return (False, None, None)
                        if drama_participant.constrained_sims is not None:
                            sim_constraints = [sim_info.sim_id for sim_info in resolver.get_participants(drama_participant.constrained_sims)]
                else:
                    sim_constraints = None
            else:
                blacklist_sim_ids = set()
                for participant_type in drama_participant.blacklist_participants:
                    sim_infos = resolver.get_participants(participant_type)
                    if not sim_infos:
                        continue
                    blacklist_sim_ids.update((sim_info.id for sim_info in sim_infos))

                if self._club_id is not None:
                    club = services.get_club_service().get_club_by_id(self._club_id)
                else:
                    club = None
                results = services.sim_filter_service().submit_filter((drama_participant.sim_filter), callback=None,
                  allow_yielding=False,
                  sim_constraints=sim_constraints,
                  blacklist_sim_ids=blacklist_sim_ids,
                  club=club,
                  requesting_sim_info=requesting_sim_info,
                  gsi_source_fn=(self.get_sim_filter_gsi_name))
                return results or (False, None, None)
            chosen_result = random.pop_weighted([(result.score, result) for result in results])
            return (True, chosen_result.sim_info, chosen_result.score)
        logger.error('Resolving an unhandled type. {}', drama_participant.type)
        return (False, None, None)

    def get_sim_filter_gsi_name(self):
        return str(self)

    def setup(self, resolver, gsi_data=None, **additional_drama_node_kwargs):
        if self._setup_complete:
            return True
        if (self._setup)(resolver, gsi_data=gsi_data, **additional_drama_node_kwargs):
            self._setup_complete = True
            return True
        return False

    def cleanup(self, from_service_stop=False):
        self._callbacks_on_cleanup(self)
        self._sender_sim_info = None
        self._receiver_sim_info = None
        self._selected_time = None
        if self._alarm_handle is not None:
            alarms.cancel_alarm(self._alarm_handle)
            self._alarm_handle = None

    def add_callback_on_cleanup_func(self, callback_func):
        self._callbacks_on_cleanup.append(callback_func)

    def add_callback_on_complete_func(self, callback_func):
        self._callbacks_on_complete.append(callback_func)

    def complete(self, from_shutdown=False):
        self._callbacks_on_complete(self, from_shutdown=from_shutdown)

    def _select_time(self, specific_time=None, time_modifier=TimeSpan.ZERO, interval_override=None):
        inverval = self.min_and_max_times if interval_override is None else interval_override
        if specific_time is not None:
            self._selected_time = specific_time
            return True
        if self.time_option.option == TimeSelectionOption.SCHEDULE:
            return self._select_time_based_on_schedule(inverval, time_modifier=time_modifier)
        if self.time_option.option == TimeSelectionOption.SINGLE_TIME:
            return self._select_time_based_on_single_time(inverval, time_modifier=time_modifier)
        logger.error('Trying to select time with invalid time option tuned {}', self.time_option.option)

    def _get_min_max_start_times_in_week_time_blocks(self, interval, anchor_time=None, time_modifier=TimeSpan.ZERO):
        possible_time_blocks = []
        now = anchor_time if anchor_time is not None else services.time_service().sim_now
        max_time_span = create_time_span(hours=(interval.upper_bound)) - time_modifier
        if max_time_span < TimeSpan.ZERO:
            return possible_time_blocks
        min_time_span = create_time_span(hours=(interval.lower_bound)) - time_modifier
        if min_time_span < TimeSpan.ZERO:
            min_time_span = TimeSpan.ZERO
        min_start_time = now + min_time_span
        max_start_time = now + max_time_span
        overlapping_week_blocks = max_start_time.week() - min_start_time.week()
        if overlapping_week_blocks == 0:
            possible_time_blocks.append((min_start_time, max_start_time))
        else:
            possible_time_blocks = []
            possible_time_blocks.append((min_start_time, min_start_time.start_of_next_week() + TimeSpan.NEGATIVE_ONE))
            possible_time_blocks.append((max_start_time.start_of_week(), max_start_time))
            if overlapping_week_blocks > 1:
                starting_week = min_start_time.week() + 1
                while starting_week < max_start_time.week():
                    possible_time_blocks.append((date_and_time_from_week_time(starting_week, DATE_AND_TIME_ZERO),
                     date_and_time_from_week_time(starting_week + 1, DATE_AND_TIME_ZERO) + TimeSpan.NEGATIVE_ONE))
                    starting_week += 1

            return possible_time_blocks

    def _select_time_based_on_single_time(self, interval, time_modifier=TimeSpan.ZERO):
        time = self.time_option.valid_time().absolute_ticks()
        possible_time_blocks = self._get_min_max_start_times_in_week_time_blocks(interval, time_modifier=time_modifier)
        final_valid_times = []
        for min_start_time, max_start_time in possible_time_blocks:
            min_week_time = min_start_time.time_since_beginning_of_week().absolute_ticks()
            max_week_time = max_start_time.time_since_beginning_of_week().absolute_ticks()
            if not time > max_week_time:
                if time < min_week_time:
                    continue
                start_of_week = min_start_time.start_of_week()
                final_valid_times.append(start_of_week + TimeSpan(time))

        if not final_valid_times:
            logger.info("Couldn't find any valid times for drama node {} so it could not be scheduled.", self)
            return False
        self._selected_time = random.random.choice(final_valid_times)
        return True

    def get_final_times_based_on_schedule(self, interval, anchor_time=None, scheduled_time_only=False, time_modifier=TimeSpan.ZERO):
        if not self.time_option.option == TimeSelectionOption.SCHEDULE:
            logger.error('This function only supports scheduled time option right now.')
            return
        else:
            start_and_end_times = []
            for time_block in self.time_option.valid_times:
                for day, day_enabled in time_block.days_available.items():
                    if not day_enabled:
                        continue
                    days_as_time_span = date_and_time.create_time_span(days=day)
                    start_time = (time_block.start_time + days_as_time_span).absolute_ticks()
                    end_time = start_time + date_and_time.create_time_span(hours=(time_block.duration)).in_ticks()
                    start_and_end_times.append((start_time, end_time))

            start_and_end_times.sort()
            if not self.allow_during_work_hours:
                if not self.simless:
                    career_times = [(start_time, end_time) for career in self._receiver_sim_info.careers.values() for start_time, end_time in iter((career.get_busy_time_periods()))]
                    if career_times:
                        possible_valid_times = []
                        career_times.append((POS_INFINITY, POS_INFINITY))
                        career_times.sort()
                        times_iter = iter(start_and_end_times)
                        career_iter = iter(career_times)
                        start_time, end_time = next(times_iter)
                        career_start_time, career_end_time = next(career_iter)
                        while True:
                            if end_time <= start_time:
                                try:
                                    start_time, end_time = next(times_iter)
                                except StopIteration:
                                    break

                            elif end_time <= career_start_time:
                                possible_valid_times.append((start_time, end_time))
                                try:
                                    start_time, end_time = next(times_iter)
                                except StopIteration:
                                    break

                            elif career_end_time <= start_time:
                                career_start_time, career_end_time = next(career_iter)
                            elif start_time < career_start_time:
                                possible_valid_times.append((start_time, career_start_time))
                                start_time = career_end_time
                            elif career_start_time <= start_time:
                                start_time = career_end_time

                else:
                    possible_valid_times = start_and_end_times
            else:
                possible_valid_times = start_and_end_times
            possible_valid_times or logger.info('Could not find valid time because there are no possible valid times.  This is either bad tuning or a scheduling conflict with the career of the sim.')
            return
        possible_time_blocks = self._get_min_max_start_times_in_week_time_blocks(interval, anchor_time=anchor_time, time_modifier=time_modifier)
        final_valid_times = []
        for min_start_time, max_start_time in possible_time_blocks:
            min_week_time = min_start_time.time_since_beginning_of_week().absolute_ticks()
            max_week_time = max_start_time.time_since_beginning_of_week().absolute_ticks()
            for possible_start, possible_end in possible_valid_times:
                if possible_start > max_week_time or possible_end < min_week_time:
                    continue
                if not scheduled_time_only:
                    if possible_start < min_week_time:
                        possible_start = min_week_time
                    if possible_end > max_week_time:
                        possible_end = max_week_time
                    start_of_week = min_start_time.start_of_week()
                    final_valid_times.append((start_of_week + TimeSpan(possible_start),
                     start_of_week + TimeSpan(possible_end)))

        return final_valid_times

    def _select_time_based_on_schedule(self, interval, time_modifier=TimeSpan.ZERO):
        final_valid_times = self.get_final_times_based_on_schedule(interval, time_modifier=time_modifier)
        if not final_valid_times:
            logger.info('Could not find valid time because there are no valid times between the start and end times.')
            return False
        total_time = sum(((end - start).in_ticks() for start, end in final_valid_times))
        if total_time == 0:
            self._selected_time = final_valid_times[0][0]
            return True
        random_time = random.random.randint(0, total_time)
        for start, end in final_valid_times:
            random_time -= (end - start).in_ticks()
            if random_time <= 0:
                self._selected_time = start + TimeSpan(-random_time)
                return True

        logger.error('Did not select time for node {} despite finding valid times.', self)
        return False

    def _validate_time(self, time_to_check):
        if self.time_option.option != TimeSelectionOption.SCHEDULE:
            return
        week_time = time_to_check.time_since_beginning_of_week()
        for time_block in self.time_option.valid_times:
            for day, day_enabled in time_block.days_available.items():
                if not day_enabled:
                    continue
                days_as_time_span = date_and_time.create_time_span(days=day)
                start_time = time_block.start_time + days_as_time_span
                end_time = start_time + date_and_time.create_time_span(hours=(time_block.duration))
                if start_time <= week_time <= end_time:
                    return

        logger.error('Node {}: Scheduled or trying to run at {}, which is not a valid tuned time.', self,
          time_to_check,
          trigger_breakpoint=True)

    @classmethod
    def get_week_time_for_weekly_schedule(cls):
        if cls.time_option.option == TimeSelectionOption.SINGLE_TIME:
            return cls.time_option.valid_time()
        if cls.time_option.option == TimeSelectionOption.SCHEDULE:
            valid_times = list()
            for time_block in cls.time_option.valid_times:
                for day, day_enabled in time_block.days_available.items():
                    if not day_enabled:
                        continue
                    days_as_time_span = date_and_time.create_time_span(days=day)
                    start_time = time_block.start_time + days_as_time_span
                    valid_times.append(start_time)

            if valid_times:
                return random.random.choice(valid_times)
        logger.error('No valid week time found for weekly schedule of {}, please check Time Option tuning.', self)

    def _alarm_callback(self, _):
        services.drama_scheduler_service()._run_node(self._uid)

    def _schedule_alarm(self):
        if self._selected_time is None:
            logger.error('Trying to schedule alarm for drama node {} when no time has been scheduled.', self)
            return False
        if self._alarm_handle is not None:
            alarms.cancel_alarm(self._alarm_handle)
        time_till_node = self._selected_time - services.time_service().sim_now
        self._alarm_handle = alarms.add_alarm(self, time_till_node, self._alarm_callback)
        return True

    def schedule(self, resolver, specific_time=None, time_modifier=TimeSpan.ZERO, **setup_kwargs):
        if not (self.setup)(resolver, **setup_kwargs):
            return False
        else:
            resolver = self._get_resolver()
            if not self._test(resolver, skip_run_tests=True):
                return False
            if not self._select_time(specific_time=specific_time, time_modifier=time_modifier):
                return False
            return self._schedule_alarm() or False
        return True

    def _run(self):
        raise NotImplementedError

    def run(self):
        try:
            resolver = self._get_resolver()
            test_results = self._test(resolver, skip_run_tests=False)
        except UnavailableClubError as e:
            try:
                test_results = TestResult(False, 'Exception: {}', repr(e))
            finally:
                e = None
                del e

        if not test_results:
            if is_drama_node_log_enabled():
                log_drama_node_scoring(self, DramaNodeLogActions.CANCELED, test_results.reason)
            for loot_action in self.tests_failed_loot:
                loot_action.apply_to_resolver(resolver)

            if self.reschedule_on_failed_tests is not None:
                if self._select_time(interval_override=(self.reschedule_on_failed_tests)):
                    if self._schedule_alarm():
                        return DramaNodeRunOutcome.RESCHEDULED
            return DramaNodeRunOutcome.FAILURE
        if self.cooldown is not None:
            if self.cooldown.cooldown_option == CooldownOption.ON_RUN:
                services.drama_scheduler_service().start_cooldown(type(self))
        if is_drama_node_log_enabled():
            log_drama_node_scoring(self, DramaNodeLogActions.RUNNING)
        return self._run()

    def on_situation_creation_during_zone_spin_up(self) -> 'None':
        pass

    def resume(self):
        pass

    def score(self):
        if self.scoring is None:
            return 0
            score = self.scoring.base_score
            if self._receiver_sim_info_score is None:
                if self.scoring.receiving_sim_scoring_filter is not None:
                    result = services.sim_filter_service().submit_filter((self.scoring.receiving_sim_scoring_filter), callback=None,
                      sim_constraints=(
                     self._receiver_sim_info.id,),
                      allow_yielding=False,
                      gsi_source_fn=(self.get_sim_filter_gsi_name))
                    if not result:
                        return 0
                    self._receiver_sim_info_score = result[0].score
        else:
            self._receiver_sim_info_score = 1
        score *= self._receiver_sim_info_score
        if self._sender_sim_info_score is None:
            self._sender_sim_info_score = 1
        score *= self._sender_sim_info_score
        return score

    def get_score_details(self):
        if self.scoring is None:
            scoring = 'Disabled'
            base_score = 0
            sender_sim_score = 0
            receiver_sim_score = 0
            final_score = 0
        else:
            scoring = 'Enabled'
            base_score = self.scoring.base_score
            sender_sim_score = self._sender_sim_info_score
            receiver_sim_score = self._receiver_sim_info_score
            final_score = self.score()
        return 'Scoring : {scoring}\nBase Score : {base_score}\nSender Sim Score : {sender_sim_score}\nReceiver Sim Score : {receiver_sim_score}\nFinal Score: {final_score} = {base_score} * {sender_sim_score} * {receiver_sim_score}'.format(scoring=scoring,
          base_score=base_score,
          sender_sim_score=sender_sim_score,
          receiver_sim_score=receiver_sim_score,
          final_score=final_score)

    def _test(self, resolver, skip_run_tests=False):
        if not self.simless:
            if self._receiver_sim_info is None:
                return TestResult(False, 'Cannot run because the target sim info is None.')
            else:
                if self.sender_sim_info.type != DramaNodeParticipantOption.DRAMA_PARTICIPANT_OPTION_NONE:
                    if self._sender_sim_info is None:
                        return TestResult(False, 'Cannot run because the sender sim info is None.')
                if self.picked_sim_info.type != DramaNodeParticipantOption.DRAMA_PARTICIPANT_OPTION_NONE and self._picked_sim_info is None:
                    return TestResult(False, 'Cannot run because the picked sim info is None.')
        else:
            result = self.pretests.run_tests(resolver)
            return result or result
        if not skip_run_tests:
            if not self.simless:
                if self._require_instanced_sim:
                    if not self._receiver_sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS):
                        return TestResult(False, 'Cannot run because the target sim is not instanced.')
                else:
                    if self.sender_sim_info.type != DramaNodeParticipantOption.DRAMA_PARTICIPANT_OPTION_NONE:
                        if self._sender_sim_info == SimInfoLODLevel.MINIMUM:
                            return TestResult(False, 'Cannot run because the sender sim info is min LOD.')
                        if self.sender_sim_info_type == SenderSimInfoType.UNINSTANCED_ONLY:
                            if self._sender_sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS):
                                return TestResult(False, 'Cannot run because the sender sim info is instanced.')
                    if not self.allow_during_work_hours:
                        if self._receiver_sim_info.career_tracker.currently_during_work_hours:
                            return TestResult(False, 'Cannot run because the target sim is at work.')
            result = self.run_tests.run_tests(resolver)
            if not result:
                return result
        return TestResult.TRUE

    def try_do_travel_dialog_delay(self) -> 'Optional[DramaNodeRunOutcome]':
        if services.ui_dialog_service().has_active_modal_dialogs():
            current_time = services.time_service().sim_now
            self._selected_time = current_time + create_time_span(minutes=1)
            if not self._schedule_alarm():
                return DramaNodeRunOutcome.FAILURE
            return DramaNodeRunOutcome.RESCHEDULED

    @flexmethod
    def travel_to_destination(cls, inst):
        inst_or_cls = cls if inst is None else inst
        lot_id = inst_or_cls.get_destination_lot_id()
        if lot_id is None:
            return
        travel_interaction = inst_or_cls.get_travel_interaction()
        if travel_interaction is None:
            return
        inst_or_cls.push_travel_interaction(travel_interaction, lot_id)

    @flexmethod
    def push_travel_interaction(cls, inst, travel_interaction, lot_id):
        active_sim_info = services.active_sim_info()
        active_sim = active_sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS_EXCEPT_UNINITIALIZED)
        if active_sim is None:
            return
        pick = PickInfo(pick_type=(PickType.PICK_TERRAIN), lot_id=lot_id,
          ignore_neighborhood_id=True)
        context = interactions.context.InteractionContext(active_sim, (interactions.context.InteractionContext.SOURCE_SCRIPT_WITH_USER_INTENT),
          (interactions.priority.Priority.High),
          insert_strategy=(interactions.context.QueueInsertStrategy.NEXT),
          pick=pick)
        active_sim.push_super_affordance(travel_interaction, None, context)

    @flexmethod
    def get_destination_lot_id(cls, inst):
        pass

    @flexmethod
    def get_travel_interaction(cls, inst):
        pass

    def _save_custom_data(self, writer):
        pass

    def save(self, drama_node_proto):
        drama_node_proto.uid = self._uid
        drama_node_proto.node_type = self.guid64
        drama_node_proto.selected_time = self._selected_time.absolute_ticks()
        if self._receiver_sim_info is not None:
            drama_node_proto.receiver_sim_id = self._receiver_sim_info.id
        if self._receiver_sim_info_score is not None:
            drama_node_proto.receiver_score = self._receiver_sim_info_score
        if self._sender_sim_info is not None:
            drama_node_proto.sender_sim_id = self._sender_sim_info.id
        if self._sender_sim_info_score is not None:
            drama_node_proto.sender_score = self._sender_sim_info_score
        if self._picked_sim_info is not None:
            drama_node_proto.picked_sim_id = self._picked_sim_info.id
        if self._club_id is not None:
            drama_node_proto.club_id = self._club_id
        if self._story_progression_participants is not None:
            for participant_type, participant in self._story_progression_participants.items():
                number_of_shifts = get_number_of_bit_shifts_by_participant_type(participant_type)
                if number_of_shifts is None:
                    continue
                with ProtocolBufferRollback(drama_node_proto.story_progression_participants) as (story_progression_participant):
                    story_progression_participant.participant_type = number_of_shifts
                    if type(participant) is str:
                        story_progression_participant.participant_str = participant
                    else:
                        if type(participant) is int:
                            story_progression_participant.participant = int(participant)
                        else:
                            story_progression_participant.participant_loc_str = participant

        writer = sims4.PropertyStreamWriter()
        self._save_custom_data(writer)
        data = writer.close()
        if writer.count > 0:
            drama_node_proto.custom_data = data

    def _load_custom_data(self, reader):
        return True

    def load(self, drama_node_proto, schedule_alarm=True):
        sim_info_manager = services.sim_info_manager()
        self._uid = drama_node_proto.uid
        self._selected_time = DateAndTime(drama_node_proto.selected_time)
        if drama_node_proto.HasField('receiver_sim_id'):
            self._receiver_sim_info = sim_info_manager.get(drama_node_proto.receiver_sim_id)
            if self._receiver_sim_info is None:
                return False
        if drama_node_proto.HasField('receiver_score'):
            self._receiver_sim_info_score = drama_node_proto.receiver_score
        self._sender_sim_info = sim_info_manager.get(drama_node_proto.sender_sim_id)
        if drama_node_proto.HasField('sender_score'):
            self._sender_sim_info_score = drama_node_proto.sender_score
        self._picked_sim_info = sim_info_manager.get(drama_node_proto.picked_sim_id)
        if drama_node_proto.HasField('club_id'):
            self._club_id = drama_node_proto.club_id
        if drama_node_proto.story_progression_participants:
            self._story_progression_participants = {}
            for story_progression_participant in drama_node_proto.story_progression_participants:
                participant_type = ParticipantType(1 << story_progression_participant.participant_type)
                if story_progression_participant.HasField('participant_str'):
                    participant = story_progression_participant.participant_str
                else:
                    if story_progression_participant.HasField('participant_loc_str'):
                        participant = story_progression_participant.participant_loc_str
                    else:
                        participant = story_progression_participant.participant
                self._story_progression_participants[participant_type] = participant

        if drama_node_proto.HasField('custom_data'):
            reader = DefaultPropertyStreamReader(drama_node_proto.custom_data)
            valid = self._load_custom_data(reader)
            if not valid:
                return False
        if schedule_alarm:
            return self._schedule_alarm()
        return True

    def on_calendar_alert_alarm(self):
        calendar_alert_msg = self.create_calendar_alert()
        if calendar_alert_msg is None:
            return
        op = GenericProtocolBufferOp(Operation.CALENDAR_ALERT, calendar_alert_msg)
        Distributor.instance().add_op_with_no_owner(op)

    def run_immediate(self):
        if self._alarm_handle is not None:
            alarms.cancel_alarm(self._alarm_handle)
            self._alarm_handle = None
        services.drama_scheduler_service()._run_node(self._uid)