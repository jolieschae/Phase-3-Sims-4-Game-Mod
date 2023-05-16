# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\acting\stage_mark_component.py
# Compiled at: 2018-04-25 21:20:19
# Size of source mod 2**32: 664 bytes
from objects.components import Component, types

class StageMarkComponent(Component, allow_dynamic=True, component_name=types.STAGE_MARK_COMPONENT):

    def __init__(self, *args, performance_interactions=(), **kwargs):
        (super().__init__)(*args, **kwargs)
        self._performance_interactions = performance_interactions

    def component_super_affordances_gen(self, **kwargs):
        yield from self._performance_interactions
        if False:
            yield None