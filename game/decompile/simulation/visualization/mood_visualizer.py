# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\visualization\mood_visualizer.py
# Compiled at: 2018-07-10 17:45:11
# Size of source mod 2**32: 1424 bytes
from debugvis import Context
import sims4.math

def strip_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


class MoodVisualizer:

    def __init__(self, sim, layer):
        self._sim = sim.ref()
        self.layer = layer
        self.start()

    @property
    def sim(self):
        if self._sim is not None:
            return self._sim()

    def start(self):
        self.sim.Buffs.on_mood_changed.append(self._on_mood_changed)
        self._on_mood_changed()

    def stop(self):
        sim = self.sim
        if sim is not None:
            if sim.Buffs is not None:
                sim.Buffs.on_mood_changed.remove(self._on_mood_changed)

    def _on_mood_changed(self, **kwargs):
        offset = sims4.math.Vector3.Y_AXIS() * 0.4
        BONE_INDEX = 5
        mood_name = strip_prefix(self.sim.get_mood().__name__, 'Mood_')
        with Context(self.layer) as (context):
            context.add_text_object((self.sim), offset, mood_name, bone_index=BONE_INDEX)