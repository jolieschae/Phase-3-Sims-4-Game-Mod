# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\utils\stored_actor_location_helpers.py
# Compiled at: 2021-01-21 01:32:02
# Size of source mod 2**32: 2952 bytes
import routing, services
from event_testing.results import TestResult
from event_testing.tests import TunableTestSet
from interactions.base.basic import TunableBasicContentSet
from interactions.utils.satisfy_constraint_interaction import SitOrStandSuperInteraction
from objects.components import types
from objects.components.stored_actor_location_component import StoredActorLocationTuning
from routing import Location
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import HasTunableFactory

class GoToStoredLocationSuperInteraction(SitOrStandSuperInteraction, HasTunableFactory):
    INSTANCE_TUNABLES = {'basic_content': TunableBasicContentSet(no_content=True,
                        default='no_content')}

    @classmethod
    def _test(cls, target, context, slot=None, **kwargs):
        if target is None:
            return TestResult(False, 'Target is None and cannot be.')
        else:
            stored_actor_location_component = target.get_component(types.STORED_ACTOR_LOCATION_COMPONENT)
            if stored_actor_location_component is None:
                return TestResult(False, 'Attempting to test routability against a location stored on an object {} without the Stored Actor Location Component.')
            location = stored_actor_location_component.get_stored_location()
            if location is None:
                return TestResult(False, 'Stored Actor Location Component does not have a stored location.')
            lot = services.active_lot()
            position = location.translation
            if not lot.is_position_on_lot(position):
                return TestResult(False, 'Stored location is not on the active lot.', tooltip=(StoredActorLocationTuning.UNROUTABLE_MESSAGE_OFF_LOT))
            routing_location = routing.Location(position, location.orientation, location.routing_surface)
            return routing.test_connectivity_pt_pt(context.sim.routing_location, routing_location, context.sim.routing_context) or TestResult(False, 'Stored location is not routable.', tooltip=(StoredActorLocationTuning.UNROUTABLE_MESSAGE_NOT_CONNECTED))
        return TestResult.TRUE


lock_instance_tunables(GoToStoredLocationSuperInteraction, test_autonomous=(TunableTestSet.DEFAULT_LIST),
  allow_autonomous=False)