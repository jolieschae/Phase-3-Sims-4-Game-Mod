# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\live_events\live_event_telemetry.py
# Compiled at: 2021-11-22 21:29:05
# Size of source mod 2**32: 1277 bytes
import sims4.telemetry, telemetry_helper
TELEMETRY_GROUP_AB_TESTS = 'ABTE'
TELEMETRY_HOOK_AB_TEST_DIALOG = 'ABDG'
TELEMETRY_FIELD_AB_TEST_NAME = 'test'
TELEMETRY_FIELD_DIALOG_RESPONSE = 'dres'
ab_test_telemetry_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_AB_TESTS)

class LiveEventTelemetry:

    @staticmethod
    def send_live_event_dialog_telemetry(test_name, sim_info, dialog_response):
        with telemetry_helper.begin_hook(ab_test_telemetry_writer, TELEMETRY_HOOK_AB_TEST_DIALOG, sim_info=sim_info) as (hook):
            hook.write_string(TELEMETRY_FIELD_AB_TEST_NAME, test_name.name)
            hook.write_enum(TELEMETRY_FIELD_DIALOG_RESPONSE, dialog_response)