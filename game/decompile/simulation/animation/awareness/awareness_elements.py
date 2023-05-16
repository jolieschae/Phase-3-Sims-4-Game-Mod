# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\awareness\awareness_elements.py
# Compiled at: 2016-06-06 14:26:43
# Size of source mod 2**32: 1163 bytes
from element_utils import build_critical_section_with_finally
from animation.awareness.awareness_enums import AwarenessChannel
from animation.awareness.awareness_tuning import AwarenessSourceRequest

def with_audio_awareness(*actors, sequence=()):
    awareness_modifiers = []

    def begin(_):
        for actor in actors:
            if actor is None:
                continue
            if actor.is_sim:
                continue
            awareness_modifier = AwarenessSourceRequest(actor, awareness_sources={AwarenessChannel.AUDIO_VOLUME: 1})
            awareness_modifier.start()
            awareness_modifiers.append(awareness_modifier)

    def end(_):
        for awareness_modifier in awareness_modifiers:
            awareness_modifier.stop()

    return build_critical_section_with_finally(begin, sequence, end)