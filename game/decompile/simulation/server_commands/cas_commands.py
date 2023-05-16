# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\cas_commands.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 15910 bytes
from business.business_enums import BusinessEmployeeType
from clubs.club_enums import ClubOutfitSetting
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target, RequiredTargetParam, OptionalSimInfoParam
from sims.occult.occult_enums import OccultType
from sims.outfits.outfit_enums import OutfitCategory
from sims.sim_info_types import Gender, Age
from sims4.commands import CommandRestrictionFlags
from sims4.common import Pack
from sims4.resources import get_protobuff_for_key
import services, sims4.commands

@sims4.commands.Command('sims.modify_in_cas', command_type=(sims4.commands.CommandType.Live), command_restrictions=(CommandRestrictionFlags.RESTRICT_SAVE_UNLOCKED))
def modify_in_cas(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('No valid target for sims.modify_in_cas.', _connection)
        return False
    sims4.commands.client_cheat('sims.exit2cas {} {} {}'.format(sim.id, sim.household_id, services.get_active_sim().id), _connection)
    return True


@sims4.commands.Command('sims.modify_outfit_in_cas', command_type=(sims4.commands.CommandType.Live), command_restrictions=(CommandRestrictionFlags.RESTRICT_SAVE_UNLOCKED))
def modify_outfit_in_cas(outfit_category: int, outfit_index: int=0, opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('No valid target for sims.modify_in_cas.', _connection)
        return False
    sims4.commands.client_cheat('sims.exit2cas {} {} {} outfitType {}'.format(sim.id, sim.household_id, services.get_active_sim().id, outfit_category), _connection)
    return True


@sims4.commands.Command('sims.modify_in_cas_with_householdId', command_type=(sims4.commands.CommandType.Live), command_restrictions=(CommandRestrictionFlags.RESTRICT_SAVE_UNLOCKED))
def modify_in_cas_with_household_id(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('No valid target for sims.modify_in_cas_with_householdId.', _connection)
        return False
    sims4.commands.client_cheat('sims.exit2caswithhouseholdid {} {}'.format(sim.id, sim.household_id), _connection)
    return True


@sims4.commands.Command('sims.modify_career_outfit_in_cas', command_type=(sims4.commands.CommandType.Live), command_restrictions=(CommandRestrictionFlags.RESTRICT_SAVE_UNLOCKED))
def modify_career_outfit_in_cas(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('No valid target specified.', _connection)
        return False
    sims4.commands.client_cheat('sims.exit2caswithhouseholdid {} {} career'.format(sim.id, sim.household_id), _connection)
    return True


@sims4.commands.Command('sims.modify_disguise_in_cas', command_type=(sims4.commands.CommandType.Live), command_restrictions=(CommandRestrictionFlags.RESTRICT_SAVE_UNLOCKED))
def modify_disguise_in_cas(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('No valid target specified.', _connection)
        return False
    occult_tracker = sim.sim_info.occult_tracker
    occult_tracker.set_pending_occult_type(sim.sim_info.current_occult_types)
    occult_tracker.switch_to_occult_type(OccultType.HUMAN)
    sims4.commands.client_cheat('sims.exit2caswithhouseholdid {} {} disguise'.format(sim.id, sim.household_id), _connection)
    return True


@sims4.commands.Command('sims.modify_gender_in_cas', command_type=(sims4.commands.CommandType.Live), command_restrictions=(CommandRestrictionFlags.RESTRICT_SAVE_UNLOCKED))
def modify_gender_in_cas(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('No valid target specified.', _connection)
        return False
    sims4.commands.client_cheat('sims.exit2caswithhouseholdid {} {} gender'.format(sim.id, sim.household_id), _connection)
    return True


@sims4.commands.Command('cas.modify_mannequin', command_type=(sims4.commands.CommandType.Live), command_restrictions=(CommandRestrictionFlags.RESTRICT_SAVE_UNLOCKED))
def modify_mannequin_in_cas(obj_id: RequiredTargetParam=None, apply_outfit=False, _connection=None):
    mannequin = obj_id.get_target()
    if mannequin is None:
        sims4.commands.output('No valid target with the specified ID found.', _connection)
        return False
    mannequin_component = mannequin.mannequin_component
    if mannequin_component is None:
        sims4.commands.output('The specified target does not have a Mannequin component.', _connection)
        return False
    persistence_service = services.get_persistence_service()
    if persistence_service is not None:
        persistence_service.del_mannequin_proto_buff(mannequin.id)
        sim_info_data_proto = persistence_service.add_mannequin_proto_buff()
        mannequin_component.populate_sim_info_data_proto(sim_info_data_proto)
        current_zone_id = services.current_zone_id()
        sim_info_data_proto.zone_id = current_zone_id
        sim_info_data_proto.world_id = persistence_service.get_world_id_from_zone(current_zone_id)
        sims4.commands.client_cheat('sims.exit2caswithmannequinid {} {}'.format(mannequin.id, 'apply_outfit' if apply_outfit else ''), _connection)
    return True


@sims4.commands.Command('cas.modify_business_uniform', command_type=(sims4.commands.CommandType.Live), pack=(Pack.EP01), command_restrictions=(CommandRestrictionFlags.RESTRICT_SAVE_UNLOCKED))
def modify_business_uniform_in_cas(employee_type: BusinessEmployeeType, gender: Gender, _connection=None):
    business_manager = services.business_service().get_business_manager_for_zone()
    if business_manager is None:
        return False
    employee_uniform_data = business_manager.get_employee_uniform_data(employee_type, gender)
    if employee_uniform_data is None:
        return False
    persistence_service = services.get_persistence_service()
    if persistence_service is not None:
        sim_info_data_proto = persistence_service.prepare_mannequin_for_cas(employee_uniform_data)
        uniform_pose = business_manager.get_uniform_pose_for_employee_type(employee_type)
        if uniform_pose is not None:
            sim_info_data_proto.animation_pose.asm = get_protobuff_for_key(uniform_pose.asm)
            sim_info_data_proto.animation_pose.state_name = uniform_pose.state_name
        sims4.commands.client_cheat('sims.exit2caswithmannequinid {} career'.format(employee_uniform_data.sim_id), _connection)
    return True


@sims4.commands.Command('cas.modify_club_mannequin_in_cas', command_type=(sims4.commands.CommandType.Live), pack=(Pack.EP02), command_restrictions=(CommandRestrictionFlags.RESTRICT_SAVE_UNLOCKED))
def modify_club_mannequin_in_cas(club_id: int, age: Age, gender: Gender, _connection=None):
    club_service = services.get_club_service()
    if club_service is None:
        return False
    club = club_service.get_club_by_id(club_id)
    if club is None:
        sims4.commands.output('The specified club_id could not be found. Please specify a valid club_id.', _connection)
        return False
    club_uniform_data = club.get_club_uniform_data(age, gender)
    if club_uniform_data is None:
        sims4.commands.output('There was an error trying to get the uniform data for the specified age, gender', _connection)
        return False
    persistence_service = services.get_persistence_service()
    if persistence_service is not None:
        persistence_service.prepare_mannequin_for_cas(club_uniform_data)
        club.outfit_setting = ClubOutfitSetting.OVERRIDE
        sims4.commands.client_cheat('sims.exit2caswithmannequinid {} club'.format(club_uniform_data.sim_id), _connection)
    return True


@sims4.commands.Command('cas.modify_style_in_cas', command_type=(sims4.commands.CommandType.Live), command_restrictions=(CommandRestrictionFlags.RESTRICT_SAVE_UNLOCKED))
def modify_style_in_cas(gender: Gender, _connection=None):
    style_service = services.get_style_service()
    if style_service is None:
        return False
    style_data = style_service.get_style_outfit_data(gender)
    persistence_service = services.get_persistence_service()
    if persistence_service is not None:
        persistence_service.prepare_mannequin_for_cas(style_data)
        sims4.commands.client_cheat('sims.exit2caswithmannequinid {} career'.format(style_data.sim_id), _connection)
    return True


@sims4.commands.Command('cas.plan_batuu_outfit', pack=(Pack.GP09), command_type=(sims4.commands.CommandType.Live), command_restrictions=(CommandRestrictionFlags.RESTRICT_SAVE_UNLOCKED))
def plan_batuu_outfit(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection, target_type=OptionalSimInfoParam)
    if sim is None:
        sims4.commands.output('No valid target specified.', _connection)
        return False
    else:
        return sim.has_outfit_category(OutfitCategory.BATUU) or False
    sims4.commands.client_cheat('sims.exit2caswithhouseholdid {} {} batuu'.format(sim.id, sim.household_id), _connection)
    return True


@sims4.commands.Command('sims.switch_to_werewolf', command_type=(sims4.commands.CommandType.DebugOnly), command_restrictions=(CommandRestrictionFlags.RESTRICT_SAVE_UNLOCKED))
def switch_to_werewolf_form(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('No valid target specified.', _connection)
        return False
    occult_tracker = sim.sim_info.occult_tracker
    occult_tracker.set_pending_occult_type(sim.sim_info.current_occult_types)
    occult_tracker.switch_to_occult_type(OccultType.WEREWOLF)
    return True


@sims4.commands.Command('cas.design_fashion_outfits', command_type=(sims4.commands.CommandType.Live), command_restrictions=(CommandRestrictionFlags.RESTRICT_SAVE_UNLOCKED))
def design_fashion_outfits_in_cas(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_target=opt_sim, _connection=_connection, target_type=OptionalSimInfoParam)
    if sim_info is None:
        sims4.commands.output('No valid target specified.', _connection)
        return False
    active_sim_info = services.active_sim_info()
    if active_sim_info is not None:
        if active_sim_info.id != sim_info.id:
            return False
    fashion_trend_service = services.fashion_trend_service()
    if fashion_trend_service is None:
        sims4.commands.output('fashion_trend_service is None', _connection)
        return False
    fashion_trend_service.thrift_store_mannequin = fashion_trend_service.get_mannequin(sim_info.clothing_preference_gender)
    if fashion_trend_service.thrift_store_mannequin is None:
        sims4.commands.output('There was an error trying to get the mannequin data for the specified age {}, and gender {}'.format(sim_info.age, sim_info.clothing_preference_gender), _connection)
        return False
    persistence_service = services.get_persistence_service()
    if persistence_service is not None:
        sim_info_data_proto = persistence_service.prepare_mannequin_for_cas(fashion_trend_service.thrift_store_mannequin)
        mannequin_pose = fashion_trend_service.get_mannequin_pose()
        if mannequin_pose is not None:
            sim_info_data_proto.animation_pose.asm = get_protobuff_for_key(mannequin_pose.asm)
            sim_info_data_proto.animation_pose.state_name = mannequin_pose.state_name
        sims4.commands.client_cheat('sims.exit2caswithmannequinid {} fashion {}'.format(fashion_trend_service.thrift_store_mannequin.id, sim_info.id), _connection)
    return True


@sims4.commands.Command('sims.modify_preferences_in_cas', command_type=(sims4.commands.CommandType.Live), command_restrictions=(CommandRestrictionFlags.RESTRICT_SAVE_UNLOCKED))
def modify_preferences_in_cas(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('No valid target specified.', _connection)
        return False
    sims4.commands.client_cheat('sims.exit2caswithhouseholdid {} {} preferences'.format(sim.id, sim.household_id), _connection)
    return True