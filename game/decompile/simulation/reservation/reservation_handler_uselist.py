# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\reservation\reservation_handler_uselist.py
# Compiled at: 2016-11-04 14:09:08
# Size of source mod 2**32: 637 bytes
from reservation.reservation_handler import _ReservationHandler
from reservation.reservation_result import ReservationResult

class ReservationHandlerUseList(_ReservationHandler):

    def allows_reservation(self, other_reservation_handler):
        return ReservationResult.TRUE