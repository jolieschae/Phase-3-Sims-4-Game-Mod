# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\timeline_handlers.py
# Compiled at: 2014-03-08 22:38:57
# Size of source mod 2**32: 2328 bytes
import collections

def _label(e, label):
    if label:
        return 'label="{}"'.format(e)
    return ''


def dotviz(t, label=True):
    lines = [
     'digraph timeline {']
    lines.append('rankdir = LR;')
    times = collections.defaultdict(list)
    for when, ix, element in t.queue:
        times[when].append((ix, element))

    sorted_times = sorted(times.keys())
    lines.append('subgraph T {')
    lines.append(' rank=min;')
    lines.append(' node [shape=box];')
    lines.append(' {};'.format(' -> '.join(['T{}'.format(when) for when in sorted_times])))
    if t._active is not None:
        lines.append('Eactive [shape=ellipse;{}];'.format(_label(t._active[0], label)))
        lines.append('Eactive -> T{};'.format(sorted_times[0]))
    lines.append('}')
    for when, events in sorted(times.items()):
        lines.append('subgraph {')
        for ix, element in events:
            lines.append(' E{} [{}];'.format(abs(ix), _label(element, label)))

        row = ' T{} -> {};'.format(when, ' -> '.join(('E{}'.format(abs(ix)) for ix, _ in sorted(events))))
        lines.append(row)
        lines.append('}')
        if t._active is not None:
            for ix, elem in events:
                if elem is t._active[0]:
                    lines.append('Eactive -> E{} [dir=none; style=dashed; constraint=false];'.format(abs(ix)))

    lines.append('}')
    return '\n'.join(lines)