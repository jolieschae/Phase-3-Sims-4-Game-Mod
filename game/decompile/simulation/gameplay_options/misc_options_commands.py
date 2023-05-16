# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gameplay_options\misc_options_commands.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 2292 bytes
import services, sims4
from event_testing.game_option_tests import TestableGameOptions
from event_testing.test_events import TestEvent
from sims4.common import Pack

@sims4.commands.Command('misc_options.restrict_npc_werewolves', pack=(Pack.GP12), command_type=(sims4.commands.CommandType.Live))
def restrict_npc_werwolves(enabled: bool=False, _connection=None):
    misc_options_service = services.misc_options_service()
    if misc_options_service is None:
        return False
    misc_options_service.set_restrict_npc_werewolves(enabled)
    services.get_event_manager().process_event((TestEvent.TestedGameOptionChanged), custom_keys=(
     TestableGameOptions.RESTRICT_NPC_WEREWOLVES,))
    return True


@sims4.commands.Command('misc_options.npc_relationship_autonomy_enabled', pack=(Pack.GP12), command_type=(sims4.commands.CommandType.Live))
def npc_relationship_autonomy_enabled(enabled: bool=False, _connection=None):
    misc_options_service = services.misc_options_service()
    if misc_options_service is None:
        return False
    misc_options_service.set_npc_relationship_autonomy_enabled(enabled)
    services.get_event_manager().process_event((TestEvent.TestedGameOptionChanged), custom_keys=(
     TestableGameOptions.NPC_RELATIONSHIP_AUTONOMY_ENABLED,))
    return True


@sims4.commands.Command('misc_options.self_discovery_enabled', pack=(Pack.EP13), command_type=(sims4.commands.CommandType.Live))
def self_discovery_enabled(enabled: bool=False, _connection=None):
    misc_options_service = services.misc_options_service()
    if misc_options_service is None:
        return False
    misc_options_service.set_self_discovery_enabled(enabled)
    services.get_event_manager().process_event((TestEvent.TestedGameOptionChanged), custom_keys=(
     TestableGameOptions.SELF_DISCOVERY_ENABLED,))
    return True