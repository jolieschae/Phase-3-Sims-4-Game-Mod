# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\register_test_event_mixin.py
# Compiled at: 2017-03-29 18:00:18
# Size of source mod 2**32: 1886 bytes
import services

class RegisterTestEventMixin:

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._registered_test_events = set()

    def _register_test_event_for_keys(self, test_event, custom_keys):
        for custom_key in custom_keys:
            self._register_test_event(test_event, custom_key)

    def _register_test_event(self, test_event, custom_key=None):
        custom_key_tuple = (
         test_event, custom_key)
        self._registered_test_events.add(custom_key_tuple)
        services.get_event_manager().register_with_custom_key(self, test_event, custom_key)

    def _unregister_test_event(self, test_event, custom_key=None):
        custom_key_tuple = (
         test_event, custom_key)
        if custom_key_tuple in self._registered_test_events:
            self._registered_test_events.remove(custom_key_tuple)
            services.get_event_manager().unregister_with_custom_key(self, test_event, custom_key)

    def _unregister_for_all_test_events(self):
        for event_type, custom_key in self._registered_test_events:
            services.get_event_manager().unregister_with_custom_key(self, event_type, custom_key)

        self._registered_test_events.clear()