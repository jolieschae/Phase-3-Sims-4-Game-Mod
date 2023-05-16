# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\performance\object_leak_commands.py
# Compiled at: 2017-12-01 19:51:05
# Size of source mod 2**32: 2151 bytes
import itertools
from performance.object_leak_tracker import ObjectLeakTracker
import services, sims4.commands

@sims4.commands.Command('object_leak_tracker.start', command_type=(sims4.commands.CommandType.Automation))
def create_object_leak_tracker(_connection=None):
    result = services.create_object_leak_tracker(start=True)
    if result:
        sims4.commands.cheat_output('Object leak tracker started', _connection)
    else:
        sims4.commands.cheat_output('Object leak tracker already started', _connection)


@sims4.commands.Command('object_leak_tracker.dump')
def describe(obj_id: int=None, depth: int=None, _connection=None):
    obj = services.current_zone().find_object(obj_id, include_props=True)
    if obj is not None:
        ObjectLeakTracker.generate_referrer_graph_for_objects((obj,), max_depth=depth)
        sims4.commands.cheat_output('Dumped {}'.format(obj), _connection)
    else:
        sims4.commands.cheat_output('No object with id {}'.format(obj_id), _connection)


@sims4.commands.Command('object_leak_tracker.dump_pid')
def describe_pid(pid: int=None, depth: int=None, _connection=None):
    tracker = services.get_object_leak_tracker()
    if tracker is None:
        sims4.commands.cheat_output('Object leak tracker not running', _connection)
        return
    obj = None
    for node in itertools.chain.from_iterable(tracker.buckets.values()):
        if node.pid == pid:
            obj = node.get_object()
            break

    if obj is None:
        sims4.commands.cheat_output("Object leak tracker doesn't know about {}".format(pid), _connection)
        return
    ObjectLeakTracker.generate_referrer_graph_for_objects((obj,), max_depth=depth)
    sims4.commands.cheat_output('Dumped {}'.format(obj), _connection)