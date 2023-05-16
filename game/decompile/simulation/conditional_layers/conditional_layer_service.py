# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\conditional_layers\conditional_layer_service.py
# Compiled at: 2021-05-26 20:51:12
# Size of source mod 2**32: 37168 bytes
from _collections import defaultdict
from conditional_layers.conditional_layer_enums import ConditionalLayerRequestType, ConditionalLayerRequestSpeedType
from protocolbuffers import GameplaySaveData_pb2 as gameplay_serialization
from build_buy import mark_conditional_objects_loaded, load_conditional_objects, test_location_for_object, move_object_to_household_inventory, HouseholdInventoryFlags, set_client_conditional_layer_active, conditional_layer_destroyed
from conditional_layers.conditional_layer_handlers import is_archive_enabled, archive_layer_request_culling, LayerRequestAction
from crafting.crafting_tunable import CraftingTuning
from date_and_time import TimeSpan, create_time_span
from distributor.rollback import ProtocolBufferRollback
from event_testing.resolver import GlobalResolver
from interactions.interaction_finisher import FinishingType
from objects.client_object_mixin import ClientObjectMixin
from objects.components.types import SPAWNER_COMPONENT
from sims4.service_manager import Service
from sims4.tuning.tunable import TunableSimMinute, TunableRange
from sims4.utils import classproperty
from ui.ui_dialog_notification import TunableUiDialogNotificationSnippet
import alarms, objects.components.types, persistence_error_types, services, sims4.log
logger = sims4.log.Logger('ConditionalLayerService', default_owner='jjacobson')

class ConditionalLayerRequest:

    def __init__(self, conditional_layer, callback, speed, interval, object_count):
        self.conditional_layer = conditional_layer
        self.callback = callback
        self.speed = speed
        self.timer_interval = interval
        self.timer_object_count = object_count
        self.alarm_handle = None

    def __repr__(self):
        return '<{0}: Conditional Layer {1}: Layer Hash; Speed {2}>'.format(type(self).__name__, self.conditional_layer, self.conditional_layer.layer_name, self.speed)

    @classproperty
    def request_type(cls):
        raise NotImplementedError

    def execute_request(self):
        raise NotImplementedError

    def notify_requester(self):
        if is_archive_enabled():
            archive_layer_request_culling(self, LayerRequestAction.COMPLETED)
        if self.callback is not None:
            self.callback(self.conditional_layer)

    def cleanup_request(self):
        self.conditional_layer = None
        self.callback = None
        self.speed = None
        self.timer_interval = None
        self.timer_object_count = None
        if self.alarm_handle is not None:
            alarms.cancel_alarm(self.alarm_handle)
            self.alarm_handle = None


class LoadConditionalLayerRequest(ConditionalLayerRequest):
    OBJECT_MOVED_TO_HOUSEHOLD_INVENTORY_NOTIFICATION = TunableUiDialogNotificationSnippet(description='\n            The notification that we will display to inform the player that\n            objects were moved to their household inventory.\n            ')

    def __init__(self, *args, fade_in):
        (super().__init__)(*args)
        self.fade_in = fade_in

    @classproperty
    def request_type(cls):
        return ConditionalLayerRequestType.LOAD_LAYER

    def _set_up_loaded_objects(self, object_ids):
        should_show_blocking_object_notification = False
        object_manager = services.object_manager()
        conditional_layer_service = services.conditional_layer_service()
        layer_info = conditional_layer_service._get_layer_info(self.conditional_layer)
        for object_id in object_ids:
            if object_id in layer_info.objects_loaded:
                logger.error('Trying to setup object of id {} which was already setup.', object_id)
                continue
            obj = object_manager.get(object_id)
            if obj is None:
                logger.error('Error when trying to setup objects loaded by the layer.  Open street director was given object id {} of object not in the object manager.', object_id)
                continue
            result, errors, blocking_objects = test_location_for_object(obj=obj, return_blocking_object_ids=True)
            if blocking_objects:
                for blocking_obj_id in blocking_objects:
                    blocking_obj_id = blocking_obj_id[0]
                    blocking_obj = object_manager.get(blocking_obj_id)
                    if blocking_obj is None:
                        continue
                    household_id = blocking_obj.get_household_owner_id()
                    if household_id is None:
                        continue
                    active_household_id = services.active_household_id()
                    if blocking_obj.has_component(objects.components.types.CRAFTING_COMPONENT):
                        blocking_obj.destroy(source=self, cause='Destroying object with Crafting Component from conditional layer service.',
                          fade_duration=(ClientObjectMixin.FADE_DURATION))
                        continue
                    tracker = blocking_obj.get_tracker(CraftingTuning.SERVINGS_STATISTIC)
                    if tracker is not None:
                        if tracker.has_statistic(CraftingTuning.SERVINGS_STATISTIC):
                            blocking_obj.destroy(source=self, cause='Destroying object with servings statistic from conditional layer service.',
                              fade_duration=(ClientObjectMixin.FADE_DURATION))
                            continue
                    if household_id == active_household_id:
                        should_show_blocking_object_notification = True
                    move_object_to_household_inventory(blocking_obj)

            if self.fade_in:
                obj.opacity = 0
                obj.fade_in()
            if obj.has_component(SPAWNER_COMPONENT):
                obj.spawner_component.initialize_spawning()
            layer_info.objects_loaded.add(object_id)

        if should_show_blocking_object_notification:
            early_exit_notification = LoadConditionalLayerRequest.OBJECT_MOVED_TO_HOUSEHOLD_INVENTORY_NOTIFICATION(services.active_sim_info())
            early_exit_notification.show_dialog()

    def _load_layer_immediately(self):
        zone_id = services.current_zone_id()
        layer_info = services.conditional_layer_service()._get_layer_info(self.conditional_layer)
        mark_conditional_objects_loaded(zone_id, self.conditional_layer.layer_name, layer_info.objects_loaded)
        complete, object_ids = load_conditional_objects(zone_id, self.conditional_layer.layer_name, -1)
        if not complete:
            logger.error('Error when trying to load layer {}.  Attempted to load entire layer at once and it did not completely load everything.', self.conditional_layer)
        self._set_up_loaded_objects(object_ids)
        if is_archive_enabled():
            archive_layer_request_culling(self, (LayerRequestAction.EXECUTING), objects_in_layer_count=(len(layer_info.objects_loaded)))
        services.conditional_layer_service().complete_current_request()

    def _load_layer_gradually(self):
        zone_id = services.current_zone_id()
        layer_info = services.conditional_layer_service()._get_layer_info(self.conditional_layer)
        mark_conditional_objects_loaded(zone_id, self.conditional_layer.layer_name, layer_info.objects_loaded)

        def load_objects_callback(_):
            complete, object_ids = load_conditional_objects(zone_id, self.conditional_layer.layer_name, self.timer_object_count)
            self._set_up_loaded_objects(object_ids)
            if is_archive_enabled():
                archive_layer_request_culling(self, (LayerRequestAction.EXECUTING), objects_in_layer_count=(len(layer_info.objects_loaded)))
            if complete:
                alarms.cancel_alarm(self.alarm_handle)
                self._alarm_handle = None
                services.conditional_layer_service().complete_current_request()

        self.alarm_handle = alarms.add_alarm(self, (TimeSpan.ZERO),
          load_objects_callback,
          repeating=True,
          repeating_time_span=create_time_span(minutes=(self.timer_interval)))

    def _load_layer_as_client_only(self):
        conditional_layer_service = services.conditional_layer_service()
        conditional_layer_service._set_client_layer((self.conditional_layer), True, speed=(self.speed))
        conditional_layer_service.complete_current_request()

    def execute_request(self):
        if self.conditional_layer.client_only:
            self._load_layer_as_client_only()
        else:
            if self.speed == ConditionalLayerRequestSpeedType.GRADUALLY:
                self._load_layer_gradually()
            else:
                if self.speed == ConditionalLayerRequestSpeedType.IMMEDIATELY:
                    self._load_layer_immediately()
                else:
                    logger.error('Invalid speed {} has been set for load conditional layer request.', self._speed)


class DestroyConditionalLayerRequest(ConditionalLayerRequest):
    DESTRUCTION_TIMEOUT = TunableSimMinute(description='\n        The number of SimMinutes that we will give Sims to stop using the\n        object before we go ahead and destroy it anyways.\n        ',
      default=10,
      minimum=1)

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._destory_object_timeouts = {}

    @classproperty
    def request_type(cls):
        return ConditionalLayerRequestType.DESTROY_LAYER

    def cleanup_request(self):
        super().cleanup_request()
        self._destory_object_timeouts = None

    def _destroy_layer_immediately(self):
        object_manager = services.object_manager()
        layer_info = services.conditional_layer_service()._get_layer_info(self.conditional_layer)
        for object_id in layer_info.objects_loaded:
            obj = object_manager.get(object_id)
            if obj is not None:
                obj.destroy(source=self, cause='Destroying object from conditional layer service.',
                  fade_duration=(ClientObjectMixin.FADE_DURATION))

        layer_info.objects_loaded.clear()
        conditional_layer_destroyed(services.current_zone_id(), self.conditional_layer.layer_name)
        services.conditional_layer_service().complete_current_request()

    def _destroy_objects_callback(self, _):
        object_manager = services.object_manager()
        layer_info = services.conditional_layer_service()._get_layer_info(self.conditional_layer)
        objects_destroyed = 0
        objects_index = 0
        now = services.time_service().sim_now
        timeout_time = now + create_time_span(minutes=(DestroyConditionalLayerRequest.DESTRUCTION_TIMEOUT))
        objects_loaded = list(layer_info.objects_loaded)
        while objects_destroyed < self.timer_object_count:
            if not objects_loaded:
                alarms.cancel_alarm(self.alarm_handle)
                self.alarm_handle = None
                conditional_layer_destroyed(services.current_zone_id(), self.conditional_layer.layer_name)
                services.conditional_layer_service().complete_current_request()
                return
            if objects_index >= len(objects_loaded):
                return
            object_id = objects_loaded[objects_index]
            obj = object_manager.get(object_id)
            if obj is None:
                del objects_loaded[objects_index]
                layer_info.objects_loaded.remove(object_id)
                continue
            timeout = self._destory_object_timeouts.get(object_id)
            if timeout is not None:
                if timeout <= now:
                    obj.destroy(source=self, cause='Destroying object from conditional layer service.',
                      fade_duration=(ClientObjectMixin.FADE_DURATION))
                    del self._destory_object_timeouts[object_id]
                    objects_destroyed += 1
                    continue
            users = obj.get_users()
            if users:
                objects_index += 1
                if object_id in self._destory_object_timeouts:
                    continue
                for sim in users:
                    for interaction in sim.si_state:
                        if interaction.target is None:
                            continue
                        if not interaction.target is obj:
                            if interaction.target.is_part:
                                if interaction.target.part_owner is obj:
                                    pass
                                interaction.cancel((FinishingType.TARGET_DELETED), cancel_reason_msg='Removing conditional object.')

                self._destory_object_timeouts[object_id] = timeout_time
                continue
            obj.destroy(source=self, cause='Destroying object from conditional layer service.',
              fade_duration=(ClientObjectMixin.FADE_DURATION))
            del objects_loaded[objects_index]
            layer_info.objects_loaded.remove(object_id)
            if object_id in self._destory_object_timeouts:
                del self._destory_object_timeouts[object_id]
            objects_destroyed += 1

    def _destroy_layer_gradually(self):
        self.alarm_handle = alarms.add_alarm(self, (TimeSpan.ZERO),
          (self._destroy_objects_callback),
          repeating=True,
          repeating_time_span=create_time_span(minutes=(self.timer_interval)))

    def _destroy_layer_as_client_only(self, speed):
        conditional_layer_service = services.conditional_layer_service()
        conditional_layer_service._set_client_layer((self.conditional_layer), False, speed=speed)
        conditional_layer_service.complete_current_request()

    def execute_request(self):
        speed = ConditionalLayerRequestSpeedType.IMMEDIATELY if services.current_zone().is_zone_shutting_down else self.speed
        if self.conditional_layer.client_only:
            self._destroy_layer_as_client_only(speed)
        else:
            if speed == ConditionalLayerRequestSpeedType.GRADUALLY:
                self._destroy_layer_gradually()
            else:
                if speed == ConditionalLayerRequestSpeedType.IMMEDIATELY:
                    self._destroy_layer_immediately()
                else:
                    logger.error('Invalid speed {} has been set for destroy conditional layer request.', self._speed)


class ConditionalLayerInfo:

    def __init__(self):
        self.objects_loaded = set()
        self.last_request_type = None


class ConditionalLayerService(Service):
    STREET_LAYER_OBJECTS_TO_DESTROY = TunableRange(description="\n        The number of objects from the street's tested conditional layers\n        to destroy at a time when destroying a layer.\n        ",
      tunable_type=int,
      default=1,
      minimum=1)
    STREET_LAYER_OBJECTS_ALARM_TIME = TunableSimMinute(description="\n        The frequency that we will create or destroy objects in the street's\n        tested conditional layers.        \n        ",
      default=5,
      minimum=1)

    def __init__(self):
        self._layer_infos = {}
        self._current_request = None
        self._requests = []
        self._active_street_conditional_layers = set()

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_CONDITIONAL_LAYER_SERVICE

    @property
    def requests(self):
        return tuple(self._requests)

    def on_client_disconnect(self, client):
        for conditional_layer in self._layer_infos:
            self._set_client_layer(conditional_layer, False, speed=(ConditionalLayerRequestSpeedType.IMMEDIATELY))

    def stop(self):
        super().stop()
        if self._current_request is not None:
            self._current_request.cleanup_request()
        for request in self._requests:
            request.cleanup_request()

    def save(self, open_street_data=None, **kwargs):
        if open_street_data is None:
            return
        open_street_data.conditional_layer_service = gameplay_serialization.ConditionalLayerServiceData()
        for conditional_layer, layer_info in self._layer_infos.items():
            if not layer_info.objects_loaded:
                if not conditional_layer.client_only:
                    continue
                elif conditional_layer.client_only and layer_info.last_request_type != ConditionalLayerRequestType.LOAD_LAYER:
                    continue
                with ProtocolBufferRollback(open_street_data.conditional_layer_service.layer_infos) as (layer_data):
                    layer_data.conditional_layer = conditional_layer.guid64
                    layer_data.object_ids.extend(list(layer_info.objects_loaded))

    def load(self, zone_data=None, **kwargs):
        open_street_id = services.current_zone().open_street_id
        open_street_data = services.get_persistence_service().get_open_street_proto_buff(open_street_id)
        return open_street_data is None or open_street_data.HasField('conditional_layer_service') or None
        conditional_layers = services.get_instance_manager(sims4.resources.Types.CONDITIONAL_LAYER).types.values()
        for layer_data in open_street_data.conditional_layer_service.layer_infos:
            if layer_data.layer_hash != 0:
                for conditional_layer in conditional_layers:
                    if conditional_layer.layer_name == layer_data.layer_hash:
                        break
                else:
                    conditional_layer = None

                if conditional_layer is None:
                    logger.error('Trying to load a conditional_layer via the layer_hash but one was not found. layer_hash = {}', layer_data.layer_hash)
                    continue
                layer_info = self._get_layer_info(conditional_layer)
            else:
                conditional_layer_manager = services.get_instance_manager(sims4.resources.Types.CONDITIONAL_LAYER)
                conditional_layer = conditional_layer_manager.get(layer_data.conditional_layer)
                layer_info = self._get_layer_info(conditional_layer)
            layer_info.objects_loaded = set(layer_data.object_ids)
            if conditional_layer.client_only or layer_info.objects_loaded:
                layer_info.last_request_type = ConditionalLayerRequestType.LOAD_LAYER

    def on_zone_load(self, **kwargs):
        for conditional_layer in self._layer_infos:
            if conditional_layer.client_only and conditional_layer not in self._active_street_conditional_layers:
                self._set_client_layer(conditional_layer, True, speed=(ConditionalLayerRequestSpeedType.IMMEDIATELY))

    def on_zone_unload(self):
        for conditional_layer, layer_info in self._layer_infos.items():
            if conditional_layer.client_only and layer_info.last_request_type == ConditionalLayerRequestType.LOAD_LAYER and conditional_layer not in self._active_street_conditional_layers:
                self._set_client_layer(conditional_layer, False, speed=(ConditionalLayerRequestSpeedType.IMMEDIATELY))

    def _execute_next_request(self):
        while self._requests:
            request = self._requests.pop(0)
            layer_info = self._get_layer_info(request.conditional_layer)
            if layer_info.last_request_type != request.request_type:
                self._current_request = request
                logger.info('Executing Request: {}', self._current_request)
                if is_archive_enabled():
                    archive_layer_request_culling(self._current_request, LayerRequestAction.EXECUTING)
                self._current_request.execute_request()
                return
            try:
                request.notify_requester()
            except Exception:
                logger.exception('Exception while notifying request owner.')

    def _add_request(self, request):
        layer_info = self._get_layer_info(request.conditional_layer)
        if request.conditional_layer.layer_name is None:
            logger.error('Layer name for {} is None, this request will not be processed.', request.conditional_layer)
        else:
            logger.info('Adding Request: {}', request)
            self._requests.append(request)
        if is_archive_enabled():
            archive_layer_request_culling(request, LayerRequestAction.SUBMITTED)
        if self._current_request is None:
            self._execute_next_request()

    def complete_current_request(self):
        if self._current_request is None:
            logger.error("Trying to complete the current request when one doesn't exist.")
        else:
            request = self._current_request
            layer_info = self._get_layer_info(request.conditional_layer)
            if request.request_type is ConditionalLayerRequestType.DESTROY_LAYER:
                del self._layer_infos[request.conditional_layer]
            else:
                layer_info.last_request_type = request.request_type
        try:
            request.notify_requester()
        except Exception:
            logger.exception('Exception while notifying request owner.')

        self._current_request = None
        self._execute_next_request()

    def is_object_in_conditional_layer(self, obj_id):
        return any((obj_id in layer_info.objects_loaded for layer_info in self._layer_infos.values()))

    def is_layer_loaded(self, conditional_layer, consider_queued_requests=True):
        if consider_queued_requests:
            for i in range(-1, -len(self._requests), -1):
                request = self._requests[i]
                if request.conditional_layer == conditional_layer:
                    return request.request_type == ConditionalLayerRequestType.LOAD_LAYER

            if self._current_request is not None:
                if self._current_request.conditional_layer == conditional_layer:
                    return self._current_request.request_type == ConditionalLayerRequestType.LOAD_LAYER
        layer_info = self._layer_infos.get(conditional_layer)
        return layer_info is not None and layer_info.last_request_type == ConditionalLayerRequestType.LOAD_LAYER

    def _get_layer_info(self, conditional_layer):
        if conditional_layer not in self._layer_infos:
            self._layer_infos[conditional_layer] = ConditionalLayerInfo()
        return self._layer_infos[conditional_layer]

    def _set_client_layer(self, conditional_layer, is_load, speed=None):
        zone_id = services.current_zone_id()
        client = services.client_manager().get_first_client()
        if client is None:
            if is_load:
                logger.error('Adding client layer but there is no client.')
            else:
                if not services.current_zone().is_zone_shutting_down:
                    logger.error('Removing client layer but there is no client.')
            return
        account_id = services.client_manager().get_first_client().account.id
        if speed != ConditionalLayerRequestSpeedType.IMMEDIATELY and conditional_layer.fade_data is not None:
            fade_duration = conditional_layer.fade_data.fade_duration
            delay_min = conditional_layer.fade_data.delay_min
            delay_max = conditional_layer.fade_data.delay_max
            set_client_conditional_layer_active(zone_id, account_id, conditional_layer.layer_name, is_load, fade_duration, delay_min, delay_max)
        else:
            set_client_conditional_layer_active(zone_id, account_id, conditional_layer.layer_name, is_load)

    def get_layer_objects(self, conditional_layer):
        layer_info = self._get_layer_info(conditional_layer)
        object_manager = services.object_manager()
        layer_objects = []
        for object_id in layer_info.objects_loaded:
            obj = object_manager.get(object_id)
            if obj is not None:
                layer_objects.append(obj)

        return layer_objects

    def load_conditional_layer(self, conditional_layer, callback=None, speed=ConditionalLayerRequestSpeedType.IMMEDIATELY, timer_interval=0, timer_object_count=0, fade_in=True):
        request = LoadConditionalLayerRequest(conditional_layer, callback,
          speed,
          timer_interval,
          timer_object_count,
          fade_in=fade_in)
        self._add_request(request)

    def destroy_conditional_layer(self, conditional_layer, callback=None, speed=ConditionalLayerRequestSpeedType.IMMEDIATELY, timer_interval=0, timer_object_count=0):
        request = DestroyConditionalLayerRequest(conditional_layer, callback, speed, timer_interval, timer_object_count)
        self._add_request(request)