# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\game\game_team.py
# Compiled at: 2019-04-02 15:04:19
# Size of source mod 2**32: 1358 bytes
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory

class GameTeam(HasTunableSingletonFactory, AutoFactoryInit):

    def add_player(self, game, sim):
        raise NotImplementedError

    def can_be_on_same_team(self, target_a, target_b):
        return True

    def team_determines_part(self):
        return True

    def can_be_on_opposing_team(self, target_a, target_b):
        return True

    def remove_player(self, game, sim):
        raise NotImplementedError