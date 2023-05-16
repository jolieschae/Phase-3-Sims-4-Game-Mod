# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\payment_liability.py
# Compiled at: 2018-09-21 18:30:55
# Size of source mod 2**32: 576 bytes
from interactions.liability import Liability

class PaymentLiability(Liability):
    LIABILITY_TOKEN = 'PaymentLiability'

    def __init__(self, amount, payment_destinations, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.amount = amount
        self.payment_destinations = payment_destinations