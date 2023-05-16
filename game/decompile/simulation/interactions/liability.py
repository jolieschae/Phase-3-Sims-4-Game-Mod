# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\liability.py
# Compiled at: 2020-08-11 20:32:13
# Size of source mod 2**32: 6670 bytes
from _weakrefset import WeakSet
from interactions.base.interaction_constants import InteractionQueuePreparationStatus

class Liability:

    def release(self):
        pass

    def merge(self, interaction, key, new_liability):
        return new_liability

    def should_transfer(self, continuation):
        return True

    def transfer(self, interaction):
        pass

    def on_reset(self):
        self.release()

    def on_add(self, interaction):
        pass

    def on_run(self):
        pass

    def gsi_text(self):
        return type(self).__name__

    @classmethod
    def on_affordance_loaded_callback(cls, affordance, liability_tuning):
        pass


class ReplaceableLiability(Liability):

    def merge(self, interaction, key, new_liability):
        interaction.remove_liability(key)
        return new_liability


class SharedLiability(Liability):

    def __init__(self, *args, source_liability=None, **kwargs):
        (super().__init__)(**kwargs)
        self._released = False
        if source_liability is None:
            self._shared_liability_refs = WeakSet()
        else:
            self._shared_liability_refs = source_liability._shared_liability_refs
        self._shared_liability_refs.add(self)

    def shared_release(self):
        raise NotImplementedError('SharedLiability: {} trying to release with no shared_release implementation'.format(self))

    def release(self, *args, **kwargs):
        self._released = True
        if all((cur_liability._released for cur_liability in self._shared_liability_refs)):
            (self.shared_release)(*args, **kwargs)

    def create_new_liability(self, interaction, *args, **kwargs):
        return (self.__class__)(args, source_liability=self, **kwargs)


class PreparationLiability(Liability):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._is_prepared = False

    def on_add(self, interaction):
        super().on_add(interaction)
        if interaction.is_super:
            interaction.add_prepare_liability(self)

    def _prepare_gen(self, timeline):
        raise NotImplementedError

    def transfer(self, continuation):
        super().transfer(continuation)
        self._is_prepared = False

    def on_prepare_gen(self, timeline):
        if self._is_prepared:
            return InteractionQueuePreparationStatus.SUCCESS
        result = yield from self._prepare_gen(timeline)
        if result == InteractionQueuePreparationStatus.SUCCESS:
            self._is_prepared = True
        return result
        if False:
            yield None

    def path_generation_deferred(self):
        return False