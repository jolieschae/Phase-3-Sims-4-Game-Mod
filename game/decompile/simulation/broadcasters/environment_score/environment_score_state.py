# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\broadcasters\environment_score\environment_score_state.py
# Compiled at: 2016-02-01 23:54:11
# Size of source mod 2**32: 3324 bytes
from objects.components.needs_state_value import NeedsStateValue
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableMapping, TunableReference
from statistics.mood import TunableEnvironmentScoreModifiers
import objects, services, sims4

class EnvironmentScoreState(HasTunableFactory, AutoFactoryInit, NeedsStateValue):
    FACTORY_TUNABLES = {'base_modifiers':TunableEnvironmentScoreModifiers.TunableFactory(description="\n            Modifiers for this object's Environment Score based on it's Client State.\n            \n            Example: Broken objects should emit a negative environment score and should\n            have an added negative modifier.\n            \n            Example: Blooming Flowers should emit a positive emotion when they are blooming\n            "), 
     'trait_modifiers':TunableMapping(description='\n                Each trait can put modifiers on any number of moods as well as the negative environment scoring.\n                \n                Example: Neat trait could set the negative score multiplier\n                to 2 for spoiled/dirty/broken objects.\n                \n                Example: For a dirty object, a Sim with the Slob trait\n                could set the negative score multiplier to 0, and even set\n                the happy mood to +2.\n                ',
       key_type=TunableReference(description='\n                    The Trait that the Sim must have to enable these modifiers.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
       pack_safe=True),
       value_type=TunableEnvironmentScoreModifiers.TunableFactory(description='\n                    The Environmental Score modifiers for a particular trait.\n                    '),
       key_name='trait',
       value_name='modifiers')}

    def __init__(self, target, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.target = target

    def start(self, *_, **__):
        if self.target.environmentscore_component is None:
            self.target.add_dynamic_component(objects.components.types.ENVIRONMENT_SCORE_COMPONENT)
        if self.target.environmentscore_component is not None:
            self.target.environmentscore_component.add_state_environment_score(self)

    def stop(self, *_, **__):
        env_score_component = self.target.environmentscore_component
        if env_score_component is not None:
            env_score_component.remove_state_environment_score(self)