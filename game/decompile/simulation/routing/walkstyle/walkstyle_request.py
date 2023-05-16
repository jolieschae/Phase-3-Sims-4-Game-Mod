# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\walkstyle\walkstyle_request.py
# Compiled at: 2021-06-03 14:49:09
# Size of source mod 2**32: 3298 bytes
from element_utils import build_critical_section_with_finally
from routing.walkstyle.walkstyle_enums import WalkStylePriority
from routing.walkstyle.walkstyle_tuning import TunableWalkstyle
from sims4.tuning.tunable import AutoFactoryInit, HasTunableFactory, TunableEnumEntry, Tunable
from uid import unique_id

@unique_id('request_id')
class WalkStyleRequest(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'walkstyle':TunableWalkstyle(description='\n            The locomotion resource (i.e. walkstyle) to request. Depending\n            on the tuned priority and other requests active on the Sim, this\n            may or may not apply immediately.\n            '), 
     'priority':TunableEnumEntry(description='\n            The priority of the walkstyle. Higher priority walkstyles will take\n            precedence over lower priority. Equal priority will favor recent\n            requests.\n            ',
       tunable_type=WalkStylePriority,
       default=WalkStylePriority.INVALID,
       invalid_enums=(
      WalkStylePriority.INVALID,)), 
     'can_replace_with_short_walkstyle':Tunable(description='\n            If checked, this walkstyle can be replaced with the short walkstyle\n            tuned on the routing component if the path distance is shorter than \n            the short walkstyle distance (also tuned on the routing component).\n            \n            Note that if you never want a certain walkstyle to be replaced \n            by the default short walkstyle, you can use the "short walkstyle \n            map" (also on the routing component) to override it. \n            \n            Also note that if this walkstyle ends up being replaced via \n            "Combo Walktyle Replacements" (also on the routing component), the \n            replaced walkstyle will not adhere to this tuning. \n            ',
       tunable_type=bool,
       default=True)}

    def __init__(self, obj, *args, can_replace_with_short_walkstyle=True, **kwargs):
        (super().__init__)(args, can_replace_with_short_walkstyle=can_replace_with_short_walkstyle, **kwargs)
        self._obj = obj.ref()

    def start(self, *_, **__):
        obj = self._obj()
        if obj is None:
            return
        obj.request_walkstyle(self, self.request_id)

    def stop(self, *_, **__):
        obj = self._obj()
        if obj is None:
            return
        obj.remove_walkstyle(self.request_id)

    def __call__(self, sequence=()):
        return build_critical_section_with_finally(self.start, sequence, self.stop)