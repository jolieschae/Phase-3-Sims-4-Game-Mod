# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\sched.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 6609 bytes
import time, heapq
from collections import namedtuple
import threading
from time import monotonic as _time
__all__ = [
 'scheduler']

class Event(namedtuple('Event', 'time, priority, action, argument, kwargs')):
    __slots__ = []

    def __eq__(s, o):
        return (
         s.time, s.priority) == (o.time, o.priority)

    def __lt__(s, o):
        return (
         s.time, s.priority) < (o.time, o.priority)

    def __le__(s, o):
        return (
         s.time, s.priority) <= (o.time, o.priority)

    def __gt__(s, o):
        return (
         s.time, s.priority) > (o.time, o.priority)

    def __ge__(s, o):
        return (
         s.time, s.priority) >= (o.time, o.priority)


Event.time.__doc__ = 'Numeric type compatible with the return value of the\ntimefunc function passed to the constructor.'
Event.priority.__doc__ = 'Events scheduled for the same time will be executed\nin the order of their priority.'
Event.action.__doc__ = 'Executing the event means executing\naction(*argument, **kwargs)'
Event.argument.__doc__ = 'argument is a sequence holding the positional\narguments for the action.'
Event.kwargs.__doc__ = 'kwargs is a dictionary holding the keyword\narguments for the action.'
_sentinel = object()

class scheduler:

    def __init__(self, timefunc=_time, delayfunc=time.sleep):
        self._queue = []
        self._lock = threading.RLock()
        self.timefunc = timefunc
        self.delayfunc = delayfunc

    def enterabs(self, time, priority, action, argument=(), kwargs=_sentinel):
        if kwargs is _sentinel:
            kwargs = {}
        event = Event(time, priority, action, argument, kwargs)
        with self._lock:
            heapq.heappush(self._queue, event)
        return event

    def enter(self, delay, priority, action, argument=(), kwargs=_sentinel):
        time = self.timefunc() + delay
        return self.enterabs(time, priority, action, argument, kwargs)

    def cancel(self, event):
        with self._lock:
            self._queue.remove(event)
            heapq.heapify(self._queue)

    def empty(self):
        with self._lock:
            return not self._queue

    def run(self, blocking=True):
        lock = self._lock
        q = self._queue
        delayfunc = self.delayfunc
        timefunc = self.timefunc
        pop = heapq.heappop
        while True:
            with lock:
                if not q:
                    break
                else:
                    time, priority, action, argument, kwargs = q[0]
                    now = timefunc()
                    if time > now:
                        delay = True
                    else:
                        delay = False
                        pop(q)
            if delay:
                if not blocking:
                    return time - now
                delayfunc(time - now)
            else:
                action(*argument, **kwargs)
                delayfunc(0)

    @property
    def queue(self):
        with self._lock:
            events = self._queue[:]
        return list(map(heapq.heappop, [events] * len(events)))