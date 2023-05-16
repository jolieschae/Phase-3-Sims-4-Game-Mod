# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\object_commands.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 82226 bytes
import collections, itertools, random, weakref
from crafting.crafting_interactions import DebugCreateCraftableInteraction, create_craftable
from crafting.crafting_tunable import CraftingTuning
from distributor.ops import GenericProtocolBufferOp, SetVoiceActor
from distributor.rollback import ProtocolBufferRollback
from distributor.system import Distributor
from objects import VisibilityState, MaterialState, PaintingState
from objects.components import types, Component, consumable_component
from objects.components.censor_grid_component import CensorState
from objects.gallery_tuning import GalleryGameplayTuning
from objects.persistence_groups import PersistenceGroups
from objects.prop_object import PropObject
from objects.components.stored_actor_location_component import add_stored_sim_location
from postures.posture_graph import supress_posture_graph_build
from protocolbuffers.DistributorOps_pb2 import Operation
from protocolbuffers.UI_pb2 import InventoryCountUpdate
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target, RequiredTargetParam, TunableInstanceParam, NoneIntegerOrString, OptionalSimInfoParam
from sims.outfits.outfit_enums import OutfitCategory, SpecialOutfitIndex, REGULAR_OUTFIT_CATEGORIES, HIDDEN_OUTFIT_CATEGORIES
from sims4.tuning.tunable import TunableReference
import build_buy, camera, distributor, objects.system, placement, postures.posture_graph, routing, services, sims4.commands, sims4.hash_util, sims4.math
logger = sims4.log.Logger('Object')

class ObjectCommandTuning:
    DIRTY_COMMODITY = TunableReference(description='The Dirty Commodity', manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)))
    BROKEN_COMMODITY = TunableReference(description='The Broken Commodity', manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)))
    BURNED_MATERIAL_STATE = TunableReference(description='The Burned Material State', manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)))
    BURNED_ASH_STATE = TunableReference(description='The Burned Ash State', manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)))


def _all_objects_gen(manager, lot_filter):
    for obj in manager.get_all():
        if lot_filter is None:
            yield obj
        elif lot_filter == 'onlot':
            if obj.persistence_group == PersistenceGroups.OBJECT:
                yield obj
        if lot_filter == 'offlot' and obj.persistence_group == PersistenceGroups.IN_OPEN_STREET:
            yield obj


@sims4.commands.Command('objects.list', command_type=(sims4.commands.CommandType.Automation))
def list_objects(filter_name=None, lot_filter=None, _connection=None):
    manager = services.object_manager()
    if filter_name is None:
        object_types = {}
        total = 0
        for obj in _all_objects_gen(manager, lot_filter):
            total += 1
            t = type(obj).__name__
            object_types[t] = object_types.get(t, 0) + 1

        for object_type, count in object_types.items():
            sims4.commands.output('{}: {}'.format(object_type, count), _connection)

        sims4.commands.output('Total: {}'.format(total), _connection)
    else:
        if filter_name == 'all':
            sims4.commands.automation_output('AllObjectsList; Status:Begin', _connection)
            total = 0
            for obj in _all_objects_gen(manager, lot_filter):
                sims4.commands.automation_output('AllObjectsList; Status:Data, obj_id={:#018x}, addr={:#010x}'.format(obj.id, id(obj)), _connection)
                sims4.commands.output('{}: {} (obj_id={:#018x}, addr={:#010x})'.format(type(obj).__name__, obj, obj.id, id(obj)), _connection)
                total += 1

            sims4.commands.automation_output('AllObjectsList; Status:End', _connection)
            sims4.commands.output('Total: {}'.format(total), _connection)
        else:
            if filter_name == 'definitions':
                sims4.commands.automation_output('AllObjectDefinitionsList; Status:Begin', _connection)
                all_definitions = collections.Counter()
                for obj in _all_objects_gen(manager, lot_filter):
                    all_definitions[obj.definition] += 1

                for definition, count in sorted((all_definitions.items()), key=(lambda x: x[0].id)):
                    sims4.commands.output('{},{:#010x},{}'.format(definition.name, definition.id, count), _connection)
                    sims4.commands.automation_output('AllObjectDefinitionsList; Status:Data, def_name={}, def_id={:#010x}, count={}'.format(definition.name, definition.id, count), _connection)

                sims4.commands.automation_output('AllObjectDefinitionsList; Status:End', _connection)
            else:
                if filter_name == 'interactables':
                    sims4.commands.automation_output('InteractbleObjectsList; Status:Begin', _connection)
                    for obj in _all_objects_gen(manager, lot_filter):
                        if obj.interactable == True:
                            sims4.commands.automation_output('InteractbleObjectsList; Status:Data, ObjectType:{}, ObjectName:{}, ObjectId:{}'.format(type(obj).__name__, obj, obj.id), _connection)
                            sims4.commands.output('InteractbleObjectsList; Status:Data, ObjectType:{}, ObjectName:{}, ObjectId:{}'.format(type(obj).__name__, obj, obj.id), _connection)

                    sims4.commands.automation_output('InteractbleObjectsList; Status:End', _connection)
                else:
                    total = 0
                    for obj in _all_objects_gen(manager, lot_filter):
                        t = type(obj).__name__
                        if filter_name in t:
                            sims4.commands.output('{}: {} (obj_id={:#018x}, addr={:#010x})'.format(type(obj).__name__, obj, obj.id, id(obj)), _connection)
                            total += 1

                    sims4.commands.output('Total: {}'.format(total), _connection)


@sims4.commands.Command('qa.object.get_radius', command_type=(sims4.commands.CommandType.Automation))
def qa_get_object_radius(obj_id: int, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.automation_output('qa.object.radius: Object ID not in the object manager.', _connection)
    if obj is not None:
        sims4.commands.automation_output('ObjectRadius; Radius:{}'.format(obj.object_radius), _connection)


@sims4.commands.Command('objects.dump')
def dump_object(obj_id: int, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('DUMP_OBJECT: Object ID not in the object manager.', _connection)
    if obj is not None:
        sims4.commands.output('Object {} ({})'.format(obj_id, obj.__class__.__name__), _connection)
        for key, value in vars(obj).items():
            sims4.commands.output('\t{} = {}'.format(key, value), _connection)
            if isinstance(value, Component):
                for key, value in vars(value).items():
                    sims4.commands.output('\t\t{} = {}'.format(key, value), _connection)


@sims4.commands.Command('objects.dump_def')
def dump_definition(guid: int, _connection=None):
    manager = services.definition_manager()
    obj_def = manager.get(guid)
    if not obj_def:
        sims4.commands.output('DUMP_DEFINITION: Unknown object definition GUID {}.'.format(guid), _connection)
    else:
        sims4.commands.output('Definition {}'.format(guid), _connection)
        for key, value in vars(obj_def).items():
            sims4.commands.output('    {} = {}'.format(key, value), _connection)


@sims4.commands.Command('objects.in_use')
def show_in_use(obj_id: int, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('in_use: Object ID not in the object manager.', _connection)
        return
        if getattr(obj, 'in_use'):
            sims4.commands.output('[{}] {} in_use = '.format(obj_id, obj.__class__.__name__, obj.in_use), _connection)
        else:
            sims4.commands.output('[{}] {} does not have the in_use property.'.format(obj_id, obj.__class__.__name__), _connection)


@sims4.commands.Command('objects.create', command_type=(sims4.commands.CommandType.Automation))
def create_object(def_id, x=0.0, y=0.0, z=0.0, level=0, _connection=None):
    obj = objects.system.create_object(def_id)
    if obj is not None:
        zone_id = services.current_zone_id()
        routing_surface = routing.SurfaceIdentifier(zone_id, level, routing.SurfaceType.SURFACETYPE_WORLD)
        obj.move_to(translation=(sims4.math.Vector3(x, y, z)), routing_surface=routing_surface)
    return obj


@sims4.commands.Command('qa.objects.fglcreate', command_type=(sims4.commands.CommandType.Automation))
def qa_create_object(def_id, x_pos=None, y_pos=None, z_pos=None, pos_increment=None, max_search_distance=None, _connection=None):
    obj = objects.system.create_object(def_id)
    if not x_pos is None:
        if y_pos is None or z_pos is None:
            start_pos = services.active_lot().get_default_position()
    else:
        start_pos = sims4.math.Vector3(x_pos, y_pos, z_pos)
    if max_search_distance is None:
        max_search_distance = 100
    if obj is not None:
        pos_increment_info = placement.PositionIncrementInfo(position_increment=pos_increment, from_exception=False)
        starting_location = placement.create_starting_location(position=start_pos)
        fgl_context = placement.create_fgl_context_for_object(starting_location, obj, max_distance=max_search_distance,
          position_increment_info=pos_increment_info)
        position, orientation, _ = fgl_context.find_good_location()
        if position is None:
            sim = get_optional_target(None, _connection)
            if sim is not None:
                obj.transform = sims4.math.Transform(sim.position)
            else:
                obj.transform = sims4.math.Transform(start_pos)
        else:
            obj.transform = sims4.math.Transform(position, orientation)
        return True
    return False


@sims4.commands.Command('objects.create_multiple_objects', 'objects.make_it_rain')
def create_multiple_objects(number: int, *obj_ids, _connection=None):
    manager = services.object_manager()
    sim = get_optional_target(None, _connection)
    if sim is not None:
        starting_position = sim.position
        routing_surface = sim.routing_surface
    else:
        lot = services.active_lot()
        starting_position = lot.position
        routing_surface = routing.SurfaceIdentifier(services.current_zone().id, 0, routing.SurfaceType.SURFACETYPE_WORLD)
    with postures.posture_graph.supress_posture_graph_build():
        for obj_id in obj_ids:
            obj_id = int(obj_id)
            original_obj = None
            if obj_id in manager:
                original_obj = manager.get(obj_id)
            if original_obj is None:
                return
            obj_definition_id = original_obj.definition.id
            created_obj_count = number
            while created_obj_count > 0:
                if original_obj.crafting_component is not None:
                    obj = create_craftable(original_obj.crafting_component._crafting_process.recipe, sim)
                else:
                    obj = objects.system.create_object(obj_definition_id)
                if obj is not None:
                    starting_location = placement.create_starting_location(position=starting_position)
                    fgl_context = placement.create_fgl_context_for_object(starting_location, obj)
                    position, orientation, _ = fgl_context.find_good_location()
                    if position is not None and orientation is not None:
                        obj.move_to(translation=position, orientation=orientation,
                          routing_surface=routing_surface)
                    else:
                        obj.destroy(source=obj, cause='Failed to find good location for create_multiple_objects')
                created_obj_count -= 1


@sims4.commands.Command('objects.create_multiple_objects_from_definition')
def create_multiple_objects_from_definition(number: int, *obj_defs, _connection=None):
    created_objs = []
    obj_ids = []
    try:
        for obj_def in obj_defs:
            obj = objects.system.create_object(obj_def)
            if obj is not None:
                created_objs.append(obj)
                obj_ids.append(obj.id)

        create_multiple_objects(number, *obj_ids, **{'_connection': _connection})
    finally:
        for obj in created_objs:
            obj.destroy(source=obj, cause='Destroying original objects in create_multiple_objects_from_definition')


@sims4.commands.Command('objects.create_all_carryables')
def create_all_carryables(_connection=None):
    carryable_component_name = 'carryable'
    done = False
    created_objs = []
    obj_ids = []
    try:
        definition_manager = services.definition_manager()
        for obj_def in definition_manager.loaded_definitions:
            obj_tuning = obj_def.cls
            carryable_component = obj_tuning._components.get(carryable_component_name)
            if carryable_component is None:
                continue
            try:
                obj = objects.system.create_object(obj_def)
            except:
                obj = None

            if obj is not None:
                created_objs.append(obj)
                obj_ids.append(obj.id)
            if done:
                break

        create_multiple_objects(1, *obj_ids, **{'_connection': _connection})
    finally:
        for obj in created_objs:
            obj.destroy(source=obj, cause='Destroying original objects in create_all_carryables.')


@sims4.commands.Command('objects.set_as_head', command_type=(sims4.commands.CommandType.Cheat))
def set_as_head(obj_id=None, scale=None, forward_rot=None, up_rot=None, _connection=None):
    sim = get_optional_target(None, _connection)
    if sim is None:
        return
    else:
        original_obj = obj_id.get_target()
        if original_obj is None:
            return
            if original_obj.is_sim:
                sims4.commands.output('Cannot set a Sim as your head.', _connection)
                return
            obj_definition_id = original_obj.definition.id
            if original_obj.crafting_component is not None:
                obj = create_craftable(original_obj.crafting_component._crafting_process.recipe, sim)
        else:
            obj = objects.system.create_object(obj_definition_id)
    if obj is None:
        return
    if scale is None:
        head_width = 0.75
        default_object_width = head_width / 4
        polygon = obj.footprint_polygon
        if len(polygon) > 1:
            polygon2 = list(polygon)[1:]
            polygon2.append(polygon[-1])
            object_width_x = max([abs(x - y).x for x, y in zip(polygon2, polygon)])
            object_width_z = max([abs(x - y).z for x, y in zip(polygon2, polygon)])
            object_width = min((object_width_x, object_width_z))
        else:
            object_width = default_object_width
        new_scale = head_width / object_width
        obj.scale = new_scale
    else:
        obj.scale = scale
    forward_rot = 4 * sims4.math.PI / 3 if forward_rot is None else forward_rot
    up_rot = 3 * sims4.math.PI / 2 if up_rot is None else up_rot
    forward_orientation = sims4.math.Quaternion.from_axis_angle(forward_rot, sims4.math.FORWARD_AXIS)
    up_orientation = sims4.math.Quaternion.from_axis_angle(up_rot, sims4.math.UP_AXIS)
    orientation = sims4.math.Quaternion.concatenate(forward_orientation, up_orientation)
    new_transform = sims4.math.Transform.IDENTITY()
    new_transform.orientation = orientation
    neck_hash = sims4.hash_util.hash32('b__neck__')
    if sim.current_object_set_as_head is not None:
        if sim.current_object_set_as_head() is not None:
            sim.current_object_set_as_head().destroy(source=sim, cause='Destroying existing object set as head when setting new one.')
    sim.current_object_set_as_head = weakref.ref(obj)
    obj.set_parent(sim, transform=new_transform, joint_name_or_hash=neck_hash)


@sims4.commands.Command('objects.remove_object_set_as_head', command_type=(sims4.commands.CommandType.Cheat))
def remove_object_set_as_head(_connection=None):
    sim = get_optional_target(None, _connection)
    if sim is None:
        return
    if sim.current_object_set_as_head is not None:
        if sim.current_object_set_as_head() is not None:
            sim.current_object_set_as_head().destroy(source=sim, cause='Removing object set as head')
    sim.current_object_set_as_head = None


@sims4.commands.Command('objects.teleport')
def teleport_object(obj_id: int=None, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    if obj is None:
        return
    ot = obj.get_component(types.OBJECT_TELEPORTATION_COMPONENT)
    if ot is not None:
        ot.teleport(None)


@sims4.commands.Command('objects.reset', command_type=(sims4.commands.CommandType.Cheat))
def reset(obj_id: int=None, expected: bool=True, _connection=None):
    return objects.system.reset_object(obj_id, expected=expected, cause='Command')


@sims4.commands.Command('objects.destroy', command_type=(sims4.commands.CommandType.Automation))
def destroy_objects(*obj_ids, _connection=None):
    result = True
    for obj_id in obj_ids:
        obj_id = int(obj_id, 0)
        obj = objects.system.find_object(obj_id, include_props=True)
        if obj is None:
            result = False
            continue
        obj.destroy(source=obj, cause='Destroyed requested objects in destroy_objects command.')
        if obj.is_sim:
            obj.client.selectable_sims.notify_dirty()

    return result


@sims4.commands.Command('objects.destroy_children')
def destroy_object_children(obj_id: int=None, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    if obj is None:
        return
    for child in list(obj.children):
        child.destroy(source=obj, cause='Destroy children requested by destroy_object_children command')


@sims4.commands.Command('objects.gsi_create_obj', command_type=(sims4.commands.CommandType.Automation))
def gsi_create_object(def_id, x_pos=None, y_pos=None, z_pos=None, _connection=None):
    obj = objects.system.create_object(def_id)
    if not x_pos is None:
        if y_pos is None or z_pos is None:
            sim = get_optional_target(None, _connection)
            if sim is not None:
                start_pos = sim.position
            else:
                start_pos = services.current_zone().lot.center
    else:
        start_pos = sims4.math.Vector3(x_pos, y_pos, z_pos)
    if obj is not None:
        household = services.owning_household_of_active_lot()
        if household is not None:
            obj.set_household_owner_id(household.id)
        else:
            starting_location = placement.create_starting_location(position=start_pos)
            fgl_context = placement.create_fgl_context_for_object(starting_location, obj, max_distance=100)
            position, orientation, _ = fgl_context.find_good_location()
            if position is None:
                obj.transform = sims4.math.Transform(start_pos)
            else:
                obj.transform = sims4.math.Transform(position, orientation)
        return True
    return False


def get_all_object_variants(def_id, match_pack=True, match_tuning_id=True, match_catalog_name=True, match_debug_name=None):
    all_variants = []
    main_key = sims4.resources.Key(sims4.resources.Types.OBJECTDEFINITION, def_id, 0)
    main_pack_id = build_buy.get_object_pack_by_key(main_key.type, main_key.instance, main_key.group)
    main_tuning_file_id = services.definition_manager().get_tuning_file_id(main_key.instance)
    main_catalog_name = build_buy.get_object_catalog_name(main_key.instance)
    for key in sorted(sims4.resources.list(type=(sims4.resources.Types.OBJECTDEFINITION))):
        catalog_name = build_buy.get_object_catalog_name(key.instance)
        if catalog_name is not None:
            pack_id = build_buy.get_object_pack_by_key(key.type, key.instance, key.group)
            tuning_file_id = services.definition_manager().get_tuning_file_id(key.instance)
            debug_name = sims4.resources.get_debug_name(key, table_type=(sims4.hash_util.KEYNAMEMAPTYPE_OBJECTINSTANCES))
            if pack_id is not None and tuning_file_id is not None:
                if not match_pack or main_pack_id == pack_id:
                    if not match_tuning_id or main_tuning_file_id == tuning_file_id:
                        if not match_catalog_name or main_catalog_name == catalog_name:
                            if match_debug_name is None or debug_name.endswith(match_debug_name):
                                all_variants.append(key.instance)

    return all_variants


OBJECT_PLACEMENT_PADDING = 0.5
UP_OFFSET = 5
MINIMUM_DEPTH_OFFSET = 1
last_corner_pos = None
last_largest_depth = None

def create_objects_in_grid(obj_def_list, start_pos_x=None, start_pos_z=None, grid_size_x=None, grid_size_z=None):
    global last_corner_pos
    global last_largest_depth
    lot_corners = services.current_zone().lot.corners
    corner_pos = min(lot_corners, key=(lambda c: (c.x, c.z)))
    if start_pos_x is not None:
        if start_pos_z is not None:
            corner_pos.x = start_pos_x
            corner_pos.z = start_pos_z
    lot_x_size = services.current_zone().lot.size_x
    lot_z_size = services.current_zone().lot.size_z
    if grid_size_x is not None:
        if grid_size_z is not None:
            lot_x_size = grid_size_x
            lot_z_size = grid_size_z
    lot_x_max = corner_pos.x + lot_x_size
    lot_z_max = corner_pos.z + lot_z_size
    start_x = corner_pos.x
    start_z = corner_pos.z
    largest_depth_offset = 0
    if last_corner_pos is not None:
        corner_pos = last_corner_pos
    if last_largest_depth is not None:
        largest_depth_offset = last_largest_depth
    household = services.owning_household_of_active_lot()
    for def_id in obj_def_list:
        obj = objects.system.create_object(def_id)
        if obj is not None:
            bounding_box = obj.get_bounding_box()
            obj_width = abs(bounding_box.a.x) + abs(bounding_box.b.x)
            obj_depth = abs(bounding_box.a.y) + abs(bounding_box.b.y)
            if obj_width == 0:
                if obj_depth == 0:
                    placement_footprint = placement.get_accurate_placement_footprint_polygon(obj.position, obj.orientation, obj.scale, obj.get_footprint())
                    lower_bound, upper_bound = placement_footprint.bounds()
                    obj_width = abs(upper_bound.x) + abs(lower_bound.x)
                    obj_depth = abs(upper_bound.z) + abs(lower_bound.z)
            x_offset = obj_width / 2 + OBJECT_PLACEMENT_PADDING
            corner_pos.x += obj_width / 2
            if household is not None:
                obj.set_household_owner_id(household.id)
            if obj_depth > largest_depth_offset:
                largest_depth_offset = obj_depth
            if corner_pos.x + x_offset >= lot_x_max:
                offset = max(MINIMUM_DEPTH_OFFSET, largest_depth_offset / 2)
                corner_pos.z += offset + OBJECT_PLACEMENT_PADDING
                if corner_pos.z > lot_z_max:
                    corner_pos.y += UP_OFFSET
                    corner_pos.z = start_z
                largest_depth_offset = 0
                corner_pos.x = start_x + obj_width / 2
            obj.move_to(translation=corner_pos, orientation=(obj.orientation), routing_surface=(obj.routing_surface))
            corner_pos.x += x_offset

    last_corner_pos = corner_pos
    last_largest_depth = largest_depth_offset


@sims4.commands.Command('objects.gsi_reset_grid_coordinates')
def gsi_reset_grid_coordinates(_connection=None, command_type=sims4.commands.CommandType.Automation):
    global last_corner_pos
    last_corner_pos = None
    last_largest_depth = None
    return True


@sims4.commands.Command('objects.gsi_create_objs_from_pack', command_type=(sims4.commands.CommandType.Automation))
def gsi_create_all_pack_objs(def_id: int, _connection=None):
    all_objs = get_all_object_variants(def_id, match_tuning_id=False, match_catalog_name=False, match_debug_name='set1#')
    if all_objs:
        create_objects_in_grid(all_objs)
        return True
    return False


@sims4.commands.Command('objects.gsi_create_obj_and_variants', command_type=(sims4.commands.CommandType.Automation))
def gsi_create_object_and_variants(def_id: int, _connection=None):
    all_variants = get_all_object_variants(def_id)
    if all_variants:
        create_objects_in_grid(all_variants)
        return True
    return False


@sims4.commands.Command('objects.gsi_create_obj_in_inventory', command_type=(sims4.commands.CommandType.Automation))
def gsi_create_object_in_inv(def_id: int, quantity: int=1, _connection=None):
    sim = get_optional_target(None, _connection)
    if sim is None:
        sims4.commands.output('gsi_create_object_in_inv failed: There is no currently selected Sim to place the object in.', _connection)
        return
    household = services.owning_household_of_active_lot()
    for _ in range(quantity):
        obj = objects.system.create_object(def_id)
        if obj is None:
            sims4.commands.output('gsi_create_object_in_inv failed: cannot create object with def: {}'.format(def_id), _connection)
            return
        if household is not None:
            obj.set_household_owner_id(household.id)
        sim.inventory_component.system_add_object(obj)


@sims4.commands.Command('objects.fade_and_destroy')
def fade_and_destroy_object(obj_id: RequiredTargetParam, fade_duration: float=1.0, _connection=None):
    obj = obj_id.get_target()
    if obj is None:
        return False
    obj.destroy(source=obj, cause='fade_and_destroy command', fade_duration=fade_duration)
    return True


@sims4.commands.Command('objects.clear_lot', 'objects.destroy_all')
def destroy_all_objects(_connection=None):
    with supress_posture_graph_build():
        all_objects = list(itertools.chain(services.object_manager().objects, services.prop_manager().objects))
        for obj in all_objects:
            if obj.persistence_group != objects.persistence_groups.PersistenceGroups.SIM:
                obj.destroy(source=obj, cause='destroy_all_objects command')

        return True


@sims4.commands.Command('objects.clear_minor')
def destroy_all_objects_with_less_area_than(max_area=0.25, _connection=None):
    with supress_posture_graph_build():
        all_objects = list(itertools.chain(services.object_manager().objects, services.prop_manager().objects))
        for obj in all_objects:
            if isinstance(obj, PropObject):
                obj.destroy(source=obj, cause='Prop in destroy_all_objects_with_less_area_than command')
            elif obj.persistence_group != objects.persistence_groups.PersistenceGroups.SIM:
                poly = obj.footprint_polygon
            if poly and poly.area() < max_area:
                obj.destroy(source=obj, cause='Too small in destroy_all_objects_with_less_area_than command')

    return True


@sims4.commands.Command('objects.destroy_random', command_type=(sims4.commands.CommandType.Automation))
def destroy_random_objects(count: int=1, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    with supress_posture_graph_build():
        all_objects = list(itertools.chain(services.object_manager().objects, services.prop_manager().objects))
        non_sim_objects = list((obj for obj in all_objects if obj.persistence_group != objects.persistence_groups.PersistenceGroups.SIM))
        count = min(count, len(non_sim_objects))
        to_kill = random.sample(non_sim_objects, count)
        for obj in to_kill:
            obj.destroy(source=obj, cause='destroy_random_objects command')

        output('{}/{} objects destroyed!'.format(len(to_kill), len(non_sim_objects)))
    return True


@sims4.commands.Command('objects.set_build_buy_lockout_state')
def set_build_buy_lockout_state(opt_obj: OptionalTargetParam=None, lockout_state: bool=None, lockout_timer: int=None, _connection=None):
    obj = get_optional_target(opt_obj, _connection)
    if obj is None:
        return False
    if lockout_state is None:
        lockout_state = not obj.build_buy_lockout
    obj.set_build_buy_lockout_state(lockout_state, lockout_timer)


@sims4.commands.Command('objects.set_position', command_type=(sims4.commands.CommandType.Automation))
def set_position(obj_id, x=0, y=0, z=0, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('set_position: Object ID not in the object manager.', _connection)
    if obj is not None:
        location = obj.location.clone(translation=(sims4.math.Vector3(x, y, z)))
        obj.location = location


@sims4.commands.Command('objects.set_tint')
def set_tint(obj_id, r=1.0, g=1.0, b=1.0, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('SET_TINT: Object ID not in the object manager.', _connection)
    if obj is not None:
        tint = sims4.color.from_rgba(r, g, b)
        obj.tint = tint


@sims4.commands.Command('objects.set_opacity')
def set_opacity(obj_id: int, a: float=1.0, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('SET_OPACITY: Object ID not in the object manager.', _connection)
    if obj is not None:
        obj.opacity = a


@sims4.commands.Command('objects.fade_opacity')
def fade_opacity(obj_id: int, opacity: float=1.0, duration: float=0.0, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('FADE_OPACITY: Object ID not in the object manager.', _connection)
    if obj is not None:
        obj.fade_opacity(opacity, duration)


@sims4.commands.Command('objects.set_painting_state')
def set_painting_state(obj_id, texture_name_or_hash, reveal_level=0, use_overlay=False, effect=sims4.math.MAX_UINT32, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('SET_PAINTING_STATE: Object ID not in the object manager.', _connection)
    if obj is not None:
        if obj.canvas_component is not None:
            if texture_name_or_hash is None:
                painting_state = None
            else:
                if type(texture_name_or_hash) is str:
                    painting_state = PaintingState.from_name(texture_name_or_hash, reveal_level, use_overlay, effect)
                else:
                    painting_state = PaintingState(texture_name_or_hash, reveal_level, use_overlay, effect)
            obj.canvas_component.painting_state = painting_state


@sims4.commands.Command('objects.set_light_dimmer')
def set_light_dimmer(obj_id: int, a: float=1.0, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('SET_LIGHT_DIMMER: Object ID not in the object manager.', _connection)
        return False
        if not obj.lighting_component:
            sims4.commands.output("SET_LIGHT_DIMMER: Object doesn't have a lighting component so the light dimmer can't be set.", _connection)
            return False
        obj.set_light_dimmer_value(a)


@sims4.commands.Command('objects.add_censor')
def add_censor(obj_id: int, mode: str=None, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('ADD_CENSOR: Object ID not in the object manager.', _connection)
    if obj is not None:
        mode = mode.upper()
        if mode.startswith('CENSOR_'):
            mode = mode[7:]
        elif mode in CensorState:
            handle = obj.censorgrid_component.add_censor(CensorState[mode])
            sims4.commands.output('Censor created with handle: {}'.format(handle), _connection)
        else:
            sims4.commands.output('Unknown censor mode name: ' + mode, _connection)


@sims4.commands.Command('objects.remove_censor')
def remove_censor(obj_id: int, handle: int=None, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('REMOVE_CENSOR: Object ID not in the object manager.', _connection)
    if obj is not None:
        obj.censorgrid_component.remove_censor(handle)


@sims4.commands.Command('objects.set_geometry_state')
def set_geometry_state(obj_id: int, state_name='', _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('SET_GEOMETRY_STATE: Object ID not in the object manager.', _connection)
    if obj is not None:
        obj.geometry_state = state_name


@sims4.commands.Command('objects.set_visibility')
def set_visibility(obj_id, visibility=True, inherits=False, enable_drop_shadow=False, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('SET_VISIBILITY: Object ID not in the object manager.', _connection)
    if obj is not None:
        obj.visibility = VisibilityState(visibility, inherits, enable_drop_shadow)


@sims4.commands.Command('objects.set_material_state')
def set_material_state(obj_id: int, state_name='', a: float=1.0, t: float=0.0, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('SET_MATERIAL_STATE: Object ID not in the object manager.', _connection)
    if obj is not None:
        obj.material_state = MaterialState(state_name, a, t)


@sims4.commands.Command('objects.set_material_variant')
def set_material_variant(obj_id: int, state_name='', _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('SET_MATERIAL_VARIANT: Object ID not in the object manager.', _connection)
    if obj is not None:
        variant_hash = str(sims4.hash_util.hash32(state_name))
        obj.material_variant = variant_hash


@sims4.commands.Command('objects.set_object_definition')
def set_object_definition(obj_id: int, definition_id: int, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('SET_OBJECT_DEFINITION: Object ID not in the object manager.', _connection)
    if obj is not None:
        if not obj.set_definition(definition_id):
            sims4.commands.output("SET_OBJECT_DEFINITION: requested new definition isn't similar to current", _connection)


@sims4.commands.Command('objects.show_crafting_cache')
def show_crafting_cache(_connection=None):
    manager = services.object_manager()
    for crafting_type, ref_count in manager.crafting_cache:
        sims4.commands.output('{} -> {}'.format(crafting_type, ref_count), _connection)


@sims4.commands.Command('objects.show_lockouts')
def show_lockouts(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        sims4.commands.output('Standard Lockouts:', _connection)
        for obj, end_time in sim._lockouts.items():
            sims4.commands.output('  {} -> {}'.format(obj, end_time), _connection)

        sims4.commands.output('Crafting Lockouts:', _connection)
        for obj, crafting_lockout_data in sim._crafting_lockouts.items():
            sims4.commands.output('  {}:'.format(obj), _connection)
            for crafting_type, ref_count in crafting_lockout_data._crafting_lockout_ref_counts.items():
                sims4.commands.output('    {} -> {}'.format(crafting_type, ref_count), _connection)

    else:
        sims4.commands.output('No target for objects.show_lockouts.', _connection)


@sims4.commands.Command('objects.clear_lockouts')
def clear_lockouts(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        sim.clear_all_lockouts()
    else:
        sims4.commands.output('No target for objects.clear_lockouts.', _connection)


@sims4.commands.Command('objects.clear_crafting_autonomoy_cache')
def clear_autonomous_crafting_cache(_connection=None):
    services.object_manager().crafting_cache.clear()


@sims4.commands.Command('animal_objects.clear_animal_gift_preference_knowledge')
def clear_animal_gift_preference_knowledge(_connection=None):
    for animal_obj in services.object_manager().get_all_objects_with_component_gen(objects.components.types.ANIMAL_PREFERENCE_COMPONENT):
        if animal_obj.animalpreference_component:
            animal_obj.animalpreference_component.clear_preference_knowledge()


@sims4.commands.Command('animal_objects.reset_animal_gift_preference_cooldowns')
def reset_animal_gift_preference_cooldowns(_connection=None):
    for animal_obj in services.object_manager().get_all_objects_with_component_gen(objects.components.types.ANIMAL_PREFERENCE_COMPONENT):
        if animal_obj.animalpreference_component:
            animal_obj.animalpreference_component.reset_preference_cooldowns()


@sims4.commands.Command('discouragement_regions.enable')
def discouragement_regions_enable(_connection=None):
    import sims4.geometry
    sims4.geometry.PolygonFootprint.set_global_enabled(True)
    return True


@sims4.commands.Command('discouragement_regions.disable')
def discouragement_regions_disable(_connection=None):
    import sims4.geometry
    sims4.geometry.PolygonFootprint.set_global_enabled(False)
    return True


@sims4.commands.Command('objects.toggle_lockout_visualization')
def toggle_lockout_visualization(_connection=None):
    objects.base.lockout_visualization = not objects.script_object.lockout_visualization
    sims4.commands.output('Lockout visualization: {}'.format(objects.script_object.lockout_visualization), _connection)
    return True


@sims4.commands.Command('objects.current_value')
def object_current_value(obj_id: int, new_value: int=None, _connection=None):
    output = sims4.commands.Output(_connection)
    obj = services.object_manager()[obj_id]
    output('Current value: {}'.format(obj.current_value))
    if new_value is not None:
        obj.current_value = new_value
        output('New value: {}'.format(obj.current_value))
    return True


@sims4.commands.Command('objects.focus_camera_on_object', command_type=(sims4.commands.CommandType.Live))
def focus_camera_on_object(obj_id: int, _connection=None):
    manager = services.object_manager()
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('Object ID not in the object manager.', _connection)
        return
        if obj is not None:
            client = services.client_manager().get(_connection)
            camera.focus_on_position(obj.position, client)


@sims4.commands.Command('objects.add_stored_sim')
def object_add_stored_sim_info(obj: RequiredTargetParam=None, sim_id: OptionalTargetParam=None, _connection=None):
    obj = obj.get_target()
    sim = get_optional_target(sim_id, _connection)
    if obj is not None:
        if sim is not None:
            obj.add_dynamic_component((types.STORED_SIM_INFO_COMPONENT), sim_id=(sim.id))
            return True
    return False


@sims4.commands.Command('objects.get_inventory_counts', command_type=(sims4.commands.CommandType.Live))
def get_inventory_counts(_connection=None):
    zone = services.current_zone()
    if zone is None:
        return False
    if zone.lot is None:
        return False
    inventory_counts_msg = InventoryCountUpdate()
    for inventory_type, inventory in zone.lot.get_all_object_inventories_gen():
        with ProtocolBufferRollback(inventory_counts_msg.inventory_counts) as (inventory_count_msg):
            inventory_count_msg.inventory_type = inventory_type
            inventory_count_msg.count = len(inventory)

    distributor = Distributor.instance()
    distributor.add_op_with_no_owner(GenericProtocolBufferOp(Operation.INVENTORY_COUNT_UPDATE, inventory_counts_msg))
    return True


@sims4.commands.Command('objects.set_state_value', command_type=(sims4.commands.CommandType.Automation))
def set_state_value(state_value: TunableInstanceParam(sims4.resources.Types.OBJECT_STATE), obj_id: int=None, _connection=None):
    state = state_value.state
    object_manager = services.object_manager()
    if obj_id is not None:
        obj = object_manager.get(obj_id)
        if obj is not None:
            if obj.state_component is not None:
                if obj.has_state(state):
                    obj.set_state(state, state_value)
                    return True
                sims4.commands.output('State Value {} from State {} is invalid for object {} '.format(state_value, state, obj), _connection)
                return False
    for obj in [objVal for objVal in object_manager.values()]:
        if obj.state_component is not None and obj.has_state(state):
            obj.set_state(state, state_value)

    return True


@sims4.commands.Command('objects.wait_for_state_value', command_type=(sims4.commands.CommandType.Automation))
def wait_for_state_value(state: TunableInstanceParam(sims4.resources.Types.OBJECT_STATE), required_state_value: TunableInstanceParam(sims4.resources.Types.OBJECT_STATE), target: OptionalTargetParam=None, _connection=None):
    if required_state_value is None:
        return False
        if target is None:
            return False
        obj = services.object_manager().get(target.target_id)
        if obj is None or obj.state_component is None:
            return False
        if not obj.has_state(state):
            return False
        state_value = obj.get_state(state)
        if required_state_value is state_value:
            sims4.commands.automation_output('ObjectState; Value:{0}'.format(state_value.guid64), _connection)
    else:

        def state_change_callback(owner, state, old_value, new_value):
            if new_value is required_state_value:
                sims4.commands.automation_output('ObjectState; Value:{0}'.format(required_state_value.guid64), _connection)
                owner.remove_state_changed_callback(state_change_callback)

        obj.add_state_changed_callback(state_change_callback)
    return True


@sims4.commands.Command('qa.objects.set_commodity_extreme', command_type=(sims4.commands.CommandType.Automation))
def set_commodity_extreme(commodity_value: TunableInstanceParam(sims4.resources.Types.STATISTIC), setToMin: bool=True, obj_id: int=None, _connection=None):
    object_manager = services.object_manager()
    if obj_id is not None:
        obj = object_manager.get(obj_id)
        if obj is not None:
            if obj.commodity_tracker.has_statistic(commodity_value):
                obj.commodity_tracker.set_min(commodity_value) if setToMin else obj.commodity_tracker.set_max(commodity_value)
                return True
        sims4.commands.output('Commodity Value {} is invalid for object {} '.format(commodity_value, obj), _connection)
        return False
    for obj in [objVal for objVal in object_manager.values()]:
        if obj.commodity_tracker.has_statistic(commodity_value):
            obj.commodity_tracker.set_min(commodity_value) if setToMin else obj.commodity_tracker.set_max(commodity_value)

    return True


@sims4.commands.Command('qa.objects.dirty', command_type=(sims4.commands.CommandType.Automation))
def make_dirty(obj_id: int=None, _connection=None):
    return set_commodity_extreme(ObjectCommandTuning.DIRTY_COMMODITY, True, obj_id, _connection)


@sims4.commands.Command('qa.objects.clean', command_type=(sims4.commands.CommandType.Automation))
def make_clean(obj_id: int=None, _connection=None):
    return set_commodity_extreme(ObjectCommandTuning.DIRTY_COMMODITY, False, obj_id, _connection)


@sims4.commands.Command('qa.objects.break', command_type=(sims4.commands.CommandType.Automation))
def make_broken(obj_id: int=None, _connection=None):
    return set_commodity_extreme(ObjectCommandTuning.BROKEN_COMMODITY, True, obj_id, _connection)


@sims4.commands.Command('qa.objects.fix', command_type=(sims4.commands.CommandType.Automation))
def make_fixed(obj_id: int=None, _connection=None):
    return set_commodity_extreme(ObjectCommandTuning.BROKEN_COMMODITY, False, obj_id, _connection)


@sims4.commands.Command('qa.objects.burn', command_type=(sims4.commands.CommandType.Automation))
def make_burned(obj_id: int=None, _connection=None):
    ashRetVal = set_state_value(ObjectCommandTuning.BURNED_ASH_STATE, obj_id, _connection)
    matChangeRetVal = set_state_value(ObjectCommandTuning.BURNED_MATERIAL_STATE, obj_id, _connection)
    return ashRetVal and matChangeRetVal


@sims4.commands.Command('objects.set_household_owner', command_type=(sims4.commands.CommandType.Automation))
def set_household_owner(obj_id: int=None, household_id: int=None, _connection=None):
    if obj_id is None:
        sims4.commands.output('Usage: objects.set_household_owner <obj_id> optional:<household_id>: No obj_id provided', _connection)
        return False
    selected_obj = services.object_manager().get(obj_id)
    if selected_obj is None:
        sims4.commands.output('Usage: objects.set_household_owner <obj_id> optional:<household_id>: obj_id is not in the object manager', _connection)
        return False
    current_zone = services.current_zone()
    if household_id is None:
        household_id = current_zone.lot.owner_household_id
    household = services.household_manager().get(household_id)
    if household is None:
        sims4.commands.output('Usage: objects.set_household_owner <obj_id> optional:<household_id>: Could not find household({})'.format(household_id), _connection)
        return False
    selected_obj.set_household_owner_id(household_id)
    return True


@sims4.commands.Command('objects.get_users', command_type=(sims4.commands.CommandType.Automation))
def get_object_use_list(obj_id: int=None, _connection=None):
    if obj_id is None:
        sims4.commands.output('Usage: objects.get_users <obj_id>: No obj_id provided', _connection)
        return False
    current_zone = services.current_zone()
    selected_obj = current_zone.find_object(obj_id)
    if selected_obj is None:
        sims4.commands.output('Usage: objects.get_users <obj_id>: obj_id is not in the object manager or inventory manager.', _connection)
        return False
    object_users = selected_obj.get_users(sims_only=True)
    user_strs = []
    for index, reserver in enumerate(object_users):
        user_strs.append('SimId{}:{}'.format(index, reserver.id))

    use_list_str = 'ObjectUserList; ObjectId:{}, NumUsers:{}, {}'.format(obj_id, len(object_users), ', '.join(user_strs))
    sims4.commands.automation_output(use_list_str, _connection)
    sims4.commands.output(use_list_str, _connection)


@sims4.commands.Command('objects.print_transform', command_type=(sims4.commands.CommandType.Cheat))
def print_object_transform(obj_id: int=None, _connection=None):
    if obj_id is None:
        sims4.commands.output('Usage: objects.print_object_transform <obj_id>: No obj_id provided', _connection)
        return False
    else:
        current_zone = services.current_zone()
        selected_obj = current_zone.find_object(obj_id)
        if selected_obj is None:
            sims4.commands.output('Usage: objects.get_users <obj_id>: obj_id is not in the object manager or inventory manager.', _connection)
            return False
        sims4.commands.output(str(selected_obj.transform), _connection)
        return selected_obj.parts or None
    for part in selected_obj.parts:
        sims4.commands.output('Part[{}]: {}'.format(part.part_suffix, part.transform), _connection)


@sims4.commands.Command('objects.consumables_infinite_toggle', command_type=(sims4.commands.CommandType.Cheat))
def make_consumables_infinite(_connection=None):
    consumable_component.debug_consumables_are_infinite = not consumable_component.debug_consumables_are_infinite
    if consumable_component.debug_consumables_are_infinite:
        message = 'All consumables have infinite contents!'
    else:
        message = 'All consumables are again ordinary and thus boring.'
    sims4.commands.output(message, _connection)


@sims4.commands.Command('qa.objects.consumables_infinite_toggle', command_type=(sims4.commands.CommandType.Automation))
def qa_make_consumables_infinite(_connection=None):
    consumable_component.debug_consumables_are_infinite = not consumable_component.debug_consumables_are_infinite


@sims4.commands.Command('objects.consumable_make_spoiled', command_type=(sims4.commands.CommandType.Automation))
def make_consumable_spoiled(obj_id: int, _connection=None):
    current_zone = services.current_zone()
    selected_obj = current_zone.find_object(obj_id)
    if selected_obj is None:
        sims4.commands.output('Usage: objects.consumable_make_spoiled <obj_id>: obj_id is not in the object manager or inventory manager.', _connection)
        return False
    selected_obj.set_state(CraftingTuning.FRESHNESS_STATE, CraftingTuning.SPOILED_STATE_VALUE)


@sims4.commands.Command('objects.request_customizable_object_data', command_type=(sims4.commands.CommandType.Live))
def request_customizable_object_data(*object_ids: int, _connection=None):
    manager = services.object_manager()
    objects = []
    for obj_id in object_ids:
        obj_id = int(obj_id)
        obj = None
        if obj_id in manager:
            obj = manager.get(obj_id)
        if obj is None:
            continue
        if obj.has_tag(GalleryGameplayTuning.EXPORT_SAVE_DATA_TO_GALLERY_TAG):
            objects.append(obj)

    custom_data_list = distributor.ops.CustomizableObjectDataList(objects)
    distributor_system = Distributor.instance()
    distributor_system.add_op_with_no_owner(custom_data_list)


@sims4.commands.Command('objects.replace_with_random', command_type=(sims4.commands.CommandType.Cheat))
def replace_object_with_random(obj_id: RequiredTargetParam=None, num_tries: int=0, error_margin: int=50):
    original_obj = obj_id.get_target()
    if original_obj is None:
        return
    new_obj_def = build_buy.get_replacement_object(services.current_zone().id, original_obj.id, num_tries, error_margin)
    if new_obj_def is not None:
        position = original_obj.position
        orientation = original_obj.orientation
        routing_surface = original_obj.routing_surface
        original_obj.destroy()
        new_obj = objects.system.create_object(new_obj_def)
        new_obj.move_to(routing_surface=routing_surface, translation=position, orientation=orientation)


@sims4.commands.Command('objects.notify_image_composited', command_type=(sims4.commands.CommandType.Live))
def notify_image_composited(obj_id, resource_key, resource_key_type, resource_key_group, no_op_version, _connection=None):
    obj = services.current_zone().find_object(obj_id)
    if obj is None:
        sims4.commands.output('Notify Image Composited could not find object: {} '.format(obj_id), _connection)
        return
    canvas_component = obj.canvas_component
    if canvas_component is None:
        sims4.commands.output('Notify Image Composited object: {} does not have a family portrait component.'.format(obj_id), _connection)
        return
    canvas_component.set_composite_image(resource_key, resource_key_type, resource_key_group, no_op_version)


@sims4.commands.Command('objects.notify_image_composite_failed', command_type=(sims4.commands.CommandType.Live))
def notify_image_composite_failed(obj_id: int, _connection=None):
    object_manager = services.object_manager()
    obj = object_manager.get(obj_id)
    if obj is None:
        sims4.commands.output('Notify Image Composite Failed could not find object: {} '.format(obj_id), _connection)
        return
    canvas_component = obj.canvas_component
    if canvas_component is None:
        sims4.commands.output('Notify Image Composite Failed object: {} does not have a portrait component.'.format(obj_id), _connection)
        return


@sims4.commands.Command('objects.lock_door', command_type=(sims4.commands.CommandType.Cheat))
def lock_door(obj_id: RequiredTargetParam=None, _connection=None):
    door_obj = obj_id.get_target()
    if door_obj is None:
        sims4.commands.output('Lock door fail! No door object selected!', _connection)
        return
    door_obj.lock()


@sims4.commands.Command('objects.unlock_door', command_type=(sims4.commands.CommandType.Cheat))
def unlock_door(obj_id: RequiredTargetParam=None, _connection=None):
    door_obj = obj_id.get_target()
    if door_obj is None:
        sims4.commands.output('Unlock door fail! No door object selected!', _connection)
        return
    door_obj.unlock()


@sims4.commands.Command('objects.lock_all_doors', command_type=(sims4.commands.CommandType.Cheat))
def lock_all_doors(_connection=None):
    object_manager = services.object_manager()
    for portal in object_manager.portal_cache_gen():
        portal.lock()


@sims4.commands.Command('objects.unlock_all_doors', command_type=(sims4.commands.CommandType.Cheat))
def unlock_all_doors(_connection=None):
    object_manager = services.object_manager()
    for portal in object_manager.portal_cache_gen():
        portal.unlock()


@sims4.commands.Command('objects.update_display_number', command_type=(sims4.commands.CommandType.Cheat))
def update_display_number(obj_id: int, *display_numbers, _connection=None):
    obj_mgr = services.object_manager()
    obj = obj_mgr.get(obj_id)
    if obj is None:
        sims4.commands.output('update_display_number! No object selected!', _connection)
        return
    number_list = None if not display_numbers else [int(number) for number in display_numbers]
    obj.update_display_number(display_number=number_list)


@sims4.commands.Command('objects.set_voice_actor', command_type=(sims4.commands.CommandType.Cheat))
def set_voice_actor(obj_id: int, voice_actor: str, _connection=None):
    obj_mgr = services.object_manager()
    obj = obj_mgr.get(obj_id)
    if obj is None:
        sims4.commands.output('No object selected', _connection)
        return
    msg = SetVoiceActor(sims4.hash_util.hash32(voice_actor))
    distributor = Distributor.instance()
    distributor.add_op(obj, msg)


@sims4.commands.Command('objects.set_modular_pieces')
def set_modular_pieces(obj_id: RequiredTargetParam=None, *obj_ids, _connection=None):
    modular_obj = obj_id.get_target()
    if modular_obj is None:
        sims4.commands.output('Modular piece fail, no such object {}'.format(obj_id.target_id), _connection)
        return
    modular_obj.set_modular_pieces((tuple((int(piece_id, base=0) for piece_id in obj_ids))), from_load=True)


@sims4.commands.Command('objects.add_stored_sim_location')
def object_add_stored_sim_location(obj: RequiredTargetParam=None, sim_id: OptionalTargetParam=None, _connection=None):
    obj = obj.get_target()
    sim = get_optional_target(sim_id, _connection)
    return add_stored_sim_location(obj, sim)


@sims4.commands.Command('objects.create_objects_in_grid_by_definition')
def create_objects_in_grid_by_definition(def_id, amount, start_pos_x=None, start_pos_z=None, grid_size_x=None, grid_size_z=None, _connection=None):
    gsi_reset_grid_coordinates(_connection)
    def_ids = [def_id] * amount
    create_objects_in_grid(def_ids, start_pos_x, start_pos_z, grid_size_x, grid_size_z)


@sims4.commands.Command('objects.wear_trendi_outfit', command_type=(sims4.commands.CommandType.Live))
def wear_trendi_outfit(inventory_obj_id: int=None, target_sim: OptionalSimInfoParam=None, set_current_outfit=False, _connection=None):
    inventory_manager = services.inventory_manager()
    sims4.commands.output('inventory_manager {}'.format(inventory_manager), _connection)
    if inventory_manager is None:
        sims4.commands.output('Inventory Manager was none', _connection)
        return False
    inventory_obj = inventory_manager.get(inventory_obj_id)
    if inventory_obj is None:
        sims4.commands.output('Object could not be retrieved and was none for id'.format(inventory_obj_id), _connection)
        return False
    if inventory_obj.mannequin_component is None:
        sims4.commands.output('ObjectId:{} does not have a mannequin component'.format(inventory_obj), _connection)
        return False
    mannequin = inventory_obj.mannequin_component
    sims4.commands.output('inventory_obj {} - {}'.format(inventory_obj, mannequin), _connection)
    sim_info = get_optional_target(opt_target=target_sim, _connection=_connection, target_type=OptionalSimInfoParam)
    if sim_info is None:
        sims4.commands.output('No valid target specified.', _connection)
        return False
    outfits = mannequin.get_outfits()
    if outfits is None:
        sims4.commands.output('there are no outfits on mannequin {}'.format(mannequin.id), _connection)
        return False
    sim_info_source = outfits.get_sim_info()
    current_outfit_category, current_outfit_index = sim_info.get_current_outfit()
    sim_info.generate_merged_outfit(sim_info_source, (
     OutfitCategory.SPECIAL, SpecialOutfitIndex.FASHION), (
     current_outfit_category, current_outfit_index), (
     OutfitCategory.EVERYDAY, 0))
    if set_current_outfit:
        sim_info.set_current_outfit((OutfitCategory.SPECIAL, SpecialOutfitIndex.FASHION))
    return True


@sims4.commands.Command('objects.stop_wearing_trendi_outfit', command_type=(sims4.commands.CommandType.Live))
def stop_wearing_trendi_outfit(target_sim: OptionalSimInfoParam=None, set_current_outfit=False, _connection=None):
    output = sims4.commands.Output(_connection)
    sim_info = get_optional_target(opt_target=target_sim, _connection=_connection, target_type=OptionalSimInfoParam)
    if sim_info is None:
        output('No valid target specified.')
        return False
    else:
        outfits = sim_info.get_outfits()
        if outfits is None:
            output('there are no outfits on sim {}'.format(sim_info.id))
            return False
            current_outfit_category, current_outfit_index = sim_info.get_current_outfit()
            previous_outfit_category, previous_outfit_index = sim_info.get_previous_outfit()
            if (
             previous_outfit_category, previous_outfit_index) == (OutfitCategory.SPECIAL, SpecialOutfitIndex.TOWEL):
                outfits.remove_outfit(OutfitCategory.SPECIAL, SpecialOutfitIndex.FASHION)
        else:
            outfits.remove_outfits_in_category(OutfitCategory.SPECIAL)
    if previous_outfit_category in REGULAR_OUTFIT_CATEGORIES or previous_outfit_category in HIDDEN_OUTFIT_CATEGORIES:
        if previous_outfit_category == current_outfit_category:
            sim_info.set_outfit_dirty(current_outfit_category)
        sim_info.set_previous_outfit((sim_info.get_previous_outfit()), force=True)
    else:
        sim_info.set_previous_outfit(sim_info.get_random_outfit(outfit_categories=(OutfitCategory.EVERYDAY,)), force=True)
    if set_current_outfit:
        sim_info.set_current_outfit(sim_info.get_previous_outfit())
    return True


@sims4.commands.Command('objects.toggle_slot', command_type=(sims4.commands.CommandType.DebugOnly))
def toggle_slot(target_param: RequiredTargetParam, slot_name: NoneIntegerOrString=None, _connection=None):
    target = target_param.get_target()
    if not target:
        output = sims4.commands.Output(_connection)
        output('Invalid Target')
        return
    else:
        slot_comp = target.slot_component
        slot_hash = sims4.hash_util.hash32(slot_name) if type(slot_name) is str else slot_name
        output = slot_name and slot_comp.has_slot(slot_hash) or sims4.commands.Output(_connection)
        output('Slot {} does not exist on {}'.format(slot_name, target))
        output('Please specify a slot name, which should be a bone from the rig and must include any subroot indices')
        object_slots = target.slots_resource
        if object_slots:
            possible_slots = set()
            for slot_index in range(object_slots.get_slot_count(sims4.ObjectSlots.SLOT_CONTAINMENT)):
                slot_hash = object_slots.get_slot_name_hash(sims4.ObjectSlots.SLOT_CONTAINMENT, slot_index)
                possible_slots.add(sims4.hash_util.unhash_with_fallback(slot_hash))

            output('Possible Slots: {}'.format(possible_slots))
        return
    slot_hashes = slot_comp.disabled_slot_hashes
    if slot_hashes and slot_hash in slot_hashes:
        slot_comp.enable_slot(slot_hash)
        output = sims4.commands.Output(_connection)
        output('Slot {} Enabled on {}'.format(slot_name, target))
    else:
        slot_comp.disable_slot(slot_hash)
        output = sims4.commands.Output(_connection)
        output('Slot {} Disabled on {}'.format(slot_name, target))