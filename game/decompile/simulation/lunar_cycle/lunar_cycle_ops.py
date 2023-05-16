# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\lunar_cycle\lunar_cycle_ops.py
# Compiled at: 2022-06-13 18:18:17
# Size of source mod 2**32: 1945 bytes
from protocolbuffers import DistributorOps_pb2, WeatherSeasons_pb2
from distributor.ops import Op

class MoonPhaseUpdateOp(Op):

    def __init__(self, phase_type, skip_environment_changes):
        super().__init__()
        op = WeatherSeasons_pb2.MoonPhaseUpdate()
        op.current_moon_phase = phase_type.value
        op.skip_environment_changes = skip_environment_changes
        self.op = op

    def __repr__(self):
        return 'MOON_PHASE_UPDATE:{}'.format(str(self.op))

    def write(self, msg):
        msg.type = DistributorOps_pb2.Operation.MOON_PHASE_UPDATE
        msg.data = self.op.SerializeToString()


class LunarEffectTooltipUpdateOp(Op):

    def __init__(self, current_phase):
        super().__init__()
        op = WeatherSeasons_pb2.UiLunarEffectTooltipUpdate()
        op.current_moon_phase = current_phase
        self.op = op

    def set_tooltip(self, tooltip):
        self.op.tooltip_text = tooltip

    def __repr__(self):
        return 'LUNAR_EFFECT_TOOLTIP_UPDATE:{}'.format(str(self.op))

    def write(self, msg):
        msg.type = DistributorOps_pb2.Operation.UI_LUNAR_EFFECT_TOOLTIP_UPDATE
        msg.data = self.op.SerializeToString()


class MoonForecastUpdateOp(Op):

    def __init__(self, forecast_moon_phases):
        super().__init__()
        op = WeatherSeasons_pb2.MoonForecastUpdate()
        op.forecast_moon_phases.extend(forecast_moon_phases)
        self.op = op

    def __repr__(self):
        return 'MOON_FORECAST_UPDATE:{}'.format(str(self.op))

    def write(self, msg):
        msg.type = DistributorOps_pb2.Operation.MOON_FORECAST_UPDATE
        msg.data = self.op.SerializeToString()