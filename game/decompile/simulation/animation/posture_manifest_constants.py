# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\posture_manifest_constants.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 9942 bytes
from animation.posture_manifest import MATCH_ANY, MATCH_NONE, PostureManifestEntry, PostureManifest
from interactions.constraints import Constraint, create_constraint_set
from postures.posture_state_spec import create_body_posture_state_spec
from sims4.common import is_available_pack, Pack
from sims4.tuning.tunable import TunableReference
import services, sims4.resources
STAND_POSTURE_MANIFEST = PostureManifest((
 PostureManifestEntry(None, '', 'stand', 'FullBody', MATCH_ANY, MATCH_ANY, MATCH_ANY, MATCH_ANY),
 PostureManifestEntry(None, '', 'stand', 'UpperBody', MATCH_ANY, MATCH_ANY, MATCH_ANY, MATCH_ANY))).intern()
STAND_NO_SURFACE_POSTURE_MANIFEST = PostureManifest((
 PostureManifestEntry(None, '', 'stand', 'FullBody', MATCH_ANY, MATCH_ANY, MATCH_ANY, MATCH_NONE),
 PostureManifestEntry(None, '', 'stand', 'UpperBody', MATCH_ANY, MATCH_ANY, MATCH_ANY, MATCH_NONE))).intern()
STAND_NO_CARRY_NO_SURFACE_POSTURE_MANIFEST = PostureManifest((
 PostureManifestEntry(None, '', 'stand', 'FullBody', MATCH_NONE, MATCH_NONE, MATCH_NONE, MATCH_NONE),
 PostureManifestEntry(None, '', 'stand', 'UpperBody', MATCH_NONE, MATCH_NONE, MATCH_NONE, MATCH_NONE))).intern()
STAND_OR_MOVING_STAND_POSTURE_MANIFEST = PostureManifest((
 PostureManifestEntry(None, '', 'movingStand', 'FullBody', MATCH_ANY, MATCH_ANY, MATCH_ANY, MATCH_ANY),
 PostureManifestEntry(None, '', 'movingStand', 'UpperBody', MATCH_ANY, MATCH_ANY, MATCH_ANY, MATCH_ANY),
 PostureManifestEntry(None, '', 'stand', 'FullBody', MATCH_ANY, MATCH_ANY, MATCH_ANY, MATCH_ANY),
 PostureManifestEntry(None, '', 'stand', 'UpperBody', MATCH_ANY, MATCH_ANY, MATCH_ANY, MATCH_ANY))).intern()
STAND_POSTURE_STATE_SPEC = create_body_posture_state_spec(STAND_POSTURE_MANIFEST)
STAND_AT_NONE_POSTURE_STATE_SPEC = create_body_posture_state_spec(STAND_POSTURE_MANIFEST, body_target=None)
STAND_NO_SURFACE_STATE_SPEC = create_body_posture_state_spec(STAND_NO_SURFACE_POSTURE_MANIFEST)
STAND_NO_CARRY_NO_SURFACE_STATE_SPEC = create_body_posture_state_spec(STAND_NO_CARRY_NO_SURFACE_POSTURE_MANIFEST)
STAND_OR_MOVING_STAND_STATE_SPEC = create_body_posture_state_spec(STAND_OR_MOVING_STAND_POSTURE_MANIFEST)
STAND_OR_MOVING_STAND_AT_NONE_STATE_SPEC = create_body_posture_state_spec(STAND_OR_MOVING_STAND_POSTURE_MANIFEST, body_target=None)
STAND_CONSTRAINT = Constraint(debug_name='Stand', posture_state_spec=STAND_POSTURE_STATE_SPEC)
STAND_NO_SURFACE_CONSTRAINT = Constraint(debug_name='Stand-NoSurface', posture_state_spec=STAND_NO_SURFACE_STATE_SPEC)
STAND_NO_CARRY_NO_SURFACE_CONSTRAINT = Constraint(debug_name='Stand-NoCarryNoSurface', posture_state_spec=STAND_NO_CARRY_NO_SURFACE_STATE_SPEC)
STAND_CONSTRAINT_OUTER_PENALTY = Constraint(debug_name='Stand', posture_state_spec=STAND_POSTURE_STATE_SPEC, ignore_outer_penalty_threshold=1.0)
STAND_AT_NONE_CONSTRAINT = Constraint(debug_name='Stand@None', posture_state_spec=STAND_AT_NONE_POSTURE_STATE_SPEC)
STAND_OR_MOVING_STAND_CONSTRAINT = Constraint(debug_name='Stand-Or-MovingStand', posture_state_spec=STAND_OR_MOVING_STAND_STATE_SPEC)
STAND_OR_MOVING_STAND_AT_NONE_CONSTRAINT = Constraint(debug_name='Stand-Or-MovingStand@None', posture_state_spec=STAND_OR_MOVING_STAND_AT_NONE_STATE_SPEC)
SIT_POSTURE_MANIFEST = PostureManifest((
 PostureManifestEntry(None, '', 'sit', 'FullBody', MATCH_ANY, MATCH_ANY, MATCH_NONE, MATCH_ANY),
 PostureManifestEntry(None, '', 'sit', 'UpperBody', MATCH_ANY, MATCH_ANY, MATCH_NONE, MATCH_ANY))).intern()
SIT_NO_CARRY_ANY_SURFACE_MANIFEST = PostureManifest((
 PostureManifestEntry(None, '', 'sit', 'FullBody', MATCH_NONE, MATCH_NONE, MATCH_NONE, MATCH_ANY),
 PostureManifestEntry(None, '', 'sit', 'UpperBody', MATCH_NONE, MATCH_NONE, MATCH_NONE, MATCH_ANY))).intern()
_SIT_FAMILY_PACK_SPECIFIC_PICKUP_POSTURES = PostureManifest((
 PostureManifestEntry(None, 'Kotatsu_Sit_Posture', '', 'FullBody', MATCH_ANY, MATCH_ANY, MATCH_NONE, MATCH_ANY),
 PostureManifestEntry(None, 'Kotatsu_Sit_Posture', '', 'UpperBody', MATCH_ANY, MATCH_ANY, MATCH_NONE, MATCH_ANY))).intern()
_SIT_FAMILY_BG_PICKUP_POSTURES = PostureManifest((
 PostureManifestEntry(None, 'sit', '', 'FullBody', MATCH_ANY, MATCH_ANY, MATCH_NONE, MATCH_ANY),
 PostureManifestEntry(None, 'sit', '', 'UpperBody', MATCH_ANY, MATCH_ANY, MATCH_NONE, MATCH_ANY))).intern()
_SIT_FAMILY_PICKUP_POSTURES = PostureManifest(list(_SIT_FAMILY_BG_PICKUP_POSTURES) + list(_SIT_FAMILY_PACK_SPECIFIC_PICKUP_POSTURES)).intern()
if is_available_pack(Pack.EP10):
    SIT_PICKUP_POSTURES = _SIT_FAMILY_PICKUP_POSTURES
else:
    SIT_PICKUP_POSTURES = _SIT_FAMILY_BG_PICKUP_POSTURES
SIT_POSTURE_STATE_SPEC = create_body_posture_state_spec(SIT_POSTURE_MANIFEST)
SIT_NO_CARRY_ANY_SURFACE_STATE_SPEC = create_body_posture_state_spec(SIT_NO_CARRY_ANY_SURFACE_MANIFEST)
SIT_CONSTRAINT = Constraint(debug_name='Sit', posture_state_spec=SIT_POSTURE_STATE_SPEC)
SIT_NO_CARRY_ANY_SURFACE_CONSTRAINT = Constraint(debug_name='SitNoCarryAnySurface', posture_state_spec=SIT_NO_CARRY_ANY_SURFACE_STATE_SPEC)
SWIM_POSTURE_TYPE = 'swim'
SWIM_POSTURE_MANIFEST = PostureManifest((
 PostureManifestEntry(None, SWIM_POSTURE_TYPE, '', 'FullBody', None, None, None, MATCH_ANY),
 PostureManifestEntry(None, SWIM_POSTURE_TYPE, '', 'UpperBody', None, None, None, MATCH_ANY))).intern()
SWIM_AT_NONE_POSTURE_STATE_SPEC = create_body_posture_state_spec(SWIM_POSTURE_MANIFEST, body_target=None)
SWIM_AT_NONE_CONSTRAINT = Constraint(debug_name='swim@None', posture_state_spec=SWIM_AT_NONE_POSTURE_STATE_SPEC)

class PostureConstants:
    SIT_POSTURE_TYPE = TunableReference(description='\n        A reference to the sit posture type.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.POSTURE)))


SIT_INTIMATE_POSTURE_MANIFEST = PostureManifest((
 PostureManifestEntry(None, 'sitIntimate', '', 'FullBody', MATCH_NONE, MATCH_NONE, MATCH_NONE, MATCH_ANY),
 PostureManifestEntry(None, 'sitIntimate', '', 'UpperBody', MATCH_NONE, MATCH_NONE, MATCH_NONE, MATCH_ANY),
 PostureManifestEntry(None, 'sitIntimateBooth', '', 'FullBody', MATCH_NONE, MATCH_NONE, MATCH_NONE, MATCH_ANY),
 PostureManifestEntry(None, 'sitIntimateBooth', '', 'UpperBody', MATCH_NONE, MATCH_NONE, MATCH_NONE, MATCH_ANY))).intern()
SIT_INTIMATE_POSTURE_STATE_SPEC = create_body_posture_state_spec(SIT_INTIMATE_POSTURE_MANIFEST)
SIT_INTIMATE_CONSTRAINT = Constraint(debug_name='SitIntimate', posture_state_spec=SIT_INTIMATE_POSTURE_STATE_SPEC)
STAND_OR_SIT_POSTURE_MANIFEST = PostureManifest(list(STAND_POSTURE_MANIFEST) + list(SIT_POSTURE_MANIFEST)).intern()
STAND_OR_SIT_CONSTRAINT = create_constraint_set((STAND_CONSTRAINT, SIT_CONSTRAINT), debug_name='Stand-or-Sit')
STAND_SIT_OR_SWIM_CONSTRAINT_OUTER_PENALTY = create_constraint_set((STAND_CONSTRAINT_OUTER_PENALTY, SIT_CONSTRAINT, SWIM_AT_NONE_CONSTRAINT), debug_name='Stand-Sit-Or-Swim-Outer-Penalty')
ADJUSTMENT_CONSTRAINT = create_constraint_set((STAND_OR_MOVING_STAND_CONSTRAINT, SIT_CONSTRAINT), debug_name='Adjustment-Constraint')