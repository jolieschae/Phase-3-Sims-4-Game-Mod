# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relationships\cross_age_tuning.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 2542 bytes
from sims.sim_info_types import Age
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, Tunable, TunableMapping, TunableEnumEntry
from snippets import define_snippet

class CrossAgeTuning(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'default_value':Tunable(description='\n            The default value, if the mapping requested is not found in the cross age tuning.\n            For example:\n            - for multipliers, you would want to set this to 1\n            - for modifiers which are additive, you would want to set this to 0 \n            ',
       tunable_type=float,
       default=1), 
     'cross_age_tuning':TunableMapping(description="\n            A mapping of subject's age to another map of target's age to a tuned value.\n            ",
       key_name='subject_age',
       key_type=TunableEnumEntry(description="\n                The subject's age.\n                ",
       tunable_type=Age,
       default=(Age.ADULT)),
       value_name='target_age_to_multiplier',
       value_type=TunableMapping(description="\n                The data associated with the subject's age.\n\n                Contains a map of the target's age to a multiplier.\n                ",
       key_name='target_age',
       key_type=TunableEnumEntry(description="\n                    The target's age.\n                    ",
       tunable_type=Age,
       default=(Age.ADULT)),
       value_name='multiplier',
       value_type=Tunable(description="\n                    The tuned value when this is the target's age.\n                    ",
       tunable_type=float,
       default=1)))}

    def get_value(self, subject_age, target_age):
        target_mapping = self.cross_age_tuning.get(subject_age, None)
        if target_mapping is None:
            return self.default_value
        target_value = target_mapping.get(target_age, self.default_value)
        return target_value


_, CrossAgeTuningSnippet = define_snippet('cross_age_tuning', CrossAgeTuning.TunableFactory())