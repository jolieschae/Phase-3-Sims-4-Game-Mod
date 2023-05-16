# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\picker\stayover_multi_picker_interaction.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 15423 bytes
from protocolbuffers import Dialog_pb2
from date_and_time import create_time_span
from event_testing.resolver import SingleSimResolver
from interactions import ParticipantType, ParticipantTypeSim
from interactions.context import InteractionContext, InteractionSource
from interactions.priority import Priority
from interactions.base.multi_picker_interaction import MultiPickerInteraction
from sims4.localization import TunableLocalizedString, TunableLocalizedStringFactoryVariant, NULL_LOCALIZED_STRING_FACTORY
from sims4.tuning.tunable import OptionalTunable, TunableReference, TunableTuple, TunableEnumFlags
from sims4.tuning.tunable_base import GroupNames
from ui.ui_dialog_multi_picker import UiMultiPicker
import clock, services, sims4.log, sims4.resources
logger = sims4.log.Logger('StayoverObjectMultiPicker', default_owner='nabaker')

class UiStayoverMultiPicker(UiMultiPicker):
    FACTORY_TUNABLES = {'text':OptionalTunable(description='\n            If enabled, this dialog will include text.\n            ',
       tunable=TunableLocalizedStringFactoryVariant(description="\n                The dialog's text.\n                "),
       disabled_value=NULL_LOCALIZED_STRING_FACTORY), 
     'stayover_pickers':TunableTuple(description='\n            A list of picker interactions to use to build pickers.\n            ',
       duration_picker=TunableTuple(description='\n                A number picker for players to select a duration and\n                send to gameplay.\n                ',
       picker_interaction=TunableReference(description='\n                    The interaction that will be used to generate a picker.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       class_restrictions='NumberPickerSuperInteraction'),
       disabled_tooltip=TunableLocalizedString(description='\n                    The string that will be displayed when an item in the \n                    associated picker is not available.\n                    '),
       locked_args={'max_selected_tooltip':None, 
      'show_header':False}),
       start_time_picker=OptionalTunable(description='\n                A time picker for players to select a start time and send to gameplay.\n                If disabled, stayover will start immediately.\n                ',
       tunable=TunableTuple(description='\n                    A time picker for players to select a start time and send to gameplay\n                    ',
       picker_interaction=TunableReference(description='\n                        The interaction that will be used to generate a picker.\n                        ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       class_restrictions='TimePickerSuperInteraction'),
       disabled_tooltip=TunableLocalizedString(description='\n                        The string that will be displayed when an item in the \n                        associated picker is not available.\n                        '),
       locked_args={'max_selected_tooltip':None, 
      'show_header':False})),
       sim_picker=TunableTuple(description='\n                A sim picker for players to select the sims and\n                send to gameplay.\n                ',
       picker_interaction=TunableReference(description='\n                    The interaction that will be used to generate a picker.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       class_restrictions='SimPickerInteraction'),
       locked_args={'max_selected_tooltip':None, 
      'show_header':True,  'disabled_tooltip':None}),
       existing_invitees_picker=TunableTuple(description='\n                A sim picker for players to select the previously invited sims and\n                send to gameplay.\n                ',
       picker_interaction=TunableReference(description='\n                    The interaction that will be used to generate a picker.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       class_restrictions='SimPickerInteraction'),
       locked_args={'max_selected_tooltip':None, 
      'show_header':True,  'disabled_tooltip':None}),
       tuning_group=GroupNames.PICKERTUNING), 
     'min_selectable_tooltip':TunableLocalizedString(description='\n            The tooltip text when the ok button is disabled because no sims are selected in either sim picker.\n            ',
       tuning_group=GroupNames.PICKERTUNING), 
     'max_selectable_tooltip':TunableLocalizedString(description='\n            The tooltip text when the ok button is disabled because selected sims across both pickers exceeds capacity\n            for a stayover on the active hosueholds lot.  (Presumably editing a stayover after the capacity has\n            decreased due to additional roommates or household members since the stayover was previously planned.)\n            ',
       tuning_group=GroupNames.PICKERTUNING)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._duration_dialog = None
        self._time_dialog = None
        self._sim_dialog = None
        self._existing_invitee_dialog = None
        self.stayover_info = None

    def build_msg(self, duration_override=None, time_override=None, default_picked_sims=set(), days_away=0, **kwargs):
        message = (super().build_msg)(**kwargs)
        message.dialog_type = Dialog_pb2.UiDialogMessage.MULTI_PICKER
        context = InteractionContext(self._owner(), InteractionSource.SCRIPT, Priority.Low)
        self._duration_dialog, _ = self.build_multi_picker_msg((self.stayover_pickers.duration_picker), (message.multi_picker_data),
          context, default_override=duration_override)
        if self.stayover_pickers.start_time_picker is not None:
            self._time_dialog, _ = self.build_multi_picker_msg((self.stayover_pickers.start_time_picker), (message.multi_picker_data),
              context, default_override=time_override,
              days_away=days_away)
        combined_limits_msg = message.multi_picker_data.combined_limits_datas.add()
        if default_picked_sims:
            self._existing_invitee_dialog, _ = self.build_multi_picker_msg((self.stayover_pickers.existing_invitees_picker), (message.multi_picker_data),
              context, combined_limits_msg=combined_limits_msg,
              default_selection=default_picked_sims,
              included_override=default_picked_sims)
        self._sim_dialog, _ = self.build_multi_picker_msg((self.stayover_pickers.sim_picker), (message.multi_picker_data),
          context, combined_limits_msg=combined_limits_msg,
          excluded_override=default_picked_sims)
        combined_limits_msg.min_selectable = 1
        combined_limits_msg.max_selectable = services.travel_group_manager().get_stayover_capacity(services.active_household())
        combined_limits_msg.max_selectable_tooltip = self.max_selectable_tooltip
        combined_limits_msg.min_selectable_tooltip = self.min_selectable_tooltip
        return message

    def multi_picker_result(self, response_proto):
        super().multi_picker_result(response_proto)
        invited_sims = [] if self._existing_invitee_dialog is None else self._existing_invitee_dialog.get_result_tags()
        self.stayover_info = (self._duration_dialog.get_single_result_tag(),
         None if self._time_dialog is None else self._time_dialog.get_single_result_tag(),
         self._sim_dialog.get_result_tags() + invited_sims)
        self._changes_made = True


class StayoverMultiPickerInteraction(MultiPickerInteraction):
    INSTANCE_TUNABLES = {'picker_dialog':UiStayoverMultiPicker.TunableFactory(description='\n            Tuning for the ui customize object multi picker. \n            ',
       tuning_group=GroupNames.PICKERTUNING), 
     'stayover_behavioral_situation':TunableReference(description='\n            The behavioral situation that will run for the guest sims in the stay over.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION),
       class_restrictions='AmbientSimSpecificCustomStatesSituation',
       tuning_group=GroupNames.PICKERTUNING), 
     'planned_stayover_drama_node':TunableReference(description='\n            The drama node that will be scheduled when a player plans a stayover.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.DRAMA_NODE),
       class_restrictions=('PlayerPlannedStayoverDramaNode', )), 
     'default_selected_participants':TunableEnumFlags(description='\n            Participants of the interaction that should be selected by default in the picker.\n            ',
       enum_type=ParticipantTypeSim,
       allow_no_flags=True,
       tuning_group=GroupNames.PICKERTUNING)}

    def __init__(self, *args, days_away=0, drama_id=0, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._days_away = days_away
        self._drama_id = drama_id

    @classmethod
    def has_valid_choice(cls, target, context, **kwargs):
        return (cls.picker_dialog.stayover_pickers.sim_picker.picker_interaction.has_valid_choice)(target, context, **kwargs)

    def _show_picker_dialog(self, owner, **kwargs):
        if self.use_pie_menu():
            return
        dialog = (self._create_dialog)(owner, **kwargs)
        default_sim_ids = set((sim_or_sim_info.id for sim_or_sim_info in self.get_participants(self.default_selected_participants) if self.sim.sim_info is not sim_or_sim_info.sim_info))
        original_duration = None
        original_start_time = None
        if self._drama_id != 0:
            existing_drama_node = services.drama_scheduler_service().get_scheduled_node_by_uid(self._drama_id)
            if existing_drama_node is not None:
                original_duration = existing_drama_node.duration
                default_sim_ids.update(existing_drama_node.guest_sim_ids)
                start_time = existing_drama_node.get_calendar_start_time()
                original_start_time = start_time.time_of_day()
                self._days_away = int(start_time.absolute_days()) - int(services.time_service().sim_now.absolute_days())
        dialog.show_dialog(duration_override=original_duration, time_override=original_start_time,
          default_picked_sims=default_sim_ids,
          days_away=(self._days_away))

    def _on_picker_selected(self, dialog):
        if dialog.stayover_info is not None:
            duration, time, sim_ids = dialog.stayover_info
            if duration is not None:
                if self._drama_id != 0:
                    services.drama_scheduler_service().cancel_scheduled_node(self._drama_id)
                household = self.sim.household
                zone_id = self.sim.household.home_zone_id
                if time is None:
                    scheduled_time = services.time_service().sim_now
                else:
                    current_time = services.time_service().sim_now
                    scheduled_time = current_time + current_time.time_till_next_day_time(time, rollover_same_time=(self._days_away != 0))
                    if time < current_time.time_of_day():
                        self._days_away -= 1
                scheduled_time = scheduled_time + create_time_span(days=(self._days_away))
                services.drama_scheduler_service().schedule_node((self.planned_stayover_drama_node), (SingleSimResolver(self.sim.sim_info)),
                  specific_time=scheduled_time,
                  zone_id=zone_id,
                  household_id=(household.id),
                  duration=duration,
                  guest_sim_ids=sim_ids,
                  behavior_situation=(self.stayover_behavioral_situation))
        super()._on_picker_selected(dialog)