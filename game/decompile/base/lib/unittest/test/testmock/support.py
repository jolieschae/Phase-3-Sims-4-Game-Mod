# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\test\testmock\support.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 408 bytes


def is_instance(obj, klass):
    return issubclass(type(obj), klass)


class SomeClass(object):
    class_attribute = None

    def wibble(self):
        pass


class X(object):
    pass


def examine_warnings(func):

    def wrapper():
        with catch_warnings(record=True) as (ws):
            func(ws)

    return wrapper