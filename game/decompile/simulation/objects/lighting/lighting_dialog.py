# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\lighting\lighting_dialog.py
# Compiled at: 2017-08-30 17:59:50
# Size of source mod 2**32: 1799 bytes
from protocolbuffers import UI_pb2, DistributorOps_pb2
from ui.ui_dialog import UiDialogBase
from distributor.system import Distributor
from distributor.ops import GenericProtocolBufferOp

class UiDialogLightColorAndIntensity(UiDialogBase):
    DIALOG_MSG_TYPE = DistributorOps_pb2.Operation.UI_LIGHT_COLOR_SHOW

    def __init__(self, obj, r, g, b, intensity, on_update=None, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._obj = obj
        self._red = r
        self._green = g
        self._blue = b
        self._intensity = intensity
        self._on_update = on_update

    def build_msg(self, **kwargs):
        msg = UI_pb2.LightColorAndIntensity()
        msg.response_id = self.dialog_id
        msg.target_id = self._obj.id
        msg.red = self._red
        msg.green = self._green
        msg.blue = self._blue
        msg.intensity = self._intensity
        return msg

    def distribute_dialog(self, dialog_type, dialog_msg, **kwargs):
        distributor = Distributor.instance()
        distributor.add_op_with_no_owner(GenericProtocolBufferOp(dialog_type, dialog_msg))

    def update_dialog_data(self, **kwargs):
        if self._on_update is not None:
            (self._on_update)(**kwargs)

    def has_responses(self):
        return True