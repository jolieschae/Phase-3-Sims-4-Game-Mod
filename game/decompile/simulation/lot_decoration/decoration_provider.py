# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\lot_decoration\decoration_provider.py
# Compiled at: 2018-04-11 21:38:49
# Size of source mod 2**32: 1529 bytes
from lot_decoration.lot_decoration_enums import LOT_DECORATION_DEFAULT_ID
import services
DEFAULT_DECORATION_TYPE = 'DefaultDecorations'

class DefaultDecorationProvider:

    @property
    def decoration_preset(self):
        pass

    @property
    def decoration_type_id(self):
        return LOT_DECORATION_DEFAULT_ID


DEFAULT_DECORATION_PROVIDER = DefaultDecorationProvider()

class HolidayDecorationProvider:

    def __init__(self, holiday_id):
        self._holiday_id = holiday_id

    @property
    def decoration_preset(self):
        return services.holiday_service().get_decoration_preset(self._holiday_id)

    @property
    def decoration_type_id(self):
        return self._holiday_id