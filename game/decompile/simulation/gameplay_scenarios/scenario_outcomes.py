# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gameplay_scenarios\scenario_outcomes.py
# Compiled at: 2022-08-26 18:13:12
# Size of source mod 2**32: 8117 bytes
from filters.tunable import TunableSimFilter
from gameplay_scenarios.scenario_tests_set import ScenarioTestSet
from interactions import ParticipantType
from interactions.utils.loot import LootActions
from sims4.localization import TunableLocalizedString
from sims4.tuning.instances import TunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableList, TunableTuple, Tunable, HasTunableReference, TunableReference, TunableVariant, TunableResourceKey
import services, sims4
from sims4.tuning.tunable_base import GroupNames, ExportModes

class ScenarioPhaseLoot(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'loots': TunableList(description='\n            A list of loots to apply as a scenario outcome.\n            ',
                tunable=TunableTuple(description='\n                ',
                scenario_loot=TunableTuple(description='\n                    A loot action and a list of targets.\n                    ',
                loot_action=LootActions.TunableReference(description='\n                        An action that will be applied to everyone in the list of targets.\n                        ',
                pack_safe=True),
                actor_role=TunableReference(description='\n                        The role of main targets for the loot.\n                        Loot will be applied to every sim in the scenario with the specified role using that sim as the \n                        actor participant in the loot.\n                        E.g. loot that is applied to "Actor" will be applied to the every sim in the specified role\n                        E.g. loot that is applied to "SignificantOtherActor" will be applied to the significant others \n                        of every sim in the specified role.\n                        Leave this empty if loot subject(s) are globally available participants that aren\'t related to \n                        sims in a role.  E.g. "ActiveHousehold", "AllInstancedSims".\n                        ',
                manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
                class_restrictions=('ScenarioRole', ),
                allow_none=True),
                secondary_actor_role=TunableReference(description='\n                        The role of secondary targets for the loot.\n                        Fill secondary target only for loots requiring pair of sims. Like relationship loots.\n                        Loot will be applied between every pair of sims in the scenario with (actor_role, secondary_actor_role)\n                        ',
                manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
                class_restrictions=('ScenarioRole', ),
                allow_none=True),
                actor_sim_filter=TunableReference(description='\n                        An alternative way(to actor_role) to access sim_info for the loots requiring "Actor". \n                        This will not create a new sim like in situations. \n                        It is just a reference for the sim filter in the scenario_npc_sims.\n                        ',
                manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER)),
                class_restrictions=TunableSimFilter,
                tuning_group=(GroupNames.SIM_FILTER),
                allow_none=True),
                secondary_actor_sim_filter=TunableReference(description='\n                        An alternative way(to secondary_actor_role) to access sim_info for the loots requiring "Actor". \n                        This will not create a new sim like in situations. \n                        It is just a reference for the sim filter in the scenario_npc_sims.\n                        ',
                manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER)),
                class_restrictions=TunableSimFilter,
                tuning_group=(GroupNames.SIM_FILTER),
                allow_none=True))))}


class ScenarioOutcome(HasTunableReference, metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SNIPPET)):
    INSTANCE_TUNABLES = {'visible':Tunable(description='\n            If checked, the outcome text will be visible in the UI, such as in the scenario cards.\n            ',
       tunable_type=bool,
       default=True,
       tuning_group=GroupNames.UI,
       export_modes=ExportModes.ClientBinary), 
     'scenario_outcome_loot':ScenarioPhaseLoot.TunableFactory(description='\n            Loot Actions for the outcome of the scenario.\n            '), 
     'outcome_title_text':TunableLocalizedString(description='\n            The text that will display as the player-facing for\n            outcome title.\n            ',
       allow_none=True,
       tuning_group=GroupNames.UI,
       export_modes=ExportModes.All), 
     'outcome_description_text':TunableLocalizedString(description='\n            The text that will display as the player-facing for\n            outcome description.\n            ',
       allow_none=True,
       tuning_group=GroupNames.UI,
       export_modes=ExportModes.All), 
     'outcome_next_steps_text':TunableLocalizedString(description='\n            The text that will display when this outcome is achieved to\n            let the player know how they can continue with the household\n            they played the scenario with.\n            ',
       allow_none=True,
       tuning_group=GroupNames.UI), 
     'outcome_icon':TunableResourceKey(description=",\n            The icon to show next to this outcome's description\n            in the outcome panel.\n            ",
       allow_none=True,
       resource_types=sims4.resources.CompoundTypes.IMAGE,
       tuning_group=GroupNames.UI), 
     'outcome_reward_icon':TunableResourceKey(description=',\n            The icon to show under the reward section of the scenario\n            outcome panel.\n            ',
       allow_none=True,
       resource_types=sims4.resources.CompoundTypes.IMAGE,
       tuning_group=GroupNames.UI), 
     'outcome_reward_icon_tooltip':TunableLocalizedString(description='\n            Tooltip text for the reward icon.\n            ',
       allow_none=True,
       tuning_group=GroupNames.UI), 
     'outcome_bonus_reward_icon':TunableResourceKey(description=',\n            If enabled, the icon to show under the bonus reward section\n            of the scenario outcome panel.\n            ',
       allow_none=True,
       resource_types=sims4.resources.CompoundTypes.IMAGE,
       tuning_group=GroupNames.UI,
       export_modes=ExportModes.ClientBinary), 
     'outcome_bonus_reward_icon_tooltip':TunableLocalizedString(description='\n            Tooltip text for the bonus reward icon.\n            ',
       allow_none=True,
       tuning_group=GroupNames.UI), 
     'tests':ScenarioTestSet.TunableFactory(description='\n            A set of tests that all of them should pass to reach this scenario outcome.\n            ',
       tuning_group=GroupNames.TESTS)}