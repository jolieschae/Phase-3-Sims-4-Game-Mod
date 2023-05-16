# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\postures\generic_posture_node.py
# Compiled at: 2018-10-29 19:13:01
# Size of source mod 2**32: 520 bytes
from objects.proxy import ProxyObject

class SimPostureNode(ProxyObject):

    def __str__(self):
        return 'Generic Sim Node ' + str(self._proxied_obj)

    @property
    def sim_proxied(self):
        return self._proxied_obj