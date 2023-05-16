# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\portals\portal_data_animation.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 8660 bytes
from _math import Transform
from protocolbuffers import Routing_pb2 as routing_protocols
import build_buy, services, sims4, sims4.math
from animation import get_throwaway_animation_context
from animation.animation_utils import StubActor
from animation.arb import Arb
from animation.asm import create_asm
from routing import Location
from routing.portals.portal_data_base import _PortalTypeDataBase
from routing.portals.portal_location import _PortalBoneLocation
from routing.portals.portal_tuning import PortalType
from sims4.tuning.tunable import TunableReference, Tunable, TunableTuple, OptionalTunable, TunableVariant
PORTAL_ANIMATION = 0
PORTAL_BONES = 1
PORTAL_ONE_WAY_ONLY = 2

class _PortalTypeDataAnimation(_PortalTypeDataBase):
    FACTORY_TUNABLES = {'animation_element':TunableReference(description='\n            The animation to play when a Sim traverses this portal.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.ANIMATION)), 
     'requires_los_between_entry_and_exit':Tunable(description='\n            If checked, this portal will only be valid if there is LOS between\n            the entry and exit points. If unchecked, LOS is not required.\n            ',
       tunable_type=bool,
       default=True), 
     'requires_height_check':Tunable(description="\n            If checked, We will check height between the portal points and the object's location. \n            If either the portal entry point or the portal exit point is at a location whose y \n            position differs by more than portal_height_offset_threshold from the object's, \n            the portal is not created. \n            Portal_height_offset_threshold is tuned at Native Build Buy Tuning.\n            ",
       tunable_type=bool,
       default=False), 
     'go_there_locations':OptionalTunable(tunable=TunableTuple(description="\n                Location tunables for entering through the portal. Talk to your GPE partner if you're unsure which direction is which. \n                ",
       there_start=_PortalBoneLocation.TunableFactory(description='\n                    The location where entering through the portal starts.\n                    '),
       there_end=_PortalBoneLocation.TunableFactory(description='\n                    The location where entering through the portal ends.\n                    ')),
       disabled_name='use_animation_boundaries',
       enabled_name='use_bone_locations'), 
     'go_back_locations':TunableVariant(description="\n                Location tunables for exiting through the portal. Talk to your GPE partner if you're unsure which direction is which.",
       animation_back_portal=TunableTuple(description="\n                Location tunables for exiting through the portal using animation constraints. Talk to your GPE partner if you're unsure which direction is which.\n                ",
       locked_args={'option': PORTAL_ANIMATION}),
       bone_back_portal=TunableTuple(description="\n                Location tunables for exiting through the portal using bones. Talk to your GPE partner if you're unsure which direction is which.\n                ",
       back_start=_PortalBoneLocation.TunableFactory(description='\n                    The location where exiting through the portal starts.\n                    '),
       back_end=_PortalBoneLocation.TunableFactory(description='\n                    The location where exiting through the portal ends.\n                    '),
       locked_args={'option': PORTAL_BONES}),
       one_way_only=TunableTuple(description='\n                    Ignores the back portal and makes this object one way only.',
       locked_args={'option': PORTAL_ONE_WAY_ONLY}),
       default='animation_back_portal')}

    @property
    def portal_type(self):
        return PortalType.PortalType_Animate

    @property
    def requires_los_between_points(self):
        return self.requires_los_between_entry_and_exit

    def _get_arb(self, actor, obj, *, is_mirrored):
        arb = Arb()
        asm = create_asm((self.animation_element.asm_key), context=(get_throwaway_animation_context()))
        asm.set_actor(self.animation_element.actor_name, actor)
        asm.set_actor(self.animation_element.target_name, obj)
        asm.set_parameter('isMirrored', is_mirrored)
        self.animation_element.append_to_arb(asm, arb)
        return arb

    def add_portal_data(self, actor, portal_instance, is_mirrored, walkstyle):
        arb = self._get_arb(actor, (portal_instance.obj), is_mirrored=is_mirrored)
        op = routing_protocols.RouteAnimateData()
        op.arb_data = arb._bytes()
        node_data = routing_protocols.RouteNodeData()
        node_data.type = routing_protocols.RouteNodeData.DATA_ANIMATE
        node_data.data = op.SerializeToString()
        return node_data

    def get_portal_duration(self, portal_instance, is_mirrored, walkstyle, age, gender, species):
        actor = StubActor(1, species=species)
        arb = self._get_arb(actor, (portal_instance.obj), is_mirrored=is_mirrored)
        _, duration, _ = arb.get_timing()
        return duration

    def get_portal_locations(self, obj):
        locations = []
        actor = StubActor(1)
        if self.go_there_locations is None:
            there_entry, there_exit = self._set_animation_portal(actor, obj, False)
        else:
            there_entry = self.go_there_locations.there_start(obj)
            there_exit = self.go_there_locations.there_end(obj)
        if self.go_back_locations.option == PORTAL_ANIMATION:
            back_entry, back_exit = self._set_animation_portal(actor, obj, True)
        else:
            if self.go_back_locations.option == PORTAL_BONES:
                back_entry = self.go_back_locations.back_start(obj)
                back_exit = self.go_back_locations.back_end(obj)
            elif self.requires_height_check and (self.is_offset_from_object(there_entry, obj, build_buy.get_portal_height_offset_threshold()) or self.is_offset_from_object(there_exit, obj, build_buy.get_portal_height_offset_threshold())) or self.go_back_locations.option != PORTAL_ONE_WAY_ONLY:
                locations.append((there_entry, there_exit, back_entry, back_exit, 0))
            else:
                locations.append((there_entry, there_exit, None, None, 0))
            return locations

    def _set_animation_portal(self, actor, obj, isMirrored):
        arb = self._get_arb(actor, obj, is_mirrored=isMirrored)
        boundary_condition = arb.get_boundary_conditions(actor)
        entry_loc = Transform.concatenate(boundary_condition.pre_condition_transform, obj.transform)
        entry_loc = Location((entry_loc.translation), orientation=(entry_loc.orientation), routing_surface=(obj.routing_surface))
        exit_loc = Transform.concatenate(boundary_condition.post_condition_transform, obj.transform)
        exit_loc = Location((exit_loc.translation), orientation=(exit_loc.orientation), routing_surface=(obj.routing_surface))
        return (entry_loc, exit_loc)