# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\zone_modifier\zone_modifier_household_actions.py
# Compiled at: 2020-01-09 21:46:19
# Size of source mod 2**32: 3658 bytes
from autonomy.autonomy_modifier import AutonomyModifier
from sims.household_utilities.utility_operations import ShutOffUtilityModifier
from sims4.resources import Types
from sims4.tuning.tunable import TunableVariant, TunableList, HasTunableSingletonFactory, AutoFactoryInit, TunableReference, Tunable
import services

class ZoneModifierHouseholdActionVariants(TunableVariant):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, shut_off_utilities=ZoneModifierHouseholdShutOffUtility.TunableFactory(), 
         lot_statistic_modifier=ZoneModifierLotStatisticModifier.TunableFactory(), 
         default='shut_off_utilities', **kwargs)


class ZoneModifierHouseholdAction(HasTunableSingletonFactory, AutoFactoryInit):

    def start_action(self, household_id):
        raise NotImplementedError

    def stop_action(self, household_id):
        raise NotImplementedError


class ZoneModifierHouseholdShutOffUtility(ZoneModifierHouseholdAction):
    FACTORY_TUNABLES = {'utilities': TunableList(description='\n            A list of utilities to shut off.\n            ',
                    tunable=(ShutOffUtilityModifier.TunableFactory()))}

    def start_action(self, household_id):
        for utility_shut_off in self.utilities:
            shut_off = utility_shut_off()
            shut_off.start(household_id)

    def stop_action(self, household_id):
        for utility_shut_off in self.utilities:
            shut_off = utility_shut_off()
            shut_off.stop(household_id)


class ZoneModifierLotStatisticModifier(ZoneModifierHouseholdAction):
    FACTORY_TUNABLES = {'statistic':TunableReference(description='\n            The statistic to be modified by the lot trait.\n            ',
       manager=services.get_instance_manager(Types.STATISTIC)), 
     'modifier':Tunable(description='\n            The modifier to apply to the tuned statistic.\n            ',
       tunable_type=float,
       default=0)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._modifier_handle = None

    def start_action(self, household_id):
        lot = services.current_zone().lot
        autonomy_modifier = AutonomyModifier(statistic_modifiers={self.statistic: self.modifier})
        self._modifier_handle = lot.add_statistic_modifier(autonomy_modifier)

    def stop_action(self, household_id):
        lot = services.current_zone().lot
        lot.remove_statistic_modifier(self._modifier_handle)