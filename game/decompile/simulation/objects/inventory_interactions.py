# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\inventory_interactions.py
# Compiled at: 2017-08-24 15:41:56
# Size of source mod 2**32: 1359 bytes
import objects, services, sims4

@sims4.commands.Command('inventory.clone_obj_to_inv', command_type=(sims4.commands.CommandType.Automation))
def clone_obj_to_inv(obj_id: int, inventory_owner_id: int, count: int=1, _connection=None):
    obj_to_create = services.object_manager().get(obj_id)
    target_object = services.object_manager().get(inventory_owner_id)
    if obj_to_create is None or target_object is None:
        sims4.commands.output('{} or {} not found in object manager'.format(obj_id, inventory_owner_id), _connection)
        return
    inventory = target_object.inventory_component
    if inventory is None:
        sims4.commands.output("{} doesn't have an inventory".format(str(target_object)), _connection)
        return
    for _ in range(count):
        obj_instance = objects.system.create_object(obj_to_create.definition)
        if obj_instance:
            inventory.player_try_add_object(obj_instance)