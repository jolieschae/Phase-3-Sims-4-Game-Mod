# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\buffs\dynamic_buff_loot_op.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 3118 bytes
from interactions import ParticipantType
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.localization import TunableLocalizedString
from sims4.tuning.tunable import TunableMapping, TunableReference, Tunable, OptionalTunable, TunableFactory
import services, sims4.random, singletons
logger = sims4.log.Logger('Buffs')

class DynamicBuffLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'description':'\n        This loot will give a random buff based on the weight get tuned inside.\n        ', 
     'buffs':TunableMapping(description='\n            ',
       key_type=TunableReference(description='\n                Buff that will get this weight in the random.',
       manager=(services.get_instance_manager(sims4.resources.Types.BUFF))),
       value_type=Tunable(description='\n                The weight value.',
       tunable_type=float,
       default=0)), 
     'buff_reason':OptionalTunable(description='\n            If set, specify a reason why the buff was added.\n            ',
       tunable=TunableLocalizedString(description='\n                The reason the buff was added. This will be displayed in the\n                buff tooltip.\n                '))}

    def __init__(self, buffs, buff_reason, **kwargs):
        (super().__init__)(**kwargs)
        self._buffs = buffs
        self._buff_reason = buff_reason
        self._random_buff = None

    @TunableFactory.factory_option
    def subject_participant_type_options(description=singletons.DEFAULT, **kwargs):
        return (BaseLootOperation.get_participant_tunable)('subject', invalid_participants=(
                                ParticipantType.Invalid, ParticipantType.All, ParticipantType.PickedItemId), **kwargs)

    def _get_random_buff(self):
        if self._random_buff is None:
            buff_pair_list = list(self._buffs.items())
            self._random_buff = sims4.random.pop_weighted(buff_pair_list, flipped=True)
        return self._random_buff

    def _apply_to_subject_and_target(self, subject, target, resolver):
        random_buff = self._get_random_buff()
        if random_buff is not None:
            if not subject.is_sim:
                logger.error('Tuning error: subject {} of DynamicBuffLootOp giving buff {} for reason {} is not a sim', self.subject, random_buff, self._buff_reason)
                return
            subject.add_buff_from_op(random_buff, self._buff_reason)

    def _on_apply_completed(self):
        random_buff = self._random_buff
        self._random_buff = None
        return random_buff