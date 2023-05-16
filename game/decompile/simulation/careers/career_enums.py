# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\career_enums.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 5193 bytes
import enum

class CareerCategory(enum.Int):
    Invalid = 0
    Work = 1
    School = 2
    TeenPartTime = 3
    Volunteer = 4
    AdultPartTime = 5
    UniversityCourse = 6
    TeenSideHustle = 7


def get_selector_type_from_career_category(career_ref):
    career_category = career_ref.career_category
    if career_category == CareerCategory.Work:
        if career_ref.is_active:
            return CareerSelectorTypes.ACTIVE
        return CareerSelectorTypes.WORK
    if career_category == CareerCategory.Volunteer:
        return CareerSelectorTypes.VOLUNTEER
    if career_category == CareerCategory.AdultPartTime:
        return CareerSelectorTypes.ADULT_PARTTIME
    return CareerSelectorTypes.WORK


class CareerSelectorTypes(enum.Int):
    ALL = 0
    ACTIVE = 1
    WORK = 2
    VOLUNTEER = 3
    ADULT_PARTTIME = 4


class CareerPanelType(enum.Int):
    NORMAL_CAREER = 0
    AGENT_BASED_CAREER = 1
    FREELANCE_CAREER = 2
    ODD_JOB_CAREER = 3
    UNIVERSITY_COURSE = 4
    MISSIONS_CAREER = 5
    PARANORMAL_INVESTIGATOR_CAREER = 6
    ACTIVE_GIG_BASED_CAREER = 7
    QUEST_CAREER = 8


WORK_CAREER_CATEGORIES = (
 CareerCategory.Work, CareerCategory.TeenPartTime, CareerCategory.TeenSideHustle,
 CareerCategory.AdultPartTime)
WORK_PART_TIME_CAREER_CATEGORIES = (
 CareerCategory.AdultPartTime, CareerCategory.TeenPartTime, CareerCategory.TeenSideHustle, CareerCategory.Volunteer)

class GigResult(enum.Int):
    GREAT_SUCCESS = 0
    SUCCESS = 1
    FAILURE = 2
    CRITICAL_FAILURE = 3
    CANCELED = 4

    def within_range(self, min_result, max_result):
        return min_result >= self >= max_result


class CareerOutfitGenerationType(enum.Int):
    CAREER_TUNING = 0
    ZONE_DIRECTOR = 1


class CareerShiftType(enum.Int):
    ALL_DAY = 0
    MORNING = 1
    EVENING = 2


class ReceiveDailyHomeworkHelp(enum.Int):
    UNCHECKED = 0
    CHECKED_RECEIVE_HELP = 1
    CHECKED_NO_HELP = 2


class CareerEventDeclineOptions(enum.Int):
    CAREER_RABBITHOLE = 0
    CANCEL_CURRENT_GIG = 1
    DO_NOTHING = 2


class DecoratorGigType(enum.Int):
    ROOM_RENOVATION = 1
    ROOM_ADDITION = 2
    LEVEL_RENOVATION = 3
    LEVEL_ADDITION = 4


class DecoratorGigLotType(enum.Int):
    RESIDENTIAL = 1
    COMMERCIAL = 2


class TestEventCareersOrigin(enum.Int):
    UNSPECIFIED = 0
    JOIN_CAREER = 1
    REMOVE_CAREER = 2
    NEW_CAREER_TRACK = 3
    CHANGE_CAREER_LEVEL_IN_TRACK = 4
    PROMOTION = 5
    QUIT_CAREER = 6
    FIRED = 7
    LAY_OFF = 8
    DEATH = 9
    RETIRE_CAREER = 10
    INVALID_SIM_CAREER = 11