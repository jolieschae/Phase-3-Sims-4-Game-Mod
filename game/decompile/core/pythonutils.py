# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\pythonutils.py
# Compiled at: 2015-01-29 13:25:40
# Size of source mod 2**32: 525 bytes
try:
    import _pythonutils
except ImportError:

    class _pythonutils:

        @staticmethod
        def try_highwater_gc():
            return False


try_highwater_gc = _pythonutils.try_highwater_gc