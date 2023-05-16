# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\tuning\tunable_hash.py
# Compiled at: 2022-10-05 14:14:58
# Size of source mod 2**32: 3301 bytes
from sims4.tuning.tunable_base import Attributes
from sims4.tuning.tunable import Tunable
import sims4.hash_util

class _Hash(int):

    def __new__(cls, value, hashed_value):
        h = int.__new__(cls, hashed_value)
        h.unhash = value
        return h

    def __str__(self):
        return '{} ({:#x})'.format(self.unhash, self)

    def __getnewargs__(self):
        return (
         self.unhash, int(self))


class _TunableStringHash(Tunable):

    def __init__(self, default=None, export_to_binary=False, **kwargs):
        self.export_to_binary = export_to_binary
        (super().__init__)(str, default=default, **kwargs)

    def _convert_to_value(self, content):
        if content is not None:
            hash_fn = self._get_hash_fn()
            return hash_fn(content)

    def _get_hash_fn(self):
        raise NotImplementedError

    @property
    def export_binary_type(self):
        raise NotImplementedError

    def export_desc(self):
        export_dict = super().export_desc()
        if self.export_to_binary:
            export_dict[Attributes.EnumBinaryExportType] = self.export_binary_type
        return export_dict


class TunableStringHash32(_TunableStringHash):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.cache_key = 'TunableStringHash32'

    def _get_hash_fn(self):
        return sims4.hash_util.hash32

    @property
    def export_binary_type(self):
        return 'hashcode32'


class TunableStringHash64(_TunableStringHash):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.cache_key = 'TunableStringHash64'

    def _get_hash_fn(self):
        return sims4.hash_util.hash64

    @property
    def export_binary_type(self):
        return 'hashcode64'