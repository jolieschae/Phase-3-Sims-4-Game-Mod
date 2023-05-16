# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\zone_utils.py
# Compiled at: 2015-02-09 21:22:09
# Size of source mod 2**32: 1273 bytes
import collections, itertools, sims4.reload
with sims4.reload.protected(globals()):
    zone_id = None
    _zone_changed_callback = None
    zone_id_counter = itertools.count(1)
    zone_numbers = collections.defaultdict(lambda: next(zone_id_counter), {0: 0})

def set_current_zone_id(_zone_id):
    global _zone_changed_callback
    global zone_id
    zone_id = _zone_id
    if _zone_changed_callback is not None:
        _zone_changed_callback(zone_id)


def register_zone_change_callback(callback):
    global _zone_changed_callback
    _zone_changed_callback = callback