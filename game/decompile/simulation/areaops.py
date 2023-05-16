# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\areaops.py
# Compiled at: 2017-07-12 18:10:57
# Size of source mod 2**32: 641 bytes
try:
    import _areaops
except ImportError:

    class _areaops:

        @staticmethod
        def op_request(*_, **__):
            pass

        @staticmethod
        def save_gsi(*_, **__):
            pass

        @staticmethod
        def load_gsi(*_, **__):
            pass

        @staticmethod
        def trigger_assert(*_, **__):
            pass


op_request = _areaops.op_request
save_gsi = _areaops.save_gsi
load_gsi = _areaops.load_gsi
trigger_native_assert = _areaops.trigger_assert