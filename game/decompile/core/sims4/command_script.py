# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\command_script.py
# Compiled at: 2013-10-11 14:21:02
# Size of source mod 2**32: 1865 bytes
import os, paths, sims4.commands, sims4.log
logger = sims4.log.Logger('Commands')

def run_script(filename, _connection=None):
    filename = os.path.join(paths.APP_ROOT, filename)
    if not os.path.isfile(filename):
        logger.error("Could not find file '{}'", filename)
        return False
    with open(filename) as (fd):
        for line in fd:
            command = line.split('#', 1)[0].strip()
            if command.startswith('|'):
                command = command[1:]
                to_server = True
            else:
                to_server = False
            if not command:
                continue
            if to_server:
                sims4.commands.execute(command, _connection)
            elif _connection:
                sims4.commands.client_cheat(command, _connection)
            else:
                logger.error('Cannot send client command without a connection')

    return True