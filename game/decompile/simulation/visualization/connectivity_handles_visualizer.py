# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\visualization\connectivity_handles_visualizer.py
# Compiled at: 2013-03-15 12:13:49
# Size of source mod 2**32: 1942 bytes
from debugvis import Context
import services, sims4.color

class ConnectivityHandlesVisualizer:

    def __init__(self, sim, layer):
        self.layer = layer
        self.start()

    def start(self):
        services.current_zone().navmesh_change_callbacks.append(self.refresh)
        self.refresh()

    def stop(self):
        services.current_zone().navmesh_change_callbacks.remove(self.refresh)

    def refresh(self):
        pre_slot_color = sims4.color.from_rgba(0.8, 0.8, 0, 0.9)
        post_slot_color = sims4.color.from_rgba(0.9, 0.7, 0, 0.25)
        with Context((self.layer), altitude=0.1) as (context):
            for obj in services.object_manager().valid_objects():
                pass