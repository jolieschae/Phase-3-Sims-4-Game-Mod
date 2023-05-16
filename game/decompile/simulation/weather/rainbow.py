# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\weather\rainbow.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 3272 bytes
import random
from event_testing.resolver import SingleObjectResolver
from event_testing.tests import TunableTestSet
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableRange, TunablePackSafeReference
from tag import TunableTags
import objects.system, placement, services, sims4

class SpawnRainbow(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'tests':TunableTestSet(description='\n            Tests to run to validate if the placement of the rainbow should\n            be valid.  This will run over the object being placed, so any\n            object tests will be valid.\n            '), 
     'rainbow_definition':TunablePackSafeReference(description='\n            Rainbow definition to be placed on the world.\n            ',
       manager=services.definition_manager()), 
     'spawner_object_tag_set':TunableTags(description='\n            The set of tags that define the objects where the new object\n            should try to position itself.\n            ',
       filter_prefixes=('func', )), 
     'spawn_max_radius':TunableRange(description='\n            Max radius around the spawner object to search to place the new\n            object.\n            ',
       tunable_type=int,
       default=3,
       minimum=0)}

    def apply_event(self):
        if self.rainbow_definition is None:
            return
        else:
            spawner_objs = services.object_manager().get_objects_matching_tags(self.spawner_object_tag_set)
            if not spawner_objs:
                return
                spawner_obj = random.choice(list(spawner_objs))
                resolver = SingleObjectResolver(spawner_obj)
                if not self.tests.run_tests(resolver):
                    return
                rainbow_obj = objects.system.create_object(self.rainbow_definition)
                rainbow_obj.location = sims4.math.Location(sims4.math.Transform(spawner_obj.position, spawner_obj.orientation), spawner_obj.routing_surface)
                starting_location = placement.create_starting_location(position=(spawner_obj.position), orientation=(spawner_obj.orientation))
                fgl_context = placement.create_fgl_context_for_object_off_lot(starting_location, rainbow_obj, max_distance=(self.spawn_max_radius), ignored_object_ids=(spawner_obj.id,))
                position, orientation, _ = fgl_context.find_good_location()
                if position is not None:
                    rainbow_obj.location = sims4.math.Location(sims4.math.Transform(position, orientation), rainbow_obj.routing_surface)
            else:
                rainbow_obj.destroy(source=self, cause='RainbowCreation: FGL failed, object will not be created.')