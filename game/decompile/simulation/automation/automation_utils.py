# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\automation\automation_utils.py
# Compiled at: 2017-05-26 17:30:18
# Size of source mod 2**32: 858 bytes
from sims4.commands import automation_output
import services, sims4.reload
with sims4.reload.protected(globals()):
    dispatch_automation_events = False

def automation_event(message, **msg_data):
    if not dispatch_automation_events:
        return
    else:
        connection = services.client_manager().get_first_client_id()
        if msg_data:
            data_str = ['{}: {}'.format(k, v) for k, v in msg_data.items()]
            data_str = ', '.join(data_str)
            automation_output('{0}; {1}'.format(message, data_str), connection)
        else:
            automation_output('{0};'.format(message), connection)