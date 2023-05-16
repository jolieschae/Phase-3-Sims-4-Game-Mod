# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\base\object_picker_mixins.py
# Compiled at: 2021-04-29 16:46:31
# Size of source mod 2**32: 8931 bytes
from build_buy import get_object_or_style_has_tag, get_gig_objects_added, get_gig_objects_deleted
from event_testing.resolver import SingleActorAndObjectResolver
from event_testing.tests import TestListLoadingMixin, TestList
from objects.object_tests import ObjectCriteriaSingleObjectSpecificTest, ObjectCriteriaTest
from interactions import ParticipantType
from sims4.tuning.tunable_base import GroupNames
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableReference, TunableVariant, TunableRange, OptionalTunable, TunableEnumEntry
from sims4.utils import flexmethod
from world.world_tests import DistanceTest
import sims4.resources, services, tag
logger = sims4.log.Logger('Object Picker Mixin', default_owner='shipark')

class TunableObjectTaggedObjectFilterTestSet(TestListLoadingMixin):
    DEFAULT_LIST = TestList()

    def __init__(self, **kwargs):
        (super().__init__)(tunable=TunableVariant(object_criteria_test=ObjectCriteriaTest.TunableFactory(locked_args={'subject_specific_tests':ObjectCriteriaSingleObjectSpecificTest(ObjectCriteriaTest.TARGET_OBJECTS, ParticipantType.Object), 
                   'tooltip':None, 
                   'identity_test':None, 
                   'test_events':()}),
                    distance_test=(DistanceTest.TunableFactory())), **kwargs)


class ObjectPickerMixin:
    INSTANCE_TUNABLES = {'radius':OptionalTunable(description='\n            Ensures objects are within a tuned radius.\n\n            NOTE: THIS SHOULD ONLY BE DISABLED IF APPROVED BY A GPE.\n            Disabling this can have a serious performance impact since most \n            pickers will end up with way too many objects in them.\n            ',
       tunable=TunableRange(description='\n                Object must be in a certain range for consideration.\n                ',
       tunable_type=int,
       default=5,
       minimum=1,
       maximum=50),
       tuning_group=GroupNames.PICKERTUNING,
       enabled_by_default=True), 
     'object_filter_test':TunableObjectTaggedObjectFilterTestSet(description='\n            A list of test to verify object is valid to be selected for autonomous use.\n            ',
       tuning_group=GroupNames.PICKERTUNING)}

    @flexmethod
    def _get_objects_internal_gen(cls, inst, target, context, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        sim = context.sim
        sim_intended_postion = sim.intended_position
        sim_level = sim.level
        for obj in (inst_or_cls._get_mixin_objects_gen)(target, context, **kwargs):
            if inst_or_cls.radius is not None:
                delta = obj.intended_position - sim_intended_postion
                if delta.magnitude() > inst_or_cls.radius:
                    continue
            else:
                if inst_or_cls.object_filter_test:
                    resolver = SingleActorAndObjectResolver((sim.sim_info), obj, source='ObjectPickerMixin')
                    result = inst_or_cls.object_filter_test.run_tests(resolver)
                    if not result:
                        continue
                if obj.parts is not None:
                    connected = False
                    for part in obj.parts:
                        if part.is_connected(sim):
                            connected = True

                    if not connected:
                        continue
            if not obj.is_connected(sim):
                continue
            yield obj

    def _get_mixin_objects_gen(cls, inst, target, context, **kwargs):
        raise NotImplementedError


class GigObjectsPickerMixin(ObjectPickerMixin):
    INSTANCE_TUNABLES = {'gig_career':TunableReference(description='\n            The career from which to get objects added during the active gig.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CAREER),
       tuning_group=GroupNames.PICKERTUNING), 
     'decorator':OptionalTunable(description='\n            If tuned, used the interaction participant to get the decorator. Otherwise,\n            default to the active sim.\n            ',
       tunable=TunableEnumEntry(description='\n                The participant type of the decorator sim.\n                ',
       tunable_type=ParticipantType,
       default=(ParticipantType.Actor),
       tuning_group=(GroupNames.PICKERTUNING)))}

    @flexmethod
    def _get_mixin_objects_gen(cls, inst, target, context, **kwargs):
        gig_objects = set()
        inst_or_cls = inst if inst is not None else cls
        decorator_sim = None
        if inst_or_cls.decorator is None:
            decorator_sim = services.active_sim_info()
        else:
            decorator_sim = (inst_or_cls.get_participant)(participant_type=inst_or_cls.decorator, sim=context.sim, 
             target=target, **kwargs)
        if decorator_sim is None:
            logger.warn('Attempting to get gig-career objects, but the decorator sim participant {} is None.', inst_or_cls.decorator)
            return
        decorator_sim_info = decorator_sim.sim_info if decorator_sim is not None else None
        gig_career = decorator_sim.career_tracker.get_career_by_uid(inst_or_cls.gig_career.guid64)
        if gig_career is None:
            logger.warn('Attempting to get gig-career objects, but the active sim {} does not have career {}', decorator_sim_info, inst_or_cls.gig_career)
            return
        current_gig = gig_career.get_current_gig()
        if current_gig is None:
            logger.warn('Attempting to get gig-career objects, but sim {} has no active gig for career {}', decorator_sim_info, gig_career)
            return
        customer_lot_id = current_gig.get_customer_lot_id()
        if not customer_lot_id:
            logger.warn("Attempting to get gig-career objects, but there is not current let id set on sim {}'s current gig {}.", decorator_sim_info, current_gig)
            return
        object_manager = services.object_manager()
        gig_objects.update([object_manager.get(gig_object_id) for gig_object_id in get_gig_objects_added(customer_lot_id)])
        gig_objects.difference_update([object_manager.get(gig_object_id) for gig_object_id in get_gig_objects_deleted(customer_lot_id)])
        for obj in gig_objects:
            yield obj


class StyleTagObjectPickerMixin(ObjectPickerMixin):
    INSTANCE_TUNABLES = {'style_tag_set': TunableEnumEntry(description='\n            Picked objects will have the tuned style tag.\n            ',
                        tunable_type=(tag.Tag),
                        default=(tag.Tag.INVALID),
                        tuning_group=(GroupNames.PICKERTUNING))}

    @flexmethod
    def _get_mixin_objects_gen(cls, inst, target, context, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        object_manager = services.object_manager()
        for obj in object_manager.get_objects_with_style_tag_gen(inst_or_cls.style_tag_set):
            yield obj