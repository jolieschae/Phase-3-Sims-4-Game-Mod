# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_telemetry.py
# Compiled at: 2022-03-10 20:35:10
# Size of source mod 2**32: 2381 bytes
import sims4, telemetry_helper
from story_progression import STORY_PROGRESSION_ARC_SEED_REASON_STRINGS
from story_progression.story_progression_enums import StoryType
from story_progression.story_progression_result import STORY_PROGRESSION_RESULT_TYPE_STRINGS
logger = sims4.log.Logger('StoryProgressionTelemetry', default_owner='bnguyen')
TELEMETRY_GROUP_STORY_PROGRESSION = 'STRY'
writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_STORY_PROGRESSION)
TELEMETRY_HOOK_CHAPTER_START = 'CHPT'
TELEMETRY_HOOK_ARC_COMPLETE = 'ENDD'
TELEMETRY_HOOK_DISCOVERY = 'NOTF'
TELEMETRY_FIELD_ARC_DEFINITION = 'stry'
TELEMETRY_FIELD_CHAPTER_DEFINITION = 'chpt'
TELEMETRY_FIELD_REASON = 'resn'

def send_chapter_start_telemetry(chapter, reason):
    reason_string = STORY_PROGRESSION_ARC_SEED_REASON_STRINGS.get(reason, 'ERROR')
    _send_telemetry_common(TELEMETRY_HOOK_CHAPTER_START, chapter, reason_string)


def send_arc_complete_telemetry(chapter, result_type):
    reason_string = STORY_PROGRESSION_RESULT_TYPE_STRINGS.get(result_type, 'ERROR')
    _send_telemetry_common(TELEMETRY_HOOK_ARC_COMPLETE, chapter, reason_string)


def send_chapter_discovered_telemetry(chapter):
    _send_telemetry_common(TELEMETRY_HOOK_DISCOVERY, chapter)


def _send_telemetry_common(hook_string, chapter, reason_string=None):
    arc = chapter.arc
    if arc.arc_type == StoryType.SIM_BASED:
        sim_info = arc.sim_info
        household = sim_info.household
    else:
        sim_info = None
        household = arc.household
    with telemetry_helper.begin_hook(writer, hook_string, sim_info=sim_info, household=household, valid_for_npc=True) as (hook):
        hook.write_int(TELEMETRY_FIELD_ARC_DEFINITION, arc.guid64)
        hook.write_int(TELEMETRY_FIELD_CHAPTER_DEFINITION, chapter.guid64)
        if reason_string is not None:
            hook.write_string(TELEMETRY_FIELD_REASON, reason_string)