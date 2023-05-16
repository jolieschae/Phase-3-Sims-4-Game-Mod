# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\shared_commands\unittestcmd.py
# Compiled at: 2013-05-09 01:53:35
# Size of source mod 2**32: 1521 bytes
from sims4.commands import Command

class ConsoleOutput:
    try:

        def write(self, message):
            import sims4.log
            text = message.strip('\n')
            if text:
                sims4.log.info('Console', text)

    except:

        def write(self, message):
            text = message.strip('\n')
            print(text)


@Command('test.module')
def run_module_test(module, verbose: bool=False, _connection=None):
    import sims4.testing.unit
    sims4.testing.unit.test_module_by_name(module, (set()), verbose=(bool(verbose)), file_=(ConsoleOutput()))


@Command('test.path')
def run_path_test(filename, verbose: bool=False, _connection=None):
    import sims4.testing.unit
    sims4.testing.unit.test_path(filename, (set()), verbose=(bool(verbose)), file_=(ConsoleOutput()))