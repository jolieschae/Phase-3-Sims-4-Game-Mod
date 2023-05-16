# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\visualization\autonomy_timer_visualizer.py
# Compiled at: 2014-06-09 15:26:04
# Size of source mod 2**32: 2307 bytes
from debugvis import Context
import alarms, autonomy.settings, clock, sims4.math

class AutonomyTimerVisualizer:

    def __init__(self, sim, layer):
        self._sim = sim.ref()
        self._layer = layer
        self._alarm_handle = None
        self.start()

    @property
    def sim(self):
        if self._sim is not None:
            return self._sim()

    @property
    def layer(self):
        return self._layer

    def start(self):
        self._alarm_handle = alarms.add_alarm_real_time(self, (clock.interval_in_real_seconds(1.0)),
          (self._process),
          repeating=True,
          use_sleep_time=False)

    def stop(self):
        if self._alarm_handle is not None:
            self._alarm_handle.cancel()
            self._alarm_handle = None

    def _process(self, _):
        sim = self.sim
        if sim is None:
            self.stop()
            return
        else:
            offset = sims4.math.Vector3.Y_AXIS() * 0.4
            BONE_INDEX = 5
            if sim.to_skip_autonomy():
                autonomy_timer_text = 'Skipping'
            else:
                if sim.get_autonomy_state_setting() < autonomy.settings.AutonomyState.FULL:
                    autonomy_timer_text = 'Disabled'
                else:
                    autonomy_timer_text = str(sim.get_time_until_next_update())
        with Context(self._layer) as (context):
            context.add_text_object((self.sim), offset, autonomy_timer_text, bone_index=BONE_INDEX)