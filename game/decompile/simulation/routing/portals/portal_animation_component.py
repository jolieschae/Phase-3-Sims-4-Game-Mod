# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\portals\portal_animation_component.py
# Compiled at: 2020-03-09 13:38:07
# Size of source mod 2**32: 1967 bytes
from animation.animation_constants import ActorType
from animation.animation_overrides_tuning import TunableParameterMapping
from distributor.fields import ComponentField, Field
from distributor.ops import SetActorType, SetActorStateMachine, SetActorStateMachineParams
from objects.components import Component
from objects.components.types import PORTAL_ANIMATION_COMPONENT
from sims4.tuning.tunable import AutoFactoryInit, HasTunableFactory, TunableInteractionAsmResourceKey

class PortalAnimationComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=PORTAL_ANIMATION_COMPONENT):
    FACTORY_TUNABLES = {'_portal_asm':TunableInteractionAsmResourceKey(description='\n            The animation to use for this portal.\n            '), 
     '_portal_asm_parameters':TunableParameterMapping(description='\n            The parameters to utilize in the portal asm for this object.\n            ')}

    @ComponentField(op=SetActorType, priority=(Field.Priority.HIGH))
    def actor_type(self):
        return ActorType.Door

    @ComponentField(op=SetActorStateMachine)
    def portal_asm(self):
        return self._portal_asm

    @ComponentField(op=SetActorStateMachineParams, default=None)
    def portal_asm_params(self):
        if self._portal_asm_parameters:
            return self._portal_asm_parameters