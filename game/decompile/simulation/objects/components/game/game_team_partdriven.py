# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\game\game_team_partdriven.py
# Compiled at: 2019-04-08 19:44:34
# Size of source mod 2**32: 2788 bytes
from objects.components.game.game_team import GameTeam
from sims4.tuning.tunable import Tunable, TunableVariant, HasTunableSingletonFactory

class GameTeamPartDriven(GameTeam):

    class _PartRequirementAdjacent(HasTunableSingletonFactory):

        def is_on_same_team(self, part_a, part_b):
            if not part_a is None:
                return part_a.is_part or False
            else:
                return part_b is None or part_b.is_part or False
            return part_a is part_b or any((part_a is adjacent_part for adjacent_part in part_b.adjacent_parts_gen()))

    FACTORY_TUNABLES = {'part_requirement':TunableVariant(description='\n            Define how part relationships define team structure.\n            ',
       adjacent=_PartRequirementAdjacent.TunableFactory(),
       default='adjacent'), 
     '_team_determines_part':Tunable(description='\n            If True, the team a sim is added to determines which parts can be\n            used.  If false, the part a team chooses to use determines which\n            team the sim should be on.\n            ',
       tunable_type=bool,
       default=True)}

    def add_player(self, game, sim):
        target_object = game.get_target_object_for_sim(sim)
        for team in game._teams:
            if any((self.part_requirement.is_on_same_team(target_object, game.get_target_object_for_sim(other_sim)) for other_sim in team.players)):
                team.players.append(sim)
                return

        game.add_team([sim])

    def can_be_on_same_team(self, target_a, target_b):
        return self.part_requirement.is_on_same_team(target_a, target_b)

    def team_determines_part(self):
        return self._team_determines_part

    def can_be_on_opposing_team(self, target_a, target_b):
        return not self.can_be_on_same_team(target_a, target_b)

    def remove_player(self, game, sim):
        for team in game._teams:
            if sim in team.players:
                team.players.remove(sim)
                if not team.players:
                    game._teams.remove(team)
                break