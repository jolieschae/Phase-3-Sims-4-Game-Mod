# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\distributor\shared_messages.py
# Compiled at: 2018-08-14 20:20:05
# Size of source mod 2**32: 6597 bytes
from collections import namedtuple
from protocolbuffers.DistributorOps_pb2 import Operation
import protocolbuffers
from distributor.ops import Op, RelationshipUpdate
from distributor.system import Distributor
from sims4.repr_utils import standard_repr
import services, sims4.log
logger = sims4.log.Logger('DistributorMessages')

class MessageOp(Op):

    def __init__(self, protocol_buffer, message_type, immediate=False):
        super().__init__(immediate=immediate)
        self.protocol_buffer = protocol_buffer
        self.message_type = message_type

    def __repr__(self):
        return standard_repr(self, self.message_type)

    def write(self, msg):
        self.serialize_op(msg, self.protocol_buffer, Operation.UI_UPDATE)
        msg.data_context = self.message_type


def add_message_if_selectable(sim, msg_id, msg, immediate):
    if sim.is_selectable:
        if sim.valid_for_distribution:
            distributor = Distributor.instance()
            op = MessageOp(msg, msg_id, immediate)
            distributor.add_op(sim, op)


def add_message_if_player_controlled_sim(sim, msg_id, msg, immediate):
    if not sim.is_npc:
        if sim.valid_for_distribution:
            distributor = Distributor.instance()
            op = MessageOp(msg, msg_id, immediate)
            distributor.add_op(sim, op)


def add_object_message(obj, msg_id, msg, immediate):
    distributor = Distributor.instance()
    op = MessageOp(msg, msg_id, immediate)
    distributor.add_op(obj, op)


def add_object_message_for_sim_id(sim_id, msg_id, msg):
    sim_info = services.sim_info_manager().get(sim_id)
    if sim_info is not None:
        add_object_message(sim_info, msg_id, msg, False)
    else:
        logger.error('Unable to find Sim for id {} in add_object_message_for_sim_id', sim_id)


_IconInfoData = namedtuple('IconInfoData', ('icon_resource', 'obj_instance', 'obj_def_id',
                                            'obj_geo_hash', 'obj_material_hash',
                                            'obj_name'))

def IconInfoData(icon_resource=None, obj_instance=None, obj_def_id=None, obj_geo_hash=None, obj_material_hash=None, obj_name=None):
    return _IconInfoData(icon_resource, obj_instance, obj_def_id, obj_geo_hash, obj_material_hash, obj_name)


EMPTY_ICON_INFO_DATA = IconInfoData()

def build_icon_info_msg(icon_info, name, msg, desc=None, tooltip=None):
    if name is not None:
        msg.name = name
    elif desc is not None:
        msg.desc = desc
    else:
        if tooltip is not None:
            msg.tooltip = tooltip
        else:
            icon = icon_info.icon_resource
            if icon is not None:
                msg.icon.type = icon.type
                msg.icon.group = icon.group
                msg.icon.instance = icon.instance
            else:
                msg.icon.type = 0
            msg.icon.group = 0
            msg.icon.instance = 0
        icon_object = icon_info.obj_instance
        if icon_object is not None and None not in icon_object.icon_info:
            msg.icon_object.object_id, msg.icon_object.manager_id = icon_object.icon_info
            msg.object_instance_id = icon_object.id
            icon_object.populate_icon_canvas_texture_info(msg)
            icon_override = icon_object.get_icon_override()
            if icon_override is not None:
                msg.icon.type = icon_override.type
                msg.icon.group = icon_override.group
                msg.icon.instance = icon_override.instance
            icon_info_data = icon_object.get_icon_info_data()
        else:
            icon_info_data = icon_info
        icon_obj_def_id = icon_info_data.obj_def_id
        icon_obj_geo_hash = icon_info_data.obj_geo_hash
        icon_obj_material_hash = icon_info_data.obj_material_hash
        icon_obj_name = icon_info_data.obj_name
        if icon_obj_def_id is not None:
            msg.icon_object_def.definition_id = icon_obj_def_id
            if icon_obj_geo_hash is not None:
                msg.icon_object_def.geo_state_hash = icon_obj_geo_hash
            if icon_obj_material_hash is not None:
                msg.icon_object_def.material_hash = icon_obj_material_hash
            if name is None and icon_obj_name is not None:
                msg.name = icon_obj_name


def create_icon_info_msg(icon_info, name=None, desc=None, tooltip=None):
    icon_info_msg = protocolbuffers.UI_pb2.IconInfo()
    build_icon_info_msg(icon_info, name, icon_info_msg, desc=desc, tooltip=tooltip)
    return icon_info_msg


def create_message_op(msg, notification_type):
    return MessageOp(msg, notification_type)


def send_relationship_op(sim_info, message):
    distributor = Distributor.instance()
    op = RelationshipUpdate(message)
    distributor.add_op(sim_info, op)