# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\weather\weather_ops.py
# Compiled at: 2018-03-02 16:23:08
# Size of source mod 2**32: 2742 bytes
from _sims4_collections import frozendict
from protocolbuffers import DistributorOps_pb2, WeatherSeasons_pb2
from distributor.ops import Op
from distributor.rollback import ProtocolBufferRollback
import date_and_time

class WeatherEventOp(Op):

    def __init__(self, msg):
        super().__init__()
        self.op = msg

    @property
    def content(self):
        if self.op.season_weather_interlops:
            return str(self.op.season_weather_interlops)
        return ''

    def populate_op(self, message_type, start_value, start_time, end_value, end_time):
        with ProtocolBufferRollback(self.op.season_weather_interlops) as (weather_interop):
            weather_interop.message_type = message_type
            weather_interop.start_value = start_value
            weather_interop.start_time = int(start_time / date_and_time.REAL_MILLISECONDS_PER_SIM_SECOND)
            weather_interop.end_value = end_value
            weather_interop.end_time = int(end_time / date_and_time.REAL_MILLISECONDS_PER_SIM_SECOND)

    def write(self, msg):
        msg.type = DistributorOps_pb2.Operation.SEASON_WEATHER_INTERPOLATIONS
        msg.data = self.op.SerializeToString()


class WeatherUpdateOp(Op):

    def __init__(self, weather_types):
        super().__init__()
        self.op = WeatherSeasons_pb2.UiWeatherUpdate()
        for weather_type in weather_types:
            self.op.weather_type_enums.append(weather_type)

    def write(self, msg):
        msg.type = DistributorOps_pb2.Operation.UI_WEATHER_UPDATE
        msg.data = self.op.SerializeToString()


class WeatherForecastOp(Op):

    def __init__(self, forecast_instances):
        super().__init__()
        self.op = WeatherSeasons_pb2.UiWeatherForecastUpdate()
        for forecast_instance in forecast_instances:
            if forecast_instance is not None:
                self.op.forecast_instance_ids.append(forecast_instance.guid64)

    def write(self, msg):
        msg.type = DistributorOps_pb2.Operation.UI_WEATHER_FORECAST_UPDATE
        msg.data = self.op.SerializeToString()