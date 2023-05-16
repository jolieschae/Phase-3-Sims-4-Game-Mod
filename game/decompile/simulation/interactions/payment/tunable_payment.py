# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\payment\tunable_payment.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 3991 bytes
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableVariant
import sims4.log
from interactions.payment.payment_cost import PaymentAmount, PaymentAmountUpTo, PaymentBills, PaymentCatalogValue, PaymentCurrentValue, PaymentBaseRetailValue, PaymentBaseDiningBill, PaymentBusinessAmount, PaymentDialog, PaymentFromLiability, PaymentUtility, PaymentMarketplaceListing, PaymentFashionMarketplaceListing
from interactions.payment.payment_source import get_tunable_payment_source_variant
from snippets import define_snippet
from tunable_multiplier import TunableMultiplier
logger = sims4.log.Logger('Payment', default_owner='rmccord')

class Payment(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'payment_cost':TunableVariant(description='\n            The type of payment, which defines the payment amount.\n            ',
       amount=PaymentAmount.TunableFactory(),
       amount_up_to=PaymentAmountUpTo.TunableFactory(),
       bills=PaymentBills.TunableFactory(),
       catalog_value=PaymentCatalogValue.TunableFactory(),
       current_value=PaymentCurrentValue.TunableFactory(),
       base_retail_value=PaymentBaseRetailValue.TunableFactory(),
       dining_meal_cost=PaymentBaseDiningBill.TunableFactory(),
       business_amount=PaymentBusinessAmount.TunableFactory(),
       input_dialog=PaymentDialog.TunableFactory(),
       liability=PaymentFromLiability.TunableFactory(),
       object_marketplace_listing=PaymentMarketplaceListing.TunableFactory(),
       object_fashion_marketplace_listing=PaymentFashionMarketplaceListing.TunableFactory(),
       utility=PaymentUtility.TunableFactory(),
       default='amount'), 
     'payment_source':get_tunable_payment_source_variant(description='\n            The source of the funds.\n            '), 
     'cost_modifiers':TunableMultiplier.TunableFactory(description='\n            A tunable list of test sets and associated multipliers to apply to\n            the total cost of this payment.\n            ')}

    def get_simoleon_delta(self, resolver, override_amount=None):
        amount, fund_source = self.payment_cost.get_simoleon_delta(resolver, self.payment_source, self.cost_modifiers)
        if self.payment_source.require_full_amount:
            return (
             amount, fund_source)
        return (
         0, fund_source)

    def try_deduct_payment(self, resolver, sim, fail_callback=None):
        success = self.payment_cost.try_deduct_payment(resolver, sim, fail_callback, self.payment_source, self.cost_modifiers)
        if not success:
            if fail_callback:
                fail_callback()
        return success

    def get_cost_string(self):
        return self.payment_source.get_cost_string()

    def get_gain_string(self):
        return self.payment_source.get_gain_string()


TunablePaymentReference, TunablePaymentSnippet = define_snippet('payment', Payment.TunableFactory())