# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\socials\jigs\jig_type_animation.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 11229 bytes
from _math import Vector2, Transform, Vector3
from animation import get_throwaway_animation_context
from animation.animation_utils import StubActor
from animation.asm import create_asm, do_params_match
from interactions.utils.animation_reference import TunableAnimationReference
from postures import PostureTrack
from routing import FootprintType
from sims.sim_info_types import SpeciesExtended
from sims4.collections import frozendict
from sims4.geometry import PolygonFootprint
from sims4.math import yaw_quaternion_to_angle, vector3_rotate_axis_angle
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, Tunable, TunableEnumEntry
from socials.jigs.jig_utils import get_default_reserve_space, generate_jig_polygon, _generate_poly_points, JigPositioning

class SocialJigAnimation(AutoFactoryInit, HasTunableSingletonFactory):

    @staticmethod
    def on_tunable_loaded_callback(instance_class, tunable_name, source, value):
        animation_element = value.canonical_animation
        asm_key = animation_element.asm_key
        actor_name = animation_element.actor_name
        target_name = animation_element.target_name
        state_name = animation_element.begin_states[0]
        actor = StubActor(1)
        target = StubActor(2)
        animation_context = get_throwaway_animation_context()
        asm = create_asm(asm_key, context=animation_context)
        asm.set_actor(actor_name, actor)
        asm.set_actor(target_name, target)
        for posture_manifest_entry in asm.get_supported_postures_for_actor(actor_name).get_constraint_version():
            for posture_type in posture_manifest_entry.posture_types:
                if posture_type.mobile:
                    break
            else:
                continue

            break
        else:
            posture_type = None

        available_transforms = []
        if posture_type is not None:
            posture = posture_type(actor, None, (PostureTrack.BODY), animation_context=animation_context)
            boundary_conditions = asm.get_boundary_conditions_list(actor, state_name, posture=posture, target=target)
            for _, slots_to_params_entry in boundary_conditions:
                if not slots_to_params_entry:
                    continue
                for boundary_condition_entry, param_sequences_entry in slots_to_params_entry:
                    relative_transform, _, _, _ = boundary_condition_entry.get_transforms(asm, target)
                    available_transforms.append((param_sequences_entry, relative_transform))

        setattr(value, 'available_transforms', available_transforms)

    FACTORY_TUNABLES = {'canonical_animation':TunableAnimationReference(description="\n            The canonical animation element used to generate social positioning\n            for this group.\n            \n            The animation must include a target actor (such as 'y') whose\n            relative positioning from an actor, such as 'x' defines the\n            positioning.\n            ",
       callback=None), 
     'reverse_actor_sim_orientation':Tunable(description='\n            If checked then we will reverse the orientation of the actor Sim\n            when generating this jig. \n            ',
       tunable_type=bool,
       default=False), 
     'ignore_posture_jig':Tunable(description='\n            If checked, we will ignore the posture jigs of actor and target sims\n            on finding a good location for the social jig.\n            ',
       tunable_type=bool,
       default=False), 
     'jig_positioning_type':TunableEnumEntry(description='\n            Determines the type of positioning used for this Jig.\n            The other sim will come over to the relative sim.\n            ',
       tunable_type=JigPositioning,
       default=JigPositioning.RelativeToSimB), 
     'callback':on_tunable_loaded_callback}

    def _get_available_transforms_gen--- This code section failed: ---

 L. 129         0  LOAD_FAST                'self'
                2  LOAD_ATTR                canonical_animation
                4  STORE_FAST               'animation_element'

 L. 131         6  LOAD_FAST                'animation_element'
                8  LOAD_ATTR                actor_name
               10  STORE_FAST               'actor_name'

 L. 132        12  LOAD_FAST                'animation_element'
               14  LOAD_ATTR                target_name
               16  STORE_FAST               'target_name'

 L. 136        18  LOAD_FAST                'actor'
               20  LOAD_ATTR                age
               22  LOAD_ATTR                age_for_animation_cache
               24  STORE_FAST               'actor_age'

 L. 137        26  LOAD_FAST                'target'
               28  LOAD_ATTR                age
               30  LOAD_ATTR                age_for_animation_cache
               32  STORE_FAST               'target_age'

 L. 140        34  LOAD_STR                 'species'
               36  LOAD_FAST                'actor_name'
               38  BUILD_TUPLE_2         2 
               40  LOAD_GLOBAL              SpeciesExtended
               42  LOAD_METHOD              get_animation_species_param
               44  LOAD_FAST                'actor'
               46  LOAD_ATTR                extended_species
               48  CALL_METHOD_1         1  '1 positional argument'

 L. 141        50  LOAD_STR                 'age'
               52  LOAD_FAST                'actor_name'
               54  BUILD_TUPLE_2         2 
               56  LOAD_FAST                'actor_age'
               58  LOAD_ATTR                animation_age_param

 L. 142        60  LOAD_STR                 'species'
               62  LOAD_FAST                'target_name'
               64  BUILD_TUPLE_2         2 
               66  LOAD_GLOBAL              SpeciesExtended
               68  LOAD_METHOD              get_animation_species_param
               70  LOAD_FAST                'target'
               72  LOAD_ATTR                extended_species
               74  CALL_METHOD_1         1  '1 positional argument'

 L. 143        76  LOAD_STR                 'age'
               78  LOAD_FAST                'target_name'
               80  BUILD_TUPLE_2         2 
               82  LOAD_FAST                'target_age'
               84  LOAD_ATTR                animation_age_param
               86  BUILD_MAP_4           4 
               88  STORE_DEREF              'locked_params'

 L. 146        90  SETUP_LOOP          172  'to 172'
               92  LOAD_FAST                'self'
               94  LOAD_ATTR                available_transforms
               96  GET_ITER         
               98  FOR_ITER            170  'to 170'
              100  UNPACK_SEQUENCE_2     2 
              102  STORE_FAST               'param_sequences'
              104  STORE_FAST               'transform'

 L. 147       106  SETUP_LOOP          168  'to 168'
              108  LOAD_FAST                'param_sequences'
              110  GET_ITER         
              112  FOR_ITER            166  'to 166'
              114  STORE_FAST               'param_sequence'

 L. 148       116  LOAD_GLOBAL              do_params_match
              118  LOAD_FAST                'param_sequence'
              120  LOAD_DEREF               'locked_params'
              122  CALL_FUNCTION_2       2  '2 positional arguments'
              124  POP_JUMP_IF_TRUE    128  'to 128'

 L. 149       126  CONTINUE            112  'to 112'
            128_0  COME_FROM           124  '124'

 L. 150       128  LOAD_GLOBAL              frozendict
              130  LOAD_CLOSURE             'locked_params'
              132  BUILD_TUPLE_1         1 
              134  LOAD_DICTCOMP            '<code_object <dictcomp>>'
              136  LOAD_STR                 'SocialJigAnimation._get_available_transforms_gen.<locals>.<dictcomp>'
              138  MAKE_FUNCTION_8          'closure'
              140  LOAD_FAST                'param_sequence'
              142  LOAD_METHOD              items
              144  CALL_METHOD_0         0  '0 positional arguments'
              146  GET_ITER         
              148  CALL_FUNCTION_1       1  '1 positional argument'
              150  CALL_FUNCTION_1       1  '1 positional argument'
              152  STORE_FAST               'jig_params'

 L. 151       154  LOAD_FAST                'transform'
              156  LOAD_FAST                'jig_params'
              158  BUILD_TUPLE_2         2 
              160  YIELD_VALUE      
              162  POP_TOP          
              164  JUMP_BACK           112  'to 112'
              166  POP_BLOCK        
            168_0  COME_FROM_LOOP      106  '106'
              168  JUMP_BACK            98  'to 98'
              170  POP_BLOCK        
            172_0  COME_FROM_LOOP       90  '90'

Parse error at or near `LOAD_DICTCOMP' instruction at offset 134

    def get_transforms_gen(self, actor, target, fallback_routing_surface=None, fgl_kwargs=None, **kwargs):
        reserved_space_a = get_default_reserve_spaceactor.speciesactor.age
        reserved_space_b = get_default_reserve_spacetarget.speciestarget.age
        fgl_kwargs = fgl_kwargs if fgl_kwargs is not None else {}
        ignored_objects = {actor.id, target.id}
        ignored_ids = fgl_kwargs.get('ignored_object_ids')
        if self.ignore_posture_jig:
            if actor.posture._jig_instance is not None:
                ignored_objects.add(actor.posture._jig_instance.id)
            if target.posture._jig_instance is not None:
                ignored_objects.add(target.posture._jig_instance.id)
        if ignored_ids is not None:
            ignored_objects.update(ignored_ids)
        fgl_kwargs['ignored_object_ids'] = ignored_objects
        for transform, jig_params in self._get_available_transforms_gen(actor, target):
            actor_angle = yaw_quaternion_to_angle(transform.orientation)
            if self.jig_positioning_type == JigPositioning.RelativeToSimA:
                pos_a = Vector2.ZERO()
                rot_a = 0
                pos_b = vector3_rotate_axis_angle(-1 * transform.translation, -actor_angle, Vector3.Y_AXIS())
                rot_b = -actor_angle
            else:
                pos_a = transform.translation
                rot_a = actor_angle
                pos_b = Vector2.ZERO()
                rot_b = 0
            translation_a, orientation_a, translation_b, orientation_b, routing_surface = generate_jig_polygon(actor.location, pos_a, rot_a, target.location, pos_b, rot_b,
 reserved_space_a.left, reserved_space_a.right, reserved_space_a.front, reserved_space_a.back,
 reserved_space_b.left, reserved_space_b.right, reserved_space_b.front, reserved_space_b.back, fallback_routing_surface=fallback_routing_surface, 
             reverse_nonreletive_sim_orientation=self.reverse_actor_sim_orientation, 
             positioning_type=self.jig_positioning_type, **fgl_kwargs)
            if translation_a is None:
                continue
            yield (
             Transformtranslation_aorientation_a, Transformtranslation_borientation_b, routing_surface, jig_params)

    def get_footprint_polygon(self, sim_a, sim_b, sim_a_transform, sim_b_transform, routing_surface):
        reserved_space_a = get_default_reserve_spacesim_a.speciessim_a.age
        reserved_space_b = get_default_reserve_spacesim_b.speciessim_b.age
        polygon = _generate_poly_points(sim_a_transform.translation, sim_a_transform.orientation.transform_vector(Vector3.Z_AXIS()), sim_b_transform.translation, sim_b_transform.orientation.transform_vector(Vector3.Z_AXIS()), reserved_space_a.left, reserved_space_a.right, reserved_space_a.front, reserved_space_a.back, reserved_space_b.left, reserved_space_b.right, reserved_space_b.front, reserved_space_b.back)
        return PolygonFootprint(polygon, routing_surface=(sim_a.routing_surface), cost=25, footprint_type=(FootprintType.FOOTPRINT_TYPE_OBJECT), enabled=True)