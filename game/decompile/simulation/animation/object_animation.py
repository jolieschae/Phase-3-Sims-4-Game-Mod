# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\object_animation.py
# Compiled at: 2021-04-02 14:02:06
# Size of source mod 2**32: 12097 bytes
from animation.animation_element import animate_states
from balloon.balloon_utils import create_weighted_random_balloon_request
from balloon.balloon_variant import BalloonVariant
from event_testing.resolver import SingleObjectResolver
from interactions.utils.tested_variant import TunableTestedVariant
from objects.components.types import IDLE_COMPONENT
from objects.slots import get_surface_height_parameter_for_object
from routing.walkstyle.walkstyle_tuning import TunableWalkstyle
from sims4.tuning.instances import TunedInstanceMetaclass
from sims4.tuning.tunable import Tunable, TunableList, OptionalTunable, HasTunableReference, TunableInteractionAsmResourceKey, TunableTuple
from sims4.tuning.tunable_base import SourceQueries
from singletons import DEFAULT
import animation, elements, services, sims4.log, sims4.resources
logger = sims4.log.Logger('ObjectAnimations', default_owner='rmccord')

class ObjectPose(HasTunableReference, metaclass=TunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ANIMATION)):
    INSTANCE_TUNABLES = {'asm':TunableInteractionAsmResourceKey(description='\n            The animation state machine for this pose.\n            ',
       default=None), 
     'state_name':Tunable(description='\n            The animation state name for this pose.\n            ',
       tunable_type=str,
       default=None,
       source_location='asm',
       source_query=SourceQueries.ASMState)}


class ObjectAnimationElement(HasTunableReference, elements.ParentElement, metaclass=TunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ANIMATION)):
    ASM_SOURCE = 'asm_key'
    INSTANCE_TUNABLES = {ASM_SOURCE: TunableInteractionAsmResourceKey(description='\n            The ASM to use.\n            ',
                   default=None,
                   category='asm'), 
     
     'actor_name': Tunable(description='\n            The name of the actor in the ASM.\n            ',
                     tunable_type=str,
                     default=None,
                     source_location=ASM_SOURCE,
                     source_query=(SourceQueries.ASMActorAll)), 
     
     'target_name': OptionalTunable(description='\n            If enabled, some portion of this object animation expects the actor\n            to interact with another object. The object must be set by whatever\n            system uses the ASM. In and of itself, the Idle component never sets\n            this actor.\n            ',
                      tunable=Tunable(tunable_type=str,
                      default=None,
                      source_location=('../' + ASM_SOURCE),
                      source_query=(SourceQueries.ASMActorAll))), 
     
     'initial_state': OptionalTunable(description='\n            The name of the initial state in the ASM you expect your actor to be\n            in when running this AnimationElement. If you do not tune this we\n            will use the entry state which is usually what you want.\n            ',
                        tunable=Tunable(tunable_type=str,
                        default=None,
                        source_location=('../' + ASM_SOURCE),
                        source_query=(SourceQueries.ASMState)),
                        disabled_value=DEFAULT,
                        disabled_name='use_default',
                        enabled_name='custom_state_name'), 
     
     'begin_states': TunableList(description='\n            A list of states to play.\n            ',
                       tunable=str,
                       source_location=ASM_SOURCE,
                       source_query=(SourceQueries.ASMState)), 
     
     'end_states': TunableList(description='\n            A list of states to play after looping.\n            ',
                     tunable=str,
                     source_location=ASM_SOURCE,
                     source_query=(SourceQueries.ASMState)), 
     
     'balloon_tuning': TunableTuple(balloons=TunableList(description='\n                A list of possible balloons to show.\n                ',
                         tunable=(BalloonVariant.TunableFactory())),
                         balloon_delay=Tunable(description='\n                The number of seconds after the start of the animation\n                to trigger the balloon. A negative number will count backwards\n                from the end of the animation.\n                ',
                         tunable_type=float,
                         default=0),
                         balloon_delay_random_offset=Tunable(description='\n                A random time offset added to balloon requests.\n                Will always offset the delay time later and requires the delay\n                time be set to a number. A value of 0 has no randomization.\n                ',
                         tunable_type=float,
                         default=0)), 
     
     'repeat': Tunable(description='\n            If this is checked, then the begin_states will loop until the\n            controlling sequence (e.g. state change on idle component) ends. \n            At that point, end_states will play.\n            \n            This tunable allows you to create looping one-shot states. The\n            effects of this tunable on already looping states is undefined.\n            ',
                 tunable_type=bool,
                 default=False), 
     
     'use_surface_height': Tunable(description='\n            If checked, the asm will be provided with the surfaceHeight\n            global parameter, which uses slot height tuning to resolve the \n            height of the target object to a parameter value. \n            ',
                             tunable_type=bool,
                             default=False), 
     
     'include_object_children_in_fade': Tunable(description="\n            If True, fade events on the object will apply to the object's\n            children. If False, only the object is affected by the fade event.\n            ",
                                          tunable_type=bool,
                                          default=False), 
     
     'animation_walkstyle_override': OptionalTunable(description='\n            If enabled, we will send this walkstyle for the walkstyle and\n            walkstyle_override parameter on the actor in the ASM.\n            ',
                                       tunable=TunableTestedVariant(description='\n                Specify the single walkstyle to use, or a suite of tests\n                to decide which walkstyle to use for the animation.\n                ',
                                       tunable_type=TunableWalkstyle(description='\n                    The walkstyle override to use.\n                    '),
                                       is_noncallable_type=True))}

    def __init__(self, owner, use_asm_cache=True, target=None, use_surface_height=False, **animate_kwargs):
        super().__init__()
        self.owner = owner
        self.target = target
        self.animate_kwargs = animate_kwargs
        self._use_asm_cache = use_asm_cache
        self._use_surface_height = use_surface_height

    @classmethod
    def append_to_arb(cls, asm, arb):
        for state_name in cls.begin_states:
            asm.request(state_name, arb)

    @classmethod
    def append_exit_to_arb(cls, asm, arb):
        for state_name in cls.end_states:
            asm.request(state_name, arb)

    def set_walkstyle_asm_parameter(self, asm):
        if self.animation_walkstyle_override is None:
            return
        resolver = SingleObjectResolver(self.owner)

        def set_asm_param(walkstyle, walkstyle_actor, walkstyle_actor_name):
            if walkstyle_actor is None or walkstyle is None or walkstyle_actor_name is None:
                return
            tested_result = walkstyle(resolver=resolver)
            if tested_result is None:
                return
            asm.set_actor_parameter(walkstyle_actor_name, walkstyle_actor, 'walkstyle', tested_result.animation_parameter)
            asm.set_actor_parameter(walkstyle_actor_name, walkstyle_actor, 'walkstyle_override', tested_result)

        set_asm_param(self.animation_walkstyle_override, self.owner, self.actor_name)

    def get_asm(self, use_cache=True, **kwargs):
        idle_component = self.owner.get_component(IDLE_COMPONENT)
        if idle_component is None:
            logger.error('Trying to setup an object animation {}, {} on an object {} with no Idle Component.', self, self.asm_key, self.owner)
            return
        asm = (idle_component.get_asm)(self.asm_key, self.actor_name, use_cache=self._use_asm_cache and use_cache, **kwargs)
        if self.target is not None:
            if self.target_name is not None:
                asm.add_potentially_virtual_actor(self.actor_name, self.owner, self.target_name, self.target)
            if self.use_surface_height:
                surface_height = get_surface_height_parameter_for_object(self.target)
                asm.set_parameter('surfaceHeight', surface_height)
        parent_obj = self.owner.parent
        if parent_obj is not None:
            if parent_obj.is_part:
                if parent_obj.subroot_index is not None:
                    asm.set_actor_parameter(self.actor_name, self.owner, 'subrootFrom', parent_obj.part_suffix)
        return asm

    def get_balloon_request(self):
        resolver = SingleObjectResolver(self.owner)
        return create_weighted_random_balloon_request((self.balloon_tuning.balloons), (self.owner), resolver, delay=(self.balloon_tuning.balloon_delay),
          delay_randomization=(self.balloon_tuning.balloon_delay_random_offset))

    def _run(self, timeline):
        if self.asm_key is None:
            return True
        asm = self.get_asm()
        if asm is None:
            return False
        asm.context.include_object_children_in_fade = self.include_object_children_in_fade
        balloon_request = self.get_balloon_request()
        self.set_walkstyle_asm_parameter(asm)
        return timeline.run_child(animate_states(asm,
 self.begin_states, self.end_states, repeat_begin_states=self.repeat, 
         balloon_requests=(balloon_request,) if balloon_request is not None else None, **self.animate_kwargs))