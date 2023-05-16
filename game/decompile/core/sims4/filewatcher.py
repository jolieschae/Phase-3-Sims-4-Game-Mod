# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\filewatcher.py
# Compiled at: 2017-05-03 22:37:40
# Size of source mod 2**32: 3125 bytes
import os.path, sims4.log
logger = sims4.log.Logger('Filewatcher')
import _filemonitor
from _filemonitor import *
FILTER_FLAG_NAMES = {flag: name for name, flag in vars(_filemonitor).items() if name.startswith('FILTER_')}
ACTION_NAMES = {value: name for name, value in vars(_filemonitor).items() if name.startswith('ACTION_')}

def filter_repr(filter_flags):
    return ', '.join([name for flag, name in FILTER_FLAG_NAMES.items() if filter_flags & flag])


class DirectoryWatcher:

    def __init__(self, path, callback, filter_flags=FILTER_WRITES):
        self.path = path
        self.filter = filter_flags
        self.callback = callback
        self._monitor = None

    def start(self):
        logger.debug('Attempting to monitor {0}', self.path)
        try:
            self._monitor = DirectoryMonitor(self.path, self.filter)
        except BaseException as exc:
            try:
                logger.error('Unable to start DirectoryMonitor on {} ({}) ({})', self.path, filter_repr(self.filter), exc)
                return False
            finally:
                exc = None
                del exc

        return True

    def stop(self):
        self._monitor = None

    def on_tick(self):
        if self._monitor is None:
            return
        changes = self._monitor.poll()
        if changes:
            for change in changes:
                path = os.path.join(self.path, change[0])
                self.callback(path, change[1])


class MultiDirectoryWatcher:

    def __init__(self, paths, callback, filter_flags=FILTER_WRITES):
        self.watchers = [DirectoryWatcher(path, callback, filter_flags) for path in paths]

    def start(self):
        for watcher in self.watchers:
            watcher.start()

    def stop(self):
        for watcher in self.watchers:
            watcher.stop()

    def on_tick(self):
        for watcher in self.watchers:
            watcher.on_tick()