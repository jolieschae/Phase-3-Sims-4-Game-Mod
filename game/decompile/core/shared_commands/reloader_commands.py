# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\shared_commands\reloader_commands.py
# Compiled at: 2017-05-18 14:41:07
# Size of source mod 2**32: 2439 bytes
import sys, sims4.commands, sims4.core_services, sims4.log, sims4.reload_service
logger = sims4.log.Logger('Reloader Commands')

@sims4.commands.Command('hot.files.list')
def hot_files_list(_connection=None):
    output = sims4.commands.Output(_connection)
    for name, change_set in sims4.core_services.directory_watcher_manager().get_change_sets().items():
        output("Change Set '{}':".format(name))
        filenames = list(change_set)
        filenames.sort()
        for filename in filenames:
            output('  {}'.format(filename))


@sims4.commands.Command('hot.files.consume')
def hot_files_consume(name: str, _connection=None):
    output = sims4.commands.Output(_connection)
    output("Change Set '{}':".format(name))
    filenames = list(sims4.core_services.directory_watcher_manager().consume_set(name))
    for filename in sorted(filenames):
        output('  {}'.format(filename))


@sims4.commands.Command('hot.reload')
def hot_reload(*args, _connection=None):
    output = sims4.commands.Output(_connection)
    if not args:
        sims4.reload_service.trigger_reload(output)
    else:
        module_paths = []
        for module_name in args:
            module = sys.modules.get(module_name)
            if module is None:
                output('Could not find module: {}'.format(module_name))
                continue
            if not hasattr(module, '__file__'):
                output('Cannot reload builtin module: {}'.format(module_name))
                continue
            module_paths.append(module.__file__)

        sims4.reload_service.reload_files(module_paths, output)