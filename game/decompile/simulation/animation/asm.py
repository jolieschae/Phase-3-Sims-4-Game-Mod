# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\asm.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 75877 bytes
from _math import Transform
from collections import defaultdict
import _collection_utils, itertools, weakref
from animation import get_throwaway_animation_context
from animation.animation_bc_cache import read_bc_cache_from_resource
from animation.animation_utils import partition_boundary_on_params
from animation.posture_manifest import PostureManifest, PostureManifestEntry, _NOT_SPECIFIC_ACTOR_OR_NONE, MATCH_ANY, Hand, AnimationParticipant
from distributor.system import Distributor
from native.animation import ASM_ACTORTYPE_SIM
from sims.sim_info_types import Age, SpeciesExtended
from sims4.callback_utils import CallableList
from sims4.collections import frozendict
from sims4.math import transform_almost_equal_2d
from sims4.profiler_utils import create_custom_named_profiler_function
from sims4.sim_irq_service import yield_to_irq
from singletons import DEFAULT, UNSET
import caches, distributor.ops, native.animation, sims4.callback_utils, sims4.geometry, sims4.hash_util, sims4.log
logger = sims4.log.Logger('Animation')
with sims4.reload.protected(globals()):
    GLOBAL_SINGLE_PART_CONDITION_CACHE = {}
    GLOBAL_MULTI_PART_CONDITION_CACHE = {}
    _verbose_logging_asms = []
    inject_asm_name_in_callstack = False
    profile_boundary_condition_creation = False

def add_boundary_condition_logging(pattern):
    global _verbose_logging_asms
    _verbose_logging_asms.append(pattern)


def clear_boundary_condition_logging():
    global _verbose_logging_asms
    _verbose_logging_asms = []


def purge_cache():
    Asm._bc_cache.clear()
    Asm._bc_cache_error_keys.clear()
    Asm._bc_cache_localwork_keys.clear()


sims4.callback_utils.add_callbacks(sims4.callback_utils.CallbackEvent.TUNING_CODE_RELOAD, purge_cache)
do_params_match = _collection_utils.dictionary_intersection_values_match

def _consolidate_carry_info2(posture_manifest):
    if posture_manifest is None:
        return
    result = PostureManifest()
    for p0 in posture_manifest:
        free_hands = set()
        for p1 in posture_manifest:
            if p0.actor == p1.actor and p0.specific == p1.specific and p0.family == p1.family and p0.level == p1.level and p0.surface == p1.surface and p0.provides == p1.provides and p0.left in _NOT_SPECIFIC_ACTOR_OR_NONE and p1.left in _NOT_SPECIFIC_ACTOR_OR_NONE and p0.right in _NOT_SPECIFIC_ACTOR_OR_NONE and p1.right in _NOT_SPECIFIC_ACTOR_OR_NONE and p0.back in _NOT_SPECIFIC_ACTOR_OR_NONE and p1.back in _NOT_SPECIFIC_ACTOR_OR_NONE:
                free_hands.update(p1.free_hands)

        left = p0.left
        right = p0.right
        back = p0.back
        left = MATCH_ANY if Hand.LEFT in free_hands else left
        right = MATCH_ANY if Hand.RIGHT in free_hands else right
        back = MATCH_ANY if Hand.BACK in free_hands else back
        entry = PostureManifestEntry(p0.actor, p0.specific, p0.family, p0.level, left, right, back, p0.surface, p0.provides)
        result.add(entry)

    return result


def create_asm(*args, **kwargs):
    if not inject_asm_name_in_callstack:
        asm = Asm(*args, **kwargs)
        return asm
    asm = Asm(*args, **kwargs)
    name = 'ASM: {}'.format(asm.name)
    name_f = create_custom_named_profiler_function(name)
    name_f((lambda: None))
    return asm


class BoundaryConditionRelative:
    __slots__ = ('pre_condition_reference_object_name', 'pre_condition_transform',
                 'pre_condition_reference_joint_name_hash', 'post_condition_reference_object_name',
                 'post_condition_transform', 'post_condition_reference_joint_name_hash',
                 'required_slots', 'debug_info')

    def __str__(self):
        pre_str = '0'
        if self.pre_condition_transform != Transform.IDENTITY():
            n = list(self.pre_condition_transform.translation)
            n.extend(self.pre_condition_transform.orientation)
            pre_str = ('({:0.3},{:0.3},{:0.3}/{:0.3},{:0.3},{:0.3},{:0.3})'.format)(*n)
        post_str = '0'
        if self.post_condition_transform != Transform.IDENTITY():
            n = list(self.post_condition_transform.translation)
            n.extend(self.post_condition_transform.orientation)
            post_str = ('({:0.3},{:0.3},{:0.3}/{:0.3},{:0.3},{:0.3},{:0.3})'.format)(*n)
        return '{}+{} -> {}+{} {}'.format(self.pre_condition_reference_object_name, pre_str, self.post_condition_reference_object_name, post_str, self.required_slots)

    def __init__(self, pre_condition_reference_object_name, pre_condition_transform, pre_condition_reference_joint_name_hash, post_condition_reference_object_name, post_condition_transform, post_condition_reference_joint_name_hash, required_slots, debug_info):
        self.pre_condition_reference_object_name = pre_condition_reference_object_name
        self.pre_condition_transform = pre_condition_transform
        self.pre_condition_reference_joint_name_hash = pre_condition_reference_joint_name_hash
        self.post_condition_reference_object_name = post_condition_reference_object_name
        self.post_condition_transform = post_condition_transform
        self.post_condition_reference_joint_name_hash = post_condition_reference_joint_name_hash
        self.required_slots = required_slots
        self.debug_info = debug_info

    def get_pre_condition_reference_object_id(self, asm):
        actor = asm.get_actor_by_name(self.pre_condition_reference_object_name)
        if actor is not None:
            return actor.id

    def get_post_condition_reference_object_id(self, asm):
        actor = asm.get_actor_by_name(self.post_condition_reference_object_name)
        if actor is not None:
            return actor.id

    def get_relative_object_id(self, asm):
        return self.get_pre_condition_reference_object_id(asm) or self.get_post_condition_reference_object_id(asm) or None

    def get_transforms(self, asm, part):
        pre_condition_transform = self.pre_condition_transform
        post_condition_transform = self.post_condition_transform
        pre_condition_reference_joint = self.pre_condition_reference_joint_name_hash
        post_condition_reference_joint = self.post_condition_reference_joint_name_hash
        pre_condition_reference_object = asm.get_actor_by_name(self.pre_condition_reference_object_name)
        if pre_condition_reference_object is not None:
            if pre_condition_transform is not None:
                pre_obj_transform = pre_condition_reference_object.transform
                pre_condition_transform = Transform.concatenate(pre_condition_transform, pre_obj_transform)
        if self.post_condition_reference_object_name is None:
            post_condition_transform = pre_condition_transform
        else:
            post_condition_reference_object = asm.get_actor_by_name(self.post_condition_reference_object_name)
            if post_condition_reference_object is not None:
                if post_condition_transform is not None:
                    post_obj_transform = post_condition_reference_object.transform
                    post_condition_transform = Transform.concatenate(post_condition_transform, post_obj_transform)
        return (
         pre_condition_transform, post_condition_transform, pre_condition_reference_joint, post_condition_reference_joint)


class Asm(native.animation.NativeAsm):
    _bc_cache = {}
    _bc_cache_error_keys = set()
    _bc_cache_localwork_keys = defaultdict(set)

    @staticmethod
    def _is_same_actor(a: weakref.ref, b):
        if a is None:
            if b is None:
                return True
        if b is None:
            return False
        a_actor = a() if a is not None else None
        a_actor_id = a_actor.id if a_actor is not None else 0
        return a_actor_id == b.id

    def _log_bc_error(self, log, currently_set_actor_names, key, headline, actor_info):
        set_actor_names = []
        unset_actor_names = set(self.actors)
        for e in currently_set_actor_names:
            if isinstance(e, tuple):
                unset_actor_names.discard(e[1])
                e = ('{1}[{0}]'.format)(*e)
            else:
                unset_actor_names.discard(e)
            set_actor_names.append(e)

        set_actor_names.sort()
        unset_actor_names = sorted(unset_actor_names)
        log(("Boundary condition error: {}\n    {}\n        {} (Unset actors: {})\n    The boundary information we're looking for is:\n        {}: {} from {} --> {} (Posture: {})".format)(headline, actor_info, ', '.join(set_actor_names), ', '.join(unset_actor_names), *key))

    @staticmethod
    def transform_almost_equal_2d(a, b):
        return sims4.math.transform_almost_equal_2d(a,
          b, epsilon=(sims4.geometry.ANIMATION_SLOT_EPSILON),
          epsilon_orientation=(sims4.geometry.ANIMATION_SLOT_EPSILON))

    @staticmethod
    def transform_almost_equal_2d_safe(a, b):
        if a == b:
            return True
        if a is None or b is None:
            return False
        return transform_almost_equal_2d(a, b)

    def __init__(self, asm_key, context, posture_manifest_overrides=None):
        super().__init__(asm_key)
        self.context = context
        self._posture_manifest_overrides = posture_manifest_overrides
        self._prop_overrides = {}
        self._alt_prop_definitions = {}
        self._prop_state_values = {}
        self._vfx_overrides = {}
        self._sound_overrides = {}
        self._actors = {}
        self._virtual_actors = defaultdict(set)
        self._virtual_actor_relationships = {}
        self._on_state_changed_events = CallableList()
        self._boundary_condition_dirty = asm_key in sims4.resources.localwork_no_groupid

    @property
    def name(self):
        return self.state_machine_name

    @property
    def context(self):
        if self._context_ref is not None:
            return self._context_ref()

    @context.setter
    def context(self, value):
        if value is not None:
            self._context_ref = weakref.ref(value)
            value.add_asm(self)
        else:
            self._context_ref = None

    @property
    def vfx_overrides(self):
        return self._vfx_overrides

    @property
    def sound_overrides(self):
        return self._sound_overrides

    @property
    def on_state_changed_events(self):
        return self._on_state_changed_events

    def dirty_boundary_conditions(self):
        self._boundary_condition_dirty = True
        self._bc_cache_localwork_keys[self.name].clear()

    def _validate_actor(self, actor):
        for existing_actor in self.actors_gen():
            if existing_actor == actor:
                return

        raise AssertionError("Attempt to get boundary conditions for an actor {} that doesn't exist in the ASM {}.".format(actor, self))

    def get_actor_by_name(self, actor_name):
        actor_info = self._actors.get(actor_name)
        if actor_info is not None:
            return actor_info[0]()
        actor_infos = self._virtual_actors.get(actor_name)
        if actor_infos:
            for actor_info in actor_infos:
                return actor_info[0]()

    def get_actor_name_from_id(self, object_id):
        if not object_id:
            return
        for actor_name, actor_info in self._actors.items():
            boundary_actor = actor_info[0]()
            if object_id == boundary_actor.id:
                return actor_name

        for actor_name, actor_infos in self._virtual_actors.items():
            for actor_info in actor_infos:
                boundary_actor = actor_info[0]()
                if object_id == boundary_actor.id:
                    return actor_name

    def _get_all_set_actor_names(self):
        names = set(self._actors.keys())
        virtual_names = set((e[1] for e in self._virtual_actor_relationships.keys()))
        return frozenset(names | virtual_names)

    def _get_param_sequences_for_age_species_gen(self, param_sequence, actor_name, actor_species, actor_ages, target_name, target_species, target_ages):
        if target_name is None:
            params = itertools.product(actor_species, actor_ages)
        else:
            params = itertools.product(actor_species, actor_ages, target_species, target_ages)
        for _actor_species, _actor_age, *target_params in params:
            if not SpeciesExtended.is_age_valid_for_animation_cache(_actor_species, _actor_age):
                continue
            age_species_locked_args = {(
 'species', actor_name): SpeciesExtended.get_animation_species_param(_actor_species), 
             (
 'age', actor_name): _actor_age.animation_age_param}
            if target_name is not None:
                _target_species, _target_age = target_params
                if not SpeciesExtended.is_age_valid_for_animation_cache(_target_species, _target_age):
                    continue
                age_species_locked_args.update({(
 'species', target_name): SpeciesExtended.get_animation_species_param(_target_species), 
                 (
 'age', target_name): _target_age.animation_age_param})
            yield frozendict(param_sequence, age_species_locked_args)

    def _get_param_sequences_for_cache(self, actor, actor_name, to_state_name, from_state_name, posture, target_name=None):
        internal_param_sequence_list = self._get_param_sequences(actor.id, to_state_name, from_state_name, None)
        internal_param_sequence_list = internal_param_sequence_list or (None, )
        if posture is None:
            return internal_param_sequence_list
        param_sequence_list = []
        posture_key = (
         'posture', actor_name)
        exact_str = posture.name + '-'
        family_str = posture.family_name
        if family_str is not None:
            family_str = '-' + family_str + '-'
        for param_sequence in internal_param_sequence_list:
            if param_sequence:
                posture_param_value = param_sequence.get(posture_key)
                if posture_param_value is not None and not posture_param_value.startswith(exact_str):
                    if family_str is None or family_str not in posture_param_value:
                        continue
                    else:
                        actor_age_param = (
                         'age', actor_name)
                        if param_sequence is not None:
                            if actor_age_param in param_sequence:
                                age = Age.get_age_from_animation_param(param_sequence[actor_age_param])
                                actor_available_ages = (age,)
                            else:
                                actor_available_ages = Age.get_ages_for_animation_cache()
                            actor_species_param = ('species', actor_name)
                            if param_sequence is not None and actor_species_param in param_sequence:
                                species = SpeciesExtended.get_species_from_animation_param(param_sequence[actor_species_param])
                                actor_available_species = (species,)
                            else:
                                actor_available_species = SpeciesExtended
                            if target_name is None:
                                target_available_species = ()
                                target_available_ages = ()
                        else:
                            target_age_param = (
                             'age', target_name)
                        if param_sequence is not None and target_age_param in param_sequence:
                            age = Age.get_age_from_animation_param(param_sequence[target_age_param])
                            target_available_ages = (age,)
                        else:
                            target_available_ages = Age.get_ages_for_animation_cache()
                        target_species_param = ('species', target_name)
                        if param_sequence is not None and target_species_param in param_sequence:
                            species = SpeciesExtended.get_species_from_animation_param(param_sequence[target_species_param])
                            target_available_species = (species,)
                        else:
                            target_available_species = SpeciesExtended
                    for age_species_param_sequence in self._get_param_sequences_for_age_species_gen(param_sequence, actor_name, actor_available_species, actor_available_ages, target_name, target_available_species, target_available_ages):
                        param_sequence_list.append(age_species_param_sequence)

        return param_sequence_list

    def _create_containment_slot_data_list--- This code section failed: ---

 L. 601         0  LOAD_CONST               True
                2  STORE_FAST               'cache_containment_slot_data_list'

 L. 602         4  LOAD_FAST                'self'
                6  LOAD_ATTR                _get_param_sequences_for_cache
                8  LOAD_FAST                'actor'
               10  LOAD_FAST                'actor_name'
               12  LOAD_FAST                'to_state_name'
               14  LOAD_FAST                'from_state_name'

 L. 603        16  LOAD_FAST                'posture'
               18  LOAD_FAST                'target_name'
               20  LOAD_CONST               ('target_name',)
               22  CALL_FUNCTION_KW_6     6  '6 total positional and keyword args'
               24  STORE_FAST               'param_sequence_list'

 L. 604        26  BUILD_MAP_0           0 
               28  STORE_FAST               'boundary_to_params'

 L. 606     30_32  SETUP_LOOP          684  'to 684'
               34  LOAD_FAST                'param_sequence_list'
               36  GET_ITER         
            38_40  FOR_ITER            682  'to 682'
               42  STORE_FAST               'param_sequence'

 L. 608        44  LOAD_FAST                'self'
               46  LOAD_METHOD              set_param_sequence
               48  LOAD_FAST                'param_sequence'
               50  CALL_METHOD_1         1  '1 positional argument'
               52  POP_TOP          

 L. 610        54  LOAD_GLOBAL              yield_to_irq
               56  CALL_FUNCTION_0       0  '0 positional arguments'
               58  POP_TOP          

 L. 612        60  LOAD_FAST                'verbose_logging'
               62  POP_JUMP_IF_FALSE   110  'to 110'

 L. 613        64  LOAD_GLOBAL              logger
               66  LOAD_METHOD              warn
               68  LOAD_STR                 '  Setting parameter list on ASM:'
               70  CALL_METHOD_1         1  '1 positional argument'
               72  POP_TOP          

 L. 614        74  SETUP_LOOP          110  'to 110'
               76  LOAD_FAST                'param_sequence'
               78  LOAD_METHOD              items
               80  CALL_METHOD_0         0  '0 positional arguments'
               82  GET_ITER         
               84  FOR_ITER            108  'to 108'
               86  UNPACK_SEQUENCE_2     2 
               88  STORE_FAST               'param_key'
               90  STORE_FAST               'param_value'

 L. 615        92  LOAD_GLOBAL              logger
               94  LOAD_METHOD              warn
               96  LOAD_STR                 '    {}:\t{}'
               98  LOAD_FAST                'param_key'
              100  LOAD_FAST                'param_value'
              102  CALL_METHOD_3         3  '3 positional arguments'
              104  POP_TOP          
              106  JUMP_BACK            84  'to 84'
              108  POP_BLOCK        
            110_0  COME_FROM_LOOP       74  '74'
            110_1  COME_FROM            62  '62'

 L. 617       110  LOAD_FAST                'self'
              112  LOAD_METHOD              get_boundary_conditions
              114  LOAD_FAST                'actor'
              116  LOAD_FAST                'to_state_name'
              118  LOAD_FAST                'from_state_name'
              120  CALL_METHOD_3         3  '3 positional arguments'
              122  STORE_FAST               'boundary'

 L. 622       124  LOAD_CONST               None
              126  LOAD_FAST                'boundary'
              128  STORE_ATTR               debug_info

 L. 624       130  LOAD_FAST                'base_object_name'
              132  JUMP_IF_TRUE_OR_POP   144  'to 144'
              134  LOAD_FAST                'self'
              136  LOAD_METHOD              get_actor_name_from_id
              138  LOAD_FAST                'boundary'
              140  LOAD_ATTR                pre_condition_reference_object_id
              142  CALL_METHOD_1         1  '1 positional argument'
            144_0  COME_FROM           132  '132'
              144  STORE_FAST               'pre_condition_reference_object_name'

 L. 625       146  LOAD_FAST                'self'
              148  LOAD_METHOD              get_actor_name_from_id
              150  LOAD_FAST                'boundary'
              152  LOAD_ATTR                post_condition_reference_object_id
              154  CALL_METHOD_1         1  '1 positional argument'
              156  STORE_FAST               'post_condition_reference_object_name'

 L. 643       158  LOAD_FAST                'pre_condition_reference_object_name'
              160  LOAD_CONST               None
              162  COMPARE_OP               is-not
              164  POP_JUMP_IF_FALSE   196  'to 196'

 L. 644       166  LOAD_FAST                'target_name'
              168  LOAD_CONST               None
              170  COMPARE_OP               is
              172  POP_JUMP_IF_FALSE   196  'to 196'

 L. 652       174  LOAD_FAST                'self'
              176  LOAD_METHOD              get_actor_definition
              178  LOAD_FAST                'pre_condition_reference_object_name'
              180  CALL_METHOD_1         1  '1 positional argument'
              182  STORE_FAST               'actor_definition'

 L. 653       184  LOAD_FAST                'actor_definition'
              186  LOAD_ATTR                actor_type
              188  LOAD_GLOBAL              ASM_ACTORTYPE_SIM
              190  COMPARE_OP               ==
              192  POP_JUMP_IF_FALSE   196  'to 196'

 L. 654       194  CONTINUE             38  'to 38'
            196_0  COME_FROM           192  '192'
            196_1  COME_FROM           172  '172'
            196_2  COME_FROM           164  '164'

 L. 656       196  LOAD_FAST                'verbose_logging'
          198_200  POP_JUMP_IF_FALSE   334  'to 334'

 L. 657       202  LOAD_GLOBAL              logger
              204  LOAD_METHOD              warn
              206  LOAD_STR                 '    Pre conditions'
              208  CALL_METHOD_1         1  '1 positional argument'
              210  POP_TOP          

 L. 658       212  LOAD_GLOBAL              logger
              214  LOAD_METHOD              warn
              216  LOAD_STR                 '      Object: {}'
              218  LOAD_FAST                'pre_condition_reference_object_name'
              220  CALL_METHOD_2         2  '2 positional arguments'
              222  POP_TOP          

 L. 659       224  LOAD_FAST                'boundary'
              226  LOAD_ATTR                pre_condition_transform
              228  LOAD_CONST               None
              230  COMPARE_OP               is-not
          232_234  POP_JUMP_IF_FALSE   268  'to 268'

 L. 660       236  LOAD_GLOBAL              logger
              238  LOAD_METHOD              warn
              240  LOAD_STR                 '      Translation: {}'
              242  LOAD_FAST                'boundary'
              244  LOAD_ATTR                pre_condition_transform
              246  LOAD_ATTR                translation
              248  CALL_METHOD_2         2  '2 positional arguments'
              250  POP_TOP          

 L. 661       252  LOAD_GLOBAL              logger
              254  LOAD_METHOD              warn
              256  LOAD_STR                 '      Orientation: {}'
              258  LOAD_FAST                'boundary'
              260  LOAD_ATTR                pre_condition_transform
              262  LOAD_ATTR                orientation
              264  CALL_METHOD_2         2  '2 positional arguments'
              266  POP_TOP          
            268_0  COME_FROM           232  '232'

 L. 663       268  LOAD_GLOBAL              logger
              270  LOAD_METHOD              warn
              272  LOAD_STR                 '    Post conditions'
              274  CALL_METHOD_1         1  '1 positional argument'
              276  POP_TOP          

 L. 664       278  LOAD_GLOBAL              logger
              280  LOAD_METHOD              warn
              282  LOAD_STR                 '      Object: {}'
              284  LOAD_FAST                'post_condition_reference_object_name'
              286  CALL_METHOD_2         2  '2 positional arguments'
              288  POP_TOP          

 L. 665       290  LOAD_FAST                'boundary'
              292  LOAD_ATTR                post_condition_transform
              294  LOAD_CONST               None
              296  COMPARE_OP               is-not
          298_300  POP_JUMP_IF_FALSE   334  'to 334'

 L. 666       302  LOAD_GLOBAL              logger
              304  LOAD_METHOD              warn
              306  LOAD_STR                 '      Translation: {}'
              308  LOAD_FAST                'boundary'
              310  LOAD_ATTR                post_condition_transform
              312  LOAD_ATTR                translation
              314  CALL_METHOD_2         2  '2 positional arguments'
              316  POP_TOP          

 L. 667       318  LOAD_GLOBAL              logger
              320  LOAD_METHOD              warn
              322  LOAD_STR                 '      Orientation: {}'
              324  LOAD_FAST                'boundary'
              326  LOAD_ATTR                post_condition_transform
              328  LOAD_ATTR                orientation
              330  CALL_METHOD_2         2  '2 positional arguments'
              332  POP_TOP          
            334_0  COME_FROM           298  '298'
            334_1  COME_FROM           198  '198'

 L. 669       334  BUILD_LIST_0          0 
              336  STORE_FAST               'required_slots'

 L. 670       338  LOAD_FAST                'self'
              340  LOAD_METHOD              _get_all_set_actor_names
              342  CALL_METHOD_0         0  '0 positional arguments'
              344  STORE_FAST               'currently_set_actor_names'

 L. 671       346  LOAD_FAST                'boundary'
              348  LOAD_ATTR                required_slots
          350_352  POP_JUMP_IF_FALSE   466  'to 466'

 L. 672       354  SETUP_LOOP          466  'to 466'
              356  LOAD_FAST                'boundary'
              358  LOAD_ATTR                required_slots
              360  GET_ITER         
              362  FOR_ITER            464  'to 464'
              364  STORE_FAST               'required_slot'

 L. 673       366  LOAD_FAST                'required_slot'
              368  LOAD_CONST               0
              370  BINARY_SUBSCR    
              372  STORE_FAST               'pre_condition_surface_child_id'

 L. 674       374  LOAD_FAST                'required_slot'
              376  LOAD_CONST               1
              378  BINARY_SUBSCR    
              380  STORE_FAST               'pre_condition_surface_object_id'

 L. 675       382  LOAD_FAST                'self'
              384  LOAD_METHOD              get_actor_name_from_id
              386  LOAD_FAST                'pre_condition_surface_child_id'
              388  CALL_METHOD_1         1  '1 positional argument'
              390  STORE_FAST               'pre_condition_surface_child_name'

 L. 676       392  LOAD_FAST                'self'
              394  LOAD_METHOD              get_actor_name_from_id
              396  LOAD_FAST                'pre_condition_surface_object_id'
              398  CALL_METHOD_1         1  '1 positional argument'
              400  STORE_FAST               'pre_condition_surface_object_name'

 L. 677       402  LOAD_FAST                'pre_condition_surface_child_name'
          404_406  POP_JUMP_IF_FALSE   436  'to 436'
              408  LOAD_FAST                'pre_condition_surface_object_name'
          410_412  POP_JUMP_IF_FALSE   436  'to 436'

 L. 678       414  LOAD_FAST                'required_slots'
              416  LOAD_METHOD              append
              418  LOAD_FAST                'pre_condition_surface_child_name'

 L. 679       420  LOAD_FAST                'pre_condition_surface_object_name'

 L. 680       422  LOAD_FAST                'required_slot'
              424  LOAD_CONST               2
              426  BINARY_SUBSCR    
              428  BUILD_TUPLE_3         3 
              430  CALL_METHOD_1         1  '1 positional argument'
              432  POP_TOP          
              434  JUMP_BACK           362  'to 362'
            436_0  COME_FROM           410  '410'
            436_1  COME_FROM           404  '404'

 L. 682       436  LOAD_CONST               False
              438  STORE_FAST               'cache_containment_slot_data_list'

 L. 683       440  LOAD_FAST                'self'
              442  LOAD_METHOD              _log_bc_error
              444  LOAD_GLOBAL              logger
              446  LOAD_ATTR                error
              448  LOAD_FAST                'currently_set_actor_names'
              450  LOAD_FAST                'key'

 L. 684       452  LOAD_STR                 'missing parent or child object'

 L. 685       454  LOAD_STR                 "The parent or child in Maya isn't one of the following actors:"
              456  CALL_METHOD_5         5  '5 positional arguments'
              458  POP_TOP          
          460_462  JUMP_BACK           362  'to 362'
              464  POP_BLOCK        
            466_0  COME_FROM_LOOP      354  '354'
            466_1  COME_FROM           350  '350'

 L. 687       466  LOAD_GLOBAL              tuple
              468  LOAD_FAST                'required_slots'
              470  CALL_FUNCTION_1       1  '1 positional argument'
              472  STORE_FAST               'required_slots'

 L. 688       474  LOAD_FAST                'required_slots'
          476_478  POP_JUMP_IF_TRUE    494  'to 494'
              480  LOAD_FAST                'boundary'
              482  LOAD_ATTR                pre_condition_reference_object_id
              484  LOAD_CONST               None
              486  COMPARE_OP               is
          488_490  POP_JUMP_IF_FALSE   494  'to 494'

 L. 692       492  CONTINUE             38  'to 38'
            494_0  COME_FROM           488  '488'
            494_1  COME_FROM           476  '476'

 L. 694       494  LOAD_FAST                'boundary'
              496  LOAD_ATTR                pre_condition_reference_object_id
              498  LOAD_CONST               None
              500  COMPARE_OP               is-not
          502_504  POP_JUMP_IF_FALSE   530  'to 530'

 L. 695       506  LOAD_FAST                'boundary'
              508  LOAD_ATTR                pre_condition_reference_object_id
              510  LOAD_CONST               0
              512  COMPARE_OP               !=
          514_516  POP_JUMP_IF_FALSE   530  'to 530'

 L. 696       518  LOAD_FAST                'pre_condition_reference_object_name'
              520  LOAD_CONST               None
              522  COMPARE_OP               is
          524_526  POP_JUMP_IF_FALSE   530  'to 530'

 L. 716       528  CONTINUE             38  'to 38'
            530_0  COME_FROM           524  '524'
            530_1  COME_FROM           514  '514'
            530_2  COME_FROM           502  '502'

 L. 718       530  SETUP_LOOP          680  'to 680'
              532  LOAD_FAST                'boundary_to_params'
              534  LOAD_METHOD              items
              536  CALL_METHOD_0         0  '0 positional arguments'
              538  GET_ITER         
            540_0  COME_FROM           616  '616'
            540_1  COME_FROM           604  '604'
            540_2  COME_FROM           586  '586'
            540_3  COME_FROM           568  '568'
            540_4  COME_FROM           556  '556'
              540  FOR_ITER            636  'to 636'
              542  UNPACK_SEQUENCE_2     2 
              544  STORE_FAST               'boundary_existing'
              546  STORE_FAST               'params_list'

 L. 719       548  LOAD_FAST                'pre_condition_reference_object_name'
              550  LOAD_FAST                'boundary_existing'
              552  LOAD_ATTR                pre_condition_reference_object_name
              554  COMPARE_OP               ==
          556_558  POP_JUMP_IF_FALSE   540  'to 540'

 L. 720       560  LOAD_FAST                'post_condition_reference_object_name'
              562  LOAD_FAST                'boundary_existing'
              564  LOAD_ATTR                post_condition_reference_object_name
              566  COMPARE_OP               ==
          568_570  POP_JUMP_IF_FALSE   540  'to 540'

 L. 721       572  LOAD_FAST                'self'
              574  LOAD_METHOD              transform_almost_equal_2d_safe
              576  LOAD_FAST                'boundary'
              578  LOAD_ATTR                pre_condition_transform

 L. 722       580  LOAD_FAST                'boundary_existing'
              582  LOAD_ATTR                pre_condition_transform
              584  CALL_METHOD_2         2  '2 positional arguments'
          586_588  POP_JUMP_IF_FALSE   540  'to 540'

 L. 723       590  LOAD_FAST                'self'
              592  LOAD_METHOD              transform_almost_equal_2d_safe
              594  LOAD_FAST                'boundary'
              596  LOAD_ATTR                post_condition_transform

 L. 724       598  LOAD_FAST                'boundary_existing'
              600  LOAD_ATTR                post_condition_transform
              602  CALL_METHOD_2         2  '2 positional arguments'
          604_606  POP_JUMP_IF_FALSE   540  'to 540'

 L. 725       608  LOAD_FAST                'required_slots'
              610  LOAD_FAST                'boundary_existing'
              612  LOAD_ATTR                required_slots
              614  COMPARE_OP               ==
          616_618  POP_JUMP_IF_FALSE   540  'to 540'

 L. 726       620  LOAD_FAST                'params_list'
              622  LOAD_METHOD              append
              624  LOAD_FAST                'param_sequence'
              626  CALL_METHOD_1         1  '1 positional argument'
              628  POP_TOP          

 L. 727       630  BREAK_LOOP       
          632_634  JUMP_BACK           540  'to 540'
              636  POP_BLOCK        

 L. 729       638  LOAD_GLOBAL              BoundaryConditionRelative

 L. 730       640  LOAD_FAST                'pre_condition_reference_object_name'
              642  LOAD_FAST                'boundary'
              644  LOAD_ATTR                pre_condition_transform
              646  LOAD_FAST                'boundary'
              648  LOAD_ATTR                pre_condition_reference_joint_name_hash

 L. 731       650  LOAD_FAST                'post_condition_reference_object_name'
              652  LOAD_FAST                'boundary'
              654  LOAD_ATTR                post_condition_transform
              656  LOAD_FAST                'boundary'
              658  LOAD_ATTR                post_condition_reference_joint_name_hash

 L. 732       660  LOAD_FAST                'required_slots'
              662  LOAD_FAST                'boundary'
              664  LOAD_ATTR                debug_info
              666  CALL_FUNCTION_8       8  '8 positional arguments'
              668  STORE_FAST               'boundary_relative'

 L. 733       670  LOAD_FAST                'param_sequence'
              672  BUILD_LIST_1          1 
              674  LOAD_FAST                'boundary_to_params'
              676  LOAD_FAST                'boundary_relative'
              678  STORE_SUBSCR     
            680_0  COME_FROM_LOOP      530  '530'
              680  JUMP_BACK            38  'to 38'
              682  POP_BLOCK        
            684_0  COME_FROM_LOOP       30  '30'

 L. 735       684  LOAD_FAST                'verbose_logging'
          686_688  POP_JUMP_IF_FALSE   764  'to 764'

 L. 736       690  LOAD_GLOBAL              logger
              692  LOAD_METHOD              warn
              694  LOAD_STR                 '  Boundary -> Param Sequences'
              696  CALL_METHOD_1         1  '1 positional argument'
              698  POP_TOP          

 L. 737       700  SETUP_LOOP          764  'to 764'
              702  LOAD_FAST                'boundary_to_params'
              704  LOAD_METHOD              items
              706  CALL_METHOD_0         0  '0 positional arguments'
              708  GET_ITER         
              710  FOR_ITER            762  'to 762'
              712  UNPACK_SEQUENCE_2     2 
              714  STORE_FAST               'param_key'
              716  STORE_FAST               'param_value'

 L. 738       718  LOAD_GLOBAL              logger
              720  LOAD_METHOD              warn
              722  LOAD_STR                 '    {}'
              724  LOAD_FAST                'param_key'
              726  CALL_METHOD_2         2  '2 positional arguments'
              728  POP_TOP          

 L. 739       730  SETUP_LOOP          758  'to 758'
              732  LOAD_FAST                'param_value'
              734  GET_ITER         
              736  FOR_ITER            756  'to 756'
              738  STORE_FAST               'param_sequence'

 L. 740       740  LOAD_GLOBAL              logger
              742  LOAD_METHOD              warn
              744  LOAD_STR                 '      {}'
              746  LOAD_FAST                'param_sequence'
              748  CALL_METHOD_2         2  '2 positional arguments'
              750  POP_TOP          
          752_754  JUMP_BACK           736  'to 736'
              756  POP_BLOCK        
            758_0  COME_FROM_LOOP      730  '730'
          758_760  JUMP_BACK           710  'to 710'
              762  POP_BLOCK        
            764_0  COME_FROM_LOOP      700  '700'
            764_1  COME_FROM           686  '686'

 L. 742       764  BUILD_LIST_0          0 
              766  STORE_FAST               'boundary_list'

 L. 744       768  LOAD_GLOBAL              len
              770  LOAD_FAST                'boundary_to_params'
              772  CALL_FUNCTION_1       1  '1 positional argument'
              774  LOAD_CONST               0
              776  COMPARE_OP               >
          778_780  POP_JUMP_IF_FALSE   890  'to 890'

 L. 745       782  LOAD_GLOBAL              len
              784  LOAD_FAST                'boundary_to_params'
              786  CALL_FUNCTION_1       1  '1 positional argument'
              788  LOAD_CONST               1
              790  COMPARE_OP               ==
          792_794  POP_JUMP_IF_FALSE   822  'to 822'

 L. 750       796  LOAD_FAST                'boundary_list'
              798  LOAD_METHOD              append
              800  LOAD_FAST                'boundary_to_params'
              802  LOAD_METHOD              popitem
              804  CALL_METHOD_0         0  '0 positional arguments'
              806  LOAD_CONST               0
              808  BINARY_SUBSCR    
              810  BUILD_MAP_0           0 
              812  BUILD_LIST_1          1 
              814  BUILD_TUPLE_2         2 
              816  CALL_METHOD_1         1  '1 positional argument'
              818  POP_TOP          
              820  JUMP_FORWARD        890  'to 890'
            822_0  COME_FROM           792  '792'

 L. 752       822  LOAD_GLOBAL              partition_boundary_on_params
              824  LOAD_FAST                'boundary_to_params'
              826  CALL_FUNCTION_1       1  '1 positional argument'
              828  STORE_FAST               'boundary_param_sets'

 L. 753       830  SETUP_LOOP          890  'to 890'
              832  LOAD_FAST                'boundary_param_sets'
              834  LOAD_METHOD              items
              836  CALL_METHOD_0         0  '0 positional arguments'
              838  GET_ITER         
              840  FOR_ITER            888  'to 888'
              842  UNPACK_SEQUENCE_2     2 
              844  STORE_FAST               'boundary'
              846  STORE_DEREF              'param_set'

 L. 754       848  LOAD_CLOSURE             'param_set'
              850  BUILD_TUPLE_1         1 
              852  LOAD_SETCOMP             '<code_object <setcomp>>'
              854  LOAD_STR                 'Asm._create_containment_slot_data_list.<locals>.<setcomp>'
              856  MAKE_FUNCTION_8          'closure'

 L. 757       858  LOAD_FAST                'boundary_to_params'
              860  LOAD_FAST                'boundary'
              862  BINARY_SUBSCR    
              864  GET_ITER         
              866  CALL_FUNCTION_1       1  '1 positional argument'
              868  STORE_FAST               'boundary_params_list_minimal'

 L. 759       870  LOAD_FAST                'boundary_list'
              872  LOAD_METHOD              append
              874  LOAD_FAST                'boundary'
              876  LOAD_FAST                'boundary_params_list_minimal'
              878  BUILD_TUPLE_2         2 
              880  CALL_METHOD_1         1  '1 positional argument'
              882  POP_TOP          
          884_886  JUMP_BACK           840  'to 840'
              888  POP_BLOCK        
            890_0  COME_FROM_LOOP      830  '830'
            890_1  COME_FROM           820  '820'
            890_2  COME_FROM           778  '778'

 L. 761       890  LOAD_CONST               None
              892  STORE_FAST               'relative_object_name'

 L. 764       894  BUILD_LIST_0          0 
              896  STORE_FAST               'containment_slot_data_list'

 L. 767       898  SETUP_LOOP         1042  'to 1042'
              900  LOAD_FAST                'boundary_list'
              902  GET_ITER         
              904  FOR_ITER           1040  'to 1040'
              906  UNPACK_SEQUENCE_2     2 
              908  STORE_FAST               'boundary_condition'
              910  STORE_FAST               'slot_params_list'

 L. 768       912  LOAD_FAST                'boundary_condition'
              914  LOAD_ATTR                pre_condition_reference_object_name
          916_918  JUMP_IF_TRUE_OR_POP   924  'to 924'

 L. 769       920  LOAD_FAST                'boundary_condition'
              922  LOAD_ATTR                post_condition_reference_object_name
            924_0  COME_FROM           916  '916'
              924  STORE_FAST               'relative_object_name_key'

 L. 782       926  LOAD_FAST                'entry'
          928_930  POP_JUMP_IF_FALSE   960  'to 960'

 L. 786       932  LOAD_FAST                'boundary_condition'
              934  LOAD_ATTR                post_condition_reference_object_name
              936  LOAD_CONST               None
              938  COMPARE_OP               is-not
          940_942  POP_JUMP_IF_FALSE   952  'to 952'

 L. 787       944  LOAD_FAST                'boundary_condition'
              946  LOAD_ATTR                post_condition_transform
              948  STORE_FAST               'containment_transform'
              950  JUMP_FORWARD        958  'to 958'
            952_0  COME_FROM           940  '940'

 L. 789       952  LOAD_FAST                'boundary_condition'
              954  LOAD_ATTR                pre_condition_transform
              956  STORE_FAST               'containment_transform'
            958_0  COME_FROM           950  '950'
              958  JUMP_FORWARD        966  'to 966'
            960_0  COME_FROM           928  '928'

 L. 791       960  LOAD_FAST                'boundary_condition'
              962  LOAD_ATTR                pre_condition_transform
              964  STORE_FAST               'containment_transform'
            966_0  COME_FROM           958  '958'

 L. 793       966  SETUP_LOOP         1036  'to 1036'
              968  LOAD_FAST                'containment_slot_data_list'
              970  GET_ITER         
            972_0  COME_FROM           990  '990'
              972  FOR_ITER           1014  'to 1014'
              974  UNPACK_SEQUENCE_2     2 
              976  STORE_FAST               'containment_transform_existing'
              978  STORE_FAST               'slots_to_params'

 L. 794       980  LOAD_FAST                'self'
              982  LOAD_METHOD              transform_almost_equal_2d
              984  LOAD_FAST                'containment_transform'
              986  LOAD_FAST                'containment_transform_existing'
              988  CALL_METHOD_2         2  '2 positional arguments'
          990_992  POP_JUMP_IF_FALSE   972  'to 972'

 L. 795       994  LOAD_FAST                'slots_to_params'
              996  LOAD_METHOD              append
              998  LOAD_FAST                'boundary_condition'
             1000  LOAD_FAST                'slot_params_list'
             1002  BUILD_TUPLE_2         2 
             1004  CALL_METHOD_1         1  '1 positional argument'
             1006  POP_TOP          

 L. 796      1008  BREAK_LOOP       
         1010_1012  JUMP_BACK           972  'to 972'
             1014  POP_BLOCK        

 L. 798      1016  LOAD_FAST                'containment_slot_data_list'
             1018  LOAD_METHOD              append

 L. 799      1020  LOAD_FAST                'containment_transform'
             1022  LOAD_FAST                'boundary_condition'
             1024  LOAD_FAST                'slot_params_list'
             1026  BUILD_TUPLE_2         2 
             1028  BUILD_LIST_1          1 
             1030  BUILD_TUPLE_2         2 
             1032  CALL_METHOD_1         1  '1 positional argument'
             1034  POP_TOP          
           1036_0  COME_FROM_LOOP      966  '966'
         1036_1038  JUMP_BACK           904  'to 904'
             1040  POP_BLOCK        
           1042_0  COME_FROM_LOOP      898  '898'

 L. 806      1042  LOAD_FAST                'cache_containment_slot_data_list'
         1044_1046  POP_JUMP_IF_FALSE  1102  'to 1102'

 L. 807      1048  LOAD_GLOBAL              logger
             1050  LOAD_METHOD              debug
             1052  LOAD_STR                 'Caching containment slot data list for {}: {} ({} -> {})\n\tKEY={}'
             1054  LOAD_FAST                'self'
             1056  LOAD_ATTR                name
             1058  LOAD_FAST                'actor_name'
             1060  LOAD_FAST                'from_state_name'
             1062  LOAD_FAST                'to_state_name'
             1064  LOAD_FAST                'key'
             1066  CALL_METHOD_6         6  '6 positional arguments'
             1068  POP_TOP          

 L. 808      1070  LOAD_GLOBAL              tuple
             1072  LOAD_FAST                'containment_slot_data_list'
             1074  CALL_FUNCTION_1       1  '1 positional argument'
             1076  LOAD_FAST                'self'
             1078  LOAD_ATTR                _bc_cache
             1080  LOAD_FAST                'key'
             1082  STORE_SUBSCR     

 L. 809      1084  LOAD_FAST                'self'
             1086  LOAD_ATTR                _bc_cache_localwork_keys
             1088  LOAD_FAST                'self'
             1090  LOAD_ATTR                name
             1092  BINARY_SUBSCR    
             1094  LOAD_METHOD              add
             1096  LOAD_FAST                'key'
             1098  CALL_METHOD_1         1  '1 positional argument'
             1100  POP_TOP          
           1102_0  COME_FROM          1044  '1044'

 L. 811      1102  LOAD_FAST                'containment_slot_data_list'
             1104  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `LOAD_SETCOMP' instruction at offset 852

    def _make_boundary_conditions_list(self, actor, to_state_name, from_state_name, locked_params, entry=True, posture=DEFAULT, base_object_name=None, target=None):
        if any((pattern in str(self) for pattern in _verbose_logging_asms)):
            verbose_logging = True
        else:
            verbose_logging = False
        actor_name = self.get_actor_name_from_id(actor.id)
        target_name = self.get_actor_name_from_id(target.id) if target is not None else None
        if verbose_logging:
            logger.warn('Traversing as {} ({} -> {})', actor_name, from_state_name, to_state_name)
        else:
            if posture is DEFAULT:
                posture = getattr(actor, 'posture', None)
            key = (self.name, actor_name, target_name, from_state_name,
             to_state_name, posture.name if posture is not None else None)
            if not caches.USE_ACC_AND_BCC & caches.AccBccUsage.BCC != caches.AccBccUsage.BCC:
                if not self._boundary_condition_dirty or key not in self._bc_cache_localwork_keys[self.name]:
                    containment_slot_data_list = None
                else:
                    containment_slot_data_list = self._bc_cache.get(key)
                if containment_slot_data_list is None:
                    logger.info'Building containment slot data list for {}: {} ({} -> {})\n\tKEY={}'self.nameactor_namefrom_state_nameto_state_namekey
                    if profile_boundary_condition_creation:

                        def _create_containment_slot_data_list():
                            return self._create_containment_slot_data_list(key, actor, actor_name, to_state_name, from_state_name,
                              posture, entry, verbose_logging, base_object_name=base_object_name,
                              target_name=target_name)

                        profile_f = create_custom_named_profiler_function('ASM_bc {}'.format(self.name))
                        containment_slot_data_list = profile_f(_create_containment_slot_data_list)
                    else:
                        containment_slot_data_list = self._create_containment_slot_data_list(key, actor, actor_name, to_state_name,
                          from_state_name, posture,
                          entry, verbose_logging, base_object_name=base_object_name,
                          target_name=target_name)
                if not containment_slot_data_list:
                    return ()
                age = getattr(actor, 'age', UNSET)
                if age is not UNSET:
                    real_age_param = {(
 'age', actor_name): age.animation_age_param}
                    locked_params += {('age', actor_name): age.age_for_animation_cache.animation_age_param}
            else:
                real_age_param = {}
        containment_slot_data_list_filtered = []
        for containment_slot, slots_to_params in containment_slot_data_list:
            slots_to_params_valid = []
            for boundary_condition, param_sequences in slots_to_params:
                param_sequences_valid = [frozendict(param_sequence, real_age_param) for param_sequence in param_sequences if do_params_match(param_sequence, locked_params)]
                if param_sequences_valid:
                    slots_to_params_valid.append((boundary_condition, tuple(param_sequences_valid)))

            if slots_to_params_valid:
                containment_slot_data_list_filtered.append((containment_slot, tuple(slots_to_params_valid)))

        return tuple(containment_slot_data_list_filtered)

    def get_boundary_conditions_list(self, actor, to_state_name, from_state_name=DEFAULT, entry=True, locked_params=frozendict(), posture=DEFAULT, base_object_name=None, target=None):
        if from_state_name is DEFAULT:
            from_state_name = 'entry'
        boundary_list = self._make_boundary_conditions_list(actor, to_state_name, from_state_name,
          locked_params, entry=entry,
          posture=posture,
          base_object_name=base_object_name,
          target=target)
        return boundary_list

    def set_prop_override(self, prop_name, override_tuning, alternative_def=None):
        self._prop_overrides[prop_name] = override_tuning
        if alternative_def is not None:
            self._alt_prop_definitions[prop_name] = alternative_def

    def store_prop_state_values(self, prop_name, state_values):
        self._prop_state_values[prop_name] = state_values

    def set_vfx_override(self, vfx_object_name, vfx_override_name):
        self._vfx_overrides[sims4.hash_util.hash32(vfx_object_name)] = vfx_override_name

    def set_sound_override(self, sound_name, sound_id):
        self._sound_overrides[sims4.hash_util.hash64(sound_name)] = sound_id

    def get_props_in_traversal(self, from_state, to_state):
        prop_keys = super().get_props_in_traversal(from_state, to_state)
        if not prop_keys:
            return prop_keys
        result = {}
        for prop_name, prop_key in prop_keys.items():
            if prop_name in self._prop_overrides and self._prop_overrides[prop_name].definition is not None:
                alt_def = self._alt_prop_definitions.get(prop_name, None)
                result[prop_name] = alt_def.id if alt_def is not None else self._prop_overrides[prop_name].definition.id
            else:
                result[prop_name] = prop_key.instance

        return result

    def set_prop_as_asm_actor(self, prop_name, prop):
        if prop_name in self._prop_overrides:
            override_tuple = self._prop_overrides[prop_name]
            if override_tuple.set_as_actor is not None:
                if not self.set_actor(override_tuple.set_as_actor, prop):
                    logger.warn('{}: Failed to set prop as actor: {} to {}', self, prop_name, prop)

    def get_prop_state_override(self, prop_name):
        if prop_name in self._prop_overrides:
            override_tuple = self._prop_overrides[prop_name]
            if override_tuple.from_actor is not None:
                actor = self.get_actor_by_name(override_tuple.from_actor)
                if actor is not None:
                    return (
                     actor, override_tuple.states_to_override)
        return (None, None)

    def get_prop_share_key(self, prop_name):
        if prop_name in self._prop_overrides:
            override_tuple = self._prop_overrides[prop_name]
            if override_tuple.sharing is not None:
                return override_tuple.sharing.get_prop_share_key(self)

    def apply_special_case_overrides(self, prop_name, prop):
        if prop_name not in self._prop_overrides:
            return
        special_cases = self._prop_overrides[prop_name].special_cases
        if special_cases is None:
            return
        cloth_actor_name = special_cases.set_baby_cloth_from_actor
        if cloth_actor_name is not None:
            actor = self.get_actor_by_name(cloth_actor_name)
            baby_skin_tone_op = distributor.ops.SetBabySkinTone(actor.sim_info.baby_cloth_and_id())
            Distributor.instance().add_op(prop, baby_skin_tone_op)

    def set_prop_state_values(self, prop_name, prop):
        state_values = self._prop_state_values.get(prop_name)
        if state_values is None:
            return
        for state_value in state_values:
            if state_value is not None:
                prop.set_state(state_value.state, state_value)

    def request(self, state_name, arb, *args, context=None, debug_context=None, **kwargs):
        context = context or self.context
        if context is None:
            logger.error('Invalid call to Asm.request() to state_name {} with no animation context on {}. Actors {}', state_name, self, (self._actors), owner='rmccord')
            context = get_throwaway_animation_context()
            self.context = context
        current_state = self.current_state
        self._on_state_changed_events(self, state_name)
        context._pre_requestselfarbstate_name
        result = (super().request)(state_name, arb, *args, request_id=context.request_id, **kwargs)
        context._post_requestselfarbstate_name
        if result == native.animation.ASM_REQUESTRESULT_SUCCESS:
            return True
        if result == native.animation.ASM_REQUESTRESULT_TARGET_JUMPED_TO_TARGET_STATE:
            raise RuntimeError('{}: Attempt to traverse between two states ({} -> {}) where no valid path exists! Actors {}{}'.format(self, current_state, state_name, self._actors, _format_debug_context(debug_context)))
        else:
            if result == native.animation.ASM_REQUESTRESULT_TARGET_STATE_NOT_FOUND:
                logger.error("{}: Attempt to request state that doesn't exist - {}.{}", self, state_name, _format_debug_context(debug_context))
                return False
            logger.error('{}: Unknown result code when requesting state - {}.{}', self, state_name, _format_debug_context(debug_context))

    def traverse(self, from_state_name, to_state_name, arb, *args, context=None, from_boundary_conditions=False, **kwargs):
        context = context or self.context
        if not from_boundary_conditions:
            self._on_state_changed_events(self, to_state_name)
            context._pre_requestselfarbto_state_name
        success = (super().traverse)(from_state_name, to_state_name, arb, *args, request_id=context.request_id, from_boundary_conditions=from_boundary_conditions, **kwargs)
        if not from_boundary_conditions:
            context._post_requestselfarbto_state_name
        return success

    def set_current_state(self, state_name):
        self._on_state_changed_events(self, state_name)
        return super().set_current_state(state_name)

    def exit(self, arb, *args, context=None, **kwargs):
        context = context or self.context
        self._on_state_changed_events(self, 'exit')
        context._pre_requestselfarb'exit'
        success = (super().exit)(arb, *args, request_id=context.request_id, **kwargs)
        context._post_requestselfarb'exit'
        return success

    def set_actor(self, actor_name, actor, suffix=DEFAULT, actor_participant=None, **kwargs):
        actor_set = False
        if actor is None:
            if actor_name in self._actors:
                del self._actors[actor_name]
            return super().set_actor(actor_name, None)
        if suffix is DEFAULT:
            suffix = actor.part_suffix
        else:
            animation_actor = actor.animation_actor
            if actor_name in self._actors:
                old_actor, old_suffix, _ = self._actors[actor_name]
                if Asm._is_same_actor(old_actor, animation_actor) and old_suffix == suffix:
                    actor_set = True
                else:
                    if old_actor() is None:
                        if self._clear_actor(actor_name):
                            del self._actors[actor_name]
                            actor_set = False
                        else:
                            return False
                    else:
                        return False
            if not actor_set:
                if (super().set_actor)(actor_name, animation_actor, suffix=suffix, **kwargs):
                    self._actors[actor_name] = (
                     animation_actor.ref(), suffix, actor_participant)
                    actor_set = True
                else:
                    logger.warn('{}: Failed to set actor {} to {}:{}', self.name, actor_name, actor, suffix)
            return actor_set or False
        overrides = actor.get_anim_overrides(actor_name)
        if overrides:
            overrides.override_asmselfanimation_actorsuffix
        return True

    def _get_virtual_actor_weakref_callback(self, actor_name, actor, actor_suffix):
        actor_id = actor.id

        def _weakref_callback(*_, **__):
            self._remove_virtual_actoractor_nameactor_idactor_suffix
            self._remove_dead_virtual_actors()

        return _weakref_callback

    def add_virtual_actor(self, actor_name, actor, suffix=DEFAULT):
        actor_set = False
        if suffix is DEFAULT:
            suffix = actor.part_suffix
        else:
            animation_actor = actor.animation_actor
            if actor_name in self._virtual_actors:
                for old_actor, old_suffix in self._virtual_actors[actor_name]:
                    if Asm._is_same_actor(old_actor, animation_actor) and old_suffix == suffix:
                        actor_set = True
                        break

            if not actor_set:
                if super().add_virtual_actoractor_nameanimation_actorsuffix:
                    callback = self._get_virtual_actor_weakref_callbackactor_nameanimation_actorsuffix
                    self._virtual_actors[actor_name].add((animation_actor.ref(callback=callback), suffix))
                    actor_set = True
                else:
                    logger.warn('{}: Failed to add virtual actor {}: {}:{}', self.name, actor_name, actor, suffix)
            return actor_set or False
        overrides = actor.get_anim_overrides(actor_name)
        if overrides:
            overrides.override_asmselfanimation_actorsuffix
        return True

    def setup_part_owner(self, target, part_owner_name):
        if part_owner_name in self.actors:
            part_owner, _ = self.get_actor_and_suffix(part_owner_name)
            if part_owner is None:
                return self.set_actor(part_owner_name, target, suffix=None, actor_participant=(AnimationParticipant.CONTAINER))
        return True

    def _remove_dead_virtual_actors(self):
        deletes = []
        for key, (target_ref, _) in self._virtual_actor_relationships.items():
            target = target_ref() if target_ref is not None else None
            if target is None:
                deletes.append(key)

        for key in deletes:
            del self._virtual_actor_relationships[key]

    def remove_virtual_actor(self, name, actor, suffix=None):
        animation_actor = actor.animation_actor
        if not super().remove_virtual_actornameanimation_actorsuffix:
            return False
        self._virtual_actors[name].remove((animation_actor.ref(), suffix))
        deletes = []
        for key, (target_ref, target_suffix) in self._virtual_actor_relationships.items():
            if Asm._is_same_actor(target_ref, animation_actor) and target_suffix == suffix:
                deletes.append(key)

        for key in deletes:
            del self._virtual_actor_relationships[key]

        return True

    def remove_virtual_actors_by_name(self, name):
        actor_suffixes = self._virtual_actors.get(name)
        if actor_suffixes is not None:
            for weak_actor, suffix in tuple(actor_suffixes):
                actor = weak_actor()
                if actor is not None:
                    self.remove_virtual_actornameactorsuffix

    def specialize_virtual_actor_relationship(self, actor_name, actor, actor_suffix, target_name, target, target_suffix):
        if (
         actor_name, target_name) in self._virtual_actor_relationships:
            old_target_ref, old_target_suffix = self._virtual_actor_relationships[(actor_name, target_name)]
            if not Asm._is_same_actor(old_target_ref, target) or old_target_suffix != target_suffix:
                old_target = old_target_ref() if old_target_ref is not None else None
                if old_target is None:
                    logger.error'Virtual actor {} on {} has been garbage collected, but is still in the specialization map'target_nameself
            else:
                self.remove_virtual_actor(target_name, old_target, suffix=old_target_suffix)
        result = super().specialize_virtual_actor_relationshipactor_nameactoractor_suffixtarget_nametarget.animation_actortarget_suffix
        if result:
            self._virtual_actor_relationships[(actor_name, target_name)] = (
             target.ref(), target_suffix)
        return result

    def add_potentially_virtual_actor(self, actor_name, actor, target_name, target, part_suffix=DEFAULT, target_participant=None):
        if part_suffix is DEFAULT:
            part_suffix = target.part_suffix
        else:
            target_definition = self.get_actor_definition(target_name)
            if target_definition is None:
                logger.error"Failed to add potentially virtual actor '{}' on asm '{}'. The actor does not exist."target_nameself.name
                return False
            if target_definition.is_virtual and not self.add_virtual_actortarget_nametargetpart_suffix:
                logger.error('Failed to add virtual actor {}, suffix {} on asm {}.', target_name, part_suffix, self.name)
                return False
                if not self.specialize_virtual_actor_relationshipactor_nameactorNonetarget_nametargetpart_suffix:
                    logger.error'Failed to specialize virtual actor for (name: {}, rig: {}, suffix: {}) for ASM: {} and Sim: {}.'target_nametarget.rigpart_suffixself.nameactor
                    return False
                else:
                    if not self.set_actor(target_name, target, suffix=part_suffix, actor_participant=target_participant):
                        logger.error'Failed to set actor {} for actor name {} on asm {}. Part suffix:{}, actor_participant:{}'targettarget_nameself.namepart_suffixtarget_participant
                        return False
        return True

    def update_locked_params(self, locked_params, virtual_actor_map=None, ignore_virtual_suffix=False):
        if not locked_params:
            return
        for param_name, param_value in locked_params.items():
            actor = None
            if not isinstance(param_name, tuple):
                self.set_parameter(param_name, param_value)
                continue
            param_name, actor_name = param_name
            if not ignore_virtual_suffix:
                if actor_name in self._virtual_actors:
                    if virtual_actor_map is None or actor_name not in virtual_actor_map:
                        continue
                    actor = virtual_actor_map[actor_name]
                    if actor is None:
                        raise RuntimeError('{}: Virtual actors for {} do not include {}: {}'.format(self.name, actor_name, actor, self._virtual_actors[actor_name]))
                    suffix = self.get_suffix(actor_name, actor)
                else:
                    actor, suffix = self.get_actor_and_suffix(actor_name)
                if actor is not None:
                    self.set_actor_parameter(actor_name, actor, param_name, param_value, suffix)
                else:
                    self.set_parameter(param_name, param_value)

    def get_actor_and_suffix(self, actor_name):
        if actor_name in self._actors:
            actor, suffix, _ = self._actors[actor_name]
            actor = actor() if actor is not None else None
            return (actor, suffix)
        return (None, None)

    def get_virtual_actor_and_suffix(self, actor_name, target_name):
        if (
         actor_name, target_name) in self._virtual_actor_relationships:
            target, suffix = self._virtual_actor_relationships[(actor_name, target_name)]
            target = target() if target is not None else None
            return (target, suffix)
        return (None, None)

    def get_suffix(self, actor_name, actor):
        if actor_name in self._actors:
            existing_actor, suffix, _ = self._actors[actor_name]
            if existing_actor is not None:
                existing_actor = existing_actor()
                if existing_actor == actor:
                    return suffix
        if actor_name in self._virtual_actors:
            for existing_actor, suffix in self._virtual_actors[actor_name]:
                if existing_actor is not None:
                    existing_actor = existing_actor()
                    if existing_actor == actor:
                        return suffix

    def actors_gen(self):
        for actor, _, _ in self._actors.values():
            actor = actor() if actor is not None else None
            if actor is not None:
                yield actor

        for actor_list in self._virtual_actors.values():
            for actor, _ in actor_list:
                actor = actor() if actor is not None else None
                if actor is not None:
                    yield actor

    def actors_info_gen(self):
        for name, (actor, suffix, _) in self._actors.items():
            actor = actor() if actor is not None else None
            if actor is not None:
                yield (
                 name, actor, suffix)

        for name, actor_list in self._virtual_actors.items():
            for actor, suffix in actor_list:
                actor = actor() if actor is not None else None
                if actor is not None:
                    yield (
                     name, actor, suffix)

    def get_actor_name(self, obj):
        for name, actor, _ in self.actors_info_gen():
            if actor.id == obj.id:
                return name

    def get_all_parameters(self):
        return self._get_params()

    def _apply_posture_manifest_overrides(self, manifest: PostureManifest):
        result = manifest
        if self._posture_manifest_overrides:
            if manifest:
                result = PostureManifest()
                for entry in manifest:
                    for override_key, override_value in self._posture_manifest_overrides.items():
                        if entry.matches_override_key(override_key):
                            extra_entries = entry.get_entries_with_override(override_value)
                            result.update(extra_entries)
                        else:
                            result.add(entry)

        return result

    _provided_posture_cache = {}
    _supported_posture_cache = {}

    @property
    def provided_postures(self):
        cache_key = self.state_machine_name
        if cache_key in self._provided_posture_cache:
            manifest = self._provided_posture_cache[cache_key]
        else:
            super_manifest = super().provided_postures
            manifest = PostureManifest((PostureManifestEntry(*entry, provides=True, from_asm=True) for entry in super_manifest))
            manifest = _consolidate_carry_info2(manifest)
            self._provided_posture_cache[cache_key] = manifest.intern()
        manifest = self._apply_posture_manifest_overrides(manifest)
        return manifest

    def get_supported_postures_for_actor(self, actor_name):
        cache_key = (
         self.state_machine_name, actor_name)
        if cache_key in self._supported_posture_cache:
            manifest = self._supported_posture_cache[cache_key]
        else:
            manifest = PostureManifest((PostureManifestEntry(*entry) for entry in super().get_supported_postures_for_actor(actor_name) or ()))
            manifest = _consolidate_carry_info2(manifest)
            manifest = manifest.get_clean_manifest()
            self._supported_posture_cache[cache_key] = manifest.intern()
        manifest = self._apply_posture_manifest_overrides(manifest)
        return manifest


def get_boundary_condition_cache_debug_information():
    return [
     (
      'BC_CACHE SIZE', len(Asm._bc_cache), 'dict size of _bc_cache')]


def _format_debug_context(debug_context):
    if debug_context:
        return ' (debug context: {})'.format(debug_context)
    return ''


Asm._bc_cache.update(read_bc_cache_from_resource())