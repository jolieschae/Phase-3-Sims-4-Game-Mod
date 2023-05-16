# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\common.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 4277 bytes
import placement, services, sims4
from element_utils import build_critical_section_with_finally
logger = sims4.log.Logger('Interaction Utils')

class InteractionRetargetHandler:

    def __init__(self, interaction, target):
        self._target = target
        self._old_target = interaction.target
        self._interaction = interaction

    def begin(self, _):
        self._interaction.set_target(self._target)

    def end(self, _):
        self._interaction.set_target(self._old_target)


def retarget_interaction(interaction, target, *args):
    if interaction is not None:
        interaction_retarget_handler = InteractionRetargetHandler(interaction, target)
        return build_critical_section_with_finally(interaction_retarget_handler.begin, args, interaction_retarget_handler.end)
    return args


class InteractionUtils:

    @staticmethod
    def do_put_near(subject, target, fallback_to_spawn_point, use_fgl):
        if not subject is None:
            if target is None:
                logger.error('Trying to run a PutNear basic extra with a None Subject and/or Target. subject:{}, target:{}', subject,
                  target, owner='trevor')
                return
            surface = target.routing_surface
            if use_fgl:
                starting_location = placement.create_starting_location(location=(target.location))
                if subject.is_sim:
                    fgl_context = placement.create_fgl_context_for_sim(starting_location, subject)
                else:
                    fgl_context = placement.create_fgl_context_for_object(starting_location, subject)
                translation, orientation, _ = fgl_context.find_good_location()
                if translation is None and fallback_to_spawn_point:
                    zone = services.current_zone()
                    fallback_point = zone.get_spawn_point(lot_id=(zone.lot.lot_id))
                    translation, orientation = fallback_point.next_spawn_spot()
                    surface = fallback_point.routing_surface
            else:
                transform = target.location.transform
                translation = transform.translation
                orientation = transform.orientation
            if translation is None:
                return
        else:
            inventoryitem_component = subject.inventoryitem_component
            if inventoryitem_component is not None:
                if subject.is_in_inventory():
                    inventory_owner = inventoryitem_component.last_inventory_owner
                    if not inventory_owner.inventory_component.try_remove_object_by_id(subject.id):
                        logger.error("Failed to remove object from {}'s inventory when running PutNear basic extra on {}", inventory_owner,
                          subject, owner='skorman')
                        return
        subject.move_to(translation=translation, orientation=(orientation or subject.orientation),
          routing_surface=surface,
          parent=None,
          joint_name_or_hash=None,
          slot_hash=0)