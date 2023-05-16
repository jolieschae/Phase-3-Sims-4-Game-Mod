# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\service_npc_nanny_situation.py
# Compiled at: 2016-10-19 18:14:23
# Size of source mod 2**32: 630 bytes
from event_testing.test_events import TestEvent
from situations.complex.service_npc_situation import ServiceNpcSituation
import services

class ServiceNpcNannySituation(ServiceNpcSituation):

    def _on_set_sim_job(self, sim, job_type):
        super()._on_set_sim_job(sim, job_type)
        services.get_event_manager().process_event((TestEvent.AvailableDaycareSimsChanged), sim_info=(self.service_sim().sim_info))