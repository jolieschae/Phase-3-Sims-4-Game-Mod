# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\tunable_icon.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 12633 bytes
import random
from distributor.shared_messages import IconInfoData, EMPTY_ICON_INFO_DATA
from interactions import ParticipantType, ParticipantTypeSingle
from interactions.utils.interaction_liabilities import PRIVACY_LIABILITY
from objects import ALL_HIDDEN_REASONS
from sims4.localization import LocalizationHelperTuning
from sims4.log import LEVEL_ERROR
from sims4.tuning.tunable import TunableFactory, TunableResourceKey, TunableEnumFlags, TunableVariant, TunablePackSafeResourceKey, TunablePackSafeReference
import services, sims4.log, sims4.resources
logger = sims4.log.Logger('Icons', default_owner='rmccord')

class TunableIcon(TunableResourceKey):

    def __init__(self, *, description='The icon image to be displayed.', **kwargs):
        (super().__init__)(None, resource_types=sims4.resources.CompoundTypes.IMAGE, description=description, **kwargs)


class TunableIconAllPacks(TunablePackSafeResourceKey):

    def __init__(self, *, description='The icon image to be displayed.', **kwargs):
        (super().__init__)(None, resource_types=sims4.resources.CompoundTypes.IMAGE, description=description, **kwargs)

    @property
    def validate_pack_safe(self):
        return False


class TunableIconFactory(TunableFactory):

    @staticmethod
    def factory(_, key, balloon_target_override=None, **kwargs):
        if balloon_target_override is not None:
            return IconInfoData(obj_instance=balloon_target_override)
        return IconInfoData(icon_resource=key)

    FACTORY_TYPE = factory

    def __init__(self, pack_safe=False, **kwargs):
        icon_type = TunableIcon if not pack_safe else TunableIconAllPacks
        (super().__init__)(key=icon_type(), description='The icon image to be displayed.', **kwargs)


class TunableParticipantTypeIconFactory(TunableFactory):

    @staticmethod
    def factory(resolver, participant_type, balloon_target_override=None, **kwargs):
        if resolver is None:
            logger.callstack('Attempting to use a None resolver in an icon.', level=LEVEL_ERROR, owner='rmccord')
            return EMPTY_ICON_INFO_DATA
        elif balloon_target_override is not None:
            return IconInfoData(obj_instance=balloon_target_override)
            icon_targets = resolver.get_participants(participant_type)
            if icon_targets:
                chosen_object = random.choice(icon_targets)
        else:
            chosen_object = None
        return IconInfoData(obj_instance=chosen_object)

    FACTORY_TYPE = factory

    def __init__(self, default_participant_type=None, **kwargs):
        (super().__init__)(participant_type=TunableEnumFlags(enum_type=ParticipantType,
  default=(default_participant_type or ParticipantType.Actor)), 
         description="The Sim who's thumbnail will be used.", **kwargs)


class TunableHolidayIconFactory(TunableFactory):

    @staticmethod
    def factory(resolver, participant_type, balloon_target_override=None, **kwargs):
        if resolver is None:
            logger.callstack('Attempting to use a None resolver in an icon.', level=LEVEL_ERROR, owner='bosee')
            return EMPTY_ICON_INFO_DATA
            if balloon_target_override is not None:
                return IconInfoData(obj_instance=balloon_target_override)
            participant = resolver.get_participant(participant_type)
            if participant is None:
                logger.callstack('Unable to retrieve participant for holiday icon variant.', level=LEVEL_ERROR, owner='bosee')
                return EMPTY_ICON_INFO_DATA
        else:
            holiday_tracker = participant.household.holiday_tracker
            holiday_service = services.holiday_service()
            if holiday_service is not None:
                if holiday_tracker is not None and holiday_tracker.active_holiday_id is not None:
                    return IconInfoData(icon_resource=(holiday_service.get_holiday_display_icon(holiday_tracker.active_holiday_id)))
        return EMPTY_ICON_INFO_DATA

    def __init__(self, default_participant_type=None, **kwargs):
        (super().__init__)(participant_type=TunableEnumFlags(description="\n                We use this participant's holiday tracker to get the icon.\n                ",
                             enum_type=ParticipantTypeSingle,
                             default=(default_participant_type or ParticipantType.Actor)), **kwargs)

    FACTORY_TYPE = factory


class TunablePrivacyIconFactory(TunableFactory):

    @staticmethod
    def factory(resolver, balloon_target_override=None, **kwargs):
        if resolver is None:
            logger.callstack('Attempting to use a None resolver in an icon.', level=LEVEL_ERROR, owner='rmccord')
            return EMPTY_ICON_INFO_DATA
        else:
            if balloon_target_override is not None:
                return IconInfoData(obj_instance=balloon_target_override)
            privacy_liability = resolver.get_liability(PRIVACY_LIABILITY)
            if privacy_liability:
                violators = privacy_liability.privacy.violators
                if violators:
                    return IconInfoData(obj_instance=(random.choice(list(violators))))
        return EMPTY_ICON_INFO_DATA

    FACTORY_TYPE = factory

    def __init__(self, **kwargs):
        (super().__init__)(description="\n            Search an interaction's privacy liability to find violating Sims\n            and randomly select one to display an icon of.\n            ", **kwargs)


class TunableLifestyleBrandIconFactory(TunableFactory):

    @staticmethod
    def factory(resolver, participant_type, balloon_target_override=None, **kwargs):
        if resolver is None:
            logger.callstack('Attempting to use a None resolver in an icon.', level=LEVEL_ERROR, owner='rmccord')
            return EMPTY_ICON_INFO_DATA
        if balloon_target_override is not None:
            return IconInfoData(obj_instance=balloon_target_override)
        participant = resolver.get_participant(participant_type)
        if participant is None:
            logger.callstack('Unable to retrieve participant for Lifestyle Brand.', level=LEVEL_ERROR, owner='bosee')
            return EMPTY_ICON_INFO_DATA
        lifestyle_brand_tracker = participant.lifestyle_brand_tracker
        if lifestyle_brand_tracker is None:
            logger.callstack('Unable to find a Lifestyle Brand Tracker for the participant: {}', participant, level=LEVEL_ERROR, owner='rfleig')
            return EMPTY_ICON_INFO_DATA
        lifestyle_brand_icon = lifestyle_brand_tracker.logo
        if lifestyle_brand_icon is None:
            logger.callstack('Unable to find a Lifestyle Brand Logo for the participant: {}', participant, level=LEVEL_ERROR, owner='rfleig')
            return EMPTY_ICON_INFO_DATA
        return IconInfoData(icon_resource=lifestyle_brand_icon)

    FACTORY_TYPE = factory

    def __init__(self, **kwargs):
        (super().__init__)(participant_type=TunableEnumFlags(description='\n                The Participant who owns the lifestyle brand we want to use.\n                ',
                             enum_type=ParticipantTypeSingle,
                             default=(ParticipantType.Actor)), **kwargs)


class TunableCareerIconOverrideIconFactory(TunableFactory):

    @staticmethod
    def factory(resolver, participant_type, career_reference, balloon_target_override=None, **kwargs):
        if resolver is None:
            logger.callstack('Attempting to use a None resolver in an icon.', level=LEVEL_ERROR, owner='yecao')
            return EMPTY_ICON_INFO_DATA
        elif balloon_target_override is not None:
            return IconInfoData(obj_instance=balloon_target_override)
            participant = resolver.get_participant(participant_type)
            participant is None or participant.is_sim or logger.callstack('Unable to retrieve participant for Career.', level=LEVEL_ERROR, owner='yecao')
            return EMPTY_ICON_INFO_DATA
            career_tracker = participant.career_tracker
            if career_tracker is None:
                logger.callstack('Unable to find a Career Tracker for the participant: {}', participant, level=LEVEL_ERROR,
                  owner='yecao')
                return EMPTY_ICON_INFO_DATA
            for current_career in career_tracker.careers.values():
                if career_reference is not None and current_career.guid64 == career_reference.guid64 and current_career.icon_override is not None:
                    localized_full_name = LocalizationHelperTuning.get_sim_full_name(participant)
                    return IconInfoData(icon_resource=(current_career.icon_override), obj_name=localized_full_name)

            icon_targets = resolver.get_participants(participant_type)
            if icon_targets:
                chosen_object = random.choice(icon_targets)
        else:
            chosen_object = None
        return IconInfoData(obj_instance=chosen_object)

    FACTORY_TYPE = factory

    def __init__(self, **kwargs):
        (super().__init__)(participant_type=TunableEnumFlags(description='\n                The Participant who owns the career.\n                ',
  enum_type=ParticipantTypeSingle,
  default=(ParticipantType.Actor)), 
         career_reference=TunablePackSafeReference(description='\n                The Career to override the icon.\n                ',
  manager=(services.get_instance_manager(sims4.resources.Types.CAREER))), **kwargs)


class TunableIconVariant(TunableVariant):

    def __init__(self, default_participant_type=None, icon_pack_safe=False, **kwargs):
        if default_participant_type is not None:
            default = 'participant'
        else:
            default = 'resource_key'
        (super().__init__)(resource_key=TunableIconFactory(pack_safe=icon_pack_safe), 
         participant=TunableParticipantTypeIconFactory(default_participant_type=default_participant_type), 
         privacy=TunablePrivacyIconFactory(), 
         tradition=TunableHolidayIconFactory(), 
         lifestyle_brand=TunableLifestyleBrandIconFactory(), 
         career_icon_override=TunableCareerIconOverrideIconFactory(), 
         default=default, **kwargs)