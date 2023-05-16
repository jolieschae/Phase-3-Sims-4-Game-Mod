# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\formation\formation_type_base.py
# Compiled at: 2020-08-25 18:49:34
# Size of source mod 2**32: 3627 bytes
from interactions.constraints import ANYWHERE
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit
from sims4.utils import classproperty
import enum, sims4.math

class FormationRoutingType(enum.Int, export=False):
    NONE = 0
    FOLLOW = ...
    PARIED = ...


class FormationTypeBase(HasTunableFactory, AutoFactoryInit):

    def __init__(self, master, slave, formation_cls, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._master = master
        self._slave = slave
        self._formation_cls = formation_cls

    def set_formation_offset_index(self, index):
        raise NotImplementedError

    @classproperty
    def routing_type():
        return FormationRoutingType.NONE

    @property
    def master(self):
        return self._master

    @property
    def slave(self):
        return self._slave

    @property
    def slave_attachment_type(self):
        return Routing_pb2.SlaveData.SLAVE_NONE

    @staticmethod
    def get_max_slave_count(tuned_factory):
        return sims4.math.MAX_INT32

    @property
    def offset(self):
        return sims4.math.Vector3.ZERO()

    @property
    def route_length_minimum(self):
        return 0

    def attachment_info_gen(self):
        pass
        if False:
            yield None

    def on_add(self):
        pass

    def on_release(self):
        pass

    def on_master_route_start(self):
        pass

    def on_master_route_end(self):
        pass

    def get_routing_slave_constraint(self):
        return ANYWHERE

    def should_slave_for_path(self, path):
        return True

    def build_routing_slave_pb(self, slave_pb, path=None):
        pass

    def update_slave_position(self, master_transform, master_orientation, routing_surface, distribute=True, path=None, canceled=False):
        pass