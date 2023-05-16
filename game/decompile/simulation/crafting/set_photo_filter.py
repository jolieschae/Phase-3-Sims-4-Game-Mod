# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\set_photo_filter.py
# Compiled at: 2019-05-09 13:42:28
# Size of source mod 2**32: 1682 bytes
from crafting.photography_enums import PhotoStyleType
from interactions import ParticipantTypeSingle, ParticipantType
from interactions.utils.interaction_elements import XevtTriggeredElement
from sims4.tuning.tunable import TunableEnumEntry
import sims4
logger = sims4.log.Logger('Photography', default_owner='rrodgers')

class SetPhotoFilter(XevtTriggeredElement):
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            The participant object that is the photo.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantType.Object), 
     'photo_filter':TunableEnumEntry(description='\n            The photo filter that you want this photo to use.\n            ',
       tunable_type=PhotoStyleType,
       default=PhotoStyleType.NORMAL)}

    def _do_behavior(self):
        photo_obj = self.interaction.get_participant(self.participant)
        if photo_obj is None:
            logger.error('set_photo_filter basic extra tuned participant does not exist.')
            return False
        canvas_component = photo_obj.canvas_component
        if canvas_component is None:
            logger.error('set_photo_filter basic extra tuned participant does not have a canvas component.')
            return False
        canvas_component.painting_effect = self.photo_filter
        return True