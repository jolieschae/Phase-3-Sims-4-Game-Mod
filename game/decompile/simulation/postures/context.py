# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\postures\context.py
# Compiled at: 2012-07-23 16:36:34
# Size of source mod 2**32: 1031 bytes
from interactions.context import InteractionContext
from interactions.priority import Priority

class PostureContext:
    __slots__ = ('source', 'priority', 'pick')

    def __init__(self, source=InteractionContext.SOURCE_SCRIPT, priority=Priority.Low, pick=None):
        self.source = source
        self.priority = priority
        self.pick = pick

    def __repr__(self):
        return '{0}.{1}({2}, {3})'.format(self.__module__, self.__class__.__name__, self.source, repr(self.priority))