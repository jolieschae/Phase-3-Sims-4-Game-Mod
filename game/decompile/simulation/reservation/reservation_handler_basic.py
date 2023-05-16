# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\reservation\reservation_handler_basic.py
# Compiled at: 2019-11-06 12:15:50
# Size of source mod 2**32: 6679 bytes
import functools
from reservation.reservation_handler import _ReservationHandler
from reservation.reservation_handler_interlocked import ReservationHandlerInterlocked
from reservation.reservation_handler_multi import ReservationHandlerMulti
from reservation.reservation_handler_uselist import ReservationHandlerUseList
from reservation.reservation_result import ReservationResult
import sims4.log
logger = sims4.log.Logger('Reservation')

class ReservationHandlerBasic(_ReservationHandler):

    def allows_reservation(self, other_reservation_handler):
        if self._is_sim_allowed_to_clobber(other_reservation_handler):
            return ReservationResult.TRUE
        if isinstance(other_reservation_handler, ReservationHandlerUseList):
            return ReservationResult.TRUE
        if isinstance(other_reservation_handler, ReservationHandlerInterlocked):
            return ReservationResult.TRUE
        return ReservationResult(False, '{} disallows any other reservation type: ({})', self,
          other_reservation_handler, result_obj=(self.sim))

    def begin_reservation(self, *args, _may_reserve_already_run=False, **kwargs):
        if self.target.parts is not None:
            logger.error("\n                {} is attempting to execute a basic reservation on {}, which has parts. This is not allowed.\n                {} and its associated postures need to be allowed to run on the object's individual parts in order\n                for this to work properly.\n                ", self.sim, self.target, self.reservation_interaction.get_interaction_type() if self.reservation_interaction is not None else 'The reservation owner')
        if not _may_reserve_already_run:
            result = self.may_reserve(_from_reservation_call=True)
            if not result:
                return result
        (super().begin_reservation)(args, _may_reserve_already_run=True, **kwargs)
        return ReservationResult.TRUE


class _ReservationHandlerMultiTarget(_ReservationHandler):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._part_handlers = []

    def _get_reservation_handler_type(self):
        return ReservationHandlerBasic

    def _get_reservation_targets(self):
        raise NotImplementedError

    def allows_reservation(self, other_reservation_handler):
        for handler in self._part_handlers:
            reserve_result = handler.allows_reservation(other_reservation_handler)
            if not reserve_result:
                return reserve_result

        return ReservationResult.TRUE

    def begin_reservation(self, *_, _may_reserve_already_run=False, **__):
        if not _may_reserve_already_run:
            result = self.may_reserve(_from_reservation_call=True)
            if not result:
                return result
        handler_type = self._get_reservation_handler_type()
        for target in self._get_reservation_targets():
            part_handler = handler_type((self._sim), target, reservation_interaction=(self._reservation_interaction))
            part_handler.begin_reservation(_may_reserve_already_run=True)
            self._part_handlers.append(part_handler)

        return ReservationResult.TRUE

    def end_reservation(self, *_, **__):
        for part_handler in self._part_handlers:
            part_handler.end_reservation()

    def may_reserve(self, _from_reservation_call=False, **kwargs):
        handler_type = self._get_reservation_handler_type()
        for target in self._get_reservation_targets():
            part_handler = handler_type((self._sim), target, **kwargs)
            result = (part_handler.may_reserve)(**kwargs)
            if not result:
                return result

        return ReservationResult.TRUE


class ReservationHandlerAllParts(_ReservationHandlerMultiTarget):

    def _get_reservation_targets(self):
        target = self._target
        if target.is_part:
            target = target.part_owner
        elif not target.parts:
            targets = (
             target,)
        else:
            targets = target.parts
        return targets


class ReservationHandlerUnmovableObjects(_ReservationHandlerMultiTarget):

    def _get_reservation_handler_type(self):
        return functools.partial(ReservationHandlerMulti, reservation_limit=None)

    def _get_reservation_targets(self):
        if self._target.live_drag_component is None:
            if self._target.carryable_component is None:
                return (
                 self._target,)
        return ()