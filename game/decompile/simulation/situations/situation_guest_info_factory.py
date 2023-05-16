# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_guest_info_factory.py
# Compiled at: 2019-01-18 21:55:46
# Size of source mod 2**32: 1938 bytes
from sims4.tuning.tunable import TunableFactory, TunableEnumEntry
from situations.bouncer.bouncer_types import BouncerRequestPriority, RequestSpawningOption
from situations.situation_guest_list import SituationGuestInfo

class SituationGuestInfoFactory(TunableFactory):

    @staticmethod
    def factory(sim_id, job_type, *, bouncer_request_priority, request_spawning_option):
        guest_info = SituationGuestInfo(sim_id, job_type,
          request_spawning_option,
          bouncer_request_priority,
          expectation_preference=True)
        return guest_info

    FACTORY_TYPE = factory

    def __init__(self):
        super().__init__(description="\n            Situation Guest Info tuning. Consult a GPE if you're at all unsure\n            what any of this does.\n            ",
          bouncer_request_priority=TunableEnumEntry(description='\n                Bouncer Request Priority. Requests with higher priority will be\n                filled first. Conversely, lower priority requests will be pushed\n                out first upon hitting the sim cap.\n                ',
          tunable_type=BouncerRequestPriority,
          default=(BouncerRequestPriority.EVENT_DEFAULT_JOB)),
          request_spawning_option=TunableEnumEntry(description='\n                Spawning Option.\n                MUST_SPAWN: Choose from uninstantiated Sims.\n                CANNOT_SPAWN: Choose from instantiated Sims.\n                DONT_CARE: Choose from all Sims.\n                ',
          tunable_type=RequestSpawningOption,
          default=(RequestSpawningOption.DONT_CARE)))