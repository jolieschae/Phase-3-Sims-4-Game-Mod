# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_action_fame.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 3608 bytes
from collections import Counter
from fame.fame_tuning import FameTunables
from sims.sim_info_lod import SimInfoLODLevel
from sims4.tuning.tunable import TunableTuple
from story_progression.story_progression_action import _StoryProgressionAction
from tunable_time import TunableTimeOfDay
import services, sims4.telemetry, telemetry_helper
TELEMETRY_GROUP_STORY_PROGRESSION = 'STRY'
TELEMETRY_HOOK_FAME = 'FAME'
TELEMETRY_FIELD_FAME_PLAYED = 'fmpl'
TELEMETRY_FIELD_FAME_NON_PLAYED = 'fmnp'
TELEMETRY_FIELD_FAME_ONE_STAR_NON_PLAYED = 'fmn1'
TELEMETRY_FIELD_FAME_TWO_STAR_NON_PLAYED = 'fmn2'
TELEMETRY_FIELD_FAME_THREE_STAR_NON_PLAYED = 'fmn3'
TELEMETRY_FIELD_FAME_FOUR_STAR_NON_PLAYED = 'fmn4'
TELEMETRY_FIELD_FAME_FIVE_STAR_NON_PLAYED = 'fmn5'
fame_telemetry_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_STORY_PROGRESSION)

class StoryProgressionActionFame(_StoryProgressionAction):
    FACTORY_TUNABLES = {'time_of_day': TunableTuple(description='\n            Only run this action when it is between a certain time of day.\n            ',
                      start_time=TunableTimeOfDay(default_hour=2),
                      end_time=TunableTimeOfDay(default_hour=6))}

    def should_process(self, options):
        current_time = services.time_service().sim_now
        if not current_time.time_between_day_times(self.time_of_day.start_time, self.time_of_day.end_time):
            return False
        return True

    def process_action(self, story_progression_flags):
        if FameTunables.FAME_RANKED_STATISTIC is None:
            return
        played_famous = 0
        non_played_famous = 0
        non_played_fame_level = Counter()
        for sim_info in services.sim_info_manager().get_all():
            if sim_info.lod == SimInfoLODLevel.MINIMUM:
                continue
            fame_stat = sim_info.get_statistic((FameTunables.FAME_RANKED_STATISTIC), add=False)
            if not fame_stat:
                continue
            if fame_stat.rank_level >= 1:
                if sim_info.is_player_sim:
                    played_famous += 1
                else:
                    non_played_famous += 1
                    non_played_fame_level[fame_stat.rank_level] += 1

        with telemetry_helper.begin_hook(fame_telemetry_writer, TELEMETRY_HOOK_FAME) as (hook):
            hook.write_int(TELEMETRY_FIELD_FAME_PLAYED, played_famous)
            hook.write_int(TELEMETRY_FIELD_FAME_NON_PLAYED, non_played_famous)
            hook.write_int(TELEMETRY_FIELD_FAME_ONE_STAR_NON_PLAYED, non_played_fame_level[1])
            hook.write_int(TELEMETRY_FIELD_FAME_TWO_STAR_NON_PLAYED, non_played_fame_level[2])
            hook.write_int(TELEMETRY_FIELD_FAME_THREE_STAR_NON_PLAYED, non_played_fame_level[3])
            hook.write_int(TELEMETRY_FIELD_FAME_FOUR_STAR_NON_PLAYED, non_played_fame_level[4])
            hook.write_int(TELEMETRY_FIELD_FAME_FIVE_STAR_NON_PLAYED, non_played_fame_level[5])