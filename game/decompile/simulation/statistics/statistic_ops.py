# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\statistic_ops.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 96192 bytes
import random
from event_testing.resolver import DoubleSimResolver, SingleSimResolver, SingleActorAndObjectResolver
from event_testing.tests import TunableTestSet
from interactions import ParticipantType, ParticipantTypeSavedActor
from interactions.utils import LootType
from interactions.utils.loot_basic_op import BaseLootOperation, BaseTargetedLootOperation, LootOperationTargetFilterTestMixin
from interactions.utils.success_chance import SuccessChance
from interactions.utils.tunable_icon import TunableIcon
from relationships.global_relationship_tuning import RelationshipGlobalTuning
from relationships.relationship_enums import RelationshipTrackType, SentimentSignType, SentimentDurationType
from relationships.relationship_track import ObjectRelationshipTrack
from sims4 import math
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import Tunable, TunableVariant, TunableInterval, TunableEnumEntry, TunableReference, TunablePercent, TunableFactory, TunableRate, TunableList, OptionalTunable, TunableTuple, TunableRange, HasTunableSingletonFactory, TunableEnumFlags, TunablePackSafeReference, AutoFactoryInit
from sims4.tuning.tunable_base import RateDescriptions
from singletons import DEFAULT
from statistics.skill import Skill, TunableSkillLootData, TunableVariantSkillLootData
from statistics.statistic_enums import PeriodicStatisticBehavior, StatisticLockAction
from tunable_multiplier import TunableStatisticModifierCurve, TunableObjectCostModifierCurve, TunableMultiplier
from ui.ui_dialog_notification import UiDialogNotification
import enum, objects.components.types, services, sims4.log, sims4.resources, statistics.skill, statistics.statistic_categories
logger = sims4.log.Logger('SimStatistics')
autonomy_logger = sims4.log.Logger('Autonomy')
GAIN_TYPE_RATE = 0
GAIN_TYPE_AMOUNT = 1

class StatisticOperation(BaseLootOperation):
    STATIC_CHANGE_INTERVAL = 1
    DISPLAY_TEXT = TunableLocalizedStringFactory(description='\n        A string displaying the amount that this stat operation awards. It will\n        be provided two tokens: the statistic name and the value change.\n        ')
    DEFAULT_PARTICIPANT_ARGUMENTS = {'subject': TunableEnumFlags(description='\n             The owner of the stat that we are operating on.\n             ',
                  enum_type=ParticipantType,
                  default=(ParticipantType.Actor),
                  invalid_enums=(
                 ParticipantType.Invalid,))}

    @staticmethod
    def get_statistic_override(*, pack_safe):
        return (
         pack_safe,)

    @TunableFactory.factory_option
    def statistic_override(pack_safe=False):
        return {'stat': TunableReference(description='\n                The statistic we are operating on.\n                ',
                   manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
                   pack_safe=pack_safe)}

    FACTORY_TUNABLES = {'advertise': Tunable(description='\n            This statistic operation should advertise to autonomy.  This only\n            advertises if the statistic operation is used as part of Periodic\n            Statistic Change.\n            ',
                    tunable_type=bool,
                    needs_tuning=True,
                    default=True)}

    def __init__(self, stat=None, **kwargs):
        (super().__init__)(**kwargs)
        self._stat = stat
        self._ad_multiplier = 1
        self._loot_type = LootType.GENERIC
        if self._stat is not None:
            if issubclass(self._stat, Skill):
                self._loot_type = LootType.SKILL

    def __repr__(self):
        return '<{} {} {}>'.format(type(self).__name__, self.stat, self.subject)

    @property
    def stat(self):
        return self._stat

    @property
    def loot_type(self):
        return self._loot_type

    @property
    def ad_multiplier(self):
        return self._ad_multiplier

    def _apply_to_subject_and_target(self, subject, target, resolver):
        stat = self.get_stat(None)
        if not subject.is_locked(stat):
            tracker = subject.get_tracker(stat)
            if tracker is not None:
                self._apply(tracker, resolver=resolver)

    def _apply(self, tracker, resolver=None):
        raise NotImplementedError

    def get_value(self, obj=None, interaction=None, sims=None):
        raise NotImplementedError

    def _attempt_to_get_real_stat_value(self, obj, interaction):
        if obj is None:
            if interaction is not None:
                obj = interaction.get_participant(ParticipantType.Actor)
        if obj is not None:
            stat_value = obj.get_stat_value(self.stat)
            if stat_value is not None:
                return stat_value
        return self.stat.default_value

    def _get_interval(self, aop):
        return aop.super_affordance.approximate_duration

    def get_fulfillment_rate(self, interaction):
        if not self._advertise:
            return 0
        value = self.get_value(interaction=interaction)
        if interaction.target is not None:
            value *= interaction.target.get_stat_multiplier(self.stat, self.subject)
        interval = self._get_interval(interaction)
        if interval <= 0:
            logger.error('Tuning error: affordance interval should be greater than 0 (defaulting to 1)')
            interval = 1
        score = value / interval
        return score

    def _get_display_text(self, resolver=None):
        return self.stat.stat_name is None or self.stat.stat_name.hash or None
        value = self.get_value()
        if value:
            return (self.DISPLAY_TEXT)(*self._get_display_text_tokens())

    def _get_display_text_tokens(self, resolver=None):
        return (
         self.stat.stat_name, self.get_value())


def _get_tunable_amount(gain_type=GAIN_TYPE_AMOUNT):
    if gain_type == GAIN_TYPE_RATE:
        return TunableRate(description='\n            The gain, per interval for this operation.\n            ',
          display_name='Rate',
          rate_description=(RateDescriptions.PER_SIM_MINUTE),
          tunable_type=float,
          default=0)
    if gain_type == GAIN_TYPE_AMOUNT:
        return Tunable(description='\n            The one-time gain for this operation.\n            ',
          tunable_type=float,
          default=0)
    raise ValueError('Unsupported gain type: {}'.format(gain_type))


class StatisticChangeOp(StatisticOperation):

    class MaxPoints(HasTunableSingletonFactory):
        FACTORY_TUNABLES = {'max_points': Tunable(description='\n                The point total that a stat cannot go above when increasing. \n                If the increase would go above this point total, instead it will\n                just be equal to this point total.\n                ',
                         tunable_type=int,
                         default=0)}

        def __init__(self, *args, max_points=None, **kwargs):
            (super().__init__)(*args, **kwargs)
            self.max_points = max_points

        def __call__(self, stat):
            return self.max_points

    class MaxRank(HasTunableSingletonFactory):
        FACTORY_TUNABLES = {'max_rank': TunableRange(description='\n                The rank that a stat cannot go beyond when increasing.\n                If the increase would go beyond achieving this rank, instead\n                it will be set to the min points required to meet this rank.\n                This will prevent any gains toward the next rank from occurring.\n                \n                NOTE: Must be used with a RankedStatistic or it will return 0\n                as the max.\n                ',
                       tunable_type=int,
                       default=0,
                       minimum=0)}

        def __init__(self, *args, max_rank=None, **kwargs):
            (super().__init__)(*args, **kwargs)
            self.max_rank = max_rank

        def __call__(self, stat):
            if hasattr(stat, 'points_to_rank'):
                return stat.points_to_rank(self.max_rank)
            return 0

    FACTORY_TUNABLES = {'amount':lambda *args, **kwargs: _get_tunable_amount(*args, **kwargs), 
     'maximum':TunableVariant(description='\n        A variant containing the different ways you can cap the max amount a\n        statistic reaches as result of a change.\n        ',
       points=MaxPoints.TunableFactory(),
       rank=MaxRank.TunableFactory(),
       locked_args={'no_max': None},
       default='no_max'), 
     'exclusive_to_owning_si':Tunable(description='\n            If enabled, this gain will be exclusive to the SI that created it\n            and will not be allowed to occur if the sim is running mixers from\n            a different SI.\n            If disabled, this gain will happen as long as this\n            SI is active, regardless of which SI owns the mixer the sim is\n            currently running.\n            This is only effective on Sims.\n            ',
       tunable_type=bool,
       needs_tuning=True,
       default=True), 
     'periodic_change_behavior':TunableEnumEntry(description='\n         When applying this change operation at the beginning of an interaction\n         as part of a periodic statistic change and statistic is\n         a continuous statistic, tune the behavior of this operation when\n         interaction begins.\n         \n         Terminology:\n         BaseBehavior: For change operations that succeed chance\n         and test or if chance is 100% or no tests, the statistic stores the\n         start time and when interaction ends determine how much time is passed\n         and multiply amount.  Continuous statistic WILL NOT decay with this\n         behavior.  This is for better performance.\n         \n         IntervalBehavior:  If continuous statistic is using interval behavior.\n         the amount tuned will be given at specified interval if chance and\n         tests succeeds.  Continuous statistics WILL decay between interval\n         time.\n                 \n         Tuning Behavior \n         APPLY_AT_START_ONLY: If chance and tests for change operation is\n         successful, periodic update will occur and follow BaseBehavior.  If\n         either fail, change operation is not given at any point.\n         \n         RETEST_ON_INTERVAL: If test and chance succeeds, then this will follow\n         BaseBehavior.  If test or chance fails, this operation will follow\n         interval behavior.\n         \n         APPLY_AT_INTERVAL_ONLY: This will strictly follow Interval Behavior.\n         ',
       tunable_type=PeriodicStatisticBehavior,
       default=PeriodicStatisticBehavior.APPLY_AT_START_ONLY), 
     'statistic_multipliers':TunableList(description='\n        Tunables for adding statistic based multipliers to the payout in the\n        format:\n        \n        amount *= statistic.value\n        ',
       tunable=TunableStatisticModifierCurve.TunableFactory()), 
     'object_cost_multiplier':OptionalTunable(description='\n        When enabled allows you to multiply the stat gain amount based on the \n        value of the object specified.\n        ',
       tunable=TunableObjectCostModifierCurve.TunableFactory())}

    def __init__(self, amount=0, min_value=None, max_value=None, exclusive_to_owning_si=None, periodic_change_behavior=PeriodicStatisticBehavior.APPLY_AT_START_ONLY, maximum=None, statistic_multipliers=None, object_cost_multiplier=None, **kwargs):
        (super().__init__)(**kwargs)
        self._amount = amount
        self.maximum = maximum
        self._min_value = min_value
        self._max_value = None
        if max_value is not None:
            self._max_value = max_value
        else:
            if maximum is not None:
                self._max_value = maximum(self.stat)
        self._exclusive_to_owning_si = exclusive_to_owning_si
        self.periodic_change_behavior = periodic_change_behavior
        self._statistic_multipliers = statistic_multipliers
        self._object_cost_multiplier = object_cost_multiplier

    @property
    def exclusive_to_owning_si(self):
        return self._exclusive_to_owning_si

    def get_value(self, obj=None, interaction=None, sims=None):
        multiplier = 1
        if sims:
            targets = sims.copy()
        else:
            if interaction is not None:
                targets = interaction.get_participants(ParticipantType.Actor)
            else:
                targets = None
        if targets:
            multiplier = self.stat.get_skill_based_statistic_multiplier(targets, self._amount)
            for sim in targets:
                resolver = interaction.get_resolver() if interaction is not None else SingleSimResolver(sim)
                local_mult = self._get_local_statistic_multipliers(resolver)
                multiplier *= local_mult

        if self._object_cost_multiplier is not None:
            resolver = interaction.get_resolver() if interaction is not None else SingleActorAndObjectResolver(sim, object)
            multiplier *= self._get_object_cost_multiplier(resolver)
        return self._amount * multiplier

    def _get_interval(self, aop):
        return StatisticOperation.STATIC_CHANGE_INTERVAL

    def _apply(self, tracker, resolver=None):
        interaction = resolver.interaction if resolver is not None else None
        multiplier = self._get_local_multipliers(resolver=resolver)
        amount = self._amount * multiplier
        tracker.add_value((self.stat), amount, min_value=(self._min_value), max_value=(self._max_value),
          interaction=interaction)

    def _remove(self, tracker, interaction=None):
        resolver = interaction.get_resolver if interaction is not None else SingleSimResolver(tracker.owner)
        multiplier = self._get_local_multipliers(resolver=resolver)
        amount = self._amount * multiplier
        tracker.add_value((self.stat), (-amount), min_value=(self._min_value), max_value=(self._max_value),
          interaction=interaction)

    def _get_local_multipliers(self, resolver):
        multiplier = self._get_local_statistic_multipliers(resolver)
        multiplier *= self._get_object_cost_multiplier(resolver)
        return multiplier

    def _get_local_statistic_multipliers(self, resolver):
        multiplier = 1
        if self._statistic_multipliers is not None:
            for data in self._statistic_multipliers:
                multiplier *= data.get_multiplier(resolver, None)

        return multiplier

    def _get_object_cost_multiplier(self, resolver):
        multiplier = 1
        if self._object_cost_multiplier is not None:
            multiplier *= self._object_cost_multiplier.get_multiplier(resolver, None)
        return multiplier


class StatisticSetOp(StatisticOperation):
    FACTORY_TUNABLES = {'value': Tunable(description='\n            The new statistic value.',
                tunable_type=int,
                default=None)}

    def __init__(self, value=None, **kwargs):
        (super().__init__)(**kwargs)
        self.value = value

    def __repr__(self):
        if self.stat is not None:
            return '<{}: {} set to {}>'.format(self.__class__.__name__, self.stat.__name__, self.value)
        return '<{}: Stat is None in StatisticSetOp>'.format(self.__class__.__name__)

    def get_value(self, obj=None, interaction=None, sims=None):
        stat_value = self._attempt_to_get_real_stat_value(obj, interaction)
        return self.value - stat_value

    def _apply(self, tracker, resolver=None):
        interaction = resolver.interaction if resolver is not None else None
        tracker.set_value((self.stat), (self.value), interaction=interaction)


class StatisticSetRankOp(StatisticOperation):

    @TunableFactory.factory_option
    def statistic_override(pack_safe=False):
        return {'stat': TunableReference(description='\n                The statistic we are operating on.\n                ',
                   manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
                   pack_safe=pack_safe,
                   class_restrictions=('RankedStatistic', ))}

    FACTORY_TUNABLES = {'value': Tunable(description='\n            The new rank value.\n            ',
                tunable_type=int,
                default=None)}

    def __init__(self, value=None, **kwargs):
        (super().__init__)(**kwargs)
        self.value = value

    def __repr__(self):
        if self.stat is not None:
            return '<{}: {} set rank to {}>'.format(self.__class__.__name__, self.stat.__name__, self.value)
        return '<{}: Stat is None in StatisticSetRankOp>'.format(self.__class__.__name__)

    def get_value(self, obj=None, interaction=None, sims=None):
        stat_value = self._attempt_to_get_real_stat_value(obj, interaction)
        rank_value = self.stat.points_to_rank(self.value)
        return rank_value - stat_value

    def _apply(self, tracker, resolver=None):
        interaction = resolver.interaction if resolver is not None else None
        tracker.set_value((self.stat), (self.stat.points_to_rank(self.value)), interaction=interaction)


class StatisticSetRangeOp(StatisticOperation):

    class _StatisticSetRangeFloat(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'value_range': TunableInterval(description='\n                The upper and lower bound of the range.\n                ',
                          tunable_type=float,
                          default_lower=1,
                          default_upper=2)}

        def get_value(self):
            return self.value_range.random_float()

    class _StatisticSetRangeInt(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'value_range': TunableInterval(description='\n                The upper and lower bound of the range.\n                ',
                          tunable_type=int,
                          default_lower=1,
                          default_upper=2)}

        def get_value(self):
            return self.value_range.random_int()

    FACTORY_TUNABLES = {'locked_args':{'subject': ParticipantType.Actor}, 
     'value_type':TunableVariant(float_range=_StatisticSetRangeFloat.TunableFactory(),
       int_range=_StatisticSetRangeInt.TunableFactory(),
       default='int_range')}
    REMOVE_INSTANCE_TUNABLES = ('advertise', 'tests', 'chance')

    def __init__(self, value_type=None, **kwargs):
        (super().__init__)(**kwargs)
        self.value_type = value_type

    def __repr__(self):
        if self.stat is not None:
            return '<{}: {} set in range [{},{}]>'.format(self.__class__.__name__, self.stat.__name__, self.value_type.value_range.lower_bound, self.value_type.value_range.upper_bound)
        return '<{}: Stat is None in StatisticSetRangeOp>'.format(self.__class__.__name__)

    def get_value(self, obj=None, interaction=None, sims=None):
        stat_value = self._attempt_to_get_real_stat_value(obj, interaction)
        return self.value_type.value_range.upper_bound - stat_value

    def _apply(self, tracker, resolver=None):
        value = self.value_type.get_value()
        tracker.set_value((self.stat), value, interaction=None)


class StatisticSetMaxOp(StatisticOperation):

    def __init__(self, **kwargs):
        (super().__init__)(**kwargs)

    def __repr__(self):
        if self.stat is not None:
            return '<{}: {} maximum>'.format(self.__class__.__name__, self.stat.__name__)
        return '<{}: Stat is None in StatisticSetMaxOp>'.format(self.__class__.__name__)

    def get_value(self, obj=None, interaction=None, sims=None):
        stat_value = self._attempt_to_get_real_stat_value(obj, interaction)
        return self.stat.max_value - stat_value

    def _apply(self, tracker, **kwargs):
        tracker.set_max(self.stat)


class StatisticSetMinOp(StatisticOperation):

    def __init__(self, **kwargs):
        (super().__init__)(**kwargs)

    def __repr__(self):
        if self.stat is not None:
            return '<{}: {} minimum>'.format(self.__class__.__name__, self.stat.__name__)
        return '<{}: Stat is None in StatisticSetMinOp>'.format(self.__class__.__name__)

    def get_value(self, obj=None, interaction=None, sims=None):
        stat_value = self._attempt_to_get_real_stat_value(obj, interaction)
        return self.stat.min_value - stat_value

    def _apply(self, tracker, **kwargs):
        tracker.set_min(self.stat)


class StatisticAddOp(StatisticOperation):

    def __init__(self, **kwargs):
        (super().__init__)(**kwargs)

    def __repr__(self):
        if self.stat is not None:
            return '<{}: {} add stat>'.format(self.__class__.__name__, self.stat.__name__)
        return '<{}: Stat is None in StatisticAddOp>'.format(self.__class__.__name__)

    def get_value(self, obj=None, interaction=None, sims=None):
        return 0

    def _apply(self, tracker, **kwargs):
        tracker.add_statistic(self.stat)


class StatisticRemoveOp(StatisticOperation):

    def __init__(self, **kwargs):
        (super().__init__)(**kwargs)

    def __repr__(self):
        if self.stat is not None:
            return '<{}: {} remove/set to convergence>'.format(self.__class__.__name__, self.stat.__name__)
        return '<{}: Stat is None in StatisticRemoveOp>'.format(self.__class__.__name__)

    def get_value(self, obj=None, interaction=None, sims=None):
        return 0

    def _apply(self, tracker, **kwargs):
        tracker.remove_statistic(self.stat)


class StatisticLockOp(BaseLootOperation):
    FACTORY_TUNABLES = {'stat':TunablePackSafeReference(description='\n            The statistic we are operating on.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC),
       class_restrictions=('Commodity', )), 
     'lock':Tunable(description='\n            Lock or unlock a statistic.\n            ',
       tunable_type=bool,
       default=True), 
     'lock_action':TunableEnumEntry(description='\n            Determine what to do with the value of a\n            statistic when we lock it.\n            ',
       tunable_type=StatisticLockAction,
       default=StatisticLockAction.DO_NOT_CHANGE_VALUE)}

    def __init__(self, stat, lock, lock_action, **kwargs):
        (super().__init__)(**kwargs)
        self._stat = stat
        self._lock = lock
        self._lock_action = lock_action

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if self._stat is None:
            return
        else:
            statistic_component = subject.get_component(objects.components.types.STATISTIC_COMPONENT)
            if statistic_component is None:
                logger.error('Trying to lock statistic {} on {}, but it has no Statistic Component.', self._stat, subject)
                return
                interaction = resolver.interaction
                if self._lock:
                    statistic_component.lock_statistic(self._stat, self._lock_action, 'locked by loot in interaction {} at {}'.format(interaction, services.time_service().sim_now))
            else:
                statistic_component.unlock_statistic(self._stat, 'unlocked by loot in interaction {} at {}'.format(interaction, services.time_service().sim_now))


class TransferType(enum.Int):
    ADDITIVE = 0
    SUBTRACTIVE = 1
    REPLACEMENT = 2
    AVERAGE = 3


class StatisticTransferOp(StatisticOperation):
    FACTORY_TUNABLES = {'statistic_donor':TunableEnumEntry(description='\n            The owner of the statistic we are transferring the value from.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.TargetSim), 
     'transferred_stat':TunableReference(description='\n            The statistic whose value to transfer.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC)), 
     'transfer_type':TunableEnumEntry(description='\n            Type of statistic transfer to use.\n            ',
       tunable_type=TransferType,
       default=TransferType.ADDITIVE), 
     'transfer_type_average_advanced':OptionalTunable(description='\n            If enabled, the average calculation will be the sum of multiplying\n            the stat value and stat quantity then dividing with total quantity.\n            T  = Transferred Stat value\n            S  = Stat value\n            QT = Quantity Transferred Stat value\n            QS = Quantity Stat value\n            Result = ((T * QT) + (S * QS)) / (QT + QS)\n            \n            If disabled, the result will calculate Mean of 2 stat values.\n            Result = (T + S) / 2\n            ',
       tunable=TunableTuple(description='\n                Statistic quantities for both subject and donor.\n                ',
       quantity_transferred_stat=TunableReference(description='\n                    Statistic quantity donor which will be applied to the\n                    average calculation.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC))),
       quantity_stat=TunableReference(description='\n                    Statistic quantity subject which will be applied to the\n                    average calculation.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)))))}

    def __init__(self, statistic_donor=None, transferred_stat=None, transfer_type=None, transfer_type_average_advanced=None, **kwargs):
        (super().__init__)(**kwargs)
        self._statistic_donor = statistic_donor
        self._transferred_stat = transferred_stat
        self._transfer_type = transfer_type
        self._transfer_type_average_advanced = transfer_type_average_advanced

    def __repr__(self):
        if self.stat is not None:
            return '<{}: {} transfer>'.format(self.__class__.__name__, self.stat.__name__)
        return '<{}: Stat is None in StatisticTransferOp>'.format(self.__class__.__name__)

    def get_value(self, obj=None, interaction=None, sims=None):
        return self.stat.get_value()

    def _apply(self, tracker, resolver=None):
        interaction = resolver.interaction if resolver is not None else None
        donors = resolver.get_participants(self._statistic_donor) if resolver is not None else []
        for donor in donors:
            transfer_stat_tracker = donor.get_tracker(self._transferred_stat)
            if transfer_stat_tracker is None:
                continue
            transfer_value = transfer_stat_tracker.get_value(self._transferred_stat)
            if self._transfer_type == TransferType.ADDITIVE:
                tracker.add_value((self.stat), transfer_value, interaction=interaction)
            elif self._transfer_type == TransferType.SUBTRACTIVE:
                tracker.add_value((self.stat), (-transfer_value), interaction=interaction)
            elif self._transfer_type == TransferType.REPLACEMENT:
                tracker.set_value((self.stat), transfer_value, interaction=interaction)
            elif self._transfer_type == TransferType.AVERAGE:
                subject_value = tracker.get_value(self.stat)
                if self._transfer_type_average_advanced is None:
                    average_value = (subject_value + transfer_value) / 2
                else:
                    subject = tracker.owner
                    if subject is None:
                        logger.error('Failed to find the owner for tracker {}.', tracker, owner='mkartika')
                        continue
                    q_stat_tracker = subject.get_tracker(self._transfer_type_average_advanced.quantity_stat)
                    q_transfer_stat_tracker = donor.get_tracker(self._transfer_type_average_advanced.quantity_transferred_stat)
                    if q_stat_tracker is None:
                        logger.error('Failed to find quantity stat tracker for stat {} on {}.', (self._transfer_type_average_advanced.quantity_stat),
                          subject,
                          owner='mkartika')
                        continue
                    if q_transfer_stat_tracker is None:
                        logger.error('Failed to find quantity stat tracker for stat {} on {}.', (self._transfer_type_average_advanced.quantity_transferred_stat),
                          donor,
                          owner='mkartika')
                        continue
                    q_value = q_stat_tracker.get_value(self._transfer_type_average_advanced.quantity_stat)
                    q_transfer_value = q_transfer_stat_tracker.get_value(self._transfer_type_average_advanced.quantity_transferred_stat)
                    average_value = (subject_value * q_value + transfer_value * q_transfer_value) / (q_value + q_transfer_value)
                tracker.set_value((self.stat), average_value, interaction=interaction)


class NormalizeStatisticsOp(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'stats_to_normalize':TunableList(description='\n            Stats to be affected by the normalization.\n            ',
       tunable=TunableReference((services.get_instance_manager(sims4.resources.Types.STATISTIC)),
       class_restrictions=(statistics.commodity.Commodity))), 
     'normalize_percent':TunablePercent(description='\n            In seeking the average value, this is the percent of movement toward the average value \n            the stat will move to achieve the new value. For example, if you have a Sim with 50 \n            fun, and a Sim with 100 fun, and want to normalize them exactly halfway to their \n            average of 75, tune this to 100%. A value of 50% would move one Sim to 67.5 and the other\n            to 77.5\n            ',
       default=100,
       maximum=100,
       minimum=0)}

    def __init__(self, stats_to_normalize, normalize_percent, **kwargs):
        (super().__init__)(**kwargs)
        self._stats = stats_to_normalize
        self._normalize_percent = normalize_percent

    def _apply_to_subject_and_target(self, subject, target, resolver):
        for stat_type in self._stats:
            source_tracker = target.get_tracker(stat_type)
            if source_tracker is None:
                return
            if not source_tracker.has_statistic(stat_type):
                continue
            target_tracker = subject.get_tracker(stat_type)
            if target_tracker is None:
                return
            source_value = source_tracker.get_value(stat_type)
            target_value = target_tracker.get_value(stat_type)
            average_value = (source_value + target_value) / 2
            source_percent_gain = (source_value - average_value) * self._normalize_percent
            target_percent_gain = (target_value - average_value) * self._normalize_percent
            target_tracker.set_value(stat_type, source_value - source_percent_gain)
            source_tracker.set_value(stat_type, target_value - target_percent_gain)


class SkillEffectivenessLoot(StatisticChangeOp):
    FACTORY_TUNABLES = {'subject':TunableEnumEntry(description='\n            The sim(s) to operation is applied to.',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'effectiveness':TunableEnumEntry(description='\n            Enum to determine which curve to use when giving points to sim.',
       tunable_type=statistics.skill.SkillEffectiveness,
       needs_tuning=True,
       default=statistics.skill.SkillEffectiveness.STANDARD), 
     'level':Tunable(description='\n            x-point on skill effectiveness curve.',
       tunable_type=int,
       default=0), 
     'locked_args':{'amount': 0}}

    def __init__(self, stat, amount, effectiveness, level, **kwargs):
        if stat is None:
            final_amount = 0
        else:
            final_amount = stat.get_skill_effectiveness_points_gain(effectiveness, level)
        (super().__init__)(stat=stat, amount=final_amount, **kwargs)


class TunableStatisticChange(TunableVariant):

    def __init__(self, *args, locked_args=None, variant_locked_args=None, gain_type=GAIN_TYPE_AMOUNT, include_relationship_ops=True, statistic_override=None, description='A variant of statistic operations.', **kwargs):
        if include_relationship_ops:
            kwargs['object_relationship_change'] = (StatisticAddObjectRelationship.TunableFactory)(description='\n                Add to the object relationship score statistic for this Super Interaction.\n                ', 
             amount=gain_type, **ObjectRelationshipOperation.DEFAULT_PARTICIPANT_ARGUMENTS)
            kwargs['relationship_change'] = (StatisticAddRelationship.TunableFactory)(description='\n                Adds to the relationship score statistic for this Super Interaction\n                ', 
             amount=gain_type, **RelationshipOperation.DEFAULT_PARTICIPANT_ARGUMENTS)
            kwargs['relationship_change_multiple'] = (StatisticAddRelationshipMultiple.TunableFactory)(description='\n                Modifies the relationship track score of multiple tracks at \n                once.\n                ', 
             amount=gain_type, **RelationshipOperation.DEFAULT_PARTICIPANT_ARGUMENTS)
            kwargs['relationship_set'] = (StatisticSetRelationship.TunableFactory)(description='\n                Sets the relationship score statistic to a specific value.\n                ', **RelationshipOperation.DEFAULT_PARTICIPANT_ARGUMENTS)
            kwargs['relationship_remove_track'] = (StatisticRemoveRelationshipTrack.TunableFactory)(description='\n                Removes the given relationship track.\n                ', **RelationshipOperation.DEFAULT_PARTICIPANT_ARGUMENTS)
            kwargs['relationship_set_multiple'] = (StatisticSetRelationshipMultiple.TunableFactory)(description='\n                Sets the relationship track score of multiple tracks at \n                once.\n                ', **RelationshipOperation.DEFAULT_PARTICIPANT_ARGUMENTS)
            kwargs['relationship_set_max'] = (StatisticSetRelationshipMax.TunableFactory)(description='\n                Sets a relationship track to its maximum value.\n                ', **RelationshipOperation.DEFAULT_PARTICIPANT_ARGUMENTS)
            kwargs['random_relationship_set'] = (RandomSimStatisticAddRelationship.TunableFactory)(description='\n                Adds the relationship statistic score about an amount to a \n                random sim selected out of all the known sims for the Actor.\n                ', 
             locked_args={'target_participant_type':ParticipantType.Actor, 
 'advertise':False,  'stat':None}, **RelationshipOperation.DEFAULT_PARTICIPANT_ARGUMENTS)
        (super().__init__)(args, description=description, 
         statistic_change=(StatisticChangeOp.TunableFactory)(**, **StatisticOperation.DEFAULT_PARTICIPANT_ARGUMENTS), 
         statistic_add=(StatisticAddOp.TunableFactory)(description='\n                Attempt to add the specified statistic.\n                ', 
 locked_args=locked_args, 
 statistic_override=statistic_override, **StatisticOperation.DEFAULT_PARTICIPANT_ARGUMENTS), 
         statistic_remove=(StatisticRemoveOp.TunableFactory)(description='\n                Attempt to remove the specified statistic.\n                ', 
 locked_args=locked_args, 
 statistic_override=statistic_override, **StatisticOperation.DEFAULT_PARTICIPANT_ARGUMENTS), 
         statistic_set=(StatisticSetOp.TunableFactory)(description='\n                Set a statistic to the provided value.\n                ', 
 locked_args=locked_args, 
 statistic_override=statistic_override, **StatisticOperation.DEFAULT_PARTICIPANT_ARGUMENTS), 
         statistic_set_rank=(StatisticSetRankOp.TunableFactory)(description='\n                Set a Ranked Statistic to a specific rank level.\n                ', 
 locked_args=locked_args, 
 statistic_override=statistic_override, **StatisticOperation.DEFAULT_PARTICIPANT_ARGUMENTS), 
         statistic_set_max=(StatisticSetMaxOp.TunableFactory)(description='\n                Set a statistic to its maximum value.\n                ', 
 locked_args=locked_args, 
 statistic_override=statistic_override, **StatisticOperation.DEFAULT_PARTICIPANT_ARGUMENTS), 
         statistic_set_min=(StatisticSetMinOp.TunableFactory)(description='\n                Set a statistic to its minimum value.\n                ', 
 locked_args=locked_args, 
 statistic_override=statistic_override, **StatisticOperation.DEFAULT_PARTICIPANT_ARGUMENTS), 
         statistic_set_in_range=(StatisticSetRangeOp.TunableFactory)(description='\n                Set a statistic to a random value in the tuned range.\n                ', 
 locked_args=locked_args, 
 statistic_override=statistic_override, **StatisticOperation.DEFAULT_PARTICIPANT_ARGUMENTS), 
         statistic_transfer=(StatisticTransferOp.TunableFactory)(description='\n                Transfer a statistic value from one target to another.\n                ', 
 locked_args=locked_args, **StatisticOperation.DEFAULT_PARTICIPANT_ARGUMENTS), 
         statistic_lock=StatisticLockOp.TunableFactory(description='\n                Lock or Unlock a statistic.\n                '), 
         statistic_remove_by_category=RemoveStatisticByCategory.TunableFactory(description='\n                Remove all statistics of a specific category.\n                '), 
         statistic_change_by_category=ChangeStatisticByCategory.TunableFactory(description='\n                Change value of  all statistics of a specific category.\n                '), 
         locked_args=variant_locked_args, **kwargs)


class TunableProgressiveStatisticChange(TunableVariant):

    def __init__(self, *args, locked_args=None, **kwargs):
        (super().__init__)(args, description='A variant of statistic operations.', 
         statistic_change=(StatisticChangeOp.TunableFactory)(description='\n                Modify the value of a statistic.\n                ', 
 locked_args=locked_args, **StatisticOperation.DEFAULT_PARTICIPANT_ARGUMENTS), 
         relationship_change=(StatisticAddRelationship.TunableFactory)(description='\n                Adds to the relationship score statistic for this Super Interaction\n                ', **RelationshipOperation.DEFAULT_PARTICIPANT_ARGUMENTS), **kwargs)


class DynamicSkillLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'skill_loot_data_override':TunableSkillLootData(description="\n            This data will override loot data in the interaction. In\n            interaction, tuning field 'skill_loot_data' is used to determine\n            skill loot data."), 
     'exclusive_to_owning_si':Tunable(description='\n            If enabled, this gain will be exclusive to the SI that created it\n            and will not be allowed to occur if the sim is running mixers from\n            a different SI.\n            If disabled, this gain will happen as long as this\n            SI is active, regardless of which SI owns the mixer the sim is\n            currently running.\n            This is only effective on Sims.\n            ',
       tunable_type=bool,
       needs_tuning=True,
       default=True)}

    def __init__(self, skill_loot_data_override, exclusive_to_owning_si, **kwargs):
        (super().__init__)(**kwargs)
        self._skill_loot_data_override = skill_loot_data_override
        self._exclusive_to_owning_si = exclusive_to_owning_si

    @property
    def periodic_change_behavior(self):
        return PeriodicStatisticBehavior.APPLY_AT_START_ONLY

    @property
    def exclusive_to_owning_si(self):
        return self._exclusive_to_owning_si

    def _get_skill_level_data(self, interaction):
        stat = self._skill_loot_data_override.stat
        if stat is None:
            if interaction is not None:
                stat = interaction.stat_from_skill_loot_data
                if stat is None:
                    return (None, None, None)
        effectiveness = self._skill_loot_data_override.effectiveness
        if effectiveness is None:
            if interaction is not None:
                effectiveness = interaction.skill_effectiveness_from_skill_loot_data
                if effectiveness is None:
                    logger.error('Skill Effectiveness is not tuned for this loot operation in {}', interaction)
                    return (None, None, None)
        level_range = self._skill_loot_data_override.level_range
        if level_range is None:
            if interaction is not None:
                level_range = interaction.level_range_from_skill_loot_data
        return (
         stat, effectiveness, level_range)

    def get_stat(self, interaction):
        stat = self._skill_loot_data_override.stat
        if stat is None:
            stat = interaction.stat_from_skill_loot_data
        return stat

    def get_value(self, obj=None, interaction=None, sims=None):
        amount = 0
        multiplier = 1
        if obj is not None:
            if interaction is not None:
                stat_type, effectiveness, level_range = self._get_skill_level_data(interaction)
                if stat_type is None:
                    return 0
                else:
                    tracker = obj.get_tracker(stat_type)
                    if tracker is None:
                        return stat_type.default_value
                        amount = self._get_change_amount(tracker, stat_type, effectiveness, level_range)
                        if sims:
                            targets = sims.copy()
                    else:
                        targets = interaction.get_participants(ParticipantType.Actor)
                if targets:
                    multiplier = stat_type.get_skill_based_statistic_multiplier(targets, amount)
        return amount * multiplier

    def _apply_to_subject_and_target(self, subject, target, resolver):
        stat_type, effectiveness, level_range = self._get_skill_level_data(resolver.interaction)
        if stat_type is None:
            return
        tracker = subject.get_tracker(stat_type)
        if tracker is not None:
            amount = self._get_change_amount(tracker, stat_type, effectiveness, level_range)
            tracker.add_value(stat_type, amount, interaction=(resolver.interaction))

    def _get_change_amount(self, tracker, stat_type, effectiveness, level_range):
        cur_level = tracker.get_user_value(stat_type)
        if level_range is not None:
            point_level = math.clamp(level_range.lower_bound, cur_level, level_range.upper_bound)
        else:
            point_level = cur_level
        amount = stat_type.get_skill_effectiveness_points_gain(effectiveness, point_level)
        return amount


class DynamicVariantSkillLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'skill_loot_data': TunableVariantSkillLootData(description='\n            The reference to the skill data.\n            ')}

    def __init__(self, skill_loot_data, **kwargs):
        (super().__init__)(**kwargs)
        self._skill_loot_data = skill_loot_data

    def _get_skill_level_data(self, subject, interaction):
        stat = self._skill_loot_data.stat(subject, interaction)
        if stat is None:
            return (None, None, None)
        effectiveness = self._skill_loot_data.effectiveness
        if effectiveness is None:
            logger.error('Skill Effectiveness is not tuned for this loot operation in {}')
            return (None, None, None)
        level_range = self._skill_loot_data.level_range
        return (
         stat, effectiveness, level_range)

    def _get_change_amount(self, tracker, stat_type, effectiveness, level_range):
        cur_level = tracker.get_user_value(stat_type)
        if level_range is not None:
            point_level = math.clamp(level_range.lower_bound, cur_level, level_range.upper_bound)
        else:
            point_level = cur_level
        amount = stat_type.get_skill_effectiveness_points_gain(effectiveness, point_level)
        return amount

    def _apply_to_subject_and_target(self, subject, target, resolver):
        stat_type, effectiveness, level_range = self._get_skill_level_data(subject, resolver.interaction)
        if stat_type is None:
            return
        tracker = subject.get_tracker(stat_type)
        if tracker is not None:
            amount = self._get_change_amount(tracker, stat_type, effectiveness, level_range)
            tracker.add_value(stat_type, amount, interaction=(resolver.interaction))


class BaseStatisticByCategoryOp(BaseLootOperation):
    FACTORY_TUNABLES = {'statistic_category': TunableEnumEntry((statistics.statistic_categories.StatisticCategory), (statistics.statistic_categories.StatisticCategory.INVALID), description='The category of commodity to remove.')}

    def __init__(self, statistic_category, **kwargs):
        (super().__init__)(**kwargs)
        self._category = statistic_category


class RemoveStatisticByCategory(BaseStatisticByCategoryOp):
    FACTORY_TUNABLES = {'count_to_remove': OptionalTunable(description='\n            If enabled, randomly remove x number of commodities from the tuned category.\n            If disabled, all commodities specified by category will be removed.\n            ',
                          tunable=TunableRange(tunable_type=int,
                          default=1,
                          minimum=1))}

    def __init__(self, count_to_remove, **kwargs):
        (super().__init__)(**kwargs)
        self._count_to_remove = count_to_remove

    def _apply_to_subject_and_target(self, subject, target, resolver):
        category = self._category
        commodity_tracker = subject.commodity_tracker
        if commodity_tracker is None:
            return
        qualified_commodities = [c for c in commodity_tracker if category in c.get_categories()]
        if self._count_to_remove:
            random.shuffle(qualified_commodities)
        count_to_remove = min(self._count_to_remove, len(qualified_commodities)) if self._count_to_remove else len(qualified_commodities)
        for i in range(count_to_remove):
            commodity = qualified_commodities[i]
            if commodity.remove_on_convergence:
                commodity_tracker.remove_statistic(commodity.stat_type)
            else:
                commodity_tracker.set_value(commodity.stat_type, commodity.get_initial_value())


class TunableChangeAmountFactory(TunableFactory):

    @staticmethod
    def apply_change(sim, statistic, change_amout):
        stat_type = type(statistic)
        tracker = sim.get_tracker(type(statistic))
        if tracker is not None:
            tracker.add_value(stat_type, change_amout)

    FACTORY_TYPE = apply_change

    def __init__(self, **kwargs):
        (super().__init__)(change_amout=Tunable(description='\n                            Amount of change to be applied to statistics that match category.',
                         tunable_type=float,
                         default=0), **kwargs)


class TunablePercentChangeAmountFactory(TunableFactory):

    @staticmethod
    def apply_change(subject, statistic, percent_change_amount):
        stat_type = type(statistic)
        tracker = subject.get_tracker(stat_type)
        if tracker is not None:
            current_value = tracker.get_value(stat_type)
            change_amount = current_value * percent_change_amount
            tracker.add_value(stat_type, change_amount)

    FACTORY_TYPE = apply_change

    def __init__(self, **kwargs):
        (super().__init__)(percent_change_amount=TunablePercent(description='\n                             Percent of current value of statistic should amount\n                             be changed.  If you want to decrease the amount by\n                             50% enter -50% into the tuning field.',
                                  default=(-50),
                                  minimum=(-100)), **kwargs)


class ChangeStatisticByCategory(BaseStatisticByCategoryOp):
    FACTORY_TUNABLES = {'change': TunableVariant(stat_change=(TunableChangeAmountFactory()),
                 percent_change=(TunablePercentChangeAmountFactory()))}

    def __init__(self, change, **kwargs):
        (super().__init__)(**kwargs)
        self._change = change

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject.commodity_tracker is not None:
            category = self._category
            for commodity in tuple(subject.commodity_tracker):
                if category in commodity.get_categories():
                    self._change(subject, commodity)


class ObjectStatisticChangeOp(StatisticChangeOp):
    FACTORY_TUNABLES = {'locked_args': {'subject':None, 
                     'advertise':False, 
                     'tests':(), 
                     'chance':SuccessChance.ONE, 
                     'exclusive_to_owning_si':False}}

    def apply_to_object(self, obj):
        tracker = obj.get_tracker(self.stat)
        if tracker is not None:
            self._apply(tracker)

    def remove_from_object(self, obj):
        tracker = obj.get_tracker(self.stat)
        if tracker is not None:
            self._remove(tracker)

    def get_fulfillment_rate(self, interaction):
        return 0


class RelationshipOperationBase(LootOperationTargetFilterTestMixin, StatisticOperation):
    FACTORY_TUNABLES = {'headline_icon_modifier':OptionalTunable(description='\n            If enabled then when updating the relationship track we will\n            use an icon modifier when sending the headline.\n            ',
       tunable=TunableIcon(description='\n                The icon that we will use as a modifier to the headline.\n                ')), 
     'locked_args':{'advertise':False, 
      'stat':None}}
    DEFAULT_PARTICIPANT_ARGUMENTS = {'subject':TunableEnumFlags(description='\n            The owner Sim for this relationship change. Relationship is updated\n            between the participant sim and the target objects as defined by\n            the object relationship track.\n            ',
       enum_type=ParticipantType,
       invalid_enums=ParticipantType.Invalid,
       default=ParticipantType.Actor), 
     'target_participant_type':TunableEnumFlags(description="\n            The target Sim for this relationship change. Any\n            relationship that would be given to 'self' is discarded.\n            ",
       enum_type=ParticipantType,
       invalid_enums=(
      ParticipantType.Invalid,),
       default=ParticipantType.Invalid)}

    def __init__(self, track_range=None, headline_icon_modifier=None, **kwargs):
        (super().__init__)(**kwargs)
        self._track_range = track_range
        self._headline_icon_modifier = headline_icon_modifier
        self._loot_type = LootType.RELATIONSHIP

    def _pre_process_for_source_and_target(self, source_sim_info, target_sim_info):
        pass

    def find_op_participants(self, interaction, source=None, target=None):
        if source is None:
            actors = interaction.get_participants(self.subject)
            if not actors:
                return (
                 source, target)
            source = next(iter(actors))
        if target is None:
            targets = interaction.get_participants(self.target_participant_type)
            for potential_target in targets:
                if potential_target is not source:
                    target = potential_target
                    break

        return (
         source, target)

    def _get_interval(self, aop):
        return StatisticOperation.STATIC_CHANGE_INTERVAL

    def _apply_to_subject_and_target(self, subject, target, resolver):
        sim_mgr = services.sim_info_manager()
        if subject == ParticipantType.AllRelationships:
            if target == ParticipantType.AllRelationships:
                logger.error('Could not evaluate participants for {} since both subject and target were AllRelationships. Need a source sim info.', self)
                return
            else:
                target_sim_info = self._get_sim_info_from_participant(target)
                return target_sim_info or None
            source_sim_infos = set((sim_mgr.get(relations.get_other_sim_id(target_sim_info.sim_id)) for relations in target_sim_info.relationship_tracker))
            source_sim_infos.discard(None)
            target_sim_infos = (target_sim_info,)
        else:
            if target == ParticipantType.AllRelationships:
                source_sim_info = self._get_sim_info_from_participant(subject)
                if not source_sim_info:
                    return
                target_sim_infos = set((sim_mgr.get(relations.get_other_sim_id(source_sim_info.sim_id)) for relations in source_sim_info.relationship_tracker))
                target_sim_infos.discard(None)
                source_sim_infos = (source_sim_info,)
            else:
                source_sim_infos = (
                 self._get_sim_info_from_participant(subject),)
                if source_sim_infos:
                    return source_sim_infos[0] or None
                else:
                    target_sim_infos = (
                     self._get_sim_info_from_participant(target),)
                    return target_sim_infos and target_sim_infos[0] or None
        for target_sim_info in target_sim_infos:
            for source_sim_info in source_sim_infos:
                if source_sim_info is target_sim_info:
                    self.target_participant_type & ParticipantType.PickedSim or logger.error('Attempting to give relationship loot between the same sim {} in {} with resolver: {}', target_sim_info, self, resolver, owner='nabaker')
                    continue
                self._pre_process_for_source_and_target(source_sim_info, target_sim_info)
                self._apply_to_sim_info(source_sim_info, target_sim_info.sim_id)

    def _get_sim_info_from_participant(self, participant):
        if isinstance(participant, int):
            sim_info_manager = services.sim_info_manager()
            if sim_info_manager is None:
                return
            sim_info = sim_info_manager.get(participant)
        else:
            sim_info = getattr(participant, 'sim_info', participant)
        if sim_info is None:
            logger.error('Could not get Sim Info from {0} in StatisticAddRelationship loot op.', participant)
        return sim_info

    def _apply_to_sim_info(self, source_sim_info, target_sim_id, **kwargs):
        (self._apply_relationship_operation)(source_sim_info.relationship_tracker,
 target_sim_id, headline_icon_modifier=self._headline_icon_modifier, **kwargs)

    def _apply_relationship_operation(self, relationship_tracker, target_sim_id, **kwargs):
        raise NotImplementedError

    def _get_display_text(self, resolver=None):
        value = self.get_value()
        if value:
            return (self.DISPLAY_TEXT)(*self._get_display_text_tokens(resolver))

    def _get_display_text_tokens(self, resolver=None):
        subject = None
        target = None
        if resolver is not None:
            subject = resolver.get_participant(self._subject)
            target = resolver.get_participant(self._target_participant_type)
        return (
         subject, target, self.get_value())


class RelationshipOperation(RelationshipOperationBase):
    FACTORY_TUNABLES = {'track':TunableReference(description='\n                The track to be manipulated.',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC),
       class_restrictions='RelationshipTrack'), 
     'track_range':TunableInterval(description='\n            The relationship track must > lower_bound and <= upper_bound for\n            the operation to apply.',
       tunable_type=float,
       default_lower=-101,
       default_upper=100)}

    def __init__(self, track_range=None, track=DEFAULT, **kwargs):
        (super().__init__)(**kwargs)
        self._track_range = track_range
        self._track = DEFAULT if track is None else track

    def __repr__(self):
        return '<{} {} {}, subject: {} target:{}>'.format(type(self).__name__, self._track, self._track_range, self.subject, self.target_participant_type)

    def get_stat(self, interaction, source=None, target=None):
        source, target = self.find_op_participants(interaction, source, target)
        if source is None or target is None:
            return
        elif isinstance(target, int):
            target_sim_id = target
        else:
            target_sim_id = target.sim_id
        return source.sim_info.relationship_tracker.get_relationship_track(target_sim_id, (self._track), add=True)

    def _apply_to_sim_info(self, source_sim_info, target_sim_id, **kwargs):
        value = source_sim_info.relationship_tracker.get_relationship_score(target_sim_id, self._track)
        if value in self._track_range:
            apply_initial_modifier = not services.relationship_service().has_relationship_track(source_sim_info.sim_id, target_sim_id, self._track)
            (super()._apply_to_sim_info)(source_sim_info, target_sim_id, apply_initial_modifier=apply_initial_modifier, **kwargs)


class RelationshipMultiplierMixin:
    FACTORY_TUNABLES = {'relationship_multiplier': OptionalTunable(description='\n            A multiplier made for relationship operations.\n            ',
                                  tunable=(TunableMultiplier.TunableFactory()))}

    def __init__(self, relationship_multiplier=None, **kwargs):
        (super().__init__)(**kwargs)
        self._relationship_multiplier = relationship_multiplier
        self._relationship_multiplier_value = 1

    def _pre_process_for_source_and_target(self, source_sim_info, target_sim_info):
        if self._relationship_multiplier is not None:
            resolver = DoubleSimResolver(source_sim_info, target_sim_info)
            self._relationship_multiplier_value = self._relationship_multiplier.get_multiplier(resolver)

    def _get_multiplied_value(self, value):
        return value * self._relationship_multiplier_value


class StatisticAddRelationship(RelationshipMultiplierMixin, RelationshipOperation):
    FACTORY_TUNABLES = {'amount':lambda *args, **kwargs: _get_tunable_amount(*args, **kwargs), 
     'add_track_if_not_present':Tunable(description="\n                    When changing the value of a track, add the track if it's not already present.\n                    False means if the track is not already present, the operation is skipped",
       tunable_type=bool,
       default=True)}

    def __init__(self, amount=None, add_track_if_not_present=True, **kwargs):
        (super().__init__)(**kwargs)
        self._amount = amount
        self._add_track_if_not_present = add_track_if_not_present

    def get_value(self, **kwargs):
        return self._get_multiplied_value(self._amount)

    def _apply_relationship_operation(self, relationship_tracker, target_sim_id, **kwargs):
        if not self._add_track_if_not_present:
            actor_sim_id = relationship_tracker._sim_info.sim_id
            if not services.relationship_service().has_relationship_track(actor_sim_id, target_sim_id, self._track):
                return
        (relationship_tracker.add_relationship_score)(target_sim_id, self.get_value(), track=self._track.stat_type, **kwargs)


class RandomSimStatisticAddRelationship(StatisticAddRelationship):
    KNOWN_SIMS = 0
    ALL_SIMS = 1

    @staticmethod
    def _verify_tunable_callback(cls, tunable_name, source, value):
        if value._store_single_result_on_interaction:
            if not value._number_of_random_sims is None:
                if not value._number_of_random_sims == 1:
                    logger.error('RandomSimStatisticAddRelationship is tuned to store result on interaction and is expecting more than one result. {}', source)

    FACTORY_TUNABLES = {'who':TunableVariant(description="\n            Which Sims are valid choices before running tests.\n            If set to known_sims_only then it will only choose between Sims \n            that the subject sim already knows.\n            \n            IF set to all_sims then it will choose between all of the sims, \n            including those that the Sim hasn't met.\n            ",
       locked_args={'known_sims_only':KNOWN_SIMS, 
      'all_sims':ALL_SIMS},
       default='known_sims_only'), 
     'tests_on_random_sim':TunableTestSet(description='\n            Tests that will be run to filer the Sims where we will pick the\n            random sim to apply this statistic change.\n            '), 
     'number_of_random_sims':OptionalTunable(description='\n            If enabled allows you to specify the number of Sims to choose to\n            add the relationship with.\n            ',
       tunable=TunableRange(description='\n                The number of Sims to choose to add relationship with from\n                the list of valid choices.\n                ',
       tunable_type=int,
       minimum=1,
       default=1)), 
     'loot_applied_notification':OptionalTunable(description='\n            If enable the notification will be displayed passing the subject\n            and the random sim as tokens.\n            ',
       tunable=UiDialogNotification.TunableFactory(description='\n                Notification that will be shown when the loot is applied.\n                ')), 
     'create_sim_if_no_results':OptionalTunable(description='\n            If enabled, will result in a new Sim Info being created to meet\n            the conditions of the supplied Sim Template.\n            ',
       tunable=TunableReference(description='\n                A reference to a Sim Filter to use to create a Sim.\n                                \n                This does not guarantee that the created Sim will pass\n                tests_on_random_sim. However the resulting sim will be used as\n                a valid result.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER)),
       class_restrictions=('TunableSimFilter', ))), 
     'store_single_result_on_interaction':OptionalTunable(description='\n            If enabled will place the result into the SavedActor specified on\n            the interaction.\n            \n            This will only work if the value of number_or_random_sims is 1.\n            This will overwrite whatever else is currently set in the\n            SavedActor space chosen.\n            ',
       tunable=TunableEnumEntry(description='\n            \n                ',
       tunable_type=ParticipantTypeSavedActor,
       default=(ParticipantTypeSavedActor.SavedActor1))), 
     'verify_tunable_callback':_verify_tunable_callback}

    def __init__(self, who=None, tests_on_random_sim=None, number_of_random_sims=None, loot_applied_notification=None, create_sim_if_no_results=None, store_single_result_on_interaction=None, **kwargs):
        (super().__init__)(**kwargs)
        self._who = who
        self._tests_on_random_sim = tests_on_random_sim
        self._number_of_random_sims = number_of_random_sims
        self._loot_applied_notification = loot_applied_notification
        self._create_sim_if_no_results = create_sim_if_no_results
        self._store_single_result_on_interaction = store_single_result_on_interaction

    def _apply_to_subject_and_target--- This code section failed: ---

 L.1906         0  LOAD_FAST                'self'
                2  LOAD_METHOD              _get_sim_info_from_participant
                4  LOAD_FAST                'subject'
                6  CALL_METHOD_1         1  '1 positional argument'
                8  STORE_FAST               'source_sim_info'

 L.1907        10  LOAD_FAST                'source_sim_info'
               12  POP_JUMP_IF_TRUE     18  'to 18'

 L.1908        14  LOAD_CONST               None
               16  RETURN_VALUE     
             18_0  COME_FROM            12  '12'

 L.1910        18  BUILD_LIST_0          0 
               20  STORE_FAST               'valid_sim_infos'

 L.1911        22  LOAD_FAST                'self'
               24  LOAD_ATTR                _who
               26  LOAD_FAST                'self'
               28  LOAD_ATTR                KNOWN_SIMS
               30  COMPARE_OP               ==
               32  POP_JUMP_IF_FALSE    92  'to 92'

 L.1912        34  LOAD_FAST                'source_sim_info'
               36  LOAD_ATTR                relationship_tracker
               38  LOAD_METHOD              get_target_sim_infos
               40  CALL_METHOD_0         0  '0 positional arguments'
               42  STORE_FAST               'target_sim_infos'

 L.1913        44  SETUP_LOOP          162  'to 162'
               46  LOAD_FAST                'target_sim_infos'
               48  GET_ITER         
             50_0  COME_FROM            74  '74'
               50  FOR_ITER             88  'to 88'
               52  STORE_FAST               'target_sim_info'

 L.1914        54  LOAD_GLOBAL              DoubleSimResolver
               56  LOAD_FAST                'source_sim_info'
               58  LOAD_FAST                'target_sim_info'
               60  CALL_FUNCTION_2       2  '2 positional arguments'
               62  STORE_FAST               'test_resolver'

 L.1915        64  LOAD_FAST                'self'
               66  LOAD_ATTR                _tests_on_random_sim
               68  LOAD_METHOD              run_tests
               70  LOAD_FAST                'test_resolver'
               72  CALL_METHOD_1         1  '1 positional argument'
               74  POP_JUMP_IF_FALSE    50  'to 50'

 L.1916        76  LOAD_FAST                'valid_sim_infos'
               78  LOAD_METHOD              append
               80  LOAD_FAST                'target_sim_info'
               82  CALL_METHOD_1         1  '1 positional argument'
               84  POP_TOP          
               86  JUMP_BACK            50  'to 50'
               88  POP_BLOCK        
               90  JUMP_FORWARD        162  'to 162'
             92_0  COME_FROM            32  '32'

 L.1917        92  LOAD_FAST                'self'
               94  LOAD_ATTR                _who
               96  LOAD_FAST                'self'
               98  LOAD_ATTR                ALL_SIMS
              100  COMPARE_OP               ==
              102  POP_JUMP_IF_FALSE   162  'to 162'

 L.1918       104  LOAD_GLOBAL              services
              106  LOAD_METHOD              sim_info_manager
              108  CALL_METHOD_0         0  '0 positional arguments'
              110  STORE_FAST               'sim_info_manager'

 L.1919       112  SETUP_LOOP          162  'to 162'
              114  LOAD_FAST                'sim_info_manager'
              116  LOAD_METHOD              values
              118  CALL_METHOD_0         0  '0 positional arguments'
              120  GET_ITER         
            122_0  COME_FROM           146  '146'
              122  FOR_ITER            160  'to 160'
              124  STORE_FAST               'sim_info'

 L.1920       126  LOAD_GLOBAL              DoubleSimResolver
              128  LOAD_FAST                'source_sim_info'
              130  LOAD_FAST                'sim_info'
              132  CALL_FUNCTION_2       2  '2 positional arguments'
              134  STORE_FAST               'test_resolver'

 L.1921       136  LOAD_FAST                'self'
              138  LOAD_ATTR                _tests_on_random_sim
              140  LOAD_METHOD              run_tests
              142  LOAD_FAST                'test_resolver'
              144  CALL_METHOD_1         1  '1 positional argument'
              146  POP_JUMP_IF_FALSE   122  'to 122'

 L.1922       148  LOAD_FAST                'valid_sim_infos'
              150  LOAD_METHOD              append
              152  LOAD_FAST                'sim_info'
              154  CALL_METHOD_1         1  '1 positional argument'
              156  POP_TOP          
              158  JUMP_BACK           122  'to 122'
              160  POP_BLOCK        
            162_0  COME_FROM_LOOP      112  '112'
            162_1  COME_FROM           102  '102'
            162_2  COME_FROM            90  '90'
            162_3  COME_FROM_LOOP       44  '44'

 L.1924       162  LOAD_FAST                'valid_sim_infos'
              164  POP_JUMP_IF_TRUE    204  'to 204'

 L.1925       166  LOAD_FAST                'self'
              168  LOAD_ATTR                _create_sim_if_no_results
              170  POP_JUMP_IF_TRUE    176  'to 176'

 L.1926       172  LOAD_CONST               None
              174  RETURN_VALUE     
            176_0  COME_FROM           170  '170'

 L.1927       176  LOAD_FAST                'self'
              178  LOAD_ATTR                _create_sim_if_no_results
              180  LOAD_METHOD              create_sim_info
              182  LOAD_CONST               0
              184  CALL_METHOD_1         1  '1 positional argument'
              186  STORE_FAST               'result'

 L.1928       188  LOAD_FAST                'result'
              190  POP_JUMP_IF_FALSE   204  'to 204'

 L.1929       192  LOAD_FAST                'valid_sim_infos'
              194  LOAD_METHOD              append
              196  LOAD_FAST                'result'
              198  LOAD_ATTR                sim_info
              200  CALL_METHOD_1         1  '1 positional argument'
              202  POP_TOP          
            204_0  COME_FROM           190  '190'
            204_1  COME_FROM           164  '164'

 L.1931       204  SETUP_LOOP          412  'to 412'
              206  LOAD_GLOBAL              range
              208  LOAD_FAST                'self'
              210  LOAD_ATTR                _number_of_random_sims
              212  JUMP_IF_TRUE_OR_POP   216  'to 216'
              214  LOAD_CONST               1
            216_0  COME_FROM           212  '212'
              216  CALL_FUNCTION_1       1  '1 positional argument'
              218  GET_ITER         
            220_0  COME_FROM           352  '352'
            220_1  COME_FROM           338  '338'
              220  FOR_ITER            410  'to 410'
              222  STORE_FAST               '_'

 L.1932       224  LOAD_FAST                'valid_sim_infos'
              226  POP_JUMP_IF_TRUE    230  'to 230'

 L.1933       228  BREAK_LOOP       
            230_0  COME_FROM           226  '226'

 L.1935       230  LOAD_GLOBAL              random
              232  LOAD_METHOD              choice
              234  LOAD_FAST                'valid_sim_infos'
              236  CALL_METHOD_1         1  '1 positional argument'
              238  STORE_FAST               'target_sim_info'

 L.1936       240  LOAD_FAST                'valid_sim_infos'
              242  LOAD_METHOD              remove
              244  LOAD_FAST                'target_sim_info'
              246  CALL_METHOD_1         1  '1 positional argument'
              248  POP_TOP          

 L.1937       250  LOAD_FAST                'source_sim_info'
              252  LOAD_FAST                'target_sim_info'
              254  COMPARE_OP               is
          256_258  POP_JUMP_IF_FALSE   280  'to 280'

 L.1939       260  LOAD_GLOBAL              random
              262  LOAD_METHOD              choice
              264  LOAD_FAST                'valid_sim_infos'
              266  CALL_METHOD_1         1  '1 positional argument'
              268  STORE_FAST               'target_sim_info'

 L.1940       270  LOAD_FAST                'valid_sim_infos'
              272  LOAD_METHOD              remove
              274  LOAD_FAST                'target_sim_info'
              276  CALL_METHOD_1         1  '1 positional argument'
              278  POP_TOP          
            280_0  COME_FROM           256  '256'

 L.1943       280  LOAD_FAST                'self'
              282  LOAD_METHOD              _apply_to_sim_info
              284  LOAD_FAST                'source_sim_info'
              286  LOAD_FAST                'target_sim_info'
              288  LOAD_ATTR                sim_id
              290  CALL_METHOD_2         2  '2 positional arguments'
              292  POP_TOP          

 L.1945       294  LOAD_FAST                'self'
              296  LOAD_ATTR                _loot_applied_notification
              298  LOAD_CONST               None
              300  COMPARE_OP               is-not
          302_304  POP_JUMP_IF_FALSE   334  'to 334'

 L.1946       306  LOAD_FAST                'self'
              308  LOAD_ATTR                _loot_applied_notification
              310  LOAD_FAST                'source_sim_info'
              312  LOAD_GLOBAL              DoubleSimResolver
              314  LOAD_FAST                'source_sim_info'
              316  LOAD_FAST                'target_sim_info'
              318  CALL_FUNCTION_2       2  '2 positional arguments'
              320  LOAD_CONST               ('resolver',)
              322  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              324  STORE_FAST               'dialog'

 L.1947       326  LOAD_FAST                'dialog'
              328  LOAD_METHOD              show_dialog
              330  CALL_METHOD_0         0  '0 positional arguments'
              332  POP_TOP          
            334_0  COME_FROM           302  '302'

 L.1949       334  LOAD_FAST                'self'
              336  LOAD_ATTR                _store_single_result_on_interaction
              338  POP_JUMP_IF_FALSE   220  'to 220'

 L.1950       340  LOAD_FAST                'resolver'
              342  LOAD_ATTR                interaction
              344  STORE_FAST               'interaction'

 L.1951       346  LOAD_FAST                'interaction'
              348  LOAD_CONST               None
              350  COMPARE_OP               is-not
              352  POP_JUMP_IF_FALSE   220  'to 220'

 L.1952       354  SETUP_LOOP          408  'to 408'
              356  LOAD_GLOBAL              enumerate
              358  LOAD_GLOBAL              list
              360  LOAD_GLOBAL              ParticipantTypeSavedActor
              362  CALL_FUNCTION_1       1  '1 positional argument'
              364  CALL_FUNCTION_1       1  '1 positional argument'
              366  GET_ITER         
            368_0  COME_FROM           384  '384'
              368  FOR_ITER            406  'to 406'
              370  UNPACK_SEQUENCE_2     2 
              372  STORE_FAST               'index'
              374  STORE_FAST               'tag'

 L.1953       376  LOAD_FAST                'tag'
              378  LOAD_FAST                'self'
              380  LOAD_ATTR                _store_single_result_on_interaction
              382  COMPARE_OP               is
          384_386  POP_JUMP_IF_FALSE   368  'to 368'

 L.1954       388  LOAD_FAST                'interaction'
              390  LOAD_METHOD              set_saved_participant
              392  LOAD_FAST                'index'
              394  LOAD_FAST                'target_sim_info'
              396  CALL_METHOD_2         2  '2 positional arguments'
              398  POP_TOP          

 L.1955       400  BREAK_LOOP       
          402_404  JUMP_BACK           368  'to 368'
              406  POP_BLOCK        
            408_0  COME_FROM_LOOP      354  '354'
              408  JUMP_BACK           220  'to 220'
              410  POP_BLOCK        
            412_0  COME_FROM_LOOP      204  '204'

Parse error at or near `LOAD_FAST' instruction at offset 162


class TunableRelationshipTrackSelectionStrategyBase(HasTunableSingletonFactory, AutoFactoryInit):

    def get_tracks(self, relationship_tracker, target_sim_info):
        raise NotImplementedError


class TunableSentimentTrackSelectionByType(TunableRelationshipTrackSelectionStrategyBase):
    FACTORY_TUNABLES = {'sentiment_sign':OptionalTunable(description='\n            If tuned, only sentiments with the tuned sign will be affected.\n            ',
       tunable=TunableEnumEntry(tunable_type=SentimentSignType,
       default=(SentimentSignType.INVALID),
       invalid_enums=(
      SentimentSignType.INVALID,))), 
     'sentiment_duration':OptionalTunable(description='\n            If tuned, only sentiments with the tuned duration will be affected.\n            ',
       tunable=TunableEnumEntry(tunable_type=SentimentDurationType,
       default=(SentimentDurationType.INVALID),
       invalid_enums=(
      SentimentDurationType.INVALID,)))}

    def get_tracks(self, relationship_tracker, target_sim_id):
        sentiment_list = []
        for track in relationship_tracker.relationship_tracks_gen(target_sim_id, track_type=(RelationshipTrackType.SENTIMENT)):
            if self.sentiment_sign is not None:
                if self.sentiment_sign != track.sign:
                    continue
            if self.sentiment_duration is not None:
                if self.sentiment_duration != track.duration:
                    continue
            sentiment_list.append(track)

        return sentiment_list


class StatisticAddRelationshipMultiple(RelationshipMultiplierMixin, RelationshipOperationBase):
    FACTORY_TUNABLES = {'amount':lambda *args, **kwargs: _get_tunable_amount(*args, **kwargs), 
     'track_selection_strategy':TunableVariant(description='\n            The strategy we will use for selecting tracks for this op to\n            operate on.\n            ',
       sentiments_by_type=TunableSentimentTrackSelectionByType.TunableFactory(),
       default='sentiments_by_type')}

    def __init__(self, amount=None, track_selection_strategy=None, **kwargs):
        (super().__init__)(**kwargs)
        self._amount = amount
        self._track_selection_strategy = track_selection_strategy

    def get_value(self, **kwargs):
        return self._get_multiplied_value(self._amount)

    def _apply_relationship_operation(self, relationship_tracker, target_sim_id, **kwargs):
        rel_value = self.get_value()
        for track in self._track_selection_strategy.get_tracks(relationship_tracker, target_sim_id):
            (relationship_tracker.add_relationship_score)(target_sim_id, rel_value, track=track.stat_type, **kwargs)


class StatisticSetRelationship(RelationshipMultiplierMixin, RelationshipOperation):
    FACTORY_TUNABLES = {'value':Tunable(description='\n                The value to set the relationship to.',
       tunable_type=float,
       default=0), 
     'add_track_if_not_present':Tunable(description="\n                When setting the value of a track, add the track if it's not already present.\n                False means if the track is not already present, the operation is skipped",
       tunable_type=bool,
       default=True)}

    def __init__(self, value=None, add_track_if_not_present=True, **kwargs):
        (super().__init__)(**kwargs)
        self._value = value
        self._add_track_if_not_present = add_track_if_not_present

    def get_value(self, **kwargs):
        return self._get_multiplied_value(self._value) - self._track.default_value

    def _apply_relationship_operation(self, relationship_tracker, target_sim_id, **kwargs):
        if not self._add_track_if_not_present:
            actor_sim_id = relationship_tracker._sim_info.sim_id
            if not services.relationship_service().has_relationship_track(actor_sim_id, target_sim_id, self._track):
                return
        (relationship_tracker.set_relationship_score)(target_sim_id,
 self._get_multiplied_value(self._value), track=self._track.stat_type, **kwargs)


class StatisticRemoveRelationshipTrack(RelationshipOperation):

    def __init__(self, **kwargs):
        (super().__init__)(**kwargs)

    def get_value(self, **kwargs):
        return self._track.default_value

    def _apply_relationship_operation(self, relationship_tracker, target_sim_id, **kwargs):
        relationship_tracker.remove_relationship_track(target_sim_id, self._track)


class StatisticSetRelationshipMultiple(RelationshipMultiplierMixin, RelationshipOperationBase):
    FACTORY_TUNABLES = {'value':lambda *args, **kwargs: _get_tunable_amount(*args, **kwargs), 
     'track_selection_strategy':TunableVariant(description='\n            The strategy we will use for selecting tracks for this op to\n            operate on.\n            ',
       sentiments_by_type=TunableSentimentTrackSelectionByType.TunableFactory(),
       default='sentiments_by_type')}

    def __init__(self, value=None, track_selection_strategy=None, **kwargs):
        (super().__init__)(**kwargs)
        self._value = value
        self._track_selection_strategy = track_selection_strategy

    def get_value(self, **kwargs):
        return self._get_multiplied_value(self._value)

    def _apply_relationship_operation(self, relationship_tracker, target_sim_id, **kwargs):
        rel_value = self.get_value()
        for track in self._track_selection_strategy.get_tracks(relationship_tracker, target_sim_id):
            (relationship_tracker.set_relationship_score)(target_sim_id, rel_value, track=track.stat_type, **kwargs)


class StatisticSetRelationshipMax(RelationshipOperation):

    def get_value(self, obj=None, interaction=None, sims=None):
        return self._track.max_value - self._track.default_value

    def _apply_relationship_operation(self, relationship_tracker, target_sim_id, **kwargs):
        relationship_tracker.set_track_to_max(target_sim_id, self._track.stat_type)


class ObjectRelationshipOperation(RelationshipOperationBase):
    FACTORY_TUNABLES = {'track':TunableReference(description='\n            The track to be manipulated.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC),
       class_restrictions='ObjectRelationshipTrack'), 
     'track_range':TunableInterval(description='\n            The relationship track must > lower_bound and <= upper_bound for\n            the operation to apply.',
       tunable_type=float,
       default_lower=-101,
       default_upper=100)}

    def __init__(self, track_range=None, track=DEFAULT, headline_icon_modifier=None, **kwargs):
        (super().__init__)(**kwargs)
        self._track_range = track_range
        self._track = DEFAULT if track is None else track

    def get_stat(self, interaction, source=None, target=None):
        source, target = self.find_op_participants(interaction, source, target)
        if source is None or target is None:
            logger.error('None participant found while applying Object Relationship Operations. Source: {}, Target: {}', source, target)
            return
        obj_tag_set = ObjectRelationshipTrack.OBJECT_BASED_FRIENDSHIP_TRACKS[self._track]
        return services.relationship_service().get_object_relationship_track((source.sim_info.sim_id), obj_tag_set, (target.definition.id), track=(self._track), add=True)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        source_sim_info = self._get_sim_info_from_participant(subject)
        if not source_sim_info:
            return
        self._apply_to_sim_info(source_sim_info, target)

    def _apply_to_sim_info(self, source_sim_info, target, **kwargs):
        obj_tag_set = ObjectRelationshipTrack.OBJECT_BASED_FRIENDSHIP_TRACKS[self._track]
        if not target.has_any_tag(obj_tag_set.tags):
            logger.error('Attempting to add object-type-rel between sim {} and object {} for track {}, but the target object does not have the appropriate tags {}', source_sim_info,
              target, (self._track), (obj_tag_set.tags), owner='shipark')
            return
        track = services.relationship_service().get_object_relationship_track((source_sim_info.sim_id), obj_tag_set,
          target_def_id=(target.definition.id),
          track=(self._track.stat_type),
          add=True)
        if track.get_value() in self._track_range:
            apply_initial_modifier = not services.relationship_service().has_object_relationship_track(source_sim_info.sim_id, obj_tag_set, self._track)
            (super()._apply_to_sim_info)(source_sim_info, target, apply_initial_modifier=apply_initial_modifier, **kwargs)


class StatisticAddObjectRelationship(ObjectRelationshipOperation):
    FACTORY_TUNABLES = {'amount': lambda *args, **kwargs: _get_tunable_amount(*args, **kwargs)}

    def __init__(self, amount=None, **kwargs):
        (super().__init__)(**kwargs)
        self._amount = amount

    def get_value(self, **kwargs):
        return self._amount

    def _apply_relationship_operation(self, relationship_tracker, target, **kwargs):
        actor_sim_id = relationship_tracker._sim_info.sim_id
        services.relationship_service().add_object_relationship_score(actor_sim_id, (ObjectRelationshipTrack.OBJECT_BASED_FRIENDSHIP_TRACKS[self._track]),
          (self._amount),
          track=(self._track.stat_type))

    def _apply(self, tracker, target_sim, **kwargs):
        (tracker.add_value)((self._track), (self._amount), **kwargs)