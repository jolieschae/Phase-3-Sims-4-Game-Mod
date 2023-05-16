# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\formation\formation_type_paired.py
# Compiled at: 2018-10-24 12:56:03
# Size of source mod 2**32: 707 bytes
from protocolbuffers import Routing_pb2
from routing.formation.formation_type_base import FormationTypeBase, FormationRoutingType
from sims4.utils import classproperty

class FormationTypePaired(FormationTypeBase):

    @classproperty
    def routing_type():
        return FormationRoutingType.PARIED

    @property
    def slave_attachment_type(self):
        return Routing_pb2.SlaveData.SLAVE_PAIRED_CHILD