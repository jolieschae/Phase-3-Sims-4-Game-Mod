# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\tunable_utils\create_object.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 4148 bytes
from crafting.crafting_tunable import CraftingTuning
from objects.components.state import CommodityBasedObjectStateValue
from objects.components.state_references import TunableStateValueReference
from objects.system import create_object
from sims4.random import weighted_random_item
from sims4.tuning.tunable import TunableReference, TunableTuple, TunableList, TunableRange, AutoFactoryInit, HasTunableSingletonFactory, TunableFactory
import crafting, services, sims4
logger = sims4.log.Logger('CreateObject')

class ObjectCreator(HasTunableSingletonFactory, AutoFactoryInit):

    @TunableFactory.factory_option
    def get_definition(pack_safe):
        return {'definition': TunableReference(description='\n                The definition of the object to be created.\n                ',
                         manager=(services.definition_manager()),
                         pack_safe=pack_safe)}

    FACTORY_TUNABLES = {'definition': TunableReference(description='\n            The definition of the object to be created.\n            ',
                     manager=(services.definition_manager()))}

    def __call__(self, **kwargs):
        return create_object((self.definition), **kwargs)

    def get_object_definition(self):
        return self.definition

    def get_footprint(self):
        return self.definition.get_footprint()

    @property
    def id(self):
        return self.definition.id


def _verify_tunable_quality_value_callback(instance_class, tunable_name, source, quality, weight):
    if quality not in CraftingTuning.QUALITY_STATE.values:
        logger.error('A TunableRecipeCreator {} specifies an invalid quality {}.', source, quality)


class RecipeCreator(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'recipe':TunableReference(description='\n            Recipe to produce an object with.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.RECIPE)), 
     'weighted_quality':TunableList(description='\n            A list of weighted quality in which the object will be created.\n            \n            If empty, it will apply a default quality.\n            ',
       tunable=TunableTuple(description='\n                A possible level of quality for this item that will be generated.\n                This will be randomly chosen based off weight against other items in the list.\n                ',
       weight=TunableRange(tunable_type=int,
       default=1,
       minimum=1),
       quality=TunableStateValueReference(class_restrictions=CommodityBasedObjectStateValue),
       verify_tunable_callback=_verify_tunable_quality_value_callback))}

    def __call__(self, crafter_sim=None, post_add=None, **kwargs):
        choices = [(quality.weight, quality.quality) for quality in self.weighted_quality]
        quality = weighted_random_item(choices) if choices else None
        return crafting.crafting_interactions.create_craftable((self.recipe), crafter_sim, quality=quality, post_add=post_add)

    def get_object_definition(self):
        return self.recipe.final_product.definition