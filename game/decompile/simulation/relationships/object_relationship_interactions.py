# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relationships\object_relationship_interactions.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 6621 bytes
from interactions.aop import AffordanceObjectPair
from interactions.base.immediate_interaction import ImmediateSuperInteraction
from interactions.context import InteractionContext, InteractionSource
from interactions.priority import Priority
from relationships.relationship_track import ObjectRelationshipTrack
from sims4.localization import LocalizationHelperTuning, TunableLocalizedStringFactory
from sims4.tuning.tunable import TunableMapping, TunableReference, TunableTuple, OptionalTunable
from sims4.utils import flexmethod
from singletons import DEFAULT
import services, sims4
logger = sims4.log.Logger('Relationship', default_owner='madang')

class ObjectRelationshipInteraction(ImmediateSuperInteraction):
    INSTANCE_TUNABLES = {'object_variant_mapping':TunableMapping(description='\n            Map of the possible object relationship tracks, each representing\n            an object, and the associated interaction that will be pushed when \n            selected.\n            ',
       key_type=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
       class_restrictions='ObjectRelationshipTrack',
       pack_safe=True),
       value_type=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       class_restrictions='SuperInteraction',
       pack_safe=True)), 
     'custom_name_string_wrapper':OptionalTunable(description='\n            If tuned, if the object relationship name has been set\n            with the name component, then the display name of the interaction\n            will be wrapped into this string.\n            \n            It should be written like this, with the object name\n            token indexed at 0:\n            "Summon 0.String" \n            ',
       tunable=TunableLocalizedStringFactory())}

    def __init__(self, aop, context, track=None, **kwargs):
        (super().__init__)(aop, context, **kwargs)
        self.rel_track = track

    @flexmethod
    def _get_name(cls, inst, target=DEFAULT, context=DEFAULT, track=None, **interaction_parameters):
        if track is None:
            return inst.create_localized_string(inst.display_name)
            tag_set = None
            if track in ObjectRelationshipTrack.OBJECT_BASED_FRIENDSHIP_TRACKS:
                tag_set = ObjectRelationshipTrack.OBJECT_BASED_FRIENDSHIP_TRACKS[track]
        elif tag_set is not None:
            relationship_service = services.relationship_service()
            relationship = relationship_service.get_object_relationship(context.sim.id, tag_set)
            if relationship is not None:
                object_name = relationship.get_object_rel_name()
                if object_name:
                    if cls.custom_name_string_wrapper is not None:
                        return cls.custom_name_string_wrapper(LocalizationHelperTuning.get_raw_text(object_name))
                    return LocalizationHelperTuning.get_raw_text(object_name)
        if track in cls.object_variant_mapping:
            return cls.create_localized_string((cls.object_variant_mapping[track].display_name), context=context, target=target)
        return inst.create_localized_string(inst.display_name)

    @classmethod
    def potential_interactions(cls, target, context, from_inventory_to_owner=False, **kwargs):
        if not cls.allow_autonomous:
            if context.source == InteractionSource.AUTONOMY:
                return ()
        for rel_track, affordance in cls.object_variant_mapping.items():
            tag_set = None
            if rel_track in ObjectRelationshipTrack.OBJECT_BASED_FRIENDSHIP_TRACKS:
                tag_set = ObjectRelationshipTrack.OBJECT_BASED_FRIENDSHIP_TRACKS[rel_track]
            if tag_set is not None:
                result = affordance.test(target=target, context=context)
                if result or result.tooltip is not None:
                    yield AffordanceObjectPair(cls, target, cls, None, track=rel_track,
                      from_inventory_to_owner=from_inventory_to_owner)

    @flexmethod
    def test(cls, inst, target=DEFAULT, context=DEFAULT, super_interaction=None, skip_safe_tests=False, **interaction_parameters):
        rel_track = interaction_parameters.get('track')
        if rel_track is not None:
            if rel_track in cls.object_variant_mapping:
                affordance = cls.object_variant_mapping[rel_track].affordance
                if affordance is not None:
                    return affordance.test(target=target, context=context)

    def _run_interaction_gen(self, timeline):
        if self.rel_track is None:
            return False
        context = InteractionContext(self.sim, InteractionContext.SOURCE_PIE_MENU, Priority.High)
        result = self.sim.push_super_affordance(self.object_variant_mapping[self.rel_track], self.target, context)
        return True
        if False:
            yield None