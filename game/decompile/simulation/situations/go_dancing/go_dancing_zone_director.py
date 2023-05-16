# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\go_dancing\go_dancing_zone_director.py
# Compiled at: 2017-01-23 16:56:42
# Size of source mod 2**32: 2136 bytes
from situations.situation import Situation
from venues.scheduling_zone_director import SchedulingZoneDirector
import services

class GoDancingZoneDirector(SchedulingZoneDirector):
    INSTANCE_TUNABLES = {'go_dancing_background_situation': Situation.TunableReference(description='\n            The situation that is always runnning at the Cafe to make sure any\n            Sims that show up beyond the schedule tuning will get coffee. These\n            could be Sims the player invites, the player themselves, and clique\n            Sims. \n            \n            Note, the situation that this points to will be a very\n            generic situation that spins up a CafeGenericSimSituation for that\n            individual Sim. This is so that Sims can get coffee on their own\n            autonomy and be independent of one another.\n            ',
                                          class_restrictions=('GoDancingBackgroundSituation', ))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._background_situation_id = None

    def create_situations_during_zone_spin_up(self):
        super().create_situations_during_zone_spin_up()
        situation_manager = services.get_zone_situation_manager()
        for situation in situation_manager:
            if type(situation) is self.go_dancing_background_situation:
                self._background_situation_id = situation.id
                break
        else:
            self._background_situation_id = situation_manager.create_situation((self.go_dancing_background_situation), user_facing=False,
              creation_source=(self.instance_name))