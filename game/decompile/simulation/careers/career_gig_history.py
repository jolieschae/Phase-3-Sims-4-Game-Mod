# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\career_gig_history.py
# Compiled at: 2021-05-10 14:30:23
# Size of source mod 2**32: 11085 bytes
from careers.career_enums import DecoratorGigLotType, GigResult
from sims4 import commands
import services, sims4.resources
logger = sims4.log.Logger('GigHistory', default_owner='mars')

class GigHistory:
    __slots__ = ('_customer_id', '_lot_id', '_gig_id', '_career_id', '_gig_result',
                 '_gig_score', '_customer_name', '_project_title', '_gig_lot_type',
                 '_after_photos', '_before_photos', '_hi_low_res_dict', '_selected_photos',
                 '_deletion_photos')

    def __init__(self, *, customer_id, lot_id, gig_id, career_id, gig_result, customer_name, lot_type, project_title, gig_score=0):
        self._customer_id = customer_id
        self._lot_id = lot_id
        self._gig_id = gig_id
        self._career_id = career_id
        self._gig_result = gig_result
        self._gig_score = gig_score
        self._customer_name = customer_name
        self._project_title = project_title
        self._gig_lot_type = lot_type
        self._after_photos = []
        self._before_photos = []
        self._hi_low_res_dict = {}
        self._selected_photos = {}
        self._deletion_photos = []

    @property
    def customer_id(self):
        return self._customer_id

    @property
    def lot_id(self):
        return self._lot_id

    @property
    def gig_id(self):
        return self._gig_id

    @property
    def career_id(self):
        return self._career_id

    @property
    def gig_result(self):
        return self._gig_result

    @property
    def gig_score(self):
        return self._gig_score

    @property
    def customer_name(self):
        return self._customer_name

    @property
    def after_photos(self):
        return self._after_photos

    @property
    def before_photos(self):
        return self._before_photos

    @property
    def hi_low_res_dict(self):
        return self._hi_low_res_dict

    @property
    def project_title(self):
        return self._project_title

    @property
    def gig_lot_type(self):
        return self._gig_lot_type

    @property
    def selected_photos(self):
        return self._selected_photos

    def get_selected_photos(self):
        return self.selected_photos.values()

    def update_selected_photos(self, picked_photo_data, before=True):
        photo_index, photo_resource_key = picked_photo_data
        selected_pair = self.selected_photos.get(photo_index, [None, None])
        if selected_pair[0] is not None:
            if selected_pair[1] is not None:
                selected_pair = [
                 None, None]
        elif before:
            selected_pair[0] = photo_resource_key
        else:
            selected_pair[1] = photo_resource_key
        self.selected_photos[photo_index] = selected_pair

    @property
    def deletion_photos(self):
        return self._deletion_photos

    def update_deleted_photos(self, photo_resource_key):
        self._deletion_photos.append(photo_resource_key.instance)

    def clear_deletion_cache(self):
        self._deletion_photos.clear()

    def clear_selected_photos(self):
        self.selected_photos.clear()

    def update_photo_difference(self):
        self._before_photos = [before_photo for before_photo in self.before_photos if before_photo.instance not in self.deletion_photos]
        self._after_photos = [after_photo for after_photo in self.after_photos if after_photo.instance not in self.deletion_photos]
        for key_to_remove in self.deletion_photos:
            if key_to_remove in self._hi_low_res_dict:
                del self._hi_low_res_dict[key_to_remove]

        selected_photos = list(self.selected_photos.items())
        for index, photos in selected_photos:
            mark_dirty = False
            for photo in photos:
                mark_dirty = mark_dirty or photo.instance in self._deletion_photos

            if mark_dirty:
                del self._selected_photos[index]

        self.deletion_photos.clear()

    def save_gig_history(self, gig_history_proto):
        gig_history_proto.customer_sim_id = self._customer_id
        gig_history_proto.client_lot_id = self._lot_id
        gig_history_proto.gig_id = self._gig_id
        gig_history_proto.career_id = self._career_id
        gig_history_proto.gig_result = self._gig_result
        gig_history_proto.gig_score = self._gig_score
        gig_history_proto.client_hh_name = self._customer_name
        gig_history_proto.gig_lot_type = self._gig_lot_type
        gig_history_proto.project_title = self._project_title
        gig_history_proto.after_photos.extend(self._after_photos)
        gig_history_proto.before_photos.extend(self._before_photos)
        self._save_selected_photos(gig_history_proto)
        self._save_hi_low_res_dict(gig_history_proto)

    def _save_selected_photos(self, gig_history_proto):
        for before_after_photos in self.selected_photos.values():
            if len(before_after_photos) != 2:
                continue
            photo_pair_msg = gig_history_proto.selected_pairs.add()
            photo_pair_msg.before_photo = before_after_photos[0]
            photo_pair_msg.after_photo = before_after_photos[1]

    def _save_hi_low_res_dict(self, gig_history_proto):
        for hi_res_photo_instance, low_res_photo in self.hi_low_res_dict.items():
            hi_low_res_pair_msg = gig_history_proto.hi_low_res_pairs.add()
            hi_low_res_pair_msg.hi_res_photo_instance = hi_res_photo_instance
            hi_low_res_pair_msg.low_res_photo = low_res_photo

    @staticmethod
    def load_gig_history(gig_history_proto):
        career = services.get_instance_manager(sims4.resources.Types.CAREER).get(gig_history_proto.career_id)
        if career is None:
            return
        gig_history = GigHistory(customer_id=(gig_history_proto.customer_sim_id), lot_id=(gig_history_proto.client_lot_id),
          gig_id=(gig_history_proto.gig_id),
          career_id=(gig_history_proto.career_id),
          gig_result=(GigResult(gig_history_proto.gig_result)),
          gig_score=(gig_history_proto.gig_score),
          customer_name=(gig_history_proto.client_hh_name),
          lot_type=(DecoratorGigLotType(gig_history_proto.gig_lot_type)),
          project_title=(gig_history_proto.project_title))
        for after_photo_res_key in gig_history_proto.after_photos:
            gig_history.after_photos.append(after_photo_res_key)

        for before_photo_res_key in gig_history_proto.before_photos:
            gig_history.before_photos.append(before_photo_res_key)

        gig_history._load_selected_photos(gig_history_proto)
        gig_history._load_hi_low_res_dict(gig_history_proto)
        return gig_history

    def _load_selected_photos(self, gig_history_proto):
        selection_index = 1
        for photo_pair in gig_history_proto.selected_pairs:
            self.selected_photos[selection_index] = [
             photo_pair.before_photo, photo_pair.after_photo]
            selection_index += 1

    def _load_hi_low_res_dict(self, gig_history_proto):
        for hi_low_res_pair in gig_history_proto.hi_low_res_pairs:
            self.hi_low_res_dict[hi_low_res_pair.hi_res_photo_instance] = hi_low_res_pair.low_res_photo