# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\career_mixins.py
# Compiled at: 2019-10-15 19:55:43
# Size of source mod 2**32: 972 bytes
from sims4.utils import flexmethod

class CareerKnowledgeMixin:

    @flexmethod
    def show_knowledge_notification(cls, inst, sim_info, resolver):
        inst_or_cls = inst if inst is not None else cls
        if inst_or_cls.current_track_tuning.knowledge_notification:
            notification = inst_or_cls.current_track_tuning.knowledge_notification(sim_info, resolver=resolver)
            notification.show_dialog(additional_tokens=(inst_or_cls.get_career_text_tokens()))