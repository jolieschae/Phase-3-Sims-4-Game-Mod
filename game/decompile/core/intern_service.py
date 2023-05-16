# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\intern_service.py
# Compiled at: 2015-02-23 19:52:12
# Size of source mod 2**32: 2558 bytes
import sims4.log, sims4.service_manager
logger = sims4.log.Logger('InternService', default_owner='manus')

class InternService(sims4.service_manager.Service):

    def __init__(self):
        self._intern_dict = None
        self.started = False

    def intern(self, item):
        if self._intern_dict is None:
            return item
        if item in self._intern_dict:
            return self._intern_dict[item]
        self._intern_dict[item] = item
        return item

    def start(self):
        self.started = True

    def stop(self):
        self.started = False
        if self._intern_dict is not None:
            logger.error('InternService was not stopped using a service.')
            self.stop_interning()

    def _start_interning(self):
        if not self.started:
            logger.error('InternService was not started.')
        if self._intern_dict is not None:
            logger.error('InternService was double-started.')
        self._intern_dict = {}

    def _stop_interning(self):
        if self._intern_dict is None:
            logger.error('InternService was double-stopped.')
        self._intern_dict = None

    def get_start_interning(self):
        return _StartInterning(self)

    def get_stop_interning(self):
        return _StopInterning(self)


class _StartInterning(sims4.service_manager.Service):

    def __init__(self, intern_service):
        self.intern_service = intern_service

    def start(self):
        self.intern_service._start_interning()


class _StopInterning(sims4.service_manager.Service):

    def __init__(self, intern_service):
        self.intern_service = intern_service

    def start(self):
        self.intern_service._stop_interning()