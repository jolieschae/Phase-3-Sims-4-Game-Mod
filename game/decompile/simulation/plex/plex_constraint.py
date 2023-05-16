# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\plex\plex_constraint.py
# Compiled at: 2020-03-05 21:37:27
# Size of source mod 2**32: 2655 bytes
from interactions.constraints import Nowhere, Constraint, ANYWHERE
from sims4.geometry import CompoundPolygon, RestrictedPolygon
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableVariant, TunableTuple
from singletons import DEFAULT
import services, sims4.log
logger = sims4.log.Logger('PlexConstraint', default_owner='tingyul')

class PlexConstraint(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'non_plex_constraint': TunableVariant(description="\n            What the behavior of this constraint should be if it's used from\n            not a plex.\n            ",
                              anywhere=TunableTuple(description='\n                Use Anywhere constraint. This effectively means this plex\n                constraint does nothing if the player is not on a plex zone.\n                ',
                              locked_args={'constraint': ANYWHERE}),
                              nowhere=TunableTuple(description='\n                Use Nowhere constraint. This effectively makes this plex\n                constraint unsatisfiable if the player is not on a plex zone.\n                ',
                              locked_args={'constraint': Nowhere('PlexConstraint: non-plex zone')}),
                              default='anywhere')}

    def create_constraint(self, sim, target=None, target_position=DEFAULT, routing_surface=DEFAULT, **kwargs):
        if target is None:
            target = sim
        else:
            if routing_surface is DEFAULT:
                routing_surface = target.intended_routing_surface
            else:
                plex_service = services.get_plex_service()
                zone_id = services.current_zone_id()
                return plex_service.is_zone_a_plex(zone_id) or self.non_plex_constraint.constraint
            level = routing_surface.secondary_id
            polygons = plex_service.get_plex_polygons(level)
            return polygons or Nowhere('PlexConstraint: plex {} not on level {}', zone_id, level)
        compound_polygon = CompoundPolygon(polygons)
        restricted_polygon = RestrictedPolygon(compound_polygon, [])
        constraint = Constraint(geometry=restricted_polygon,
          routing_surface=routing_surface,
          debug_name=('Plex zone id: {}, level: {}'.format(zone_id, level)))
        return constraint