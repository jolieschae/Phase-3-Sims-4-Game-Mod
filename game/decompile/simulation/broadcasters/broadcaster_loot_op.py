# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\broadcasters\broadcaster_loot_op.py
# Compiled at: 2021-06-01 22:08:55
# Size of source mod 2**32: 2762 bytes
from broadcasters.broadcaster_request import BroadcasterRequest
from interactions import ParticipantType
from interactions.utils.loot_basic_op import BaseLootOperation
import element_utils, services, sims4.log
logger = sims4.log.Logger('Broadcaster Loots', default_owner='jdimailig')

def verify_immediate_broadcaster(instance_class, tunable_name, source, broadcaster_types=[], **kwargs):
    from broadcasters.broadcaster import Broadcaster
    for tested_broadcaster_tuple in broadcaster_types:
        broadcaster = tested_broadcaster_tuple.item
        if not broadcaster.frequency.frequency_type != Broadcaster.FREQUENCY_ENTER:
            broadcaster.immediate or logger.error('Only on-enter immediate broadcasters are allowed in this op found {}', broadcaster)


class BroadcasterOneShotLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'broadcaster_request': BroadcasterRequest.TunableFactory(description='\n            The broadcaster request to run.\n            ',
                              verify_tunable_callback=verify_immediate_broadcaster,
                              locked_args={'offset_time':None, 
                             'participant':ParticipantType.Object})}

    def __init__(self, *args, broadcaster_request=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.broadcaster_request = broadcaster_request

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject.is_sim:
            if subject.sim_info is subject:
                subject = subject.get_sim_instance()
                if subject is None:
                    logger.error('Requested broadcaster for uninstanced Sim')
                    return
        request = self.broadcaster_request(subject, sequence=(element_utils.sleep_until_next_tick_element(),))
        if resolver.interaction is not None:
            request.cache_excluded_participants(resolver.interaction)
        sim_timeline = services.time_service().sim_timeline
        sim_timeline.schedule(request)