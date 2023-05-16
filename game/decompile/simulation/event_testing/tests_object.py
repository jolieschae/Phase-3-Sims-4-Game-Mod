# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\tests_object.py
# Compiled at: 2017-02-03 01:14:23
# Size of source mod 2**32: 2758 bytes
from objects.object_tests import TagTestType
from sims4.tuning.tunable import TunableFactory, TunableEnumEntry, OptionalTunable, TunableReference
import services, sims4, tag

class NumberTaggedObjectsOwnedFactory(TunableFactory):

    @staticmethod
    def factory(tag_set, test_type, desired_state, required_household_owner_id=None):
        items = []
        for obj in services.object_manager().values():
            if required_household_owner_id is not None:
                if obj.get_household_owner_id() != required_household_owner_id:
                    continue
                else:
                    if desired_state is not None:
                        if not obj.has_state(desired_state.state):
                            continue
                        if obj.get_state(desired_state.state) is not desired_state:
                            continue
                    object_tags = set(obj.get_tags())
                    if test_type == TagTestType.CONTAINS_ANY_TAG_IN_SET:
                        if object_tags & tag_set:
                            items.append(obj)
                    if test_type == TagTestType.CONTAINS_ALL_TAGS_IN_SET and object_tags & tag_set == tag_set:
                        items.append(obj)
                if test_type == TagTestType.CONTAINS_NO_TAGS_IN_SET:
                    object_tags & tag_set or items.append(obj)

        return items

    FACTORY_TYPE = factory

    def __init__(self, **kwargs):
        (super().__init__)(tag_set=sims4.tuning.tunable.TunableSet(TunableEnumEntry((tag.Tag), (tag.Tag.INVALID), description='What tag to test for'), description='The tags of objects we want to test ownership of'), 
         test_type=TunableEnumEntry(TagTestType, (TagTestType.CONTAINS_ANY_TAG_IN_SET), description='How to test the tags in the tag set against the objects on the lot.'), 
         desired_state=OptionalTunable(TunableReference(description='\n                             A state value that must exist on the object to be counted. Example: Masterwork',
  manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
  class_restrictions='ObjectStateValue')), **kwargs)