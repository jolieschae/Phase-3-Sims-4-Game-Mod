# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\gardening\gardening_component_base_plant.py
# Compiled at: 2021-01-26 20:38:51
# Size of source mod 2**32: 4377 bytes
from protocolbuffers import SimObjectAttributes_pb2 as protocols
from protocolbuffers import UI_pb2 as ui_protocols
from objects.components import types
from objects.gardening.gardening_component import _GardeningComponent
from objects.gardening.gardening_tuning import GardeningTuning
from objects.hovertip import TooltipFields
from sims4.localization import LocalizationHelperTuning
import objects.components.types, services, sims4.log
logger = sims4.log.Logger('Gardening', default_owner='shipark')

class _GardeningBasePlantComponent(_GardeningComponent, component_name=objects.components.types.GARDENING_COMPONENT, persistence_key=protocols.PersistenceMaster.PersistableData.GardeningComponent):

    def on_add(self, *args, **kwargs):
        zone = services.current_zone()
        if not zone.is_zone_loading:
            gardening_service = services.get_gardening_service()
            gardening_service.add_gardening_object(self.owner)
        return (super().on_add)(*args, **kwargs)

    def on_remove(self, *_, **__):
        gardening_service = services.get_gardening_service()
        gardening_service.remove_gardening_object(self.owner)

    def on_finalize_load(self):
        gardening_service = services.get_gardening_service()
        gardening_service.add_gardening_object(self.owner)

    def on_location_changed(self, old_location):
        zone = services.current_zone()
        if not zone.is_zone_loading:
            gardening_service = services.get_gardening_service()
            gardening_service.move_gardening_object(self.owner)

    def on_state_changed(self, state, old_value, new_value, from_init):
        self.update_hovertip()

    def _ui_metadata_gen(self):
        if not self.show_gardening_tooltip():
            self.owner.hover_tip = ui_protocols.UiObjectMetadata.HOVER_TIP_DISABLED
            return
        if self.show_gardening_details():
            if self.owner.has_state(GardeningTuning.EVOLUTION_STATE):
                state_value = self.owner.get_state(GardeningTuning.EVOLUTION_STATE)
                evolution_value = state_value.range.upper_bound
                yield ('evolution_progress', evolution_value)
            else:
                if GardeningTuning.SEASONALITY_STATE is not None:
                    if self.owner.has_state(GardeningTuning.SEASONALITY_STATE):
                        sesonality_state_value = self.owner.get_state(GardeningTuning.SEASONALITY_STATE)
                        if sesonality_state_value is not None:
                            season_text = sesonality_state_value.display_name
                            seasonality_text = GardeningTuning.get_seasonality_text_from_plant(self.owner.definition)
                            if seasonality_text:
                                season_text = LocalizationHelperTuning.get_new_line_separated_strings(season_text, seasonality_text)
                            yield (
                             TooltipFields.season_text.name, season_text)
                if self.owner.has_state(GardeningTuning.QUALITY_STATE_VALUE):
                    quality_state_value = self.owner.get_state(GardeningTuning.QUALITY_STATE_VALUE)
                    if quality_state_value is not None:
                        quality_value = quality_state_value.value
                        yield ('quality', quality_value)
        yield from super()._ui_metadata_gen()