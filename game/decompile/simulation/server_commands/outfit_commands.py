# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\outfit_commands.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 9443 bytes
import functools, services
from cas.cas import get_tags_from_outfit
from objects.components.mannequin_component import MannequinGroupSharingMode, set_mannequin_group_sharing_mode
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target, OptionalSimInfoParam, TunableInstanceParam
from sims.outfits import outfit_generator
from sims.outfits.outfit_enums import OutfitCategory
from sims4.commands import CommandType
from tag import Tag
import sims4.commands

@sims4.commands.Command('outfits.generate_outfit')
def generate_outfit(outfit_category: OutfitCategory, outfit_index: int=0, obj_id: OptionalTargetParam=None, outfit_gen: TunableInstanceParam(sims4.resources.Types.SNIPPET)=None, _connection=None):
    obj = get_optional_target(obj_id, _connection)
    if obj is None:
        return False
    else:
        outfits = obj.get_outfits()
        if outfits is None:
            return False
            sim_info = outfits.get_sim_info()
            if outfit_gen is not None:
                fn = functools.partial(outfit_gen, sim_info)
        else:
            fn = sim_info.generate_outfit
    fn(outfit_category=outfit_category, outfit_index=outfit_index)
    output = sims4.commands.Output(_connection)
    output('Generated {} outfit {}.'.format(outfit_category, outfit_index))
    return True


@sims4.commands.Command('outfits.switch_outfit')
def switch_outfit(outfit_category: OutfitCategory=0, outfit_index: int=0, obj_id: OptionalTargetParam=None, _connection=None):
    obj = get_optional_target(obj_id, _connection)
    if obj is None:
        return False
    outfits = obj.get_outfits()
    if outfits is None:
        return False
    sim_info = outfits.get_sim_info()
    sim_info.set_current_outfit((outfit_category, outfit_index))
    return True


@sims4.commands.Command('outfits.info')
def show_outfit_info(obj_id: OptionalTargetParam=None, _connection=None):
    obj = get_optional_target(obj_id, _connection)
    if obj is None:
        return False
    outfits = obj.get_outfits()
    if outfits is None:
        return False
    sim_info = outfits.get_sim_info()
    output = sims4.commands.Output(_connection)
    output('Current outfit: {}'.format(sim_info.get_current_outfit()))
    output('Previous outfit: {}'.format(sim_info.get_previous_outfit()))
    for outfit_category, outfit_list in outfits.get_all_outfits():
        output('\t{}'.format(OutfitCategory(outfit_category)))
        for outfit_index, outfit_data in enumerate(outfit_list):
            output('\t\t{}: {}'.format(outfit_index, ', '.join((str(part) for part in outfit_data.part_ids))))

    output('')
    return True


@sims4.commands.Command('outfits.set_sharing_mode', command_type=(CommandType.Live))
def set_outfit_sharing_mode(outfit_sharing_mode: MannequinGroupSharingMode):
    set_mannequin_group_sharing_mode(outfit_sharing_mode)
    return True


@sims4.commands.Command('outfits.remove_outfit')
def remove_outfit(outfit_category: OutfitCategory, outfit_index: int=0, obj_id: OptionalTargetParam=None, _connection=None):
    obj = get_optional_target(obj_id, _connection)
    if obj is None:
        return False
    outfit_tracker = obj.get_outfits()
    if outfit_tracker is None:
        return False
    outfit_tracker.remove_outfit(outfit_category, outfit_index)
    return True


@sims4.commands.Command('outfits.copy_outfit', command_type=(CommandType.Live))
def copy_outfit(destination_outfit_category, source_outfit_category, source_outfit_index=0, obj_id=None, _connection=None):
    obj = get_optional_target(obj_id, _connection)
    if obj is None:
        return False
    else:
        outfit_tracker = obj.get_outfits()
        if outfit_tracker is None:
            return False
        return outfit_tracker.has_outfit((source_outfit_category, source_outfit_index)) or False
    outfit_data = outfit_tracker.get_outfit(source_outfit_category, source_outfit_index)
    destination_outfit = outfit_tracker.add_outfit(destination_outfit_category, outfit_data)
    sim_info = outfit_tracker.get_sim_info()
    sim_info.on_outfit_generated(destination_outfit[0], destination_outfit[1])
    sim_info.resend_outfits()
    sim_info.set_current_outfit(destination_outfit)
    return True


@sims4.commands.Command('outfits.get_tags')
def print_outfit_tags(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    current_outfit_category, current_outfit_index = sim_info.get_current_outfit()
    tag_values = (set().union)(*get_tags_from_outfit(sim_info._base, current_outfit_category, current_outfit_index).values())
    output = sims4.commands.Output(_connection)
    tag_names = [Tag(tag_value).name for tag_value in tag_values]
    tag_names.sort()
    for tag in tag_names:
        output(tag)


@sims4.commands.Command('outfits.current_outfit_info', command_type=(sims4.commands.CommandType.Automation))
def get_current_outfit_info(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        return False
    outfit_category, outfit_index = sim_info.get_current_outfit()
    sims4.commands.automation_output('OutfitInfo; OutfitCategory:{}, OutfitIndex:{}'.format(outfit_category, outfit_index), _connection)
    return True


@sims4.commands.Command('outfits.toggle_outfit_change_log')
def toggle_outfit_change_log(_connection=None):
    output = sims4.commands.Output(_connection)
    enable = not outfit_generator.outfit_change_log_enabled
    if enable:
        outfit_generator.outfit_change_log_enabled = True
        output('Outfit generation logging enabled.')
    else:
        outfit_generator.outfit_change_log_enabled = False
        output('Outfit generation logging disabled.')
    return True


@sims4.commands.Command('outfits.check_fashion_outfits_on_mannequin', command_type=(sims4.commands.CommandType.DebugOnly))
def check_fashion_outfits_on_mannequin(_connection=None):
    fashion_trend_service = services.fashion_trend_service()
    if fashion_trend_service is None:
        sims4.commands.output('fashion_trend_service is None', _connection)
        return False
    if fashion_trend_service.thrift_store_mannequin is None:
        sims4.commands.output('There was no thrift store mannequin currently saved', _connection)
        return False
    outfits = fashion_trend_service.thrift_store_mannequin.get_outfits()
    if outfits is None:
        sims4.commands.output('there are no outfits on mannequin {}'.format(fashion_trend_service.thrift_store_mannequin.id), _connection)
        return False
    sim_infos = outfits.get_sim_info()
    output = sims4.commands.Output(_connection)
    output('Mannequin ID: {}'.format(sim_infos.id))
    output('Current outfit: {}'.format(sim_infos.get_current_outfit()))
    output('Previous outfit: {}'.format(sim_infos.get_previous_outfit()))
    for outfit_category, outfit_list in outfits.get_all_outfits():
        output('\t{}'.format(OutfitCategory(outfit_category)))
        for outfit_index, outfit_data in enumerate(outfit_list):
            outfit_data_trend = outfit_data.trend if outfit_data.trend != 0 else None
            output('\t\t{}: {} - Cost {} - Trend {} - Title {}'.format(outfit_index, ', '.join((str(part) for part in outfit_data.part_ids)), outfit_data.cost, outfit_data_trend, outfit_data.title))

    output('')
    return True


@sims4.commands.Command('outfits.check_thrift_store_inventory', command_type=(sims4.commands.CommandType.DebugOnly))
def check_thrift_store_inventory(_connection=None):
    fashion_trend_service = services.fashion_trend_service()
    if fashion_trend_service is None:
        sims4.commands.output('fashion_trend_service is None', _connection)
        return False
    thrift_store_inventory = fashion_trend_service.get_current_thrift_store_inventory_cas_part_tags()
    output = sims4.commands.Output(_connection)
    output('{}'.format(thrift_store_inventory))
    return True