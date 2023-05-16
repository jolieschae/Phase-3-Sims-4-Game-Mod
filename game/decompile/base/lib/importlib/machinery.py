# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\importlib\machinery.py
# Compiled at: 2018-08-07 18:30:17
# Size of source mod 2**32: 920 bytes
import _imp
from ._bootstrap import ModuleSpec
from ._bootstrap import BuiltinImporter
from ._bootstrap import FrozenImporter
from ._bootstrap_external import SOURCE_SUFFIXES, DEBUG_BYTECODE_SUFFIXES, OPTIMIZED_BYTECODE_SUFFIXES, BYTECODE_SUFFIXES, EXTENSION_SUFFIXES
from ._bootstrap_external import PathFinder
from ._bootstrap_external import FileFinder
from ._bootstrap_external import SourceFileLoader
from ._bootstrap_external import SourcelessFileLoader
from ._bootstrap_external import ExtensionFileLoader

def all_suffixes():
    return SOURCE_SUFFIXES + BYTECODE_SUFFIXES + EXTENSION_SUFFIXES