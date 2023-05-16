# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\statistic_metrics_handlers.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 14353 bytes
import inspect, services
from gsi_handlers.gsi_utils import parse_filter_to_list
from objects import ALL_HIDDEN_REASONS
from objects.components.types import STATISTIC_COMPONENT
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
from statistics.commodity import Commodity
from statistics.life_skill_statistic import LifeSkillStatistic
from statistics.ranked_statistic import RankedStatistic
from statistics.skill import Skill
stat_metrics_schema = GsiGridSchema(label='Statistic Component Metrics', auto_refresh=False)
stat_metrics_schema.add_field('name', label='Name')
stat_metrics_schema.add_field('instanced', label='Instanced')
stat_metrics_schema.add_field('lod', label='LOD')
stat_metrics_schema.add_field('num_total_statistics', label='Total', type=(GsiFieldVisualizers.INT))
stat_metrics_schema.add_field('num_total_culled_statistics', label='Total Culled', type=(GsiFieldVisualizers.INT))
stat_metrics_schema.add_field('num_static_commodities', label='Static Commodity', type=(GsiFieldVisualizers.INT))
stat_metrics_schema.add_field('num_culled_static_commodities', label='Culled Static Commodity', type=(GsiFieldVisualizers.INT))
stat_metrics_schema.add_field('num_statistics', label='Statistic', type=(GsiFieldVisualizers.INT))
stat_metrics_schema.add_field('num_culled_statistics', label='Culled Statistic', type=(GsiFieldVisualizers.INT))
stat_metrics_schema.add_field('num_trait_statistics', label='TraitStatistic', type=(GsiFieldVisualizers.INT))
stat_metrics_schema.add_field('num_culled_trait_statistics', label='Culled TraitStatistic', type=(GsiFieldVisualizers.INT))
stat_metrics_schema.add_field('num_commodities', label='Commodity', type=(GsiFieldVisualizers.INT))
stat_metrics_schema.add_field('num_culled_commodities', label='Culled Commodity', type=(GsiFieldVisualizers.INT))
stat_metrics_schema.add_field('num_skills', label='Skill', type=(GsiFieldVisualizers.INT))
stat_metrics_schema.add_field('num_culled_skills', label='Culled Skill', type=(GsiFieldVisualizers.INT))
stat_metrics_schema.add_field('num_life_skill_statistics', label='LifeSkillStatistic', type=(GsiFieldVisualizers.INT))
stat_metrics_schema.add_field('num_culled_life_skill_statistics', label='Culled LifeSkillStatistic', type=(GsiFieldVisualizers.INT))
stat_metrics_schema.add_field('num_ranked_statistics', label='RankedStatistic', type=(GsiFieldVisualizers.INT))
stat_metrics_schema.add_field('num_culled_ranked_statistics', label='Culled RankedStatistic', type=(GsiFieldVisualizers.INT))
stat_metrics_schema.add_field('num_other_continuous', label='Other ContinuousStatistics', type=(GsiFieldVisualizers.INT))
stat_metrics_schema.add_field('num_culled_other_continuous', label='Other Culled ContinuousStatistics', type=(GsiFieldVisualizers.INT))

def populate_base_statistic_fields(statistic, dict, culled):
    stat_type = statistic if culled else type(statistic)
    dict['name'] = str(stat_type.__name__)
    dict['instance_required'] = 'N/A' if culled else statistic.instance_required
    dict['value'] = statistic.get_value()
    dict['default_value'] = statistic.default_value
    dict['statistic_modifier'] = 'N/A' if culled else statistic._statistic_modifier
    dict['culled'] = culled


def add_base_statistic_fields(sub_schema):
    sub_schema.add_field('name', label='Name', width=2)
    sub_schema.add_field('culled', label='culled')
    sub_schema.add_field('instance_required', label='Instance Required')
    sub_schema.add_field('value', label='value', type=(GsiFieldVisualizers.INT))
    sub_schema.add_field('default_value', label='default value')
    sub_schema.add_field('statistic_modifier', label='statistic modifier')


def populate_continuous_statistic_fields(statistic, dict, culled):
    dict['convergence_value'] = 'N/A' if culled else statistic.convergence_value
    dict['default_convergence_value'] = statistic.default_convergence_value
    dict['change_rate'] = 'N/A' if culled else statistic._get_change_rate_without_decay()
    dict['decay_rate'] = 'N/A' if culled else statistic.get_decay_rate()


def add_continuous_statistic_fields(sub_schema):
    sub_schema.add_field('convergence_value', label='convergence value')
    sub_schema.add_field('default_convergence_value', label='default convergence value')
    sub_schema.add_field('change_rate', label='change rate')
    sub_schema.add_field('decay_rate', label='decay rate')


with stat_metrics_schema.add_has_many('static_commodities', GsiGridSchema) as (sub_schema):
    add_base_statistic_fields(sub_schema)
with stat_metrics_schema.add_has_many('statistics', GsiGridSchema) as (sub_schema):
    add_base_statistic_fields(sub_schema)
with stat_metrics_schema.add_has_many('trait_statistics', GsiGridSchema) as (sub_schema):
    add_base_statistic_fields(sub_schema)
    add_continuous_statistic_fields(sub_schema)
with stat_metrics_schema.add_has_many('commodities', GsiGridSchema) as (sub_schema):
    add_base_statistic_fields(sub_schema)
    add_continuous_statistic_fields(sub_schema)
    sub_schema.add_field('core', label='core')
    sub_schema.add_field('visible', label='visible')
with stat_metrics_schema.add_has_many('skills', GsiGridSchema) as (sub_schema):
    add_base_statistic_fields(sub_schema)
    add_continuous_statistic_fields(sub_schema)
with stat_metrics_schema.add_has_many('life_skill_statistics', GsiGridSchema) as (sub_schema):
    add_base_statistic_fields(sub_schema)
    add_continuous_statistic_fields(sub_schema)
with stat_metrics_schema.add_has_many('ranked_statistics', GsiGridSchema) as (sub_schema):
    add_base_statistic_fields(sub_schema)
    add_continuous_statistic_fields(sub_schema)
with stat_metrics_schema.add_has_many('other_continuous', GsiGridSchema) as (sub_schema):
    add_base_statistic_fields(sub_schema)
    add_continuous_statistic_fields(sub_schema)
FILTER_INSTANCED_SIM_INFOS = 'instanced_sim_infos'
FILTER_ALL_SIM_INFOS = 'all_sim_infos'
FILTER_INSTANCED_OBJECTS = 'instanced_objects'
stat_metrics_schema.add_filter(FILTER_INSTANCED_SIM_INFOS)
stat_metrics_schema.add_filter(FILTER_ALL_SIM_INFOS)
stat_metrics_schema.add_filter(FILTER_INSTANCED_OBJECTS)

def populate_data_from_statistic_component(obj, data):
    statistic_component = obj.get_component(STATISTIC_COMPONENT)
    num_static_commodities = 0
    num_culled_static_commodities = 0
    static_commodities_data = []
    for static_commodity in statistic_component.get_static_commodity_tracker().all_statistics():
        culled = inspect.isclass(static_commodity)
        if culled:
            num_culled_static_commodities = num_culled_static_commodities + 1
        statistic_data = {}
        populate_base_statistic_fields(static_commodity, statistic_data, culled)
        num_static_commodities = num_static_commodities + 1
        static_commodities_data.append(statistic_data)

    data['num_static_commodities'] = num_static_commodities
    data['num_culled_static_commodities'] = num_culled_static_commodities
    data['static_commodities'] = static_commodities_data
    num_culled_statistics = 0
    num_statistics = 0
    statistics_data = []
    for statistic in statistic_component.get_statistic_tracker().all_statistics():
        culled = inspect.isclass(statistic)
        if culled:
            num_culled_statistics = num_culled_statistics + 1
        num_statistics = num_statistics + 1
        statistic_data = {}
        populate_base_statistic_fields(statistic, statistic_data, culled)
        statistics_data.append(statistic_data)

    data['num_statistics'] = num_statistics
    data['num_culled_statistics'] = num_culled_statistics
    data['statistics'] = statistics_data
    num_culled_trait_statistics = 0
    num_trait_statistics = 0
    trait_statistics_data = []
    for trait_statistic in statistic_component.get_trait_statistic_tracker().all_statistics():
        culled = inspect.isclass(trait_statistic)
        if culled:
            num_culled_trait_statistics = num_culled_trait_statistics + 1
        num_trait_statistics = num_trait_statistics + 1
        statistic_data = {}
        populate_base_statistic_fields(trait_statistic, statistic_data, culled)
        trait_statistics_data.append(statistic_data)

    data['num_trait_statistics'] = num_trait_statistics
    data['num_culled_trait_statistics'] = num_culled_trait_statistics
    data['trait_statistics'] = trait_statistics_data
    num_commodities = 0
    num_culled_commodities = 0
    num_skills = 0
    num_culled_skills = 0
    num_life_skills = 0
    num_culled_life_skills = 0
    num_ranked_statistics = 0
    num_culled_ranked_statistics = 0
    num_other_continuous = 0
    num_culled_other_continuous = 0
    commodities_data = []
    skills_data = []
    life_skills_data = []
    ranked_statistics = []
    other_continuous_statistic_data = []
    for continuous_stat in statistic_component.get_commodity_tracker().all_statistics():
        culled = inspect.isclass(continuous_stat)
        stat_type = continuous_stat if culled else type(continuous_stat)
        statistic_data = {}
        populate_base_statistic_fields(continuous_stat, statistic_data, culled)
        populate_continuous_statistic_fields(continuous_stat, statistic_data, culled)
        if issubclass(stat_type, Commodity):
            num_commodities = num_commodities + 1
            if culled:
                num_culled_commodities = num_culled_commodities + 1
            statistic_data['core'] = 'N/A' if culled else continuous_stat.core
            statistic_data['visible'] = 'N/A' if culled else continuous_stat.is_visible_commodity()
            commodities_data.append(statistic_data)
        elif issubclass(stat_type, Skill):
            num_skills = num_skills + 1
            if culled:
                num_culled_skills = num_culled_skills + 1
            skills_data.append(statistic_data)
        elif issubclass(stat_type, LifeSkillStatistic):
            num_life_skills = num_life_skills + 1
            if culled:
                num_culled_life_skills = num_culled_life_skills + 1
            life_skills_data.append(statistic_data)
        elif issubclass(stat_type, RankedStatistic):
            num_ranked_statistics = num_ranked_statistics + 1
            if culled:
                num_culled_ranked_statistics = num_culled_ranked_statistics + 1
            ranked_statistics.append(statistic_data)
        else:
            num_other_continuous = num_other_continuous + 1
            if culled:
                num_culled_other_continuous = num_culled_other_continuous + 1
            other_continuous_statistic_data.append(statistic_data)

    data['num_total_statistics'] = num_static_commodities + num_statistics + num_trait_statistics + num_commodities + num_skills + num_life_skills + num_ranked_statistics + num_other_continuous
    data['num_total_culled_statistics'] = num_culled_static_commodities + num_culled_statistics + num_culled_trait_statistics + num_culled_commodities + num_culled_skills + num_culled_life_skills + num_culled_ranked_statistics + num_culled_other_continuous
    data['num_commodities'] = num_commodities
    data['num_culled_commodities'] = num_culled_commodities
    data['num_skills'] = num_skills
    data['num_culled_skills'] = num_culled_skills
    data['num_life_skill_statistics'] = num_life_skills
    data['num_culled_life_skill_statistics'] = num_culled_life_skills
    data['num_ranked_statistics'] = num_ranked_statistics
    data['num_culled_ranked_statistics'] = num_culled_ranked_statistics
    data['num_other_continuous'] = num_other_continuous
    data['num_culled_other_continuous'] = num_culled_other_continuous
    data['commodities'] = commodities_data
    data['skills'] = skills_data
    data['life_skill_statistics'] = life_skills_data
    data['ranked_statistics'] = ranked_statistics
    data['other_continuous'] = other_continuous_statistic_data


@GsiHandler('stat_metric_handler', stat_metrics_schema)
def generate_stat_metric_data(*args, zone_id: int=None, filter=None, **kwargs):
    filter_list = parse_filter_to_list(filter)
    all_data = []
    if filter_list is None:
        return all_data
    if FILTER_ALL_SIM_INFOS in filter_list or FILTER_INSTANCED_SIM_INFOS in filter_list:
        for sim_info in list(services.sim_info_manager().objects):
            data = {}
            is_instanced = sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if FILTER_ALL_SIM_INFOS not in filter_list:
                if not is_instanced:
                    continue
            data['name'] = str(sim_info)
            data['instanced'] = str(is_instanced)
            data['lod'] = str(sim_info.lod)
            populate_data_from_statistic_component(sim_info, data)
            all_data.append(data)

    if FILTER_INSTANCED_OBJECTS in filter_list:
        for obj in list(services.object_manager(zone_id).objects):
            if not obj.has_component(STATISTIC_COMPONENT):
                continue
            data = {}
            data['name'] = str(obj)
            data['instanced'] = 'Yes'
            data['lod'] = 'NO LOD SUPPORT'
            populate_data_from_statistic_component(obj, data)
            all_data.append(data)

    return all_data