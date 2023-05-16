# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\lot_decoration\lot_decoration_elements.py
# Compiled at: 2018-04-10 14:59:13
# Size of source mod 2**32: 4357 bytes
from interactions import ParticipantType
from interactions.utils.interaction_elements import XevtTriggeredElement
from lot_decoration import decorations_logger
from lot_decoration.lot_decoration_enums import DecorationLocation
from lot_decoration.lot_decoration_mixins import HolidayOrEverydayDecorationMixin
from sims4.resources import Types
from sims4.tuning.tunable import TunableEnumSet, AutoFactoryInit, HasTunableFactory, TunableVariant
import services

class _DecorateBehaviorBase(HasTunableFactory, AutoFactoryInit):

    def __init__(self, lot_decoration_service, interaction, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._interaction = interaction
        self._decoration_service = lot_decoration_service


class _ApplyDecorationAtLocationsBase(HolidayOrEverydayDecorationMixin, _DecorateBehaviorBase):
    FACTORY_TUNABLES = {'_locations_to_decorate': TunableEnumSet(enum_type=DecorationLocation)}


class _ApplyDecoration(_ApplyDecorationAtLocationsBase):

    def perform(self):
        decorations_manager = services.get_instance_manager(Types.LOT_DECORATION)
        guid = self._interaction.get_participant(ParticipantType.PickedItemId)
        decoration = decorations_manager.get(guid)
        if decoration is None:
            decorations_logger.error('Referencing unknown decoration guid {}', guid)
        else:
            for location in self._locations_to_decorate:
                if location not in decoration.available_locations:
                    continue
                self._decoration_service.apply_decoration_for_holiday(decoration, location, self.occasion())


class _RemoveDecoration(_ApplyDecorationAtLocationsBase):

    def perform(self):
        for location in self._locations_to_decorate:
            self._decoration_service.remove_decoration_for_holiday(location, self.occasion())


class _ResetDecorations(HolidayOrEverydayDecorationMixin, _DecorateBehaviorBase):

    def perform(self):
        self._decoration_service.reset_decoration_to_holiday_default(self.occasion())


class _PutUpDecorations(HolidayOrEverydayDecorationMixin, _DecorateBehaviorBase):

    def perform(self):
        self._decoration_service.decorate_zone_for_holiday(services.current_zone_id(), self.occasion())


class _TakeDownDecorations(_DecorateBehaviorBase):

    def perform(self):
        self._decoration_service.decorate_zone_for_holiday(services.current_zone_id(), None)


class LotDecorationElement(XevtTriggeredElement):
    FACTORY_TUNABLES = {'behavior': TunableVariant(description='\n            The function to perform for this element.\n            ',
                   apply_decoration=(_ApplyDecoration.TunableFactory()),
                   remove_decoration=(_RemoveDecoration.TunableFactory()),
                   reset_decorations=(_ResetDecorations.TunableFactory()),
                   put_up_decorations=(_PutUpDecorations.TunableFactory()),
                   take_down_decorations=(_TakeDownDecorations.TunableFactory()),
                   default='apply_decoration')}

    def _do_behavior(self):
        lot_decoration_service = services.lot_decoration_service()
        if lot_decoration_service is None:
            return
        self.behavior(lot_decoration_service, self.interaction).perform()