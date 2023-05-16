# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\career_tuning.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 129091 bytes
from protocolbuffers.DistributorOps_pb2 import Operation
import protocolbuffers, enum
from audio.primitive import TunablePlayAudio
from away_actions.away_actions import AwayAction
from buffs.tunable import TunableBuffReference
from caches import cached
from careers import career_ops
from careers.career_enums import CareerCategory, CareerOutfitGenerationType, CareerPanelType, CareerShiftType, get_selector_type_from_career_category, CareerSelectorTypes, CareerEventDeclineOptions, TestEventCareersOrigin
from careers.career_location import TunableCareerLocationVariant
from careers.career_scheduler import TunableCareerScheduleVariant, get_career_schedule_for_level
from careers.career_story_progression import CareerStoryProgressionParameters
from distributor.ops import GenericProtocolBufferOp
from distributor.system import Distributor
from event_testing.resolver import SingleSimResolver
from event_testing.test_events import TestEvent
from event_testing.tests import TunableTestSet
from filters.tunable import TunableSimFilter
from interactions import ParticipantType
from interactions.utils.adventure import Adventure
from interactions.utils.loot import LootActions
from interactions.utils.success_chance import SuccessChance
from interactions.utils.tested_variant import TunableTestedVariant
from objects.mixins import SuperAffordanceProviderMixin, TargetSuperAffordanceProviderMixin, MixerProviderMixin, MixerActorMixin
from objects.object_creation import ObjectCreation
from sims.outfits.outfit_generator import TunableOutfitGeneratorReference
from sims.sim_info_types import Age
from sims4.localization import TunableLocalizedStringFactory, TunableLocalizedString
from sims4.math import MAX_UINT64
from sims4.tuning.geometric import TunableCurve
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableTuple, TunableEnumFlags, TunableEnumEntry, OptionalTunable, Tunable, TunableMapping, TunableThreshold, TunableList, TunableReference, TunableRange, HasTunableReference, TunableSimMinute, TunableSet, TunablePercent, HasTunableSingletonFactory, AutoFactoryInit, TunableVariant, TunableRegionDescription, HasTunableFactory, TunablePackSafeReference
from sims4.tuning.tunable_base import GroupNames, ExportModes
from sims4.utils import classproperty
from singletons import DEFAULT
from statistics.base_statistic import StatisticChangeDirection
from statistics.commodity import RuntimeCommodity, CommodityTimePassageFixupType
from statistics.runtime_statistic import RuntimeStatistic
from traits.trait_type import TraitType
from tunable_multiplier import TunableMultiplier, TestedSum
from ui.ui_dialog import UiDialogResponse, UiDialogOkCancel, UiDialogOk, UiDialog, PhoneRingType
from ui.ui_dialog_generic import UiDialogTextInputOk, UiDialogTextInputOkCancel
from ui.ui_dialog_notification import UiDialogNotification, TunableUiDialogNotificationSnippet
from ui.ui_dialog_picker import TunablePickerDialogVariant, ObjectPickerTuningFlags
from ui.ui_dialog_reveal_sequence import UiDialogRevealSequence
from venues.venue_constants import NPCSummoningPurpose
import careers.career_base, event_testing.tests, interactions.utils.interaction_elements, scheduler, services, sims4.localization, sims4.resources, sims4.tuning.tunable, tunable_time, ui.screen_slam
logger = sims4.log.Logger('CareerTuning', default_owner='tingyul')

class ActiveCareerType(enum.Int):
    NON_ACTIVE = 0
    ACTIVE = 1
    MULTI_SIM_ACTIVE = 2


def _get_career_notification_tunable_factory(**kwargs):
    return (UiDialogNotification.TunableFactory)(locked_args={'text_tokens':DEFAULT, 
                   'icon':None, 
                   'primary_icon_response':UiDialogResponse(text=None, ui_request=UiDialogResponse.UiDialogUiRequest.SHOW_CAREER_PANEL), 
                   'secondary_icon':None}, **kwargs)


class CareerToneTuning(AutoFactoryInit, HasTunableSingletonFactory):
    FACTORY_TUNABLES = {'default_action_list':TunableList(description='\n            List of test to default action. Should any test pass, that will\n            be set as the default action.\n            ',
       tunable=TunableTuple(default_action_test=OptionalTunable(description='\n                    If enabled, test will be run on the sim. \n                    Otherwise, no test will be run and default_action tuned will\n                    automatically be chosen. There should only be one item, \n                    which is also the default item in the list which has this \n                    disabled.\n                    ',
       tunable=TunableTestSet(description='\n                        Test to run to figure out what the default away action \n                        should be.\n                        ')),
       default_action=AwayAction.TunableReference(description='\n                    Default away action tone.\n                    '))), 
     'optional_actions':TunableSet(description='\n            Additional selectable away action tones.\n            ',
       tunable=AwayAction.TunableReference(pack_safe=True)), 
     'leave_work_early':TunableReference(description='\n            Sim Info interaction to end work early.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION),
       class_restrictions='CareerLeaveWorkEarlyInteraction'), 
     'stay_late':OptionalTunable(description='\n            If enabled, a Sim Info interaction to extend the work session.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       class_restrictions='CareerStayLateInteraction'))}

    def get_default_action(self, sim_info):
        resolver = SingleSimResolver(sim_info)
        for default_action_info in self.default_action_list:
            default_test = default_action_info.default_action_test
            if default_test is None or default_test.run_tests(resolver):
                return default_action_info.default_action

        logger.error('Failed to find default action for career tone tuning.                       Did you forget to add a default action with no test at                       the end of the list?')


class Career(HasTunableReference, careers.career_base.CareerBase, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.CAREER)):
    HOMEWORK_HELP_MAPPING = TunableMapping(description='\n        Determine how often and how much help a sim receives on their homework.\n        ',
      key_type=TunableEnumEntry(description='\n            The age at which the homework help data applies.\n            ',
      tunable_type=Age,
      default=(Age.CHILD)),
      value_type=TunableTuple(description='\n            The homework help data the defines the eligibility, chance\n            and percent of homework completeness to apply when giving\n            homework help.\n            ',
      eligible_regions=TunableList(description='\n                Regions in which sims who attend school are\n                eligible to get homework help. If none are tuned,\n                all regions are valid.\n                ',
      tunable=TunableRegionDescription(description='\n                    Regions in which children who attend school are\n                    eligible to get homework help. If none are tuned,\n                    all regions are valid.\n                    ',
      pack_safe=True)),
      progress_percentage=TunablePercent(description='\n                The progress percentage that the homework is complete\n                after the student has been given homework help.\n                ',
      default=50),
      base_chance=TunablePercent(description='\n                The tunable chance that the sim receives homework help.\n                ',
      default=50),
      homework_help_notification=TunableUiDialogNotificationSnippet(description='\n                The notification that will show at the end of the day if a sim\n                receives homework help.\n                ')))
    NUM_CAREERS_PER_DAY = sims4.tuning.tunable.Tunable(int, 2, description='\n                                 The number of careers that are randomly selected\n                                 each day to populate career selection for the\n                                 computer and phone.\n                                 ')
    CAREER_TONE_INTERACTION = TunableReference(description='\n        The interaction that applies the tone away action.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)))
    FIND_JOB_PHONE_INTERACTION = sims4.tuning.tunable.TunableReference(description="\n        Find job phone interaction. This will be pushed on a Sim when player\n        presses the Look For Job button on the Sim's career panel.\n        ",
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)))
    REVEAL_SEQUENCE_DIALOG = UiDialogRevealSequence.TunableFactory(description='\n        Display the before and after photos from gig history.\n        ')
    INTERIOR_DECORATOR_CAREER = TunablePackSafeReference(description='                \n        A reference to the gig-career that provides the reveal moment photos.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.CAREER)))
    SWITCH_JOBS_DIALOG = UiDialogOkCancel.TunableFactory(description='\n         If a Sim already has a career and is joining a new one, this dialog\n         asks the player to confirm that they want to quit the existing career.\n         \n         Params passed to Text:\n         {0.SimFirstName} and the like - Sim switching jobs\n         {1.String} - Job title of existing career\n         {2.String} - Career name of existing career\n         {3.String} - Company name of existing career\n         {4.String} - Career name of new career\n         ')
    SWITCH_MANY_JOBS_DIALOG = UiDialogOkCancel.TunableFactory(description='\n         If a Sim already has more than one career and is joining a new one, \n         this dialog asks the player to confirm that they want to quit the existing careers.\n         \n         Params passed to Text:\n         {0.SimFirstName} and the like - Sim switching jobs\n         {1.String} - Job title of existing career\n         {2.String} - Career name of existing career\n         {3.String} - Company name of existing career\n         {4.String} - Career name of new career\n         ')
    UNRETIRE_DIALOG = UiDialogOkCancel.TunableFactory(description='\n         If a Sim is retired and is joining a career, this dialog asks the\n         player to confirm that they want to unretire and lose any retirement\n         benefits.\n         \n         Params passed to Text:\n         {0.SimFirstName} and the like - Sim switching jobs\n         {1.String} - Job title of retired career\n         {2.String} - Career name of retired career\n         {3.String} - Career name of new career\n         ')
    FIRST_TIME_ASSIGNMENT_DIALOG = UiDialogOkCancel.TunableFactory(description='\n         Dialog to offer an immediate assignment to a Sim on accepting a\n         new job. \n         \n         Params passed to Text:\n         {0.SimFirstName} and the like - Sim switching jobs\n         {1.String} - Line separated list of assignment names.\n         ')
    FIRST_TIME_ASSIGNMENT_DIALOG_DELAY = sims4.tuning.tunable.TunableSimMinute(description='\n        The time in Sim Minutes between a Sim accepting\n        a job and getting the first assignment pop-up\n        ',
      default=3.0,
      minimum=0.0)
    FIRST_TIME_DEFERRED_ASSIGNMENT_ADDITIONAL_DELAY = sims4.tuning.tunable.TunableInterval(description='\n        A minimum and maximum time between which an additional delay will be\n        randomly chosen. This delay will be added to the normal first time\n        assignment delay. A different value will be chosen for each occurrence.\n        ',
      tunable_type=(sims4.tuning.tunable.TunableSimMinute),
      default_lower=120,
      default_upper=720,
      minimum=0)
    CAREER_PERFORMANCE_UPDATE_INTERVAL = sims4.tuning.tunable.TunableSimMinute(description="\n        In Sim minutes, how often during a work session the Sim's work\n        performance is updated.\n        ",
      default=30.0,
      minimum=0.0)
    SCHOLARSHIP_INFO_EVENT = TunableEnumEntry(description='\n        The event to register for when waiting for a Scholarship Info Sign to be shown.\n        ',
      tunable_type=TestEvent,
      default=(TestEvent.Invalid))
    WORK_SESSION_PERFORMANCE_CHANGE = TunableReference(description="\n        Used to track a sim's work performance change over a work session.\n        ",
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)))
    BUFFS_LEAVE_WORK = TunableSet(description='\n        The buffs that are applied when sim left work.\n        ',
      tunable=TunableBuffReference(pack_safe=True))
    PART_TIME_CAREER_SHIFT_ICONS = TunableMapping(description='\n        Used to populate icons on the shifts dropdown on Career Selector\n        ',
      key_name='shift_type',
      key_type=TunableEnumEntry(description='Shift Type.', tunable_type=CareerShiftType,
      default=(CareerShiftType.ALL_DAY)),
      value_name='icon',
      value_type=sims4.tuning.tunable.TunableResourceKey(None,
      resource_types=(sims4.resources.CompoundTypes.IMAGE),
      description='The icon to be displayed.'),
      tuple_name='PartTimeShiftTuningTuple',
      export_modes=(ExportModes.All))
    TEXT_INPUT_NEW_NAME = 'new_name'
    TEXT_INPUT_NEW_DESCRIPTION = 'new_description'
    REGISTER_CAREER_DIALOG_DATA = TunableTuple(register_career_dialog=TunableVariant(description='\n            The rename dialog to show when running this interaction.\n            ',
      ok_dialog=UiDialogTextInputOk.TunableFactory(text_inputs=(
     TEXT_INPUT_NEW_NAME, TEXT_INPUT_NEW_DESCRIPTION)),
      ok_cancel_dialog=UiDialogTextInputOkCancel.TunableFactory(text_inputs=(
     TEXT_INPUT_NEW_NAME, TEXT_INPUT_NEW_DESCRIPTION))),
      register_career_rename_title=(OptionalTunable(TunableLocalizedStringFactory(description="\n            If set, this localized string will be used as the interaction's \n            display name if the object has been previously renamed.\n            "))))
    CUSTOM_CAREER_KNOWLEDGE_NOTIFICATION = TunableUiDialogNotificationSnippet(description="\n        The notification to use when one Sim learns about another Sim's\n        career. This is only used when the sim has a custom career. \n        Regular career's notification is found in the career track.\n        ")
    CUSTOM_CAREER_REGISTER_LOOT = LootActions.TunableReference(description='\n        Loot to give when sim registers for custom career. This is not tuned\n        directly on interaction because the sim can leave custom career through\n        code for various reasons. The join loot is applied through code to \n        standardize the flow.\n        ')
    CUSTOM_CAREER_UNREGISTER_LOOT = LootActions.TunableReference(description='\n        Loot to give when sim unregisters custom career. This is not tuned\n        directly on interaction because the sim can leave custom career through\n        code for various reasons. \n        ')
    GIG_PICKER_LOCALIZATION_FORMAT = TunableLocalizedStringFactory(description='\n        String used to format the description in the gig picker.\n        Currently has tokens for name, payout range, audition time, gig time\n        and audition prep recommendation.\n        ')
    GIG_PICKER_SKIPPED_AUDITION_LOCALIZATION_FORMAT = TunableLocalizedStringFactory(description='\n        String used to format the description in the gig picker if audition is \n        skipped. Currently has tokens for name, payout range, gig time and \n        audition prep recommendation.\n        ')
    TRAIT_BASED_CAREER_LEVEL_ENTITLEMENTS = TunableList(description='\n        A list of mappings of traits to CareerLevel references. If a sim has\n        a given trait, the associated CareerLevels will become available\n        in the career selector.\n        ',
      tunable=sims4.tuning.tunable.TunableTuple(trait=sims4.tuning.tunable.TunableReference(description='\n                Trait to test for on the Sim that makes the associated\n                career levels available in the career selector.\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
      pack_safe=True),
      career_entitlements=sims4.tuning.tunable.TunableList(description='\n                The list of CareerLevels.\n                ',
      tunable=sims4.tuning.tunable.TunableReference(description='\n                    A CareerLevel.\n                    ',
      manager=(services.get_instance_manager(sims4.resources.Types.CAREER_LEVEL)),
      pack_safe=True)),
      benefits_description=TunableLocalizedString(description='\n                A description of the benefits granted by the trait to be \n                displayed in the career selector.\n                ')))
    INSTANCE_TUNABLES = {'career_category':TunableEnumEntry(description='\n            Category for career, this will be used for aspirations and other\n            systems which should trigger for careers categories but not for\n            others.\n            ',
       tunable_type=CareerCategory,
       default=CareerCategory.Invalid,
       export_modes=ExportModes.All), 
     'career_panel_type':TunableEnumEntry(description='\n            Type of panel that UI should use for this career.\n            ',
       tunable_type=CareerPanelType,
       default=CareerPanelType.NORMAL_CAREER,
       export_modes=ExportModes.All,
       tuning_group=GroupNames.UI), 
     'career_story_progression':CareerStoryProgressionParameters.TunableFactory(description='\n            Define how Story Progression handles this specific career.\n            '), 
     'career_location':TunableCareerLocationVariant(description='\n            Define where Sims go to work.\n            ',
       tuning_group=GroupNames.UI), 
     'start_track':sims4.tuning.tunable.TunableReference(description='\n            This is the career track that a Sim would start when joining\n            this career for the first time. Career Tracks contain a series of\n            levels you need to progress through to finish it. Career tracks can branch at the end\n            of a track, to multiple different tracks which is tuned within\n            the career track tuning.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CAREER_TRACK),
       export_modes=sims4.tuning.tunable_base.ExportModes.All), 
     'career_affordance':sims4.tuning.tunable.TunableReference(manager=services.get_instance_manager(sims4.resources.Types.INTERACTION),
       description='SI to push to go to work.'), 
     'go_home_to_work_affordance':TunableReference(description='\n            Interaction pushed onto a Sim to go home and start work from there\n            if they are not on their home lot.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION)), 
     'career_rabbit_hole':TunablePackSafeReference(description='\n            Rabbit hole to put sim in when they are at work.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.RABBIT_HOLE),
       class_restrictions=('CareerRabbitHole', )), 
     'tested_affordances':TunableList(description="\n            A list of test sets to run to choose the affordance to go work. If \n            an affordance is found from this list, it will be pushed onto the \n            Sim.\n            \n            If no affordance is found from this list that pass the tests, \n            normal work affordance behavior will take over, running \n            'career_affordance' if at home or 'go_home_to_work_affordance' if \n            not at home.\n            ",
       tunable=TunableTuple(tests=TunableTestSet(description='\n                    A set of tests that if passed will make this the affordance\n                    that is run to send the Sim to work.\n                    '),
       affordance=TunableReference(description='\n                    The career affordance for this test set. \n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))))), 
     'levels_lost_on_leave':sims4.tuning.tunable.Tunable(description='\n            When you leave this career for any reason you will immediately lose\n            this many levels, for rejoining the career. i.e. if you quit your\n            job at level 8, and then rejoined with this value set to 1, you\n            would rejoin the career at level 7.\n            ',
       tunable_type=int,
       default=1), 
     'days_to_level_loss':sims4.tuning.tunable.Tunable(description='\n            When you leave a career, we store off the level you would rejoin the\n            career at. Every days_to_level_loss days you will lose another level.\n            i.e. I quit my job at level 8. I get reduced "level 7 right away\n            because of levels_lost_on_leave. Then with days_to_level_loss set to\n            3, in 3 days I would goto level 6, in 6 days level 5, etc...\n            ',
       tunable_type=int,
       default=1), 
     'start_level_modifiers':TestedSum.TunableFactory(description='\n            A tunable list of test sets and associated values to apply to the\n            starting level of this Sim.\n            '), 
     'promotion_buff':OptionalTunable(description='\n            The buff to trigger when this Sim is promoted in this career.',
       tunable=TunableBuffReference()), 
     'demotion_buff':OptionalTunable(description='\n            The buff to trigger when this Sim is demoted in this career.',
       tunable=TunableBuffReference()), 
     'fired_buff':OptionalTunable(description='\n            The buff to trigger when this Sim is fired from this career.',
       tunable=TunableBuffReference()), 
     'early_promotion_modifiers':TunableMultiplier.TunableFactory(description='\n            A tunable list of test sets and associated multipliers to apply to \n            the moment of promotion. A resulting modifier multiplier of 0.10 means that promotion \n            could happen up to 10% earlier. A value less than 0 has no effect.\n            '), 
     'early_promotion_chance':TunableMultiplier.TunableFactory(description='\n            A tunable list of test sets and associated multipliers to apply to the percentage chance, \n            should the early promotion modifier deem that early promotion is possible,\n            that a Sim is in fact given a promotion. A resolved value of 0.10 will result in a 10%\n            chance.\n            '), 
     'demotion_chance_modifiers':TunableMultiplier.TunableFactory(description="\n            A tunable list of test sets and associated multipliers to apply to \n            the moment of a Sim's demotion, to provide the chance that Sim will get demoted. A resultant\n            modifier value of 0.50 means at the point of work end where performance would require demotion,\n            the Sim would have a 50% chance of being demoted. Any resultant value over 1 will result in demotion.\n            "), 
     'block_promotion_tests':TunableTestSet(description='\n            A set of tests that if passed will block career promotions. Resolver is a SingleSimResolver \n            specific to the sim in the career. Promotions are evaluated EOD, if a sim should be promoted \n            but is blocked, then they will be promoted on next EOD after they are no longer blocked.\n            '), 
     'scholarship_info_loot':OptionalTunable(description='\n            If enabled, this loot will run at the beginning of the career si.\n            ',
       tunable=LootActions.TunablePackSafeReference(description='\n                Loot to trigger at the beginning of the career\n                ',
       allow_none=True)), 
     'career_messages':TunableTuple(join_career_notification=OptionalTunable(description='\n                If tuned, we will show a message when a sim joins this career.\n                If not tuned, no message will be shown.\n                ',
       tunable=_get_career_notification_tunable_factory(description='\n                    Message when a Sim joins a new career.\n                    '),
       enabled_by_default=True),
       quit_career_notification=_get_career_notification_tunable_factory(description='\n                Message when a Sim quits a career.\n                '),
       lay_off_career_notification=_get_career_notification_tunable_factory(description='\n                Message when a Sim is laid off from a career.\n                '),
       fire_career_notification=_get_career_notification_tunable_factory(description='\n                Message when a Sim is fired from a career.\n                '),
       promote_career_notification=_get_career_notification_tunable_factory(description='\n                Message when a Sim is promoted in their career.\n                '),
       promote_career_rewardless_notification=_get_career_notification_tunable_factory(description="\n                Message when a Sim is promoted in their career and there are no\n                promotion rewards, either because there are none tuned or Sim\n                was demoted from this level in the past and so shouldn't get\n                rewards again.\n                "),
       demote_career_notification=_get_career_notification_tunable_factory(description='\n                Message when a Sim is demoted in their career.\n                '),
       career_daily_start_notification=_get_career_notification_tunable_factory(description='\n                Message on notification when sim starts his work day\n                '),
       career_daily_end_notification=TunableTestedVariant(description='\n                Message on notification when sim ends his work day\n                ',
       tunable_type=(_get_career_notification_tunable_factory()),
       locked_args={'no_notification': None}),
       career_event_confirmation_dialog=UiDialogOkCancel.TunableFactory(description='\n                 At the beginning of a work day, if the career has available events and\n                 a single Sim is eligible to do an event (or the career only supports single sim events),\n                 this dialog is shown. If player accepts, the Sim is sent to the career\n                 event (e.g. hospital, police station, etc.). If player declines, the Sim \n                 goes to rabbit hole to work.\n                 \n                 Params passed to Text:\n                 {0.SimFirstName} and the like - Sim in career\n                 {1.String} - Job title\n                 {2.String} - Career name\n                 {3.String} - Company name\n                 '),
       career_event_multi_sim_confirmation_dialog=OptionalTunable(description='\n                Sim picker dialog for multi sim active careers\n                Multi sim active careers should have this enabled.\n                ',
       tunable=UiDialogOkCancel.TunableFactory(description='\n                     At the beginning of a work day, if the career has available events and\n                     multiple Sims are eligible to do an event, (in a career that supports multi\n                     sim events), this dialog is shown. If player accepts, a picker will allow\n                     the player to choose which sims to follow to the career event (e.g. \n                     hospital, police station, etc.). Any sim not chosen goes rabbitholes\n                     to work.\n                     \n                     Params passed to Text:\n                     {0.SimFirstName} and the like - Sim in career\n                     {1.String} - Job title\n                     {2.String} - Career name\n                     {3.String} - Company name\n                     ')),
       career_event_multi_sim_picker_dialog=OptionalTunable(description='\n                Sim picker dialog for multi sim active careers\n                Multi sim active careers should have this enabled.\n                ',
       tunable=TunablePickerDialogVariant(description='\n                    sim picker dialog for multi sim career events.\n                    ',
       available_picker_flags=(ObjectPickerTuningFlags.SIM))),
       career_time_off_messages=TunableMapping(description='\n                Mapping of time off reason to the messages displayed for that reason\n                ',
       key_type=(TunableEnumEntry(career_ops.CareerTimeOffReason, career_ops.CareerTimeOffReason.NO_TIME_OFF)),
       value_type=TunableTuple(text=TunableLocalizedStringFactory(description='\n                        Localization String for the text displayed on the panel when\n                        taking time off for the specified reason.\n                        \n                        First token: sim info\n                        Second token: PTO days remaining.\n                        ',
       allow_none=True),
       tooltip=TunableLocalizedStringFactory(description='\n                        Localization String for the tooltip displayed when\n                        taking time off for the specified reason\n                        \n                        First token: sim info\n                        Second token: PTO days remaining.\n                        ',
       allow_none=True),
       day_end_notification=OptionalTunable(description='\n                        If enabled, the notification that will be sent when the\n                        Sim ends his day of PTO.\n                        ',
       tunable=TunableTestedVariant(description='\n                            Message on notification when sim ends his day of PTO\n                            ',
       tunable_type=(_get_career_notification_tunable_factory()))))),
       career_early_warning_notification=_get_career_notification_tunable_factory(description='\n                Message warning the Sim will need to leave for work soon.\n                '),
       career_early_warning_time=Tunable(description='\n                How many hours before a the Sim needs to go to work to show\n                the Career Early Warning Notification. If this is <= 0, the\n                notification will not be shown.\n                ',
       tunable_type=float,
       default=1),
       career_early_warning_alarm=OptionalTunable(description='\n                If enabled, provides options to the player to go to work,\n                work from home, or take pto. \n                \n                {0.SimFirstName} Sim in career\n                {1.String} - Career level title\n                {2.String} - Career name\n                {3.String} - Company name\n                ',
       tunable=TunableTuple(dialog=UiDialog.TunableFactory(description="\n                        Dialog that's shown. Okay is confirming leaving the\n                        situation, cancel is to miss work and stay in the\n                        situation.\n                        ",
       locked_args={'phone_ring_type': PhoneRingType.ALARM}),
       go_to_work_text=sims4.localization.TunableLocalizedStringFactory(description='\n                        Button text for choosing to go to work.\n                        '),
       work_from_home_text=sims4.localization.TunableLocalizedStringFactory(description='\n                        If the Sim has career assignments to offer, a button with\n                        this text will show up.\n                        '),
       take_pto_text=sims4.localization.TunableLocalizedStringFactory(description='\n                        If the Sim has enough PTO, a button with this text will\n                        show up.\n                        '),
       call_in_sick_text=sims4.localization.TunableLocalizedStringFactory(description='\n                        If the Sim does not have enough PTO, a button with this\n                        text will show up.\n                        ')),
       enabled_by_default=True),
       career_missing_work=OptionalTunable(description='\n                If enabled, being late for work will trigger the missing work flow\n                ',
       tunable=TunableTuple(description='\n                    Tuning for triggering the missing work flow.\n                    ',
       dialog=UiDialogOk.TunableFactory(description='\n                        The dialog that will be triggered when the sim misses work.\n                        '),
       affordance=sims4.tuning.tunable.TunableReference(description='\n                        The affordance that is pushed onto the sim when the modal\n                        dialog completes.\n                        ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
       loot=sims4.tuning.tunable.TunableList(description='\n                        Loots that are applied when the modal dialog completes.\n                        ',
       tunable=LootActions.TunableReference(pack_safe=True))),
       enabled_by_default=True),
       career_performance_warning=TunableTuple(description='\n                Tuning for triggering the career performance warning flow.\n                ',
       dialog=UiDialogOk.TunableFactory(description='\n                    The dialog that will be triggered when when the sim falls\n                    below their performance threshold.\n                    '),
       threshold=TunableThreshold(description='\n                    The threshold that the performance stat value will be\n                    compared to.  If the threshold returns true then the\n                    performance warning notification will be triggered.\n                    \n                    '),
       affordance=sims4.tuning.tunable.TunableReference(description='\n                    The affordance that is pushed onto the sim when the accepts\n                    the modal dialog.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)))),
       pto_gained_text=sims4.localization.TunableLocalizedStringFactory(description='\n                Text passed to daily end notifications when additional day of \n                PTO is earned.\n                        \n                First token: sim info\n                ',
       allow_none=True),
       overmax_rewardless_notification=_get_career_notification_tunable_factory(description='\n                The notification to display when a Sim reaches an overmax level.\n                The following tokens are provided:\n                 * 0: The Sim owner of the career\n                 * 1: The level name (e.g. Chef)\n                 * 2: The career name (e.g. Culinary)\n                 * 3: The company name (e.g. Maids United)\n                 * 4: The overmax level\n                 * 5: The new salary\n                 * 6: The salary increase\n                '),
       overmax_notification=_get_career_notification_tunable_factory(description='\n                The notification to display when a Sim reaches an overmax level.\n                The following tokens are provided:\n                 * 0: The Sim owner of the career\n                 * 1: The level name (e.g. Chef)\n                 * 2: The career name (e.g. Culinary)\n                 * 3: The company name (e.g. Maids United)\n                 * 4: The overmax level\n                 * 5: The new salary\n                 * 6: The salary increase\n                 * 7: The rewards, in the form of a string\n                '),
       situation_leave_confirmation=TunableTuple(description='\n                If a playable Sim is in a situation with a job with Confirm\n                Leave Situation For Work set, this dialog will be shown to the\n                player with the options of leaving the situation for work,\n                staying in situation and let Sim miss work, or stay in\n                situation and Sim take PTO.\n                \n                {0.SimFirstName} and the like - Sim in career\n                {1.String} - Job title\n                {2.String} - Career name\n                {3.String} - Company name\n                ',
       dialog=UiDialogOkCancel.TunableFactory(description="\n                    Dialog that's shown. Okay is confirming leaving the situation,\n                    cancel is to miss work and stay in the situation.\n                    "),
       take_pto_button_text=sims4.localization.TunableLocalizedStringFactory(description='\n                    If the Sim has enough PTO, a button with this text will show up.\n                    ')),
       career_event_end_warning=OptionalTunable(description='\n                If enabled, a notification will be displayed if time left is \n                more than time tuned. \n                If disabled, no notification will be displayed.\n                ',
       tunable=TunableTuple(description="\n                    Tuning for a notification warning the player that their Sim's\n                    active career event is about to end.\n                    ",
       notification=_get_career_notification_tunable_factory(description='\n                        Notification warning work day is going to end.\n    \n                         Params passed to Text:\n                         {0.SimFirstName} and the like - Sim in career\n                         {1.String} - Job title\n                         {2.String} - Career name\n                         {3.String} - Company name\n                        '),
       time=TunableSimMinute(description='\n                        How many Sim minutes prior to the end to show notification.\n                        ',
       default=60,
       minimum=0))),
       career_assignment_summary_notification=TunableTestedVariant(description='\n                Message on notification when day starts after having assignment(s).\n                ',
       tunable_type=(_get_career_notification_tunable_factory()),
       locked_args={'no_notification': None}),
       tuning_group=GroupNames.UI), 
     'can_be_fired':Tunable(description='\n            Whether or not the Sim can be fired from this career.  For example,\n            children cannot be fired from school.\n            ',
       tunable_type=bool,
       default=True), 
     'quittable_data':OptionalTunable(description='\n            Whether or not Sims can quit this career.\n            e.g.: Children/Teens cannot quit School.\n            \n            If the career is quittable, specify tuning directly related to\n            quitting, e.g. the confirmation dialog.\n            ',
       tunable=TunableTuple(tested_quit_dialog=OptionalTunable(description='\n                    If enabled and the tuned tests pass, instead of showing the default\n                    quit dialog the tested quit dialog will be displayed.\n                    \n                    Example: If a Sim has a scholarship (EP8) that depends on\n                    staying in the career, a tested quit dialog can be tuned to\n                    include a warning in its dialog text.\n                    ',
       tunable=TunableList(description='\n                        A tunable list of dialog-test pairs. The first test-dependent-quit-dialog to pass will have its \n                        corresponding dialog used. If none pass, then the default quit-dialog will show.\n                        ',
       tunable=TunableTuple(description='\n                            A tuple containing a quit dialog and the test set that must pass to use\n                            specified dialog. \n                            ',
       quit_dialog=UiDialogOkCancel.TunableFactory(description='\n                                This dialog asks the player to confirm that they want to\n                                quit.\n                                '),
       test_set=event_testing.tests.TunableTestSet(description='\n                                If the tests pass, the test-dependent-quit-dialog will\n                                show.\n                                ')))),
       quit_dialog=UiDialogOkCancel.TunableFactory(description='\n                    This dialog asks the player to confirm that they want to\n                    quit.\n                    ')),
       enabled_by_default=True,
       enabled_name='Can_Quit',
       disabled_name='Cannot_Quit'), 
     'career_availablity_tests':event_testing.tests.TunableTestSet(description='\n            When a Sim calls to join a Career, this test set determines if a \n            particular career can be available to that Sim at all. This test\n            set determines if a Career is visible in the Career Panel.\n            '), 
     'career_selectable_tests':event_testing.tests.TunableTestSetWithTooltip(description='\n            Test set that determines if a career that is available to a Sim\n            is valid or not. This test set determines if a Career is selectable\n            in the Career Panel.\n            '), 
     'show_career_in_join_career_picker':Tunable(description='\n            If checked, this career will be visible in the join career picker\n            window. If not checked, it will not be.\n            ',
       tunable_type=bool,
       default=True,
       tuning_group=GroupNames.UI), 
     'initial_pto':sims4.tuning.tunable.Tunable(description='\n            Initial amount of PTO earned when joining the career\n            ',
       tunable_type=float,
       default=0), 
     'disable_pto':Tunable(description='\n            If checked, will disable PTO references in the UI. This option is\n            incompatible with setting any pto tuning in the carrer or career \n            levels to non-default values.\n            ',
       default=False,
       tunable_type=bool,
       tuning_group=GroupNames.UI), 
     'initial_delay':TunableSimMinute(description='\n            The amount of time a Sim is exempt from going to work after being\n            hired. Their first work day will be at least this much into the\n            future.\n            ',
       default=480.0,
       minimum=0.0), 
     'active_career_type':TunableEnumEntry(description='\n            Whether this career is an active career type. Active careers appear\n            in a separate tab in the Join Career dialog, and multi-sim active \n            careers will have behavior that allows multiple sims to travel to \n            the same career.\n            ',
       tunable_type=ActiveCareerType,
       default=ActiveCareerType.NON_ACTIVE), 
     'allow_active_offlot':Tunable(description='\n            If checked, will allow travelling to active career even if sim\n            is off lot.\n            ',
       default=False,
       tunable_type=bool), 
     'career_events':TunableList(description='\n             A list of available career events.\n             ',
       tunable=sims4.tuning.tunable.TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.CAREER_EVENT)),
       pack_safe=True)), 
     'career_event_decline_option':TunableEnumEntry(description='\n             Select what will happen if the player chooses to decline the career event\n             confirmation dialog.\n             ',
       tunable_type=CareerEventDeclineOptions,
       default=CareerEventDeclineOptions.CAREER_RABBITHOLE), 
     'hire_agent_interaction':OptionalTunable(tunable=TunableReference(description='\n                The interaction to push a sim to hire an agent.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
       tuning_group=GroupNames.GIG,
       export_modes=(
      ExportModes.ClientBinary,)), 
     'find_audition_interaction':OptionalTunable(tunable=TunableReference(description='\n                The interaction to push a sim to look for an audition.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
       tuning_group=GroupNames.GIG,
       export_modes=(
      ExportModes.ClientBinary,)), 
     'cancel_audition_interaction':OptionalTunable(tunable=TunableReference(description='\n                The interaction to push on a sim who cancels an audition.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
       tuning_group=GroupNames.GIG,
       export_modes=(
      ExportModes.ClientBinary,)), 
     'cancel_gig_interaction':OptionalTunable(tunable=TunableReference(description='\n                The interaction to push on a sim to cancel a gig.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
       tuning_group=GroupNames.GIG,
       export_modes=(
      ExportModes.ClientBinary,)), 
     'call_costar_interaction':OptionalTunable(tunable=TunableReference(description='\n                The interaction to push a sim to call up their costars. This is added\n                for gigs.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
       tuning_group=GroupNames.GIG,
       export_modes=(
      ExportModes.ClientBinary,)), 
     'invite_over':OptionalTunable(description='\n            Tuning that provides a tunable chance for the Sim in this career\n            inviting over someone at the end of the work/school day. For\n            example, a child Sim can invite over a classmate after school,\n            or an adult can invite over a co-worker after their shift ends.\n            \n            Invite overs will only occur if the player is on the home lot.\n            ',
       tunable=TunableTuple(chance=SuccessChance.TunableFactory(description='\n                    Chance of inviting over a Sim after work/school.\n                    '),
       confirmation_dialog=UiDialogOkCancel.TunableFactory(description='\n                    Dialog offered to player to confirm inviting over someone.\n    \n                    Localization Tokens:\n                    0: Sim in career.\n                    1: Sim being invited over.\n                    '),
       sim_filter=TunableSimFilter.TunableReference(description='\n                    Sim filter specifying who to invite over.\n                    '),
       purpose=TunableEnumEntry(description='\n                    The purpose for the invite over. This will determine the\n                    behavior of the invited over Sim, as tuned in Venue -> Npc\n                    Summoning Behavior.\n                    ',
       tunable_type=NPCSummoningPurpose,
       default=(NPCSummoningPurpose.DEFAULT)))), 
     'available_for_club_criteria':Tunable(description='\n            If enabled, this career type will be available for selection when\n            creating Club Criteria. If disabled, it will not be available.\n            ',
       tunable_type=bool,
       default=False), 
     'has_coworkers':Tunable(description='\n            If checked, other Sims in this career are considered coworkers. If\n            unchecked, they are not.\n            \n            e.g.\n             * Sims in High School might should not be considered coworkers.\n            ',
       tunable_type=bool,
       default=True), 
     'display_career_info':Tunable(description='\n            If checked, the full set of career messages are displayed for this\n            career. This includes notifications when the career is joined as\n            well as performance evaluation results.\n            \n            If unchecked, those two sets of data are not made visible to the\n            player, e.g. for school career.\n            ',
       tunable_type=bool,
       default=True), 
     'is_school_career':Tunable(description='\n            If checked, the career will test into special behavior and treated\n            as school for children or teens.\n            \n            If unchecked, this is a professional career.\n            \n            Used to branch behavior at the end of the day for re-setting the career\n            performance statistics for childreen/teens so they may receive\n            homework help.\n            ',
       tunable_type=bool,
       default=False), 
     'aspirations_to_activate':TunableList(description="\n            A list of aspirations we want to activate while the Sim is in this\n            career. This saves from having to track them when the Sim is not in\n            the career.\n            \n            Note: You don't need to tune Aspirations that the Career Level\n            references directly. But if those aspirations rely on others, then\n            they need to be tuned here.\n            ",
       tunable=sims4.tuning.tunable.TunableReference(description='\n                A Career Aspiration that we want to activate when the Sim is in\n                this career.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.ASPIRATION)),
       class_restrictions='AspirationCareer'),
       unique_entries=True), 
     'show_ideal_mood':Tunable(description="\n            If checked, displays the current career track's ideal mood in the UI.\n            Does not change whether the ideal mood affects the career performance.\n            ",
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.UI,
       export_modes=ExportModes.All), 
     'is_visible_career':Tunable(description='\n            If checked, this will be considered a professional career.  If \n            unchecked, any career tests that check for a visible, \n            professional career will not take this career into account.  In \n            addition, any unchecked career will not be affected by any Career \n            Loot Ops (because it is invisible).\n            ',
       tunable_type=bool,
       default=True), 
     'early_work_loot':OptionalTunable(description='\n            If enabled, this loot will be applied to the Sim prior to going to\n            work.\n            ',
       tunable=LootActions.TunablePackSafeReference(description='\n                Loot to apply to the Sim prior to going to work.\n                ',
       allow_none=True)), 
     'preferred_region':OptionalTunable(description='\n            If enabled, allows tuning a Region that will prefer this Career. \n            Currently, that means the Career will be at the top of the Career \n            Panel while in this Region and at the bottom when not.\n            ',
       tunable=TunableRegionDescription(description='\n                The Region that should prefer this Career.\n                '),
       disabled_name='no_preferred_region',
       enabled_name='preferred_region',
       disabled_value=0,
       tuning_group=GroupNames.UI), 
     'reputation_stat':OptionalTunable(description='\n            If enabled, creates statistic used to track professional reputation for this career.\n            ',
       tunable=sims4.tuning.tunable.TunableReference(description='\n                Statistic used to track professional reputation for this career.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC))),
       export_modes=sims4.tuning.tunable_base.ExportModes.All), 
     'build_buy_info':OptionalTunable(description="\n            If enabled, allows tuning data that will be used in the Gig Info panel\n            in build buy. Currently, this is only used for the Decorator Gig when\n            the player is on the client's lot.\n            ",
       tunable=TunableTuple(description='\n                A collection of data used for the Gig Info panel in Build Buy.\n                ',
       help_text=TunableLocalizedString(description='\n                   This is the text shown when the player hovers over the question\n                   mark icon in the header.\n                   '),
       payout_label=TunableLocalizedString(description='\n                    The payout label in the panel. Right now, this will always be\n                    the label above the payout for the current Decorator Gig.\n                    '),
       budget_label=TunableLocalizedString(description="\n                    The budget label in the panel. Right now, this will\n                    always be the label above the client's budget.\n                    "),
       over_budget_label=TunableLocalizedString(description='\n                    The budget label in the panel if the player goes over budget.\n                    '),
       wallet_tooltip_budget_label=TunableLocalizedString(description='\n                    The budget label in the Simoleon Wallet tooltip.\n                    '),
       wallet_tooltip_over_budget_label=TunableLocalizedString(description='\n                    The budget label in the Simoleon Wallet Tooltip if the player\n                    goes over budget.\n                    '),
       export_class_name='CareerBuildBuyInfo'),
       tuning_group=GroupNames.UI,
       export_modes=ExportModes.ClientBinary), 
     'current_gig_limit':TunableRange(description='\n            The maximum number of concurrent, active gigs that this career allows for\n            each Sim.\n            ',
       tunable_type=int,
       default=1,
       minimum=0), 
     'career_display_name_override':OptionalTunable(description='\n            If enabled, this will override the Career name in the Career Panel in the \n            UI.  This should be used for Careers that allow multiple active gigs, as \n            each gig will be appear as its own "career" in the Career Panel.  This will \n            use a number token.\n            Ex: Quest #{0.Number}\n            ',
       tunable=TunableLocalizedStringFactory(description='\n                The text we want to use to override the title bar in for this career\n                in the Career Panel.\n                '),
       tuning_group=GroupNames.UI), 
     'icon_override_picker_interaction':OptionalTunable(description='\n            Interaction that shows Career Icon override picker. \n            ',
       tunable=TunableReference(description='\n                Player can choose an icon override for this career.\n                The chosen icon will show as a secondary icon in TNS\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
       tuning_group=GroupNames.UI), 
     'whim_set':OptionalTunable(description='\n            If enabled, this career will offer a whim set to any sim\n            that is in this career.\n            ',
       tunable=TunableReference(description='\n                A whim set that is active when this career is active.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.ASPIRATION)),
       class_restrictions=('ObjectivelessWhimSet', )))}
    _days_worked_statistic_type = None
    _active_days_worked_statistic_type = None

    @classmethod
    def _verify_tuning_callback(cls):
        if cls.disable_pto:
            if cls.initial_pto > 0:
                logger.error('Career: {} has disable PTO set but has initial PTO', cls)
            for career_level in cls.start_track.career_levels:
                if career_level.pto_per_day != 0:
                    logger.error('Career: {} has disable PTO set but has nonzero PTO gain in career level {} (zero indexed)', cls, career_level.level)

        else:
            if cls.available_for_club_criteria:
                start_track = cls.start_track
                if start_track.career_name._string_id == start_track.career_name_gender_neutral.hash:
                    logger.error('Career {} has the same string tuned for its display name and its gender-neutral display name. These must be different strings for localization.', start_track,
                      owner='BadTuning')
            for reason in career_ops.CareerTimeOffReason:
                if reason == career_ops.CareerTimeOffReason.NO_TIME_OFF:
                    continue
                if reason not in cls.career_messages.career_time_off_messages:
                    logger.error('Career: {} is missing career.career time off messages for reason: {}', cls, reason)

            if cls.is_multi_sim_active:
                if cls.career_messages.career_event_multi_sim_confirmation_dialog is None:
                    logger.error('Multi sim active career {} has no career_messages.career_event_multi_sim_confirmation_dialog tuned', cls)
                if cls.career_messages.career_event_multi_sim_picker_dialog is None:
                    logger.error('Multi sim active career {} has no career_messages.career_event_multi_sim_picker_dialog tuned', cls)

    @classmethod
    def _tuning_loaded_callback(cls):
        cls._create_runtime_commodities()
        cls._propagate_track_and_level_data()

    @classmethod
    def _create_runtime_commodities(cls):
        temp_commodity = RuntimeCommodity.generate(cls.__name__)
        temp_commodity.decay_rate = 0
        temp_commodity.convergence_value = 0
        temp_commodity.remove_on_convergence = False
        temp_commodity.visible = False
        temp_commodity.max_value_tuning = 99
        temp_commodity.min_value_tuning = 0
        temp_commodity.initial_value = cls.initial_pto
        temp_commodity.add_if_not_in_tracker = True
        temp_commodity._time_passage_fixup_type = CommodityTimePassageFixupType.FIXUP_USING_TIME_ELAPSED
        cls._pto_commodity = temp_commodity
        if cls._days_worked_statistic_type is None:
            cls._days_worked_statistic_type = RuntimeStatistic.generate(cls.__name__ + '_DaysWorked')
            cls._active_days_worked_statistic_type = RuntimeStatistic.generate(cls.__name__ + '_ActiveDaysWorked')
            cls.max_value_tuning = MAX_UINT64

    @classmethod
    def _propagate_track_and_level_data(cls):
        tracks = []
        tracks.append((cls.start_track, 1))
        while tracks:
            track, starting_user_level = tracks.pop()
            for index, career_level in enumerate(track.career_levels):
                if career_level.track is not None:
                    logger.assert_log('Invalid tuning. {} is in multiple career tracks: {}, {}', career_level.__name__, career_level.track.__name__, cls.__name__)
                career_level.career = cls
                career_level.track = track
                career_level.level = index
                career_level.user_level = index + starting_user_level

            branch_user_level = len(track.career_levels) + starting_user_level
            for branch in track.branches:
                if branch.parent_track is not None:
                    logger.error('Invalid tuning. {} has multiple parent tracks: {}, {}', branch.__name__, branch.parent_track.__name__, track.__name__)
                branch.parent_track = track
                tracks.append((branch, branch_user_level))

    @classmethod
    @cached
    def get_max_user_level--- This code section failed: ---

 L.1440         0  LOAD_CONST               0
                2  STORE_FAST               'max_user_level'

 L.1441         4  LOAD_FAST                'cls'
                6  LOAD_ATTR                start_track
                8  LOAD_CONST               0
               10  BUILD_TUPLE_2         2 
               12  BUILD_LIST_1          1 
               14  STORE_FAST               'stack'

 L.1443        16  SETUP_LOOP          100  'to 100'
               18  LOAD_FAST                'stack'
               20  POP_JUMP_IF_FALSE    98  'to 98'

 L.1444        22  LOAD_FAST                'stack'
               24  LOAD_METHOD              pop
               26  CALL_METHOD_0         0  '0 positional arguments'
               28  UNPACK_SEQUENCE_2     2 
               30  STORE_FAST               'track'
               32  STORE_FAST               'level'

 L.1445        34  LOAD_FAST                'level'
               36  LOAD_GLOBAL              len
               38  LOAD_FAST                'track'
               40  LOAD_ATTR                career_levels
               42  CALL_FUNCTION_1       1  '1 positional argument'
               44  INPLACE_ADD      
               46  STORE_FAST               'level'

 L.1447        48  LOAD_FAST                'track'
               50  LOAD_ATTR                branches
               52  POP_JUMP_IF_FALSE    86  'to 86'

 L.1448        54  SETUP_LOOP           96  'to 96'
               56  LOAD_FAST                'track'
               58  LOAD_ATTR                branches
               60  GET_ITER         
               62  FOR_ITER             82  'to 82'
               64  STORE_FAST               'branch'

 L.1449        66  LOAD_FAST                'stack'
               68  LOAD_METHOD              append
               70  LOAD_FAST                'branch'
               72  LOAD_FAST                'level'
               74  BUILD_TUPLE_2         2 
               76  CALL_METHOD_1         1  '1 positional argument'
               78  POP_TOP          
               80  JUMP_BACK            62  'to 62'
               82  POP_BLOCK        
               84  JUMP_BACK            18  'to 18'
             86_0  COME_FROM            52  '52'

 L.1451        86  LOAD_GLOBAL              max
               88  LOAD_FAST                'max_user_level'
               90  LOAD_FAST                'level'
               92  CALL_FUNCTION_2       2  '2 positional arguments'
               94  STORE_FAST               'max_user_level'
             96_0  COME_FROM_LOOP       54  '54'
               96  JUMP_BACK            18  'to 18'
             98_0  COME_FROM            20  '20'
               98  POP_BLOCK        
            100_0  COME_FROM_LOOP       16  '16'

 L.1453       100  LOAD_FAST                'max_user_level'
              102  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM' instruction at offset 98_0

    @classproperty
    def allow_multiple_careers(cls):
        return False

    @classproperty
    def pto_commodity(cls):
        return cls._pto_commodity

    @classproperty
    def can_quit(cls):
        return cls.quittable_data is not None

    @classproperty
    def is_active(cls):
        return cls.active_career_type != ActiveCareerType.NON_ACTIVE and bool(cls.career_events)

    @classproperty
    def is_multi_sim_active(cls):
        return cls.active_career_type == ActiveCareerType.MULTI_SIM_ACTIVE and bool(cls.career_events)

    @staticmethod
    def _append_career_info_pb(msg, sim_info, career, current_track, new_level, benefit_description=None, selectable=True, not_selectable_tooltip=None):
        if current_track is not None:
            career_track = current_track
        else:
            if career.start_track is not None:
                career_track = career.start_track
            else:
                logger.error('Career {} is unjoinable because it is missing Start Track tuning.', career)
                return
        if new_level < 0 or new_level >= len(career_track.career_levels):
            logger.error('Career {} has an invalid index for career level: new_level={}.', career, new_level)
            return
        career_level = career_track.career_levels[new_level]
        career_info_msg = msg.career_choices.add()
        career_info_msg.uid = career.guid64
        career_info_msg.career_track = career_track.guid64
        career_info_msg.career_level = new_level
        career_info_msg.is_active = career.is_active
        if benefit_description is not None:
            career_info_msg.benefit_description = benefit_description
        if not selectable:
            if not_selectable_tooltip is not None:
                career_info_msg.not_selectable_tooltip = not_selectable_tooltip
        career_info_msg.is_selectable = selectable
        career_info_msg.hourly_pay = career.get_hourly_pay(sim_info=sim_info, career_track=career_track,
          career_level=(career_level.level),
          overmax_level=0)
        work_schedule = get_career_schedule_for_level(career_level)
        if work_schedule is not None:
            work_schedule.populate_scheduler_msg(career_info_msg.work_schedule)

    @staticmethod
    def get_join_career_pb(sim_info, num_careers_to_show=0, default_career_selection_data=None):
        msg = protocolbuffers.Sims_pb2.CareerSelectionUI()
        msg.sim_id = sim_info.sim_id
        msg.is_branch_select = False
        msg.reason = career_ops.CareerOps.JOIN_CAREER
        current_shift = CareerShiftType.ALL_DAY
        for sim_career_id in sim_info.career_tracker.careers:
            sim_career = sim_info.career_tracker.get_career_by_uid(sim_career_id)
            if sim_career.schedule_shift_type != CareerShiftType.ALL_DAY:
                current_shift = sim_career.schedule_shift_type
                break

        msg.current_shift = current_shift
        if default_career_selection_data is not None:
            msg.default_career_select_uid = default_career_selection_data.default_career_select
            msg.career_selector_type = default_career_selection_data.career_selector_type
        all_possible_careers = services.get_career_service().get_shuffled_career_list()
        career_tracks_added = []
        career_tracks_to_skip = []
        for entitlement in Career.TRAIT_BASED_CAREER_LEVEL_ENTITLEMENTS:
            if sim_info.trait_tracker.has_trait(entitlement.trait):
                for career_level in entitlement.career_entitlements:
                    test_result = career_level.career.is_career_available(sim_info=sim_info, from_join=True)
                    if test_result and sim_info.career_tracker.get_career_by_uid(career_level.career.guid64) is None:
                        if career_level.track not in career_tracks_added:
                            selectable_test_result = career_level.career.is_career_selectable(sim_info=sim_info)
                            not_selectable_tooltip = None
                            if not selectable_test_result.result:
                                if selectable_test_result.tooltip is not None:
                                    not_selectable_tooltip = selectable_test_result.tooltip()
                            Career._append_career_info_pb(msg, sim_info,
                              (career_level.career),
                              (career_level.track),
                              (career_level.level),
                              benefit_description=(entitlement.benefits_description),
                              selectable=(selectable_test_result.result),
                              not_selectable_tooltip=not_selectable_tooltip)
                            career_tracks_added.append(career_level.track)
                        parent_track = career_level.track.parent_track
                        if parent_track is not None:
                            all_child_branches_available = True
                            for child in parent_track.branches:
                                if child not in career_tracks_added:
                                    all_child_branches_available = False
                                    break

                            if all_child_branches_available:
                                career_tracks_to_skip.append(parent_track)

        for career_tuning in all_possible_careers:
            if 0 < num_careers_to_show <= len(career_tracks_added):
                break
            if not career_tuning.show_career_in_join_career_picker:
                continue
            test_result = career_tuning.is_career_available(sim_info=sim_info, from_join=True)
            if test_result and sim_info.career_tracker.get_career_by_uid(career_tuning.guid64) is None:
                for new_level, _, current_track in career_tuning.get_career_entry_level(career_history=(sim_info.career_tracker.career_history), resolver=(SingleSimResolver(sim_info))):
                    if current_track in career_tracks_to_skip:
                        continue
                    selectable_test_result = career_tuning.is_career_selectable(sim_info=sim_info)
                    if current_track not in career_tracks_added:
                        not_selectable_tooltip = None
                        if not selectable_test_result.result:
                            if selectable_test_result.tooltip is not None:
                                not_selectable_tooltip = selectable_test_result.tooltip()
                        Career._append_career_info_pb(msg, sim_info,
                          career_tuning,
                          current_track,
                          new_level,
                          selectable=(selectable_test_result.result),
                          not_selectable_tooltip=not_selectable_tooltip)

        return msg

    @staticmethod
    def get_quit_career_pb(sim_info):
        msg = protocolbuffers.Sims_pb2.CareerSelectionUI()
        msg.sim_id = sim_info.sim_id
        msg.is_branch_select = False
        msg.reason = career_ops.CareerOps.QUIT_CAREER
        for career_instance in sim_info.careers.values():
            if not career_instance.show_career_in_join_career_picker:
                continue
            career_info_msg = msg.career_choices.add()
            career_info_msg.uid = career_instance.guid64
            career_info_msg.career_track = career_instance.current_track_tuning.guid64
            career_info_msg.career_level = career_instance.level
            career_info_msg.company = career_instance.get_company_name()
            career_info_msg.conflicted_schedule = False
            career_level = career_instance.current_track_tuning.career_levels[career_instance.level]
            work_schedule = get_career_schedule_for_level(career_level)
            if work_schedule is not None:
                work_schedule.populate_scheduler_msg(career_info_msg.work_schedule, career_instance.schedule_shift_type)

        return msg

    @staticmethod
    def get_select_career_track_pb(sim_info, career, career_branches):
        msg = protocolbuffers.Sims_pb2.CareerSelectionUI()
        msg.sim_id = sim_info.sim_id
        msg.is_branch_select = True
        for career_track in career_branches:
            career_info_msg = msg.career_choices.add()
            career_info_msg.uid = career.guid64
            career_info_msg.career_track = career_track.guid64
            career_info_msg.career_level = 0
            career_info_msg.company = career.get_company_name()
            work_schedule = get_career_schedule_for_level(career_track.career_levels[0])
            career_level = career_track.career_levels[0]
            work_schedule = get_career_schedule_for_level(career_level)
            if work_schedule is not None:
                work_schedule.populate_scheduler_msg(career_info_msg.work_schedule)

        return msg


class TunableCareerTrack(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.CAREER_TRACK)):
    INSTANCE_TUNABLES = {'career_name':sims4.localization.TunableLocalizedStringFactory(description='\n            The name of this Career Track\n            ',
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.UI), 
     'career_name_gender_neutral':sims4.localization.TunableLocalizedString(description="\n            The gender neutral name for this Career. This string is not provided\n            any tokens, and thus can't rely on context to properly form\n            masculine and feminine forms.\n            ",
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.UI), 
     'career_description':sims4.localization.TunableLocalizedString(description='A description for this Career Track',
       allow_none=True,
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.UI), 
     'icon':sims4.tuning.tunable.TunableResourceKey(None, resource_types=sims4.resources.CompoundTypes.IMAGE, description='Icon to be displayed for this Career Track',
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.UI), 
     'icon_high_res':sims4.tuning.tunable.TunableResourceKey(None, resource_types=sims4.resources.CompoundTypes.IMAGE, description='Icon to be displayed for screen slams from this career track',
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.UI), 
     'image':sims4.tuning.tunable.TunableResourceKey(None, resource_types=sims4.resources.CompoundTypes.IMAGE, description='Pre-rendered image to show in the branching select UI.',
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.UI), 
     'display_overmax_instead_of_career_levels':Tunable(description='\n            If checked, we will display overmax levels to the user instead of user career levels in the UI.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.UI), 
     'career_levels':sims4.tuning.tunable.TunableList(description='\n                            All of the career levels you need to be promoted through to\n                            get through this career track. When you get promoted past the\n                            end of a career track, and branches is tuned, you will get a selection\n                            UI where you get to pick the next part of your career.\n                            ',
       tunable=sims4.tuning.tunable.TunableReference(description='\n                                A single career track',
       manager=(services.get_instance_manager(sims4.resources.Types.CAREER_LEVEL)),
       reload_dependent=True),
       export_modes=sims4.tuning.tunable_base.ExportModes.All), 
     'branches':sims4.tuning.tunable.TunableList(sims4.tuning.tunable.TunableReference(description='A single career level',
       manager=(services.get_instance_manager(sims4.resources.Types.CAREER_TRACK))),
       description="\n                              When you get promoted past the end of a career track, branches\n                              determine which career tracks you can progress to next. i.e.\n                              You're in the medical career and the starter track has 5 levels in\n                              it. When you get promoted to level 6, you get to choose either the\n                              surgeon track, or the organ seller track \n                            ",
       export_modes=sims4.tuning.tunable_base.ExportModes.All), 
     'overmax':OptionalTunable(description='\n            If enabled, then this track is eligible for overmaxing, making Sims\n            able to increase their level and salary despite reaching the top\n            tier.\n            ',
       tunable=TunableTuple(description='\n                Overmax data for this career.\n                ',
       salary_increase=TunableRange(description='\n                    The pay raise awarded per overmax level.\n                    ',
       tunable_type=int,
       default=1,
       minimum=1),
       reward=TunableReference(description='\n                    If specified, any rewards that may be awarded when\n                    overmaxing.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.REWARD))),
       reward_by_level=OptionalTunable(description='\n                    If tuned, a special reward that will substituted for the\n                    normal reward on certain overmax levels. The keys should be\n                    tuned such that if we want a reward for the first overmax,\n                    its key should be 1.\n                    ',
       tunable=TunableMapping(key_type=TunableRange(tunable_type=int,
       default=0,
       minimum=0),
       value_type=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.REWARD))))),
       performance_threshold_increase=TunableRange(description='\n                    The amount to increase the performance requirement per\n                    overmax level. Eventually, this will be max performance.\n                    ',
       tunable_type=float,
       default=0),
       suppress_overmax_notifications=Tunable(description="\n                    If True, triggering an overmax promotion will by default not display a dialog.\n                    Individual gigs may still override this behavior by tuning gig overmax notifications in gig tuning.\n                    This merely prevents the career's base overmax notifications from appearing.\n                    ",
       tunable_type=bool,
       default=False))), 
     'knowledge_notification':OptionalTunable(description="\n            If enabled, this career track will provide a TNS when a Sim learns\n            about another Sim's career.\n            ",
       tunable=TunableUiDialogNotificationSnippet(description="\n                The notification to use when one Sim learns about another Sim's\n                career. Three additional tokens are provided: the level name (e.g.\n                Chef), the career name (e.g. Culinary), and the company name (e.g.\n                The Solar Flare).\n                "),
       enabled_by_default=True), 
     'goodbye_notification':TunableUiDialogNotificationSnippet(description='\n            The notification to use when the Sim is leaving a visit situation to\n            go to work. Three additional tokens are provided: the level name\n            (e.g. Chef), the career name (e.g. Culinary), and the company name\n            (e.g. The Solar Flare).\n            '), 
     'busy_time_situation_picker_tooltip':sims4.localization.TunableLocalizedString(description='\n            The tooltip that will display on the situation sim picker for\n            user selectable sims that will be busy during the situation.\n            ',
       export_modes=sims4.tuning.tunable_base.ExportModes.All), 
     'assignments':TunableList(description='\n            List of possible tested assignemnts that can offered on a work \n            day inside this career track.\n            ',
       tunable=TunableTuple(description='\n                Tuple of test and aspirations that will be run when selecting\n                a daily assignment.\n                ',
       tests=event_testing.tests.TunableTestSet(description='\n                   Tests to be run when daily tasks are being offered inside\n                   a career track.\n                   '),
       career_assignment=sims4.tuning.tunable.TunableReference(description='\n                    Aspiration that needs to be completed for satisfying the\n                    daily assignment.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.ASPIRATION)),
       class_restrictions='AspirationAssignment',
       pack_safe=True),
       weight=TunableRange(description='\n                    The weight of this assignment when the random roll chooses\n                    the daily tasks.\n                    ',
       tunable_type=float,
       default=1.0,
       minimum=0),
       is_first_assignment=sims4.tuning.tunable.Tunable(description='\n                    Setting this to true will trigger this assignment when a sim\n                    first joins a career.\n                    \n                    If all assignments are unchecked, the first assignment\n                    will be selected randomly.\n                    ',
       tunable_type=bool,
       default=False))), 
     'assignment_chance':TunablePercent(description='\n            Chance of an assignment being offered during a regular work day.\n            ',
       default=50), 
     'active_assignment_amount':sims4.tuning.tunable.Tunable(description='\n            Amount of active assignments to offer each time a Sim goes to work\n            \n            WARNING: Always make this less than the number of possible weighted\n            assignments.\n            ',
       tunable_type=float,
       default=2), 
     'outfit_generation_type':TunableEnumEntry(description='\n            Possible ways the career will generate the outfits for its sims.\n            By default CAREER tuning will use the level tuning to generate \n            the ouftit.\n            Zone director will use the restaurant zone director tuning to  \n            validate and generate the outfits for each level.\n            ',
       tunable_type=CareerOutfitGenerationType,
       default=CareerOutfitGenerationType.CAREER_TUNING), 
     'show_now_hiring_string':Tunable(description='\n            If true, the "Now Hiring" string will show in the "select a career"\n            panel.\n            Eg: disable for simsfluencers and video game streamers since they are \n            self-employed, only the job name will be displayed.\n            ',
       tunable_type=bool,
       default=True,
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.UI)}
    parent_track = None

    @classmethod
    def _verify_tuning_callback(cls):
        if cls.active_assignment_amount > len(cls.assignments):
            if len(cls.assignments) > 0:
                logger.error('Warning - the Active Assignment Amount is greater than the number of possible assignments {}', cls, owner='Shirley')

    @classmethod
    def get_career_description(cls, sim):
        return cls.career_description

    @classmethod
    def get_career_name(cls, sim):
        return cls.career_name(sim)


class TunableTimePeriod(sims4.tuning.tunable.TunableTuple):

    def __init__(self, **kwargs):
        (super().__init__)(start_time=tunable_time.TunableTimeOfWeek(description='Time when the period starts.'), 
         period_duration=sims4.tuning.tunable.Tunable(float, 1.0, description='Duration of this time period in hours.'), **kwargs)


class TunableOutfit(TunableTuple):

    def __init__(self, **kwargs):
        (super().__init__)(outfit_generator=OptionalTunable(TunableOutfitGeneratorReference(pack_safe=True)), 
         generate_on_level_change=Tunable(description='\n                If checked, then an outfit is regenerated for this Sim on\n                promotion/demotion. If unchecked, the existing outfit is\n                maintained.\n                ',
  tunable_type=bool,
  default=True), **kwargs)


class StatisticPerformanceModifier(TunableTuple):

    def __init__(self, **kwargs):
        (super().__init__)(statistic=TunableReference(description='\n                Statistic that contributes to this performance modifier.\n                ',
  manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC))), 
         performance_curve=TunableCurve(description='\n                Curve that maps the commodity to performance change. X is the\n                commodity value, Y is the bonus performance.\n                '), 
         reset_at_end_of_work=Tunable(description='\n                If set, the statistic will be reset back to its default value\n                when a Sim leaves work.\n                ',
  tunable_type=bool,
  default=True), 
         tooltip_text=OptionalTunable(description="\n                If enabled, this performance modifier's description will appear\n                in its tooltip.\n                ",
  tunable=TunableTuple(general_description=TunableLocalizedStringFactory(description='\n                        A description of the performance modifier. {0.String}\n                        is the thresholded description.\n                        '),
  thresholded_descriptions=TunableList(description='\n                        A list of thresholds and the text describing it. The\n                        thresholded description will be largest threshold\n                        value in this list that the commodity is >= to.\n                        ',
  tunable=TunableTuple(threshold=Tunable(description='\n                                Threshold that the commodity must >= to.\n                                ',
  tunable_type=float,
  default=0.0),
  text=TunableLocalizedString(description='\n                                Description for meeting this threshold.\n                                '))))), **kwargs)


class TunableWorkPerformanceMetrics(sims4.tuning.tunable.TunableTuple):

    def __init__(self, **kwargs):
        (super().__init__)(base_performance=sims4.tuning.tunable.Tunable(float, 1.0, description='Base work performance before any modifications are applied for going to a full day of work.'), 
         missed_work_penalty=sims4.tuning.tunable.Tunable(float, 1.0, description="Penalty that is applied to your work day performance if you don't attend a full day of work."), 
         full_work_day_percent=sims4.tuning.tunable.TunableRange(float, 80, 1, 100, description='This is the percent of the work day you must have been running the work interaction, to get full credit for your performance on that day. Ex: If this is tuned to 80, and you have a 5 hour work day, You must be inside the work interaction for at least 4 hours to get 100% of your performance. If you only went to work for 2 hours, you would get: (base_performance + positive performance mods * 0.5) + negative performance mods'), 
         commodity_metrics=sims4.tuning.tunable.TunableList(sims4.tuning.tunable.TunableTuple(commodity=sims4.tuning.tunable.TunableReference(description='Commodity this test should apply to on the sim.',
  manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC))),
  threshold=sims4.tuning.tunable.TunableThreshold(description='The amount of commodity needed to get this performance mod.'),
  performance_mod=sims4.tuning.tunable.Tunable(float, 1.0, description='Work Performance you get for passing the commodity threshold.'),
  description='DEPRECATED. USE STATISTIC METRICS INSTEAD. If the tunable commodity is within the tuned threshold, this performance mod will be applied to an individual day of work.')), 
         mood_metrics=sims4.tuning.tunable.TunableList(sims4.tuning.tunable.TunableTuple(mood=sims4.tuning.tunable.TunableReference(description='Mood the Sim needs to get this performance change.',
  manager=(services.get_instance_manager(sims4.resources.Types.MOOD))),
  performance_mod=sims4.tuning.tunable.Tunable(float, 1.0, description='Work Performance you get for having this mood.'),
  description='If the Sim is in this mood state, they will get this performance mod applied for a day of work')), 
         statistic_metrics=TunableList(description='\n                             Performance modifiers based on a statistic.\n                             ',
  tunable=(StatisticPerformanceModifier())), 
         performance_tooltip=OptionalTunable(description='\n                             Text to show on the performance tooltip below the\n                             ideal mood bar. Any Statistic Metric tooltip text\n                             will appear below this text on a new line.\n                             ',
  tunable=(TunableLocalizedString())), 
         performance_per_completed_goal=Tunable(description='\n                             The performance amount to give per completed\n                             career goal each work period.\n                             ',
  tunable_type=float,
  default=0.0), 
         tested_metrics=TunableList(description='\n                             Performance modifiers that are applied based on\n                             the test.\n                             ',
  tunable=TunableTuple(tests=event_testing.tests.TunableTestSet(description='\n                                    Tests that must pass to get the performance modifier.\n                                    '),
  performance_mod=sims4.tuning.tunable.Tunable(description='\n                                    Performance modifier (add/subtract) the Sim receives for passing the test. Can be negative.\n                                    ',
  tunable_type=float,
  default=0.0),
  performance_stat_multiplier=TunableTuple(description='\n                                    Apply a multiplier to performance depending on what the end calculated \n                                    performance value is in relation to the tuned direction.\n                                    \n                                    Example: If a multiplier and apply_direction of INCREASE were tuned, then the\n                                             multiplier would only be applied if the end calculated performance value\n                                             was a performance gain (> 0).\n                                    ',
  multiplier=sims4.tuning.tunable.Tunable(description="\n                                        Multiplier to the sim's performance for passing the tests. Can be negative. \n                                        ",
  tunable_type=float,
  default=1.0),
  apply_direction=TunableEnumEntry(description='\n                                        Direction for when the multiplier should be applied.\n                                        ',
  tunable_type=StatisticChangeDirection,
  default=(StatisticChangeDirection.BOTH))))), 
         daily_assignment_performance=Tunable(description='\n                             The total performance amount to give for completing all\n                             assignments.\n                             ',
  tunable_type=float,
  default=1.0), **kwargs)


class CareerLevel(SuperAffordanceProviderMixin, TargetSuperAffordanceProviderMixin, MixerProviderMixin, MixerActorMixin, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.CAREER_LEVEL)):
    INSTANCE_TUNABLES = {'title':sims4.localization.TunableLocalizedStringFactory(description='Your career title for this career level',
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.UI), 
     'title_description':sims4.localization.TunableLocalizedStringFactory(description='A description for this individual career level',
       allow_none=True,
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.UI), 
     'promotion_audio_sting':OptionalTunable(description='\n            The audio sting to play when the Sim is promoted to this Career Level.\n            ',
       tunable=TunablePlayAudio(),
       tuning_group=GroupNames.AUDIO), 
     'screen_slam':OptionalTunable(description='\n            Which screen slam to show when this career level is reached.\n            Localization Tokens: Sim - {0.SimFirstName}, Level Name - \n            {1.String}, Level Number - {2.Number}, Track Name - {3.String}\n            ',
       tunable=ui.screen_slam.TunableScreenSlamSnippet()), 
     'work_schedule':scheduler.WeeklySchedule.TunableFactory(description='\n            A tunable schedule that will determine when you have to be at work.\n            ',
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.DEPRECATED), 
     'schedule':TunableCareerScheduleVariant(description='\n            Define the work hours for this particular career level.\n            '), 
     'additional_unavailable_times':sims4.tuning.tunable.TunableList(TunableTimePeriod(description='An individual period of time in which the sim is unavailible at this Career Level.'),
       description='A list time periods in which the Sim is considered busy for the sake of Sim Filters in addition to the normal working hours.'), 
     'wakeup_time':tunable_time.TunableTimeOfDay(description="\n            The time when the sim needs to wake up for work.  This is used by autonomy\n            to determine when it's appropriate to nap vs sleep.  It also guides a series\n            of buffs to make the sim more inclined to sleep as their bedtime approaches.",
       default_hour=8,
       needs_tuning=True), 
     'work_outfit':TunableOutfit(description='Tuning for this career level outfit.'), 
     'work_outfit_overrides':sims4.tuning.tunable.TunableList(description='\n            A list of (test, outfit) pairs. If any test passes, the corresponding\n            work outfit override will be chosen. When a work outfit override is\n            chosen, no later tests will be evaluated, so higher priority tests\n            should come first. \n            ',
       tunable=TunableTuple(test=TunableTestSet(description='\n                    The test.\n                    '),
       work_outfit=TunableOutfit(description='\n                    The outfit to use to override work_outfit\n                    '))), 
     'aspiration':sims4.tuning.tunable.TunableReference(manager=services.get_instance_manager(sims4.resources.Types.ASPIRATION),
       allow_none=True,
       description='The Aspiration you need to complete to be eligible for promotion.',
       export_modes=sims4.tuning.tunable_base.ExportModes.All), 
     'pay_type':TunableVariant(description='\n            The different way the sim can be paid. \n            If it is gig based then just a string is displayed. \n            ',
       simoleons_per_hour=Tunable(description='\n                number of simoleons you get per hour this level.\n                ',
       tunable_type=int,
       default=10),
       potential_simoleons_weekly=TunableLocalizedStringFactory(description="\n                String to display if sim doesn't earn a set amount of simoleons\n                per hour. \n                "),
       export_modes=ExportModes.All), 
     'simoleons_for_assignments_per_day':sims4.tuning.tunable.Tunable(description=' \n            Number of simoleons acquired if completing all assignments in a day.\n            (scaled and handled out per assignment.)\n            ',
       tunable_type=int,
       default=10), 
     'pto_per_day':sims4.tuning.tunable.Tunable(description=' \n            Number of days of PTO per full day worked.  Will be scaled according\n            to how much time is actually worked.\n            ',
       tunable_type=float,
       default=0.1,
       export_modes=sims4.tuning.tunable_base.ExportModes.All), 
     'pto_accrual_trait_multiplier':TunableList(description='\n            A multiplier on the rate of pto accrual\n            ',
       tunable=sims4.tuning.tunable.TunableTuple(trait=sims4.tuning.tunable.TunableReference(description='\n                    Trait to test for on the Sim that applies the pto multiplier.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
       pack_safe=True),
       multiplier=sims4.tuning.tunable.Tunable(description='\n                    The multiplier to apply to the rate of pto accrual\n                    ',
       tunable_type=float,
       default=1))), 
     'simolean_trait_bonus':sims4.tuning.tunable.TunableList(description='\n            A bonus additional income amount applied at the end of the work day to total take home pay\n            based on the presence of the tuned trait.',
       tunable=sims4.tuning.tunable.TunableTuple(trait=sims4.tuning.tunable.TunableReference(description='\n                    Trait to test for on the Sim that allows the bonus to get added.',
       manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
       pack_safe=True),
       bonus=sims4.tuning.tunable.Tunable(description='\n                Percentage of daily take to add as bonus income.',
       tunable_type=int,
       default=20,
       tuning_group=(GroupNames.SCORING)))), 
     'performance_stat':sims4.tuning.tunable.TunableReference(services.get_instance_manager(sims4.resources.Types.STATISTIC),
       description='Commodity used to track career performance for this level.',
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.SCORING), 
     'demotion_performance_level':sims4.tuning.tunable.Tunable(float, -80.0, description='Level of performance commodity to cause demotion.',
       tuning_group=GroupNames.SCORING), 
     'fired_performance_level':sims4.tuning.tunable.Tunable(float, -95.0, description='Level of performance commodity to cause being fired.',
       tuning_group=GroupNames.SCORING), 
     'promote_performance_level':sims4.tuning.tunable.Tunable(float, 100.0, description='Level of performance commodity to cause being promoted.',
       tuning_group=GroupNames.SCORING), 
     'performance_metrics':TunableWorkPerformanceMetrics(tuning_group=GroupNames.SCORING), 
     'promotion_reward':sims4.tuning.tunable.TunableReference(manager=services.get_instance_manager(sims4.resources.Types.REWARD),
       allow_none=True,
       description='\n            Which rewards are given when this career level\n            is reached.\n            '), 
     'tones':OptionalTunable(description='\n            If enabled, specify tones that the Sim can have in its skewer while\n            at work.\n            ',
       tunable=CareerToneTuning.TunableFactory(description='\n                Tuning for tones.\n                ')), 
     'ideal_mood':sims4.tuning.tunable.TunableReference(description='\n            The ideal mood to display to the user to be in to gain performance at this career level\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.MOOD),
       allow_none=True,
       export_modes=sims4.tuning.tunable_base.ExportModes.ClientBinary,
       tuning_group=GroupNames.UI), 
     'loot_on_join':TunableList(description='\n            A list of loot actions to give the sim when they join the career\n            at this level.\n            ',
       tunable=LootActions.TunableReference(description='\n                Loot to give when Sim joins the career at this career level.\n                ',
       pack_safe=True)), 
     'loot_on_quit':TunableList(description='\n            A list of loot to give when the Sim quits the career on this level.\n            ',
       tunable=LootActions.TunableReference(description='\n                Loot to give when Sim quits the career on this career level.\n                ',
       pack_safe=True)), 
     'loot_on_lay_off':TunableList(description='\n            A list of loots to give when the Sim is laid off from the career on this level.\n            ',
       tunable=LootActions.TunableReference(description='\n                Loot to give when Sim is laid off from the career on this career level.\n                ',
       pack_safe=True)), 
     'object_create_on_join':TunableList(description='\n            Objects to create on join.  If marked as require claim they will only exist\n            for as long as the sim in in the career at this level.\n            ',
       tunable=ObjectCreation.TunableFactory()), 
     'stay_late_extension':TunableSimMinute(description='\n            How long to extend the active work shift when the Sim stays late.\n            ',
       default=120), 
     'end_of_day_loot':TunableSet(description='\n            List of loot applied to the sim at the end of the day.\n            Currently used only to max out daily task at the end of the day\n            if responsible trait is available but it can be extended to include\n            more end of day loot in the future.\n            ',
       tunable=LootActions.TunableReference(description='\n                Loot to give at the end of the day. \n                ',
       pack_safe=True)), 
     'fame_moment':OptionalTunable(description='\n            When enabled allows a fame adventure moment to be displayed to the\n            user, once per career track.\n            ',
       tunable=TunableTuple(description='\n                The data associated with a fame moment.\n                \n                moment is the adventure moment that is displayed when the\n                    moment occurs\n                \n                chance_to_occur is the liklihood that a moment happens during\n                    a shift.\n                ',
       moment=Adventure.TunableFactory(description='\n                    A reference to the adventure moment that can happen once and only\n                    once while the Sim has this career track.\n                    '),
       chance_to_occur=SuccessChance.TunableFactory(description='\n                    The chance the moment will happen during a given shift.\n                    '))), 
     'agents_available':TunableList(description='\n            List of agents available for this career level. A higher level \n            should include more agents not fewer.\n            ',
       tunable=TunableReference(description='\n                A reference to the agent available for this career level.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
       pack_safe=True),
       export_modes=ExportModes.All), 
     'ageup_branch_career':OptionalTunable(description='\n            This adult career will be assigned to the teen that ages up while\n            on the parent career.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.CAREER))))}
    career = None
    track = None
    level = None
    user_level = None

    @classmethod
    def _verify_tuning_callback(cls):
        for trait in cls.agents_available:
            if trait.trait_type != TraitType.AGENT:
                logger.error('Only trait type agent allowed in this list.')

    @classmethod
    def get_aspiration(cls):
        return cls.aspiration

    @classmethod
    def get_title(cls, sim):
        return cls.title(sim)

    @classproperty
    def simoleons_per_hour(cls):
        if isinstance(cls.pay_type, int):
            return cls.pay_type
        return 0

    @classmethod
    def get_work_outfit(cls, sim_info):
        if cls.work_outfit_overrides:
            if sim_info is not None:
                resolver = SingleSimResolver(sim_info)
                for override in cls.work_outfit_overrides:
                    if override.test.run_tests(resolver):
                        return override.work_outfit

        return cls.work_outfit

    @classmethod
    def get_adventures(cls):
        return_dict = {}
        if cls.fame_moment is not None:
            return_dict['fame moment'] = (
             cls.fame_moment.moment,)
        return return_dict


class DefaultCareerSelectionData:

    def __init__(self, default_career_select=0, career_selector_type=0):
        self.default_career_select = default_career_select
        self.career_selector_type = career_selector_type


class CareerSelectionDefault(HasTunableSingletonFactory, AutoFactoryInit):

    def get_default_career_information(self):
        raise NotImplementedError


class CareerReferenceSelectionDefault(CareerSelectionDefault):
    FACTORY_TUNABLES = {'toggle_career': TunableTuple(default_career=TunablePackSafeReference(description='\n                The default selected career.\n                ',
                        manager=(services.get_instance_manager(sims4.resources.Types.CAREER))),
                        toggle_to_career_selector_type=Tunable(description="\n                If set to True, the career panel will open to the career selector\n                type panel of the tuned default career's selector type. If False,\n                the career will be selected in the default All Careers panel.\n                ",
                        tunable_type=bool,
                        default=False))}

    def get_default_career_information(self):
        default_career = self.toggle_career.default_career
        default_career_select_uid = self.toggle_career.default_career.guid64 if default_career is not None else 0
        career_selector_type = CareerSelectorTypes.ALL
        if default_career is not None:
            if self.toggle_career.toggle_to_career_selector_type:
                career_selector_type = get_selector_type_from_career_category(default_career)
        return DefaultCareerSelectionData(default_career_select=default_career_select_uid, career_selector_type=career_selector_type)


class CareerSelectorCategoryDefault(CareerSelectionDefault):
    FACTORY_TUNABLES = {'default_selector_type': TunableEnumEntry(description='\n            The default panel at which to open the career selection\n            window.\n            ',
                                tunable_type=CareerSelectorTypes,
                                default=(CareerSelectorTypes.ALL))}

    def get_default_career_information(self):
        return DefaultCareerSelectionData(career_selector_type=(self.default_selector_type))


class CareerSelectElement(interactions.utils.interaction_elements.XevtTriggeredElement):
    FACTORY_TUNABLES = {'description':'Perform an operation on a Sim Career', 
     'career_op':sims4.tuning.tunable.TunableEnumEntry(career_ops.CareerOps, career_ops.CareerOps.JOIN_CAREER, description='\n                                Operation this basic extra will perform on the\n                                career.  Currently supports Joining, Quitting\n                                and Playing Hooky/Calling In Sick.\n                                '), 
     'subject':TunableEnumFlags(description='\n            The Sim to run this career op on.\n            Currently, the only supported options are Actor and PickedSim\n            ',
       enum_type=ParticipantType,
       default=ParticipantType.Actor), 
     'default_career_window_selection':OptionalTunable(description='\n            If enabled, then the default selection in the Career Selection Window\n            will be set to the tuned value.\n            ',
       tunable=TunableVariant(career_reference=CareerReferenceSelectionDefault.TunableFactory(description='\n                    Default selection and selector type is based on a single \n                    career reference.\n                    '),
       career_selector_type=CareerSelectorCategoryDefault.TunableFactory(description='\n                    Default selector type panel is the tuned value.\n                    '),
       default='career_reference'))}

    def _get_default_selection_data(self):
        if self.default_career_window_selection is not None:
            return self.default_career_window_selection.get_default_career_information()

    def _do_behavior--- This code section failed: ---

 L.2569         0  LOAD_GLOBAL              services
                2  LOAD_METHOD              current_zone
                4  CALL_METHOD_0         0  '0 positional arguments'
                6  LOAD_ATTR                ui_dialog_service
                8  LOAD_ATTR                auto_respond
               10  POP_JUMP_IF_FALSE    16  'to 16'

 L.2570        12  LOAD_CONST               None
               14  RETURN_VALUE     
             16_0  COME_FROM            10  '10'

 L.2572        16  LOAD_FAST                'self'
               18  LOAD_ATTR                interaction
               20  LOAD_METHOD              get_participants
               22  LOAD_FAST                'self'
               24  LOAD_ATTR                subject
               26  CALL_METHOD_1         1  '1 positional argument'
               28  STORE_FAST               'participants'

 L.2574        30  LOAD_FAST                'participants'
               32  LOAD_CONST               None
               34  COMPARE_OP               is
               36  POP_JUMP_IF_TRUE     50  'to 50'
               38  LOAD_GLOBAL              len
               40  LOAD_FAST                'participants'
               42  CALL_FUNCTION_1       1  '1 positional argument'
               44  LOAD_CONST               0
               46  COMPARE_OP               ==
               48  POP_JUMP_IF_FALSE    76  'to 76'
             50_0  COME_FROM            36  '36'

 L.2575        50  LOAD_GLOBAL              logger
               52  LOAD_ATTR                error
               54  LOAD_STR                 'Could not find participant type, {}, for the Career Select op on interaction, {}'
               56  LOAD_FAST                'self'
               58  LOAD_ATTR                subject
               60  LOAD_FAST                'self'
               62  LOAD_ATTR                interaction
               64  LOAD_STR                 'Trevor'
               66  LOAD_CONST               ('owner',)
               68  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
               70  POP_TOP          

 L.2576        72  LOAD_CONST               None
               74  RETURN_VALUE     
             76_0  COME_FROM            48  '48'

 L.2578        76  LOAD_GLOBAL              len
               78  LOAD_FAST                'participants'
               80  CALL_FUNCTION_1       1  '1 positional argument'
               82  LOAD_CONST               1
               84  COMPARE_OP               >
               86  POP_JUMP_IF_FALSE   110  'to 110'

 L.2579        88  LOAD_GLOBAL              logger
               90  LOAD_ATTR                warn
               92  LOAD_STR                 'More than one participant found of type, {}, for the Career Select op on interaction, {}'
               94  LOAD_FAST                'self'
               96  LOAD_ATTR                subject
               98  LOAD_FAST                'self'
              100  LOAD_ATTR                interaction
              102  LOAD_STR                 'Dan P'
              104  LOAD_CONST               ('owner',)
              106  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
              108  POP_TOP          
            110_0  COME_FROM            86  '86'

 L.2581       110  LOAD_GLOBAL              next
              112  LOAD_GLOBAL              iter
              114  LOAD_FAST                'participants'
              116  CALL_FUNCTION_1       1  '1 positional argument'
              118  CALL_FUNCTION_1       1  '1 positional argument'
              120  STORE_FAST               'sim_or_sim_info'

 L.2582       122  LOAD_GLOBAL              getattr
              124  LOAD_FAST                'sim_or_sim_info'
              126  LOAD_STR                 'sim_info'
              128  LOAD_FAST                'sim_or_sim_info'
              130  CALL_FUNCTION_3       3  '3 positional arguments'
              132  STORE_DEREF              'sim_info'

 L.2584       134  LOAD_FAST                'self'
              136  LOAD_ATTR                career_op
              138  LOAD_GLOBAL              career_ops
              140  LOAD_ATTR                CareerOps
              142  LOAD_ATTR                JOIN_CAREER
              144  COMPARE_OP               ==
              146  POP_JUMP_IF_FALSE   238  'to 238'

 L.2585       148  LOAD_GLOBAL              Career
              150  LOAD_ATTR                NUM_CAREERS_PER_DAY
              152  STORE_FAST               'num'

 L.2586       154  LOAD_FAST                'self'
              156  LOAD_ATTR                interaction
              158  LOAD_ATTR                debug
              160  POP_JUMP_IF_TRUE    170  'to 170'
              162  LOAD_FAST                'self'
              164  LOAD_ATTR                interaction
              166  LOAD_ATTR                cheat
              168  POP_JUMP_IF_FALSE   174  'to 174'
            170_0  COME_FROM           160  '160'

 L.2587       170  LOAD_CONST               0
              172  STORE_FAST               'num'
            174_0  COME_FROM           168  '168'

 L.2589       174  LOAD_DEREF               'sim_info'
              176  LOAD_ATTR                is_selectable
              178  POP_JUMP_IF_FALSE   234  'to 234'
              180  LOAD_DEREF               'sim_info'
              182  LOAD_ATTR                valid_for_distribution
              184  POP_JUMP_IF_FALSE   234  'to 234'

 L.2590       186  LOAD_FAST                'self'
              188  LOAD_METHOD              _get_default_selection_data
              190  CALL_METHOD_0         0  '0 positional arguments'
              192  STORE_FAST               'default_career_selection_data'

 L.2591       194  LOAD_GLOBAL              Career
              196  LOAD_ATTR                get_join_career_pb
              198  LOAD_DEREF               'sim_info'

 L.2592       200  LOAD_FAST                'num'

 L.2593       202  LOAD_FAST                'default_career_selection_data'
              204  LOAD_CONST               ('num_careers_to_show', 'default_career_selection_data')
              206  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              208  STORE_FAST               'msg'

 L.2594       210  LOAD_GLOBAL              Distributor
              212  LOAD_METHOD              instance
              214  CALL_METHOD_0         0  '0 positional arguments'
              216  LOAD_METHOD              add_op
              218  LOAD_DEREF               'sim_info'
              220  LOAD_GLOBAL              GenericProtocolBufferOp
              222  LOAD_GLOBAL              Operation
              224  LOAD_ATTR                SELECT_CAREER_UI
              226  LOAD_FAST                'msg'
              228  CALL_FUNCTION_2       2  '2 positional arguments'
              230  CALL_METHOD_2         2  '2 positional arguments'
              232  POP_TOP          
            234_0  COME_FROM           184  '184'
            234_1  COME_FROM           178  '178'
          234_236  JUMP_FORWARD        566  'to 566'
            238_0  COME_FROM           146  '146'

 L.2595       238  LOAD_FAST                'self'
              240  LOAD_ATTR                career_op
              242  LOAD_GLOBAL              career_ops
              244  LOAD_ATTR                CareerOps
              246  LOAD_ATTR                QUIT_CAREER
              248  COMPARE_OP               ==
          250_252  POP_JUMP_IF_FALSE   514  'to 514'

 L.2596       254  LOAD_GLOBAL              len
              256  LOAD_DEREF               'sim_info'
              258  LOAD_ATTR                career_tracker
              260  LOAD_METHOD              get_quittable_careers
              262  CALL_METHOD_0         0  '0 positional arguments'
              264  CALL_FUNCTION_1       1  '1 positional argument'
              266  LOAD_CONST               1
              268  COMPARE_OP               ==
          270_272  POP_JUMP_IF_FALSE   462  'to 462'

 L.2600       274  LOAD_CLOSURE             'career'
              276  LOAD_CLOSURE             'sim_info'
              278  BUILD_TUPLE_2         2 
              280  LOAD_CODE                <code_object on_quit_dialog_response>
              282  LOAD_STR                 'CareerSelectElement._do_behavior.<locals>.on_quit_dialog_response'
              284  MAKE_FUNCTION_8          'closure'
              286  STORE_FAST               'on_quit_dialog_response'

 L.2604       288  LOAD_GLOBAL              SingleSimResolver
              290  LOAD_DEREF               'sim_info'
              292  CALL_FUNCTION_1       1  '1 positional argument'
              294  STORE_FAST               'resolver'

 L.2605       296  SETUP_LOOP          512  'to 512'
              298  LOAD_DEREF               'sim_info'
              300  LOAD_ATTR                career_tracker
              302  LOAD_METHOD              get_quittable_careers
              304  CALL_METHOD_0         0  '0 positional arguments'
              306  LOAD_METHOD              values
              308  CALL_METHOD_0         0  '0 positional arguments'
              310  GET_ITER         
              312  FOR_ITER            458  'to 458'
              314  STORE_DEREF              'career'

 L.2608       316  LOAD_DEREF               'career'
              318  LOAD_ATTR                _current_track
              320  LOAD_METHOD              get_career_name
              322  LOAD_DEREF               'sim_info'
              324  CALL_METHOD_1         1  '1 positional argument'
              326  STORE_FAST               'career_name'

 L.2609       328  LOAD_DEREF               'career'
              330  LOAD_ATTR                current_level_tuning
              332  LOAD_METHOD              get_title
              334  LOAD_DEREF               'sim_info'
              336  CALL_METHOD_1         1  '1 positional argument'
              338  STORE_FAST               'job_title'

 L.2610       340  LOAD_CONST               None
              342  STORE_FAST               'dialog'

 L.2611       344  LOAD_DEREF               'career'
              346  LOAD_ATTR                quittable_data
              348  LOAD_ATTR                tested_quit_dialog
              350  LOAD_CONST               None
              352  COMPARE_OP               is-not
          354_356  POP_JUMP_IF_FALSE   406  'to 406'

 L.2612       358  SETUP_LOOP          406  'to 406'
              360  LOAD_DEREF               'career'
              362  LOAD_ATTR                quittable_data
              364  LOAD_ATTR                tested_quit_dialog
              366  GET_ITER         
            368_0  COME_FROM           382  '382'
              368  FOR_ITER            404  'to 404'
              370  STORE_FAST               'career_dialog_test'

 L.2613       372  LOAD_FAST                'career_dialog_test'
              374  LOAD_ATTR                test_set
              376  LOAD_METHOD              run_tests
              378  LOAD_FAST                'resolver'
              380  CALL_METHOD_1         1  '1 positional argument'
          382_384  POP_JUMP_IF_FALSE   368  'to 368'

 L.2615       386  LOAD_FAST                'career_dialog_test'
              388  LOAD_METHOD              quit_dialog
              390  LOAD_DEREF               'sim_info'
              392  LOAD_FAST                'resolver'
              394  CALL_METHOD_2         2  '2 positional arguments'
              396  STORE_FAST               'dialog'

 L.2616       398  BREAK_LOOP       
          400_402  JUMP_BACK           368  'to 368'
              404  POP_BLOCK        
            406_0  COME_FROM_LOOP      358  '358'
            406_1  COME_FROM           354  '354'

 L.2617       406  LOAD_FAST                'dialog'
              408  LOAD_CONST               None
              410  COMPARE_OP               is
          412_414  POP_JUMP_IF_FALSE   430  'to 430'

 L.2618       416  LOAD_DEREF               'career'
              418  LOAD_ATTR                quittable_data
              420  LOAD_METHOD              quit_dialog
              422  LOAD_DEREF               'sim_info'
              424  LOAD_FAST                'resolver'
              426  CALL_METHOD_2         2  '2 positional arguments'
              428  STORE_FAST               'dialog'
            430_0  COME_FROM           412  '412'

 L.2620       430  LOAD_FAST                'dialog'
              432  LOAD_ATTR                show_dialog
              434  LOAD_FAST                'on_quit_dialog_response'

 L.2621       436  LOAD_FAST                'career_name'
              438  LOAD_FAST                'job_title'
              440  LOAD_DEREF               'career'
              442  LOAD_METHOD              get_company_name
              444  CALL_METHOD_0         0  '0 positional arguments'
              446  BUILD_TUPLE_3         3 
              448  LOAD_CONST               ('on_response', 'additional_tokens')
              450  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              452  POP_TOP          
          454_456  JUMP_BACK           312  'to 312'
              458  POP_BLOCK        
              460  JUMP_FORWARD        512  'to 512'
            462_0  COME_FROM           270  '270'

 L.2623       462  LOAD_DEREF               'sim_info'
              464  LOAD_ATTR                is_selectable
          466_468  POP_JUMP_IF_FALSE   566  'to 566'
              470  LOAD_DEREF               'sim_info'
              472  LOAD_ATTR                valid_for_distribution
          474_476  POP_JUMP_IF_FALSE   566  'to 566'

 L.2624       478  LOAD_GLOBAL              Career
              480  LOAD_METHOD              get_quit_career_pb
              482  LOAD_DEREF               'sim_info'
              484  CALL_METHOD_1         1  '1 positional argument'
              486  STORE_FAST               'msg'

 L.2625       488  LOAD_GLOBAL              Distributor
              490  LOAD_METHOD              instance
              492  CALL_METHOD_0         0  '0 positional arguments'
              494  LOAD_METHOD              add_op
              496  LOAD_DEREF               'sim_info'
              498  LOAD_GLOBAL              GenericProtocolBufferOp
              500  LOAD_GLOBAL              Operation
              502  LOAD_ATTR                SELECT_CAREER_UI
              504  LOAD_FAST                'msg'
              506  CALL_FUNCTION_2       2  '2 positional arguments'
              508  CALL_METHOD_2         2  '2 positional arguments'
              510  POP_TOP          
            512_0  COME_FROM           460  '460'
            512_1  COME_FROM_LOOP      296  '296'
              512  JUMP_FORWARD        566  'to 566'
            514_0  COME_FROM           250  '250'

 L.2626       514  LOAD_FAST                'self'
              516  LOAD_ATTR                career_op
              518  LOAD_GLOBAL              career_ops
              520  LOAD_ATTR                CareerOps
              522  LOAD_ATTR                CALLED_IN_SICK
              524  COMPARE_OP               ==
          526_528  POP_JUMP_IF_FALSE   566  'to 566'

 L.2627       530  SETUP_LOOP          566  'to 566'
              532  LOAD_DEREF               'sim_info'
              534  LOAD_ATTR                careers
              536  LOAD_METHOD              values
              538  CALL_METHOD_0         0  '0 positional arguments'
              540  GET_ITER         
              542  FOR_ITER            564  'to 564'
              544  STORE_DEREF              'career'

 L.2628       546  LOAD_DEREF               'career'
              548  LOAD_METHOD              request_day_off
              550  LOAD_GLOBAL              career_ops
              552  LOAD_ATTR                CareerTimeOffReason
              554  LOAD_ATTR                FAKE_SICK
              556  CALL_METHOD_1         1  '1 positional argument'
              558  POP_TOP          
          560_562  JUMP_BACK           542  'to 542'
              564  POP_BLOCK        
            566_0  COME_FROM_LOOP      530  '530'
            566_1  COME_FROM           526  '526'
            566_2  COME_FROM           512  '512'
            566_3  COME_FROM           474  '474'
            566_4  COME_FROM           466  '466'
            566_5  COME_FROM           234  '234'

Parse error at or near `COME_FROM_LOOP' instruction at offset 512_1