# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\jigs.py
# Compiled at: 2020-02-04 19:46:12
# Size of source mod 2**32: 1029 bytes
import objects.game_object, objects.object_enums, objects.persistence_groups, sims4.tuning.instances

class Jig(objects.game_object.GameObject):

    @property
    def persistence_group(self):
        return objects.persistence_groups.PersistenceGroups.NONE

    @persistence_group.setter
    def persistence_group(self, value):
        pass

    def save_object(self, object_list, *args, item_location=objects.object_enums.ItemLocation.ON_LOT, container_id=0, **kwargs):
        pass

    @property
    def is_valid_posture_graph_object(self):
        return False


sims4.tuning.instances.lock_instance_tunables(Jig, _persistence=(objects.object_enums.PersistenceType.NONE),
  _world_file_object_persists=False)