# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\teleport_liability.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 8022 bytes
from interactions.liability import Liability
from placement import FindGoodLocationContext, ScoringFunctionPolygon, FGLSearchFlag, FGLSearchFlagsDefault, create_starting_location, WaterDepthInfo
from sims4.geometry import CompoundPolygon
from sims4.tuning.tunable import AutoFactoryInit, HasTunableFactory, TunableReference, Tunable, OptionalTunable
import services, sims4.resources

class TeleportLiability(Liability, HasTunableFactory, AutoFactoryInit):
    LIABILITY_TOKEN = 'TeleportLiability'
    FACTORY_TUNABLES = {'on_success_affordance':TunableReference(description='\n            If specified, the affordance to push if the teleportation was\n            successful.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION)), 
     'on_failure_affordance':TunableReference(description='\n            If specified, the affordance to push if the teleportation failed or\n            if on_success_affordance is specified and failed to execute.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION)), 
     'stay_in_connected_connectivity_group':Tunable(description='\n            If checked, the Sim will only be able to teleport to the \n            "connected" areas.\n\n            If unchecked, ignores the "connected" areas the Sim is able to\n            teleport to. For example, if a Sim tries to age up while standing\n            on a platform, then the Sim will be able to teleport to areas\n            that would have been "unconnected" to complete the interaction.\n            ',
       tunable_type=bool,
       default=True), 
     'require_target_for_teleport':Tunable(description='\n            If checked, the interaction will require a target sim for the actor\n            sim to teleport to. For example, for death, the reaper may need to\n            teleport to the dying target sim.\n            ',
       tunable_type=bool,
       default=True), 
     'height_tolerance':OptionalTunable(description='\n            If enabled, the maximum height tolerance on the terrain we will use\n            for the placement of this object when asking FGL to find a spot on \n            the floor. This is used to prevent teleportation on sloped terrain.\n            \n            If disabled, FGL will use the default (0.035m).\n            ',
       tunable=Tunable(tunable_type=float, default=0.1)), 
     'should_test_build_buy':Tunable(description='\n            If checked, the placement quadtree will be checked in addition to\n            the routing navmesh when teleporting the sim.  \n            ',
       tunable_type=bool,
       default=True)}

    def __init__(self, interaction, **kwargs):
        (super().__init__)(**kwargs)
        self._interaction = interaction
        self._interaction.route_fail_on_transition_fail = False
        self._constraint = self._interaction.constraint_intersection()

    @classmethod
    def on_affordance_loaded_callback(cls, affordance, liability_tuning):
        affordance.disable_distance_estimation_and_posture_checks = True

    def release(self):
        if self._interaction.transition_failed:
            if self._teleport():
                if self.on_success_affordance is not None:
                    if self._interaction.sim.push_super_affordance(self.on_success_affordance, self._interaction.target, self._interaction.context):
                        return
            if self.on_failure_affordance is not None:
                self._interaction.sim.push_super_affordance(self.on_failure_affordance, self._interaction.target, self._interaction.context)

    def _teleport(self):
        polygon = None if self._constraint.geometry is None else self._constraint.geometry.polygon
        if polygon:
            if isinstance(polygon, CompoundPolygon):
                scoring_functions = [ScoringFunctionPolygon(cp) for cp in polygon]
            else:
                scoring_functions = (
                 ScoringFunctionPolygon(polygon),)
            search_flags = FGLSearchFlagsDefault | FGLSearchFlag.USE_SIM_FOOTPRINT
            if self.should_test_build_buy:
                search_flags |= FGLSearchFlag.SHOULD_TEST_BUILDBUY
            if not self.stay_in_connected_connectivity_group:
                search_flags &= ~FGLSearchFlag.STAY_IN_CONNECTED_CONNECTIVITY_GROUP
            routing_surface = self._constraint.routing_surface
            target_object = self._interaction.get_constraint_target(self._interaction.target)
            if target_object is None:
                if self.require_target_for_teleport:
                    return True
            water_depth_info = WaterDepthInfo(min_water_depth=(self._constraint.get_min_water_depth()), max_water_depth=(self._constraint.get_max_water_depth()))
            obj_id = self._interaction.sim.id
            obj_def_state_index = self._interaction.sim.state_index
            starting_location = create_starting_location(position=(self._constraint.average_position), routing_surface=routing_surface)
            fgl_context = FindGoodLocationContext(starting_location, scoring_functions=scoring_functions,
              object_id=obj_id,
              object_def_state_index=obj_def_state_index,
              search_flags=search_flags,
              routing_context=(self._interaction.sim.routing_context),
              water_depth_info=water_depth_info,
              height_tolerance=(self.height_tolerance))
            translation, orientation, _ = fgl_context.find_good_location()
            if translation is not None:
                if orientation is not None:
                    self._interaction.sim.move_to(translation=translation, orientation=orientation,
                      routing_surface=routing_surface)
                    return True
        return False