# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\crafting_loots.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 3453 bytes
import random, services, sims4
from crafting.crafting_process import CraftingProcess
from interactions import ParticipantType
from interactions.utils.loot_basic_op import BaseLootOperation
from objects.components import types
from sims4.tuning.tunable import Tunable, TunableReference, TunableEnumEntry, OptionalTunable

class RefundCraftingProcessLoot(BaseLootOperation):

    def _apply_to_subject_and_target(self, subject, target, resolver):
        subject = resolver.get_participant(self.subject)
        if subject is None:
            return
        crafting_component = subject.get_component(types.CRAFTING_COMPONENT)
        if crafting_component is None:
            return
        crafting_process = crafting_component.get_crafting_process()
        if crafting_process is None:
            return
        crafting_process.refund_payment(explicit=True)


class SetupCraftedObjectLoot(BaseLootOperation):
    FACTORY_TUNABLES = {'recipe':TunableReference(description='\n            Recipe to apply onto the object.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.RECIPE)), 
     'show_crafted_by_text':Tunable(description='\n            Whether to show crafted by text on the tooltip of the crafted object. \n            ',
       tunable_type=bool,
       default=True), 
     'change_crafter':OptionalTunable(description='\n            Specify what participant the crafter should be set to. \n            ',
       tunable=TunableEnumEntry(description='\n                The new participant crafter. \n                ',
       tunable_type=ParticipantType,
       default=(ParticipantType.Actor)))}

    def __init__(self, *args, recipe, show_crafted_by_text, change_crafter, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._recipe = recipe
        self._show_crafted_by_text = show_crafted_by_text
        self.change_crafter = change_crafter

    def _apply_to_subject_and_target(self, subject, target, resolver):
        subject = resolver.get_participant(self.subject)
        if subject is None:
            return
        crafting_component = subject.get_component(types.CRAFTING_COMPONENT)
        if crafting_component is not None:
            return
        crafting_process = CraftingProcess(recipe=(self._recipe))
        if self.change_crafter:
            crafter_sim = resolver.get_participant(self.change_crafter)
            if crafter_sim is not None:
                crafter_sim = crafter_sim.get_sim_instance()
                if crafter_sim is not None:
                    crafting_process.change_crafter(crafter_sim)
        if not self._show_crafted_by_text:
            crafting_process.remove_crafted_by_text()
        crafting_process.setup_crafted_object(subject, is_final_product=True, random=(random.Random()))