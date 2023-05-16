# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\socials\geometry.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 15352 bytes
import collections, contextlib
from sims4.tuning.geometric import TunableCurve
from sims4.tuning.tunable import Tunable, TunableRange
import accumulator, placement, sims4.geometry, sims4.log, sims4.math
__all__ = [
 'SocialGeometry', 'make']
logger = sims4.log.Logger('SocialGeometry')

class SocialGeometry:
    __slots__ = ('focus', 'field', '_area', 'transform')
    GROUP_DISTANCE_CURVE = TunableCurve(description='\n    A curve defining the score for standing a given distance away from other\n    Sims in the social group.\n    \n    Higher values (on the y-axis) encourage standing at that distance (on the\n    x-axis) away from other Sims.')
    NON_GROUP_DISTANCE_CURVE = TunableCurve(description='\n    A curve defining the score for standing a given distance away from other\n    Sims *not* in the social group.\n    \n    Higher values (on the y-axis) encourage standing at that distance (on the\n     x-axis) away from other Sims.')
    GROUP_ANGLE_CURVE = TunableCurve(description='\n    A curve defining the score for two Sims with this facing angle (in radians).\n    \n    An angle of zero (on the x-axis) means a Sims is facing another Sim, while\n    PI means a Sim is facing away.  Higher values (on the y-axis) encourage\n    that angular facing.')
    OVERLAP_SCORE_MULTIPLIER = Tunable(float, 1.0, description='p\n    Higher values raise the importance of the "personal space" component of the\n    social scoring function.')
    DEFAULT_SCORE_CUTOFF = TunableRange(float, 0.8, minimum=0, maximum=1.0, description='\n    Transforms scoring below cutoff * max_score are filtered out when joining / adjusting position')
    NON_OVERLAPPING_SCORE_MULTIPLIER = Tunable(float, 0.05, description='Minimum score multiplier for non-overlapping fields')
    SCORE_STRENGTH_MULTIPLIER = Tunable(float, 3, description='\n    Values > 1 will cause Sims to go further out of their way to be in perfect social arrangements.\n    This helps overcome distance attenuation for social adjustment since we want Sims to care more\n    about where they are positioned than how far they have to go to improve that position.')
    SCORE_OFFSET_FOR_CURRENT_POSITION = Tunable(float, 0.5, description="\n    An additional score to apply to points that are virtually identical to the\n    Sim's current position if the Sim already has an entry in the geometry.\n    \n    Larger numbers provide more friction that will prevent Sims from moving\n    away from their current position unless the score of the new point makes\n    moving worthwhile.")

    def __init__(self, focus, field, transform):
        self.focus = focus
        self.field = field
        self.transform = transform
        self._area = None

    def __repr__(self):
        return 'SocialGeometry[Focus:{}]'.format(self.focus)

    @property
    def area(self):
        if self._area is None:
            self._area = self.field.area()
        return self._area


class SocialGroupGeometry(collections.MutableMapping):

    def __init__(self):
        self.members = {}
        self.aggregate = None
        self._total_focus = None
        self._lockout = 0
        self._dirty = False

    def __repr__(self):
        return 'SocialGroupGeometry[focus:{}, Members:{}]'.format(self.focus, len(self.members))

    @property
    def focus(self):
        if self.aggregate is None:
            return
        return self.aggregate.focus

    @property
    def field(self):
        if self.aggregate is None:
            return
        return self.aggregate.field

    @property
    def area(self):
        if self.aggregate is None:
            return
        return self.aggregate.area

    def minimum_distance(self, p, sim_list, skip=None):
        sim_positions = [sim.intended_position for sim in sim_list if sim is not skip]
        if not sim_positions:
            return
        return sims4.math.minimum_distance(p, sim_positions)

    @contextlib.contextmanager
    def lock(self):
        try:
            self._lockout += 1
            self.aggregate = None
            self._total_focus = None
            yield self
        finally:
            self._lockout -= 1
            if self._lockout == 0:
                if self._dirty:
                    self._reconstruct()

    def score_placement(self, sim_list, group):
        scores = []
        for sim in sim_list:
            remainder = SocialGroupGeometry()
            with remainder.lock():
                for other, other_geometry in self.members.items():
                    if other is sim:
                        continue
                    remainder[other] = other_geometry

            valid, _ = score_transforms([sim.transform], sim, group, remainder)
            if valid:
                scores.append((sim, valid[0][1]))
            else:
                scores.append((sim, 0))

        return scores

    def __len__(self):
        return len(self.members)

    def __iter__(self):
        return iter(self.members)

    def __bool__(self):
        return bool(self.members)

    def __getitem__(self, key):
        return self.members[key]

    def __setitem__(self, key, value):
        existed = key in self.members
        self.members[key] = value
        if existed:
            self._reconstruct()
        else:
            self._merge(value)

    def __delitem__(self, key):
        existed = key in self.members
        del self.members[key]
        if existed:
            self._reconstruct()

    def __contains__(self, key):
        return key in self.members

    def _reconstruct(self):
        if self._lockout:
            self._dirty = True
            return
        n = len(self.members)
        if n == 0:
            self._total_focus = None
            self.aggregate = None
            return
        total_focus = None
        field = None
        for geometry in self.members.values():
            if total_focus is None:
                total_focus = geometry.focus
                field = geometry.field
            else:
                total_focus = total_focus + geometry.focus
                field = field.intersect(geometry.field)
            if not field.convex:
                field = sims4.geometry.CompoundPolygon(sims4.geometry.Polygon())

        focus = total_focus * (1.0 / n)
        self._total_focus = total_focus
        self.aggregate = SocialGeometry(focus, field, None)

    def _merge(self, geometry):
        if self._lockout:
            self._dirty = True
            return
        if self.aggregate is None:
            self._total_focus = geometry.focus
            self.aggregate = geometry
            return
        n = len(self.members)
        self._total_focus = self._total_focus + geometry.focus
        focus = self._total_focus * (1.0 / n)
        field = self.aggregate.field.intersect(geometry.field)
        self.aggregate = SocialGeometry(focus, field, None)


def create_from_transform(base_transform, base_focus, base_field, focal_dist):
    offset = sims4.math.Transform(sims4.math.Vector3(0, 0, focal_dist), sims4.math.Quaternion.IDENTITY())
    transform = sims4.math.Transform.concatenate(offset, base_transform)
    transform.translation = sims4.math.vector_flatten(transform.translation)
    focus = transform.transform_point(base_focus)
    vertices = [transform.transform_point(v) for v in base_field]
    field = sims4.geometry.CompoundPolygon(sims4.geometry.Polygon(vertices))
    return SocialGeometry(focus, field, base_transform)


def _get_social_geometry_for_sim(sim):
    tuning = sim.posture.social_geometry
    if tuning is None:
        return (None, None)
    base_focus = tuning.focal_point
    base_field = tuning.social_space
    if base_field is None:
        return (None, None)
    social_space_override, focal_point_override = sim.si_state.get_social_geometry_override()
    if social_space_override is not None:
        if focal_point_override is not None:
            base_focus = focal_point_override
            base_field = social_space_override
    return (
     base_focus, base_field)


def create(sim, group, transform_override=None):
    base_focus, base_field = _get_social_geometry_for_sim(sim)
    if base_focus is None or base_field is None:
        return
    r = group.group_radius
    transform = transform_override or sim.intended_transform
    return create_from_transform(transform, base_focus, base_field, r)


def score_transforms--- This code section failed: ---

 L. 320         0  LOAD_GLOBAL              _get_social_geometry_for_sim
                2  LOAD_FAST                'sim'
                4  CALL_FUNCTION_1       1  '1 positional argument'
                6  UNPACK_SEQUENCE_2     2 
                8  STORE_FAST               'base_focus'
               10  STORE_FAST               'base_field'

 L. 321        12  LOAD_FAST                'base_focus'
               14  LOAD_CONST               None
               16  COMPARE_OP               is
               18  POP_JUMP_IF_TRUE     32  'to 32'
               20  LOAD_FAST                'base_field'
               22  LOAD_CONST               None
               24  COMPARE_OP               is
               26  POP_JUMP_IF_TRUE     32  'to 32'
               28  LOAD_FAST                'group_geometry'
               30  POP_JUMP_IF_TRUE     40  'to 40'
             32_0  COME_FROM            26  '26'
             32_1  COME_FROM            18  '18'

 L. 322        32  BUILD_LIST_0          0 
               34  BUILD_LIST_0          0 
               36  BUILD_TUPLE_2         2 
               38  RETURN_VALUE     
             40_0  COME_FROM            30  '30'

 L. 324        40  LOAD_FAST                'group'
               42  LOAD_ATTR                group_radius
               44  STORE_FAST               'r'

 L. 326        46  BUILD_LIST_0          0 
               48  STORE_FAST               'scored'

 L. 327        50  BUILD_LIST_0          0 
               52  STORE_FAST               'results'

 L. 328        54  BUILD_LIST_0          0 
               56  STORE_FAST               'rejected'

 L. 329        58  LOAD_CONST               None
               60  STORE_FAST               'max_score'

 L. 330        62  SETUP_LOOP          182  'to 182'
               64  LOAD_FAST                'transforms'
               66  GET_ITER         
               68  FOR_ITER            180  'to 180'
               70  STORE_FAST               'transform'

 L. 331        72  LOAD_GLOBAL              score_transform
               74  LOAD_FAST                'transform'
               76  LOAD_FAST                'sim'
               78  LOAD_FAST                'group_geometry'
               80  LOAD_FAST                'r'
               82  LOAD_FAST                'base_focus'
               84  LOAD_FAST                'base_field'
               86  CALL_FUNCTION_6       6  '6 positional arguments'
               88  STORE_FAST               'score'

 L. 332        90  LOAD_FAST                'score'
               92  LOAD_CONST               0
               94  COMPARE_OP               >
               96  POP_JUMP_IF_FALSE   118  'to 118'
               98  LOAD_FAST                'modifier'
              100  LOAD_CONST               None
              102  COMPARE_OP               is-not
              104  POP_JUMP_IF_FALSE   118  'to 118'

 L. 333       106  LOAD_FAST                'modifier'
              108  LOAD_FAST                'score'
              110  LOAD_FAST                'transform'
              112  LOAD_FAST                'sim'
              114  CALL_FUNCTION_3       3  '3 positional arguments'
              116  STORE_FAST               'score'
            118_0  COME_FROM           104  '104'
            118_1  COME_FROM            96  '96'

 L. 334       118  LOAD_FAST                'score'
              120  LOAD_CONST               0
              122  COMPARE_OP               >
              124  POP_JUMP_IF_FALSE   164  'to 164'

 L. 335       126  LOAD_FAST                'scored'
              128  LOAD_METHOD              append
              130  LOAD_FAST                'transform'
              132  LOAD_FAST                'score'
              134  BUILD_TUPLE_2         2 
              136  CALL_METHOD_1         1  '1 positional argument'
              138  POP_TOP          

 L. 336       140  LOAD_FAST                'max_score'
              142  LOAD_CONST               None
              144  COMPARE_OP               is-not
              146  POP_JUMP_IF_FALSE   158  'to 158'
              148  LOAD_GLOBAL              max
              150  LOAD_FAST                'score'
              152  LOAD_FAST                'max_score'
              154  CALL_FUNCTION_2       2  '2 positional arguments'
              156  JUMP_FORWARD        160  'to 160'
            158_0  COME_FROM           146  '146'
              158  LOAD_FAST                'score'
            160_0  COME_FROM           156  '156'
              160  STORE_FAST               'max_score'
              162  JUMP_BACK            68  'to 68'
            164_0  COME_FROM           124  '124'

 L. 338       164  LOAD_FAST                'rejected'
              166  LOAD_METHOD              append
              168  LOAD_FAST                'transform'
              170  LOAD_FAST                'score'
              172  BUILD_TUPLE_2         2 
              174  CALL_METHOD_1         1  '1 positional argument'
              176  POP_TOP          
              178  JUMP_BACK            68  'to 68'
              180  POP_BLOCK        
            182_0  COME_FROM_LOOP       62  '62'

 L. 340       182  LOAD_FAST                'cutoff'
              184  LOAD_CONST               None
              186  COMPARE_OP               is
              188  POP_JUMP_IF_FALSE   196  'to 196'

 L. 341       190  LOAD_GLOBAL              SocialGeometry
              192  LOAD_ATTR                DEFAULT_SCORE_CUTOFF
              194  STORE_FAST               'cutoff'
            196_0  COME_FROM           188  '188'

 L. 343       196  LOAD_FAST                'max_score'
              198  LOAD_CONST               None
              200  COMPARE_OP               is-not
          202_204  POP_JUMP_IF_FALSE   262  'to 262'

 L. 344       206  LOAD_FAST                'max_score'
              208  LOAD_FAST                'cutoff'
              210  BINARY_MULTIPLY  
              212  STORE_FAST               'cutoff_score'

 L. 345       214  SETUP_LOOP          262  'to 262'
              216  LOAD_FAST                'scored'
              218  GET_ITER         
              220  FOR_ITER            260  'to 260'
              222  STORE_FAST               'score_data'

 L. 346       224  LOAD_FAST                'score_data'
              226  LOAD_CONST               1
              228  BINARY_SUBSCR    
              230  LOAD_FAST                'cutoff_score'
              232  COMPARE_OP               >=
              234  POP_JUMP_IF_FALSE   248  'to 248'

 L. 347       236  LOAD_FAST                'results'
              238  LOAD_METHOD              append
              240  LOAD_FAST                'score_data'
              242  CALL_METHOD_1         1  '1 positional argument'
              244  POP_TOP          
              246  JUMP_BACK           220  'to 220'
            248_0  COME_FROM           234  '234'

 L. 349       248  LOAD_FAST                'rejected'
              250  LOAD_METHOD              append
              252  LOAD_FAST                'score_data'
              254  CALL_METHOD_1         1  '1 positional argument'
              256  POP_TOP          
              258  JUMP_BACK           220  'to 220'
              260  POP_BLOCK        
            262_0  COME_FROM_LOOP      214  '214'
            262_1  COME_FROM           202  '202'

 L. 351       262  LOAD_FAST                'results'
              264  LOAD_FAST                'rejected'
              266  BUILD_TUPLE_2         2 
              268  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `RETURN_VALUE' instruction at offset 268


def score_transform(transform, sim, group_geometry, r, base_focus, base_field):
    accum = accumulator.HarmonicMeanAccumulator()
    dist = group_geometry.minimum_distance((transform.translation), (group_geometry.members), skip=sim)
    in_group_dist_score = SocialGeometry.GROUP_DISTANCE_CURVE.get(dist)
    accum.add(in_group_dist_score)
    if accum.fault():
        return 0
    candidate_geometry = create_from_transform(transform, base_focus, base_field, r)
    candidate_area = candidate_geometry.field.area()
    if candidate_area <= sims4.math.EPSILON:
        return 0
    candidate_facing = sims4.math.yaw_quaternion_to_angle(transform.orientation)
    for other_sim, geometry in group_geometry.members.items():
        if other_sim is sim:
            continue
        other_facing = sims4.math.yaw_quaternion_to_angle(geometry.transform.orientation)
        delta = geometry.transform.translation - transform.translation
        score_facing(accum, candidate_facing, other_facing, delta)
        intersection = geometry.field.intersect(candidate_geometry.field)
        fraction = intersection.area() / candidate_area
        fraction = SocialGeometry.OVERLAP_SCORE_MULTIPLIER * max(fraction, SocialGeometry.NON_OVERLAPPING_SCORE_MULTIPLIER)
        accum.add(fraction)
        if accum.fault():
            return 0

    nearby_non_members = list(placement.get_nearby_sims_gen((transform.translation), (sim.routing_surface), exclude=group_geometry, flags=(sims4.geometry.ObjectQuadTreeQueryFlag.IGNORE_SURFACE_TYPE)))
    if sim in nearby_non_members:
        nearby_non_members.remove(sim)
    if nearby_non_members:
        nearest = group_geometry.minimum_distance(transform.translation, nearby_non_members)
        not_in_group_score = SocialGeometry.NON_GROUP_DISTANCE_CURVE.get(nearest)
        accum.add(not_in_group_score)
    return accum.value()


def score_facing(accum, sim_facing, other_facing, delta):
    facing_angle = sims4.math.vector3_angle(delta)
    angle_ab = sims4.math.angle_abs_difference(sim_facing, facing_angle)
    score_ab = SocialGeometry.GROUP_ANGLE_CURVE.get(angle_ab)
    angle_ba = sims4.math.angle_abs_difference(other_facing, facing_angle + sims4.math.PI)
    score_ba = SocialGeometry.GROUP_ANGLE_CURVE.get(angle_ba)
    accum.add(score_ab * score_ba)