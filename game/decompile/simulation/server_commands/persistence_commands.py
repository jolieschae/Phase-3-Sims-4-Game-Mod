# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\persistence_commands.py
# Compiled at: 2017-08-02 14:58:32
# Size of source mod 2**32: 2838 bytes
from services.persistence_service import SaveGameData
from sims4.commands import CommandType
import services, sims4.commands

@sims4.commands.Command('persistence.save_game', command_type=(CommandType.Live))
def save_game(send_save_message: bool=False, check_cooldown: bool=True, _connection=None):
    save_game_data = SaveGameData(0, 'scratch', True, None)
    persistence_service = services.get_persistence_service()
    persistence_service.save_using((persistence_service.save_game_gen), save_game_data, send_save_message=send_save_message,
      check_cooldown=check_cooldown)


@sims4.commands.Command('persistence.override_save_slot', command_type=(CommandType.Live))
def override_save_slot(slot_id: int=0, slot_name='Unnamed', auto_save_slot_id: int=None, ignore_callback=False, _connection=None):
    save_game_data = SaveGameData(slot_id, slot_name, True, auto_save_slot_id)
    persistence_service = services.get_persistence_service()
    persistence_service.save_using((persistence_service.save_game_gen), save_game_data, send_save_message=True,
      check_cooldown=False,
      ignore_callback=ignore_callback)


@sims4.commands.Command('persistence.save_to_new_slot', command_type=(CommandType.Live))
def save_to_new_slot(slot_id: int=0, slot_name='Unnamed', auto_save_slot_id: int=None, ignore_callback=False, _connection=None):
    save_game_data = SaveGameData(slot_id, slot_name, False, auto_save_slot_id)
    persistence_service = services.get_persistence_service()
    persistence_service.save_using((persistence_service.save_game_gen), save_game_data, send_save_message=True,
      check_cooldown=False,
      ignore_callback=ignore_callback)


@sims4.commands.Command('persistence.save_game_with_autosave', command_type=(CommandType.Live))
def save_game_with_autosave(slot_id: int=0, slot_name='Unnamed', is_new_slot: bool=False, auto_save_slot_id: int=None, _connection=None):
    override_slot = not is_new_slot
    save_game_data = SaveGameData(slot_id, slot_name, override_slot, auto_save_slot_id)
    persistence_service = services.get_persistence_service()
    persistence_service.save_using((persistence_service.save_game_gen), save_game_data, send_save_message=True,
      check_cooldown=False)