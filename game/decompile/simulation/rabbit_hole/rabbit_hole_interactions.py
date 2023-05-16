# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\rabbit_hole\rabbit_hole_interactions.py
# Compiled at: 2020-09-05 05:21:57
# Size of source mod 2**32: 2973 bytes
import sims4
from event_testing.results import TestResult
from sims.self_interactions import GoHomeTravelInteraction
from sims.sim_info_interactions import SimInfoInteraction
import services
from sims4.tuning.instances import lock_instance_tunables
from sims4.utils import flexmethod
logger = sims4.log.Logger('RabbitHoleInteractions', default_owner='rrodgers')

class GoHomeForRabbitHoleInteraction(GoHomeTravelInteraction):

    @flexmethod
    def get_icon_info(cls, inst, **kwargs):
        if inst is not None:
            icon_info = (services.get_rabbit_hole_service().get_head_rabbit_hole_home_interaction_icon)((inst.sim.id), **kwargs)
            if icon_info is not None:
                return icon_info
        logger.error('Failed to get rabbit hole travel icon for rabbit hole: {}', cls)
        return (super().get_icon_info)(cls, inst, **kwargs)

    @flexmethod
    def get_name(cls, inst, **interaction_parameters):
        if inst is not None:
            name = (services.get_rabbit_hole_service().get_head_rabbit_hole_home_interaction_name)((inst.sim.id), **interaction_parameters)
            if name is not None:
                return name
        logger.error('Failed to get rabbit hole travel display name for rabbit hole: {}', cls)
        return (super()._get_name)(cls, inst, **interaction_parameters)


lock_instance_tunables(GoHomeForRabbitHoleInteraction, display_name=None,
  display_name_overrides=None)

class RabbitHoleLeaveEarlyInteraction(SimInfoInteraction):

    @classmethod
    def _test(cls, *args, sim_info=None, **kwargs):
        if sim_info is None:
            return TestResult(False, 'No sim info')
        else:
            sim_id = sim_info.id
            rabbit_hole_service = services.get_rabbit_hole_service()
            if not rabbit_hole_service.is_in_rabbit_hole(sim_id):
                return TestResult(False, 'Not currently in a rabbit hole')
            return rabbit_hole_service.is_head_rabbit_hole_user_cancelable(sim_id) or TestResult(False, 'Rabbit hole interaction is not user cancelable')
        return (super()._test)(*args, **kwargs)

    def _run_interaction(self):
        sim_id = self._sim_info.id
        rabbit_hole_service = services.get_rabbit_hole_service()
        rabbit_hole_id = rabbit_hole_service.get_head_rabbit_hole_id(sim_id)
        if rabbit_hole_id:
            rabbit_hole_service.remove_sim_from_rabbit_hole(sim_id, rabbit_hole_id=rabbit_hole_id, canceled=True)
        return True