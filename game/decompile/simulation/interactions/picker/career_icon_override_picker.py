# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\picker\career_icon_override_picker.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 8254 bytes
import services, sims4
from distributor.shared_messages import IconInfoData
from interactions import ParticipantTypeSingle, ParticipantType
from interactions.base.picker_interaction import PickerSuperInteraction
from interactions.utils.tunable_icon import TunableIconFactory, TunableIconVariant
from sims4.localization import TunableLocalizedString
from sims4.tuning.tunable import TunableList, TunableTuple, Tunable, TunablePackSafeReference, TunableEnumFlags
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
from ui.ui_dialog_picker import ObjectPickerRow
logger = sims4.log.Logger('CareerAvatars', default_owner='yecao')

class CareerIconOverridePicker(PickerSuperInteraction):
    INSTANCE_TUNABLES = {'icon_choices':TunableList(description='\n            A list of all the tuning needed for the different Icons for a career\n            ',
       tunable=TunableTuple(description='\n                The Icon to override the default sim profile icon.\n                ',
       icon=(TunableIconVariant()),
       description_text=TunableLocalizedString(description='\n                    The description for icon that is displayed in the picker.\n                    '),
       is_default=Tunable(description='\n                    The default icon for the career when no choice from player is made.\n                    At least one of the icon should be set as default.\n                    ',
       tunable_type=bool,
       default=False)),
       tuning_group=GroupNames.PICKERTUNING,
       unique_entries=True), 
     'career_reference':TunablePackSafeReference(description='\n            The Career we pick the icon for.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CAREER),
       tuning_group=GroupNames.PICKERTUNING), 
     'participant_type':TunableEnumFlags(description='\n            The Participant who owns the career.\n            ',
       enum_type=ParticipantTypeSingle,
       default=ParticipantType.Actor,
       tuning_group=GroupNames.PICKERTUNING)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._target_career = kwargs.get('target_career')
        self._defer_assignment = kwargs.get('defer_assignment')
        self._is_changing_icon = not self._target_career

    def _run_interaction_gen(self, timeline):
        self._show_picker_dialog((self.sim), target_sim=(self.sim))
        return True
        if False:
            yield None

    @flexmethod
    def get_target_career(cls, inst):
        if inst is not None:
            if inst._target_career is not None:
                return inst._target_career
        inst_or_cls = inst if inst is not None else cls
        resolver = inst_or_cls.get_resolver()
        if inst_or_cls.participant_type is None or inst_or_cls.career_reference is None:
            logger.error('Need to set career reference and participant type in tuning for {}.', inst_or_cls)
            return
        participant = resolver.get_participant(inst_or_cls.participant_type)
        if participant is None:
            logger.error('Unable to retrieve participant for career icon override picker with participant type {}.', inst_or_cls.participant_type)
            return
        career_tracker = participant.career_tracker
        for current_career in career_tracker.careers.values():
            if current_career.guid64 == inst_or_cls.career_reference.guid64:
                if inst is not None:
                    inst._target_career = current_career
                return current_career

        logger.error("Can not find career reference: {} from {}'s career tracker.", inst_or_cls.career_reference, participant)

    @flexmethod
    def get_icon_info(cls, inst, icon_choice):
        inst_or_cls = inst if inst is not None else cls
        if icon_choice is None:
            return
        resolver = inst_or_cls.get_resolver(inst_or_cls.participant_type)
        return icon_choice.icon(resolver)

    @flexmethod
    def picker_rows_gen(cls, inst, target, context, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        selected_icon = None
        target_career = inst_or_cls.get_target_career()
        if target_career is not None:
            selected_icon = target_career.icon_override
        for override_icon in inst_or_cls.icon_choices:
            icon_info = inst_or_cls.get_icon_info(override_icon)
            icon_resource = None if icon_info is None else icon_info.icon_resource
            yield ObjectPickerRow(row_description=(override_icon.description_text), icon_info=icon_info,
              tag=icon_resource,
              is_selected=(selected_icon == icon_resource))

    def on_choice_selected(self, choice_tag, **kwargs):
        if choice_tag is None:
            for override_icon in self.icon_choices:
                if override_icon.is_default:
                    icon_info = self.get_icon_info(override_icon)
                    choice_tag = None if icon_info is None else icon_info.icon_resource

        else:
            target_career = self.get_target_career()
            defer_assignment = self._defer_assignment
            if target_career is not None:
                if not self._is_changing_icon:
                    target_career.icon_override = choice_tag
                    _, first_work_time, _ = target_career.get_next_work_time()
                    target_career.send_career_message(target_career.career_messages.join_career_notification, first_work_time)
                    target_career._setup_assignments_for_career_joined(defer_assignment=defer_assignment)
                else:
                    target_career.icon_override = choice_tag
            else:
                logger.error('No Career for picker {} found.', self)