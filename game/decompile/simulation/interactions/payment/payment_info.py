# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\payment\payment_info.py
# Compiled at: 2016-06-09 17:53:47
# Size of source mod 2**32: 858 bytes
import enum

class PaymentInfo:

    def __init__(self, amount, resolver):
        self.amount = amount
        self.resolver = resolver


class BusinessPaymentInfo(PaymentInfo):

    def __init__(self, *args, revenue_type, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.revenue_type = revenue_type


class PaymentBusinessRevenueType(enum.Int):
    ITEM_SOLD = 0
    SEED_MONEY = 1