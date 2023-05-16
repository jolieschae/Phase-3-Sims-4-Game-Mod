# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\sim_commands.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 95137 bytes
import gc, math, random, sys, time
from protocolbuffers import InteractionOps_pb2 as interaction_protocol, Sims_pb2 as protocols, Consts_pb2
from protocolbuffers.DistributorOps_pb2 import Operation, SetWhimBucks
from animation.posture_manifest import Hand
from distributor.ops import GenericProtocolBufferOp
from distributor.system import Distributor
from interactions import priority
from interactions.aop import AffordanceObjectPair
from interactions.context import InteractionContext
from interactions.priority import Priority
from interactions.utils.adventure import AdventureMomentKey, set_initial_adventure_moment_key_override
from interactions.utils.satisfy_constraint_interaction import SatisfyConstraintSuperInteraction
from objects import ALL_HIDDEN_REASONS, ALL_HIDDEN_REASONS_EXCEPT_UNINITIALIZED
from objects.object_enums import ResetReason
from objects.terrain import TravelSuperInteraction
from routing import FootprintType
from server.pick_info import PickInfo, PickType
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target, RequiredTargetParam, TunableInstanceParam, OptionalSimInfoParam
from sims.genealogy_tracker import FamilyRelationshipIndex
from sims.household_enums import HouseholdChangeOrigin
from sims.loan_tuning import LoanType, LoanTunables
from sims.outfits.outfit_enums import OutfitCategory
from sims.sim_info_types import Age, Gender, Species
from sims.sim_spawner import SimSpawner, SimCreator
from sims4.geometry import PolygonFootprint, build_rectangle_from_two_points_and_radius
from sims4.tuning.tunable import TunableReference
from ui import ui_tuning
from zone import Zone
import alarms, buffs.memory, camera, cas.cas, clock, distributor.ops, interactions.priority, interactions.utils.sim_focus, objects, objects.system, placement, routing, server_commands, services
import sims.sim_info_types as sim_info_types
import sims.sim_spawner, sims4.commands, sims4.hash_util
import sims4.log as log
import sims4.math, sims4.resources, story_progression, zone_types
with sims4.reload.protected(globals()):
    _reset_alarm_handles = {}

class CommandTuning:
    TERRAIN_TELEPORT_AFFORDANCE = TunableReference(description='\n        The affordance used by the command sims.teleport to teleport the sim. This\n        command is used during GUI Smoke as well. \n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)))
    TERRAIN_GOHERE_AFFORDANCE = TunableReference(description='\n        The affordance used by the command sims.gohere to make the sim go to a\n        specific position.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)))
    TERRAIN_SWIMHERE_AFFORDANCE = TunableReference(description='\n        The affordance used by the command sims.swimhere to make the sim swim to a\n        specific position.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)))


@sims4.commands.Command('sims.get_all_instanced_sims', command_type=(sims4.commands.CommandType.Automation))
def get_all_instanced_sims(_connection=None):
    ids = []
    automation_output = sims4.commands.AutomationOutput(_connection)
    automation_output('GetInstancedSims; Status:Begin')
    for sim_info in services.sim_info_manager().values():
        sim = sim_info.get_sim_instance()
        if sim is not None:
            ids.append(sim.id)
            automation_output('GetInstancedSims; Status:Data, SimId:{}'.format(sim.id))

    automation_output('GetInstancedSims; Status:End')
    return ids


@sims4.commands.Command('sim_info.printrefs')
def print_sim_info_refs(_connection=None):
    output = sims4.commands.Output(_connection)
    output('Could not create a new household.')
    output('-------------------- Ref Counts --------------------')
    for sim_info in services.sim_info_manager().objects:
        referrers = gc.get_referrers(sim_info)
        output('SimId: {}, NumRefs: {} '.format(sim_info.sim_id, sys.getrefcount(sim_info)))
        for referrer in referrers:
            output('    SimInfo Ref Held by: {}'.format(referrer))


@sims4.commands.Command('sims.spawnmaxsims', command_type=(sims4.commands.CommandType.Automation))
def spawn_max_sims(_connection=None):
    sim_info_manager = services.sim_info_manager()
    sim_spawner_service = services.sim_spawner_service()
    instantiated_sims = sum((1 for sim in sim_info_manager.instanced_sims_gen(allow_hidden_flags=ALL_HIDDEN_REASONS) if sim.is_npc))
    instantiated_sims += len(sim_spawner_service.get_set_of_requested_sim_ids())
    num = sim_spawner_service.npc_soft_cap - instantiated_sims
    if num > 0:
        sims4.commands.output('Max Sims commmand.  {} sims requested.'.format(num), _connection)
        sims4.commands.execute('sims.spawnsimple {}'.format(num), _connection)
    else:
        sims4.commands.output('Unable to spawn more sims.  Cap has been reached.', _connection)


@sims4.commands.Command('sims.spawnsimple', command_type=(sims4.commands.CommandType.Automation), console_type=(sims4.commands.CommandType.DebugOnly))
def spawn_client_sims_simple(num=None, x=0, y=0, z=0, age=Age.ADULT, gender=None, species=Species.HUMAN, household_id=None, instantiate=True, _connection=None):
    client = services.client_manager().get(_connection)
    if household_id is None or household_id.lower() == 'new':
        household = services.household_manager().create_household(client.account)
    else:
        if household_id.lower() == 'active':
            household = services.active_household()
        else:
            household = services.household_manager().get(int(household_id))
            if household is None:
                sims4.commands.output('Unable to find household with ID {0}.'.format(household_id), _connection)
                return False
    position = sims4.math.Vector3(x, y, z) if (x and y and z) else None
    sim_creators = [SimCreator(age=age, gender=gender, species=species) for _ in range(num)]
    SimSpawner.create_sims(sim_creators, household=household, tgt_client=client, generate_deterministic_sim=True, sim_position=position,
      account=(client.account),
      is_debug=True,
      skip_offset=True,
      additional_fgl_search_flags=(placement.FGLSearchFlag.STAY_IN_SAME_CONNECTIVITY_GROUP),
      instantiate=instantiate,
      creation_source='cheat: sims.spawnsimple',
      household_change_origin=(HouseholdChangeOrigin.CHEAT_SIMS_SPAWN_SIMPLE))


@sims4.commands.Command('sims.spawn', command_type=(sims4.commands.CommandType.Automation), console_type=(sims4.commands.CommandType.DebugOnly))
def spawn_client_sim(x=0, y=0, z=0, num=1, gender=None, age=None, generate_deterministic_sim=False, household_id=None, _connection=None):
    tgt_client = services.client_manager().get(_connection)
    if tgt_client is None:
        log.info('SimInfo', 'No client found for spawn_client_sim, bailing.')
        return False
    account = tgt_client.account
    if household_id is None:
        household = tgt_client.household
    else:
        if household_id.lower() == 'new':
            tgt_client = None
            household = services.household_manager().create_household(account)
            if household is None:
                sims4.commands.output('Could not create a new household.', _connection)
                return False
        else:
            household_id = int(household_id)
            manager = services.household_manager()
            household = manager.get(household_id)
            if household is None:
                sims4.commands.output('Unable to find household with ID {0}.'.format(household_id), _connection)
                return False
            elif gender is None:
                gender = random.choice(list(sim_info_types.Gender))
            else:
                gender = gender.lower()
                if gender in ('male', 'm'):
                    gender = sim_info_types.Gender.MALE
                else:
                    if gender in ('female', 'f'):
                        gender = sim_info_types.Gender.FEMALE
                    else:
                        sims4.commands.output('Invalid gender: {0}. Valid options: male, m, female, or f.'.format(gender), _connection)
                        return False
    if age is None:
        age = sim_info_types.Age.ADULT
    else:
        age = age.upper()
        try:
            age = sim_info_types.Age[age]
        except AttributeError:
            sims4.commands.output('Invalid age: {}. Valid options: {}.'.format(age, ', '.join(sim_info_types.Age.names)), _connection)
            return False

        if age is sim_info_types.Age.ELDER:
            sims4.commands.output('There is no {} model for {} yet, sorry.'.format(str(age), str(gender)), _connection)
            return False
        position = sims4.math.Vector3(x, y, z) if (x != 0 and y != 0 and z != 0) else None
        sim_creators = [SimCreator(gender=gender, age=age) for _ in range(num)]
        SimSpawner.create_sims(sim_creators, household=household, tgt_client=tgt_client,
          generate_deterministic_sim=generate_deterministic_sim,
          sim_position=position,
          account=account,
          is_debug=True,
          creation_source='cheat: sims.spawn',
          household_change_origin=(HouseholdChangeOrigin.CHEAT_SIMS_SPAWN))
        return True


@sims4.commands.Command('sims.recreate')
def recreate_sims(opt_sim: OptionalTargetParam=None, _connection=None):
    sims_to_load = []
    if opt_sim is not None:
        sim = get_optional_target(opt_sim, _connection)
        if sim is None:
            sims4.commands.output('No valid target for stats.enable_sim_commodities', _connection)
            return
        sims_to_load.append(sim.id)
        services.object_manager().remove(sim)
    else:
        for sim_info in services.sim_info_manager().objects:
            sims_to_load.append(sim_info.id)
            services.object_manager().remove(sim_info.get_sim_instance())

    for sim_id in sims_to_load:
        SimSpawner.load_sim(sim_id)


@sims4.commands.Command('sims.add_to_family', command_type=(sims4.commands.CommandType.Cheat))
def add_to_family(opt_sim: OptionalSimInfoParam=None, opt_sim_2: OptionalSimInfoParam=None, _connection=None):
    from_household_sim = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if opt_sim_2 is not None:
        to_household_sim = get_optional_target(opt_sim_2, target_type=OptionalSimInfoParam, _connection=_connection)
    else:
        to_household_sim = None
    if (from_household_sim is None or opt_sim_2) is not None:
        if to_household_sim is None:
            sims4.commands.output('Valid SimInfos not found for sims.add_to_family.', _connection)
            return False
    household_manager = services.household_manager()
    return household_manager.switch_sim_household(from_household_sim, to_household_sim, reason=(HouseholdChangeOrigin.CHEAT))


@sims4.commands.Command('sims.remove_from_family', command_type=(sims4.commands.CommandType.Cheat))
def remove_from_family(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is not None:
        original_household = sim_info.household
        if original_household is not None:
            if original_household.household_size > 1:
                original_household.remove_sim_info(sim_info)
                sim_info.transfer_to_hidden_household()
                client = services.client_manager().get(_connection)
                if original_household is services.active_household():
                    client.remove_selectable_sim_info(sim_info)
                if sim_info.sim_id == client.active_sim.sim_id:
                    client.set_next_sim()
                log.info('SimInfo', 'Removing Sim from family: Success')
                return True
    log.info('SimInfo', 'Removing Sim from family: Failure')
    return False


@sims4.commands.Command('sims.set_name_keys', command_type=(sims4.commands.CommandType.Live))
def set_name_keys(opt_sim: OptionalTargetParam=None, first_name_key: int=0, last_name_key: int=0, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    sim.sim_info.first_name_key = first_name_key
    sim.sim_info.last_name_key = last_name_key


@sims4.commands.Command('sims.set_first_name', command_type=(sims4.commands.CommandType.Live))
def set_first_name(opt_sim: OptionalSimInfoParam=None, first_name: str='', _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is not None:
        sim_info.first_name = first_name


@sims4.commands.Command('sims.set_last_name', command_type=(sims4.commands.CommandType.Live))
def set_last_name(opt_sim: OptionalSimInfoParam=None, last_name: str='', _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is not None:
        sim_info.last_name = last_name


@sims4.commands.Command('sims.set_next', command_type=(sims4.commands.CommandType.Live))
def set_next_sim(_connection=None):
    if _connection is not None:
        tgt_client = services.client_manager().get(_connection)
        if tgt_client is not None:
            if tgt_client.set_next_sim():
                log.info('SimInfo', 'Setting next Sim: Success')
                return True
            log.info('SimInfo', 'Setting next Sim: No change')
            return False
        else:
            log.info('SimInfo', 'Setting next Sim: No client manager')
            return False


@sims4.commands.Command('sims.set_active', command_type=(sims4.commands.CommandType.Live))
def set_active_sim(sim_id: int=None, _connection=None):
    if _connection is not None:
        if sim_id is not None:
            tgt_client = services.client_manager().get(_connection)
            if tgt_client is not None:
                if tgt_client.set_active_sim_by_id(sim_id):
                    log.info('SimInfo', 'Setting active Sim to {0}: Success', sim_id)
                    sims4.commands.automation_output('SetActiveSim; Status:Success', _connection)
                    return True
            log.info('SimInfo', 'Setting active Sim: No change')
            sims4.commands.automation_output('SetActiveSim; Status:NoChange', _connection)
            return True
    log.info('SimInfo', 'Incorrect number of parameters to set_active_sim.')
    sims4.commands.automation_output('SetActiveSim; Status:ParamError', _connection)
    return False


@sims4.commands.Command('sims.destroy_all_household_sims_but_active_sim', command_type=(sims4.commands.CommandType.Automation))
def destroy_all_household_sims_but_active_sim(*args, _connection=None):
    client = services.client_manager().get(_connection)
    if client is not None:
        household = services.active_household()
        for sim_info in tuple(household):
            if sim_info is client.active_sim_info:
                continue
            sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if sim:
                sim.reset(ResetReason.RESET_EXPECTED, None, 'Command')
                sim.destroy(source=sim, cause='Destroyed sim via command.')
            client.remove_selectable_sim_info(sim_info)
            sim_info.remove_permanently(household=household)


@sims4.commands.Command('sims.make_all_selectable')
def make_all_selectable(_connection=None):
    if _connection is not None:
        tgt_client = services.client_manager().get(_connection)
        tgt_client.make_all_sims_selectable()


@sims4.commands.Command('sims.get_travel_menu_info', command_type=(sims4.commands.CommandType.Live))
def get_travel_menu_info(*args, _connection=None):
    client = services.client_manager().get(_connection)
    if client is None:
        log.info('Travel', 'No client found for get_travel_menu_info, bailing.')
        return False
    household = client.household
    travel_info = interaction_protocol.TravelMenuInfo()
    for sim in household.instanced_sims_gen():
        travel_info.sim_ids.append(sim.id)

    distributor = Distributor.instance()
    distributor.add_op_with_no_owner(GenericProtocolBufferOp(Operation.TRAVEL_MENU_INFO, travel_info))


@sims4.commands.Command('sims.set_focus')
def set_focus(record_id, targetID=0, x=0.0, y=0.0, z=0.0, layer=1, score=1.0, targetBoneName='', flags=0, blocking=0, opt_sim=None, _connection=None):
    if targetID == 0:
        if x == 0:
            if y == 0:
                if z == 0:
                    sims4.commands.output('SET_FOCUS: No focus to set.', _connection)
        else:
            sim = get_optional_target(opt_sim, _connection)
            target = 0
            if targetID != 0:
                manager = services.object_manager()
                if targetID in manager:
                    target = targetID
                else:
                    sims4.log.warn('SimInfo', 'SET_FOCUS: Ignoring invalid Object ID.')
        bone = 0
        if targetBoneName != '':
            if targetID == 0:
                sims4.log.warn('SimInfo', 'SET_FOCUS: Ignoring bone ID without valid Object ID.')
    else:
        bone = sims4.hash_util.hash32(targetBoneName)
    offset = sims4.math.Vector3(x, y, z)
    if record_id < 0:
        record_id = 0
    if layer < 0:
        layer = 0
    interactions.utils.sim_focus.FocusAdd(sim, record_id, layer, score, sim.id, target, bone, offset, blocking, None, None, flags)


@sims4.commands.Command('sims.delete_focus')
def delete_focus(record_id: int, opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    interactions.utils.sim_focus.FocusDelete(sim, sim.id, record_id, False)


@sims4.commands.Command('sims.clear_focus')
def clear_focus(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    interactions.utils.sim_focus.FocusClear(sim, sim.id, False)


@sims4.commands.Command('sims.modify_focus_score')
def modify_focus_score(record_id: int, score: float, opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    interactions.utils.sim_focus.FocusModifyScore(sim, sim.id, record_id, score, False)


@sims4.commands.Command('sims.disable_focus')
def disable_focus(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    interactions.utils.sim_focus.FocusDisable(sim, True, False)


@sims4.commands.Command('sims.enable_focus')
def enable_focus(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    interactions.utils.sim_focus.FocusDisable(sim, False, False)


@sims4.commands.Command('sims.force_focus_update')
def force_focus_update(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    interactions.utils.sim_focus.FocusForceUpdate(sim, sim.id, False)


@sims4.commands.Command('sims.print_focus')
def print_focus(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    interactions.utils.sim_focus.FocusPrint(sim, sim.id)


@sims4.commands.Command('sims.print_focus_server')
def print_focus_server(opt_sim: OptionalTargetParam=None, _connection=None):
    interactions.utils.sim_focus.FocusPrintAll(_connection)


@sims4.commands.Command('sims.test_focus')
def test_focus(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    pos1 = sim.position + sims4.math.Vector3(2.0, 2, 0)
    pos2 = sim.position + sims4.math.Vector3(-2.0, 2, 0)
    pos3 = sim.position + sims4.math.Vector3(0, 2, 2.0)
    pos4 = sim.position + sims4.math.Vector3(0, 2, -2.0)
    set_focus(record_id=1, targetID=0, x=(pos1.x), y=(pos1.y), z=(pos1.z), opt_sim=opt_sim, _connection=_connection)
    set_focus(record_id=2, targetID=0, x=(pos2.x), y=(pos2.y), z=(pos2.z), opt_sim=opt_sim, _connection=_connection)
    set_focus(record_id=3, targetID=0, x=(pos3.x), y=(pos3.y), z=(pos3.z), opt_sim=opt_sim, _connection=_connection)
    set_focus(record_id=4, targetID=0, x=(pos4.x), y=(pos4.y), z=(pos4.z), opt_sim=opt_sim, _connection=_connection)


@sims4.commands.Command('sims.set_focus_compatibility')
def set_focus_compatibility(level: int=0, opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        op = distributor.ops.SetFocusCompatibility(level)
        distributor.ops.record(sim, op)


@sims4.commands.Command('sims.show_buffs', command_type=(sims4.commands.CommandType.Automation))
def show_buffs(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('Invalid Sim id: {}'.format(opt_sim), _connection)
        return False
    buff_component = sim.Buffs
    if buff_component is None:
        sims4.commands.output('Sim has no Buffs component: {}'.format(opt_sim), _connection)
        return False
    sims4.commands.automation_output('BuffsInfo; Status:Begin', _connection)
    sims4.commands.output('Buffs: ', _connection)
    for buff_entry in buff_component:
        s = ' {}'.format(buff_entry.__class__.__name__)
        sims4.commands.output(s, _connection)
        sims4.commands.automation_output('BuffsInfo; Status:Data, Value:{}'.format(buff_entry.__class__.__name__), _connection)

    sims4.commands.automation_output('BuffsInfo; Status:End', _connection)


@sims4.commands.Command('sims.add_buff', command_type=(sims4.commands.CommandType.Automation))
def add_buff(buff_type: TunableInstanceParam(sims4.resources.Types.BUFF), opt_target: OptionalTargetParam=None, _connection=None):
    target = get_optional_target(opt_target, _connection)
    if target is None:
        return False
    if target.debug_add_buff_by_type(buff_type):
        sims4.commands.output('({}) has been added to {}.'.format(buff_type, target.full_name), _connection)
        return True
    sims4.commands.output('({}) has NOT been added to {}.'.format(buff_type, target.full_name), _connection)
    return False


@sims4.commands.Command('sims.remove_buff', 'removeBuff', command_type=(sims4.commands.CommandType.Cheat))
def remove_buff(buff_type: TunableInstanceParam(sims4.resources.Types.BUFF), opt_target: OptionalTargetParam=None, _connection=None):
    target = get_optional_target(opt_target, _connection)
    if target is None:
        return False
    elif target.has_buff(buff_type):
        target.remove_buff_by_type(buff_type)
        sims4.commands.output('({}) has been removed from {}.'.format(buff_type, target.full_name), _connection)
    else:
        sims4.commands.output('({}) does not exist on {}.'.format(buff_type, target.full_name), _connection)


@sims4.commands.Command('sims.remove_buff_from_all', command_type=(sims4.commands.CommandType.Live))
def remove_buff_from_all(buff_type: TunableInstanceParam(sims4.resources.Types.BUFF), _connection=None):
    output = sims4.commands.Output(_connection)
    for sim_info in services.sim_info_manager().values():
        sim = sim_info.get_sim_instance()
        if sim is not None and sim.has_buff(buff_type):
            sim.remove_buff_by_type(buff_type)
            output('{} has been removed from {}.'.format(buff_type, sim.full_name))


@sims4.commands.Command('sims.remove_all_buffs', command_type=(sims4.commands.CommandType.Automation))
def remove_all_buffs(opt_target: OptionalSimInfoParam=None, _connection=None):
    target = get_optional_target(opt_target, _connection=_connection, target_type=OptionalSimInfoParam)
    if target is None:
        return False
    for buff_type in services.get_instance_manager(sims4.resources.Types.BUFF).types.values():
        if target.has_buff(buff_type):
            if buff_type.commodity is not None:
                if not target.is_valid_statistic_to_remove(buff_type.commodity):
                    continue
                tracker = target.get_tracker(buff_type.commodity)
                commodity_inst = tracker.get_statistic(buff_type.commodity)
                if commodity_inst is not None:
                    if commodity_inst.core:
                        continue
            target.remove_buff_by_type(buff_type)
            sims4.commands.output('({0}) has been removed.'.format(buff_type.__name__), _connection)


@sims4.commands.Command('sims.reminisce_about_memory', command_type=(sims4.commands.CommandType.Live))
def reminisce_about_memory(memory_id: int=0, opt_sim: OptionalTargetParam=None, _connection=None):
    if opt_sim is None:
        sims4.commands.output('Invalid Sim id: {}'.format(opt_sim), _connection)
        return False
    opt_target = RequiredTargetParam(str(opt_sim.target_id))
    memory_uids = buffs.memory.MemoryUid
    if memory_id == memory_uids.Invalid:
        sims4.commands.output('Invalid Memory Uid: {}'.format(memory_id), _connection)
        return False
    reminisce_affordance_tuple = buffs.memory.Memory.MEMORIES.get(memory_id, None)
    if reminisce_affordance_tuple is not None:
        reminisce_affordance = reminisce_affordance_tuple.reminisce_affordance
    else:
        sims4.commands.output('Memory Uid not in Memories Tuning: {}'.format(memory_id), _connection)
        return False
        if reminisce_affordance is not None:
            return server_commands.interaction_commands.push_interaction(affordance=reminisce_affordance, opt_target=opt_target, opt_sim=opt_sim, _connection=_connection)


def push_travel_affordance(opt_sim=None, lot_id=0, world_id=0, lot_name='', friend_account='', _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('Invalid Sim id: {}'.format(opt_sim), _connection)
        return False
    client = services.client_manager().get(_connection)
    context = InteractionContext(sim, (InteractionContext.SOURCE_PIE_MENU), (Priority.High), client=client, pick=None)
    result = sim.push_super_affordance(super_affordance=TravelSuperInteraction, target=sim, context=context, to_zone_id=lot_id, world_id=world_id, lot_name=lot_name, friend_account=friend_account)
    if not result:
        output = sims4.commands.Output(_connection)
        output('Failed to push: {}'.format(result))
        return False
    return True


@sims4.commands.Command('sims.travel_to_specific_location', command_type=(sims4.commands.CommandType.Live))
def travel_to_specific_location(opt_sim=None, lot_id=0, world_id=0, lot_name='', _connection=None):
    return push_travel_affordance(opt_sim=opt_sim, lot_id=lot_id, world_id=world_id, lot_name=lot_name, _connection=_connection)


@sims4.commands.Command('sims.travel_to_friend', command_type=(sims4.commands.CommandType.Live))
def travel_to_friend_location(opt_sim: OptionalTargetParam=None, friend_account: str='', _connection=None):
    return push_travel_affordance(opt_sim=opt_sim, friend_account=friend_account, _connection=_connection)


@sims4.commands.Command('sims.visit_target_sim', command_type=(sims4.commands.CommandType.Live))
def visit_target_sim(opt_target: RequiredTargetParam=None, opt_sim: OptionalTargetParam=None, _connection=None):
    sim_mgr = services.sim_info_manager()
    target_info = sim_mgr.get(opt_target.target_id)
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('Invalid Sim id: {}'.format(opt_sim), _connection)
        return False
    if target_info.zone_id == 0:
        sims4.commands.output('Invalid destination zone id: {}'.format(target_info.zone_id), _connection)
        return False
    sim.sim_info.send_travel_switch_to_zone_op(zone_id=(target_info.zone_id))
    return True


@sims4.commands.Command('sims.travel_to_target_sim', command_type=(sims4.commands.CommandType.Live))
def travel_to_target_sim(opt_target: RequiredTargetParam=None, opt_sim: OptionalTargetParam=None, _connection=None):
    sim_mgr = services.sim_info_manager()
    target_info = sim_mgr.get(opt_target.target_id)
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('Invalid Sim id: {}'.format(opt_sim), _connection)
        return False
    if target_info.zone_id == 0:
        sims4.commands.output('Invalid destination zone id: {}'.format(target_info.zone_id), _connection)
        return False
    target_info.send_travel_switch_to_zone_op()
    return True


@sims4.commands.Command('sims.summon_sim_to_zone', command_type=(sims4.commands.CommandType.Live))
def summon_sim_to_zone(opt_target: RequiredTargetParam=None, opt_sim: OptionalTargetParam=None, _connection=None):
    sim_mgr = services.sim_info_manager()
    target_info = sim_mgr.get(opt_target.target_id)
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('Invalid Sim id: {}'.format(opt_sim), _connection)
        sims4.commands.automation_output('SimsSummonToZone; Status:Failed', _connection)
        return False
    if opt_target is not None:
        sims.sim_spawner.SimSpawner.load_sim(target_info.sim_id)
        sims4.commands.automation_output('SimsSummonToZone; Status:Success', _connection)
        return True


@sims4.commands.Command('sims.teleport', command_type=(sims4.commands.CommandType.Automation))
def teleport(x=0.0, y=0.0, z=0.0, level=0, opt_sim=None, rotation=0, _connection=None):
    if x == 0:
        if y == 0:
            if z == 0:
                sims4.commands.output('teleport: no destination set.', _connection)
                return False
    sim = get_optional_target(opt_sim, _connection)
    orientation = sims4.math.angle_to_yaw_quaternion(rotation)
    pos = sims4.math.Vector3(x, y, z)
    zone_id = services.current_zone_id()
    routing_surface = routing.SurfaceIdentifier(zone_id, level, routing.SurfaceType.SURFACETYPE_WORLD)
    location = sims4.math.Location(sims4.math.Transform(pos, orientation), routing_surface)
    target = objects.terrain.TerrainPoint(location)
    pick = PickInfo(pick_type=(PickType.PICK_TERRAIN), target=target, location=pos, routing_surface=routing_surface)
    context = InteractionContext(sim, (InteractionContext.SOURCE_SCRIPT_WITH_USER_INTENT),
      (interactions.priority.Priority.High),
      pick=pick)
    sim.push_super_affordance(CommandTuning.TERRAIN_TELEPORT_AFFORDANCE, target, context)


@sims4.commands.Command('sims.teleport_instantly', command_type=(sims4.commands.CommandType.Automation))
def teleport_instantly(x=0.0, y=0.0, z=0.0, level=0, opt_sim=None, rotation=0, _connection=None):
    if x == 0:
        if y == 0:
            if z == 0:
                sims4.commands.output('teleport: no destination set.', _connection)
                return False
    sim = get_optional_target(opt_sim, _connection)
    orientation = sims4.math.angle_to_yaw_quaternion(rotation)
    pos = sims4.math.Vector3(x, y, z)
    zone_id = services.current_zone_id()
    routing_surface = routing.SurfaceIdentifier(zone_id, level, routing.SurfaceType.SURFACETYPE_WORLD)
    location = sims4.math.Location(sims4.math.Transform(pos, orientation), routing_surface)
    sim.location = location


@sims4.commands.Command('sims.route_instantly')
def route_instantly(value: bool=False, _connection=None):
    Zone.force_route_instantly = value


@sims4.commands.Command('sims.resatisfy_constraint')
def resatisfy_constraint(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        affordance = SatisfyConstraintSuperInteraction
        aop = AffordanceObjectPair(affordance, None, affordance, None)
        context = InteractionContext(sim, InteractionContext.SOURCE_SCRIPT_WITH_USER_INTENT, priority.Priority.High)
        aop.test_and_execute(context)


@sims4.commands.Command('sims.whims_award_prize', command_type=(sims4.commands.CommandType.Live))
def whims_award_prize(reward_id: int=0, opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is not None:
        if sim_info.satisfaction_tracker is None:
            output = sims4.commands.CheatOutput(_connection)
            output('The Sim specified ({}) does not have a satisfaction tracker. Likely because they are in a LOD level without a satisfaction tracker.'.format(sim_info))
            return False
        sim_info.satisfaction_tracker.purchase_satisfaction_reward(reward_id)
        sim_info.satisfaction_tracker.send_satisfaction_reward_list()
        return True
    return False


@sims4.commands.Command('sims.request_satisfaction_reward_list', command_type=(sims4.commands.CommandType.Live))
def request_satisfaction_reward_list(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is not None:
        if sim_info.satisfaction_tracker is None:
            output = sims4.commands.CheatOutput(_connection)
            output('The Sim specified ({}) does not have a satisfaction tracker. Likely because they are in a LOD level without a satisfaction tracker.'.format(sim_info))
            return False
        sim_info.satisfaction_tracker.send_satisfaction_reward_list()
        return True
    return False


@sims4.commands.Command('sims.give_satisfaction_points', command_type=(sims4.commands.CommandType.Cheat))
def give_satisfaction_points(satisfaction_points: int=0, opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is not None:
        sim_info.apply_satisfaction_points_delta(satisfaction_points, SetWhimBucks.COMMAND)
        return True
    return False


@sims4.commands.Command('sims.reset', command_type=(sims4.commands.CommandType.Automation))
def reset(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        sim.reset(ResetReason.RESET_EXPECTED, None, 'Command')
        return True
    return False


@sims4.commands.Command('resetsim', command_type=(sims4.commands.CommandType.Live))
def reset_sim(first_name='', last_name='', _connection=None):
    info = services.sim_info_manager().get_sim_info_by_name(first_name, last_name)
    if info is not None:
        sim = info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if sim is not None:
            sim.reset(ResetReason.RESET_EXPECTED, None, 'Command')
            return True
    output = sims4.commands.CheatOutput(_connection)
    output('Sim not found')
    return False


@sims4.commands.Command('sims.get_sim_id_by_name', command_type=(sims4.commands.CommandType.Live))
def get_sim_id_by_name(first_name='', last_name='', _connection=None):
    info = services.sim_info_manager().get_sim_info_by_name(first_name, last_name)
    if info is not None:
        output = sims4.commands.CheatOutput(_connection)
        output('{} has sim id: {}'.format(info, info.id))
        return True
    output = sims4.commands.CheatOutput(_connection)
    output('Sim not found')
    return False


@sims4.commands.Command('sims.reset_multiple')
def reset_sims(*obj_ids: int, _connection=None):
    for obj_id in obj_ids:
        sim = services.object_manager().get(obj_id)
        if sim is not None:
            sim.reset(ResetReason.RESET_EXPECTED, None, 'Command')

    return True


@sims4.commands.Command('sims.reset_all')
def reset_all_sims(_connection=None):
    sims = services.sim_info_manager().instanced_sims_gen(allow_hidden_flags=ALL_HIDDEN_REASONS)
    services.get_reset_and_delete_service().trigger_batch_reset(sims)
    return True


@sims4.commands.Command('sims.interrupt')
def interrupt(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        sim.reset(ResetReason.RESET_EXPECTED, None, 'Command')
        return True
    return False


def _build_terrain_interaction_target_and_context(sim, pos, routing_surface, pick_type, target_cls):
    location = sims4.math.Location(sims4.math.Transform(pos), routing_surface)
    target = target_cls(location)
    pick = PickInfo(pick_type=pick_type, target=target, location=pos, routing_surface=routing_surface)
    return (target,
     InteractionContext(sim, (InteractionContext.SOURCE_SCRIPT_WITH_USER_INTENT),
       (interactions.priority.Priority.High),
       pick=pick,
       group_id=1))


@sims4.commands.Command('sims.swimhere')
def swimhere(x=0.0, y=0.0, z=0.0, level=0, start_x=0.0, start_y=0.0, start_z=0.0, start_level=0, opt_sim=None, _connection=None):
    if x == 0:
        if y == 0:
            if z == 0:
                sims4.commands.output('swimhere: no destination set.', _connection)
                return False
    sim = get_optional_target(opt_sim, _connection)
    if start_x != 0:
        if start_z != 0:
            teleport(start_x, start_y, start_z, start_level, opt_sim, _connection=_connection)
    pos = sims4.math.Vector3(x, y, z)
    routing_surface = routing.SurfaceIdentifier(services.current_zone_id(), level, routing.SurfaceType.SURFACETYPE_POOL)
    target, context = _build_terrain_interaction_target_and_context(sim, pos, routing_surface, PickType.PICK_POOL_SURFACE, objects.terrain.OceanPoint)
    sim.push_super_affordance(CommandTuning.TERRAIN_SWIMHERE_AFFORDANCE, target, context)


@sims4.commands.Command('sims.gohere')
def gohere(x=0.0, y=0.0, z=0.0, level=0, start_x=0.0, start_y=0.0, start_z=0.0, start_level=0, opt_sim=None, _connection=None):
    if x == 0:
        if y == 0:
            if z == 0:
                sims4.commands.output('gohere: no destination set.', _connection)
                return False
    sim = get_optional_target(opt_sim, _connection)
    if start_x != 0:
        if start_z != 0:
            teleport(start_x, start_y, start_z, start_level, opt_sim, _connection=_connection)
    pos = sims4.math.Vector3(x, y, z)
    routing_surface = routing.SurfaceIdentifier(services.current_zone_id(), level, routing.SurfaceType.SURFACETYPE_WORLD)
    target, context = _build_terrain_interaction_target_and_context(sim, pos, routing_surface, PickType.PICK_TERRAIN, objects.terrain.TerrainPoint)
    sim.push_super_affordance(CommandTuning.TERRAIN_GOHERE_AFFORDANCE, target, context)


@sims4.commands.Command('sims.allgohere')
def all_gohere(x=0.0, y=0.0, z=0.0, level=0, start_x=0.0, start_y=0.0, start_z=0.0, start_level=0, opt_sim=None, _connection=None):
    for sim_info in services.sim_info_manager().objects:
        sim = sim_info.get_sim_instance()
        if sim is not None:
            gohere(x=x, y=y, z=z, level=level, start_x=start_x, start_y=start_y,
              start_z=start_z,
              start_level=start_level,
              opt_sim=(OptionalTargetParam(str(sim.id))),
              _connection=_connection)


@sims4.commands.Command('sims.test_avoidance')
def test_avoidance(x=0.0, y=0.0, z=0.0, radius=5.0, level=0, opt_sim=None, _connection=None):
    num_sims = 0
    for sim_info in services.sim_info_manager().objects:
        if sim_info.is_instanced():
            num_sims += 1

    i = 0
    for sim_info in services.sim_info_manager().objects:
        if sim_info.is_instanced():
            sim = sim_info.get_sim_instance()
            x_end = x - math.cos(i * 2.0 * math.pi / num_sims) * radius
            y_end = y
            z_end = z - math.sin(i * 2.0 * math.pi / num_sims) * radius
            gohere(x_end, y_end, z_end, level, 0.0, 0.0, 0.0, 0, (OptionalTargetParam(str(sim.id))), _connection=_connection)
            i += 1


@sims4.commands.Command('sims.path_test')
def path_test(_connection=None):
    client = services.client_manager().get(_connection)
    sim = client.active_sim
    xform = sim.transform
    translate = xform.translation
    orientation = xform.orientation
    routing_surface = sim.routing_surface
    path = routing.path_wrapper()
    path.origin = routing.Location(translate, orientation, routing_surface)
    path.context.agent_id = sim.sim_id
    goal_pos = sims4.math.Vector3(0.0, 0.0, 0.0)
    goal_orientation = sims4.math.Quaternion(0.0, 0.0, 0.0, 1.0)
    path.add_goal(routing.Location(goal_pos, goal_orientation, routing_surface), 1.0, 0)
    goal_pos = sims4.math.Vector3(50000.0, 0.0, 0.0)
    path.add_goal(routing.Location(goal_pos, goal_orientation, routing_surface), 1.0, 1)
    goal_pos = sims4.math.Vector3(200.0, 100.0, 100.0)
    path.add_goal(routing.Location(goal_pos, goal_orientation, routing_surface), 1.0, 2)
    path.make_path()
    time.sleep(15)
    goal_results = path.goal_results()
    sims4.commands.output('Results:', _connection)
    for result in goal_results:
        sims4.commands.output('Found a goal: {0} :: {1} :: {2}'.format(result[0], result[1], result[2]), _connection)


@sims4.commands.Command('sims.skewer_icon_activated', command_type=(sims4.commands.CommandType.Live))
def skewer_icon_activated(target_param: RequiredTargetParam=None, priority: Priority=Priority.High, _connection=None):
    client = services.client_manager().get(_connection)
    sim_info_manager = services.sim_info_manager()
    sim_info = sim_info_manager.get(target_param.target_id)
    if sim_info is None:
        sims4.commands.output('Invalid Sim Info {}', target_param)
        return False
        sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS_EXCEPT_UNINITIALIZED)
        affordance = None
        target = None
        if sim_info.species == Species.HUMAN:
            if sim is not None:
                affordance = ui_tuning.UiTuning.GO_HOME_INTERACTION
                target = sim
    elif sim_info.household.missing_pet_tracker.is_pet_missing(sim_info):
        sim_info.household.missing_pet_tracker.intercept_skewer_command(sim_info)
        return True
    if sim is None:
        affordance = ui_tuning.UiTuning.BRING_HERE_INTERACTION
        sim = client.active_sim
        target = None
    else:
        affordance = ui_tuning.UiTuning.COME_NEAR_ACTIVE_SIM
        target = client.active_sim
        if target is None:
            return False
        else:
            if affordance is None:
                return True
            if sim is not None:
                sim.queue.can_queue_visible_interaction() or sims4.commands.output('Interaction queue is full, cannot add anymore interactions.', _connection)
                return False
        context = client.create_interaction_context(sim)
        for aop in affordance.potential_interactions(target, context, sim_info=sim_info):
            result = aop.test_and_execute(context)
            if not result:
                continue

        return True


@sims4.commands.Command('sims.set_thumbnail')
def set_thumbnail(thumbnail, sim_id: int=None, _connection=None):
    if sim_id is not None:
        sim_info = services.sim_info_manager().get(sim_id)
        sim = sim_info.get_sim_instance() if sim_info is not None else None
    else:
        client = services.client_manager().get(_connection)
        sim = client.active_sim
    if sim is not None:
        key = sims4.resources.Key.hash64(thumbnail, sims4.resources.Types.PNG)
        sims4.commands.output('Thumbnail changed from {} to {}'.format(sim.thumbnail, key), _connection)
        sim.thumbnail = key
        return True
    sims4.commands.output('Unable to find Sim.', _connection)
    return False


@sims4.commands.Command('sims.clear_all_stats')
def clear_all_stats(opt_sim: OptionalTargetParam=None, _connection=None):
    from server_commands import statistic_commands, relationship_commands
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('Invalid Sim id: {}'.format(opt_sim), _connection)
        return False
    if sim.statistic_tracker is None:
        return
    statistic_commands.clear_skill(opt_sim, _connection=_connection)
    relationship_commands.clear_relationships(opt_sim, _connection=_connection)
    sim.commodity_tracker.debug_set_all_to_default()
    sim.statistic_tracker.debug_set_all_to_default()
    return True


@sims4.commands.Command('sims.fill_all_commodities', command_type=(sims4.commands.CommandType.Cheat))
def set_commodities_to_best_values(visible_only: bool=True, _connection=None):
    for sim_info in services.sim_info_manager().objects:
        sim_info.commodity_tracker.set_all_commodities_to_best_value(visible_only=visible_only)


@sims4.commands.Command('rosebud', 'kaching', command_type=(sims4.commands.CommandType.Live), console_type=(sims4.commands.CommandType.Cheat))
def rosebud(_connection=None):
    tgt_client = services.client_manager().get(_connection)
    modify_fund_helper(1000, Consts_pb2.TELEMETRY_MONEY_CHEAT, tgt_client.active_sim)


@sims4.commands.Command('motherlode', command_type=(sims4.commands.CommandType.Live), console_type=(sims4.commands.CommandType.Cheat))
def motherlode(_connection=None):
    tgt_client = services.client_manager().get(_connection)
    modify_fund_helper(50000, Consts_pb2.TELEMETRY_MONEY_CHEAT, tgt_client.active_sim)


@sims4.commands.Command('money', command_type=(sims4.commands.CommandType.Cheat))
def set_money(amount: int, sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(sim, _connection)
    if sim is not None:
        current_amount = sim.family_funds.money
        modify_fund_helper(amount - current_amount, Consts_pb2.TELEMETRY_MONEY_CHEAT, sim)
        return True
    return False


@sims4.commands.Command('sims.modify_funds', command_type=(sims4.commands.CommandType.Automation))
def modify_funds(amount: int, reason=None, opt_sim: OptionalTargetParam=None, _connection=None):
    if reason is None:
        reason = Consts_pb2.TELEMETRY_MONEY_CHEAT
    sim = get_optional_target(opt_sim, _connection)
    modify_fund_helper(amount, reason, sim)


def modify_fund_helper(amount, reason, sim):
    if amount > 0:
        sim.family_funds.add(amount, reason, sim)
    else:
        sim.family_funds.try_remove(-amount, reason, sim)


@sims4.commands.Command('sims.hard_reset', command_type=(sims4.commands.CommandType.Automation))
def hard_reset(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        sim.reset(ResetReason.RESET_EXPECTED, None, 'Command')
        return True
    return False


@sims4.commands.Command('sims.test_ignore_footprint')
def test_ignore_footprint(footprint_cost: int=100000, opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        poly = build_rectangle_from_two_points_and_radius(sims4.math.Vector3.Z_AXIS() + sim.location.transform.translation, sim.location.transform.translation, 1.0)
        sim.test_footprint = PolygonFootprint(poly, routing_surface=(sim.routing_surface), cost=footprint_cost, footprint_type=(FootprintType.FOOTPRINT_TYPE_OBJECT), enabled=True)
        sim.routing_context.ignore_footprint_contour(sim.test_footprint.footprint_id)
        return True
    return False


@sims4.commands.Command('sims.test_polygonal_connectivity_handle')
def test_polygonal_connectivity_handle(x=0.0, y=0.0, z=0.0, opt_sim=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        pt = sims4.math.Vector3(x, y, z)
        poly = build_rectangle_from_two_points_and_radius(sims4.math.Vector3.Z_AXIS() * 2 + sims4.math.Vector3.X_AXIS() * 2 + pt, pt, 2.0)
        zone_id = services.current_zone_id()
        routing_surface = routing.SurfaceIdentifier(zone_id, 0, routing.SurfaceType.SURFACETYPE_WORLD)
        handle = routing.connectivity.Handle(poly, routing_surface)
        if routing.test_connectivity_permissions_for_handle(handle, sim.routing_context):
            sims4.commands.output('Connectivity Group: {0} - ALLOWED'.format(handle.connectivity_groups), _connection)
        else:
            sims4.commands.output('Connectivity Group: {0} - NOT ALLOWED'.format(handle.connectivity_groups), _connection)
        return True
    return False


@sims4.commands.Command('sims.test_connectivity_permissions')
def test_connectivity_permissions(x=0.0, y=0.0, z=0.0, opt_sim=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        pt = sims4.math.Vector3(x, y, z)
        zone_id = services.current_zone_id()
        routing_surface = routing.SurfaceIdentifier(zone_id, 0, routing.SurfaceType.SURFACETYPE_WORLD)
        loc = routing.Location(pt, sims4.math.Quaternion.ZERO(), routing_surface)
        handle = routing.connectivity.Handle(loc)
        if routing.test_connectivity_permissions_for_handle(handle, sim.routing_context):
            sims4.commands.output('Connectivity Group: {0}/{1} - ALLOWED'.format(handle.connectivity_groups, handle.connectivity_groups_lite), _connection)
        else:
            sims4.commands.output('Connectivity Group: {0}/{1} - NOT ALLOWED'.format(handle.connectivity_groups, handle.connectivity_groups_lite), _connection)
        return True
    return False


@sims4.commands.Command('sims.test_connectivity_pt_pt')
def test_connectivity_pt_pt(a_x=0.0, a_y=0.0, a_z=0.0, b_x=0.0, b_y=0.0, b_z=0.0, opt_sim=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        a = sims4.math.Vector3(a_x, a_y, a_z)
        b = sims4.math.Vector3(b_x, b_y, b_z)
        zone_id = services.current_zone_id()
        routing_surface = routing.SurfaceIdentifier(zone_id, 0, routing.SurfaceType.SURFACETYPE_WORLD)
        locA = routing.Location(a, sims4.math.Quaternion.ZERO(), routing_surface)
        locB = routing.Location(b, sims4.math.Quaternion.ZERO(), routing_surface)
        if routing.test_connectivity_pt_pt(locA, locB, sim.routing_context):
            sims4.commands.output('Points are CONNECTED', _connection)
        else:
            sims4.commands.output('Points are DISCONNECTED', _connection)
        return True
    return False


@sims4.commands.Command('sims.test_raytest')
def test_raytest(x1=0.0, y1=0.0, z1=0.0, level1=0, x2=0.0, y2=0.0, z2=0.0, level2=0, ignore_id=None, opt_sim=None, _connection=None):
    pos1 = sims4.math.Vector3(x1, y1, z1)
    zone_id = services.current_zone_id()
    routing_surface1 = routing.SurfaceIdentifier(zone_id, level1, routing.SurfaceType.SURFACETYPE_WORLD)
    location1 = routing.Location(pos1, sims4.math.Quaternion.ZERO(), routing_surface1)
    pos2 = sims4.math.Vector3(x2, y2, z2)
    routing_surface2 = routing.SurfaceIdentifier(zone_id, level2, routing.SurfaceType.SURFACETYPE_WORLD)
    location2 = routing.Location(pos2, sims4.math.Quaternion.ZERO(), routing_surface2)
    sim = get_optional_target(opt_sim, _connection)
    obj = objects.system.find_object(ignore_id)
    if obj is not None:
        if obj.routing_context is not None:
            if obj.routing_context.object_footprint_id is not None:
                sim.routing_context.ignore_footprint_contour(obj.routing_context.object_footprint_id)
    sims4.commands.output('test_raytest: returned {0}.'.format(routing.ray_test(location1, location2, sim.routing_context)), _connection)
    if obj is not None:
        if obj.routing_context is not None:
            if obj.routing_context.object_footprint_id is not None:
                sim.routing_context.remove_footprint_contour_override(obj.routing_context.object_footprint_id)


@sims4.commands.Command('sims.planner_build_id')
def planner_id(opt_sim: OptionalTargetParam=None, _connection=None):
    sims4.commands.output('planner_id: returned {0}.'.format(routing.planner_build_id()), _connection)


def _remove_alarm_helper(*args):
    global _reset_alarm_handles
    current_zone = services.current_zone()
    if current_zone in _reset_alarm_handles:
        alarms.cancel_alarm(_reset_alarm_handles[current_zone])
        del _reset_alarm_handles[current_zone]
        current_zone.unregister_callback(zone_types.ZoneState.SHUTDOWN_STARTED, _remove_alarm_helper)


@sims4.commands.Command('sims.reset_periodically')
def reset_periodically(enable: bool=True, interval: int=10, reset_type='reset', _connection=None):
    _remove_alarm_helper()
    if not enable:
        return

    def reset_helper(self):
        current_zone = services.current_zone()
        reset_reason = ResetReason.RESET_ON_ERROR
        if reset_type.lower() == 'interrupt':
            reset_reason = ResetReason.RESET_EXPECTED
        else:
            if reset_type.lower() == 'random':
                if random.randint(0, 1) == 1:
                    reset_reason = ResetReason.RESET_EXPECTED
        household_manager = services.household_manager()
        for household in household_manager.get_all():
            for sim in household.instanced_sims_gen():
                sim.reset(reset_reason)

        alarms.cancel_alarm(_reset_alarm_handles[current_zone])
        reset_time_span = clock.interval_in_sim_minutes(random.randint(1, interval))
        _reset_alarm_handles[current_zone] = alarms.add_alarm(reset_periodically, reset_time_span, reset_helper)

    reset_time_span = clock.interval_in_sim_minutes(random.randint(1, interval))
    current_zone = services.current_zone()
    _reset_alarm_handles[current_zone] = alarms.add_alarm(reset_periodically, reset_time_span, reset_helper)
    current_zone.register_callback(zone_types.ZoneState.SHUTDOWN_STARTED, _remove_alarm_helper)


@sims4.commands.Command('sims.reset_random_sim_periodically')
def reset_random_sim_periodically(enable: bool=True, min_interval: int=2, max_interval: int=10, reset_type='reset', _connection=None):
    _remove_alarm_helper()
    if not enable:
        return

    def reset_helper(self):
        current_zone = services.current_zone()
        reset_reason = ResetReason.RESET_ON_ERROR
        if reset_type.lower() == 'expected':
            reset_reason = ResetReason.RESET_EXPECTED
        else:
            if reset_type.lower() == 'random':
                if random.randint(0, 1) == 1:
                    reset_reason = ResetReason.RESET_EXPECTED
        sim_info_manager = services.sim_info_manager()
        all_sims = list(sim_info_manager.instanced_sims_gen())
        sim = all_sims[random.randint(0, len(all_sims) - 1)]
        sim.reset(reset_reason)
        alarms.cancel_alarm(_reset_alarm_handles[current_zone])
        reset_time_span = clock.interval_in_sim_minutes(random.randint(min_interval, max_interval))
        _reset_alarm_handles[current_zone] = alarms.add_alarm(reset_periodically, reset_time_span, reset_helper)

    reset_time_span = clock.interval_in_sim_minutes(random.randint(min_interval, max_interval))
    current_zone = services.current_zone()
    _reset_alarm_handles[current_zone] = alarms.add_alarm(reset_periodically, reset_time_span, reset_helper)
    current_zone.register_callback(zone_types.ZoneState.SHUTDOWN_STARTED, _remove_alarm_helper)


@sims4.commands.Command('sims.changeoutfit', command_type=(sims4.commands.CommandType.DebugOnly))
def change_outfit(opt_sim: OptionalTargetParam=None, outfit_category_string='EVERYDAY', outfit_index: int=0, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        category = getattr(OutfitCategory, outfit_category_string.upper(), None)
        if category is not None:
            sim.sim_info.set_current_outfit((category, outfit_index))
        else:
            available_categories = ''
            for category in OutfitCategory:
                available_categories = available_categories + category.name + ', '

            sims4.commands.output('Unrecognized outfit category name. available categories = {}'.format(available_categories), _connection)
        return True
    return False


@sims4.commands.Command('sims.get_buffs_ids_for_outfit')
def get_buffs_ids_for_outfit--- This code section failed: ---

 L.1578         0  LOAD_GLOBAL              get_optional_target
                2  LOAD_FAST                'opt_sim'
                4  LOAD_FAST                '_connection'
                6  CALL_FUNCTION_2       2  '2 positional arguments'
                8  STORE_FAST               'sim'

 L.1579        10  LOAD_FAST                'sim'
               12  LOAD_CONST               None
               14  COMPARE_OP               is
               16  POP_JUMP_IF_FALSE    22  'to 22'

 L.1580        18  LOAD_CONST               False
               20  RETURN_VALUE     
             22_0  COME_FROM            16  '16'

 L.1582        22  LOAD_GLOBAL              getattr
               24  LOAD_GLOBAL              OutfitCategory
               26  LOAD_FAST                'outfit_category_string'
               28  LOAD_METHOD              upper
               30  CALL_METHOD_0         0  '0 positional arguments'
               32  LOAD_CONST               None
               34  CALL_FUNCTION_3       3  '3 positional arguments'
               36  STORE_FAST               'category'

 L.1583        38  LOAD_FAST                'category'
               40  LOAD_CONST               None
               42  COMPARE_OP               is-not
               44  POP_JUMP_IF_FALSE   194  'to 194'

 L.1584        46  LOAD_FAST                'sim'
               48  LOAD_ATTR                sim_info
               50  LOAD_METHOD              set_current_outfit
               52  LOAD_FAST                'category'
               54  LOAD_FAST                'outfit_index'
               56  BUILD_TUPLE_2         2 
               58  CALL_METHOD_1         1  '1 positional argument'
               60  POP_TOP          

 L.1585        62  LOAD_FAST                'sim'
               64  LOAD_ATTR                sim_info
               66  LOAD_METHOD              get_part_ids_for_outfit
               68  LOAD_FAST                'category'
               70  LOAD_FAST                'outfit_index'
               72  CALL_METHOD_2         2  '2 positional arguments'
               74  STORE_FAST               'part_ids'

 L.1586        76  LOAD_GLOBAL              sims4
               78  LOAD_ATTR                commands
               80  LOAD_METHOD              output
               82  LOAD_STR                 'parts: {}'
               84  LOAD_METHOD              format
               86  LOAD_FAST                'part_ids'
               88  CALL_METHOD_1         1  '1 positional argument'
               90  LOAD_FAST                '_connection'
               92  CALL_METHOD_2         2  '2 positional arguments'
               94  POP_TOP          

 L.1587        96  LOAD_GLOBAL              cas
               98  LOAD_ATTR                cas
              100  LOAD_METHOD              get_buff_from_part_ids
              102  LOAD_FAST                'part_ids'
              104  CALL_METHOD_1         1  '1 positional argument'
              106  STORE_FAST               'buff_guids'

 L.1588       108  LOAD_FAST                'buff_guids'
              110  POP_JUMP_IF_FALSE   170  'to 170'

 L.1589       112  SETUP_LOOP          192  'to 192'
              114  LOAD_FAST                'buff_guids'
              116  GET_ITER         
              118  FOR_ITER            166  'to 166'
              120  STORE_FAST               'buff_guid'

 L.1590       122  LOAD_GLOBAL              services
              124  LOAD_METHOD              get_instance_manager
              126  LOAD_GLOBAL              sims4
              128  LOAD_ATTR                resources
              130  LOAD_ATTR                Types
              132  LOAD_ATTR                BUFF
              134  CALL_METHOD_1         1  '1 positional argument'
              136  LOAD_METHOD              get
              138  LOAD_FAST                'buff_guid'
              140  CALL_METHOD_1         1  '1 positional argument'
              142  STORE_FAST               'buff_type'

 L.1591       144  LOAD_GLOBAL              sims4
              146  LOAD_ATTR                commands
              148  LOAD_METHOD              output
              150  LOAD_STR                 'buff: {}'
              152  LOAD_METHOD              format
              154  LOAD_FAST                'buff_type'
              156  CALL_METHOD_1         1  '1 positional argument'
              158  LOAD_FAST                '_connection'
              160  CALL_METHOD_2         2  '2 positional arguments'
              162  POP_TOP          
              164  JUMP_BACK           118  'to 118'
              166  POP_BLOCK        
              168  JUMP_ABSOLUTE       246  'to 246'
            170_0  COME_FROM           110  '110'

 L.1593       170  LOAD_GLOBAL              sims4
              172  LOAD_ATTR                commands
              174  LOAD_METHOD              output
              176  LOAD_STR                 'category: {}, index: {}, has no buffs associated'
              178  LOAD_METHOD              format
              180  LOAD_FAST                'outfit_category_string'
              182  LOAD_FAST                'outfit_index'
              184  CALL_METHOD_2         2  '2 positional arguments'
              186  LOAD_FAST                '_connection'
              188  CALL_METHOD_2         2  '2 positional arguments'
              190  POP_TOP          
            192_0  COME_FROM_LOOP      112  '112'
              192  JUMP_FORWARD        246  'to 246'
            194_0  COME_FROM            44  '44'

 L.1595       194  LOAD_STR                 ''
              196  STORE_FAST               'available_categories'

 L.1596       198  SETUP_LOOP          226  'to 226'
              200  LOAD_GLOBAL              OutfitCategory
              202  GET_ITER         
              204  FOR_ITER            224  'to 224'
              206  STORE_FAST               'category'

 L.1597       208  LOAD_FAST                'available_categories'
              210  LOAD_FAST                'category'
              212  LOAD_ATTR                name
              214  BINARY_ADD       
              216  LOAD_STR                 ', '
              218  BINARY_ADD       
              220  STORE_FAST               'available_categories'
              222  JUMP_BACK           204  'to 204'
              224  POP_BLOCK        
            226_0  COME_FROM_LOOP      198  '198'

 L.1598       226  LOAD_GLOBAL              sims4
              228  LOAD_ATTR                commands
              230  LOAD_METHOD              output
              232  LOAD_STR                 'Unrecognized outfit category name. available categories = {}'
              234  LOAD_METHOD              format
              236  LOAD_FAST                'available_categories'
              238  CALL_METHOD_1         1  '1 positional argument'
              240  LOAD_FAST                '_connection'
              242  CALL_METHOD_2         2  '2 positional arguments'
              244  POP_TOP          
            246_0  COME_FROM           192  '192'

 L.1599       246  LOAD_CONST               True
              248  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM_LOOP' instruction at offset 192_0


@sims4.commands.Command('sims.set_familial_relationship', command_type=(sims4.commands.CommandType.DebugOnly))
def set_familial_relationship(sim_a_id: OptionalTargetParam=None, sim_b_id: int=None, relationship: str=None, _connection=None):
    sim_a = get_optional_target(sim_a_id, _connection)
    if sim_a is None:
        sims4.commands.output('Must specify a sim, or have a sim selected, to set a familial relationship with.', _connection)
        return False
    try:
        relationship = FamilyRelationshipIndex(relationship)
    except Exception:
        available_relations = ''
        for relation in FamilyRelationshipIndex:
            available_relations = available_relations + relation.name + ', '

        sims4.commands.output('Unrecognized genealogy relationship name. available relations = {}'.format(available_relations), _connection)
        return False
    else:
        sim_b_info = services.sim_info_manager().get(sim_b_id)
        if sim_b_info is not None:
            sim_a.sim_info.set_and_propagate_family_relation(relationship, sim_b_info)
        else:
            sim_a.sim_info._genealogy_tracker.set_family_relation(relationship, sim_b_id)
        return True


@sims4.commands.Command('sims.send_gameplay_options_to_client', command_type=(sims4.commands.CommandType.Live))
def send_gameplay_options_to_client(get_default: bool=False, _connection=None):
    client = services.client_manager().get(_connection)
    client.account.send_options_to_client(client, get_default)


@sims4.commands.Command('sims.toggle_random_spawning', command_type=(sims4.commands.CommandType.DebugOnly))
def toggle_random_spawning(_connection=None):
    sims.sim_spawner.disable_spawning_non_selectable_sims = not sims.sim_spawner.disable_spawning_non_selectable_sims


@sims4.commands.Command('sims.focus_camera_on_sim')
def focus_camera_on_sim(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        return
    client = services.client_manager().get(_connection)
    camera.focus_on_sim(sim, follow=True, client=client)


@sims4.commands.Command('sims.inventory_view_update', command_type=(sims4.commands.CommandType.Live))
def inventory_view_update(sim_id: int=0, opt_sim: OptionalTargetParam=None, _connection=None):
    if sim_id > 0:
        sim_info = services.sim_info_manager().get(sim_id)
        sim = sim_info.get_sim_instance()
        if sim is not None:
            sim.inventory_view_update()


@sims4.commands.Command('sims.is_on_current_lot')
def is_on_current_lot(tolerance: float=0, opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('No valid sim.', _connection)
        return
    else:
        active_lot = services.active_lot()
        if active_lot.is_position_on_lot(sim.position, tolerance):
            sims4.commands.output('TRUE', _connection)
        else:
            sims4.commands.output('FALSE', _connection)


@sims4.commands.Command('sims.debug_apply_away_action')
def debug_apply_away_action(away_action: TunableInstanceParam((sims4.resources.Types.AWAY_ACTION), exact_match=True), opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('No valid sim.', _connection)
        return
    sim.sim_info.debug_apply_away_action(away_action)


@sims4.commands.Command('sims.debug_apply_default_away_action')
def debug_apply_default_away_action(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('No valid sim.', _connection)
        return
    sim.sim_info.debug_apply_default_away_action()


@sims4.commands.Command('sims.set_initial_adventure_moment_key_override')
def set_initial_adventure_moment_key(initial_adventure_moment_key_name: str, opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        try:
            initial_adventure_moment_key = AdventureMomentKey(initial_adventure_moment_key_name)
            set_initial_adventure_moment_key_override(sim, initial_adventure_moment_key)
        except ValueError:
            sims4.commands.output('{} is not a valid AdventureMomentKey entry'.format(initial_adventure_moment_key_name), _connection)


@sims4.commands.Command('baby.set_enabled_state')
def set_baby_empty_state(is_enabled: bool=True, _connection=None):
    household = services.active_household()
    if household is None:
        return False
    object_manager = services.object_manager()
    for baby_info in household.baby_info_gen():
        bassinet = object_manager.get(baby_info.sim_id)
        if bassinet is not None:
            if is_enabled:
                bassinet.enable_baby_state()
            else:
                bassinet.empty_baby_state()

    return True


@sims4.commands.Command('sims.set_handedness')
def set_handedness(handedness: str, opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        handedness = handedness.lower()
        if handedness.startswith('r'):
            sim.set_preferred_hand(Hand.RIGHT)
            sims4.commands.output('{} is now Right Handed.'.format(sim), _connection)
        else:
            if handedness.startswith('l'):
                sim.set_preferred_hand(Hand.LEFT)
                sims4.commands.output('{} is now Left Handed.'.format(sim), _connection)
            else:
                sims4.commands.output("Invalid handedness '{}' specified. Use 'right' or 'left'".format(handedness), _connection)


@sims4.commands.Command('sims.set_grubby')
def set_grubby(opt_target: OptionalTargetParam=None, set_grubby: bool=None, _connection=None):
    sim = get_optional_target(opt_target, _connection)
    if sim is None:
        return False
    else:
        sim_info = sim.sim_info
        if set_grubby is None:
            sim_info.grubby = not sim_info.grubby
        else:
            sim_info.grubby = set_grubby


@sims4.commands.Command('sims.set_dyed')
def set_dyed(opt_sim: OptionalTargetParam=None, set_dyed: bool=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        return False
    else:
        sim_info = sim.sim_info
        if set_dyed is None:
            sim_info.dyed = not sim_info.dyed
        else:
            sim_info.dyed = set_dyed


@sims4.commands.Command('sims.set_messy_face')
def set_messy_face(opt_target: OptionalTargetParam=None, set_messy_face: bool=None, _connection=None):
    sim = get_optional_target(opt_target, _connection)
    if sim is None:
        return False
    else:
        sim_info = sim.sim_info
        if set_messy_face is None:
            sim_info.messy_face = not sim_info.messy_face
        else:
            sim_info.messy_face = set_messy_face


@sims4.commands.Command('sims.test_path')
def test_path(obj_id: int=None, walkstyle_name='walk', _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    if obj is not None:
        route = routing.Route(routing.Location(obj.location.transform.translation, obj.location.transform.orientation, obj.location.routing_surface), ())
        path = routing.Path(obj, route)
        path.status = routing.Path.PLANSTATUS_READY
        start_pos = obj.location.transform.translation
        last_pos = start_pos
        start_surface = obj.location.routing_surface
        walkstyle = sims4.hash_util.hash32(walkstyle_name)
        walk_duration, walk_distance = routing.get_walkstyle_info(walkstyle, obj.age, obj.gender, obj.species)
        speed = walk_distance / walk_duration
        a = 2.5
        b = 0.1
        last_time = 0
        for i in range(51):
            angle = i * 0.25120000000000003
            x = (a + b * angle) * math.cos(angle)
            y = (a + b * angle) * math.sin(angle)
            pos = sims4.math.Vector3(start_pos.x + x, start_pos.y + i * 0.1, start_pos.z + y)
            dir = pos - last_pos
            orientation = sims4.math.Quaternion.from_forward_vector(dir)
            if i == 0:
                path.nodes.add_node(routing.Location(start_pos, orientation, start_surface), 0, 0, walkstyle)
            time = last_time + dir.magnitude() / speed
            path.nodes.add_node(routing.Location(pos, orientation, start_surface), time, 0, walkstyle)
            last_time = time
            last_pos = pos

        pos = sims4.math.Vector3(start_pos.x, start_pos.y, start_pos.z)
        dir = pos - last_pos
        orientation = sims4.math.Quaternion.from_forward_vector(dir)
        time = last_time + dir.magnitude() / speed
        path.nodes.add_node(routing.Location(pos, orientation, start_surface), time, 0, walkstyle)
        zone_id = obj.zone_id
        zone = services._zone_manager.get(zone_id)
        start_time = services.game_clock_service().monotonic_time()
        op = distributor.ops.FollowRoute(obj, path, start_time)
        distributor.ops.record(obj, op)
        final_path_node = path.nodes[-1]
        final_position = (sims4.math.Vector3)(*final_path_node.position)
        final_orientation = (sims4.math.Quaternion)(*final_path_node.orientation)
        transform = sims4.math.Transform(final_position, final_orientation)
        obj.location = obj.location.clone(routing_surface=start_surface, transform=transform)


@sims4.commands.Command('sims.set_actor_type')
def set_actor_type(obj_id: int=None, rtti_type: int=149264255, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('set_actor_type: Object ID not in the object manager.', _connection)
    if obj is not None:
        op = distributor.ops.SetActorType(rtti_type)
        distributor.ops.record(obj, op)


@sims4.commands.Command('sims.set_species')
def set_species(obj_id: int=None, species_type: int=0, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('set_species: Object ID not in the object manager.', _connection)
    if obj is not None:
        op = distributor.ops.SetSpecies(species_type)
        distributor.ops.record(obj, op)


@sims4.commands.Command('sims.test_jig')
def test_jig(opt_sim: OptionalTargetParam=None, _connection=None):
    sim_a = get_optional_target(opt_sim, _connection)
    if sim_a is not None:
        translation = sim_a.transform.translation
        orientation = sim_a.transform.orientation
        routing_surface = sim_a.routing_surface
        location = routing.Location(translation, orientation, routing_surface)
        fwd = orientation.transform_vector(sims4.math.Vector3.Z_AXIS())
        cross = sims4.math.vector_cross(fwd, sims4.math.Vector3.Y_AXIS())
        offset = 1.25
        a_width = 0.5
        b_width = 0.75
        a_length = 0.5
        b_length = 1.25
        vertices = []
        vertices.append(translation - a_width * cross)
        vertices.append(translation - a_width * cross - a_length * fwd)
        vertices.append(translation + a_width * cross - a_length * fwd)
        vertices.append(translation + a_width * cross)
        vertices.append(translation + fwd * offset + b_width * cross)
        vertices.append(translation + fwd * offset + b_width * cross + b_length * fwd)
        vertices.append(translation + fwd * offset - b_width * cross + b_length * fwd)
        vertices.append(translation + fwd * offset - b_width * cross)
        poly = sims4.geometry.Polygon(vertices)
        context = placement.FindGoodLocationContext(location, object_polygons=(poly,), search_flags=(placement.FGLSearchFlagsDefault | placement.FGLSearchFlag.ALLOW_GOALS_IN_SIM_POSITIONS | placement.FGLSearchFlag.ALLOW_GOALS_IN_SIM_INTENDED_POSITIONS))
        new_translation, new_orientation, _ = context.find_good_location()
        fwd = new_orientation.transform_vector(sims4.math.Vector3.Z_AXIS())
        cross = sims4.math.vector_cross(fwd, sims4.math.Vector3.Y_AXIS())
        vertices = []
        vertices.append(new_translation - a_width * cross)
        vertices.append(new_translation - a_width * cross - a_length * fwd)
        vertices.append(new_translation + a_width * cross - a_length * fwd)
        vertices.append(new_translation + a_width * cross)
        vertices.append(new_translation + fwd * offset + b_width * cross)
        vertices.append(new_translation + fwd * offset + b_width * cross + b_length * fwd)
        vertices.append(new_translation + fwd * offset - b_width * cross + b_length * fwd)
        vertices.append(new_translation + fwd * offset - b_width * cross)
        poly = sims4.geometry.Polygon(vertices)
        sim_a.test_footprint = PolygonFootprint(poly, routing_surface=routing_surface, cost=25, footprint_type=(FootprintType.FOOTPRINT_TYPE_OBJECT), enabled=True)
        return True
    return False


@sims4.commands.Command('sims.raytest_3d')
def raytest_3d(x1=0.0, y1=0.0, z1=0.0, x2=0.0, y2=0.0, z2=0.0, radius=0.0, opt_sim=None, _connection=None):
    if x1 == 0:
        if y1 == 0:
            if z1 == 0:
                if x2 == 0:
                    if y2 == 0:
                        if z2 == 0:
                            sims4.commands.output('raytest_3d: no ray set.', _connection)
                            return False
    else:
        start = sims4.math.Vector3(x1, y1, z1)
        end = sims4.math.Vector3(x2, y2, z2)
        color = 4278255360
        sims4.commands.execute('debugvis.draw.stop', _connection)
        if placement.ray_intersects_placement_3d((services.current_zone_id()), start, end, radius=radius):
            sims4.commands.output('raytest_3d: Found Intersection', _connection)
            color = 4294901760
        else:
            sims4.commands.output('raytest_3d: No Intersection', _connection)
    sims4.commands.execute('debugvis.draw.line {} {} {} {} {} {} false {}'.format(x1, y1, z1, x2, y2, z2, color), _connection)
    if radius > 0.0:
        dir = sims4.math.vector_normalize(end - start)
        orientation = sims4.math.Quaternion.from_forward_vector(dir)
        cross1 = orientation.transform_vector(sims4.math.Vector3.Y_AXIS()) * radius
        cross2 = orientation.transform_vector(sims4.math.Vector3.X_AXIS()) * radius
        sims4.commands.execute('debugvis.draw.line {} {} {} {} {} {} false {}'.format(x1 - cross1.x, y1 - cross1.y, z1 - cross1.z, x2 - cross1.x, y2 - cross1.y, z2 - cross1.z, color), _connection)
        sims4.commands.execute('debugvis.draw.line {} {} {} {} {} {} false {}'.format(x1 + cross1.x, y1 + cross1.y, z1 + cross1.z, x2 + cross1.x, y2 + cross1.y, z2 + cross1.z, color), _connection)
        sims4.commands.execute('debugvis.draw.line {} {} {} {} {} {} false {}'.format(x1 - cross2.x, y1 - cross2.y, z1 - cross2.z, x2 - cross2.x, y2 - cross2.y, z2 - cross2.z, color), _connection)
        sims4.commands.execute('debugvis.draw.line {} {} {} {} {} {} false {}'.format(x1 + cross2.x, y1 + cross2.y, z1 + cross2.z, x2 + cross2.x, y2 + cross2.y, z2 + cross2.z, color), _connection)


@sims4.commands.Command('sims.take_out_loan')
def take_out_loan(opt_sim: OptionalSimInfoParam=None, loan_amount: float=0.0, loan_type: LoanType=LoanType.INVALID, _connection=None):
    if loan_type is LoanType.INVALID:
        sims4.commands.output('take_out_loan: Invalid loan type specified', _connection)
        return False
    sim_info = get_optional_target(opt_sim, _connection=_connection)
    if sim_info is None:
        sims4.commands.output('take_out_loan: No sim_info specified', _connection)
        return False
    loan_amount = LoanTunables.get_loan_amount(loan_amount, loan_type)
    LoanTunables.add_debt(sim_info, loan_amount)
    return True