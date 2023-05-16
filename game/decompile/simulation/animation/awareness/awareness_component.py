# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\awareness\awareness_component.py
# Compiled at: 2017-09-18 19:48:42
# Size of source mod 2**32: 3267 bytes
from animation.awareness.awareness_ops import SetAwarenessOp
from objects.components import Component, types, componentmethod
from sims4.tuning.tunable import AutoFactoryInit, HasTunableFactory
import distributor.fields
from _collections import defaultdict

class AwarenessComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=types.AWARENESS_COMPONENT):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._modifiers = defaultdict(list)

    @distributor.fields.ComponentField(op=SetAwarenessOp)
    def awareness_modifiers(self):
        return self._modifiers

    resend_awareness_modifiers = awareness_modifiers.get_resend()

    @componentmethod
    def add_awareness_modifier(self, awareness_channel, awareness_options):
        self._modifiers[awareness_channel].append(awareness_options)
        self.resend_awareness_modifiers()

    @componentmethod
    def add_proximity_modifier(self, proximity_options):
        if proximity_options.inner_radius is not None:
            self._modifiers[SetAwarenessOp.PROXIMITY_INNER_RADIUS].append(proximity_options.inner_radius)
        if proximity_options.outer_radius is not None:
            self._modifiers[SetAwarenessOp.PROXIMITY_OUTER_RADIUS].append(proximity_options.outer_radius)
        self.resend_awareness_modifiers()

    @componentmethod
    def remove_awareness_modifier(self, awareness_channel, awareness_options):
        if awareness_channel in self._modifiers:
            if awareness_options in self._modifiers[awareness_channel]:
                self._modifiers[awareness_channel].remove(awareness_options)
        self.resend_awareness_modifiers()

    @componentmethod
    def remove_proximity_modifier(self, proximity_options):
        if proximity_options.inner_radius is not None:
            if proximity_options.inner_radius in self._modifiers[SetAwarenessOp.PROXIMITY_INNER_RADIUS]:
                self._modifiers[SetAwarenessOp.PROXIMITY_INNER_RADIUS].remove(proximity_options.inner_radius)
        if proximity_options.outer_radius is not None:
            if proximity_options.outer_radius in self._modifiers[SetAwarenessOp.PROXIMITY_OUTER_RADIUS]:
                self._modifiers[SetAwarenessOp.PROXIMITY_OUTER_RADIUS].remove(proximity_options.outer_radius)
        self.resend_awareness_modifiers()