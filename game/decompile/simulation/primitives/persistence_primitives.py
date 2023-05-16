# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\primitives\persistence_primitives.py
# Compiled at: 2014-12-16 15:20:24
# Size of source mod 2**32: 610 bytes
try:
    import _persistence_primitives
except ImportError:

    class _persistence_primitives:
        PersistVersion = 0


class PersistVersion:
    UNKNOWN = 0
    kPersistVersion_Implementation = 1
    SaveObjectDepreciation = 2
    SaveObjectCreateFromLotTemplate = 3
    SaveLoadSIFirstPass = 4
    GlobalSaveData = 5