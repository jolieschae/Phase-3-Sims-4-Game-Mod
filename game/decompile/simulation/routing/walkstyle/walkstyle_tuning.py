# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\walkstyle\walkstyle_tuning.py
# Compiled at: 2019-06-06 13:53:41
# Size of source mod 2**32: 1922 bytes
from sims4.tuning.tunable import TunableResourceKey
from sims4.tuning.tunable_hash import _Hash
import routing, sims4.resources

class Walkstyle(_Hash):

    @property
    def animation_parameter(self):
        return self.unhash


class TunableWalkstyle(TunableResourceKey):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, resource_types=(sims4.resources.Types.WALKSTYLE,), **kwargs)

    @property
    def validate_pack_safe(self):
        return False

    def load_etree_node(self, node, source, expect_error):
        value = super().load_etree_node(node, source, expect_error)
        if value is not None:
            walkstyle_hash = routing.get_walkstyle_hash_from_resource(value)
            walkstyle_name = routing.get_walkstyle_name_from_resource(value)
            value = Walkstyle(walkstyle_name, walkstyle_hash)
        return value