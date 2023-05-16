# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\world_commands.py
# Compiled at: 2018-08-21 21:20:44
# Size of source mod 2**32: 1550 bytes
import sims4.commands
from terrain import get_terrain_height
from routing import SurfaceIdentifier, SurfaceType

@sims4.commands.Command('world.test_surface_height', command_type=(sims4.commands.CommandType.DebugOnly))
def test_surface_height(x: float=0.0, y: float=0.0, z: float=0.0, _connection=None):
    terrain_height = get_terrain_height(x, z, SurfaceIdentifier(0, 0, SurfaceType.SURFACETYPE_WORLD))
    sims4.commands.output('Terrain Surface: {}'.format(terrain_height), _connection)
    object_height = get_terrain_height(x, z, SurfaceIdentifier(0, 0, SurfaceType.SURFACETYPE_OBJECT))
    sims4.commands.output('Object Surface: {}'.format(object_height), _connection)
    water_height = get_terrain_height(x, z, SurfaceIdentifier(0, 0, SurfaceType.SURFACETYPE_POOL))
    sims4.commands.output('Water Surface: {}'.format(water_height), _connection)
    difference = water_height - terrain_height
    sims4.commands.output('Water Height: {}'.format(difference), _connection)


@sims4.commands.Command('world.get_forward', command_type=(sims4.commands.CommandType.DebugOnly))
def get_forward(x1=0.0, y1=0.0, z1=0.0, x2=0.0, y2=0.0, z2=0.0, _connection=None):
    sims4.commands.output('{} {}'.format(x2 - x1, z2 - z1), _connection)