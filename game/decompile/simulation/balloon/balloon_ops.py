# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\balloon\balloon_ops.py
# Compiled at: 2020-07-31 16:25:08
# Size of source mod 2**32: 2623 bytes
from protocolbuffers import DistributorOps_pb2 as protocols, Sims_pb2
from distributor.ops import Op

class AddBalloon(Op):

    def __init__(self, balloon_request, sim):
        super().__init__()
        self.balloon_request = balloon_request
        self.sim_id = sim.id

    def write(self, msg):
        balloon_msg = Sims_pb2.AddBalloon()
        balloon_msg.sim_id = self.sim_id
        if self.balloon_request.icon is not None:
            balloon_msg.icon.type = self.balloon_request.icon.type
            balloon_msg.icon.group = self.balloon_request.icon.group
            balloon_msg.icon.instance = self.balloon_request.icon.instance
        elif self.balloon_request.icon_object is None:
            balloon_msg.icon_object.manager_id = 0
            balloon_msg.icon_object.object_id = 0
        else:
            balloon_msg.icon_object.object_id, balloon_msg.icon_object.manager_id = self.balloon_request.icon_object.icon_info
        if self.balloon_request.overlay is not None:
            balloon_msg.overlay.type = self.balloon_request.overlay.type
            balloon_msg.overlay.group = self.balloon_request.overlay.group
            balloon_msg.overlay.instance = self.balloon_request.overlay.instance
        balloon_msg.type = self.balloon_request.balloon_type
        balloon_msg.priority = self.balloon_request.priority
        balloon_msg.duration = self.balloon_request.duration
        if self.balloon_request.view_offset is not None:
            balloon_msg.view_offset_override.x = self.balloon_request.view_offset.x
            balloon_msg.view_offset_override.y = self.balloon_request.view_offset.y
            balloon_msg.view_offset_override.z = self.balloon_request.view_offset.z
        if self.balloon_request.category_icon is not None:
            balloon_msg.category_icon = self.balloon_request.category_icon
        rel_track = self.balloon_request.rel_track
        if rel_track is not None:
            rel_track.build_single_relationship_track_proto(balloon_msg.rel_track)
        self.serialize_op(msg, balloon_msg, protocols.Operation.ADD_BALLOON)