# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\priority_queue.py
# Compiled at: 2012-06-19 19:47:36
# Size of source mod 2**32: 2352 bytes
import heapq

class PriorityQueueWithGarbage:

    def __init__(self, is_garbage_func, make_garbage_func, *args):
        self._q = []
        self._is_garbage_func = is_garbage_func
        self._make_garbage_func = make_garbage_func
        if args:
            (self.append)(*args)

    def __iter__(self):
        return self._q.__iter__()

    def __len__(self):
        return self._q.__len__()

    def __bool__(self):
        self._clear_garbage()
        if self._q:
            return True
        return False

    def _clear_garbage(self):
        while self._q and self._is_garbage_func(self._q[0]):
            heapq.heappop(self._q)

    def peek(self):
        self._clear_garbage()
        if self._q:
            return self._q[0]

    def pop(self):
        self._clear_garbage()
        if self._q:
            return heapq.heappop(self._q)

    def append(self, *elements):
        for element in elements:
            heapq.heappush(self._q, element)

    def remove(self, element):
        self._make_garbage_func(element)

    def clear(self):
        del self._q[:]