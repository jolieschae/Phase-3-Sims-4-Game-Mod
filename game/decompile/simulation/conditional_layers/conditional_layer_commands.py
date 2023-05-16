# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\conditional_layers\conditional_layer_commands.py
# Compiled at: 2021-05-21 19:24:38
# Size of source mod 2**32: 4175 bytes
from conditional_layers.conditional_layer_enums import ConditionalLayerRequestSpeedType
from server_commands.argument_helpers import TunableInstanceParam
import services, sims4.commands

@sims4.commands.Command('layers.load_layer')
def load_conditional_layer(conditional_layer: TunableInstanceParam(sims4.resources.Types.CONDITIONAL_LAYER), immediate: bool=True, timer_interval: int=1, timer_object_count: int=5):
    if conditional_layer is None:
        sims4.commands.output('Unable to find the conditional_layer instance specified.')
        return
    conditional_layer_service = services.conditional_layer_service()
    speed = ConditionalLayerRequestSpeedType.IMMEDIATELY if immediate else ConditionalLayerRequestSpeedType.GRADUALLY
    conditional_layer_service.load_conditional_layer(conditional_layer, speed=speed,
      timer_interval=timer_interval,
      timer_object_count=timer_object_count)


@sims4.commands.Command('layers.destroy_layer')
def destroy_conditional_layer(conditional_layer: TunableInstanceParam(sims4.resources.Types.CONDITIONAL_LAYER), immediate: bool=True, timer_interval: int=1, timer_object_count: int=5):
    conditional_layer_service = services.conditional_layer_service()
    speed = ConditionalLayerRequestSpeedType.IMMEDIATELY if immediate else ConditionalLayerRequestSpeedType.GRADUALLY
    conditional_layer_service.destroy_conditional_layer(conditional_layer, speed=speed,
      timer_interval=timer_interval,
      timer_object_count=timer_object_count)


@sims4.commands.Command('layers.reload_layer')
def reload_conditional_layer(conditional_layer: TunableInstanceParam(sims4.resources.Types.CONDITIONAL_LAYER), immediate: bool=True, timer_interval: int=1, timer_object_count: int=5):
    conditional_layer_service = services.conditional_layer_service()
    speed = ConditionalLayerRequestSpeedType.IMMEDIATELY if immediate else ConditionalLayerRequestSpeedType.GRADUALLY
    conditional_layer_service.destroy_conditional_layer(conditional_layer, speed=speed,
      timer_interval=timer_interval,
      timer_object_count=timer_object_count)
    conditional_layer_service.load_conditional_layer(conditional_layer, speed=speed,
      timer_interval=timer_interval,
      timer_object_count=timer_object_count)


@sims4.commands.Command('layers.active_layers')
def list_active_layers(_connection=None):
    conditional_layer_service = services.conditional_layer_service()
    for conditional_layer, layer_info in conditional_layer_service._layer_infos.items():
        if layer_info.last_request_type != ConditionalLayerRequestType.LOAD_LAYER:
            continue
        msg = '{} : {}'.format(conditional_layer.__name__, len(layer_info.objects_loaded))
        sims4.commands.automation_output(msg, _connection)
        sims4.commands.cheat_output(msg, _connection)

    sims4.commands.automation_output('END', _connection)