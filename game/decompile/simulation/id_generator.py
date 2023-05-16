# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\id_generator.py
# Compiled at: 2013-04-30 23:04:56
# Size of source mod 2**32: 588 bytes
try:
    import _guid
except ImportError:
    _object_count = 0

    class _guid:

        @staticmethod
        def generate_s4guid():
            global _object_count
            _object_count += 1
            return _object_count


def __reload__(old_module_vars):
    pass


def generate_object_id():
    return _guid.generate_s4guid()