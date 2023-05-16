# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relics\relic_loot.py
# Compiled at: 2017-11-03 15:34:38
# Size of source mod 2**32: 1102 bytes
from interactions.utils.loot_basic_op import BaseLootOperation
from relics.relic_tuning import RelicComboId
from sims4.tuning.tunable import TunableEnumEntry

class AddRelicCombo(BaseLootOperation):
    FACTORY_TUNABLES = {'relic_combo_id': TunableEnumEntry(description="\n            The relic combo ID to add to the Sim's Relic Tracker.\n            ",
                         tunable_type=RelicComboId,
                         default=(RelicComboId.INVALID),
                         invalid_enums=(
                        RelicComboId.INVALID,))}

    def __init__(self, *args, relic_combo_id, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._relic_combo_id = relic_combo_id

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None:
            return
        relic_tracker = subject.relic_tracker
        relic_tracker.add_relic_combo(self._relic_combo_id)