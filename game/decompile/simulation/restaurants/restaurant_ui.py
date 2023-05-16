# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\restaurants\restaurant_ui.py
# Compiled at: 2018-04-18 17:08:22
# Size of source mod 2**32: 384 bytes
from distributor.ops import Op, protocol_constants

class ShowMenu(Op):

    def __init__(self, show_menu_message):
        super().__init__()
        self.op = show_menu_message

    def write(self, msg):
        self.serialize_op(msg, self.op, protocol_constants.RESTAURANT_SHOW_MENU)