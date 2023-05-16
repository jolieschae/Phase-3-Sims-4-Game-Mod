# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\buffs\buff_ops.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 12110 bytes
from autonomy.autonomy_modifier import AutonomyModifier
from buffs import BuffPolarity
from buffs.tunable import TunablePackSafeBuffReference
from interactions import ParticipantType
from interactions.utils.loot_basic_op import BaseLootOperation, BaseTargetedLootOperation
from sims4.localization import TunableLocalizedString
from sims4.tuning.tunable import Tunable, TunableMapping, TunableReference, TunableList, OptionalTunable, TunableEnumEntry, TunableFactory, TunableRange
from sims4.tuning.tunable_base import GroupNames
from tag import TunableTags
import services, sims4.log, singletons
logger = sims4.log.Logger('Buffs')

class BuffOp(BaseLootOperation):
    FACTORY_TUNABLES = {'buff': TunablePackSafeBuffReference()}

    def __init__(self, buff, **kwargs):
        (super().__init__)(**kwargs)
        self._buff = buff

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if self._buff.buff_type is not None:
            if subject is None:
                logger.error('Subject is None for the buff loot {}, resolver {}.', self._buff.buff_type, resolver)
                return False
            subject.add_buff_from_op(self._buff.buff_type, self._buff.buff_reason)

    def apply_to_interaction_statistic_change_element(self, interaction):
        return self._buff.buff_type is None or self._buff.buff_type.commodity or None
        autonomy_modifier_handlers = None
        locked_stat = [self._buff.buff_type.commodity]
        for recipient in interaction.get_participants(self.subject):
            if recipient.add_buff_from_op(self._buff.buff_type, self._buff.buff_reason):
                if autonomy_modifier_handlers is None:
                    autonomy_modifier_handlers = {}
                autonomy_modifier_handlers[recipient] = AutonomyModifier(locked_stats=locked_stat)

        return autonomy_modifier_handlers


class BuffTransferOp(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'moods_only':Tunable(description='\n            Checking this box will limit the operations to only the buffs with\n            an associated mood.\n            ',
       tunable_type=bool,
       default=True), 
     'buff_reason':OptionalTunable(description='\n            If set, specify a reason why the buff was added.\n            ',
       tunable=TunableLocalizedString(description='\n                The reason the buff was added. This will be displayed in the\n                buff tooltip.\n                ')), 
     'mood_types':OptionalTunable(TunableList(description='\n                If enabled, only transfer buffs with associated moods in this list.\n                ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.MOOD))))), 
     'polarity':OptionalTunable(TunableEnumEntry(description='\n                If enabled, only transfer buffs that match the selected polarity.\n                ',
       tunable_type=BuffPolarity,
       default=(BuffPolarity.NEUTRAL),
       tuning_group=(GroupNames.UI)))}

    def __init__(self, moods_only, buff_reason, mood_types=None, polarity=None, **kwargs):
        (super().__init__)(**kwargs)
        self._moods_only = moods_only
        self._buff_reason = buff_reason
        self._mood_types = mood_types
        self._polarity = polarity

    def _apply_to_subject_and_target(self, subject, target, resolver):
        old_buff_types = list(subject.get_active_buff_types())
        if self._moods_only:
            for buff_entry in old_buff_types:
                if buff_entry.mood_type is not None:
                    subject.remove_buff_by_type(buff_entry)

        else:
            for buff_entry in old_buff_types:
                subject.remove_buff_by_type(buff_entry)

        for target_buff in target.get_active_buff_types():
            if self._moods_only:
                if target_buff.mood_type is None:
                    continue
                elif self._mood_types is not None and target_buff.mood_type not in self._mood_types:
                    continue
                if self._polarity is not None:
                    if self._polarity is not target_buff.polarity:
                        continue
                buff_commodity = target_buff.commodity
                subject.add_buff(target_buff)
                if buff_commodity is not None:
                    tracker = subject.get_tracker(buff_commodity)
                    tracker.set_max(buff_commodity)
                    subject.set_buff_reason(target_buff, self._buff_reason)


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


class BuffRemovalOp(BaseLootOperation):
    FACTORY_TUNABLES = {'remove_all_visible_buffs':Tunable(description="\n            If checked, all visible buffs on the Sim, excluding those specified in\n            the 'buffs_to_ignore' list will be removed.  If unchecked, buff removal\n            will be handled by the 'buffs_to_remove' list.\n            ",
       tunable_type=bool,
       default=False), 
     'buffs_to_remove':TunableList(description="\n            If 'remove_all_buffs' is not checked, this is the list of buffs that\n            will be removed from the subject.  If 'remove_all_buffs' is checked,\n            this list will be ignored.\n            ",
       tunable=TunableReference(description='\n                Buff to be removed.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.BUFF)),
       pack_safe=True)), 
     'buff_tags_to_remove':TunableTags(description="\n            If 'remove_all_buffs' is not checked, buffs with any tag in this list\n            will be removed from the subject. If 'remove_all_buffs' is checked, this\n            list will be ignored. You can also specify how many buffs you want to remove\n            by tags in count_to_remove_by_tags\n            ",
       filter_prefixes=('buff', )), 
     'count_to_remove_by_tags':OptionalTunable(tunable=TunableRange(description='\n                If enabled, randomly remove x number of buffs specified in buff_tags_to_remove.\n                If disabled, all buffs specified in buff_tags_to_remove will be removed\n                ',
       tunable_type=int,
       default=1,
       minimum=1)), 
     'buffs_to_ignore':TunableList(description="\n            If 'remove_all_buffs' is checked, no buffs included in this list will\n            be removed.  If 'remove_all_buffs' is unchecked, this list will be\n            ignored.\n            ",
       tunable=TunableReference(description='\n                Buff to be removed.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.BUFF))))}

    def __init__(self, remove_all_visible_buffs, buffs_to_remove, buff_tags_to_remove, count_to_remove_by_tags, buffs_to_ignore, **kwargs):
        (super().__init__)(**kwargs)
        self._remove_all_visible_buffs = remove_all_visible_buffs
        self._buffs_to_remove = buffs_to_remove
        self._buff_tags_to_remove = buff_tags_to_remove
        self._count_to_remove_by_tags = count_to_remove_by_tags
        self._buffs_to_ignore = buffs_to_ignore

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if self._remove_all_visible_buffs:
            removal_list = []
            removal_list.extend(subject.Buffs)
            for buff in removal_list:
                if type(buff) in self._buffs_to_ignore:
                    continue
                else:
                    if not buff.visible:
                        continue
                    if buff.commodity is not None:
                        if subject.is_statistic_type_added_by_modifier(buff.commodity):
                            continue
                        tracker = subject.get_tracker(buff.commodity)
                        commodity_inst = tracker.get_statistic(buff.commodity)
                        if commodity_inst is not None:
                            if commodity_inst.core:
                                continue
                subject.Buffs.remove_buff_entry(buff)

        else:
            for buff_type in self._buffs_to_remove:
                subject.Buffs.remove_buff_by_type(buff_type)

            subject.Buffs.remove_buffs_by_tags((self._buff_tags_to_remove), count_to_remove=(self._count_to_remove_by_tags))