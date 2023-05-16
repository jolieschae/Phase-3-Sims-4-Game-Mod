# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\__init__.py
# Compiled at: 2021-05-06 13:56:29
# Size of source mod 2**32: 524 bytes
try:
    import _lot
except ImportError:

    class _lot:

        @staticmethod
        def get_lot_id_from_instance_id(*_, **__):
            return 0

        class Lot:
            pass


get_lot_id_from_instance_id = _lot.get_lot_id_from_instance_id