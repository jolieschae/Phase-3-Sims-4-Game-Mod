# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\command_handlers.py
# Compiled at: 2014-06-08 22:42:14
# Size of source mod 2**32: 1793 bytes
import time
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiSchema
import services, sims4.core_services
SLEEP_TIME = 0.1
TIMEOUT = int(1 / SLEEP_TIME)
command_schema = GsiSchema()
command_schema.add_field('response', label='Response')

@GsiHandler('command', command_schema)
def invoke_command(command=None, zone_id: int=None):
    ready = False
    output_accum = ''
    response = ''

    def _callback(result):
        nonlocal ready
        nonlocal response
        if result:
            response = 'Success<br>' + output_accum
        else:
            response = 'Failure<br>' + output_accum
        ready = True

    if command is not None:

        def _fake_output(s, context=None):
            nonlocal response
            response += '<br>' + s

        connection = services.client_manager().get_first_client()
        sims4.core_services.command_buffer_service().add_command(command, _callback, _fake_output, zone_id, connection.id)
    timeout_counter = 0
    while not ready:
        time.sleep(SLEEP_TIME)
        timeout_counter += 1
        if timeout_counter > TIMEOUT:
            ready = True

    return {'response': response}