# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\parts\part_data.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 18250 bytes
import enum, postures
from collections import OrderedDict
import copy, services
from animation.tunable_animation_overrides import TunableAnimationOverrides
from objects.components.state_references import TunableStateValueReference
from objects.part import ObjectPart
from sims4.localization import TunableLocalizedString
from sims4.resources import Types
from sims4.tuning.geometric import TunableVector2
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableList, OptionalTunable, Tunable, TunableMapping, TunableEnumEntry, TunableEnumFlags, TunableTuple, TunableSet, TunableReference, TunableRange
from sims4.tuning.tunable_base import TunableBase
import sims4.log
from sims4.tuning.tunable_hash import TunableStringHash32
from sims4.utils import constproperty
from singletons import EMPTY_SET
logger = sims4.log.Logger('Parts')

class PartAdjacency(enum.Int):
    IDENTITY = 0
    LEFT = 1
    RIGHT = 2


class _PartData(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'part_definition':ObjectPart.TunableReference(description='\n            The part definition associated with this part instance.\n            \n            The part definition defines supported postures and interactions,\n            disallowed buffs and portal data.\n            ',
       pack_safe=True), 
     'disabling_states':TunableList(description='\n            A list of state values which, if active on this object, will\n            disable this part.\n            ',
       tunable=TunableStateValueReference(pack_safe=True)), 
     'disabling_model_suite_indices':TunableList(description='\n            A list of model suite "state indices" which, if active on\n            this object, will disable this part.\n            ',
       tunable=TunableRange(tunable_type=int,
       default=0,
       minimum=0)), 
     'adjacent_parts':TunableList(description='\n            The parts that are adjacent to this part. You must reference a part\n            that is tuned in this mapping.\n            \n            An empty list indicates that no part is adjacent to this part.\n            ',
       tunable=Tunable(tunable_type=str,
       default=None),
       unique_entries=True), 
     'overlapping_parts':TunableList(description='\n            The parts that are unusable when this part is in use. You must\n            reference a part that is tuned in this mapping.\n            ',
       tunable=Tunable(tunable_type=str,
       default=None),
       unique_entries=True), 
     'parts_to_transition_costs_modifier':TunableMapping(description='\n            The costs modifier of transition between parts of an object. \n            This modifier will be applied in addition to module tuning \n            INNER_NON_MOBILE_TO_NON_MOBILE_COINCIDENT_COST or \n            INNER_NON_MOBILE_TO_NON_MOBILE_COST.\n            It is applied only between non-mobile to non-mobile posture transition. \n            Nice to have it if you want to modify transition costs between parts of an object.\n            \n            Warning: the calculated transition cost will be clamped to \n            MIN_INNER_NON_MOBILE_TO_NON_MOBILE_COST\n            if this modifier makes the transition cost valued zero or negative.\n            ',
       key_name='target part',
       key_type=Tunable(description='\n                The reference string to the target part.\n                ',
       tunable_type=str,
       default=None),
       value_name='modifier',
       value_type=Tunable(description='\n                The cost modifier of transition, default to 0. positive\n                if you want greater transition cost, negative it you\n                want smaller transition cost.\n                ',
       tunable_type=float,
       default=0)), 
     'subroot_index':OptionalTunable(description='\n            If enabled, this part will have a subroot index associated with it.\n            This will affect the way Sims animate, i.e. they will animate\n            relative to the position of the part, not relative to the object.\n            ',
       tunable=Tunable(description='\n                The subroot suffix associated with this part.\n                ',
       tunable_type=int,
       default=0,
       needs_tuning=False),
       enabled_by_default=True), 
     'anim_overrides':TunableAnimationOverrides(description='\n            Animation overrides for this part.\n            '), 
     'is_mirrored':OptionalTunable(description='\n            Specify whether or not solo animations played on this part\n            should be mirrored or not.\n            ',
       tunable=Tunable(description='\n                If checked, mirroring is enabled. If unchecked,\n                mirroring is disabled.\n                ',
       tunable_type=bool,
       default=False)), 
     'forward_direction_for_picking':TunableVector2(description="\n            When you click on the object this part belongs to, this offset will\n            be applied to this part when determining which part is closest to\n            where you clicked.\n            \n            By default, the object's forward vector will be used. It should only\n            be necessary to tune this value if multiple parts overlap at the\n            same location (e.g. the single bed).\n            ",
       default=TunableVector2.DEFAULT_Z,
       x_axis_name='x',
       y_axis_name='z'), 
     'disable_sim_aop_forwarding':Tunable(description='\n            If checked, Sims using this specific part will never forward\n            AOPs.\n            ',
       tunable_type=bool,
       default=False), 
     'disable_child_aop_forwarding':Tunable(description='\n            If checked, objects parented to this specific part will\n            never forward AOPs.\n            ',
       tunable_type=bool,
       default=False), 
     'restrict_autonomy_preference':Tunable(description='\n            If checked, this specific part can be used for use only autonomy preference\n            restriction.\n            ',
       tunable_type=bool,
       default=False), 
     'name':OptionalTunable(description='\n            Name of this part.  For use if the part name needs to be surfaced\n            to the player.  (i.e. when assigning sim to specific side of bed.)\n            ',
       tunable=TunableLocalizedString()), 
     'additional_part_posture_cost':Tunable(description='\n            A float that is added to the total cost of postures targeting this \n            part. A positive number will make this part more costly during \n            posture scoring, while a negative number will make this part more \n            preferable.\n            ',
       tunable_type=float,
       default=0.0), 
     'current_body_target_cost_bonus':Tunable(description="\n            A float that is added to the cost of transitioning to this part\n            if the sim's body target is currently this part. Negative numbers \n            will make this part more preferable, while positive numbers will\n            make it less preferable.\n            ",
       tunable_type=float,
       default=0.0), 
     'posture_transition_target_tag':OptionalTunable(description='\n            If enabled, a tag to apply to this part so that it is taken into\n            account for posture transition preference scoring.  For example, \n            you could tune this part to be a DINING_SURFACE.  Any SI that is \n            set up to have posture preference scoring can override the score \n            for any objects/parts that are tagged with DINING_SURFACE.\n    \n            For a more detailed description of how posture preference scoring\n            works, see the posture_target_preference tunable field description\n            in SuperInteraction.\n            ',
       tunable=TunableEnumEntry(tunable_type=(postures.PostureTransitionTargetPreferenceTag),
       default=(postures.PostureTransitionTargetPreferenceTag.INVALID)))}

    @constproperty
    def is_old_part_data():
        return False


class TunablePartDataMapping(TunableMapping):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, key_type=Tunable(description='\n                A unique, arbitrary identifier for this part. Use this to define\n                adjacent and overlapping parts.\n                ',
  tunable_type=str,
  default=None), 
         value_type=_PartData.TunableFactory(), **kwargs)

    @property
    def export_class(self):
        return 'TunableMapping'

    def load_etree_node(self, node, source, expect_error):
        value = super().load_etree_node(node, source, expect_error)
        value = OrderedDict(sorted(value.items()))
        index_map = {k: i for i, k in enumerate(value)}
        values = []
        for k, v in value.items():
            v = copy.copy(v)
            adjacent_parts = tuple((index_map[i] for i in v.adjacent_parts if i in index_map))
            setattr(v, 'adjacent_parts', adjacent_parts)
            overlapping_parts = tuple((index_map[i] for i in v.overlapping_parts if i in index_map))
            setattr(v, 'overlapping_parts', overlapping_parts)
            values.append(v)

        return tuple(values)

    def invoke_callback(self, instance_class, tunable_name, source, value):
        if not self._has_callback:
            return
        TunableBase.invoke_callback(self, instance_class, tunable_name, source, value)
        if value is not None:
            template = self._template.tunable_items['value']
            for tuned_value in value:
                template.invoke_callback(instance_class, tunable_name, source, tuned_value)

    def invoke_verify_tunable_callback(self, instance_class, tunable_name, source, value):
        if not self._has_verify_tunable_callback:
            return
        TunableBase.invoke_verify_tunable_callback(self, instance_class, tunable_name, source, value)
        if value is not None:
            template = self._template.tunable_items['value']
            for tuned_value in value:
                template.invoke_verify_tunable_callback(instance_class, tunable_name, source, tuned_value)


class DynamicPartData(_PartData):
    FACTORY_TUNABLES = {'adjacent_parts_by_direction':TunableMapping(description='\n            Parts, defined by their direction relative to the piece providing this part, that are adjacent.\n            This is used to dynamically define adjacent parts of an object that consists of modular pieces.\n            \n            Dynamic parts can not be considered adjacent in gameplay unless EXPLICITLY defined here.\n            ',
       key_type=TunableEnumEntry(description='\n                The adjacency of the pieces relative to the current piece.\n                e.g. a Sit is adjacent to Sit to the left and right of it to support scoots. \n                Sit is also adjacent to a NapLeft or NapRight within the same piece. \n                ',
       tunable_type=PartAdjacency,
       default=(PartAdjacency.IDENTITY)),
       value_type=TunableSet(description='\n                The keys that are adjacent in this direction.\n                ',
       tunable=TunableStringHash32(description='\n                    The key that the part must have.\n                    '))), 
     'overlapping_parts_by_direction':TunableMapping(description='\n            Parts, defined by their direction relative to the piece providing this part, that overlap with this part.\n            This is used to dynamically define overlapping parts of an object that consists of modular pieces.\n            ',
       key_type=TunableEnumEntry(description='\n                The adjacency of the pieces relative to the current piece.\n                e.g. a Sit will overlap with any other part that needs to use use the part on which it is situated.\n                ',
       tunable_type=PartAdjacency,
       default=(PartAdjacency.IDENTITY),
       invalid_enums=(
      PartAdjacency.IDENTITY,)),
       value_type=TunableTuple(distant_overlaps=TunableSet(description='\n                    In some cases, parts may be further away from each other, this allows an additional overlap of parts\n                    that are not directly adjacent to each other.\n                    \n                    e.g. \n                    - NapRight_0 will take up the spot to the right of it.\n                    - NapLeft_2 will take up the spot to the left of it.\n                    There is no guarantee that there is a part to the direct right of NapRight_0, nor a part\n                    directly to the left of NapLeft_2 that can be mutually reserved. (corner pieces) \n                    This allows us to tune parts that are 2 units away from it in adjacency. \n                    ',
       tunable=(TunableStringHash32())),
       overlapping_parts=TunableSet(description='\n                    The keys that are overlapping in this direction.\n                    ',
       tunable=TunableStringHash32(description='\n                        The key that the part must have.\n                        ')))), 
     'required_adjacencies':TunableSet(description='\n            In order for this part to exist, it must have a pieces all of the provided directions.\n            ',
       tunable=TunableEnumEntry(tunable_type=PartAdjacency,
       default=(PartAdjacency.IDENTITY),
       invalid_enums=(
      PartAdjacency.IDENTITY,))), 
     'disabling_adjacencies':TunableList(description='\n            This part is not generated if adjacencies matching any of the provided adjacency sets exist. \n            ',
       tunable=TunableSet(description="\n                A set of adjacencies that cannot exist in order for this part to be created.\n                e.g. a corner sofa piece cannot have a 'Sit' part if it has two pieces connected to it since we don't\n                support sitting/scooting to the corner. \n                ",
       tunable=TunableEnumEntry(tunable_type=PartAdjacency,
       default=(PartAdjacency.IDENTITY),
       invalid_enums=(
      PartAdjacency.IDENTITY,)))), 
     'provided_container_super_affordances':TunableList(description="\n            When this part is generated for its container object, these affordances will be available on it.\n            \n            For example, sectional sofas may be built in such a way that having a part a Sim can nap on just does\n            not exist.  So for sectional sofas, nap related affordances would be defined here for nap-providing parts\n            rather than directly on the sectional sofa object's super affordance tuning.\n            ",
       tunable=TunableReference(description='\n                A super affordance on this object that can be run during preroll.\n                ',
       manager=(services.get_instance_manager(Types.INTERACTION)),
       class_restrictions=('SuperInteraction', ),
       pack_safe=True),
       unique_entries=True), 
     'locked_args':{'adjacent_parts':EMPTY_SET, 
      'overlapping_parts':EMPTY_SET}}