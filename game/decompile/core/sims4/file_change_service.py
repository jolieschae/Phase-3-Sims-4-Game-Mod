# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\file_change_service.py
# Compiled at: 2014-06-08 22:04:28
# Size of source mod 2**32: 4014 bytes
from sims4.file_change_handler import FileChangeHandler
from sims4.service_manager import Service
from sims4.tuning.merged_tuning_manager import get_manager
import sims4.core_services
__all__ = [
 'FileChangeService']

class FileChangeService(Service):

    class FileChangeServiceHandler(FileChangeHandler):

        def _handle(self, key):
            sims4.core_services.file_change_manager().register_change(self._name, key)

    def __init__(self):
        self.change_sets = {}

    def stop(self):
        for name in self.change_sets.keys():
            self.remove_set(name)

    def create_set(self, name, type_filter=None, group_filter=None):
        if name in self.change_sets:
            raise KeyError("A change set with the name '{}' already exists. Please choose a unique name".format(name))
        handler = self.FileChangeServiceHandler(name, type_filter, group_filter)
        if not handler.start():
            raise RuntimeError('Unable to successfully register for a file change callback with group ID {} and type ID {}'.format(group_filter, type_filter))
        self.change_sets[name] = (
         handler, [])

    def register_change(self, setname, resource_key):
        if setname:
            changed_resources = self.change_sets[setname][1]
            if resource_key not in changed_resources:
                changed_resources.append(resource_key)
        else:
            for data in self.change_sets.values():
                if data[1] and resource_key not in data[1]:
                    data[1].append(resource_key)

        mtg = get_manager()
        mtg.register_change(resource_key)

    def consume_set(self, name):
        handler, changed_resources = self.change_sets[name]
        self.change_sets[name] = (
         handler, [])
        return changed_resources

    def remove_set(self, name):
        set_data = self.change_sets[name]
        del self.change_sets[name]
        handler = set_data[0]
        handler.stop()