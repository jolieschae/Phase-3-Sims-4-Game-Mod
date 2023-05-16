# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\shared_commands\diagnostic_commands.py
# Compiled at: 2014-06-11 04:51:23
# Size of source mod 2**32: 1008 bytes
import sims4.commands

@sims4.commands.Command('diagnostic.stack_overflow')
def diagnostic_stack_overflow(_connection=None):

    def recursive_fn():
        recursive_fn()

    recursive_fn()


@sims4.commands.Command('diagnostic.stack_overflow_property')
def diagnostic_stack_overflow_property(_connection=None):

    class Rec:

        @property
        def recursive_property(self):
            return self.recursive_property

    Rec().recursive_property


@sims4.commands.Command('diagnostic.infinite_loop')
def diagnostic_infinite_loop(_connection=None):
    while True:
        pass