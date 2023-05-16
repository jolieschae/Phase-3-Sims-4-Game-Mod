# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\gardening\gardening_component_crop_plant_element.py
# Compiled at: 2021-03-15 19:27:44
# Size of source mod 2**32: 2779 bytes
from interactions import ParticipantTypeObject
from interactions.utils.interaction_elements import XevtTriggeredElement
from objects.components import types
from sims.funds import FundsSource
from singletons import DEFAULT
import sims4.log
from sims4.tuning.tunable import TunableEnumEntry, Tunable
logger = sims4.log.Logger('Gardening', default_owner='miking')

class HarvestCropsElement(XevtTriggeredElement):
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            Plant object to harvest from.\n            ',
       tunable_type=ParticipantTypeObject,
       default=ParticipantTypeObject.Object), 
     'sell_immediately':Tunable(description='\n            If checked, the harvested crop(s) will be immediately sold for profit rather than moved into inventory.\n            ',
       tunable_type=bool,
       default=False)}

    def _do_behavior(self, *args, **kwargs):
        sim = self.interaction.sim
        if sim is None:
            logger.error('HarvestCrops: No interaction sim for {}', self)
            return
        participant = self.interaction.get_participant(self.participant)
        if participant is None:
            logger.error('HarvestCrops: Participant {} is None for {}', self.participant, self)
            return
        gardening_component = participant.get_component(types.GARDENING_COMPONENT)
        if gardening_component is None:
            logger.error('HarvestCrops: Participant {} does not have a gardening component.', participant)
            return
        if not gardening_component.supports_harvest:
            logger.error('HarvestCrops: Gardening component is not a GardeningCropPlantComponent.')
            return
        gardening_component.on_harvest(sim, self.sell_immediately)

    @classmethod
    def on_affordance_loaded_callback(cls, affordance, harvest_element, object_tuning_id=DEFAULT):

        def get_simoleon_delta(interaction, target=DEFAULT, context=DEFAULT, **interaction_parameters):
            if target is not DEFAULT:
                gardening_component = target.get_component(types.GARDENING_COMPONENT)
                if gardening_component.supports_harvest:
                    return gardening_component.get_simoleon_delta()
            return (
             0, FundsSource.HOUSEHOLD)

        if harvest_element.sell_immediately:
            affordance.register_simoleon_delta_callback(get_simoleon_delta, object_tuning_id=object_tuning_id)