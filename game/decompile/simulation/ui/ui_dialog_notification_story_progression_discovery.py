# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\ui\ui_dialog_notification_story_progression_discovery.py
# Compiled at: 2022-03-10 20:35:10
# Size of source mod 2**32: 990 bytes
import services
from singletons import DEFAULT
from ui.ui_dialog_notification import UiDialogNotification

class UIDialogNotificationStoryProgressionDiscovery(UiDialogNotification):

    def build_msg(self, additional_tokens=(), icon_override=DEFAULT, event_id=None, career_args=None, **kwargs):
        additional_tokens = list(additional_tokens)
        text_override, tokens = services.get_story_progression_service().get_discovery_string()
        additional_tokens = additional_tokens + tokens
        msg = (super().build_msg)(additional_tokens=tuple(additional_tokens), icon_override=icon_override, event_id=event_id, career_args=career_args, 
         text_override=text_override, **kwargs)
        return msg