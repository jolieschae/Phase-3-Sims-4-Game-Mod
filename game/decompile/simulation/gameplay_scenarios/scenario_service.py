# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gameplay_scenarios\scenario_service.py
# Compiled at: 2022-08-26 18:13:12
# Size of source mod 2**32: 707 bytes
import services
from sims4.service_manager import Service

class ScenarioService(Service):

    def update(self):
        active_household = services.active_household()
        if active_household is not None:
            scenario_tracker = active_household.scenario_tracker
            if scenario_tracker is not None:
                if scenario_tracker.active_scenario is not None:
                    scenario_tracker.active_scenario.update()