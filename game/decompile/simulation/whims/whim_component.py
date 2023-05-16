# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\whims\whim_component.py
# Compiled at: 2018-06-07 19:23:49
# Size of source mod 2**32: 1146 bytes
from objects.components import Component
from objects.components.types import WHIM_COMPONENT
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableReference
import services, sims4.resources

class WhimComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=WHIM_COMPONENT):
    FACTORY_TUNABLES = {'whim_set': TunableReference(description='\n            The whim set that is active when this object is on the lot.\n            ',
                   manager=(services.get_instance_manager(sims4.resources.Types.ASPIRATION)),
                   class_restrictions=('ObjectivelessWhimSet', ))}

    def on_add(self):
        self.owner.manager.add_active_whim_set(self.whim_set)

    def on_remove(self):
        self.owner.manager.remove_active_whim_set(self.whim_set)