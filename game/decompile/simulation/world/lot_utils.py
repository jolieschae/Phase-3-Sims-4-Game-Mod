# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\lot_utils.py
# Compiled at: 2020-04-27 18:18:49
# Size of source mod 2**32: 1829 bytes
import services
from audio.primitive import play_tunable_audio
from world.travel_tuning import TravelTuning
from world.lot_tuning import LotTuningMaps

def play_lot_entry_audio_sting():
    if services.narrative_service().should_suppress_travel_sting():
        return
        lot_tuning = LotTuningMaps.get_lot_tuning()
        lot_tuning_audio_sting = None
        if services.sim_info_manager().has_any_traveled_sims:
            if lot_tuning is not None:
                lot_tuning_audio_sting = lot_tuning.travel_audio_sting or lot_tuning.audio_sting
            tunable_audio_sting = lot_tuning_audio_sting or TravelTuning.TRAVEL_SUCCESS_AUDIO_STING
    elif lot_tuning is not None and lot_tuning.audio_sting is not None:
        tunable_audio_sting = lot_tuning.audio_sting
    else:
        tunable_audio_sting = TravelTuning.NEW_GAME_AUDIO_STING
    play_tunable_audio(tunable_audio_sting)