# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\ui\ui_dialog_notification.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 10724 bytes
from protocolbuffers import Consts_pb2, Dialog_pb2
from protocolbuffers.DistributorOps_pb2 import Operation
from distributor.ops import GenericProtocolBufferOp
from distributor.shared_messages import IconInfoData
from distributor.system import Distributor
from interactions import ParticipantType
from sims.sim_info_types import Age
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.dynamic_enum import DynamicEnumLocked
from sims4.tuning.tunable import TunableEnumEntry, OptionalTunable, TunableMapping, TunableRange
from singletons import DEFAULT
from snippets import define_snippet
from ui.ui_dialog import UiDialog, get_defualt_ui_dialog_response
import enum, services, sims4.log
logger = sims4.log.Logger('UI Dialog Notification', default_owner='shipark')

class TNSSuppressionGroup(DynamicEnumLocked):
    NONE = 0


class UiDialogNotification(UiDialog):
    DIALOG_MSG_TYPE = Consts_pb2.MSG_UI_NOTIFICATION_SHOW

    class UiDialogNotificationExpandBehavior(enum.Int):
        USER_SETTING = 0
        FORCE_EXPAND = 1

    class UiDialogNotificationUrgency(enum.Int):
        DEFAULT = 0
        URGENT = 1

    class UiDialogNotificationLevel(enum.Int):
        PLAYER = 0
        SIM = 1

    class UiDialogNotificationVisualType(enum.Int):
        INFORMATION = 0
        SPEECH = 1
        SPECIAL_MOMENT = 2

    FACTORY_TUNABLES = {'expand_behavior':TunableEnumEntry(description="\n            Specify the notification's expand behavior.\n            ",
       tunable_type=UiDialogNotificationExpandBehavior,
       default=UiDialogNotificationExpandBehavior.USER_SETTING), 
     'urgency':TunableEnumEntry(description="\n            Specify the notification's urgency.\n            ",
       tunable_type=UiDialogNotificationUrgency,
       default=UiDialogNotificationUrgency.DEFAULT), 
     'information_level':TunableEnumEntry(description="\n            Specify the notification's information level.\n            ",
       tunable_type=UiDialogNotificationLevel,
       default=UiDialogNotificationLevel.SIM), 
     'visual_type':TunableEnumEntry(description="\n            Specify the notification's visual treatment.\n            ",
       tunable_type=UiDialogNotificationVisualType,
       default=UiDialogNotificationVisualType.INFORMATION), 
     'primary_icon_response':OptionalTunable(description='\n            If enabled, associate a response to clicking the primary icon.\n            ',
       tunable=get_defualt_ui_dialog_response(description='\n                The response associated to the primary icon.\n                ')), 
     'secondary_icon_response':OptionalTunable(description='\n            If enabled, associate a response to clicking the secondary icon.\n            ',
       tunable=get_defualt_ui_dialog_response(description='\n                The response associated to the secondary icon.\n                ')), 
     'participant':OptionalTunable(description="\n            This field is deprecated. Please use 'icon' instead.\n            ",
       tunable=TunableEnumEntry(tunable_type=ParticipantType,
       default=(ParticipantType.TargetSim)),
       deprecated=True), 
     'tns_suppression_group':OptionalTunable(description='\n            If enabled, the TNS will be considered for suppression. Suppression occurs if the number\n            of notifications in this group that fire exceed the tuned TNS suppression limit. \n            ',
       tunable=TunableEnumEntry(tunable_type=TNSSuppressionGroup,
       default=(TNSSuppressionGroup.NONE),
       invalid_enums=(
      TNSSuppressionGroup.NONE,))), 
     'override_text_mapping':TunableMapping(description='\n            If enabled, we will override the TNS text depending on age\n            ',
       key_type=TunableEnumEntry(tunable_type=Age,
       default=(Age.ADULT)),
       value_type=TunableLocalizedStringFactory(description='\n                The alternate text that will be displayed in the TNS.\n                '),
       key_name='sim_age',
       value_name='override_string')}

    def show_dialog(self, *args, post_processing=False, **kwargs):
        tns_group = self.tns_suppression_group
        if tns_group is not None:
            if not post_processing:
                (self._set_suppression)(tns_group, *args, **kwargs)
                return
        (super().show_dialog)(*args, **kwargs)

    def _set_suppression(self, tns_group, *args, **kwargs):
        services.ui_dialog_service().set_suppression(tns_group, lambda: (self.show_dialog)(args, post_processing=True, **kwargs))
        logger.info('_set_suppression(): notification {} with tuned group {} registered with the ui dialog service.', self, tns_group)

    def distribute_dialog(self, dialog_type, dialog_msg, **kwargs):
        distributor = Distributor.instance()
        notification_op = GenericProtocolBufferOp(Operation.UI_NOTIFICATION_SHOW, dialog_msg)
        owner = self.owner
        if owner is not None and owner.valid_for_distribution:
            distributor.add_op(owner, notification_op)
        else:
            distributor.add_op_with_no_owner(notification_op)

    def build_msg(self, additional_tokens=(), icon_override=DEFAULT, text_override=DEFAULT, event_id=None, career_args=None, **kwargs):
        if icon_override is DEFAULT:
            if self.participant is not None:
                participant = self._resolver.get_participant(self.participant)
                if participant is not None:
                    icon_override = IconInfoData(obj_instance=participant)
        notification_loc_string = self.override_text_mapping.get(self.owner.age, None) if (self.owner is not None and getattr(self.owner, 'is_sim', False)) else None
        if notification_loc_string is not None:
            text_override = notification_loc_string
        msg = (super().build_msg)(icon_override=icon_override, additional_tokens=additional_tokens, 
         text_override=text_override, **kwargs)
        msg.dialog_type = Dialog_pb2.UiDialogMessage.NOTIFICATION
        notification_msg = msg.Extensions[Dialog_pb2.UiDialogNotification.dialog]
        notification_msg.expand_behavior = self.expand_behavior
        notification_msg.criticality = self.urgency
        notification_msg.information_level = self.information_level
        notification_msg.visual_type = self.visual_type
        if career_args is not None:
            notification_msg.career_args = career_args
        if self.primary_icon_response is not None:
            (self._build_response_arg)((self.primary_icon_response), 
             (notification_msg.primary_icon_response), **kwargs)
        if self.secondary_icon_response is not None:
            (self._build_response_arg)((self.secondary_icon_response), 
             (notification_msg.secondary_icon_response), **kwargs)
        return msg


TunableUiDialogNotificationReference, TunableUiDialogNotificationSnippet = define_snippet('Notification', UiDialogNotification.TunableFactory())

class UiDialogNotificationTuning:
    SUPPRESSION_ALTERNATE_TNS_MAPPING = TunableMapping(description='\n        If tuned, display an alternate TNS after a TNS group is suppressed.\n        ',
      key_type=TunableEnumEntry(tunable_type=TNSSuppressionGroup,
      default=(TNSSuppressionGroup.NONE),
      invalid_enums=(
     TNSSuppressionGroup.NONE,)),
      value_type=TunableUiDialogNotificationSnippet(description='\n            The alternate TNS to display if the TNS group is suppressed.\n            '))
    SUPPRESSION_LIMIT_OVERRIDE_MAPPING = TunableMapping(description='\n        If tuned, override the default TNS suppression limit for a specific tns group.\n        ',
      key_type=TunableEnumEntry(tunable_type=TNSSuppressionGroup,
      default=(TNSSuppressionGroup.NONE),
      invalid_enums=(
     TNSSuppressionGroup.NONE,)),
      value_type=TunableRange(tunable_type=int,
      default=3,
      minimum=2))
    DEFAULT_TNS_SUPPRESSION_LIMIT = TunableRange(description='\n        The default number of TNS dialogs in a group that fire before triggering suppression. This\n        value can be overriden for individual TNS groups.\n\n        The counter starts when the server receives the first TNS request and resets on a subsequently\n        scheduled element. That element should run on the next game tick.\n        ',
      tunable_type=int,
      default=3,
      minimum=2)