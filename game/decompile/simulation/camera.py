# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\camera.py
# Compiled at: 2021-04-06 11:23:01
# Size of source mod 2**32: 8594 bytes
from distributor.ops import FocusCamera, ShakeCamera, FocusCameraOnLot, OverrideWallsUp, CancelFocusCamera
from distributor.system import Distributor
import services
_sim_id = None
_target_position = None
_camera_position = None
_follow_mode = None
_zone_id = None
_household_id = None

def deserialize(client=None, active_sim=None):
    global _camera_position
    global _follow_mode
    global _sim_id
    global _target_position
    global _zone_id
    save_slot_data_msg = services.get_persistence_service().get_save_slot_proto_buff()
    if save_slot_data_msg is not None:
        if save_slot_data_msg.HasField('gameplay_data'):
            gameplay_data = save_slot_data_msg.gameplay_data
            if gameplay_data.HasField('camera_data'):
                camera_data = save_slot_data_msg.gameplay_data.camera_data
                if camera_data.HasField('target_id'):
                    if active_sim is not None:
                        _sim_id = active_sim.id
                    else:
                        _sim_id = camera_data.target_id
                    _target_position = camera_data.target_position
                    _camera_position = camera_data.camera_position
                    _follow_mode = camera_data.follow_mode
                    _zone_id = camera_data.zone_id
                    if camera_data.HasField('household_id'):
                        if services.active_lot().owner_household_id != camera_data.household_id:
                            return False
                    if _follow_mode:
                        if services.sim_info_manager().get(_sim_id) is None:
                            _sim_id = None
                            _target_position = None
                            _camera_position = None
                            _follow_mode = None
                            _zone_id = None
                            return False
                    zone_id = services.current_zone_id()
                    if _zone_id == zone_id:
                        op = FocusCamera(id=_sim_id, follow_mode=_follow_mode)
                        op.set_location(_target_position)
                        op.set_position(_camera_position)
                        Distributor.instance().add_op_with_no_owner(op)
                        return True
    _sim_id = None
    _target_position = None
    _camera_position = None
    _follow_mode = None
    _zone_id = None
    return False


def serialize(save_slot_data=None):
    global _household_id
    if _sim_id is not None:
        if _household_id is not None:
            camera_data = save_slot_data.gameplay_data.camera_data
            camera_data.target_id = _sim_id
            camera_data.target_position.x = _target_position.x
            camera_data.target_position.y = _target_position.y
            camera_data.target_position.z = _target_position.z
            camera_data.camera_position.x = _camera_position.x
            camera_data.camera_position.y = _camera_position.y
            camera_data.camera_position.z = _camera_position.z
            camera_data.follow_mode = _follow_mode
            camera_data.zone_id = _zone_id
            camera_data.household_id = _household_id


def update(sim_id=None, target_position=None, camera_position=None, follow_mode=None):
    global _camera_position
    global _follow_mode
    global _household_id
    global _sim_id
    global _target_position
    global _zone_id
    _sim_id = sim_id
    _target_position = target_position
    _camera_position = camera_position
    _follow_mode = follow_mode
    _zone_id = services.current_zone_id()
    _household_id = services.active_lot().owner_household_id


def focus_on_sim(sim=None, follow=True, client=None):
    focus_sim = sim or client.active_sim
    op = FocusCamera(id=(focus_sim.id), follow_mode=follow)
    Distributor.instance().add_op_with_no_owner(op)


def focus_on_object(object=None, follow=True):
    op = FocusCamera(id=(object.id), follow_mode=follow)
    Distributor.instance().add_op_with_no_owner(op)


def cancel_focus(object=None):
    op = CancelFocusCamera(id=(object.id))
    Distributor.instance().add_op_with_no_owner(op)


def focus_on_position(pos, client=None):
    op = FocusCamera()
    op.set_location(pos)
    Distributor.instance().add_op_with_no_owner(op)


def focus_on_object_from_position(obj_position=None, camera_position=None, client=None):
    op = FocusCamera()
    op.set_position(camera_position)
    op.set_location(obj_position)
    Distributor.instance().add_op_with_no_owner(op)


def shake_camera(duration, frequency=None, amplitude=None, octaves=None, fade_multiplier=None):
    Distributor.instance().add_op_with_no_owner(ShakeCamera(duration, frequency=frequency,
      amplitude=amplitude,
      octaves=octaves,
      fade_multiplier=fade_multiplier))


def focus_on_lot(lot_id=None, lerp_time=1.0):
    Distributor.instance().add_op_with_no_owner(FocusCameraOnLot(lot_id=lot_id, lerp_time=lerp_time))


def walls_up_override(walls_up=True, lot_id=None):
    Distributor.instance().add_op_with_no_owner(OverrideWallsUp(override=walls_up, lot_id=lot_id))


def set_to_default():
    op = FocusCamera(id=0)
    Distributor.instance().add_op_with_no_owner(op)