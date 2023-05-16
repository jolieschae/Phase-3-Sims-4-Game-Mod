# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\path_planner\path_plan_context.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 16355 bytes
from _math import Vector2, Vector3
import sims4
from routing import PathPlanContext
from routing.path_planner.path_plan_enums import AllowedHeightsFootprintKeyMaskBits, WadingFootprintKeyMaskBits
from routing.portals.portal_tuning import PortalFlags
from routing.walkstyle.walkstyle_behavior import WalksStyleBehavior
from sims.sim_info_types import SpeciesExtended, Age
from sims4.geometry import QtCircle, build_rectangle_from_two_points_and_radius
from sims4.tuning.tunable import AutoFactoryInit, HasTunableFactory, TunableRange, OptionalTunable, TunableEnumFlags, HasTunableSingletonFactory, TunableVariant, TunableEnumEntry, TunableMapping, Tunable, TunableList
from singletons import DEFAULT
import placement, routing, services
from terrain import get_water_depth_at_location
logger = sims4.log.Logger('PathPlanContext', default_owner='skorman')
DEFAULT_REQUIRED_HEIGHT_CLEARANCE = 0.0

class PathPlanContextWrapper(HasTunableFactory, AutoFactoryInit, PathPlanContext):

    class _AgentShapeCircle(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'radius': TunableRange(description="\n                The circle's radius, The circle is built around the agent's\n                center point.\n                ",
                     tunable_type=float,
                     minimum=0,
                     default=0.123)}

        def get_quadtree_polygon(self, position, orientation):
            return QtCircle(Vector2(position.x, position.z), self.radius)

    class _AgentShapeRectangle(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'length':TunableRange(description="\n                The rectangle's length. This is parallel to the agent's forward\n                vector.\n                ",
           tunable_type=float,
           minimum=0,
           default=1.5), 
         'width':TunableRange(description="\n                The rectangle's width. This is perpendicular to the agent's\n                forward vector.\n                ",
           tunable_type=float,
           minimum=0,
           default=0.5)}

        def get_quadtree_polygon(self, position, orientation):
            length_vector = orientation.transform_vector(Vector3.Z_AXIS()) * self.length / 2
            return build_rectangle_from_two_points_and_radius(position + length_vector, position - length_vector, self.width)

    FACTORY_TUNABLES = {'_agent_radius':TunableRange(description='\n            The size of the agent (as a circle radius), when computing a path.\n            This determines how much space is required for the agent to route\n            through space.\n            ',
       tunable_type=float,
       minimum=0,
       default=0.123), 
     '_agent_shape':TunableVariant(description="\n            The shape used to represent the agent's position and intended\n            position in the quadtree.\n            ",
       circle=_AgentShapeCircle.TunableFactory(),
       rectangle=_AgentShapeRectangle.TunableFactory(),
       default='circle'), 
     '_agent_goal_radius':TunableRange(description='\n            The clearance required (as a circle radius) at the end of a route.\n            ',
       tunable_type=float,
       minimum=0,
       default=0.123), 
     '_agent_extra_clearance_modifier':TunableRange(description="\n            The clearance that the agent will try to maintain from other objects\n            (and go around them), defined as a multiple of the agent's radius.\n            ",
       tunable_type=float,
       minimum=0,
       default=2.5), 
     '_agent_height_clearance_override':OptionalTunable(description="\n            If enabled, use a specified float value when calculating the\n            height of the object. If disabled, use the object's footprint\n            to determine the height. This tuning is required for sims,\n            since they don't use footprints.\n            ",
       tunable=Tunable(tunable_type=float, default=0.0),
       disabled_name='use_footprint_height'), 
     '_max_slope_angle':OptionalTunable(description='\n            If set (non-zero), specifies the maximum terrain angle an \n            agent is allowed to route through. Tuned in degrees, \n            stored in the client as radians.\n            ',
       tunable=Tunable(tunable_type=float, default=0.0)), 
     '_allowed_portal_flags':OptionalTunable(TunableEnumFlags(description='\n                Required portal flags can be set on portals. If these flags are\n                also set on the actor, then that actor is allowed to traverse\n                that portal type.\n                \n                e.g. Counter Surface portals have the "Counter" flag set on the\n                portals. If the "Counter" flag is set on a routing context, then\n                your able to go through counter portals.\n                ',
       enum_type=PortalFlags)), 
     '_discouraged_portal_flags':OptionalTunable(TunableEnumFlags(description="\n                Flags to set on the Sim to match the discouragement flags on\n                a portal.  If the flags don't match, the Sim will be \n                discouraged from routing through this portal. \n                \n                e.g. Regular doors have a discouragement flag that matches\n                only humans, this way pets will try to use pet doors over \n                regular doors.\n                ",
       enum_type=PortalFlags)), 
     '_allowed_heights':OptionalTunable(TunableEnumFlags(description='\n                All of the flags that define what this agent is able to route\n                under. Each Flag has a specific height assigned to it.\n                \n                FOOTPRINT_KEY_REQUIRE_SMALL_HEIGHT = 0.5m\n                FOOTPRINT_KEY_REQUIRE_TINY_HEIGHT = 0.25m\n                FOOTPRINT_KEY_REQUIRE_FLOATING = flying agent\n                ',
       enum_type=AllowedHeightsFootprintKeyMaskBits,
       default=(AllowedHeightsFootprintKeyMaskBits.SMALL_HEIGHT))), 
     'surface_preference_scoring':TunableMapping(description='\n            Surface type and additional score to apply to the cost of goals on \n            this surface.\n            This allows for geometric constraints with multi surface goals, to \n            have preference to specific surface types. i.e Cats always prefer\n            to target surface object goals, so we make the ground more \n            expensive.\n            This will only be applied for multi surface geometric constraints.\n            ',
       key_type=TunableEnumEntry(description='\n                The surface type for scoring to be applied to.\n                ',
       tunable_type=(routing.SurfaceType),
       default=(routing.SurfaceType.SURFACETYPE_WORLD),
       invalid_enums=(
      routing.SurfaceType.SURFACETYPE_UNKNOWN,)),
       value_type=TunableRange(description='\n                Additive cost to apply when calculating goals for multi surface \n                constraints.\n                ',
       tunable_type=float,
       default=10,
       minimum=0)), 
     '_allowed_wading_depths':OptionalTunable(TunableEnumFlags(description='\n                Flags that define the wading depth this agent is able to route\n                through. Each flag has a specific depth assigned to it. \n                \n                If disabled, the agent will not be allowed to wade through \n                water entities that consider these flags. Currently these flags \n                are only considered when routing through ponds.\n                \n                WADING_DEEP  = 0.7m\n                WADING_MEDIUM  = 0.5m\n                WADING_SHALLOW  = 0.35m\n                WADING_VERY_SHALLOW = 0.15m\n                ',
       enum_type=WadingFootprintKeyMaskBits,
       default=(WadingFootprintKeyMaskBits.WADING_MEDIUM)))}

    def __init__(self, agent, **kwargs):
        (super().__init__)(**kwargs)
        self._agent = agent
        self.agent_id = agent.id
        self.agent_radius = self._agent_radius
        self.agent_extra_clearance_multiplier = self._agent_extra_clearance_modifier
        self.agent_goal_radius = self._agent_goal_radius
        self.footprint_key = agent.definition.get_footprint(0)
        self.add_path_boundary_obstacle = False
        if self._agent_height_clearance_override is not None:
            self.agent_height_clearance_override = self._agent_height_clearance_override
        else:
            self.agent_height_clearance_override = -1.0
        if self._max_slope_angle is not None:
            self.max_slope_angle = self._max_slope_angle
        full_keymask = routing.FOOTPRINT_KEY_ON_LOT | routing.FOOTPRINT_KEY_OFF_LOT
        if self._allowed_heights is not None:
            full_keymask |= self._allowed_heights
        full_keymask |= self.get_height_clearance_key_mask_flags(self.agent_height_clearance_override)
        if self._allowed_wading_depths is not None:
            full_keymask |= self._allowed_wading_depths
        self.set_key_mask(full_keymask)
        full_portal_keymask = PortalFlags.DEFAULT
        species = getattr(self._agent, 'extended_species', DEFAULT)
        full_portal_keymask |= SpeciesExtended.get_portal_flag(species)
        age = getattr(self._agent, 'age', DEFAULT)
        full_portal_keymask |= Age.get_portal_flag(age)
        if self._allowed_portal_flags is not None:
            full_portal_keymask |= self._allowed_portal_flags
        full_portal_keymask |= self.get_height_clearance_portal_keymask(full_keymask)
        self.set_portal_key_mask(full_portal_keymask)
        portal_discouragement_flags = 0
        if self._discouraged_portal_flags is not None:
            portal_discouragement_flags |= self._discouraged_portal_flags
        self.set_portal_discourage_key_mask(portal_discouragement_flags)
        self.route_fail_on_fake_portals = False

    def get_quadtree_polygon(self, position=DEFAULT, orientation=DEFAULT):
        position = self._agent.position if position is DEFAULT else position
        orientation = self._agent.orientation if orientation is DEFAULT else orientation
        return self._agent_shape.get_quadtree_polygon(position, orientation)

    def add_location_to_quadtree(self, placement_type, position=DEFAULT, orientation=DEFAULT, routing_surface=DEFAULT, index=0):
        position = self._agent.position if position is DEFAULT else position
        orientation = self._agent.orientation if orientation is DEFAULT else orientation
        routing_surface = self._agent.routing_surface if routing_surface is DEFAULT else routing_surface
        if placement_type in (placement.ItemType.SIM_POSITION, placement.ItemType.SIM_INTENDED_POSITION):
            quadtree_geometry = self.get_quadtree_polygon(position=position, orientation=orientation)
        else:
            quadtree_geometry = QtCircle(Vector2(position.x, position.z), self.agent_goal_radius)
        services.sim_quadtree().insert(self._agent, self._agent.id, placement_type, quadtree_geometry, routing_surface, False, index)

    def remove_location_from_quadtree(self, placement_type, index=0):
        services.sim_quadtree().remove(self._agent.id, placement_type, index)

    def get_required_height_clearance(self, additional_head_room=0):
        if self._agent_height_clearance_override is not None:
            height_clearance = self._agent_height_clearance_override
        else:
            try:
                height_clearance = placement.get_object_height(self.footprint_key)
            except ValueError:
                logger.error("Unable to get object height from footprint key {}. Consider specifying agent height clearance overrides in the object's path plan context tuning.", self.footprint_key)
                height_clearance = DEFAULT_REQUIRED_HEIGHT_CLEARANCE

            return height_clearance + additional_head_room

    @property
    def max_allowed_wading_depth(self):
        return self.get_max_wading_depth(self.get_key_mask())

    def try_update_allowed_wading_depth_flags(self, new_flags):
        key_mask = self.get_key_mask()
        if self._allowed_wading_depths is not None:
            key_mask &= ~self._allowed_wading_depths
        if new_flags is not None:
            key_mask |= new_flags
        intended_location = self._agent.intended_location
        if get_water_depth_at_location(intended_location) > self.get_max_wading_depth(key_mask):
            return False
        self.set_key_mask(key_mask)
        return True

    def handle_update_walkstyle(self, walkstyle=None):
        if walkstyle is None:
            self.route_fail_on_fake_portals = False
            return
        self.route_fail_on_fake_portals = walkstyle in WalksStyleBehavior.WALKSTYLES_RESTRICTED_FROM_SINGLE_STEPS