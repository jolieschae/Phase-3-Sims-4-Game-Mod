# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\definition_picker_interaction.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 11678 bytes
import build_buy
from distributor.shared_messages import IconInfoData
from interactions.base.picker_interaction import ObjectPickerInteraction, DefinitionsFromTags, DefinitionsExplicit, DefinitionsRandom, DefinitionsTested
from interactions.context import InteractionContext
from interactions.utils.loot import LootActions
from objects.auto_pick import AutoPickRandom
from objects.object_creation import ObjectCreationMixin, CreationDataBase
from objects.object_tests import DefinitionIdFilter
from sims4.localization import LocalizationHelperTuning, TunableLocalizedStringFactory
from sims4.tuning.tunable import TunableVariant, TunableList, TunableTuple, TunableMapping, TunableReference, HasTunableSingletonFactory, AutoFactoryInit, HasTunableFactory
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
from singletons import DEFAULT
from traits.traits import Trait
from ui.ui_dialog_picker import ObjectPickerRow
import services, sims4.log
logger = sims4.log.Logger('DefinitionPicker', default_owner='rmccord')

class ObjectDefinitionPickerVariant(TunableVariant):

    def __init__(self, **kwargs):
        (super().__init__)(all_items=DefinitionsFromTags.TunableFactory(description='\n                Look through all the items and populate any with these tags.\n\n                This should be accompanied with specific filtering tags in\n                Object Populate Filter to get a good result.\n                '), 
         specific_items=DefinitionsExplicit.TunableFactory(description='\n                A list of specific items that is populated in this\n                dialog.\n                '), 
         random_items=DefinitionsRandom.TunableFactory(description='\n                Randomly selects items based on a weighted list.\n                '), 
         tested_items=DefinitionsTested.TunableFactory(description='\n                Test items that are able to be displayed within the picker.\n                '), 
         default='all_items', **kwargs)


class ObjectDefinitionPickerInteraction(ObjectPickerInteraction):
    INSTANCE_TUNABLES = {'object_tags_or_definition':ObjectDefinitionPickerVariant(tuning_group=GroupNames.PICKERTUNING), 
     'additional_object_tags_or_definition':TunableList(description='\n            Like Object Tags or Definition, but is a list to allow for specifying more object tags\n            and definitions.\n            ',
       tunable=ObjectDefinitionPickerVariant(),
       tuning_group=GroupNames.PICKERTUNING), 
     'definition_to_loot':TunableList(description='\n            Does a definition test to see loot should be applied to subjects.\n            ',
       tunable=TunableTuple(description='\n                Loot to apply if definition id passes.\n                ',
       definition_id_test=DefinitionIdFilter.TunableFactory(description='\n                    Definition to test for.\n                    '),
       loot_to_apply=LootActions.TunableReference(description='\n                    Loot to apply.\n                    ')),
       tuning_group=GroupNames.PICKERTUNING)}

    @classmethod
    def has_valid_choice(cls, target, context, **kwargs):
        if (cls.object_tags_or_definition.has_choices)(cls, target=target, context=context, sim=context.sim, **kwargs):
            return True
        for added_definitions in cls.additional_object_tags_or_definition:
            if (added_definitions.has_choices)(cls, target=target, context=context, sim=context.sim, **kwargs):
                return True

        return False

    @flexmethod
    def _get_objects_gen(cls, inst, *args, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        yield from inst_or_cls.object_tags_or_definition.get_items_gen(inst_or_cls)
        for added_definitions in inst_or_cls.additional_object_tags_or_definition:
            yield from added_definitions.get_items_gen(inst_or_cls)

        if False:
            yield None

    @flexmethod
    def create_row(cls, inst, row_obj, context=DEFAULT, target=DEFAULT):
        inst_or_cls = inst if inst is not None else cls
        object_name_override = inst_or_cls.object_name_override
        object_name = LocalizationHelperTuning.get_object_name(row_obj) if object_name_override is None else object_name_override.get_description(row_obj, context=context, target=target, interaction=inst_or_cls)
        icon_info = IconInfoData(obj_def_id=(row_obj.id), obj_geo_hash=(row_obj.thumbnail_geo_state_hash),
          obj_material_hash=(row_obj.material_variant))
        tag_list = build_buy.get_object_all_tags(row_obj.definition.id)
        row = ObjectPickerRow(object_id=(row_obj.id), def_id=(row_obj.id),
          icon_info=icon_info,
          tag=row_obj,
          tag_list=tag_list,
          name=object_name)
        inst_or_cls._test_continuation(row, context=context, target=target)
        return row

    def on_choice_selected(self, choice_tag, **kwargs):
        if choice_tag is None:
            return
        resolver = self.get_resolver()
        for id_loot_test in self.definition_to_loot:
            if id_loot_test.definition_id_test(choice_tag):
                id_loot_test.loot_to_apply.apply_to_resolver(resolver)

        (super().on_choice_selected)(choice_tag, **kwargs)


class _DefinitionPickerCreationData(CreationDataBase):

    def __init__(self):
        self._definition = None

    def set_definition(self, definition):
        self._definition = definition

    @property
    def definition(self):
        return self._definition

    def get_definition(self, *_, **__):
        return self._definition


class CreateObjectDefinitionPickerInteraction(ObjectCreationMixin, ObjectDefinitionPickerInteraction):
    REMOVE_INSTANCE_TUNABLES = ('creation_data', )

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.creation_data = _DefinitionPickerCreationData()

    def on_choice_selected(self, choice_tag, **kwargs):
        if choice_tag is None:
            return
        self.creation_data.set_definition(choice_tag)
        created_object = self.create_object(self.get_resolver())
        if created_object is None:
            logger.error('{} failed to create object from picked definition {}.', self, self.creation_data.definition)
        self.context.create_target_override = created_object
        for id_loot_test in self.definition_to_loot:
            if id_loot_test.definition_id_test(choice_tag):
                id_loot_test.loot_to_apply.apply_to_resolver(self.resolver)

        (super().on_choice_selected)(choice_tag, **kwargs)

    def _run_interaction_gen(self, timeline):
        if self.context.source != InteractionContext.SOURCE_PIE_MENU or self.auto_pick:
            choices = list(self._get_objects_gen(self.target, self.context))
            if choices:
                if self.auto_pick:
                    obj = self.auto_pick.perform_auto_pick(choices)
                else:
                    obj = AutoPickRandom.perform_auto_pick(choices)
                self.on_choice_selected(obj)
                return True
            return False
        yield from super()._run_interaction_gen(timeline)
        if False:
            yield None


class TraitToDefinitionPickerInteraction(ObjectDefinitionPickerInteraction):
    INSTANCE_TUNABLES = {'trait_to_definition_id':TunableMapping(description='\n            Backward mapping of trait to what umbrella the sim carries\n            ',
       key_type=Trait.TunableReference(description='\n                Trait to look for\n                '),
       value_type=TunableReference(description='\n                The object must have this definition.\n                ',
       manager=(services.definition_manager()))), 
     'disabled_toolip':TunableLocalizedStringFactory(description='\n            Tooltip that displays if the sim currently has the trait in the mapping.\n            ')}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._selected_definition_id = None

    def _create_dialog(self, owner, target_sim=None, target=None, **kwargs):
        traits_to_find = self.trait_to_definition_id.keys()
        for trait in traits_to_find:
            if not owner.has_trait(trait):
                continue
            self._selected_definition_id = self.trait_to_definition_id[trait]
            break

        return (super()._create_dialog)(owner, target_sim=target_sim, target=target, **kwargs)

    @flexmethod
    def create_row(cls, inst, row_obj, context=DEFAULT, target=DEFAULT):
        inst_or_cls = inst if inst is not None else cls
        is_disabled = inst_or_cls._selected_definition_id is not None and row_obj.id == inst_or_cls._selected_definition_id.id
        icon_info = IconInfoData(obj_def_id=(row_obj.id), obj_geo_hash=(row_obj.thumbnail_geo_state_hash),
          obj_material_hash=(row_obj.material_variant))
        row = ObjectPickerRow(object_id=(row_obj.id), def_id=(row_obj.id),
          icon_info=icon_info,
          tag=row_obj,
          is_enable=(not is_disabled),
          row_tooltip=(inst_or_cls.disabled_toolip if is_disabled else None),
          name=(LocalizationHelperTuning.get_object_name(row_obj)))
        inst_or_cls._test_continuation(row, context=context, target=target)
        return row