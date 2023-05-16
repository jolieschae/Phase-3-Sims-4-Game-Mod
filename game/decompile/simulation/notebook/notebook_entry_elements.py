# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\notebook\notebook_entry_elements.py
# Compiled at: 2021-02-03 13:19:23
# Size of source mod 2**32: 2367 bytes
from interactions.utils.interaction_elements import XevtTriggeredElement
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, OptionalTunable, TunableEnumEntry
from ui.notebook_tuning import NotebookCategories, NotebookSubCategories
import sims4.log
logger = sims4.log.Logger('Notebook')

class NotebookDisplayElement(XevtTriggeredElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'initial_selected_category':OptionalTunable(description='\n            If enabled, this tuned category will be opened/selected initially \n            in the notebook. Otherwise, as default, leftmost category will be \n            selected.\n            ',
       tunable=TunableEnumEntry(description='\n                Initial notebook categories.\n                ',
       tunable_type=NotebookCategories,
       default=(NotebookCategories.INVALID),
       invalid_enums=(
      NotebookCategories.INVALID,),
       pack_safe=True)), 
     'initial_selected_subcategory':OptionalTunable(description='\n            If enabled, this tuned subcategory will be opened/selected initially \n            in the notebook. Otherwise, as default, leftmost subcategory will be \n            selected.\n            ',
       tunable=TunableEnumEntry(description='\n                Initial notebook subcategories.\n                ',
       tunable_type=NotebookSubCategories,
       default=(NotebookSubCategories.INVALID),
       invalid_enums=(
      NotebookSubCategories.INVALID,),
       pack_safe=True))}

    def _do_behavior(self):
        if self.interaction.sim.sim_info.notebook_tracker is None:
            logger.error("Trying to display a notebook on {} but that Sim doesn't have a notebook tracker. LOD issue?", self.interaction.sim)
            return False
        self.interaction.sim.sim_info.notebook_tracker.generate_notebook_information(initial_selected_category=(self.initial_selected_category), initial_selected_subcategory=(self.initial_selected_subcategory))
        return True