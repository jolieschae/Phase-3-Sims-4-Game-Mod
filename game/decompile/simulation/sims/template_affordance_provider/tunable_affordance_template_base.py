# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\template_affordance_provider\tunable_affordance_template_base.py
# Compiled at: 2017-02-15 19:45:03
# Size of source mod 2**32: 691 bytes


class TunableAffordanceTemplateBase:

    def get_template_affordance(self):
        raise NotImplementedError

    def get_template_kwargs(self):
        raise NotImplementedError