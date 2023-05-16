# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\socials\carried_group.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 3818 bytes
from interactions.constraint_variants import TunableConstraintVariant
from interactions.constraints import Anywhere, Nowhere
from interactions.interaction_finisher import FinishingType
from sims4.tuning.tunable import TunableList
from socials.side_group import SideGroup

class CarriedGroup(SideGroup):
    INSTANCE_TUNABLES = {'group_constraints': TunableList(description='\n            A list of constraints non-carrying sims must satisfy to meet the needs of the social group.\n            The target of these constraints is the carrying sim.\n            ',
                            tunable=(TunableConstraintVariant()))}

    def __init__(self, *args, **kwargs):
        self._carried_sim = None
        self._carrying_sim = None
        (super().__init__)(*args, **kwargs)

    def _make_constraint(self, position, *args, **kwargs):
        if self._carried_sim is None:
            if self._initiating_sim is not None:
                if self._target_sim is not None:
                    if self._initiating_sim.parent is not None and self._initiating_sim.parent.is_sim:
                        self._carried_sim = self._initiating_sim
                        self._carrying_sim = self._initiating_sim.parent
                    else:
                        if self._target_sim.parent is not None:
                            if self._target_sim.parent.is_sim:
                                self._carried_sim = self._target_sim
                                self._carrying_sim = self._target_sim.parent
                    if self._carrying_sim is not None:
                        self._carrying_sim.register_on_location_changed(self._carrying_sim_location_changed)
        if self._carried_sim is None:
            return Nowhere('No carried sim set for the carried sim social group.')
        constraint_total = Anywhere()
        for constraint_factory in self.group_constraints:
            constraint = constraint_factory.create_constraint((self._initiating_sim), target=(self._carrying_sim))
            constraint_total = constraint_total.intersect(constraint)

        return constraint_total

    def _get_constraint(self, sim):
        if self._carried_sim is None:
            return Nowhere('No carried sim set for the carried sim social group.')
        if sim is self._carried_sim or sim is self._carrying_sim:
            return Anywhere()
        return self._constraint

    def _carrying_sim_location_changed(self, obj, *_, **__):
        if obj is self._carrying_sim:
            if len(self) == 2:
                if self._carrying_sim in self:
                    if self._carried_sim in self:
                        return
            self.shutdown(FinishingType.SOCIALS)

    def shutdown(self, finishing_type):
        if self._carried_sim:
            self._carrying_sim.unregister_on_location_changed(self._carrying_sim_location_changed)
            self._carrying_sim = None
            self._carried_sim = None
        super().shutdown(finishing_type)