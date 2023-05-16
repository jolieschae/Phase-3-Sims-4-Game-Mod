# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\narrative\narrative_service.py
# Compiled at: 2021-05-26 20:49:21
# Size of source mod 2**32: 27967 bytes
from collections import defaultdict
from _weakrefset import WeakSet
from conditional_layers.conditional_layer_enums import ConditionalLayerRequestSpeedType
from protocolbuffers import GameplaySaveData_pb2
import time
from date_and_time import TimeSpan, create_time_span
from distributor.rollback import ProtocolBufferRollback
from distributor.system import Distributor
from elements import GeneratorElement, SleepElement
from event_testing.resolver import GlobalResolver, SingleSimResolver
from event_testing.test_events import TestEvent
from narrative.narrative_enums import NarrativeEvent
from objects.components.types import NARRATIVE_AWARE_COMPONENT
from seasons.season_ops import SeasonParameterUpdateOp
from sims4.resources import Types
from sims4.service_manager import Service
from sims4.tuning.tunable import TunableSet, TunableReference, TunableRealSecond, TunableRange, TunableSimMinute
from sims4.utils import classproperty
import persistence_error_types, services, sims4.telemetry, telemetry_helper
TELEMETRY_GROUP_NARRATIVE = 'NRTV'
TELEMETRY_HOOK_NARRATIVE_START = 'NSTA'
TELEMETRY_HOOK_NARRATIVE_END = 'NEND'
TELEMETRY_FIELD_NARRATIVE = 'nrtv'
TELEMETRY_FIELD_SIMTIME = 'ntim'
TELEMETRY_FIELD_FIRST_TIME = 'ftim'
narrative_telemetry_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_NARRATIVE)

class NarrativeService(Service):
    INITIAL_NARRATIVES = TunableSet(description='\n        The initial set of narratives to set for a player. These narratives\n        will be set for a player if they are neither set nor already completed.\n        ',
      tunable=TunableReference(description='\n            A narrative reference.\n            ',
      manager=(services.get_instance_manager(Types.NARRATIVE)),
      pack_safe=True))
    TIME_SLICE_SECONDS = TunableRealSecond(description='\n        The maximum alloted time for sending narrative loots to all sim infos.\n        ',
      default=0.1)
    LAYER_OBJECTS_TO_LOAD = TunableRange(description='\n        The number of objects to load at a time when loading a layer.\n        Please consult a GPE before changing this value as it will impact\n        performance.\n        ',
      tunable_type=int,
      default=1,
      minimum=1)
    LAYER_OBJECTS_TO_DESTROY = TunableRange(description='\n        The number of objects to destroy at a time when destroying a layer.\n        Please consult a GPE before changing this value as it will impact\n        performance.\n        ',
      tunable_type=int,
      default=1,
      minimum=1)
    LAYER_OBJECTS_ALARM_TIME = TunableSimMinute(description='\n        The frequency that we will create or destroy objects in the layer.\n        Please consult a GPE before changing this value as it will impact\n        performance.\n        ',
      default=5,
      minimum=1)

    def __init__(self, *_, **__):
        self._active_narratives = {}
        self._locked_narratives = set()
        self._completed_narratives = set()
        self._env_settings = {}
        self._narrative_aware_object_handler = None
        self._pending_narrative_loots = []
        self._street_layers = defaultdict(list)
        self._streets_for_cleanup = None

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_NARRATIVE_SERVICE

    def setup(self, save_slot_data=None, **__):
        narrative_proto = save_slot_data.gameplay_data.narrative_service
        narrative_tuning_manager = services.get_instance_manager(Types.NARRATIVE)
        for narrative_id in narrative_proto.active_narratives:
            narrative = narrative_tuning_manager.get(narrative_id)
            if narrative is None:
                continue
            self._active_narratives[narrative] = narrative()

        for narrative_data in narrative_proto.narratives:
            narrative = narrative_tuning_manager.get(narrative_data.narrative_id)
            if narrative is None:
                continue
            narrative_instance = narrative()
            narrative_instance.load(narrative_data)
            self._active_narratives[narrative] = narrative_instance

        for narrative_id in narrative_proto.completed_narratives:
            narrative = narrative_tuning_manager.get(narrative_id)
            if narrative is None:
                continue
            self._completed_narratives.add(narrative)

        street_manager = services.get_instance_manager(Types.STREET)
        if narrative_proto.streets_need_cleanup:
            self._streets_for_cleanup = set()
            for narrative in narrative_tuning_manager.types.values():
                for street in narrative.narrative_layers.keys():
                    self._streets_for_cleanup.add(street)

        else:
            for street_id in narrative_proto.streets_to_cleanup:
                street = street_manager.get(street_id)
                if street is None:
                    continue
                if self._streets_for_cleanup is None:
                    self._streets_for_cleanup = set()
                self._streets_for_cleanup.add(street)

        layer_manager = services.get_instance_manager(Types.CONDITIONAL_LAYER)
        for layer_data in narrative_proto.layer_data:
            street = street_manager.get(layer_data.street_id)
            if street is None:
                continue
            for layer_id in layer_data.layers:
                layer = layer_manager.get(layer_id)
                if layer is None:
                    continue
                self._street_layers[street].append(layer)

    def save(self, save_slot_data=None, **__):
        narrative_proto = GameplaySaveData_pb2.PersistableNarrativeService()
        for narrative_instance in self._active_narratives.values():
            with ProtocolBufferRollback(narrative_proto.narratives) as (msg):
                narrative_instance.save(msg)

        for narrative in self._completed_narratives:
            narrative_proto.completed_narratives.append(narrative.guid64)

        for street, layers in self._street_layers.items():
            if street is None:
                continue
            with ProtocolBufferRollback(narrative_proto.layer_data) as (layer_msg):
                layer_msg.street_id = street.guid64
                for layer in layers:
                    layer_msg.layers.append(layer.guid64)

        narrative_proto.streets_need_cleanup = False
        if self._streets_for_cleanup is not None:
            for street in self._streets_for_cleanup:
                narrative_proto.streets_to_cleanup.append(street.guid64)

        save_slot_data.gameplay_data.narrative_service = narrative_proto

    def on_zone_load(self):
        startup_narratives = set(self.INITIAL_NARRATIVES)
        startup_narratives -= self._active_narratives.keys() | self._completed_narratives
        for narrative_to_start in startup_narratives:
            self._active_narratives[narrative_to_start] = narrative_to_start()
            self._send_narrative_start_telemetry(narrative_to_start)

        self._handle_narrative_updates(custom_keys=startup_narratives, immediate=True)
        for narrative_instance in self._active_narratives.values():
            narrative_instance.on_zone_load()

        active_street = services.current_street()
        layers_to_load = []
        layers_to_remove = []
        if self._streets_for_cleanup:
            narrative_tuning_manager = services.get_instance_manager(Types.NARRATIVE)
            for narrative in narrative_tuning_manager.types.values():
                if active_street in narrative.narrative_layers:
                    layers_to_remove.extend(narrative.narrative_layers[active_street])

            if active_street in self._streets_for_cleanup:
                self._streets_for_cleanup.remove(active_street)
        elif active_street in self._street_layers:
            layers_to_remove.extend(self._street_layers[active_street])
        for narrative in self._active_narratives.keys():
            new_layers = narrative.narrative_layers.get(active_street)
            if new_layers is None:
                continue
            for layer in new_layers:
                layers_to_load.append(layer)
                if layer in layers_to_remove:
                    layers_to_remove.remove(layer)

        conditional_layer_service = services.conditional_layer_service()
        for layer in layers_to_remove:
            conditional_layer_service.destroy_conditional_layer(layer)

        for layer in layers_to_load:
            conditional_layer_service.load_conditional_layer(layer)

        self._street_layers[active_street] = layers_to_load

    def should_suppress_travel_sting(self):
        return any((n.should_suppress_travel_sting for n in self._active_narratives.values()))

    def on_zone_unload(self):
        self._env_settings.clear()

    @property
    def active_narratives(self):
        return tuple(self._active_narratives)

    def get_active_narrative_instances(self):
        return self._active_narratives.items()

    @property
    def locked_narratives(self):
        narrative_tuning_manager = services.get_instance_manager(Types.NARRATIVE)
        return tuple((narrative_tuning_manager.get(narrative_id) for narrative_id in self._locked_narratives))

    @property
    def completed_narratives(self):
        return tuple(self._completed_narratives)

    def handle_narrative_event_progression(self, event, amount):
        narratives_to_end = set()
        narratives_to_start = set()
        for narrative_cls, narrative_inst in self._active_narratives.items():
            if narrative_cls.guid64 in self._locked_narratives:
                continue
            linked_narratives_to_start = narrative_inst.apply_progression_for_event(event, amount)
            if linked_narratives_to_start:
                narratives_to_start.update(linked_narratives_to_start)
                narratives_to_end.add(narrative_cls)

        for end_narrative in narratives_to_end:
            self.end_narrative(end_narrative, do_handle_updates=False)

        for start_narrative in narratives_to_start:
            self.start_narrative(start_narrative, do_handle_updates=False)

        process_event_custom_keys = narratives_to_end.union(narratives_to_start)
        self._handle_narrative_updates(custom_keys=process_event_custom_keys)

    def handle_narrative_event(self, event: NarrativeEvent):
        narratives_to_end = set()
        narratives_to_start = set()
        for narrative in self._active_narratives:
            if narrative.guid64 in self._locked_narratives:
                continue
            links = narrative.narrative_links
            if event in links:
                narratives_to_end.add(narrative)
                narratives_to_start.add(links[event])

        for end_narrative in narratives_to_end:
            self.end_narrative(end_narrative, do_handle_updates=False)

        for start_narrative in narratives_to_start:
            self.start_narrative(start_narrative, do_handle_updates=False)

        process_event_custom_keys = narratives_to_end.union(narratives_to_start)
        self._handle_narrative_updates(custom_keys=process_event_custom_keys)

    def start_narrative(self, narrative, do_handle_updates=True):
        if narrative in self._active_narratives or narrative.guid64 in self._locked_narratives:
            return
        for active_narrative in tuple(self._active_narratives):
            if active_narrative.narrative_groups & narrative.narrative_groups:
                self.end_narrative(active_narrative)

        narrative_instance = narrative()
        narrative_instance.start()
        self._active_narratives[narrative] = narrative_instance
        self._send_narrative_start_telemetry(narrative)
        if do_handle_updates:
            self._handle_narrative_updates(custom_keys=(narrative,))
        conditional_layer_service = services.conditional_layer_service()
        active_street = services.current_street()
        layers_to_load = narrative.narrative_layers.get(active_street)
        if layers_to_load is not None:
            for layer in layers_to_load:
                self._street_layers[active_street].append(layer)
                conditional_layer_service.load_conditional_layer(layer, speed=(ConditionalLayerRequestSpeedType.GRADUALLY),
                  timer_interval=(NarrativeService.LAYER_OBJECTS_ALARM_TIME),
                  timer_object_count=(NarrativeService.LAYER_OBJECTS_TO_LOAD))

    def lock_narrative(self, narrative):
        self._locked_narratives.add(narrative.guid64)

    def unlock_narrative(self, narrative):
        self._locked_narratives.remove(narrative.guid64)

    def is_narrative_locked(self, narrative):
        return narrative.guid64 in self._locked_narratives

    def _handle_narrative_updates(self, custom_keys=(), immediate=False):
        services.get_event_manager().process_event((TestEvent.NarrativesUpdated), custom_keys=custom_keys)
        self._schedule_narrative_aware_object_updates()
        self._setup_environment_settings(immediate=immediate)

    def _setup_environment_settings(self, immediate=False):
        start_time = services.time_service().sim_now
        weather_service = services.weather_service()
        if weather_service is None or services.season_service() is None:
            _forecast_override_fn = lambda _: None
        else:
            resolver = SingleSimResolver(services.active_sim_info())

            def _forecast_override_fn(forecast_override_op):
                forecast = forecast_override_op.weather_forecast
                weather_service.cross_season_override = forecast is not None
                if forecast is weather_service.get_override_forecast():
                    return
                forecast_override_op.apply_to_resolver(resolver)

        for narrative in self._active_narratives:
            override = narrative.environment_override
            if not override is None:
                if not override.should_apply():
                    continue
                _forecast_override_fn(override.weather_forecast_override)
                for param, setting in override.narrative_environment_params.items():
                    current_val = self._env_settings.get(param, 0)
                    setting_val = setting.value
                    if current_val == setting_val:
                        continue
                    elif immediate:
                        end_time = start_time
                        start_val = end_val = setting_val
                    else:
                        start_val = current_val
                        end_val = setting_val
                        end_time = start_time + create_time_span(minutes=(setting.interpolation_time))
                    op = SeasonParameterUpdateOp(param, start_val, start_time, end_val, end_time)
                    Distributor.instance().add_op_with_no_owner(op)
                    self._env_settings[param] = setting_val

    def end_narrative(self, narrative, do_handle_updates=True):
        if narrative not in self._active_narratives:
            if narrative.guid64 not in self._locked_narratives:
                return
        else:
            self._send_narrative_end_telemetry(narrative)
            del self._active_narratives[narrative]
            self._completed_narratives.add(narrative)
            if do_handle_updates:
                self._handle_narrative_updates(custom_keys=(narrative,))
            conditional_layer_service = services.conditional_layer_service()
            active_street = services.current_street()
            layers_to_remove = narrative.narrative_layers.get(active_street)
            if layers_to_remove is not None:
                for layer in layers_to_remove:
                    self._street_layers[active_street].remove(layer)
                    conditional_layer_service.destroy_conditional_layer(layer, speed=(ConditionalLayerRequestSpeedType.GRADUALLY),
                      timer_interval=(NarrativeService.LAYER_OBJECTS_ALARM_TIME),
                      timer_object_count=(NarrativeService.LAYER_OBJECTS_TO_DESTROY))

                if not self._street_layers[active_street]:
                    del self._street_layers[active_street]

    def reset_completion(self, narrative):
        self._completed_narratives.remove(narrative)

    def get_possible_replacement_situation(self, situation_type):
        resolver = GlobalResolver()
        for narrative in self._active_narratives:
            replacement_map = narrative.situation_replacements
            if situation_type not in replacement_map:
                continue
            replacement_data = replacement_map[situation_type]
            if replacement_data.replacement_tests.run_tests(resolver):
                return replacement_data.replacement

        return situation_type

    def _send_narrative_start_telemetry(self, narrative):
        with telemetry_helper.begin_hook(narrative_telemetry_writer, TELEMETRY_HOOK_NARRATIVE_START) as (hook):
            hook.write_guid(TELEMETRY_FIELD_NARRATIVE, narrative.guid64)
            hook.write_int(TELEMETRY_FIELD_SIMTIME, services.time_service().sim_now.absolute_minutes())
            hook.write_int(TELEMETRY_FIELD_FIRST_TIME, narrative not in self._completed_narratives)

    def _send_narrative_end_telemetry(self, narrative):
        with telemetry_helper.begin_hook(narrative_telemetry_writer, TELEMETRY_HOOK_NARRATIVE_END) as (hook):
            hook.write_guid(TELEMETRY_FIELD_NARRATIVE, narrative.guid64)
            hook.write_int(TELEMETRY_FIELD_SIMTIME, services.time_service().sim_now.absolute_minutes())
            hook.write_int(TELEMETRY_FIELD_FIRST_TIME, narrative not in self._completed_narratives)

    def _schedule_narrative_aware_object_updates(self):
        if self._narrative_aware_object_handler is not None:
            self._narrative_aware_object_handler.trigger_hard_stop()
        timeline = services.time_service().sim_timeline
        if timeline is None:
            return
        self._narrative_aware_object_handler = timeline.schedule(GeneratorElement(self._update_narrative_aware_objects_gen))

    def _update_narrative_aware_objects_gen(self, timeline):
        narratives = self.active_narratives
        for narrative_aware_objects in WeakSet(services.object_manager().get_all_objects_with_component_gen(NARRATIVE_AWARE_COMPONENT)):
            yield timeline.run_child(SleepElement(TimeSpan.ZERO))
            narrative_aware_objects.narrative_aware_component.on_narratives_set(narratives)

    def get_lock_save_reason(self):
        if self._pending_narrative_loots:
            return self._pending_narrative_loots[0][1]

    def add_sliced_sim_info_loots(self, loots, save_lock_tooltip):
        lock_needed = not self._pending_narrative_loots
        self._pending_narrative_loots.append((loots, save_lock_tooltip, list(services.sim_info_manager().instantiatable_sims_info_gen())))
        if lock_needed:
            services.get_persistence_service().lock_save(self)

    def update(self):
        if self._pending_narrative_loots:
            persistence_service = services.get_persistence_service()
            loots, _, sim_infos = self._pending_narrative_loots[0]
            sim_info_manager = services.sim_info_manager()
            start_time = time.monotonic()
            while time.monotonic() - start_time < self.TIME_SLICE_SECONDS:
                if not sim_infos:
                    persistence_service.unlock_save(self)
                    self._pending_narrative_loots.pop()
                    if not self._pending_narrative_loots:
                        return
                    loots, _, sim_infos = self._pending_narrative_loots[0]
                    persistence_service.lock_save(self)
                sim_info = sim_infos.pop()
                if sim_info.sim_id in sim_info_manager and sim_info.can_instantiate_sim:
                    resolver = SingleSimResolver(sim_info)
                    for loot_action in loots:
                        loot_action.apply_to_resolver(resolver)