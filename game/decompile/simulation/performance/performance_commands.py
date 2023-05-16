# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\performance\performance_commands.py
# Compiled at: 2022-08-26 18:13:12
# Size of source mod 2**32: 64377 bytes
from collections import Counter, namedtuple
from itertools import combinations
from gameplay_scenarios import scenario
from interactions.utils import loot_basic_op
from numbers import Number
import collections
from adaptive_clock_speed import AdaptiveClockSpeed
from clock import ClockSpeedMultiplierType, ClockSpeedMode
from gsi_handlers.performance_handlers import generate_statistics
from interactions.utils.death import DeathType
from relationships.global_relationship_tuning import RelationshipGlobalTuning
from relationships.relationship_enums import RelationshipBitCullingPrevention, RelationshipDecayMetricKeys, RelationshipDirection
from server_commands.autonomy_commands import show_queue, autonomy_distance_estimates_enable, autonomy_distance_estimates_dump
from server_commands.cache_commands import cache_status
from sims.household_telemetry import HouseholdRegionTelemetryData
from sims.occult.occult_enums import OccultType
from sims.sim_info import SimInfo
from sims.sim_info_lod import SimInfoLODLevel
from sims4.commands import CommandType
from sims4.profiler_utils import create_custom_named_profiler_function
from sims4.utils import create_csv
from statistics.base_statistic import BaseStatistic
from story_progression.story_progression_action_relationship_culling import StoryProgressionRelationshipCulling
from zone import freeze_game_time_in_pause
import autonomy.autonomy_util, enum, event_testing
import performance.performance_constants as consts
import services, sims4.commands, caches
CLIENT_STATE_OPS_TO_IGNORE = [
 'autonomy_modifiers']
RelationshipMetrics = namedtuple('RelationshipMetrics', ('rels', 'rels_active', 'rels_played',
                                                         'rels_unplayed', 'rel_bits_one_way',
                                                         'rel_bits_bi', 'rel_tracks',
                                                         'avg_meaningful_rels', 'played_sims_with_sentiments',
                                                         'rels_on_played_sims_with_sentiments',
                                                         'num_sentiments_on_player_sims',
                                                         'num_sims_with_sentiments',
                                                         'rels_with_sentiments',
                                                         'total_num_sentiments'))

@sims4.commands.Command('performance.log_alarms')
def log_alarms(enabled: bool=True, check_cooldown: bool=True, _connection=None):
    services.current_zone().alarm_service._log = enabled
    return True


@sims4.commands.Command('performance.log_object_statistics', command_type=(CommandType.Automation))
def log_object_statistics(outputFile=None, _connection=None):
    result = generate_statistics()
    if outputFile is not None:
        cheat_output = sims4.commands.FileOutput(outputFile, _connection)
    else:
        cheat_output = sims4.commands.CheatOutput(_connection)
    automation_output = sims4.commands.AutomationOutput(_connection)
    automation_output('PerfLogObjStats; Status:Begin')
    for name, value in result:
        eval_value = eval(value)
        if isinstance(eval_value, Number):
            automation_output('PerfLogObjStats; Status:Data, Name:{}, Value:{}'.format(name, value))
            cheat_output('{} : {}'.format(name, value))
        else:
            if isinstance(eval_value, (list, tuple)):
                automation_output('PerfLogObjStats; Status:ListBegin, Name:{}'.format(name))
                cheat_output('Name : {}'.format(name))
                for obj_freq in eval_value:
                    object_name = obj_freq.get('name')
                    frequency = obj_freq.get('frequency')
                    automation_output('PerfLogObjStats; Status:ListData, Name:{}, Frequency:{}'.format(object_name, frequency))
                    cheat_output('{} : {}'.format(object_name, frequency))

                automation_output('PerfLogObjStats; Status:ListEnd, Name:{}'.format(name))
        cheat_output('\n')

    automation_output('PerfLogObjStats; Status:End')


@sims4.commands.Command('performance.log_object_statistics_summary', command_type=(CommandType.Automation))
def log_object_statistics_summary(object_breakdown: bool=False, _connection=None):
    result = generate_statistics()
    nodes, edges = services.current_zone().posture_graph_service.get_nodes_and_edges()
    result.append((consts.POSTURE_GRAPH_NODES, nodes))
    result.append((consts.POSTURE_GRAPH_EDGES, edges))
    output = sims4.commands.CheatOutput(_connection)
    ignore = set([x for x in consts.OBJECT_CLASSIFICATIONS])
    ignore.add(consts.TICKS_PER_SECOND)
    ignore.add(consts.COUNT_PROPS)
    ignore.add(consts.COUNT_OBJECTS_PROPS)
    f = '{:50} : {:5} : {:5}'
    breakdown_key = {}
    if object_breakdown:
        breakdown_key[consts.OBJS_ACTIVE_LOT_INTERACTIVE] = (consts.OBJS_INTERACTIVE, consts.LOCATION_ACTIVE_LOT)
        breakdown_key[consts.OBJS_ACTIVE_LOT_DECORATIVE] = (consts.OBJS_DECORATIVE, consts.LOCATION_ACTIVE_LOT)
        breakdown_key[consts.OBJS_OPEN_STREET_INTERACTIVE] = (consts.OBJS_INTERACTIVE, consts.LOCATION_OPEN_STREET)
        breakdown_key[consts.OBJS_OPEN_STREET_DECORATIVE] = (consts.OBJS_DECORATIVE, consts.LOCATION_OPEN_STREET)
        f = '{:75} : {:5} : {:5}'
        d = '  {:73} : {:5}'
    output(f.format('Metric', 'Value', 'Budget'))
    if object_breakdown:
        output(d.format('Object Name', ''))
    for name, value in result:
        if name in ignore:
            continue
        budget = consts.BUDGETS.get(name, '')
        output(f.format(name, value, budget))
        if name not in breakdown_key:
            continue
        breakdown_name, location = breakdown_key[name]
        for detail_name, detail_result in result:
            if detail_name != breakdown_name:
                continue
            detail_result_dict_list = eval(detail_result)
            for detail in detail_result_dict_list:
                if detail.get(consts.FIELD_LOCATION) == location:
                    output(d.format(detail.get(consts.FIELD_NAME), detail.get(consts.FIELD_FREQUENCY)))

    output('\nDetailed info in GSI: Performance Metrics panel, |performance.log_object_statistics, |performance.posture_graph_summary, RedDwarf: World Coverage Report')


@sims4.commands.Command('performance.add_automation_profiling_marker', command_type=(CommandType.Automation))
def add_automation_profiling_marker(message: str='Unspecified', _connection=None):
    name_f = create_custom_named_profiler_function(message)
    return name_f((lambda: None))


class SortStyle(enum.Int, export=False):
    ALL = 0
    AVERAGE_TIME = 1
    TOTAL_TIME = 2
    COUNT = 3


@sims4.commands.Command('performance.test_profile.dump', command_type=(CommandType.Automation))
def dump_tests_profile(sort: SortStyle=SortStyle.ALL, _connection=None):
    create_profile_results(profile_name='test', profile=(event_testing.resolver.test_profile), sort=sort,
      _connection=_connection)


@sims4.commands.Command('performance.test_profile.dump_resolver', command_type=(CommandType.Automation))
def dump_test_resolver_profiles(_connection=None):
    TIME_MULTIPLIER = 1000

    def average_time(time, count):
        if time == 0 or count == 0:
            return 0
        return time * TIME_MULTIPLIER / count

    resolver_types = set()
    for test_name, test_metrics in event_testing.resolver.test_profile.items():
        resolver_types |= test_metrics.resolvers.keys()

    resolver_types = list(resolver_types)
    resolver_types.sort()

    def callback(file):
        file.write('Test,Count,AvgTime,ResolveTime,TestTime,{}\n'.format(','.join(('{}Count,{}'.format(x, x) for x in resolver_types))))
        for test_name, test_metrics in event_testing.resolver.test_profile.items():
            metrics = test_metrics.metrics
            file.write('{},{},{},{},{}'.format(test_name, metrics.count, average_time(metrics.get_total_time(), metrics.count), average_time(metrics.resolve_time, metrics.count), average_time(metrics.test_time, metrics.count)))
            for resolver_type in resolver_types:
                sub_metrics = test_metrics.resolvers.get(resolver_type)
                if sub_metrics is None:
                    file.write(',,')
                else:
                    count = sum((m.count for m in sub_metrics.values()))
                    resolve_time = sum((m.resolve_time for m in sub_metrics.values()))
                    file.write(',{},{}'.format(count, average_time(resolve_time, count)))

            file.write('\n')

    filename = 'test_resolver_profile'
    create_csv(filename, callback=callback, connection=_connection)


@sims4.commands.Command('performance.test_profile.enable', command_type=(CommandType.Automation))
def enable_test_profile(_connection=None):
    event_testing.resolver.test_profile = dict()
    output = sims4.commands.CheatOutput(_connection)
    output('Test profiling enabled. Dump the profile any time using performance.test_profile.dump')


@sims4.commands.Command('performance.test_profile.disable', command_type=(CommandType.Automation))
def disable_test_profile(_connection=None):
    event_testing.resolver.test_profile = None
    output = sims4.commands.CheatOutput(_connection)
    output('Test profiling disabled.')


@sims4.commands.Command('performance.test_profile.clear', command_type=(CommandType.Automation))
def clear_tests_profile(_connection=None):
    if event_testing.resolver.test_profile is not None:
        event_testing.resolver.test_profile.clear()
    output = sims4.commands.CheatOutput(_connection)
    output('Test profile metrics have been cleared.')


@sims4.commands.Command('performance.loot_profile.enable', command_type=(CommandType.Automation))
def enable_loot_profile(_connection=None):
    loot_basic_op.loot_profile = dict()
    output = sims4.commands.CheatOutput(_connection)
    output('Loot profiling enabled. Dump the profile any time using performance.loot_profile.dump')


@sims4.commands.Command('performance.loot_profile.disable', command_type=(CommandType.Automation))
def disable_loot_profile(_connection=None):
    loot_basic_op.loot_profile = None
    output = sims4.commands.CheatOutput(_connection)
    output('Loot profiling disabled.')


@sims4.commands.Command('performance.loot_profile.dump', command_type=(CommandType.Automation))
def dump_loots_profile(sort: SortStyle=SortStyle.ALL, _connection=None):
    create_profile_results(profile_name='loot', profile=(loot_basic_op.loot_profile), sort=sort,
      _connection=_connection,
      should_create_interaction_view=False)


@sims4.commands.Command('performance.scenario.enable', command_type=(CommandType.Automation))
def enable_scenario_profile(_connection=None):
    scenario.scenario_profiles = dict()
    output = sims4.commands.CheatOutput(_connection)
    output('Scenario profiling enabled. Dump the profile any time using performance.scenario.dump')
    freeze_game_time_in_pause(True)


@sims4.commands.Command('performance.scenario.disable', command_type=(CommandType.Automation))
def disable_scenario_profile(_connection=None):
    scenario.scenario_profiles = None
    output = sims4.commands.CheatOutput(_connection)
    output('Scenario profiling disabled.')


@sims4.commands.Command('performance.scenario.dump', command_type=(CommandType.Automation))
def dump_scenario_profile(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    if scenario.scenario_profiles is None:
        output('scenario profiling is currently disabled. Use |performance.scenario.enable')
        return
    if len(scenario.scenario_profiles) == 0:
        output('scenario profiling is currently enabled but has no records.')
        return
    profile = None

    def scenario_callback(file):
        file.write('Phase Name,Final Debt,Max Debt,10%,20%,30%,40%,50%,60%,70%,80%,90%\n')
        for test_name, test_metrics in profile.items():
            perf_percentage_list = test_metrics.perf_percentage_list
            if len(perf_percentage_list) != 0:
                file.write('{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(test_name, test_metrics.get_final_time(), perf_percentage_list[9], perf_percentage_list[8], perf_percentage_list[7], perf_percentage_list[6], perf_percentage_list[5], perf_percentage_list[4], perf_percentage_list[3], perf_percentage_list[2], perf_percentage_list[1], perf_percentage_list[0]))

    for scenario_name, scenario_profile in scenario.scenario_profiles.items():
        filename = 'scenario_profile_{}'.format(scenario_name)
        profile = scenario_profile
        create_csv(filename, callback=scenario_callback, connection=_connection)


def create_profile_results(profile_name, profile, sort: SortStyle=SortStyle.ALL, _connection=None, should_create_interaction_view=True, should_create_sim_resolver_view=True):
    output = sims4.commands.CheatOutput(_connection)
    if profile is None:
        output('{} profiling is currently disabled. Use |performance.{}_profile.enable'.format(profile_name, profile_name))
        return
        if len(profile) == 0:
            output('{} profiling is currently enabled but has no records.'.format(profile_name))
            return

        def get_sort_style(metric):
            if sort == SortStyle.AVERAGE_TIME:
                return metric.get_average_time()
            if sort == SortStyle.TOTAL_TIME:
                return metric.get_total_time()
            if sort == SortStyle.COUNT:
                return metric.count

        TIME_MULTIPLIER = 1000

        def test_callback(file):
            file.write('{},Count,AverageTime(ms),TotalTime(ms),Resolver,Key,Count,AverageTime(ms),TotalTime(ms),MaxTime(ms)\n'.format(profile_name))
            for test_name, test_metrics in sorted((profile.items()), key=(lambda t: get_sort_style(t[1].metrics)),
              reverse=True):
                file.write('{},{},{},{},,,,,\n'.format(test_name, test_metrics.metrics.count, test_metrics.metrics.get_average_time() * TIME_MULTIPLIER, test_metrics.metrics.get_total_time() * TIME_MULTIPLIER))
                for resolver in sorted(test_metrics.resolvers.keys()):
                    data = test_metrics.resolvers[resolver]
                    for key, metrics in sorted((data.items()), key=(lambda t: get_sort_style(t[1])), reverse=True):
                        if metrics.get_average_time() > 0:
                            file.write(',,,,{},{},{},{},{},{}\n'.format(resolver, key, metrics.count, metrics.get_average_time() * TIME_MULTIPLIER, metrics.get_total_time() * TIME_MULTIPLIER, metrics.get_max_time() * TIME_MULTIPLIER))

        def create_test_view(sort_style):
            if sort_style != SortStyle.ALL:
                filename = profile_name + '_profile_' + str(sort_style).replace('.', '_')
                create_csv(filename, callback=test_callback, connection=_connection)

        interactions = collections.defaultdict(list)

        def interaction_callback(file):
            file.write('Interaction,TotalTime(ms),Test,Count,AverageTime(ms),AverageResolveTime(ms),TotalTime(ms),MaxTime(ms)\n')
            for iname, tests in sorted((interactions.items()), reverse=True,
              key=(lambda t: sum((m.get_total_time(include_test_set=False) for _, m in t[1])))):
                file.write('{},{},,,,,\n'.format(iname, sum((m.get_total_time(include_test_set=False) for _, m in tests)) * TIME_MULTIPLIER))
                for test, met in sorted(tests, reverse=True,
                  key=(lambda t: (
                 not t[1].is_test_set, t[1].get_total_time()))):
                    file.write(',,{},{},{},{},{},{}\n'.format(test, met.count, met.get_average_time() * TIME_MULTIPLIER, met.resolve_time * TIME_MULTIPLIER / met.count, met.get_total_time() * TIME_MULTIPLIER, met.get_max_time() * TIME_MULTIPLIER))

        def create_interaction_view():
            for tname, tmetrics in profile.items():
                interaction_resolver = tmetrics.resolvers.get('InteractionResolver')
                if interaction_resolver is None:
                    continue
                for interaction, metrics in interaction_resolver.items():
                    interactions[interaction].append((tname, metrics))

            filename = '{}_profile_interactions'.format(profile_name)
            create_csv(filename, callback=interaction_callback, connection=_connection)

        sim_resolvers = collections.defaultdict(list)

        def sim_resolver_callback(file):
            file.write('ResolverInfo,TotalTime(ms),Test,Count,AverageTime(ms),TotalTime(ms),MaxTime(ms)\n')
            for rname, tests in sorted((sim_resolvers.items()), reverse=True, key=(lambda t: sum((m.get_total_time(include_test_set=False) for _, m in t[1])))):
                file.write('{},{},,,,\n'.format(rname, sum((m.get_total_time(include_test_set=False) for _, m in tests)) * TIME_MULTIPLIER))
                for test, met in sorted(tests, reverse=True,
                  key=(lambda t: (
                 not t[1].is_test_set, t[1].get_total_time()))):
                    file.write(',,{},{},{},{},{}\n'.format(test, met.count, met.get_average_time() * TIME_MULTIPLIER, met.get_total_time() * TIME_MULTIPLIER, met.get_max_time() * TIME_MULTIPLIER))

        def create_sim_resolver_view():
            for tname, tmetrics in profile.items():
                datum_prefix = 'SingleSimResolver:'
                sim_resolver = tmetrics.resolvers.get('SingleSimResolver')
                if sim_resolver is None:
                    datum_prefix = 'DoubleSimResolver:'
                    sim_resolver = tmetrics.resolvers.get('DoubleSimResolver')
                if sim_resolver is None:
                    continue
                for resolver_datum, metrics in sim_resolver.items():
                    sim_resolvers[datum_prefix + resolver_datum].append((tname, metrics))

            filename = '{}_profile_sim_resolvers'.format(profile_name)
            create_csv(filename, callback=sim_resolver_callback, connection=_connection)

        if sort == SortStyle.ALL:
            for sort in SortStyle.values:
                create_test_view(sort)

    else:
        create_test_view(sort)
    if should_create_interaction_view:
        create_interaction_view()
    if should_create_sim_resolver_view:
        create_sim_resolver_view()


@sims4.commands.Command('performance.loot_profile.clear', command_type=(CommandType.Automation))
def clear_loots_profile(_connection=None):
    if loot_basic_op.loot_profile is not None:
        loot_basic_op.loot_profile.clear()
    output = sims4.commands.CheatOutput(_connection)
    output('Loot profile metrics have been cleared.')


@sims4.commands.Command('performance.print_player_household_metrics', command_type=(CommandType.Automation))
def player_household_metrics(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    active_sim_count, player_sim_count, played_sim_count = (0, 0, 0)
    active_household_count, player_household_count, played_household_count = (0, 0,
                                                                              0)
    households = services.household_manager().get_all()
    for household in households:
        if household.is_active_household:
            active_household_count += 1
            active_sim_count += len(household)
        if household.is_player_household:
            player_household_count += 1
            player_sim_count += len(household)
        if household.is_played_household:
            played_household_count += 1
            played_sim_count += len(household)

    for name, value in (('#sim_infos', len(services.sim_info_manager())), ('#active sim_infos', active_sim_count),
     (
      '#player sim_infos', player_sim_count),
     (
      '#played sim_infos', played_sim_count),
     (
      '#households', len(households)),
     (
      '#active households', active_household_count),
     (
      '#player households', player_household_count),
     (
      '#played households', played_household_count)):
        output('{:50} : {}'.format(name, value))

    return True


def get_relationship_decay_metrics(output=None):
    total_relationships = 0
    metrics = collections.defaultdict(Counter)
    for x, y in combinations(services.sim_info_manager().values(), 2):
        x_y = x.relationship_tracker.relationship_decay_metrics(y.id)
        y_x = y.relationship_tracker.relationship_decay_metrics(x.id)
        decay_metrics = x_y if x_y is not None else y_x
        if decay_metrics is not None:
            active_counter = None
            total_relationships += 1
            if x.is_npc:
                active_counter = y.is_npc or metrics['active']
            elif x.is_played_sim or y.is_played_sim:
                active_counter = metrics['played']
            else:
                active_counter = metrics['unplayed']
            if active_counter is None:
                continue
            active_counter += decay_metrics
            active_counter[RelationshipDecayMetricKeys.RELS] += 1
            long_term_tracks_decaying = decay_metrics[RelationshipDecayMetricKeys.LONG_TERM_TRACKS_DECAYING]
            if long_term_tracks_decaying > 0:
                active_counter[RelationshipDecayMetricKeys.RELS_WITH_DECAY] += 1

    return (
     total_relationships, metrics)


@sims4.commands.Command('performance.relationship_decay_metrics')
def print_relationship_decay_metrics(long_version: bool=False, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    total_tracks, metrics = get_relationship_decay_metrics(output=output)
    output('TOTAL_RELS = {:10}'.format(total_tracks))
    for status, metric in metrics.items():
        long_term_tracks = metric[RelationshipDecayMetricKeys.LONG_TERM_TRACKS]
        short_term_tracks = metric[RelationshipDecayMetricKeys.LONG_TERM_TRACKS]
        long_term_tracks_decaying = metric[RelationshipDecayMetricKeys.LONG_TERM_TRACKS_DECAYING]
        short_term_tracks_decaying = metric[RelationshipDecayMetricKeys.SHORT_TERM_TRACKS_DECAYING]
        long_term_tracks_decaying_at_convergence = metric[RelationshipDecayMetricKeys.LONG_TERM_TRACKS_AT_CONVERGENCE]
        short_term_tracks_decaying_at_convergence = metric[RelationshipDecayMetricKeys.SHORT_TERM_TRACKS_AT_CONVERGENCE]
        if not long_version:
            output('{:30} : {:5} : #decaying:{:4}: #tracks:{:4} : #tracks_decaying:{:4} : #tracks_at_convergence:{:4}'.format(str(status), metric[RelationshipDecayMetricKeys.RELS], metric[RelationshipDecayMetricKeys.RELS_WITH_DECAY], long_term_tracks + short_term_tracks, long_term_tracks_decaying + short_term_tracks_decaying, long_term_tracks_decaying_at_convergence + short_term_tracks_decaying_at_convergence))
            continue
        output('{:30} : {:5} : #decaying:{:4}: #tracks:{:4} : #tracks_decaying:{:4} : #tracks_at_convergence:{:4}: #long_term:{:4} : #long_term_decaying:{:4} : #long_term_at_convergence:{:4}: #short_term:{:4} : #short_term_decaying:{:4} : #short_term_at_convergence:{:4}'.format(str(status), metric[RelationshipDecayMetricKeys.RELS], metric[RelationshipDecayMetricKeys.RELS_WITH_DECAY], long_term_tracks + short_term_tracks, long_term_tracks_decaying + short_term_tracks_decaying, long_term_tracks_decaying_at_convergence + short_term_tracks_decaying_at_convergence, long_term_tracks, long_term_tracks_decaying, long_term_tracks_decaying_at_convergence, short_term_tracks, short_term_tracks_decaying, short_term_tracks_decaying_at_convergence))

    return metrics


@sims4.commands.Command('performance.relationship_object_per_sim')
def dump_relationship_object_information_per_sim(_connection=None):

    def callback(file):
        entries = []
        active_rel_objs = 0
        playable_rel_objs = 0
        unplayed_rel_obj = 0
        one_way_rel_obj = 0
        for x in services.sim_info_manager().values():
            total_rels = 0
            household_rels = 0
            rels_can_be_culled = 0
            rels_decaying = 0
            rels_target_unplayable = 0
            family_rels = 0
            rels_with_no_long_term_tracks = 0
            rels_target_playable = 0
            rels_target_active = 0
            for relationship in x.relationship_tracker:
                total_rels += 1
                decay_information = x.relationship_tracker.relationship_decay_metrics(relationship.get_other_sim_id(x.sim_id))
                if decay_information is not None:
                    decay_enabled, _, possible_tracks_decaying, _ = decay_information
                    if decay_enabled:
                        rels_decaying += 1
                    else:
                        if possible_tracks_decaying == 0:
                            rels_with_no_long_term_tracks += 1
                        else:
                            target_sim_info = relationship.get_other_sim_info(x.sim_id)
                            if target_sim_info is not None:
                                if target_sim_info.household_id == x.household_id:
                                    household_rels += 1
                                else:
                                    if any((bit.relationship_culling_prevention == RelationshipBitCullingPrevention.PLAYED_AND_UNPLAYED for bit in relationship._bits.values())):
                                        family_rels += 1
                                    else:
                                        rels_can_be_culled += 1
                                if not target_sim_info.is_npc:
                                    rels_target_active += 1
                                else:
                                    if target_sim_info.is_played_sim:
                                        rels_target_playable += 1
                                    else:
                                        rels_target_unplayable += 1
                                x.is_npc and target_sim_info.is_npc or active_rel_objs += 1
                            else:
                                if x.is_played_sim or target_sim_info.is_played_sim:
                                    playable_rel_objs += 1
                                else:
                                    unplayed_rel_obj += 1
                else:
                    one_way_rel_obj += 1

            entries.append('a{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(x.id, x.first_name, x.last_name, total_rels, rels_can_be_culled, household_rels, family_rels, rels_target_active, rels_target_playable, rels_target_unplayable, rels_decaying, rels_with_no_long_term_tracks))

        total_rel_objects = active_rel_objs + playable_rel_objs + unplayed_rel_obj + one_way_rel_obj
        file.write('Metrics\n')
        file.write('#relationship python objs:,{}\n'.format(total_rel_objects))
        file.write('#relationships one way objects:,{}\n'.format(one_way_rel_obj))
        file.write('#relationships active objects:,{}\n'.format(active_rel_objs))
        file.write('#relationships played objects:,{}\n'.format(playable_rel_objs))
        file.write('#relationships unplayed objects:,{}\n\n'.format(unplayed_rel_obj))
        file.write('SimID,FirstName,LastName,Played,RelationshipObjects,#Cullable,HouseholdConnected,BitPreventingCulling,WithActive,WithPlayable,WithUnplayayble,#Decaying,#NoLongTermTracks\n')
        for row_entry in entries:
            file.write(row_entry)

    create_csv('relationship_objects_per_sim', callback=callback, connection=_connection)


def get_relationship_metrics(output=None):
    rels = 0
    rels_active = 0
    rels_played = 0
    rels_unplayed = 0
    rel_bits_one_way = 0
    rel_bits_bi = 0
    rel_tracks = 0
    meaningful_rels = collections.defaultdict(int)
    played_sims_with_sentiments = set()
    rels_on_played_sims_with_sentiments = 0
    num_sentiments_on_player_sims = 0
    sims_with_sentiments = set()
    rels_with_sentiments = 0
    total_num_sentiments = 0
    rel_service = services.relationship_service()
    for relationship in rel_service:
        x = relationship.find_sim_info_a()
        x_id = x.sim_id
        y = relationship.find_sim_info_b()
        y_id = y.sim_id
        x_bits = set(relationship.get_bits(x_id))
        y_bits = set(relationship.get_bits(y_id))
        rel_bits_bi += sum((1 for bit in x_bits if bit.directionality == RelationshipDirection.BIDIRECTIONAL))
        rel_bits_one_way += sum((1 for bit in x_bits if bit.directionality == RelationshipDirection.UNIDIRECTIONAL)) + sum((1 for bit in y_bits if bit.directionality == RelationshipDirection.UNIDIRECTIONAL))
        rel_tracks += len(relationship.relationship_track_tracker)
        x_sentiment_count = len(relationship.sentiment_track_tracker(x_id))
        y_sentiment_count = len(relationship.sentiment_track_tracker(y_id))
        if not x_sentiment_count > 0:
            if y_sentiment_count > 0:
                if x_sentiment_count > 0:
                    rel_tracks += x_sentiment_count
                    total_num_sentiments += x_sentiment_count
                    sims_with_sentiments.add(x_id)
                    if x.is_played_sim:
                        played_sims_with_sentiments.add(x_id)
                        num_sentiments_on_player_sims += x_sentiment_count
                if y_sentiment_count > 0:
                    rel_tracks += y_sentiment_count
                    total_num_sentiments += y_sentiment_count
                    sims_with_sentiments.add(y_id)
                    if y.is_played_sim:
                        played_sims_with_sentiments.add(y_id)
                        num_sentiments_on_player_sims += y_sentiment_count
                if x.is_played_sim or y.is_played_sim:
                    rels_on_played_sims_with_sentiments += 1
                rels_with_sentiments += 1
            rels += 1
            x.is_npc and y.is_npc or rels_active += 1
            if not x.is_npc:
                if RelationshipGlobalTuning.MEANINGFUL_RELATIONSHIP_BITS & x_bits:
                    meaningful_rels[x_id] += 1
            if not y.is_npc:
                if RelationshipGlobalTuning.MEANINGFUL_RELATIONSHIP_BITS & y_bits:
                    meaningful_rels[y_id] += 1
                elif x.is_played_sim or y.is_played_sim:
                    rels_played += 1
                    if x.is_played_sim:
                        if RelationshipGlobalTuning.MEANINGFUL_RELATIONSHIP_BITS & x_bits:
                            meaningful_rels[x_id] += 1
                elif y.is_played_sim:
                    if RelationshipGlobalTuning.MEANINGFUL_RELATIONSHIP_BITS & y_bits:
                        meaningful_rels[y_id] += 1
                    else:
                        rels_unplayed += 1

    avg_meaningful_rels = sum(meaningful_rels.values()) / float(len(meaningful_rels)) if meaningful_rels else 0
    num_player_sims_with_sentiments = len(played_sims_with_sentiments)
    num_sims_with_sentiments = len(sims_with_sentiments)
    return RelationshipMetrics(rels, rels_active, rels_played, rels_unplayed, rel_bits_one_way, rel_bits_bi, rel_tracks, avg_meaningful_rels, num_player_sims_with_sentiments, rels_on_played_sims_with_sentiments, num_sentiments_on_player_sims, num_sims_with_sentiments, rels_with_sentiments, total_num_sentiments)


@sims4.commands.Command('performance.relationship_status', command_type=(CommandType.Automation))
def relationship_status(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    metrics = get_relationship_metrics(output=output)
    dump = []
    dump.append(('#relationships', metrics.rels))
    dump.append(('#relationships active sims', metrics.rels_active))
    dump.append(('#relationships played sims', metrics.rels_played))
    dump.append(('#relationships unplayed sims', metrics.rels_unplayed))
    dump.append(('#relationships rel bits one-way', metrics.rel_bits_one_way))
    dump.append(('#relationships rel bits bi-directional', metrics.rel_bits_bi))
    dump.append(('#relationships rel tracks', metrics.rel_tracks))
    dump.append(('#average meaningful rels', metrics.avg_meaningful_rels))
    for name, value in dump:
        output('{:40} : {}'.format(name, value))

    return dump


def get_sim_info_creation_sources():
    counter = Counter()
    for sim_info in services.sim_info_manager().values():
        counter[str(sim_info.creation_source)] += 1

    return counter


@sims4.commands.Command('performance.print_sim_info_creation_sources', command_type=(CommandType.Automation))
def print_sim_info_creation_sources(_connection=None):
    counter = get_sim_info_creation_sources()
    output = sims4.commands.CheatOutput(_connection)
    automation_output = sims4.commands.AutomationOutput(_connection)
    output('Total sim_infos: {}'.format(sum(counter.values())))
    output('--------------------')
    automation_output('SimInfoPerformance; Status:Begin, TotalSimInfos:{}'.format(sum(counter.values())))
    for source, count in counter.most_common():
        automation_source = source
        if source == '':
            source = 'Unknown - Is empty string'
            automation_source = 'Unknown'
        output('{:100} : {}'.format(source, count))
        if ': ' in automation_source:
            automation_source = automation_source.replace(': ', '(') + ')'
        automation_output('SimInfoPerformance; Status:Data, Source:{}, Count:{}'.format(automation_source, count))

    automation_output('SimInfoPerformance; Status:End')
    return counter


@sims4.commands.Command('performance.print_census_report', command_type=(CommandType.Automation))
def print_census_report(_connection=None):
    age = Counter()
    gender = Counter()
    ghost = Counter()
    occult = Counter()
    lod = Counter()
    sim_types = Counter()
    household_types = Counter()
    output = sims4.commands.CheatOutput(_connection)
    for sim_info in services.sim_info_manager().values():
        age[sim_info.age] += 1
        gender[sim_info.gender] += 1
        if sim_info.is_ghost:
            death_type = sim_info.death_tracker._death_type
            if death_type is not None:
                ghost[DeathType(death_type)] += 1
            else:
                output('{} is a ghost with no death_type.'.format(sim_info))
        for ot in OccultType:
            if sim_info.occult_types & ot:
                occult[ot] += 1

        lod[sim_info.lod] += 1

    for household in services.household_manager().values():
        if household.is_active_household:
            household_types['active'] += 1
            sim_types['active'] += len(household)
        elif household.is_player_household:
            household_types['player'] += 1
            sim_types['player'] += len(household)
        else:
            household_types['unplayed'] += 1
            sim_types['unplayed'] += len(household)

    formatting = '{:14} : {:^10} : {}'
    output(formatting.format('Classification', 'Total', 'Histogram'))

    def _print(classification, counter):
        output(formatting.format(classification, sum(counter.values()), counter.most_common()))

    result = []
    result.append(('Households', household_types))
    result.append(('Sims', sim_types))
    result.append(('LOD', lod))
    result.append(('Age', age))
    result.append(('Gender', gender))
    result.append(('Occult', occult))
    result.append(('Ghost', ghost))
    for name, counter in result:
        _print(name, counter)

    return result


@sims4.commands.Command('performance.clock_status', command_type=(CommandType.Automation))
def clock_status(_connection=None):
    stats = []
    game_clock = services.game_clock_service()
    clock_speed = ClockSpeedMode(game_clock.clock_speed)
    deviance, threshold, current_duration, duration = AdaptiveClockSpeed.get_debugging_metrics()
    output = sims4.commands.CheatOutput(_connection)
    stats.append(('Clock Speed',
     clock_speed,
     '(Current player-facing clock speed)'))
    stats.append(('Speed Multiplier Type',
     ClockSpeedMultiplierType(game_clock.clock_speed_multiplier_type),
     '(Decides the speed 2/3/SS3 multipliers for adaptive speed)'))
    stats.append(('Clock Speed Multiplier',
     game_clock.current_clock_speed_scale(),
     '(Current Speed scaled with appropriate speed settings)'))
    stats.append(('Simulation Deviance',
     '{:>7} / {:<7}'.format(deviance, threshold),
     '(Simulation clock deviance from time service clock / Tuning Threshold [units: ticks])'))
    stats.append(('Deviance Duration',
     '{:>7} / {:<7}'.format(str(current_duration), duration),
     '(Current duration in multiplier phase / Tuning Duration [units: ticks])'))
    for name, value, description in stats:
        output('{:25} {!s:40} {}'.format(name, value, description))

    sims4.commands.automation_output('Performance; ClockSpeed:{}'.format(clock_speed), _connection)


@sims4.commands.Command('performance.status', command_type=(CommandType.Automation))
def status(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output('==Clock==')
    clock_status(_connection=_connection)
    output('==AutonomyQueue==')
    show_queue(_connection=_connection)
    output('==ACC&BCC==')
    cache_status(_connection=_connection)


@sims4.commands.Command('performance.trigger_sim_info_firemeter', command_type=(CommandType.Automation))
def trigger_sim_info_firemeter--- This code section failed: ---

 L. 965         0  LOAD_GLOBAL              sims4
                2  LOAD_ATTR                commands
                4  LOAD_METHOD              CheatOutput
                6  LOAD_FAST                '_connection'
                8  CALL_METHOD_1         1  '1 positional argument'
               10  STORE_FAST               'output'

 L. 966        12  LOAD_GLOBAL              services
               14  LOAD_METHOD              sim_info_manager
               16  CALL_METHOD_0         0  '0 positional arguments'
               18  STORE_DEREF              'sim_info_manager'

 L. 967        20  LOAD_CLOSURE             'sim_info_manager'
               22  BUILD_TUPLE_1         1 
               24  LOAD_DICTCOMP            '<code_object <dictcomp>>'
               26  LOAD_STR                 'trigger_sim_info_firemeter.<locals>.<dictcomp>'
               28  MAKE_FUNCTION_8          'closure'
               30  LOAD_GLOBAL              SimInfoLODLevel
               32  GET_ITER         
               34  CALL_FUNCTION_1       1  '1 positional argument'
               36  STORE_FAST               'lod_counts'

 L. 968        38  LOAD_DEREF               'sim_info_manager'
               40  LOAD_METHOD              trigger_firemeter
               42  CALL_METHOD_0         0  '0 positional arguments'
               44  POP_TOP          

 L. 970        46  LOAD_FAST                'output'
               48  LOAD_STR                 'LOD counts Before/After firemeter:'
               50  CALL_FUNCTION_1       1  '1 positional argument'
               52  POP_TOP          

 L. 971        54  SETUP_LOOP          102  'to 102'
               56  LOAD_GLOBAL              SimInfoLODLevel
               58  GET_ITER         
               60  FOR_ITER            100  'to 100'
               62  STORE_FAST               'lod'

 L. 972        64  LOAD_DEREF               'sim_info_manager'
               66  LOAD_METHOD              get_num_sim_infos_with_lod
               68  LOAD_FAST                'lod'
               70  CALL_METHOD_1         1  '1 positional argument'
               72  STORE_FAST               'new_count'

 L. 973        74  LOAD_FAST                'output'
               76  LOAD_STR                 '{}: {} -> {}'
               78  LOAD_METHOD              format
               80  LOAD_FAST                'lod'
               82  LOAD_ATTR                name
               84  LOAD_FAST                'lod_counts'
               86  LOAD_FAST                'lod'
               88  BINARY_SUBSCR    
               90  LOAD_FAST                'new_count'
               92  CALL_METHOD_3         3  '3 positional arguments'
               94  CALL_FUNCTION_1       1  '1 positional argument'
               96  POP_TOP          
               98  JUMP_BACK            60  'to 60'
              100  POP_BLOCK        
            102_0  COME_FROM_LOOP       54  '54'

Parse error at or near `LOAD_DICTCOMP' instruction at offset 24


@sims4.commands.Command('performance.trigger_npc_relationship_culling', command_type=(CommandType.Automation))
def trigger_npc_relationship_culling(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output('Before relationship culling')
    relationship_status(_connection=_connection)
    StoryProgressionRelationshipCulling.trigger_npc_relationship_culling()
    output('After relationship culling')
    relationship_status(_connection=_connection)


@sims4.commands.Command('performance.posture_graph_summary', command_type=(CommandType.Automation))
def posture_graph_summary(outputFile=None, _connection=None):
    if outputFile is not None:
        output = sims4.commands.FileOutput(outputFile, _connection)
    else:
        output = sims4.commands.CheatOutput(_connection)
    services.current_zone().posture_graph_service.print_summary(output)
    sims4.commands.automation_output('PostureGraphSummary; Status:End', _connection)


@sims4.commands.Command('performance.sub_autonomy_tracking_start', 'autonomy.sub_autonomy_tracking_start', command_type=(sims4.commands.CommandType.Automation))
def record_autonomy_ping_data(_connection=None):
    autonomy.autonomy_util.record_autonomy_ping_data(services.time_service().sim_now)


@sims4.commands.Command('performance.sub_autonomy_tracking_print', 'autonomy.sub_autonomy_tracking_print', command_type=(sims4.commands.CommandType.Automation))
def print_sub_autonomy_output(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    autonomy.autonomy_util.print_sub_autonomy_ping_data(services.time_service().sim_now, output)


@sims4.commands.Command('performance.sub_autonomy_tracking_stop', 'autonomy.sub_autonomy_tracking_stop', command_type=(sims4.commands.CommandType.Automation))
def stop_recording_autonomy_ping_data(_connection=None):
    autonomy.autonomy_util.stop_sub_autonomy_ping_data()


@sims4.commands.Command('performance.autonomy_profile.enable', command_type=(CommandType.Automation))
def enable_autonomy_profiling_data(_connection=None):
    autonomy.autonomy_util.record_autonomy_profiling_data()
    output = sims4.commands.CheatOutput(_connection)
    output('Autonomy profiling enabled. Dump the profile any time using performance.autonomy_profile.dump')


@sims4.commands.Command('performance.autonomy_profile.disable', command_type=(CommandType.Automation))
def disable_autonomy_profiling_data(_connection=None):
    autonomy.autonomy_util.g_autonomy_profile_data = None
    output = sims4.commands.CheatOutput(_connection)
    output('Autonomy profiling disabled.')


@sims4.commands.Command('performance.autonomy_profile.clear', command_type=(CommandType.Automation))
def autonomy_autonomy_profiling_data_clear(_connection=None):
    if autonomy.autonomy_util.g_autonomy_profile_data is not None:
        autonomy.autonomy_util.g_autonomy_profile_data.reset_profiling_data()
    output = sims4.commands.CheatOutput(_connection)
    output('Autonomy profile metrics have been cleared.')


@sims4.commands.Command('performance.autonomy_profile.dump', command_type=(CommandType.Automation))
def dump_autonomy_profiling_data(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    if autonomy.autonomy_util.g_autonomy_profile_data is None:
        output('Autonomy profiling is currently disabled. Use |performance.autonomy_profile.enable')
        return
    if not autonomy.autonomy_util.g_autonomy_profile_data.autonomy_requests:
        output('Autonomy profiling is currently enabled but has no records.')
        return

    def callback(file):
        autonomy.autonomy_util.g_autonomy_profile_data.write_profiling_data_to_file(file)

    filename = 'autonomy_profile'
    create_csv(filename, callback=callback, connection=_connection)


@sims4.commands.Command('performance.send_household_region_telemetry', command_type=(CommandType.Automation))
def send_region_sim_info_telemetry(_connection=None):
    HouseholdRegionTelemetryData.send_household_region_telemetry()


def print_commodity_census(predicate=(lambda x: x), most_common=10, _connection=None):
    counter = collections.Counter()
    initial_counter = collections.Counter()
    commodity_counter = collections.Counter()
    commodity_initial_counter = collections.Counter()
    core_commodity_counter = collections.Counter()
    nonsim_stat_counter = collections.Counter()

    def compile_tracker(tracker, non_sim):
        try:
            for t in tracker:
                if not predicate(t):
                    continue
                stat_type = t.stat_type if hasattr(t, 'stat_type') else t
                counter[stat_type] += 1
                if hasattr(t, 'initial_value'):
                    if t.get_value() == t.initial_value:
                        initial_counter[stat_type] += 1
                if non_sim:
                    nonsim_stat_counter[stat_type] += 1

        except TypeError:
            pass

    def compile_obj_state_trackers(obj):
        if hasattr(obj, 'commodity_tracker'):
            if obj.commodity_tracker is not None:
                compile_tracker(obj.commodity_tracker, not obj.is_sim)
                for commodity in obj.commodity_tracker:
                    if not predicate(commodity):
                        continue
                    commodity_counter[commodity.stat_type] += 1
                    if hasattr(commodity, 'initial_value'):
                        if commodity.get_value() == commodity.initial_value:
                            commodity_initial_counter[commodity.stat_type] += 1
                    if commodity.core:
                        core_commodity_counter[commodity.stat_type] += 1

        if hasattr(obj, 'statistic_tracker'):
            if obj.statistic_tracker is not None:
                compile_tracker(obj.statistic_tracker, not obj.is_sim)

    for sim_info in services.sim_info_manager().values():
        for tracker_name in SimInfo.SIM_INFO_TRACKERS:
            tracker = getattr(sim_info, tracker_name)
            if tracker is None:
                continue
            compile_tracker(tracker, False)

        compile_obj_state_trackers(sim_info)

    for mgr in services.client_object_managers():
        for obj in mgr.get_all():
            if hasattr(obj, 'is_sim'):
                obj.is_sim or compile_obj_state_trackers(obj)

    dump = []
    num_statistics = sum(counter.values())
    num_statistics_initial = sum(initial_counter.values())
    dump.append(('Total count', num_statistics))
    dump.append(('Initial count', num_statistics_initial))
    dump.append(('Non-initial count', num_statistics - num_statistics_initial))
    num_commodities = sum(commodity_counter.values())
    num_commodities_initial = sum(commodity_initial_counter.values())
    dump.append(('Total commodities count', num_commodities))
    dump.append(('Initial commodities count', num_commodities_initial))
    dump.append(('Non-initial commodities count', num_commodities - num_commodities_initial))
    num_non_sim_commodities = sum(nonsim_stat_counter.values())
    dump.append(('Total non-sim commodities count', num_non_sim_commodities))
    num_core_commodities = sum(core_commodity_counter.values())
    dump.append(('Total core commodities count', num_core_commodities))
    output = sims4.commands.CheatOutput(_connection)
    for name, value in dump:
        output('{:35} : {}'.format(name, value))

    output('\nMost common:')
    for commodity, num in counter.most_common(most_common):
        name = commodity.__name__ if hasattr(commodity, '__name__') else str(commodity)
        output('{:50} : {}'.format(name, num))

    output('\nMost common core:')
    for commodity, num in core_commodity_counter.most_common(most_common):
        name = commodity.__name__ if hasattr(commodity, '__name__') else str(commodity)
        output('{:50} : {}'.format(name, num))

    output('\nMost common at initial value:')
    for commodity, num in initial_counter.most_common(most_common):
        name = commodity.__name__ if hasattr(commodity, '__name__') else str(commodity)
        output('{:50} : {}'.format(name, num))


def print_base_statistic_tuning(skill, _connection=None):
    lod_to_set_map = {}
    lod_to_persisted_count = {}
    for stat_type in services.get_instance_manager(sims4.resources.Types.STATISTIC).types.values():
        if not issubclass(stat_type, BaseStatistic):
            continue
        elif stat_type.is_skill != skill:
            continue
        else:
            if hasattr(stat_type, 'remove_on_convergence'):
                if stat_type.remove_on_convergence:
                    continue
            min_lod_value = stat_type.min_lod_value if hasattr(stat_type, 'min_lod_value') else None
            if min_lod_value not in lod_to_set_map:
                lod_to_set_map[min_lod_value] = set()
                lod_to_persisted_count[min_lod_value] = 0
            try:
                if stat_type.persisted:
                    name = '{} (p)'.format(stat_type.__name__)
                    lod_to_persisted_count[min_lod_value] += 1
                else:
                    name = stat_type.__name__
            except:
                name = stat_type.__name__

        lod_to_set_map[min_lod_value].add(name)

    output = sims4.commands.CheatOutput(_connection)
    output('Tuned {} Base Statistics'.format('Skill' if skill else 'Non-Skill'))
    for key, val in lod_to_set_map.items():
        output('{} : {} ({} persisted)'.format(key, len(val), lod_to_persisted_count[key]))
        for entry in sorted(list(val)):
            output('    {}'.format(entry))


@sims4.commands.Command('performance.analyze.global', command_type=(CommandType.Automation))
def analyze_global(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output('==Census==')
    print_census_report(_connection=_connection)
    output('==Relationships==')
    relationship_status(_connection=_connection)
    output('==Commodities==')
    commodity_status(_connection=_connection)
    output('==Environment==')
    log_object_statistics_summary(_connection=_connection)
    output('-==Object Score==-')
    from performance.object_score_commands import score_objects_in_world
    score_objects_in_world(verbose=False, _connection=_connection)


@sims4.commands.Command('performance.analyze.runtime.enable', command_type=(CommandType.Automation))
def analyze_begin(_connection=None):
    enable_test_profile(_connection=_connection)
    enable_loot_profile(_connection=_connection)
    autonomy_distance_estimates_enable(_connection=_connection)
    enable_test_cache(_connection=_connection)


@sims4.commands.Command('performance.analyze.runtime.dump', command_type=(CommandType.Automation))
def analyze_dump(_connection=None):
    dump_tests_profile(_connection=_connection)
    dump_loots_profile(_connection=_connection)
    dump_test_resolver_profiles(_connection=_connection)
    autonomy_distance_estimates_dump(_connection=_connection)


@sims4.commands.Command('performance.test_caches.dump', command_type=(CommandType.Automation))
def test_cache_dump(_connection=None):

    def callback(file):
        file.write('Function Key,Number of valid cached value missed')
        sorted_list = sorted((caches.cache_clear_misses.items()), key=(lambda x: x[1]), reverse=True)
        for function_key, cache_miss_number in sorted_list:
            file.write('\n {},{}'.format(str(function_key).replace(',', '_'), cache_miss_number))

    output = sims4.commands.CheatOutput(_connection)
    if caches.cache_clear_misses is None:
        output('Caches profiling is currently disabled. Use |performance.test_caches.enable')
        return
    if len(caches.cache_clear_misses) == 0:
        output('Caches profiling is currently enabled but has no records.')
        return
    create_csv('cache_profile', callback=callback, connection=_connection)


@sims4.commands.Command('performance.test_caches.enable', command_type=(CommandType.Automation))
def enable_test_cache(_connection=None):
    caches.cache_clear_misses = {}


@sims4.commands.Command('performance.test_caches.disable', command_type=(CommandType.Automation))
def disable_test_cache(_connection=None):
    test_cache_dump(_connection)
    caches.cache_clear_misses = None


@sims4.commands.Command('performance.commodity_status', command_type=(CommandType.Automation))
def commodity_status(most_common: int=10, include_tuning: bool=False, _connection=None):

    def predicate(commodity):
        return not (hasattr(commodity, 'is_skill') and commodity.is_skill)

    print_commodity_census(predicate=predicate, most_common=most_common, _connection=_connection)
    if include_tuning:
        print_base_statistic_tuning(skill=False, _connection=_connection)


@sims4.commands.Command('performance.skill_status', command_type=(CommandType.Automation))
def skill_status(most_common: int=10, include_tuning: bool=False, _connection=None):

    def predicate(commodity):
        return hasattr(commodity, 'is_skill') and commodity.is_skill

    print_commodity_census(predicate=predicate, most_common=most_common, _connection=_connection)
    if include_tuning:
        print_base_statistic_tuning(skill=True, _connection=_connection)