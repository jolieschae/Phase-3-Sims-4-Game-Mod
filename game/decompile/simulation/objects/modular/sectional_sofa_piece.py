# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\modular\sectional_sofa_piece.py
# Compiled at: 2021-04-13 19:58:27
# Size of source mod 2**32: 14058 bytes
import weakref
from _sims4_collections import frozendict
import routing
from objects.game_object import GameObject
from objects.part import Part
from objects.parts.part_data import DynamicPartData, PartAdjacency
from sims4.math import Transform
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableMapping
from sims4.tuning.tunable_hash import TunableStringHash32

class SectionalSofaPartAnimationProxy:

    def __init__(self, proxied_part, id_override):
        self._proxied_part = proxied_part
        self.id = id_override

    def __getattr__(self, item):
        return getattr(self._proxied_part, item)

    def ref(self, callback=None):
        return weakref.ref(self, callback)


class SofaPiecePart(Part):
    _unproxied_attributes = Part._unproxied_attributes | {
     "'_part_key'", "'_piece'", "'_obj_part_idx'", "'_animation_proxy'", 
     "'_adjacent_parts'", "'_overlapping_parts'"}

    def __init__(self, owner, part_data, piece, obj_part_idx, part_key):
        super().__init__(owner, part_data)
        self._piece = piece
        self._obj_part_idx = obj_part_idx
        self._part_key = part_key
        self._animation_proxy = SectionalSofaPartAnimationProxy(self, piece.id)
        self._set_part_location()
        self._adjacent_parts = None
        self._overlapping_parts = None

    @property
    def part_identifier(self):
        return '{}_{}'.format(self._part_key.unhash if False else self._part_key, self._obj_part_idx)

    def __repr__(self):
        return '<part {} on {}>'.format(self.part_identifier, self.part_owner)

    def __str__(self):
        return '{}[{}]({})'.format(self.part_owner, self.part_identifier, self._piece)

    def adjacent_parts_gen(self):
        if self._adjacent_parts is None:
            self._adjacent_parts = tuple(self._parts_by_direction_gen(self._piece, self._data.adjacent_parts_by_direction))
        yield from self._adjacent_parts
        if False:
            yield None

    def get_overlapping_parts(self):
        if self._overlapping_parts is None:
            self._overlapping_parts = tuple(self._get_overlapping_parts_gen())
        return self._overlapping_parts

    def _get_overlapping_parts_gen(self):
        yield from self._piece.provided_parts
        for direction, overlapping_part_data in self._data.overlapping_parts_by_direction.items():
            yield from self._parts_by_direction_gen(self._piece, {direction: overlapping_part_data.overlapping_parts})
            if overlapping_part_data.distant_overlaps:
                if direction not in self._piece.adjacent_pieces:
                    continue
                if direction not in self._piece.adjacent_pieces:
                    continue
                piece = self._piece.adjacent_pieces[direction]
                if direction in piece.adjacent_pieces:
                    yield from self._parts_by_direction_gen(piece, {direction: overlapping_part_data.distant_overlaps})

        if False:
            yield None

    def _parts_by_direction_gen(self, piece, parts_by_direction):
        adjacency_map = piece.adjacent_pieces
        for direction, part_keys in parts_by_direction.items():
            if direction == PartAdjacency.IDENTITY:
                for part in piece.provided_parts:
                    if part._part_key in part_keys:
                        yield part

            elif direction in adjacency_map:
                for part in adjacency_map[direction].provided_parts:
                    if part._part_key in part_keys:
                        yield part

    def get_bounding_box(self):
        return self._piece.get_bounding_box()

    def get_ignored_objects_for_line_of_sight(self):
        return (
         self._piece,)

    @property
    def animation_actor(self):
        return self._animation_proxy

    def raycast_context(self, for_carryable=False):
        return self._piece.raycast_context(for_carryable=for_carryable)

    @property
    def footprint_polygon(self):
        return self._piece.footprint_polygon

    @property
    def rig(self):
        return self._piece.rig

    def on_owner_location_changed(self):
        self._set_part_location()

    def _set_part_location(self):
        transform = Transform.concatenate(self.get_joint_transform(), self._piece.transform)
        routing_surface = None
        surface_type = self.part_definition.part_surface.get_surface_type(self, transform=transform)
        if surface_type is not None:
            owner = self._piece
            routing_surface = routing.SurfaceIdentifier(owner.zone_id, owner.level, surface_type)
        self._part_location = self._piece.location.clone(transform=transform, routing_surface=routing_surface)

    @property
    def provided_super_affordances(self):
        return self._data.provided_container_super_affordances


class SectionalSofaPiece(GameObject):
    INSTANCE_TUNABLES = {'dynamic_parts': TunableMapping(description="\n            A mapping of keys to parts provided by this part.  Parts generated by this object will have an identifier\n            of '{key}_{piece_index}', where piece_index is the index of the modular piece in the context of the\n            greater sofa as assigned by the order it was added to the sofa.\n            \n            Think of the key as the 'type' of the part. Parts CAN be adjacent to parts that have specific types\n            if they are adjacent or provided by the same piece (which is considered IDENTITY adjacent).  The adjacency\n            is specifically defined in tuning explicitly as a way of specifying the adjacency connections.\n            \n            For example, I am sitting at Sit_0, I can only go into Nap_0 because it is provided by this piece\n            and defined IDENTITY adjacent in adjacency tuning. \n            Sit_0 can adjacent to Sit_1 if I define LEFT/RIGHT adjacencies on the sit layer.\n            \n            There is NEVER going to be a case where Sit_0 can be adjacent to Sit_2.  That would imply that the Sit parts\n            are provided on pieces that are 2 object pieces apart, which are never going to be adjacent with our rules.\n            \n            LEFT in sofa terms is defined in the point of view of a Sim that is currently SEATED on the couch.\n            A part that is left adjacent implies that a Sim can scoot left to sit on that part.  \n            \n            Likewise, sectional sofa model suites have a definition of west end/east for arm-rest end pieces.\n            LEFT will be naturally towards an WEST end piece, and RIGHT will naturally move towards an EAST end piece.\n            ",
                        key_type=TunableStringHash32(description='\n                A unique, arbitrary identifier for this part. Used to define adjacent and overlapping parts.\n                '),
                        value_type=(DynamicPartData.TunableFactory()))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._sofa_container = None
        self._provided_parts = None
        self._adjacencies = {}

    @property
    def container(self):
        return self._sofa_container

    def on_location_changed(self, old_location):
        super().on_location_changed(old_location)
        if self._provided_parts:
            if self._sofa_container:
                for part in self._provided_parts:
                    part._set_part_location()

                self.container._parts_moved = True

    def generate_parts(self, owner, obj_part_idx):
        self._sofa_container = owner
        self._provided_parts = []
        for part_key, part_data in self.dynamic_parts.items():
            adjacency_keys = set(self._adjacencies.keys())
            if part_data.required_adjacencies:
                if not adjacency_keys & part_data.required_adjacencies:
                    continue
            if part_data.disabling_adjacencies:
                if adjacency_keys:
                    if any((not disabling_set - adjacency_keys for disabling_set in part_data.disabling_adjacencies)):
                        continue
            part = SofaPiecePart(owner, part_data, self, obj_part_idx, part_key)
            self._provided_parts.append(part)

        return self._provided_parts

    @property
    def provided_parts(self):
        return self._provided_parts

    def add_adjacency(self, piece, direction):
        self._adjacencies[direction] = piece

    @property
    def adjacent_pieces(self):
        return self._adjacencies

    def clear_adjacencies(self):
        self._adjacencies.clear()

    @property
    def forwarded_pick_targets(self):
        if self._sofa_container is not None:
            return (self._sofa_container,)
        return ()

    def get_users(self, sims_only=False):
        users = super().get_users(sims_only=sims_only)
        if self._sofa_container is not None:
            users |= self._sofa_container.get_users(sims_only=sims_only)
        return users


lock_instance_tunables(SectionalSofaPiece, _part_data=(tuple()),
  _part_data_map=(frozendict()))