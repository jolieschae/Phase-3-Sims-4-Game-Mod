# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\elements_handlers.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 3256 bytes
from builtins import isinstance
from alarms import AlarmElement
from scheduling import ElementHandle
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema
import services
timeline_schema = GsiGridSchema(label='Elements')
timeline_schema.add_field('line', label='Element')

class _Node:

    def __init__(self, element_handle):
        self.element_handle = element_handle
        self.level = 0

    @property
    def index(self):
        return self.element_handle.ix

    def __repr__(self):
        indent = '.' * self.level
        if self.index is None:
            return '{}{}'.format(indent, self.element_handle.element.tracing_repr())
        return '{}{}:{}'.format(indent, self.element_handle.element.tracing_repr(), self.index)


@GsiHandler('sim_timeline_elements', timeline_schema)
def create_sim_timeline_data(zone_id: int=None):
    time_service = services.time_service()
    if time_service is None:
        return
    sim_timeline = time_service.sim_timeline
    if sim_timeline is None:
        return
    return _create_timeline_fields(services.time_service().sim_timeline)


def _create_timeline_fields(timeline):
    stacks = _create_all_timeline_stacks(timeline)
    data = []
    for stack in stacks:
        for node in stack:
            data.append({'line': str(node)})

        data.append({'line': ''})

    return data


def _create_all_timeline_stacks(timeline):
    all_stacks = []
    if timeline is None:
        return all_stacks
    local_timeline = []
    for handle in timeline.heap:
        if handle.when is not None:
            local_timeline.append(ElementHandle(handle.when, handle.ix, handle.timeline, handle.is_scheduled, handle.element))

    for element_handle in sorted(local_timeline):
        if not element_handle.element is None:
            if isinstance(element_handle.element, AlarmElement):
                continue
            all_stacks.append(_create_stack(element_handle))

    return all_stacks


def _create_stack(scheduled_handle):
    stack = []
    stack.append(_Node(scheduled_handle))
    child_handle = scheduled_handle
    while child_handle is not None and child_handle.element is not None and child_handle.element._parent_handle is not None:
        parent_handle = child_handle.element._parent_handle
        node = _Node(parent_handle)
        stack.insert(0, node)
        child_handle = parent_handle

    for i, node in enumerate(stack):
        node.level = i

    return stack