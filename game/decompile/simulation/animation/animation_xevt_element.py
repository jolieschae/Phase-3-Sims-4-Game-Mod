# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\animation_xevt_element.py
# Compiled at: 2021-04-02 13:13:53
# Size of source mod 2**32: 8861 bytes
import services, sims4
from animation.animation_element import register_balloon_requests
from animation.arb import Arb
from animation.arb_element import distribute_arb_element
from animation.object_animation import ObjectAnimationElement
from event_testing.resolver import SingleObjectResolver
from interactions import ParticipantType
from interactions.utils.animation_reference import TunableAnimationReference
from interactions.utils.interaction_elements import XevtTriggeredElement
from objects.components.types import IDLE_COMPONENT
from sims4.random import weighted_random_item
from sims4.tuning.tunable import TunableEnumEntry, TunableList, TunableTuple, TunableReference
from tunable_multiplier import TunableMultiplier
logger = sims4.log.Logger('AnimationXevtElement', default_owner='miking')

class AnimationXevtElementBase(XevtTriggeredElement):
    FACTORY_TUNABLES = {'participant': TunableEnumEntry(description='\n            The participant on which to play the animation.\n            ',
                      tunable_type=ParticipantType,
                      default=(ParticipantType.Actor))}

    def _choose_animation_element(self, resolver):
        weighted_animations = [(entry.weight.get_multiplier(resolver), (entry.animation_element, entry.loots)) for entry in self.animations]
        if not weighted_animations:
            return
        animation_element, loots = weighted_random_item(weighted_animations)
        return (animation_element, loots)

    def _construct_animation_element(self, anim_element_factory, participant):
        raise NotImplementedError

    def _setup_asm(self, animation_element, participant, asm):
        asm.set_actor(animation_element.actor_name, participant)

    def _do_behavior(self):
        participant = self.interaction.get_participant(self.participant)
        if participant is None:
            logger.error('Got a None participant trying to run an AnimationXevtElement.')
            return False
        resolver = SingleObjectResolver(participant)
        animation_element, loots = self._choose_animation_element(resolver)
        if animation_element is None:
            logger.error('Failed to select an animation_element in AnimationXevtElement.')
            return False
        animation = self._construct_animation_element(animation_element, participant)
        if animation is None:
            logger.error('Failed to construct animation {} in AnimationXevtElement.', animation_element)
            return False
        asm = animation.get_asm()
        if asm is None:
            logger.warn('Unable to get a valid ASM for Xevt ({}) for {}.', animation_element, self.interaction)
            return False
        self._setup_asm(animation, participant, asm)
        arb = Arb()
        animation_element.append_to_arb(asm, arb)
        animation_element.append_exit_to_arb(asm, arb)
        distribute_arb_element(arb)
        resolver = self.interaction.get_resolver()
        for loot in loots:
            loot.apply_to_resolver(resolver)

        return True


class AnimationXevtElement(AnimationXevtElementBase):
    FACTORY_TUNABLES = {'animations': TunableList(description='\n            A tunable list of weighted animations. When choosing an animation\n            one of the modifiers in this list will be applied. The weight\n            will be used to run a weighted random selection.\n            ',
                     tunable=TunableTuple(description='\n                A Modifier to apply and weight for the weighted random \n                selection.\n                ',
                     animation_element=TunableAnimationReference(description='\n                    The animation to play during the XEvent.\n                    ',
                     callback=None,
                     class_restrictions=('AnimationElement', 'AnimationElementSet')),
                     loots=TunableList(description='\n                    A list of loots applied when this animation is chosen to be \n                    played during an XEvent.\n                    ',
                     tunable=TunableReference(description='\n                        A loot to be applied when this animation is chosen to be \n                        played during an XEvent.\n                        ',
                     manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
                     class_restrictions=('LootActions', 'RandomWeightedLoot'))),
                     weight=TunableMultiplier.TunableFactory(description='\n                    A weight with testable multipliers that is used to \n                    determine how likely this entry is to be picked when \n                    selecting randomly.\n                    ')))}

    def _construct_animation_element(self, anim_element_factory, _):
        return anim_element_factory(self.interaction)


class ObjectAnimationXevtElement(AnimationXevtElementBase):
    FACTORY_TUNABLES = {'animations': TunableList(description='\n            A tunable list of weighted animations. When choosing an animation\n            one of the modifiers in this list will be applied. The weight\n            will be used to run a weighted random selection.\n            ',
                     tunable=TunableTuple(description='\n                A Modifier to apply and weight for the weighted random \n                selection.\n                ',
                     animation_element=ObjectAnimationElement.TunableReference(description='\n                    The animation to play during the XEvent.\n                    Note: Not all fields tunable on ObjectAnimationElements will be utilized here.\n                    Talk to a GPE to find out which fields are supported.\n                    '),
                     loots=TunableList(description='\n                    A list of loots applied when this animation is chosen to be \n                    played during an XEvent.\n                    ',
                     tunable=TunableReference(description='\n                        A loot to be applied when this animation is chosen to be \n                        played during an XEvent.\n                        ',
                     manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
                     class_restrictions=('LootActions', 'RandomWeightedLoot'))),
                     weight=TunableMultiplier.TunableFactory(description='\n                    A weight with testable multipliers that is used to \n                    determine how likely this entry is to be picked when \n                    selecting randomly.\n                    ')))}

    def _construct_animation_element(self, anim_element_factory, participant):
        if not participant.has_component(IDLE_COMPONENT):
            return
        return anim_element_factory(participant)

    def _setup_asm(self, animation_element, participant, asm):
        super()._setup_asm(animation_element, participant, asm)
        balloon_request = animation_element.get_balloon_request()
        if balloon_request is not None:
            register_balloon_requests(asm, (balloon_request,))