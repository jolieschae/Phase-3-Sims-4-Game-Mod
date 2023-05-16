# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\queue.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 11680 bytes
import threading
from collections import deque
from heapq import heappush, heappop
from time import monotonic as time
try:
    from _queue import SimpleQueue
except ImportError:
    SimpleQueue = None

__all__ = ["'Empty'", "'Full'", "'Queue'", "'PriorityQueue'", "'LifoQueue'", "'SimpleQueue'"]
try:
    from _queue import Empty
except AttributeError:

    class Empty(Exception):
        pass


class Full(Exception):
    pass


class Queue:

    def __init__(self, maxsize=0):
        self.maxsize = maxsize
        self._init(maxsize)
        self.mutex = threading.Lock()
        self.not_empty = threading.Condition(self.mutex)
        self.not_full = threading.Condition(self.mutex)
        self.all_tasks_done = threading.Condition(self.mutex)
        self.unfinished_tasks = 0

    def task_done(self):
        with self.all_tasks_done:
            unfinished = self.unfinished_tasks - 1
            if unfinished <= 0:
                if unfinished < 0:
                    raise ValueError('task_done() called too many times')
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished

    def join(self):
        with self.all_tasks_done:
            while self.unfinished_tasks:
                self.all_tasks_done.wait()

    def qsize(self):
        with self.mutex:
            return self._qsize()

    def empty(self):
        with self.mutex:
            return not self._qsize()

    def full(self):
        with self.mutex:
            return 0 < self.maxsize <= self._qsize()

    def put(self, item, block=True, timeout=None):
        with self.not_full:
            if self.maxsize > 0:
                if (block or self._qsize()) >= self.maxsize:
                    raise Full
                else:
                    if timeout is None:
                        while self._qsize() >= self.maxsize:
                            self.not_full.wait()

                    else:
                        if timeout < 0:
                            raise ValueError("'timeout' must be a non-negative number")
                        else:
                            endtime = time() + timeout
                            while self._qsize() >= self.maxsize:
                                remaining = endtime - time()
                                if remaining <= 0.0:
                                    raise Full
                                self.not_full.wait(remaining)

            self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()

    def get(self, block=True, timeout=None):
        with self.not_empty:
            if not (block or self._qsize()):
                raise Empty
            else:
                if timeout is None:
                    while not self._qsize():
                        self.not_empty.wait()

                else:
                    if timeout < 0:
                        raise ValueError("'timeout' must be a non-negative number")
                    else:
                        endtime = time() + timeout
                        while not self._qsize():
                            remaining = endtime - time()
                            if remaining <= 0.0:
                                raise Empty
                            self.not_empty.wait(remaining)

            item = self._get()
            self.not_full.notify()
            return item

    def put_nowait(self, item):
        return self.put(item, block=False)

    def get_nowait(self):
        return self.get(block=False)

    def _init(self, maxsize):
        self.queue = deque()

    def _qsize(self):
        return len(self.queue)

    def _put(self, item):
        self.queue.append(item)

    def _get(self):
        return self.queue.popleft()


class PriorityQueue(Queue):

    def _init(self, maxsize):
        self.queue = []

    def _qsize(self):
        return len(self.queue)

    def _put(self, item):
        heappush(self.queue, item)

    def _get(self):
        return heappop(self.queue)


class LifoQueue(Queue):

    def _init(self, maxsize):
        self.queue = []

    def _qsize(self):
        return len(self.queue)

    def _put(self, item):
        self.queue.append(item)

    def _get(self):
        return self.queue.pop()


class _PySimpleQueue:

    def __init__(self):
        self._queue = deque()
        self._count = threading.Semaphore(0)

    def put(self, item, block=True, timeout=None):
        self._queue.append(item)
        self._count.release()

    def get(self, block=True, timeout=None):
        if timeout is not None:
            if timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
        if not self._count.acquire(block, timeout):
            raise Empty
        return self._queue.popleft()

    def put_nowait(self, item):
        return self.put(item, block=False)

    def get_nowait(self):
        return self.get(block=False)

    def empty(self):
        return len(self._queue) == 0

    def qsize(self):
        return len(self._queue)


if SimpleQueue is None:
    SimpleQueue = _PySimpleQueue