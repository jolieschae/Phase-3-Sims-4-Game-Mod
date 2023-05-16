# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\payment\payment_source.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 10423 bytes
from bucks.bucks_enums import BucksType
from bucks.bucks_utils import BucksUtils
from protocolbuffers import Consts_pb2
from business.business_funds import BusinessFundsCategory
from interactions import ParticipantType
from sims.funds import FundsSource, get_funds_for_source
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import TunableVariant, HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunableReference, Tunable, OptionalTunable
import services, sims4.log
logger = sims4.log.Logger('Payment', default_owner='rmccord')

def get_tunable_payment_source_variant(*args, **kwargs):
    kwargs['household'] = _PaymentSourceHousehold.TunableFactory()
    kwargs['business'] = _PaymentSourceBusiness.TunableFactory()
    kwargs['statistic'] = _PaymentSourceStatistic.TunableFactory()
    kwargs['bucks'] = _PaymentSourceBucks.TunableFactory()
    kwargs['no_source'] = _PaymentSourceNoSource.TunableFactory()
    return TunableVariant(args, default='household', **kwargs)


class _PaymentSource(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'require_full_amount':Tunable(description='\n            If False, the payment element will subtract whatever funds are \n            available if there are not enough funds.\n            ',
       tunable_type=bool,
       default=True), 
     'allow_credits':Tunable(description='\n            If False, the payment element will permit negative payments (credits).\n            ',
       tunable_type=bool,
       default=False), 
     'cost_string_override':OptionalTunable(description='\n            When enabled, override the format for displaying interaction names on interactions that\n            have this payment as a cost. \n            \n            0.String is the interaction name. \n            1 will be the the cost amount.\n            ',
       tunable=TunableLocalizedStringFactory()), 
     'gain_string_override':OptionalTunable(description='\n            When enabled, override the format for displaying interaction names on interactions that\n            have this payment as a gain.\n             \n            0.String is the interaction name. \n            1 will be the the gain amount.\n            ',
       tunable=TunableLocalizedStringFactory())}

    @property
    def funds_source(self):
        raise NotImplementedError

    def try_remove_funds(self, sim, amount, resolver=None, reason=None):
        funds = get_funds_for_source((self.funds_source), sim=sim)
        if amount < 0:
            if self.allow_credits:
                funds.add(-amount, Consts_pb2.TELEMETRY_INTERACTION_REWARD, sim)
                return amount
        return funds.try_remove_amount(amount, Consts_pb2.TELEMETRY_INTERACTION_COST, sim, self.require_full_amount)

    def max_funds(self, sim, resolver=None):
        funds = get_funds_for_source((self.funds_source), sim=sim)
        if funds is not None:
            return funds.money
        return 0

    def get_cost_string(self):
        return self.cost_string_override

    def get_gain_string(self):
        return self.gain_string_override


class _PaymentSourceHousehold(_PaymentSource):

    @property
    def funds_source(self):
        return FundsSource.HOUSEHOLD


class _PaymentSourceBusiness(_PaymentSourceHousehold):
    FACTORY_TUNABLES = {'funds_category': TunableEnumEntry(description='\n            If defined, this expense is categorized and can be displayed in the\n            Retail finance dialog.\n            ',
                         tunable_type=BusinessFundsCategory,
                         default=(BusinessFundsCategory.NONE),
                         invalid_enums=(
                        BusinessFundsCategory.NONE,))}

    @property
    def funds_source(self):
        business_funds = get_funds_for_source((FundsSource.BUSINESS), sim=None)
        if business_funds is None:
            return super().funds_source
        return FundsSource.BUSINESS

    def try_remove_funds(self, sim, amount, resolver=None, reason=None):
        business_funds = get_funds_for_source((FundsSource.BUSINESS), sim=sim)
        if business_funds is None:
            return super().try_remove_funds(sim, amount, resolver=None, reason=reason)
        return business_funds.try_remove_amount(amount, (Consts_pb2.TELEMETRY_INTERACTION_COST), sim, funds_category=(self.funds_category), require_full_amount=(self.require_full_amount))


class _PaymentSourceStatistic(_PaymentSource):
    FACTORY_TUNABLES = {'statistic':TunableReference(description='\n            The statistic that should be used to pay.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC)), 
     'participant':TunableEnumEntry(description='\n            The participant whose statistic should be used to pay\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor)}

    @property
    def funds_source(self):
        return FundsSource.STATISTIC

    def try_remove_funds(self, sim, amount, resolver=None, reason=None):
        if resolver is not None:
            target = resolver.get_participant(self.participant)
            if target is not None:
                tracker = target.get_tracker(self.statistic)
                if tracker is not None:
                    stat = tracker.get_statistic(self.statistic)
                    if stat is None:
                        return
                    current_value = stat.get_value()
                    new_value = current_value - amount
                    if new_value < 0:
                        if self.require_full_amount:
                            return
                        amount = current_value
                        new_value = 0
                    stat.set_value(new_value)
                    return amount

    def max_funds(self, sim, resolver=None):
        if resolver is not None:
            target = resolver.get_participant(self.participant)
            if target is not None:
                tracker = target.get_tracker(self.statistic)
                if tracker is not None:
                    stat = tracker.get_statistic(self.statistic)
                    return stat.get_value()
        return 0


class _PaymentSourceBucks(_PaymentSource):
    FACTORY_TUNABLES = {'bucks_type': TunableEnumEntry(description='\n            The type of Bucks to pay.\n            ',
                     tunable_type=BucksType,
                     default=(BucksType.INVALID),
                     pack_safe=True)}

    @property
    def funds_source(self):
        return FundsSource.BUCKS

    def try_remove_funds(self, sim, amount, resolver=None, reason=None):
        sim_id = None if sim is None else sim.id
        tracker = BucksUtils.get_tracker_for_bucks_type((self.bucks_type), owner_id=sim_id, add_if_none=(amount > 0))
        if tracker is None:
            logger.error('Attempting to make a Bucks payment to {} of amount {} but they have no tracker for that bucks type {}.', sim, amount, self.bucks_type)
            return
        result = tracker.try_modify_bucks((self.bucks_type), (-amount), reason=reason)
        return result

    def get_cost_string(self):
        if self.cost_string_override is not None:
            return self.cost_string_override
        if self.bucks_type in BucksUtils.BUCK_TYPE_TO_DISPLAY_DATA:
            return BucksUtils.BUCK_TYPE_TO_DISPLAY_DATA[self.bucks_type].cost_string

    def get_gain_string(self):
        if self.gain_string_override is not None:
            return self.gain_string_override
        if self.bucks_type in BucksUtils.BUCK_TYPE_TO_DISPLAY_DATA:
            return BucksUtils.BUCK_TYPE_TO_DISPLAY_DATA[self.bucks_type].gain_string

    def max_funds(self, sim, *args):
        sim_id = None if sim is None else sim.id
        tracker = BucksUtils.get_tracker_for_bucks_type(self.bucks_type, sim_id)
        if tracker is None:
            return 0
        return tracker.get_bucks_amount_for_type(self.bucks_type)


class _PaymentSourceNoSource(_PaymentSource):
    FACTORY_TUNABLES = {'locked_args': {'allow_credits':False, 
                     'require_full_amount':False}}

    @property
    def funds_source(self):
        return FundsSource.NO_SOURCE

    def try_remove_funds(self, sim, amount, resolver=None, reason=None):
        return amount

    def max_funds(self, sim, resolver=None):
        return sims4.math.MAX_INT32