# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\mtx_commands.py
# Compiled at: 2015-01-26 16:25:18
# Size of source mod 2**32: 553 bytes
import sims4.commands, sims4.common

@sims4.commands.Command('mtx.show_pack_entitlements')
def show_pack_entitlements(_connection=None):
    output = sims4.commands.Output(_connection)
    output('Available packs:')
    for pack in sims4.common.get_available_packs():
        output('    {}'.format(pack))

    return True