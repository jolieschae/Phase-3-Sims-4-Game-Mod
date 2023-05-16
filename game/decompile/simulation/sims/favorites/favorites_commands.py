# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\favorites\favorites_commands.py
# Compiled at: 2019-08-07 19:02:24
# Size of source mod 2**32: 3712 bytes
import services, sims4.commands
from server_commands.argument_helpers import OptionalSimInfoParam, get_optional_target, RequiredTargetParam
from tag import Tag

@sims4.commands.Command('favorites.list')
def list_favorites(opt_sim: OptionalSimInfoParam=None, _connection=None):
    output = sims4.commands.Output(_connection)
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        output("Can't find provided Sim.")
        return
    favorites_tracker = sim_info.favorites_tracker
    if favorites_tracker is None:
        output('Sim has no favorites tracker.')
        return
    favorites = favorites_tracker.favorites
    if not favorites:
        output('Sim has no favorites objects.')
        return
    zone = services.current_zone()
    for tag, obj_id in favorites.items():
        output_str = str(tag) + '\t'
        obj_inst = zone.find_object(obj_id)
        if obj_inst is None:
            output_str += 'None (error?)'
        else:
            output_str += str(obj_inst)
        output(output_str)


@sims4.commands.Command('favorites.set')
def set_favorite(favorite_type: Tag, obj: RequiredTargetParam, opt_sim: OptionalSimInfoParam=None, _connection=None):
    output = sims4.commands.Output(_connection)
    obj = obj.get_target()
    if obj is None:
        output("Can't find specified object")
        return
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        output("Can't find provided Sim.")
        return
    favorites_tracker = sim_info.favorites_tracker
    if favorites_tracker is None:
        output('Sim has no favorites tracker.')
        return
    favorites_tracker.set_favorite(favorite_type, obj.id)
    output('{} set as the favorite for type {}'.format(obj, favorite_type))


@sims4.commands.Command('favorites.unset')
def unset_favorite(favorite_type: Tag, opt_sim: OptionalSimInfoParam=None, _connection=None):
    output = sims4.commands.Output(_connection)
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        output("Can't find provided Sim.")
        return
    favorites_tracker = sim_info.favorites_tracker
    if favorites_tracker is None:
        output('Sim has no favorites tracker.')
        return
    favorites_tracker.clear_favorite_type(favorite_type)
    output('Unset favorite for type {}.'.format(favorite_type))


@sims4.commands.Command('favorites.clear')
def clear_favorites(opt_sim: OptionalSimInfoParam=None, _connection=None):
    output = sims4.commands.Output(_connection)
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        output("Can't find provided Sim.")
        return
    favorites_tracker = sim_info.favorites_tracker
    if favorites_tracker is None:
        output('Sim has no favorites tracker.')
        return
    favorites_tracker.clean_up()
    output('Favorites Tracker cleared.')