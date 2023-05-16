# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\test_handlers.py
# Compiled at: 2017-08-08 15:40:45
# Size of source mod 2**32: 3896 bytes
from gsi_handlers.gameplay_archiver import GameplayArchiver
from interactions import ParticipantType
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
import sims4.log
logger = sims4.log.Logger('GSI Test Handlers')