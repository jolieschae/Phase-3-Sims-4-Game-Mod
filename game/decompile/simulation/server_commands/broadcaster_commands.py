# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\broadcaster_commands.py
# Compiled at: 2015-07-15 19:14:35
# Size of source mod 2**32: 2620 bytes
from server_commands.argument_helpers import OptionalTargetParam, TunableInstanceParam, get_optional_target
from sims4.commands import CommandType
import services, sims4.commands, sims4.resources

@sims4.commands.Command('broadcasters.add')
def broadcasters_add(broadcaster_type: TunableInstanceParam(sims4.resources.Types.BROADCASTER), broadcasting_object: OptionalTargetParam=None, _connection=None):
    broadcasting_object = get_optional_target(broadcasting_object, _connection)
    if broadcasting_object is None:
        return False
    broadcaster = broadcaster_type(broadcasting_object=broadcasting_object)
    broadcaster_service = broadcaster.get_broadcaster_service()
    broadcaster_service.add_broadcaster(broadcaster)
    return True


def _output_broadcaster_cache(object_cache, tags_cache, output):
    if object_cache is None:
        output('    There is no cache.')
        return
    elif tags_cache is None:
        output('    Considering all objects.')
    else:
        output('    Considering objects with tags:')
        for tag in tags_cache:
            output('        {}'.format(tag))

    output('    Cached objects:')
    for obj in object_cache:
        output('        {}'.format(obj))


@sims4.commands.Command('broadcasters.info', command_type=(CommandType.Automation))
def broadcasters_info(_connection=None):
    current_zone = services.current_zone()
    broadcaster_service = current_zone.broadcaster_service
    broadcaster_service_real_time = current_zone.broadcaster_real_time_service
    if broadcaster_service is None or broadcaster_service_real_time is None:
        return False
    output = sims4.commands.Output(_connection)
    output('Broadcaster Service Game Time info:')
    object_cache, object_cache_tags = broadcaster_service.get_object_cache_info()
    _output_broadcaster_cache(object_cache, object_cache_tags, output)
    output('Broadcaster Service Real Time info:')
    real_time_objects, real_time_tags = broadcaster_service_real_time.get_object_cache_info()
    _output_broadcaster_cache(real_time_objects, real_time_tags, output)
    return True