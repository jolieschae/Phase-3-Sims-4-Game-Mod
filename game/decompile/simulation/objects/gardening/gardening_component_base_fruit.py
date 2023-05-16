# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\gardening\gardening_component_base_fruit.py
# Compiled at: 2021-06-02 16:54:41
# Size of source mod 2**32: 3372 bytes
from protocolbuffers import SimObjectAttributes_pb2 as protocols
from event_testing.tests import TunableTestSet
from objects.components import componentmethod_with_fallback, types
from objects.gardening.gardening_component import _GardeningComponent
from objects.gardening.gardening_tuning import GardeningTuning
from objects.hovertip import TooltipFields
from sims4.localization import TunableLocalizedString
from sims4.tuning.tunable import TunableReference
import objects.components.types, services, sims4.log, sims4.math
logger = sims4.log.Logger('Gardening', default_owner='shipark')

class _GardeningBaseFruitComponent(_GardeningComponent, component_name=objects.components.types.GARDENING_COMPONENT, persistence_key=protocols.PersistenceMaster.PersistableData.GardeningComponent):
    FACTORY_TUNABLES = {'plant':TunableReference(description='\n            The plant that this fruit will grow into if planted or if it\n            spontaneously germinates.\n            ',
       manager=services.definition_manager()), 
     'fruit_name':TunableLocalizedString(description='\n            Fruit name that will be used on the spliced plant description.\n            ',
       allow_catalog_name=True), 
     'tests':TunableTestSet(description='\n            Conditional tests to determine if spawning occurs.\n            ')}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)

    def on_add(self, *args, **kwargs):
        return (super().on_add)(*args, **kwargs)

    def on_state_changed(self, state, old_value, new_value, from_init):
        self.update_hovertip()

    def on_added_to_inventory(self):
        for on_state_value, to_state_value in GardeningTuning.PICKUP_STATE_MAPPING.items():
            if self.owner.has_state(on_state_value):
                self.owner.set_state(to_state_value)

    @componentmethod_with_fallback((lambda: None))
    def get_notebook_information(self, reference_notebook_entry, notebook_sub_entries):
        notebook_entry = reference_notebook_entry(self.owner.definition.id)
        return (notebook_entry,)

    def _ui_metadata_gen(self):
        yield from super()._ui_metadata_gen()
        season_service = services.season_service()
        if season_service is not None:
            season_text = GardeningTuning.get_seasonality_text_from_plant(self.plant)
            if season_text:
                yield (
                 TooltipFields.season_text.name, season_text)