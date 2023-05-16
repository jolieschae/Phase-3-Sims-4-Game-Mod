# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\photography_interactions.py
# Compiled at: 2021-04-28 18:05:03
# Size of source mod 2**32: 14451 bytes
import sims4, build_buy
from distributor.shared_messages import IconInfoData
from interactions.base.picker_interaction import PickerSuperInteraction
from sims4.tuning.tunable import TunableList, TunableVariant, TunableReference, HasTunableSingletonFactory, AutoFactoryInit, OptionalTunable, Tunable, TunableEnumEntry
from sims4.utils import flexmethod
from sims4.tuning.tunable_base import GroupNames
from ui.ui_dialog_picker import ObjectPickerRow, ObjectPickerType, ObjectPickerStyle
import services
logger = sims4.log.Logger('Photo Interactions', default_owner='shipark')
INT_DECORATOR_CELL_STYLES = (
 ObjectPickerStyle.NUMBERED, ObjectPickerStyle.DELETE)

class PhotoPickerSuperInteraction(PickerSuperInteraction):

    class _GigSource(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'career_reference':TunableReference(description='                \n                A reference to the gig-career that provides the stored photos.\n                ',
           manager=services.get_instance_manager(sims4.resources.Types.CAREER)), 
         'before_or_after_photos':OptionalTunable(description='\n                If enabled, filter the photos stored on the gig by the\n                before/after value on the Photos.\n                \n                If disabled, then the gig will return all the photos\n                from the Gig, regardless of before/after value.\n                ',
           enabled_by_default=False,
           disabled_name='disabled',
           enabled_name='enabled',
           tunable=Tunable(description='\n                    If True, use the before photos stored on the Gig. If False,\n                    use the after photos stored on the Gig.\n                    ',
           default=True,
           tunable_type=bool))}

        def _get_career(self, sim_info):
            career = sim_info.career_tracker.get_career_by_uid(self.career_reference.guid64)
            if career is None:
                logger.error('Tried to get photos from missing career {} on sim {}', self.career_reference, sim_info)
                return
            return career

        def _photo_source_rows_gen(self, context, photo_cell_style, gig_source_histories):
            sim_info = context.sim.sim_info
            career = self._get_career(sim_info)
            if career is None:
                logger.error('Career is None, failed to get photos. {}', career)
                return
            gig_photos, gig_photos_low_res = self._get_career_photos(sim_info.career_tracker, career, gig_source_histories)
            if gig_photos is None:
                return
            for icon_resource in gig_photos_low_res:
                yield ObjectPickerRow(icon_info=IconInfoData(icon_resource=icon_resource), object_picker_style=photo_cell_style)

        def _get_career_photos(self, career_tracker, career, gig_source_histories):
            raise NotImplementedError

        def get_gig_history_subject(self, career_tracker, career):
            return []

    class _PhotoSourceActiveGig(_GigSource):

        def _get_career_photos(self, career_tracker, career, gig_source_histories):
            current_gig = career.get_current_gig()
            if current_gig is None:
                logger.error('No active gig for career {}', career)
                return (None, None)
            else:
                gig_key = current_gig.get_gig_history_key()
                if gig_key is None:
                    logger.error('No valid gig history key for active gig in career {}', career)
                    return (None, None)
                    gig_history = career_tracker.get_gig_history_by_key(gig_key)
                    if gig_history is None:
                        logger.error('No gig history found for active gig in career {}', career)
                        return (None, None)
                    career_photos = []
                    career_photos_low_res = []
                    if self.before_or_after_photos:
                        career_photos.extend(gig_history.before_photos)
                else:
                    career_photos.extend(gig_history.after_photos)
            for hi_res_photo in career_photos:
                career_photos_low_res.append(gig_history.hi_low_res_dict.get(hi_res_photo.instance, hi_res_photo))

            if gig_source_histories is not None:
                gig_source_histories[gig_key] = [career_photo.instance for career_photo in career_photos]
            return (
             career_photos, career_photos_low_res)

        def get_gig_history_subject(self, career_tracker, career):
            current_gig = career.get_current_gig()
            if current_gig is None:
                logger.error('No active gig for career {}', career)
                return
            gig_history_key = current_gig.get_gig_history_key()
            if gig_history_key is None:
                logger.error('No gig history key found for active gig in career {}', career)
                return
            gig_history = career_tracker.get_gig_history_by_key(gig_history_key)
            return [(gig_history_key, gig_history)]

    class _PhotoSourceGigHistory(_GigSource):

        def _get_career_photos(self, career_tracker, career, gig_source_histories):
            gig_history_items = career_tracker.gig_history.items()
            photos = []
            photos_low_res = []
            if self.before_or_after_photos:
                for gig_key, gig_history in gig_history_items:
                    if gig_source_histories is not None:
                        gig_source_histories[gig_key] = [before_photo.instance for before_photo in gig_history.before_photos]
                    photos.extend(gig_history.before_photos)
                    for hi_res_photo in gig_history.before_photos:
                        photos_low_res.append(gig_history.hi_low_res_dict.get(hi_res_photo.instance, hi_res_photo))

            else:
                for gig_key, gig_history in gig_history_items:
                    if gig_source_histories is not None:
                        gig_source_histories[gig_key] = [after_photo.instance for after_photo in gig_history.after_photos]
                    photos.extend(gig_history.after_photos)
                    for hi_res_photo in gig_history.after_photos:
                        photos_low_res.append(gig_history.hi_low_res_dict.get(hi_res_photo.instance, hi_res_photo))

            return (
             photos, photos_low_res)

        def get_gig_history_subject(self, career_tracker, _):
            return career_tracker.gig_history.items()

    INSTANCE_TUNABLES = {'photo_source':TunableVariant(description='\n            Set the source of the photos in the picker.\n            ',
       tunable=TunableVariant(active_gig=(_PhotoSourceActiveGig.TunableFactory()),
       gig_history=(_PhotoSourceGigHistory.TunableFactory()),
       default='active_gig'),
       tuning_group=GroupNames.PICKERTUNING), 
     'photo_cell_style':TunableEnumEntry(description='\n            Set the style for the photo cell.\n            ',
       tunable_type=ObjectPickerStyle,
       default=ObjectPickerStyle.NUMBERED,
       tuning_group=GroupNames.PICKERTUNING)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.picker_type = ObjectPickerType.PHOTO

    def _run_interaction_gen(self, timeline):
        self._show_picker_dialog((self.sim), target_sim=(self.sim))
        return True
        if False:
            yield None

    @flexmethod
    def picker_rows_gen(cls, inst, target, context, **kwargs):
        inst_or_cls = cls if inst is None else inst
        yield from inst_or_cls.photo_source._photo_source_rows_gen(context, inst_or_cls.photo_cell_style)
        if False:
            yield None


class InteriorDecoratorPhotoPicker(PhotoPickerSuperInteraction):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.gig_source_histories = {}

    @flexmethod
    def picker_rows_gen(cls, inst, target, context, **kwargs):
        inst_or_cls = cls if inst is None else inst
        yield from inst_or_cls.photo_source._photo_source_rows_gen(context, inst_or_cls.photo_cell_style, None if inst is None else inst.gig_source_histories)
        if False:
            yield None

    @classmethod
    def _verify_tuning_callback(cls):
        if cls.photo_cell_style not in INT_DECORATOR_CELL_STYLES:
            logger.error('Photo Cell Style {} is not supported by Interior Decorator Photo Picker.', cls.photo_cell_style)
        if not isinstance(cls.photo_source, PhotoPickerSuperInteraction._GigSource):
            logger.error('Photo Source {} is not supported by Interior Decorator Photo Picker.', cls.photo_source)

    def _on_picker_selected(self, dialog):
        select_photos = True if self.photo_cell_style == ObjectPickerStyle.NUMBERED else False
        self._handle_decorator_outcome(dialog, select_photos)

    def _handle_decorator_outcome(self, dialog, select_photos):
        sim_info = services.active_sim_info()
        career = self.photo_source._get_career(sim_info)
        career_photos, _ = self.photo_source._get_career_photos(sim_info.career_tracker, career, self.gig_source_histories)
        if career_photos is None:
            logger.error('Error retrieving the career photos on picker selection.')
            return
        else:
            gig_histories = self.photo_source.get_gig_history_subject(sim_info.career_tracker, career)
            if select_photos:
                self._update_selection_photos(dialog, gig_histories, career_photos)
            else:
                self._update_deletion_photos(dialog, gig_histories, career_photos)

    def _update_selection_photos(self, dialog, gig_histories, career_photos):
        if len(dialog.control_ids) == 0:
            logger.error("The dialog {}'s control-ids is empty. Photo selection failed Verify that SELECTION SEQEUENCE                            is tuned under the Control Id Type field of the Picker .", dialog)
            return
        picked_photo_map = {}
        for picked_result in dialog.picked_results:
            picked_photo = career_photos[picked_result]
            picked_photo_map[picked_photo.instance] = (dialog.control_ids[picked_result], picked_photo)

        for gig_key, gig_history in gig_histories:
            photo_instances = self.gig_source_histories.get(gig_key, None)
            if photo_instances is None:
                logger.error('Photo Picker is retrieving an invalid gig from the photo source; selection fails.')
                return
            for photo_instance in photo_instances:
                picked_photo_data = picked_photo_map.get(photo_instance, None)
                if picked_photo_data is None:
                    continue
                gig_history.update_selected_photos(picked_photo_data, self.photo_source.before_or_after_photos)

    def _update_deletion_photos(self, dialog, gig_histories, career_photos):
        picked_photo_map = {}
        for picked_result in dialog.picked_results:
            picked_photo = career_photos[picked_result]
            picked_photo_map[picked_photo.instance] = picked_photo

        for gig_key, gig_history in gig_histories:
            photo_instances = self.gig_source_histories.get(gig_key, None)
            if photo_instances is None:
                logger.error('Photo Picker is retrieving an invalid gig from the photo source; deletion fails.')
                return
            for photo_instance in photo_instances:
                picked_photo = picked_photo_map.get(photo_instance, None)
                if picked_photo is None:
                    continue
                gig_history.update_deleted_photos(picked_photo)