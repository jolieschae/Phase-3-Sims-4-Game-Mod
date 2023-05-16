# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\template_affordance_provider\tunable_provided_template_affordance.py
# Compiled at: 2017-03-16 18:33:15
# Size of source mod 2**32: 2119 bytes
from sims.template_affordance_provider.tunable_affordance_template_discipline import TunableAffordanceTemplateDiscipline
from sims4.tuning.tunable import TunableTuple, TunableSimMinute, TunableList, TunableVariant, OptionalTunable

class TunableProvidedTemplateAffordance(TunableTuple):

    def __init__(self, description='\n        A list of affordances and template data to attach to the affordances and\n        then provide on the owning sim for some tunable duration.\n        ', **kwargs):
        (super().__init__)(description=description, post_run_duration=OptionalTunable(description='\n                The amount of time, after the provided (interaction, buff, etc.)\n                is done, to provide the templates. If the default time is used,\n                the Default Post Run Duration module tuning will be used.\n                ',
  tunable=TunableSimMinute(description='\n                    The amount of time, after the providing interaction ends, this\n                    set of template affordances will be provided. A duration of 0\n                    minutes means the template affordance will only be provided for\n                    the duration of the providing interaction.\n                    ',
  default=0),
  disabled_name='Use_Default_Time',
  enabled_name='Use_Custom_Time'), 
         template_affordances=TunableList(description='\n                A list of template affordances and their corresponding template\n                data.\n                ',
  tunable=TunableVariant(description='\n                    A template affordance and its template data.\n                    ',
  discipline=(TunableAffordanceTemplateDiscipline.TunableFactory()),
  default='discipline')), **kwargs)