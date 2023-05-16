# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\ensemble\ensemble_interactions.py
# Compiled at: 2016-07-12 21:28:12
# Size of source mod 2**32: 1070 bytes
from objects.base_interactions import ProxyInteraction
from sims4.utils import classproperty, flexmethod

class EnsembleConstraintProxyInteraction(ProxyInteraction):
    INSTANCE_SUBCLASSES_ONLY = True

    @classproperty
    def proxy_name(cls):
        return '[Ensemble]'

    @classmethod
    def generate(cls, proxied_affordance, ensemble):
        result = super().generate(proxied_affordance)
        result.ensemble = ensemble
        return result

    @flexmethod
    def _constraint_gen(cls, inst, *args, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        for constraint in (super(__class__, inst_or_cls)._constraint_gen)(*args, **kwargs):
            yield constraint

        yield inst_or_cls.ensemble.get_center_of_mass_constraint()