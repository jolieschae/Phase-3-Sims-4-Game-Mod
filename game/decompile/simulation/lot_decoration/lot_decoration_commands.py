# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\lot_decoration\lot_decoration_commands.py
# Compiled at: 2018-05-03 17:38:19
# Size of source mod 2**32: 2871 bytes
from lot_decoration.lot_decoration_enums import DecorationLocation
from server_commands.argument_helpers import TunableInstanceParam
from sims4.common import Pack
import services, sims4.commands

@sims4.commands.Command('lot_decorations.apply_decoration', pack=(Pack.EP05))
def apply_decoration(decoration: TunableInstanceParam(sims4.resources.Types.LOT_DECORATION), location: DecorationLocation, _connection=None):
    services.lot_decoration_service().apply_decoration_for_holiday(decoration, location, services.active_household().holiday_tracker.get_active_or_upcoming_holiday())


@sims4.commands.Command('lot_decorations.remove_decoration', pack=(Pack.EP05))
def remove_decoration(location: DecorationLocation, _connection=None):
    services.lot_decoration_service().remove_decoration_for_holiday(location, services.active_household().holiday_tracker.get_active_or_upcoming_holiday())


@sims4.commands.Command('lot_decorations.reset_lot_decorations_to_default', pack=(Pack.EP05))
def reset_lot_decorations_to_default(holiday_id: int, _connection=None):
    services.lot_decoration_service().reset_decoration_to_holiday_default(services.active_household().holiday_tracker.get_active_or_upcoming_holiday())


@sims4.commands.Command('lot_decorations.apply_preset_to_neighbors', pack=(Pack.EP05))
def apply_preset_to_neighbors(preset: TunableInstanceParam(sims4.resources.Types.LOT_DECORATION_PRESET), _connection=None):
    services.lot_decoration_service().decorate_neighborhood_for_holiday((services.active_household().holiday_tracker.get_active_or_upcoming_holiday()), preset_override=preset)


@sims4.commands.Command('lot_decorations.apply_preset_to_zone', pack=(Pack.EP05))
def apply_preset_to_zone(preset: TunableInstanceParam(sims4.resources.Types.LOT_DECORATION_PRESET), zone_id: int=None, _connection=None):
    if zone_id is None:
        zone_id = services.current_zone_id()
    services.lot_decoration_service().decorate_zone_for_holiday(zone_id, (services.active_household().holiday_tracker.get_active_or_upcoming_holiday()), preset_override=preset)