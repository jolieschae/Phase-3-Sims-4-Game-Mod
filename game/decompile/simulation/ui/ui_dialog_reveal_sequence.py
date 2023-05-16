# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\ui\ui_dialog_reveal_sequence.py
# Compiled at: 2021-04-19 22:29:40
# Size of source mod 2**32: 3693 bytes
from protocolbuffers import Dialog_pb2
from crafting.photography_enums import RevealPhotoStates
from distributor.shared_messages import create_icon_info_msg, IconInfoData
from sims4.tuning.tunable import TunablePackSafeReference
from ui.ui_dialog import UiDialog
import services, sims4.resources, sims4.log
logger = sims4.log.Logger('Reveal Sequence Dialog', default_owner='shipark')

class UiDialogRevealSequence(UiDialog):
    FACTORY_TUNABLES = {'career_reference': TunablePackSafeReference(description='                \n            A reference to the gig-career that provides the reveal moment photos.\n            ',
                           manager=(services.get_instance_manager(sims4.resources.Types.CAREER)))}

    def __init__(self, *args, active_gig=True, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._active_gig = active_gig

    def get_selected_pairs(self, sim_info):
        if self.career_reference is None:
            return
        career_tracker = sim_info.career_tracker
        if career_tracker is None:
            logger.error("Trying to display the Reveal Sequence but Sim '{}' doesn't have a career tracker.", sim_info)
            return
        career = career_tracker.get_career_by_uid(self.career_reference.guid64)
        if career is None:
            logger.error('Trying to display the Reveal Sequence but Sim {} does not have a career of type: {}', sim_info, self.career_reference)
            return
        return career_tracker.get_selected_photos(career, self._active_gig)

    def _create_photo_icon_info_messsage(self, icon_resource, photo_state):
        icon_data = IconInfoData(icon_resource=icon_resource)
        icon_info_msg = create_icon_info_msg(icon_data)
        icon_info_msg.control_id = photo_state
        return icon_info_msg

    def set_icon_infos(self, owner, msg):
        selected_pairs = self.get_selected_pairs(owner.sim_info)
        if selected_pairs is None:
            logger.error('Attempting to create the Reveal Sequence without any selected photos set.')
            return
        for before_photo, after_photo in selected_pairs:
            before_icon_info_msg = self._create_photo_icon_info_messsage(before_photo, RevealPhotoStates.BEFORE_PHOTO)
            msg.icon_infos.append(before_icon_info_msg)
            after_icon_info_msg = self._create_photo_icon_info_messsage(after_photo, RevealPhotoStates.AFTER_PHOTO)
            msg.icon_infos.append(after_icon_info_msg)

    def build_msg(self, owner=None, **kwargs):
        msg = (super().build_msg)(**kwargs)
        msg.dialog_type = Dialog_pb2.UiDialogMessage.REVEAL_SEQUENCE
        self.set_icon_infos(owner, msg)
        return msg