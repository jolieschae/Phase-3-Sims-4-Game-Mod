# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\affordance_tuning.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 5692 bytes
from interactions.base.basic import TunableBasicContentSet, TunableBasicExtras
from interactions.utils.outcome import TunableOutcome, TunableOutcomeActions
from interactions.utils.tunable import TunableStatisticAdvertisements
from objects.components import Component, types, componentmethod_with_fallback
from sims4.tuning.tunable import TunableList, TunableReference, HasTunableFactory, TunableMapping, TunableTuple
from statistics.skill import TunableSkillLootData
import event_testing.tests, services, sims4.log
logger = sims4.log.Logger(types.AFFORDANCE_TUNING_COMPONENT.class_attr)

class AffordanceTuningComponent(Component, HasTunableFactory, component_name=types.AFFORDANCE_TUNING_COMPONENT):
    FACTORY_TUNABLES = {'affordance_map': TunableMapping(key_type=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
                         pack_safe=True,
                         description='Affordance with additional tuning.'),
                         value_type=TunableTuple(tests=event_testing.tests.TunableTestSetWithTooltip(description='\n                    Additive: These test will be used in addition to any tests\n                    tuned on the affordance.\n                    '),
                         skill_loot_data=TunableSkillLootData(description='\n                    Override: This will be used instead of any skill loot data\n                    tuned on the affordance.\n                    '),
                         false_ads=TunableStatisticAdvertisements(description='\n                    Additive: These will be used in addition to any false\n                    advertisements tuned on the affordance.\n                    '),
                         outcome=TunableOutcome(description='\n                    Additive: This will be used in addition to Outcome tuned\n                    on the affordance.\n                    ',
                         outcome_locked_args={'cancel_si': None, 
                        TunableOutcomeActions.ADD_TARGET_AFFORDANCE_LOOT_KEY: False},
                         animation_callback=None),
                         basic_content=TunableBasicContentSet(description='\n                    Additive: This will be used in addition to any Basic\n                    Content tuned on the affordance.\n                    ',
                         animation_callback=None,
                         one_shot=True,
                         flexible_length=True,
                         no_content=True,
                         default='no_content'),
                         basic_extras=TunableBasicExtras(description='\n                    Additive: This will be used in addition to any Basic\n                    Extras tuned on the affordance.\n                    '),
                         loot_list=TunableList(TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
                         class_restrictions='LootActions'),
                         description='\n                        Additive: This will be used in addition to any Loot\n                        Lists tuned on the affordance.\n                        ')),
                         description='\n                Affordance->Additional Tuning map.  Look at individual fields\n                to see if the tuning is an override or additive.\n                ')}

    def __init__(self, owner, affordance_map=None):
        super().__init__(owner)
        self._affordance_map = affordance_map

    def _create_tuning_accessor(name, fallback):

        @componentmethod_with_fallback(fallback)
        def tuning_accessor(self, interaction):
            tuning = self._affordance_map.get(interaction.get_interaction_type())
            if tuning is None:
                return fallback(interaction)
            return getattr(tuning, name)

        tuning_accessor.__name__ = 'get_affordance_' + name
        return tuning_accessor

    get_affordance_tests = _create_tuning_accessor('tests', (lambda interaction: None))
    get_affordance_loot_list = _create_tuning_accessor('loot_list', (lambda interaction: []))
    get_affordance_skill_loot_data = _create_tuning_accessor('skill_loot_data', (lambda interaction: None))
    get_affordance_false_ads = _create_tuning_accessor('false_ads', (lambda interaction: ()))
    get_affordance_outcome = _create_tuning_accessor('outcome', (lambda interaction: None))
    get_affordance_basic_content = _create_tuning_accessor('basic_content', (lambda interaction: None))
    get_affordance_basic_extras = _create_tuning_accessor('basic_extras', (lambda interaction: ()))
    del _create_tuning_accessor