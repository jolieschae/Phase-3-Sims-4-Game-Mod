# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\loot_element.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 2318 bytes
import services, sims4
from interactions import ParticipantType
from interactions.utils.interaction_elements import XevtTriggeredElement
from interactions.utils.loot import LootActions, LootOperationList, RandomWeightedLoot
from sims4.tuning.tunable import TunableList, OptionalTunable, TunableReference
from tunable_utils.tunable_object_generator import TunableObjectGeneratorVariant

class LootElement(XevtTriggeredElement):
    FACTORY_TUNABLES = {'loot_list':TunableList(description='\n            A list of loot operations. This includes Loot Actions and Random Weighted Loots.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True)), 
     'object_override':OptionalTunable(description='\n            If disabled, this loot is executed once, and all participants tuned\n            in the various actions are retrieved from the owning interaction.\n            \n            If enabled, this loot is executed once for each of the generated\n            objects. The Object participant corresponds to this object. All\n            other participants (e.g. Actor) are retrieved from the owning\n            interaction.\n            ',
       tunable=TunableObjectGeneratorVariant(participant_default=(ParticipantType.ObjectChildren)))}

    def _do_behavior(self, *args, **kwargs):
        if self.object_override is None:
            resolver = self.interaction.get_resolver()
            loots = (LootOperationList(resolver, self.loot_list),)
        else:
            loots = []
            for obj in self.object_override.get_objects(self.interaction):
                resolver = self.interaction.get_resolver(target=obj)
                loots.append(LootOperationList(resolver, self.loot_list))

        for loot in loots:
            loot.apply_operations()