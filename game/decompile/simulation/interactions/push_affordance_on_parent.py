# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\push_affordance_on_parent.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 2032 bytes
import random
from interactions.context import InteractionContext
from interactions.priority import Priority
from interactions.utils.interaction_elements import XevtTriggeredElement
from sims4.tuning.tunable import TunableReference
import services, sims4.resources

class PushAffordanceOnRandomParent(XevtTriggeredElement):
    FACTORY_TUNABLES = {'affordance_to_push': TunableReference(description='\n            The affordance to push on a random parent of the Actor.\n            ',
                             manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
                             class_restrictions='SuperInteraction',
                             pack_safe=True)}

    def _do_behavior(self, *args, **kwargs):
        child_sim = self.interaction.sim
        child_sim_info = child_sim.sim_info
        household = child_sim_info.household
        parents = set()
        for sim_info in household:
            if not sim_info is child_sim_info:
                if not (sim_info.is_teen_or_younger or sim_info.is_instanced()):
                    continue
                parents.add(sim_info)

        for parent_sim_info in child_sim_info.genealogy.get_parent_sim_infos_gen():
            if parent_sim_info.is_instanced():
                parents.add(parent_sim_info)

        if not parents:
            return
        random_parent = random.choice(list(parents)).get_sim_instance()
        context = InteractionContext(random_parent, InteractionContext.SOURCE_SCRIPT, Priority.High)
        random_parent.push_super_affordance(self.affordance_to_push, child_sim, context)