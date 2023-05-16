# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\change_painting_state.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 6431 bytes
from objects import PaintingState, PuzzleState
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableVariant, TunableTuple, TunableResourceKey, OptionalTunable, TunableRange, Tunable, TunableFactory
import sims4.resources

class _DontUsePaintingTextureField(TunableFactory):

    @staticmethod
    def factory(setter_function):
        return setter_function(None)

    FACTORY_TYPE = factory


class _ClearTexture(TunableFactory):

    @staticmethod
    def factory(setter_function):
        return setter_function(0)

    FACTORY_TYPE = factory


class _SetTexture(TunableFactory):

    @staticmethod
    def factory(setter_function, texture_key=None):
        return setter_function(texture_key.instance)

    FACTORY_TYPE = factory

    def __init__(self, *args, **kwargs):
        (super().__init__)(texture_key=TunableResourceKey(description='\n                The resource key that we want to switch the painting state to.\n                ',
                        resource_types=[
                       sims4.resources.Types.TGA],
                        default=None), **kwargs)


class ChangePaintingState(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'texture_id':TunableVariant(description='\n            Modify the texture id in some way.\n            ',
       set_texture=_SetTexture(),
       clear_texture=_ClearTexture()), 
     'reveal_level':OptionalTunable(description='\n            If enabled then we will change the reveal level of the painting\n            state.\n            ',
       tunable=TunableRange(description='\n                The reveal level that we will change the painting state to.\n                ',
       tunable_type=int,
       default=(PaintingState.REVEAL_LEVEL_MIN),
       minimum=(PaintingState.REVEAL_LEVEL_MIN),
       maximum=(PuzzleState.REVEAL_LEVEL_MAX))), 
     'state_texture_id':TunableVariant(description='\n            Change the state texture id in some way.  This is the\n            texture that will be revealed when being revealed as a mural.\n            ',
       set_texture=_SetTexture(),
       clear_texture=_ClearTexture(),
       dont_use=_DontUsePaintingTextureField()), 
     'overlay_texture_id':TunableVariant(description='\n            Change the overlay texture id in some way.  This is the\n            texture that we want to use as the overlay on this picture\n            ',
       set_texture=_SetTexture(),
       clear_texture=_ClearTexture(),
       dont_use=_DontUsePaintingTextureField()), 
     'reveal_texture_id':TunableVariant(description='\n            Change the reveal texture id in some way.  This is the\n            texture that we will use as a map to reveal the painting/puzzle being\n            created.\n            ',
       set_texture=_SetTexture(),
       clear_texture=_ClearTexture(),
       dont_use=_DontUsePaintingTextureField()), 
     'use_for_puzzle':OptionalTunable(description='\n            Treat this state change as one for puzzles.\n            ',
       enabled_name='reveal_texture_id_B',
       tunable=TunableVariant(description='\n                Change the secondary reveal texture id in some way.  This is the\n                texture that we will use as a map to reveal the puzzle being\n                created.\n                ',
       set_texture=(_SetTexture()),
       clear_texture=(_ClearTexture()),
       dont_use=(_DontUsePaintingTextureField())))}

    def __init__(self, target, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.target = target

    def start(self, *_, **__):
        painting_state = self.target.canvas_component.painting_state
        if painting_state is None:
            if self.use_for_puzzle is not None:
                painting_state = PuzzleState(0)
            else:
                painting_state = PaintingState(0)
        if self.texture_id is not None:
            painting_state = self.texture_id(painting_state.set_texture_id)
        if self.reveal_level is not None:
            painting_state = painting_state.get_at_level(self.reveal_level)
        if self.state_texture_id is not None:
            painting_state = self.state_texture_id(painting_state.set_stage_texture_id)
        if self.overlay_texture_id is not None:
            painting_state = self.overlay_texture_id(painting_state.set_overlay_texture_id)
        if self.reveal_texture_id is not None:
            painting_state = self.reveal_texture_id(painting_state.set_reveal_texture_id)
        if self.use_for_puzzle is not None:
            painting_state = self.use_for_puzzle(painting_state.set_reveal_texture_id_b)
        self.target.canvas_component.painting_state = painting_state

    def stop(self, *_, **__):
        pass