# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\global_policies\global_policy_loots.py
# Compiled at: 2019-02-08 16:35:03
# Size of source mod 2**32: 1886 bytes
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import TunableReference, Tunable
import services, sims4
logger = sims4.log.Logger('Global Policy Progress Loot', default_owner='shipark')

class GlobalPolicyAddProgress(BaseLootOperation):
    FACTORY_TUNABLES = {'global_policy':TunableReference(description='\n            The global policy of which the progress stat will be changed.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SNIPPET),
       class_restrictions=('GlobalPolicy', ),
       allow_none=False), 
     'amount':Tunable(description='\n            Amount of progress to be added to the in-progress policy.\n            ',
       tunable_type=int,
       default=0)}

    def __init__(self, *args, global_policy=None, amount=0, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.global_policy = global_policy
        self.amount = amount

    def _apply_to_subject_and_target(self, participent, target, resolver, **kwargs):
        if self.global_policy is None:
            logger.error('Add Global Policy Progress Loot has a global policy with                         None value, loot from interaction {} will not be executed.', resolver._interaction)
            return
        services.global_policy_service().add_global_policy_progress((self.global_policy), (self.amount), resolver=resolver)