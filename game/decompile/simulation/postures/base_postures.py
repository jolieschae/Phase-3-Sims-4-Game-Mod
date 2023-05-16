# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\postures\base_postures.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 23754 bytes
from contextlib import contextmanager
import collections
from animation.posture_manifest import AnimationParticipant
from animation import ClipEventType
from carry.carry_elements import CarryElementHelper
from carry.carry_utils import SCRIPT_EVENT_ID_START_CARRY
from element_utils import do_all
from event_testing.results import TestResult
from interactions.constraints import Constraint
from interactions.utils.object_definition_or_tags import ObjectDefinitonsOrTagsVariant
from postures import PostureTrack
from postures.posture import Posture
from postures.posture_animation_data import AnimationDataByActorSpecies, _TunableAnimationData
from postures.posture_state_spec import create_body_posture_state_spec
from routing.walkstyle.walkstyle_tuning import TunableWalkstyle
from sims.sim_info_types import Age
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import Tunable, OptionalTunable, TunableReference, TunableList, TunableMapping, TunableEnumEntry, TunableTuple
from sims4.tuning.tunable_base import GroupNames, SourceQueries
from sims4.utils import classproperty, constproperty, flexmethod
from singletons import DEFAULT
import services, sims4.log, sims4.reload
logger = sims4.log.Logger('BasePosture')
with sims4.reload.protected(globals()):
    _sims_that_create_puppet_postures = collections.Counter()

@contextmanager
def create_puppet_postures(sim):
    count = _sims_that_create_puppet_postures[sim]
    count += 1
    _sims_that_create_puppet_postures[sim] = count
    try:
        yield
    finally:
        count = _sims_that_create_puppet_postures[sim]
        count -= 1
        if count < 0:
            raise AssertionError('Bookkeeping error in create_puppet_postures for {}'.format(sim))
        elif count == 0:
            del _sims_that_create_puppet_postures[sim]
        else:
            _sims_that_create_puppet_postures[sim] = count


class MultiSimPosture(Posture):
    INSTANCE_TUNABLES = {'_animation_data':AnimationDataByActorSpecies.TunableFactory(animation_data_options={'_actor_b_param_name':Tunable(description="\n                    The actor for this posture's target Sim. Usually, this is\n                    'y' and should not be modified.\n                    ",
        tunable_type=str,
        source_location=_TunableAnimationData.ASM_SOURCE,
        source_query=SourceQueries.ASMActorSim,
        default='y'), 
      'locked_args':{'actor_param_name_list': ('_actor_param_name', '_actor_b_param_name')}},
       tuning_group=GroupNames.ANIMATION), 
     '_actor_required_part_definition':OptionalTunable(description='\n            When enabled, specifies which part definition a part must match to\n            be a valid part for the actor in this posture.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_PART)))), 
     '_actor_b_required_part_definition':OptionalTunable(description='\n            When enabled, specifies which part definition a part must match\n            to be a valid part for actor b in this posture.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_PART)))), 
     'require_parallel_entry_transition':Tunable(description='\n            If this is checked, then two Sims are able to directly enter this\n            multi-Sim posture if and only if their previous posture matches\n            (with the exception of "Be Carried")\n            \n            e.g., when this is checked:\n             VALID\n             x=stand, x=relax, x=woohoo\n             y=stand, y=relax, y=woohoo\n             \n             x=relax, x=relax, x=woohoo\n             y=sit,   y=relax, y=woohoo\n             \n             x=stand,  x=bathe\n             y=carried y=bathe\n             \n             INVALID\n             x=stand, x=woohoo\n             y=sit,   y=woohoo\n             \n            If this is unchecked, then there is no restriction about the\n            posture\'s entry sequence. The two Sims are able to enter the posture\n            independently.\n            \n            e.g., when this is unchecked:\n             VALID\n             x=stand, x=sit,    x=intimate\n             y=stand, y=liedown y=intimate\n            ',
       tunable_type=bool,
       default=True), 
     'carry_actor_b_on_exit_transition':TunableMapping(description="\n            By default on exiting the multi sim posture both sims should go into their default posture. \n            Add the age (of actor B) as key to enable carrying actor B after exiting the posture.\n            If actor B's age is not in the list, we won't carry them after exiting the posture.\n            \n            Please note the carry transition is triggered by Xevt id 700, so please add this Xevt to this\n            posture ASM's animation clip.\n            ",
       key_type=TunableEnumEntry(description='\n                Ages of actor B. For example if we add INFANT in keys, the adult sim will carry infant sim\n                on exiting this multi sim posture.\n                ',
       tunable_type=Age,
       default=(Age.INFANT)),
       value_type=TunableTuple(description='\n                Data representing how we want to carry the actor B.\n                ',
       carry_affordance=TunableReference(description='\n                    The affordance to push on actor A sim who carries actor B. \n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
       carry_track=TunableEnumEntry(description='\n                    Which hand to carry the actor B sim.\n                    ',
       tunable_type=PostureTrack,
       default=(PostureTrack.RIGHT))))}

    @classproperty
    def multi_sim(cls):
        return True

    def __init__(self, sim, target, track, *, master=True, **kwargs):
        (super().__init__)(sim, target, track, **kwargs)
        self._master = master
        self._setting_up = False
        if sim in _sims_that_create_puppet_postures:
            self._master = False

    @property
    def linked_sim(self):
        return self._linked_posture.sim

    @property
    def is_puppet(self):
        return not self._master

    @property
    def linked_posture(self):
        return self._linked_posture

    @linked_posture.setter
    def linked_posture(self, posture):
        if not self._master:
            posture.linked_posture = self
            return
        self._set_linked_posture(posture)
        posture._set_linked_posture(self)
        posture._master = False
        posture.rebind((posture.target), animation_context=(self._animation_context))

    @property
    def _actor_param_name(self):
        if self._master:
            return super()._actor_param_name
        animation_data = self.get_animation_data()
        return animation_data._actor_b_param_name

    def _set_linked_posture(self, posture):
        self._linked_posture = posture

    @classmethod
    def is_animation_available_for_species(cls, species):
        return True

    def add_transition_extras(self, sequence, *, arb):
        if self.linked_sim.parent is self.sim:
            carry_element_helper = CarryElementHelper(interaction=(self.source_interaction), sequence=sequence,
              carry_target=(self.linked_sim))
            sequence = carry_element_helper.exit_carry_while_holding(arb=arb)
        return sequence

    def append_transition_to_arb(self, *args, **kwargs):
        if not self.is_puppet:
            (super().append_transition_to_arb)(*args, **kwargs)
        else:
            (self.linked_posture.append_transition_to_arb)(*args, **kwargs)

    def append_idle_to_arb(self, arb):
        if not self.is_puppet:
            self.asm.request(self._state_name, arb)
            self.linked_posture.asm.set_current_state(self._state_name)
        else:
            self.linked_posture.append_idle_to_arb(arb)

    @property
    def should_carry_sim_on_exit(self):
        carried_sim = self.sim if self.is_puppet else self.linked_sim
        return carried_sim.age in self.carry_actor_b_on_exit_transition

    def append_exit_to_arb(self, arb, *args, **kwargs):
        if not self.is_puppet:
            (super().append_exit_to_arb)(arb, *args, **kwargs)
        else:
            (self.linked_posture.append_exit_to_arb)(arb, *args, **kwargs)

    def _setup_asm_posture(self, *args, **kwargs):
        return (super().setup_asm_posture)(*args, **kwargs)

    def setup_asm_posture(self, asm, sim, target, **kwargs):
        result = (self._setup_asm_posture)(asm, sim, target, **kwargs)
        if result:
            linked_posture = self.linked_posture
            if linked_posture is not None:
                if asm.set_actor((linked_posture._actor_param_name), (linked_posture.sim), actor_participant=(AnimationParticipant.TARGET)):
                    return asm.add_potentially_virtual_actor((linked_posture._actor_param_name), (linked_posture.sim), (linked_posture.get_target_name()), (linked_posture.target), target_participant=(AnimationParticipant.CONTAINER))
                return TestResult(False, 'Could not set actor {} on actor name {} for posture {} and asm {}'.format(linked_posture.sim, linked_posture._actor_param_name, self, asm))
            return True
        return result

    @flexmethod
    def _post_route_clothing_change(cls, inst, *args, **kwargs):
        return (super(__class__, inst if inst is not None else cls).post_route_clothing_change)(*args, **kwargs)

    def _exit_clothing_change(self, *args, **kwargs):
        return (super().exit_clothing_change)(*args, **kwargs)

    @flexmethod
    def post_route_clothing_change(cls, inst, *args, **kwargs):
        if inst is None:
            logger.error('No class support for {}.post_route_clothing_change', cls)
            return
        return (inst.get_linked_clothing_change)(inst._post_route_clothing_change, inst.linked_posture._post_route_clothing_change, *args, **kwargs)

    def exit_clothing_change(self, *args, **kwargs):
        return (self.get_linked_clothing_change)(self._exit_clothing_change, self.linked_posture._exit_clothing_change, *args, **kwargs)

    def get_linked_clothing_change(self, change_func, linked_change_func, *args, sim_info=DEFAULT, **kwargs):
        clothing_change = change_func(args, sim_info=sim_info, **kwargs)
        if self.linked_posture is not None:
            linked_clothing_change = linked_change_func(args, sim_info=self.linked_posture.sim.sim_info, **kwargs)
        if clothing_change is not None or linked_clothing_change is not None:
            clothing_change = do_all(clothing_change, linked_clothing_change)
        return clothing_change

    def add_outfit_exit_event(self, arb):
        super().add_outfit_exit_event(arb)
        if not self.is_puppet:
            self.linked_posture.add_outfit_exit_event(arb)

    def prepare_exit_clothing_change(self, interaction, *, sim_info, **kwargs):
        (super().prepare_exit_clothing_change)(interaction, sim_info=sim_info, **kwargs)
        if not self.is_puppet:
            (self.linked_posture.prepare_exit_clothing_change)(interaction, sim_info=self.linked_sim.sim_info, **kwargs)

    def setup_idle_asm_override(self, asm):
        result = self.setup_asm_interaction(asm, self.sim, self.target, self._actor_param_name, self.get_target_name())
        if result:
            linked_posture = self.linked_posture
            result = asm.set_actor(linked_posture._actor_param_name, linked_posture.sim)
            if result:
                return asm.add_potentially_virtual_actor((linked_posture._actor_param_name), (linked_posture.sim), (linked_posture.get_target_name()), (linked_posture.target), target_participant=(AnimationParticipant.CONTAINER))
        return result

    def get_idle_behavior(self):
        if not self._master:
            return
        return super().get_idle_behavior(setup_asm_override=(self.setup_idle_asm_override))


class MultiSimSocialPosture(MultiSimPosture):

    def setup_asm_posture(self, asm, sim, target, **kwargs):
        result = (self._setup_asm_posture)(asm, sim, target, **kwargs)
        if result:
            linked_posture = self.linked_posture
            if linked_posture is not None:
                if not asm.set_actor((linked_posture._actor_param_name), (linked_posture.sim), actor_participant=(AnimationParticipant.TARGET)):
                    return TestResult(False, 'Could not set actor {} on actor name {} for posture {} and asm {}'.format(linked_posture.sim, linked_posture._actor_param_name, self, asm))
            return True
        return result

    def setup_idle_asm_override(self, asm):
        result = self.setup_asm_interaction(asm, self.sim, self.target, self._actor_param_name, self.get_target_name())
        if result:
            linked_posture = self.linked_posture
            result = asm.set_actor(linked_posture._actor_param_name, linked_posture.sim)
        return result


lock_instance_tunables(MultiSimSocialPosture, _actor_required_part_definition=None,
  _actor_b_required_part_definition=None,
  unconstrained=True,
  jig=False,
  use_containment_slot_for_exit=False)

class IntimatePartPosture(MultiSimPosture):
    INSTANCE_TUNABLES = {'_targets_same_part':Tunable(description='\n            If this is checked, then two Sims target the same part.\n            ',
       tunable_type=bool,
       default=False), 
     '_has_opposite_mirrored_targets':Tunable(description="\n            If checked, assume that the animation content of x and y is\n            mirrored relative to one another. For instance, if x is targeting a\n            part that is un-mirrored, assume that y should target a mirrored \n            part.\n             \n            An example of when this should be checked is the bed woohoo \n            posture, where the left and right side of the bed (and by extension \n            x and y's target parts) are mirrors of each other. Conversely, it\n            should be unchecked for pillow fight, where both sims target parts\n            on the same side of the bed (one at the head and one at the foot). \n            ",
       tunable_type=bool,
       default=True)}

    @classproperty
    def targets_same_part(cls):
        return cls._targets_same_part

    @classmethod
    def is_valid_destination_target(cls, sim, target, adjacent_sim=None, adjacent_target=None, **kwargs):
        if not target.is_part:
            return False
        if adjacent_sim is None:
            return sim.posture.posture_type is cls
        if target.may_reserve(sim) or target.usable_by_transition_controller(sim.queue.transition_controller):
            if cls.targets_same_part:
                parts_iter = (
                 target,)
            else:
                parts_iter = target.adjacent_parts_gen()
            for part in parts_iter:
                if not part.may_reserve(adjacent_sim):
                    if part.usable_by_transition_controller(sim.queue.transition_controller):
                        if adjacent_target is not None:
                            if part is not adjacent_target:
                                continue
                    if part.supports_posture_type(cls):
                        return True

        return False

    def setup_asm_posture(self, asm, sim, target, **kwargs):
        result = (super().setup_asm_posture)(asm, sim, target, **kwargs)
        if result:
            if self.linked_posture is not None:
                asm.set_parameter('isMirrored', True if self.is_mirrored else False)
            return True
        return result

    def setup_asm_interaction(self, asm, sim, target, actor_name, target_name, **kwargs):
        result = (super().setup_asm_interaction)(asm, sim, target, actor_name, target_name, **kwargs)
        if result:
            if self.linked_posture is not None:
                is_mirrored = self.is_mirrored
                if self.is_puppet:
                    is_mirrored = not is_mirrored
                asm.set_parameter('isMirrored', True if is_mirrored else False)
            return True
        return result

    @property
    def is_mirrored(self):
        if self._linked_posture is None:
            is_mirrored = super().is_mirrored
            if self.is_puppet:
                if self._has_opposite_mirrored_targets:
                    is_mirrored = not is_mirrored
            return is_mirrored
        if self.is_puppet:
            return self.linked_posture.is_mirrored
        if self.target is None:
            return False
        relative_target = self.linked_posture.target if self._has_opposite_mirrored_targets else None
        return self.target.is_mirrored(relative_target)


class MobilePosture(Posture):
    INSTANCE_TUNABLES = {'compatible_walkstyles':TunableList(description='\n            The exhaustive list of walkstyles allowed while Sims are in this\n            mobile posture. If a Sim has a request for a walkstyle that is not\n            supported, the first element is used as a replacement.\n            ',
       tunable=TunableWalkstyle(pack_safe=True),
       unique_entries=False), 
     'posture_objects':OptionalTunable(description='\n            If enabled, we will use this tuning to find objects related to this\n            posture if it is unconstrained. This allows unconstrained mobile\n            postures to reset back into the object they were contained in.\n            ',
       tunable=ObjectDefinitonsOrTagsVariant(description='\n                The filter we use to check objects that this posture cares about.\n                ')), 
     '_skip_route':Tunable(description='\n            If checked, this mobile posture does not use a route to transition \n            to and from another posture. WARNING: Please consult a GPE before\n            checking this.\n            ',
       tunable_type=bool,
       default=False)}
    _posture_at_none_posture_state_spec = None
    _posture_at_none_constraint = None

    @constproperty
    def mobile():
        return True

    @classproperty
    def is_vehicle(cls):
        return not cls.unconstrained

    @classproperty
    def skip_route(cls):
        return cls._skip_route

    @classmethod
    def is_object_related(cls, test_object):
        if cls.posture_objects is not None:
            return cls.posture_objects.matches(test_object)
        return False

    @classmethod
    def get_mobile_at_none_constraint(cls):
        if cls._posture_at_none_constraint is None:
            cls._cache_mobile_posture_constraint()
        return cls._posture_at_none_constraint

    @classmethod
    def _cache_mobile_posture_constraint(cls):
        if cls._posture_at_none_constraint is None:
            cls._posture_at_none_posture_state_spec = create_body_posture_state_spec((cls.get_provided_postures()), body_target=None)
            cls._posture_at_none_constraint = Constraint(debug_name=('{}@None'.format(cls.name)), posture_state_spec=(cls._posture_at_none_posture_state_spec))