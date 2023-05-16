# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\vet\vet_clinic_summary_dialog.py
# Compiled at: 2017-04-11 13:35:05
# Size of source mod 2**32: 1152 bytes
from business.business_summary_dialog import BusinessSummaryDialog
import sims4
logger = sims4.log.Logger('Business', default_owner='jdimailig')

class VetClinicSummaryDialog(BusinessSummaryDialog):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._advertising_cost = 0
        self._employee_wages = 0

    def _calculated_profit(self):
        return self._business_manager.daily_revenue - self._employee_wages - self._advertising_cost

    def _add_line_entries(self):
        self._add_daily_revenue_line_entry()
        self._add_employee_wages_line_entry()
        self._add_advertising_costs()
        self._employee_wages = self._business_manager.get_total_employee_wages()
        self._advertising_cost = self._business_manager.get_current_advertising_cost()