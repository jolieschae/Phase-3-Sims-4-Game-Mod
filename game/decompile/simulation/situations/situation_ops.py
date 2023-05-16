# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_ops.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 2185 bytes
import objects, services, sims4.resources
from drama_scheduler.drama_node_types import DramaNodeType
from interactions import ParticipantType
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import TunableReference

class SetSituationSpecialObjectLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'situation': TunableReference(description='\n            The Situation to which the target object is added. If the subject Sim is not in this situation,\n            nothing will happen.\n            ',
                    manager=(services.get_instance_manager(sims4.resources.Types.SITUATION)))}

    def __init__(self, situation, **kwargs):
        (super().__init__)(target_participant_type=ParticipantType.Object, **kwargs)
        self._situation = situation

    def _apply_to_subject_and_target(self, subject, target, resolver):
        drama_scheduler = services.drama_scheduler_service()
        for drama_node in drama_scheduler.get_scheduled_nodes_by_drama_node_type(DramaNodeType.PLAYER_PLANNED):
            situation_seed = drama_node.get_situation_seed()
            if situation_seed.situation_type.guid64 == self._situation.guid64:
                if situation_seed.host_sim_id == subject.id:
                    situation_seed.special_object_definition_id = target.definition.id
                    crafting_component = target.get_component(objects.components.types.CRAFTING_COMPONENT)
                    if crafting_component is not None:
                        recipe_name = crafting_component.get_recipe().get_recipe_name()
                        situation_seed.special_object_name = recipe_name
                return