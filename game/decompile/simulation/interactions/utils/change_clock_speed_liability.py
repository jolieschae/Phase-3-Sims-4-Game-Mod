# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\change_clock_speed_liability.py
# Compiled at: 2021-05-28 14:28:08
# Size of source mod 2**32: 1786 bytes
import services, sims4
from clock import ClockSpeedMultiplierType
from interactions.liability import Liability
from sims4.tuning.tunable import AutoFactoryInit, HasTunableFactory, TunableEnumEntry
logger = sims4.log.Logger('ChangeClockSpeedsLiability', default_owner='jmorrow')

class ChangeClockSpeedsLiability(Liability, HasTunableFactory, AutoFactoryInit):
    LIABILITY_TOKEN = 'ChangeClockSpeedLiability'
    FACTORY_TUNABLES = {'clock_speed_multipliers_override': TunableEnumEntry(description='\n             The clock speed multipliers to override the GameClock with for\n             the duration of the interaction. See "Clock Speed Type Multiplier Map"\n             in clock.tuning.\n             ',
                                           tunable_type=ClockSpeedMultiplierType,
                                           default=(ClockSpeedMultiplierType.DEFAULT))}

    def __init__(self, interaction, **kwargs):
        (super().__init__)(**kwargs)
        self._interaction = interaction

    def on_run(self):
        game_clock = services.game_clock_service()
        success = game_clock.set_clock_speed_multiplier_type_override(self.clock_speed_multipliers_override)
        if not success:
            logger.error('Trying to add multiple ClockSpeedMultiplierType overrides at the same time. This is not supported.', owner='jmorrow')

    def release(self):
        game_clock = services.game_clock_service()
        game_clock.clear_clock_speed_multiplier_type_override()

    def should_transfer(self, continuation):
        return False