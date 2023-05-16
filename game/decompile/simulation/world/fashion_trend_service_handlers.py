# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\fashion_trend_service_handlers.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 4267 bytes
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema, GsiBarChartSchema, GsiFieldVisualizers
import services
fashion_trend_schema = GsiGridSchema(label='Fashion Trends', sim_specific=False)
fashion_trend_schema.add_field('name', label='Name', unique_field=True)
fashion_trend_schema.add_field('type', label='Type')
fashion_trend_schema.add_field('value', label='Value')
fashion_trend_schema.add_field('default_value', label='Default Value')
fashion_trend_schema.add_field('min', label='Minimum')
fashion_trend_schema.add_field('max', label='Maximum')
fashion_trend_schema.add_field('statistic_modifier', label='Statistic Modifier')

@GsiHandler('fashion_trend_service', fashion_trend_schema)
def generate_fashion_trend_service_data(*args, zone_id: int=None, **kwargs):
    fashion_trend_service_data = []
    fashion_trend_service = services.fashion_trend_service()
    if fashion_trend_service is None:
        return fashion_trend_service_data
    for statistic in list(fashion_trend_service.statistic_tracker):
        entry = {'name':type(statistic).__name__, 
         'type':'Statistic', 
         'value':statistic.get_value(), 
         'default_value':statistic.default_value, 
         'min':statistic.min_value, 
         'max':statistic.max_value, 
         'statistic_modifier':statistic._statistic_modifier}
        fashion_trend_service_data.append(entry)

    for commodity in fashion_trend_service.commodity_tracker.get_all_commodities():
        entry = {'name':type(commodity).__name__, 
         'type':'Commodity', 
         'value':commodity.get_value(), 
         'default_value':commodity.default_value, 
         'min':commodity.min_value, 
         'max':commodity.max_value, 
         'statistic_modifier':commodity._statistic_modifier}
        fashion_trend_service_data.append(entry)

    return fashion_trend_service_data


fashion_trend_commodity_and_stat_view_schema = GsiBarChartSchema(label='Fashion Trends - Stat/Commodity Visualizer', sim_specific=False)
fashion_trend_commodity_and_stat_view_schema.add_field('name', axis=(GsiBarChartSchema.Axis.X))
fashion_trend_commodity_and_stat_view_schema.add_field('value', type=(GsiFieldVisualizers.INT))
fashion_trend_commodity_and_stat_view_schema.add_field('percentFull', axis=(GsiBarChartSchema.Axis.Y),
  type=(GsiFieldVisualizers.INT),
  is_percent=True)

@GsiHandler('fashion_trend_commodity_and_stat_view', fashion_trend_commodity_and_stat_view_schema)
def fashion_trend_commodity_and_stat_view_data():
    data = []
    fashion_trend_service = services.fashion_trend_service()
    if fashion_trend_service is not None:
        if fashion_trend_service.static_commodity_tracker is not None:
            for stat in fashion_trend_service.commodity_tracker.all_statistics():
                if not stat.is_commodity:
                    continue
                stat_name = stat.stat_type.__name__
                stat_value = stat.get_value()
                data.append({'name':stat_name,  'value':stat_value, 
                 'percentFull':stat_value / stat.max_value * 100 if stat.max_value != 0 else 0})

        if fashion_trend_service.statistic_tracker is not None:
            for stat in fashion_trend_service.statistic_tracker.all_statistics():
                stat_name = stat.stat_type.__name__
                stat_value = stat.get_value()
                data.append({'name':stat_name,  'value':stat_value, 
                 'percentFull':(stat_value - stat.min_value) / (stat.max_value - stat.min_value) * 100})

    return sorted(data, key=(lambda entry: entry['name']))