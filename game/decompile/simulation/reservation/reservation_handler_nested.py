# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\reservation\reservation_handler_nested.py
# Compiled at: 2019-11-06 12:30:09
# Size of source mod 2**32: 1689 bytes
from reservation.reservation_result import ReservationResult

class ReservationHandlerNested:

    def __init__(self):
        self._handlers = []

    def get_targets(self):
        targets = set()
        for handler in self._handlers:
            targets.update(handler.get_targets())

        return frozenset(targets)

    def add_handler(self, handler):
        self._handlers.append(handler)

    def begin_reservation(self, *_, _may_reserve_already_run=False, **__):
        if not _may_reserve_already_run:
            result = self.may_reserve(_from_reservation_call=True)
            if not result:
                return result
        for handler in self._handlers:
            handler.begin_reservation(_may_reserve_already_run=True)

        return ReservationResult.TRUE

    def end_reservation(self, *_, **__):
        for handler in self._handlers:
            handler.end_reservation()

    def do_reserve(self, sequence=None):
        for handler in self._handlers:
            sequence = handler.do_reserve(sequence=sequence)

        return sequence

    def may_reserve(self, *args, **kwargs):
        for handler in self._handlers:
            reserve_result = (handler.may_reserve)(*args, **kwargs)
            if not reserve_result:
                return reserve_result

        return ReservationResult.TRUE