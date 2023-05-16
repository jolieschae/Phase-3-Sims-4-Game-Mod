# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\school\school_tuning.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 4392 bytes
from event_testing.resolver import SingleSimResolver
from event_testing.tests import TunableTestSet
from objects import ALL_HIDDEN_REASONS
from objects.system import create_object
from sims.sim_info_types import Age
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableMapping, TunableEnumEntry
import services, sims4.resources

class SchoolTuning(HasTunableSingletonFactory, AutoFactoryInit):

    class _SchoolData(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'school_career':TunableReference(description='\n                The career for this age.\n                ',
           manager=services.get_instance_manager(sims4.resources.Types.CAREER)), 
         'school_homework':TunableReference(description='\n                The homework object for this school career.\n                ',
           manager=services.definition_manager())}

    FACTORY_TUNABLES = {'school_data':TunableMapping(description='\n            Ensure Sims of these ages are auto-enrolled in school.\n            ',
       key_type=TunableEnumEntry(description='\n                The age for which we ensure a school career is added.\n                ',
       tunable_type=Age,
       default=(Age.CHILD)),
       value_type=_SchoolData.TunableFactory(),
       minlength=1), 
     'school_data_tests':TunableTestSet(description="\n            Tests that must pass in order for a Sim to be added to a school career on load.\n            \n            Example: with EP12 installed we don't want drop outs or early graduates being forced back into school. \n            Testing for the appropriate traits prevents that from happening, but only when EP12 is installed.\n            ")}

    def update_school_data(self, sim_info, create_homework=False):
        self._apply_school_career(sim_info)
        if create_homework:
            self._create_homework(sim_info)

    def _apply_school_career(self, sim_info):
        for school_age, school_data in self.school_data.items():
            school_career_type = school_data.school_career
            if school_age == sim_info.age:
                if school_career_type.guid64 not in sim_info.careers:
                    resolver = SingleSimResolver(sim_info)
                    if self.school_data_tests.run_tests(resolver):
                        sim_info.career_tracker.add_career(school_career_type(sim_info, init_track=True))
            else:
                sim_info.career_tracker.remove_career((school_career_type.guid64), post_quit_msg=False)

    def _create_homework(self, sim_info):
        sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if sim is None:
            return
        school_data = self.school_data.get(sim_info.age, None)
        if school_data is None:
            return
        inventory = sim.inventory_component
        if inventory.has_item_with_definition(school_data.school_homework):
            return
        obj = create_object(school_data.school_homework)
        if obj is not None:
            obj.update_ownership(sim)
            if inventory.can_add(obj):
                inventory.player_try_add_object(obj)
                return
            obj.destroy(source=self, cause='Failed to add homework to sim inventory')