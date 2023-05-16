# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\picker\filtered_object_picker.py
# Compiled at: 2021-11-22 21:29:05
# Size of source mod 2**32: 8525 bytes
from interactions import ParticipantTypeSingle
from interactions.base.picker_interaction import ObjectPickerInteraction, ObjectsInMultipleInventoriesMixin
from interactions.utils.object_definition_or_tags import ObjectDefinitonsOrTagsVariant
from sims4.tuning.tunable import TunableVariant, OptionalTunable, TunableEnumEntry, TunableList, TunableReference
from sims4.tuning.tunable_base import GroupNames
from build_buy import find_objects_in_household_inventory, get_object_in_household_inventory
import event_testing
from event_testing.tests import TunableTestVariant
from objects.script_object import ScriptObject
from event_testing.resolver import InteractionResolver
from sims4.utils import flexmethod
import services, sims4.log, sims
logger = sims4.log.Logger('FilteredObjectPickerInteraction', default_owner='jdimailig')

class FilteredObjectPickerInteraction(ObjectPickerInteraction):
    ON_LOT_ONLY = 'on_lot'
    OFF_LOT_ONLY = 'off_lot'
    ANYWHERE = 'anywhere'
    INSTANCE_TUNABLES = {'object_filter':ObjectDefinitonsOrTagsVariant(description='\n            Filter to use to find an object.\n            ',
       tuning_group=GroupNames.PICKERTUNING), 
     'on_off_lot_requirement':TunableVariant(description='\n            Whether to accept objects on the active lot.\n            ',
       default=ON_LOT_ONLY,
       locked_args={ON_LOT_ONLY: ON_LOT_ONLY, 
      OFF_LOT_ONLY: OFF_LOT_ONLY, 
      ANYWHERE: ANYWHERE},
       tuning_group=GroupNames.PICKERTUNING), 
     'additional_tests':OptionalTunable(description='\n            Additional tests to further trim Objects selected to show up in the picker.\n            ',
       tunable=event_testing.tests.TunableTestSetWithTooltip(tuning_group=(GroupNames.TESTS)),
       tuning_group=GroupNames.PICKERTUNING), 
     'default_selection_tests':OptionalTunable(description='\n            Run tests on items to pre-select in the picker.\n            ',
       tunable=event_testing.tests.TunableTestSetWithTooltip(tuning_group=(GroupNames.TESTS)),
       tuning_group=GroupNames.PICKERTUNING), 
     'use_household_inventory_definition_list':TunableList(description='\n            Check for objects in HH inventory. We need to search by object definition here.\n            ',
       tunable=TunableReference(description='\n                Object Definition of items to be searched for.\n                ',
       manager=(services.definition_manager()),
       pack_safe=True),
       tuning_group=GroupNames.PICKERTUNING), 
     'include_participant_inventory':OptionalTunable(description='\n            if specified, include objects in the specified participants inventory\n            ',
       tunable=TunableEnumEntry(tunable_type=ParticipantTypeSingle,
       default=(ParticipantTypeSingle.Actor)),
       tuning_group=GroupNames.PICKERTUNING)}

    @flexmethod
    def _get_objects_gen(cls, inst, target, context, **kwargs):

        def _matches_lot_requirement(obj):
            if cls.on_off_lot_requirement == cls.ANYWHERE:
                return True
            if cls.on_off_lot_requirement == cls.ON_LOT_ONLY:
                return obj.is_on_active_lot()
            return not obj.is_on_active_lot()

        object_manager = services.object_manager()
        interaction_parameters = {}
        inst_or_cls = inst if inst is not None else cls
        resolver = InteractionResolver(cls, inst, target=target, context=context, **interaction_parameters)
        for obj in object_manager.get_objects_with_filter_gen(cls.object_filter):
            interaction_parameters['picked_item_ids'] = {
             obj.id}
            resolver.interaction_parameters = interaction_parameters
            if inst_or_cls.additional_tests is None or inst_or_cls.additional_tests.run_tests(resolver):
                if _matches_lot_requirement(obj):
                    yield obj

        if inst_or_cls.include_participant_inventory is not None:
            subject = (inst_or_cls.get_participant)(participant=inst_or_cls.include_participant_inventory, sim=context.sim, target=target, **kwargs)
            if subject is not None:
                for obj in subject.inventory_component:
                    if not cls.object_filter.matches(obj):
                        continue
                    interaction_parameters['picked_item_ids'] = {
                     obj.id}
                    resolver.interaction_parameters = interaction_parameters
                    if inst_or_cls.additional_tests is None or inst_or_cls.additional_tests.run_tests(resolver):
                        yield obj

        if len(inst_or_cls.use_household_inventory_definition_list) > 0:
            household_id = inst_or_cls._get_household_id_for_participant(target, context)
            definition_id_list = []
            for obj in inst_or_cls.use_household_inventory_definition_list:
                definition_id_list.append(obj.id)

            for obj_id in find_objects_in_household_inventory(definition_id_list, household_id):
                interaction_parameters['picked_item_ids'] = {
                 obj_id}
                resolver.interaction_parameters = interaction_parameters
                if not inst_or_cls.additional_tests is None:
                    if inst_or_cls.additional_tests.run_tests(resolver):
                        pass
                    obj = object_manager.get(obj_id)
                    obj is None or _matches_lot_requirement(obj) or (yield get_object_in_household_inventory(obj_id, household_id))

    @flexmethod
    def picker_rows_gen(cls, inst, target, context, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        interaction_parameters = {}
        resolver = InteractionResolver(cls, inst, target=target, context=context, **interaction_parameters)
        for obj in inst_or_cls._get_objects_gen(target, context):
            obj_id = obj.id
            interaction_parameters['picked_item_ids'] = {obj_id}
            resolver.interaction_parameters = interaction_parameters
            if inst_or_cls.default_selection_tests is not None and inst_or_cls.default_selection_tests.run_tests(resolver):
                is_selected = True
            else:
                is_selected = False
            row = inst_or_cls.create_row(obj, context=context, target=target, is_selected=is_selected)
            yield row

    @flexmethod
    def _get_household_id_for_participant(cls, inst, target, context, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        inventory_subject = (inst_or_cls.get_participant)(sim=context.sim, target=target, **kwargs)
        if inventory_subject is not None:
            if isinstance(inventory_subject, sims.household.Household):
                return inventory_subject.id
            if isinstance(inventory_subject, ScriptObject):
                if inventory_subject.is_sim:
                    return inventory_subject.sim_info.household_id
                return inventory_subject.get_household_owner_id()

    def _on_picker_selected(self, dialog):
        if dialog.accepted:
            super()._on_picker_selected(dialog)