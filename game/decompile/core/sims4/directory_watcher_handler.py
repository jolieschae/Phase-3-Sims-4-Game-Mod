# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\directory_watcher_handler.py
# Compiled at: 2014-06-11 04:51:45
# Size of source mod 2**32: 4265 bytes
import queue, sims4.log
logger = sims4.log.Logger('Directory Watcher Change Handler')

class DirectoryWatcherHandler:

    def __init__(self):
        self._q = queue.Queue()
        self._watcher = None

    def _test(self):
        return (lambda filename: True)

    def _parse_filename(self):

        def add_files(changed_files, removed_files):
            for filename in changed_files:
                self._q.put(filename)

            for filename in removed_files:
                self._q.put(filename)

        return add_files

    def _handle(self):
        raise NotImplementedError('_handle not implemented in a DirectoryWatcherHandler subclass')

    def _paths(self):
        raise NotImplementedError('_paths not implemented in a DirectoryWatcherHandler subclass')

    def set_paths(self, paths):
        raise NotImplementedError('set_paths not implemented in a DirectoryWatcherHandler subclass')

    def on_tick(self):
        self._watcher.on_tick()
        while not self._q.empty():
            self._handle(self._q.get())

    def start(self):
        try:
            from sims4 import filewatcher
        except ImportError:
            logger.warn('filewatcher is unavailable; unable to start reloader')
            return False
        else:
            tester = self._test()
            handler = self._parse_filename()

            def callback(path, action):
                if tester(path):
                    changed = []
                    removed = []
                    if action == filewatcher.ACTION_REMOVED:
                        removed.append(path)
                    else:
                        changed.append(path)
                    handler(changed, removed)

            self._watcher = filewatcher.MultiDirectoryWatcher(self._paths(), callback)
            return self._watcher.start()

    def stop(self):
        if self._watcher is not None:
            self._watcher.stop()
            self._watcher = None