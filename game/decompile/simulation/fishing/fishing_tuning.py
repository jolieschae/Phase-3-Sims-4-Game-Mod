# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\fishing\fishing_tuning.py
# Compiled at: 2019-02-20 14:08:48
# Size of source mod 2**32: 3535 bytes
from fishing.fishing_data import TunableFishingBaitReference
from notebook.notebook_entry import SubEntryData
from sims4.tuning.tunable import TunableMapping
from tag import TunableTag
from ui.notebook_tuning import NotebookCustomTypeTuning
import services, sims4.log
logger = sims4.log.Logger('Fishing')

class FishingTuning:
    BAIT_TAG_DATA_MAP = TunableMapping(description='\n        Mapping between fishing bait tag and fishing bait data.\n        ',
      key_type=TunableTag(description='\n            The bait tag to which we want to map a bait data.\n            ',
      filter_prefixes=('func_bait', )),
      key_name='Bait Tag',
      value_type=TunableFishingBaitReference(description='\n            The bait data.\n            ',
      pack_safe=True),
      value_name='Bait Data')

    @staticmethod
    def get_fishing_bait_data(obj_def):
        bait_data = None
        for tag, data in FishingTuning.BAIT_TAG_DATA_MAP.items():
            if not obj_def.has_build_buy_tag(tag) or bait_data is None or bait_data.bait_priority < data.bait_priority:
                bait_data = data

        return bait_data

    @staticmethod
    def get_fishing_bait_data_set(obj_def_ids):
        if obj_def_ids is None:
            return frozenset()
        definition_manager = services.definition_manager()
        bait_data_guids = set()
        for def_id in obj_def_ids:
            bait_def = definition_manager.get(def_id)
            if bait_def is None:
                continue
            bait_data = FishingTuning.get_fishing_bait_data(bait_def)
            if bait_data is None:
                logger.error('Object {} failed trying to get fishing bait data category. Make sure the object has bait category tag.', bait_def)
                continue
            bait_data_guids.add(bait_data.guid64)

        return bait_data_guids

    @staticmethod
    def get_fishing_bait_description(obj):
        bait_data = FishingTuning.get_fishing_bait_data(obj.definition)
        if bait_data is not None:
            return bait_data.bait_description()

    @staticmethod
    def add_bait_notebook_entry(sim, created_fish, bait):
        if sim.sim_info.notebook_tracker is None:
            return
        sub_entries = None
        if bait:
            bait_data = FishingTuning.get_fishing_bait_data(bait.definition)
            if bait_data is not None:
                sub_entries = (
                 SubEntryData(bait_data.guid64, True),)
        sim.sim_info.notebook_tracker.unlock_entry(NotebookCustomTypeTuning.BAIT_NOTEBOOK_ENTRY((created_fish.definition.id), sub_entries=sub_entries))