# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\conditional_animation.py
# Compiled at: 2019-09-23 13:34:26
# Size of source mod 2**32: 1984 bytes
from animation.animation_utils import flush_all_animations
from element_utils import maybe, build_critical_section

def conditional_animation(interaction, value, xevt_id, animation, **kwargs):
    target = interaction.target
    did_set = False
    kill_handler = False

    def check_fn():
        current_state = target.get_state(value.state)
        return current_state is not value

    def set_fn(_):
        nonlocal did_set
        if did_set:
            return
        (target.set_state)((value.state), value, **kwargs)
        did_set = True

    if animation is None:
        return maybe(check_fn, set_fn)

    def set_handler(*_, **__):
        if kill_handler:
            return
        set_fn(None)

    def cleanup_asm(asm):
        nonlocal kill_handler
        if xevt_id is not None:
            kill_handler = True

    def reg_xevt(*_, **__):
        if xevt_id is not None:
            interaction.store_event_handler(set_handler, xevt_id)

    return maybe(check_fn, build_critical_section(reg_xevt, build_critical_section(animation(interaction, cleanup_asm=cleanup_asm), flush_all_animations, set_fn)))