# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\pick_tests.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 10195 bytes
from build_buy import FloorFeatureType, is_location_outside
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from caches import cached_test
from interactions import ParticipantType
import interactions.go_here_test as go_here_test
from server.pick_info import PickTerrainType, PICK_TRAVEL, PickType
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, OptionalTunable, Tunable, TunableSet, TunableVariant, TunableEnumSet
from terrain import is_position_in_street
from world.terrain_enums import TerrainTag
import build_buy, services, terrain

class PickTerrainTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'terrain_location':TunableEnumEntry(description='\n             Terrain type to find. Note that tuning the "Can Go Here" pick type \n             will test connectivity, which can have performance implications,\n             so use sparingly. \n             ',
       tunable_type=PickTerrainType,
       default=PickTerrainType.ANYWHERE), 
     'terrain_feature':OptionalTunable(description='\n            Tune this if you want to require a floor feature to be present\n            ',
       tunable=TunableEnumEntry(tunable_type=FloorFeatureType,
       default=(FloorFeatureType.BURNT))), 
     'terrain_feature_radius':Tunable(description='\n            The radius to look for the floor feature, if one is tuned in terrain_feature\n            ',
       tunable_type=float,
       default=2.0)}

    @cached_test
    def __call__(self, context=None):
        if context is None:
            return TestResult(False, 'Interaction Context is None. Make sure this test is Tuned on an Interaction.')
            pick_info = context.pick
            if pick_info is None:
                return TestResult(False, 'PickTerrainTest cannot run without a valid pick info from the Interaction Context.')
            if pick_info.pick_type not in PICK_TRAVEL:
                return TestResult(False, 'Attempting to run a PickTerrainTest with a pick that has an invalid type.')
        else:
            if self.terrain_feature is not None:
                zone_id = services.current_zone_id()
                if not build_buy.find_floor_feature(zone_id, self.terrain_feature, pick_info.location, pick_info.routing_surface.secondary_id, self.terrain_feature_radius):
                    return TestResult(False, 'Location does not have the required floor feature.')
            if self.terrain_location == PickTerrainType.ANYWHERE:
                return TestResult.TRUE
            on_lot = services.current_zone().lot.is_position_on_lot(pick_info.location)
            if self.terrain_location == PickTerrainType.ON_LOT:
                if on_lot:
                    return TestResult.TRUE
                return TestResult(False, 'Pick Terrain is not ON_LOT as expected.')
            if self.terrain_location == PickTerrainType.OFF_LOT:
                if not on_lot:
                    return TestResult.TRUE
                return TestResult(False, 'Pick Terrain is not OFF_LOT as expected.')
            current_zone_id = services.current_zone().id
            other_zone_id = pick_info.get_zone_id_from_pick_location()
            if self.terrain_location == PickTerrainType.ON_OTHER_LOT:
                if (on_lot or other_zone_id) is not None:
                    if other_zone_id != current_zone_id:
                        return TestResult.TRUE
                return TestResult(False, 'Pick Terrain is not ON_OTHER_LOT as expected.')
            if self.terrain_location == PickTerrainType.NO_LOT:
                if other_zone_id is None:
                    return TestResult.TRUE
                return TestResult(False, 'Pick Terrain is is on a valid lot, but not expected.')
            in_street = is_position_in_street(pick_info.location)
            if self.terrain_location == PickTerrainType.IN_STREET:
                if in_street:
                    return TestResult.TRUE
                return TestResult(False, 'Pick Terrain is not IN_STREET as expected.')
            if self.terrain_location == PickTerrainType.OFF_STREET:
                if not in_street:
                    return TestResult.TRUE
                return TestResult(False, 'Pick Terrain is in the street, but not expected.')
            if self.terrain_location == PickTerrainType.IS_OUTSIDE:
                is_outside = is_location_outside(pick_info.location, pick_info.level)
                if is_outside:
                    return TestResult.TRUE
                return TestResult(False, 'Pick Terrain is not outside')
            if self.terrain_location == PickTerrainType.IN_POND or self.terrain_location == PickTerrainType.OUT_OF_POND:
                is_in_pond = bool(build_buy.get_pond_id(pick_info.location))
                if self.terrain_location == PickTerrainType.IN_POND:
                    if is_in_pond:
                        return TestResult.TRUE
                    return TestResult(False, 'Pick Terrain is not in pond.')
                if self.terrain_location == PickTerrainType.OUT_OF_POND:
                    if not is_in_pond:
                        return TestResult.TRUE
                    return TestResult(False, 'Pick Terrain in pond.')
        if self.terrain_location == PickTerrainType.CAN_GO_HERE:
            return go_here_test(None, context=context)
        return TestResult.TRUE


class PickTypeTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'whitelist':TunableSet(description='\n            A set of pick types that will pass the test if the pick type\n            matches any of them.\n            ',
       tunable=TunableEnumEntry(description='\n                A pick type.\n                ',
       tunable_type=PickType,
       default=(PickType.PICK_NONE))), 
     'blacklist':TunableSet(description='\n            A set of pick types that will fail the test if the pick type\n            matches any of them.\n            ',
       tunable=TunableEnumEntry(description='\n                A pick type.\n                ',
       tunable_type=PickType,
       default=(PickType.PICK_NONE))), 
     'terrain_tags':OptionalTunable(description='\n            If checked, will verify the location of the test is currently on\n            one of the tuned terrain tags.\n            ',
       disabled_name="Don't_Test",
       tunable=TunableEnumSet(description='\n                A set of terrain tags. Only one of these tags needs to be\n                present at this location. Although it is not tunable, there\n                is a threshold weight underneath which a terrain tag will\n                not appear to be present.\n                ',
       enum_type=TerrainTag,
       enum_default=(TerrainTag.INVALID))), 
     'prohibited_terrain_tags':OptionalTunable(description='\n            If enabled, will verify the location of the test is currently not on\n            one of the tuned terrain tags.\n            ',
       disabled_name="Don't_Test",
       tunable=TunableEnumSet(description='\n                A set of terrain tags. If any tag is present at the location, the test will fail\n                ',
       enum_type=TerrainTag,
       enum_default=(TerrainTag.INVALID)))}

    @cached_test
    def __call__(self, context=None):
        if context is None:
            return TestResult(False, 'Interaction Context is None. Make sure this test is Tuned on an Interaction.')
            pick_info = context.pick
            if pick_info is None:
                return TestResult(False, 'PickTerrainTest cannot run without a valid pick info from the Interaction Context.')
            pick_type = pick_info.pick_type
            if self.whitelist:
                if pick_type not in self.whitelist:
                    return TestResult(False, 'Pick type {} not in whitelist {}'.format(pick_type, self.whitelist))
            if pick_type in self.blacklist:
                return TestResult(False, 'Pick type {} in blacklist {}'.format(pick_type, self.blacklist))
        else:
            position = pick_info.location
            if self.terrain_tags is not None:
                if not terrain.is_terrain_tag_at_position((position.x), (position.z), (self.terrain_tags), level=(pick_info.routing_surface.secondary_id)):
                    return TestResult(False, 'Pick does not have required terrain tag.', tooltip=(self.tooltip))
            if self.prohibited_terrain_tags is not None and terrain.is_terrain_tag_at_position((position.x), (position.z), (self.prohibited_terrain_tags), level=(pick_info.routing_surface.secondary_id)):
                return TestResult(False, 'Pick has a prohibited terrain tag.', tooltip=(self.tooltip))
        return TestResult.TRUE


class PickInfoTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'pick_type_test': TunableVariant(pick_terrain=(PickTerrainTest.TunableFactory()),
                         pick_type=(PickTypeTest.TunableFactory()),
                         default='pick_terrain')}

    def get_expected_args(self):
        return {'context': ParticipantType.InteractionContext}

    @cached_test
    def __call__(self, *args, **kwargs):
        return (self.pick_type_test)(*args, **kwargs)