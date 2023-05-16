# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\apartments\apartment_picker_interaction.py
# Compiled at: 2016-08-23 15:17:47
# Size of source mod 2**32: 7354 bytes
from event_testing.results import TestResult
from interactions import ParticipantType
from interactions.base.picker_interaction import PickerSuperInteraction
from interactions.base.picker_strategy import LotPickerEnumerationStrategy
from interactions.context import QueueInsertStrategy
from interactions.utils.tunable import TunableContinuation
from objects.terrain import TerrainInteractionMixin, TravelMixin
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
from singletons import DEFAULT
from ui.ui_dialog import PhoneRingType
from ui.ui_dialog_picker import UiApartmentPicker, LotPickerRow
import services, sims4.log
logger = sims4.log.Logger('ApartmentPicker', default_owner='rmccord')

class ApartmentPickerInteraction(TravelMixin, TerrainInteractionMixin, PickerSuperInteraction):
    INSTANCE_TUNABLES = {'picker_dialog':UiApartmentPicker.TunableFactory(description='\n            The apartment picker dialog.\n            ',
       tuning_group=GroupNames.PICKERTUNING,
       locked_args={'text_cancel':None, 
      'text_ok':None, 
      'title':None, 
      'text':None, 
      'text_tokens':DEFAULT, 
      'icon':None, 
      'secondary_icon':None, 
      'phone_ring_type':PhoneRingType.NO_RING}), 
     'actor_continuation':TunableContinuation(description='\n            If specified, a continuation to push on the actor when a picker \n            selection has been made.\n            ',
       locked_args={'actor': ParticipantType.Actor},
       tuning_group=GroupNames.PICKERTUNING), 
     'target_continuation':TunableContinuation(description='\n            If specified, a continuation to push on the sim targeted\n            ',
       tuning_group=GroupNames.PICKERTUNING)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, choice_enumeration_strategy=LotPickerEnumerationStrategy(), **kwargs)

    @classmethod
    def _test(cls, target, context, **kwargs):
        to_zone_id = context.pick.get_zone_id_from_pick_location()
        if not services.get_plex_service().is_zone_an_apartment(to_zone_id, consider_penthouse_an_apartment=False):
            return TestResult(False, 'Picked zone is not a plex.')
        return (cls.travel_pick_info_test)(target, context, **kwargs)

    @classmethod
    def has_valid_choice(cls, target, context, **kwargs):
        if cls._get_valid_lot_choices(target, context):
            return True
        return False

    def _push_continuations(self, zone_datas):
        picked_zone_set = {zone_data.zone_id for zone_data in zone_datas if zone_data is not None}
        self.interaction_parameters['picked_zone_ids'] = frozenset(picked_zone_set)
        insert_strategy = QueueInsertStrategy.LAST if not self.target_continuation else QueueInsertStrategy.NEXT
        if self.actor_continuation:
            self.push_tunable_continuation((self.actor_continuation), insert_strategy=insert_strategy, picked_zone_ids=picked_zone_set)
        if self.target_continuation:
            self.push_tunable_continuation((self.target_continuation), insert_strategy=insert_strategy, actor=(self.target), picked_zone_ids=picked_zone_set)

    def _create_dialog(self, owner, target_sim=None, target=None, **kwargs):
        traveling_sims = []
        picked_sims = self.get_participants(ParticipantType.PickedSim)
        if picked_sims:
            traveling_sims = list(picked_sims)
        else:
            if target is not None:
                if target.is_sim:
                    if target is not self.sim:
                        traveling_sims.append(target)
        dialog = self.picker_dialog(owner, title=(lambda *_, **__: self.get_name()), resolver=(self.get_resolver()), traveling_sims=traveling_sims)
        (self._setup_dialog)(dialog, **kwargs)
        dialog.set_target_sim(target_sim)
        dialog.set_target(target)
        dialog.add_listener(self._on_picker_selected)
        return dialog

    def _run_interaction_gen(self, timeline):
        self._show_picker_dialog((self.sim), target_sim=None, target=(self.target))
        return True
        if False:
            yield None

    @flexmethod
    def create_row(cls, inst, tag):
        return LotPickerRow(zone_data=tag, option_id=(tag.zone_id), tag=tag)

    @flexmethod
    def _get_valid_lot_choices(cls, inst, target, context, target_list=None):
        to_zone_id = context.pick.get_zone_id_from_pick_location()
        if to_zone_id is None:
            logger.error('Could not resolve lot id: {} into a valid zone id when traveling to an apartment lot.', (context.pick.lot_id), owner='rmccord')
            return []
        else:
            plex_service = services.get_plex_service()
            return plex_service.is_zone_a_plex(to_zone_id) or []
        valid_zone_ids = plex_service.get_plex_zones_in_group(to_zone_id)
        persistence_service = services.get_persistence_service()
        results = list((persistence_service.get_zone_proto_buff(zone_id) for zone_id in valid_zone_ids))
        return results

    @flexmethod
    def picker_rows_gen(cls, inst, target, context, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        for zone_data in inst_or_cls._get_valid_lot_choices(target, context):
            logger.info('ApartmentPicker: add zone_data:{}', zone_data)
            yield LotPickerRow(zone_data=zone_data, option_id=(zone_data.zone_id), tag=zone_data)

    def _on_picker_selected(self, dialog):
        results = dialog.get_result_tags()
        if results:
            self._push_continuations(results)

    def on_choice_selected(self, choice_tag, **kwargs):
        result = choice_tag
        if result is not None:
            self._push_continuations((result,))