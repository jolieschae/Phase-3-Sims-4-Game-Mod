# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\waypoints\waypoint_generator_gig_objects.py
# Compiled at: 2021-03-29 01:19:32
# Size of source mod 2**32: 2321 bytes
from routing.waypoints.waypoint_generator_object_mixin import _WaypointGeneratorMultipleObjectMixin
from sims4.tuning.tunable import TunablePackSafeReference
import build_buy, sims4, services
logger = sims4.log.Logger('Waypoint Generator Gig Objets', default_owner='shipark')

class _WaypointGeneratorMultipleGigObjects(_WaypointGeneratorMultipleObjectMixin):
    FACTORY_TUNABLES = {'gig_career': TunablePackSafeReference(manager=(services.get_instance_manager(sims4.resources.Types.CAREER)))}

    def _get_objects(self):
        gig_objects = set()
        if self.gig_career is None:
            logger.error('Gig career tuning is None and cannot be.')
            return gig_objects
        sim_info = services.active_sim_info()
        gig_career = sim_info.career_tracker.get_career_by_uid(self.gig_career.guid64)
        if gig_career is None:
            logger.error('Attempting to get gig-career objects, but the active sim {} does not have career {}', sim_info, self.gig_career)
            return gig_objects
        current_gig = gig_career.get_current_gig()
        if current_gig is None:
            logger.error('Attempting to get gig-career objects, but sim {] has no active gig for career {}', sim_info, gig_career)
            return gig_objects
        customer_lot_id = current_gig.get_customer_lot_id()
        if not customer_lot_id:
            logger.error("Attempting to get gig-career objects, but there is not current let id set on sim {}'s current gig {}.", sim_info, current_gig)
            return gig_objects
        gig_objects.update(build_buy.get_gig_objects_added(customer_lot_id))
        gig_objects.difference_update(build_buy.get_gig_objects_deleted(customer_lot_id))
        return gig_objects