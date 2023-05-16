# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\portals\portal_data_variable_jump.py
# Compiled at: 2020-02-19 16:59:14
# Size of source mod 2**32: 3035 bytes
from animation import get_throwaway_animation_context, animation_constants
from animation.arb import Arb
from animation.asm import create_asm
from routing.portals.portal_data_locomotion import _PortalTypeDataLocomotion
from routing.portals.portal_tuning import PortalType
from routing.portals.variable_jump_mixin import _VariableJumpMixin

class _PortalTypeDataVariableJump(_PortalTypeDataLocomotion, _VariableJumpMixin):

    @property
    def portal_type(self):
        return PortalType.PortalType_Animate

    def add_portal_data(self, actor, portal_instance, is_mirrored, walkstyle):
        return self._add_variable_jump_portal_data(actor, portal_instance, is_mirrored, walkstyle)

    def get_portal_duration(self, portal_instance, is_mirrored, walkstyle, age, gender, species):
        return self._get_variable_jump_portal_duration(portal_instance, is_mirrored, species)

    def _get_arb(self, actor, portal_instance, *, is_mirrored):
        arb = Arb()
        asm = create_asm((self.animation_element.asm_key), context=(get_throwaway_animation_context()))
        asm.set_actor(self.animation_element.actor_name, actor)
        if is_mirrored:
            entry_location, exit_location = portal_instance.back_entry, portal_instance.back_exit
        else:
            entry_location, exit_location = portal_instance.there_entry, portal_instance.there_exit
        asm.set_actor_parameter(self.animation_element.actor_name, actor, animation_constants.ASM_INITIAL_TRANSLATION, entry_location.position)
        asm.set_actor_parameter(self.animation_element.actor_name, actor, animation_constants.ASM_INITIAL_ORIENTATION, entry_location.orientation)
        asm.set_actor_parameter(self.animation_element.actor_name, actor, animation_constants.ASM_TARGET_TRANSLATION, exit_location.position)
        asm.set_actor_parameter(self.animation_element.actor_name, actor, animation_constants.ASM_TARGET_ORIENTATION, entry_location.orientation)
        self.animation_element.append_to_arb(asm, arb)
        return arb