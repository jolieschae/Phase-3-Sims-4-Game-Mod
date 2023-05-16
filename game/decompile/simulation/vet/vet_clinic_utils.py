# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\vet\vet_clinic_utils.py
# Compiled at: 2017-10-04 15:28:54
# Size of source mod 2**32: 1644 bytes
from event_testing.resolver import SingleSimResolver
from vet.vet_clinic_tuning import VetClinicTuning, logger
import services

def get_vet_clinic_zone_director():
    venue_service = services.venue_service()
    return venue_service is None or venue_service.venue_is_type(VetClinicTuning.VET_CLINIC_VENUE) or None
    return venue_service.get_zone_director()


def get_bonus_payment(difficulty):
    for bonus_item in reversed(VetClinicTuning.DIFFICULTY_BONUS_PAYMENT):
        if bonus_item.threshold.compare(difficulty):
            return bonus_item.bonus_amount

    return 0


def get_value_of_service_buff(markup, vet_sim_info):
    resolver = SingleSimResolver(vet_sim_info)
    for markup_tests in reversed(VetClinicTuning.VALUE_OF_SERVICE_AWARDS):
        if markup_tests.markup_threshold.compare(markup):
            for skill_tests in reversed(markup_tests.skill_to_buffs):
                if resolver(skill_tests.skill_range):
                    return skill_tests.value_of_service_buff

    logger.error('Could not find an appropriate value of service buff for {}. Please verify there are no holes in VALUE_OF_SERVICE_AWARDS tuning', vet_sim_info)