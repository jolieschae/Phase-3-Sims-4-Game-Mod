# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\carry\carry_interactions.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 3260 bytes
from animation.posture_manifest import PostureManifest, PostureManifestEntry, AnimationParticipant, MATCH_ANY, SlotManifest
from interactions.base.basic import TunableBasicContentSet
from interactions.base.super_interaction import SuperInteraction
from interactions.constraints import Constraint
from event_testing.results import TestResult
from postures.posture_state_spec import PostureStateSpec
from sims4.tuning.tunable import TunableReference
from sims4.utils import constproperty
import services, sims4.resources
CARRY_TARGET_POSTURE_MANIFEST = PostureManifest((
 PostureManifestEntry(None, None, None, None, AnimationParticipant.TARGET, MATCH_ANY, MATCH_ANY, MATCH_ANY),
 PostureManifestEntry(None, None, None, None, MATCH_ANY, AnimationParticipant.TARGET, MATCH_ANY, MATCH_ANY),
 PostureManifestEntry(None, None, None, None, MATCH_ANY, MATCH_ANY, AnimationParticipant.TARGET, MATCH_ANY))).intern()
CARRY_TARGET_POSTURE_STATE_SPEC = PostureStateSpec(CARRY_TARGET_POSTURE_MANIFEST, SlotManifest().intern(), None)

class PickUpObjectSuperInteraction(SuperInteraction):
    INSTANCE_TUNABLES = {'basic_content':TunableBasicContentSet(one_shot=True, no_content=True, default='no_content'), 
     'si_to_push':TunableReference(manager=services.get_instance_manager(sims4.resources.Types.INTERACTION), allow_none=True,
       description='SI to push after picking up the object.')}

    @classmethod
    def _constraint_gen(cls, *args, **kwargs):
        yield Constraint(debug_name=('PickUpObjectSuperInteraction({})'.format(cls.si_to_push)), posture_state_spec=CARRY_TARGET_POSTURE_STATE_SPEC)

    @classmethod
    def _test(cls, target, context, **kwargs):
        from sims.sim import Sim
        if isinstance(target.parent, Sim):
            return TestResult(False, 'Cannot pick up an object parented to a Sim.')
        if context.source == context.SOURCE_AUTONOMY:
            if context.sim.posture_state.get_carry_track(target.definition.id) is not None:
                return TestResult(False, 'Sims should not autonomously pick up more than one object.')
        return TestResult.TRUE


class CarryCancelInteraction(SuperInteraction):

    @constproperty
    def is_carry_cancel_interaction():
        return True


class PickUpRequesterInteraction(SuperInteraction):

    @constproperty
    def is_pickup_requester():
        return True