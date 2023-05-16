# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\localization_commands.py
# Compiled at: 2014-04-08 16:49:13
# Size of source mod 2**32: 1749 bytes
from protocolbuffers.Consts_pb2 import MSG_LOCALIZED_STRING_VALIDATE
from protocolbuffers.Localization_pb2 import LocalizedStringValidate
from sims.sim_spawner import SimSpawner
from sims4.localization.localization_validation import get_all_strings_to_validate_gen
import services, sims4.commands

@sims4.commands.Command('localization.validate_strings', command_type=(sims4.commands.CommandType.Automation))
def localization_validate_strings(all_locales: bool=False, _connection=None):
    output = sims4.commands.Output(_connection)
    client = services.client_manager().get(_connection)
    if client is None:
        output('Unable to find client.')
        return False
    locales = iter(SimSpawner.LOCALE_MAPPING) if all_locales else (client.account.locale,)
    for locale in locales:
        sims4.commands.client_cheat('ui.loc.set_locale {}'.format(locale), _connection)
        msg = LocalizedStringValidate()
        for localized_string in get_all_strings_to_validate_gen():
            localized_string_msg = msg.localized_strings.add()
            localized_string_msg.MergeFrom(localized_string)

        client.send_message(MSG_LOCALIZED_STRING_VALIDATE, msg)

    sims4.commands.client_cheat('ui.loc.set_locale {}'.format(client.account.locale), _connection)
    return True