# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\parenting_utils.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 8250 bytes
import weakref
from interactions import ParticipantTypeActorTargetSim, ParticipantTypeObject
from interactions.utils.interaction_elements import XevtTriggeredElement
from objects.components import types
from placement import FGLSearchFlag, create_starting_location, find_good_location
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableEnumEntry, TunableVariant, HasTunableSingletonFactory
from sims4.tuning.tunable_hash import TunableStringHash32
import build_buy, enum, placement, sims4.log
logger = sims4.log.Logger('ParentingUtils', default_owner='camilogarcia')

class HeadPlacementLocation(enum.Int):
    GROUND_PLACEMENT = 0
    INVENTORY_PLACEMENT = 1


class SetAsHead(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'bone_name': TunableStringHash32(description='\n            Bone where the object will be attached to.\n            ',
                    default='b__neck__')}

    def apply(self, participant_to_parent, parent_target):
        if parent_target.current_object_set_as_head is not None:
            if parent_target.current_object_set_as_head() is not None:
                return False
        SetAsHead.set_head_object(parent_target, participant_to_parent, self.bone_name)

    @classmethod
    def set_head_object(cls, parent, object_to_parent, bone_hash):
        forward_rot = 4 * sims4.math.PI / 3
        up_rot = 3 * sims4.math.PI / 2
        forward_orientation = sims4.math.Quaternion.from_axis_angle(forward_rot, sims4.math.FORWARD_AXIS)
        up_orientation = sims4.math.Quaternion.from_axis_angle(up_rot, sims4.math.UP_AXIS)
        orientation = sims4.math.Quaternion.concatenate(forward_orientation, up_orientation)
        new_transform = sims4.math.Transform.IDENTITY()
        new_transform.orientation = orientation
        parent.current_object_set_as_head = weakref.ref(object_to_parent)
        object_to_parent.set_parent(parent, new_transform, joint_name_or_hash=bone_hash)
        if not parent.is_sim:
            logger.error('Parenting {} into a non sim object {}', object_to_parent, parent)
            return
        if object_to_parent.has_component(types.PARENT_TO_SIM_HEAD_COMPONENT):
            object_to_parent.remove_component(types.PARENT_TO_SIM_HEAD_COMPONENT)
        object_to_parent.add_dynamic_component((types.PARENT_TO_SIM_HEAD_COMPONENT), parent_sim_info_id=(parent.sim_info.id), bone_hash=bone_hash)


class UnsetAsHead(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'placement_location': TunableEnumEntry(description="\n            Location where the object will be placed after the element is ran.\n            If the inventory is specified and the object can't be placed on the\n            inventory, the household inventory will be used as a fallback.\n            ",
                             tunable_type=HeadPlacementLocation,
                             default=(HeadPlacementLocation.GROUND_PLACEMENT))}

    def apply(self, participant_to_unparent, parent_target):
        if parent_target.current_object_set_as_head is None or parent_target.current_object_set_as_head() is not participant_to_unparent:
            return False
        participant_to_unparent.clear_parent(parent_target.transform, parent_target.routing_surface)
        if self.placement_location == HeadPlacementLocation.GROUND_PLACEMENT:
            self._place_object_on_ground(participant_to_unparent, parent_target) or logger.warn('Object {} failed to be placed on ground next to Sim {}', participant_to_unparent, parent_target)
            self._fallback_placement(participant_to_unparent, parent_target)
        else:
            if parent_target.inventory_component.can_add(participant_to_unparent):
                if not parent_target.inventory_component.player_try_add_object(participant_to_unparent):
                    logger.warn('Object {} failed to be placed on the inventory for Sim {}', participant_to_unparent, parent_target)
                    self._fallback_placement(participant_to_unparent, parent_target)
        parent_target.current_object_set_as_head = None
        participant_to_unparent.remove_component(types.PARENT_TO_SIM_HEAD_COMPONENT)

    def _fallback_placement(self, participant_to_unparent, parent_target):
        if not build_buy.move_object_to_household_inventory(participant_to_unparent):
            logger.error('Object {} failed to be moved to the household inventory', participant_to_unparent)
            participant_to_unparent.location = parent_target.location

    def _place_object_on_ground(self, head_obj, source_obj):
        starting_location = create_starting_location(location=(source_obj.location))
        search_flags = FGLSearchFlag.ALLOW_GOALS_IN_SIM_INTENDED_POSITIONS | FGLSearchFlag.ALLOW_GOALS_IN_SIM_POSITIONS
        fgl_context = placement.create_fgl_context_for_object(starting_location, head_obj, search_flags=search_flags, ignored_object_ids=(source_obj.id,))
        translation, orientation, _ = fgl_context.find_good_location()
        if translation is None or orientation is None:
            return False
        head_obj.move_to(translation=translation, orientation=orientation,
          routing_surface=(source_obj.routing_surface))
        return True


class SetAsHeadElement(XevtTriggeredElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'participant_to_slot':TunableEnumEntry(description='\n            The participant of the interaction that will be parented into the \n            target.\n            ',
       tunable_type=ParticipantTypeObject,
       default=ParticipantTypeObject.Object), 
     'participant_target':TunableEnumEntry(description='\n            The target where the object will be parented.\n            ',
       tunable_type=ParticipantTypeActorTargetSim,
       default=ParticipantTypeActorTargetSim.Actor), 
     'set_head_operation':TunableVariant(description='\n            Operation that should be done when the element is executed.\n            ',
       set_as_head=SetAsHead.TunableFactory(),
       unset_as_head=UnsetAsHead.TunableFactory(),
       default='set_as_head')}

    def _do_behavior(self):
        participant_to_parent = self.interaction.get_participant(self.participant_to_slot)
        if participant_to_parent is None:
            return False
        else:
            parent_target = self.interaction.get_participant(self.participant_target)
            return parent_target is None or parent_target.is_sim or False
        return self.set_head_operation.apply(participant_to_parent, parent_target)