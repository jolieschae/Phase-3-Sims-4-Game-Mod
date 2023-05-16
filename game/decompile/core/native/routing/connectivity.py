# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\native\routing\connectivity.py
# Compiled at: 2014-12-15 19:27:05
# Size of source mod 2**32: 457 bytes
try:
    from _pathing import connectivity_handle as Handle, connectivity_handle_list as HandleList
except ImportError:

    class Handle:

        def __init__(self, location):
            self.location = location


    class HandleList:

        def __init__(self):
            pass