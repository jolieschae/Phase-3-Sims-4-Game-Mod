# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\dummy_threading.py
# Compiled at: 2011-04-08 23:53:23
# Size of source mod 2**32: 2893 bytes
from sys import modules as sys_modules
import _dummy_thread
holding_thread = False
holding_threading = False
holding__threading_local = False
try:
    if '_thread' in sys_modules:
        held_thread = sys_modules['_thread']
        holding_thread = True
    sys_modules['_thread'] = sys_modules['_dummy_thread']
    if 'threading' in sys_modules:
        held_threading = sys_modules['threading']
        holding_threading = True
        del sys_modules['threading']
    if '_threading_local' in sys_modules:
        held__threading_local = sys_modules['_threading_local']
        holding__threading_local = True
        del sys_modules['_threading_local']
    import threading
    sys_modules['_dummy_threading'] = sys_modules['threading']
    del sys_modules['threading']
    sys_modules['_dummy__threading_local'] = sys_modules['_threading_local']
    del sys_modules['_threading_local']
    from _dummy_threading import *
    from _dummy_threading import __all__
finally:
    if holding_threading:
        sys_modules['threading'] = held_threading
        del held_threading
    else:
        del holding_threading
        if holding__threading_local:
            sys_modules['_threading_local'] = held__threading_local
            del held__threading_local
        del holding__threading_local
        if holding_thread:
            sys_modules['_thread'] = held_thread
            del held_thread
        else:
            del sys_modules['_thread']
    del holding_thread
    del _dummy_thread
    del sys_modules