# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\player_planned_stayover_drama_node.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 18034 bytes
from date_and_time import create_time_span, TimeSpan
from drama_scheduler.drama_node import BaseDramaNode, DramaNodeRunOutcome
from drama_scheduler.drama_node_types import DramaNodeType
from sims4.localization import LocalizationHelperTuning, TunableLocalizedStringFactory
from sims4.tuning.instances import lock_instance_tunables
from sims4.utils import classproperty, flexmethod
from travel_group.travel_group_stayover import TravelGroupStayover
from ui.ui_dialog import UiDialogOk, UiDialogOkCancel, UiDialogResponse, ButtonType
from venues.venue_event_drama_node import VenueEventDramaNode
import clock, services, sims4.log
ZONE_ID_TOKEN = 'zone_id'
HOUSEHOLD_ID_TOKEN = 'household_id'
DURATION_TOKEN = 'duration'
GUEST_SIM_IDS_TOKEN = 'guest_sim_ids'
BEHHAVIOR_SITUATION_ID_TOKEN = 'behavior_situation_id'
logger = sims4.log.Logger('PlayerPlannedStayoverDramaNode', default_owner='nabaker')

class PlayerPlannedStayoverDramaNode(BaseDramaNode):
    RESPONSE_ID_GO_HOME = 0
    INSTANCE_TUNABLES = {'existing_travel_group_dialog':UiDialogOkCancel.TunableFactory(description='\n            The ok cancel dialog that will display to the user if there are any conflicting travel groups.  Reasons\n            for conflict will be a passed in bulleted list as first (scripted) token.  O.K. cancels the travel group(s) involved in any conflicts. and\n            starts the new stayover.  Cancel cancels the new stayover.\n            '), 
     'confirm_dialog':UiDialogOkCancel.TunableFactory(description='\n            The ok cancel dialog that will display to the user if there are no conflicts.\n            '), 
     'invalid_dialog':UiDialogOk.TunableFactory(description='\n            The ok dialog that will display to the user if it is no longer possible to start the stayover.  (e.g. too\n            many sims due to addition or somesuch.)\n            '), 
     'existing_household_vacation_error_text':TunableLocalizedStringFactory(description='\n            Bulletpoint if members of active household are already on a vacation.\n            '), 
     'existing_household_stayover_error_text':TunableLocalizedStringFactory(description='\n            Bulletpoint if stayover already in progress on active households zone.\n            '), 
     'existing_guest_vacation_error_text':TunableLocalizedStringFactory(description='\n            Bulletpoint for any guests household that is already on a vacation/stayover. \n            (Household name is first parameter).\n            '), 
     'existing_guest_stayover_error_text':TunableLocalizedStringFactory(description='\n            Bulletpoint for any guests household that is already involved in hosting a stayover.\n            (Household name is first parameter).\n            '), 
     'calendar_alert_description':TunableLocalizedStringFactory(description='\n            Description that shows in the calendar alert.\n            '), 
     'travel_home_text':TunableLocalizedStringFactory(description='\n            Button text for travel home button if off lot.\n            '), 
     'travel_home_disabled_text':TunableLocalizedStringFactory(description='\n            Tooltip text for travel home button if off lot but unable to travel.\n            ')}

    @classproperty
    def persist_when_active(cls):
        return True

    @classproperty
    def drama_node_type(cls):
        return DramaNodeType.STAYOVER

    def __init__(self, *args, uid=None, zone_id=None, household_id=None, duration=None, guest_sim_ids=[], behavior_situation=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._zone_id = zone_id
        self._household_id = household_id
        self._duration = duration
        self._guest_sim_ids = guest_sim_ids
        self._behavior_situation = behavior_situation

    @property
    def duration(self):
        return self._duration

    @property
    def guest_sim_ids(self):
        return self._guest_sim_ids

    @property
    def _require_instanced_sim(self):
        return False

    def _validate_stayover--- This code section failed: ---

 L. 121         0  LOAD_FAST                'self'
                2  LOAD_ATTR                _zone_id
                4  LOAD_CONST               None
                6  COMPARE_OP               is
                8  POP_JUMP_IF_TRUE     46  'to 46'

 L. 122        10  LOAD_FAST                'self'
               12  LOAD_ATTR                _household_id
               14  LOAD_CONST               None
               16  COMPARE_OP               is
               18  POP_JUMP_IF_TRUE     46  'to 46'

 L. 123        20  LOAD_FAST                'self'
               22  LOAD_ATTR                _duration
               24  LOAD_CONST               None
               26  COMPARE_OP               is
               28  POP_JUMP_IF_TRUE     46  'to 46'

 L. 124        30  LOAD_FAST                'self'
               32  LOAD_ATTR                _guest_sim_ids
               34  POP_JUMP_IF_FALSE    46  'to 46'

 L. 125        36  LOAD_FAST                'self'
               38  LOAD_ATTR                _behavior_situation
               40  LOAD_CONST               None
               42  COMPARE_OP               is
               44  POP_JUMP_IF_FALSE    50  'to 50'
             46_0  COME_FROM            34  '34'
             46_1  COME_FROM            28  '28'
             46_2  COME_FROM            18  '18'
             46_3  COME_FROM             8  '8'

 L. 126        46  LOAD_CONST               False
               48  RETURN_VALUE     
             50_0  COME_FROM            44  '44'

 L. 128        50  LOAD_GLOBAL              services
               52  LOAD_METHOD              household_manager
               54  CALL_METHOD_0         0  '0 positional arguments'
               56  LOAD_METHOD              get
               58  LOAD_FAST                'self'
               60  LOAD_ATTR                _household_id
               62  CALL_METHOD_1         1  '1 positional argument'
               64  STORE_FAST               'household'

 L. 129        66  LOAD_FAST                'household'
               68  LOAD_ATTR                home_zone_id
               70  LOAD_FAST                'self'
               72  LOAD_ATTR                _zone_id
               74  COMPARE_OP               !=
               76  POP_JUMP_IF_FALSE    82  'to 82'

 L. 130        78  LOAD_CONST               False
               80  RETURN_VALUE     
             82_0  COME_FROM            76  '76'

 L. 132        82  LOAD_GLOBAL              len
               84  LOAD_FAST                'household'
               86  CALL_FUNCTION_1       1  '1 positional argument'
               88  LOAD_GLOBAL              len
               90  LOAD_FAST                'self'
               92  LOAD_ATTR                _guest_sim_ids
               94  CALL_FUNCTION_1       1  '1 positional argument'
               96  BINARY_ADD       
               98  STORE_FAST               'total_count'

 L. 133       100  LOAD_GLOBAL              services
              102  LOAD_METHOD              get_roommate_service
              104  CALL_METHOD_0         0  '0 positional arguments'
              106  STORE_FAST               'roommate_service'

 L. 134       108  LOAD_FAST                'roommate_service'
              110  LOAD_CONST               None
              112  COMPARE_OP               is-not
              114  POP_JUMP_IF_FALSE   132  'to 132'

 L. 135       116  LOAD_FAST                'total_count'
              118  LOAD_FAST                'roommate_service'
              120  LOAD_METHOD              get_roommate_count
              122  LOAD_FAST                'household'
              124  LOAD_ATTR                home_zone_id
              126  CALL_METHOD_1         1  '1 positional argument'
              128  INPLACE_ADD      
              130  STORE_FAST               'total_count'
            132_0  COME_FROM           114  '114'

 L. 136       132  LOAD_FAST                'total_count'
              134  LOAD_GLOBAL              TravelGroupStayover
              136  LOAD_ATTR                HOUSEHOLD_AND_GUEST_MAXIMUM
              138  COMPARE_OP               >
              140  POP_JUMP_IF_FALSE   146  'to 146'

 L. 137       142  LOAD_CONST               False
              144  RETURN_VALUE     
            146_0  COME_FROM           140  '140'

 L. 138       146  LOAD_GLOBAL              services
              148  LOAD_METHOD              sim_info_manager
              150  CALL_METHOD_0         0  '0 positional arguments'
              152  STORE_FAST               'sim_info_manager'

 L. 139       154  SETUP_LOOP          212  'to 212'
              156  LOAD_FAST                'self'
              158  LOAD_ATTR                _guest_sim_ids
              160  GET_ITER         
            162_0  COME_FROM           202  '202'
              162  FOR_ITER            210  'to 210'
              164  STORE_FAST               'sim_id'

 L. 140       166  LOAD_FAST                'sim_info_manager'
              168  LOAD_METHOD              get
              170  LOAD_FAST                'sim_id'
              172  CALL_METHOD_1         1  '1 positional argument'
              174  STORE_FAST               'sim_info'

 L. 141       176  LOAD_FAST                'sim_info'
              178  LOAD_CONST               None
              180  COMPARE_OP               is
              182  POP_JUMP_IF_FALSE   188  'to 188'

 L. 142       184  LOAD_CONST               False
              186  RETURN_VALUE     
            188_0  COME_FROM           182  '182'

 L. 143       188  LOAD_FAST                'sim_info'
              190  LOAD_ATTR                can_instantiate_sim
              192  POP_JUMP_IF_TRUE    198  'to 198'

 L. 144       194  LOAD_CONST               False
              196  RETURN_VALUE     
            198_0  COME_FROM           192  '192'

 L. 145       198  LOAD_FAST                'sim_info'
              200  LOAD_ATTR                is_selectable
              202  POP_JUMP_IF_FALSE   162  'to 162'

 L. 146       204  LOAD_CONST               False
              206  RETURN_VALUE     
              208  JUMP_BACK           162  'to 162'
              210  POP_BLOCK        
            212_0  COME_FROM_LOOP      154  '154'

 L. 147       212  LOAD_CONST               True
              214  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `RETURN_VALUE' instruction at offset 214

    def on_situation_creation_during_zone_spin_up(self) -> None:
        result = services.drama_scheduler_service.schedule_node((self.__class__), (self._get_resolver),
          specific_time=(services.time_service.sim_now),
          drama_inst=self)
        if result is None:
            services.drama_scheduler_service.complete_nodeself.uid

    def _run(self):
        delay_result = self.try_do_travel_dialog_delay
        if delay_result is not None:
            return delay_result
        if services.ui_dialog_service.has_active_modal_dialogs:
            current_time = services.time_service.sim_now
            self._selected_time = current_time + create_time_span(minutes=5)
            if not self._schedule_alarm:
                return DramaNodeRunOutcome.FAILURE
            return DramaNodeRunOutcome.RESCHEDULED
        household = services.household_manager.getself._household_id
        if not self._validate_stayover:
            if household.is_active_household:
                fail_dialog = self.invalid_dialog(services.active_sim_info, None)
                fail_dialog.show_dialog
            return DramaNodeRunOutcome.FAILURE
        additional_responses = None
        if household.home_zone_id != services.current_zone_id:
            disabled_text = None
            if services.get_zone_situation_manager.is_user_facing_situation_running:
                disabled_text = self.travel_home_disabled_text
            go_home_response = UiDialogResponse(dialog_response_id=(self.RESPONSE_ID_GO_HOME), text=(self.travel_home_text),
              disabled_text=disabled_text)
            additional_responses = (go_home_response,)
        error_strings = []
        travel_group_manager = services.travel_group_manager
        if household.get_travel_group is not None:
            error_strings.appendself.existing_household_vacation_error_text
        if travel_group_manager.get_travel_group_by_zone_idself._zone_id is not None:
            error_strings.appendself.existing_household_stayover_error_text
        household_set = set()
        for sim_info in self._get_guest_sim_infos:
            household_set.addsim_info.household

        for guest_household in household_set:
            if guest_household.get_travel_group is not None:
                error_strings.appendself.existing_guest_vacation_error_textguest_household.name
            if travel_group_manager.get_travel_group_by_zone_idguest_household.home_zone_id is not None:
                error_strings.appendself.existing_guest_stayover_error_textguest_household.name

        if error_strings:
            if not household.is_active_household:
                return DramaNodeRunOutcome.FAILURE
            error_bullets = (LocalizationHelperTuning.get_bulleted_list)(*(None, ), *error_strings)
            error_dialog = self.existing_travel_group_dialog((self._receiver_sim_info), resolver=(self._get_resolver))
            if additional_responses:
                error_dialog.set_responsesadditional_responses

            def error_resposne(dialog):
                if (dialog.response is None or dialog.response) != ButtonType.DIALOG_RESPONSE_OK:
                    if dialog.response != self.RESPONSE_ID_GO_HOME:
                        services.drama_scheduler_service.complete_nodeself.uid
                        return
                travel_group = household.get_travel_group
                if travel_group is not None:
                    travel_group.end_vacation
                travel_group = travel_group_manager.get_travel_group_by_zone_idself._zone_id
                if travel_group is not None:
                    travel_group.end_vacation
                for response_household in household_set:
                    travel_group = response_household.get_travel_group
                    if travel_group is not None:
                        travel_group.end_vacation
                    travel_group = travel_group_manager.get_travel_group_by_zone_idresponse_household.home_zone_id
                    if travel_group is not None:
                        travel_group.end_vacation

                self._start_stayover
                if dialog.response == self.RESPONSE_ID_GO_HOME:
                    self.travel_to_destination
                services.drama_scheduler_service.complete_nodeself.uid

            error_dialog.show_dialog(on_response=error_resposne, additional_tokens=(error_bullets,))
            return DramaNodeRunOutcome.SUCCESS_NODE_INCOMPLETE
        if not household.is_active_household:
            self._start_stayover
            return DramaNodeRunOutcome.SUCCESS_NODE_COMPLETE
        dialog = self.confirm_dialog((self._receiver_sim_info), resolver=(self._get_resolver))
        if additional_responses:
            dialog.set_responsesadditional_responses

        def response(dialog):
            if dialog.response is not None:
                if dialog.response == ButtonType.DIALOG_RESPONSE_OK:
                    self._start_stayover
                else:
                    if dialog.response == self.RESPONSE_ID_GO_HOME:
                        self._start_stayover
                        self.travel_to_destination
            services.drama_scheduler_service.complete_nodeself.uid

        dialog.show_dialog(on_response=response)
        return DramaNodeRunOutcome.SUCCESS_NODE_INCOMPLETE

    def _start_stayover(self):
        create_timestamp = self._selected_time
        end_timestamp = create_timestamp + clock.interval_in_sim_daysself._duration
        travel_group_manager = services.travel_group_manager
        sim_info_manager = services.sim_info_manager
        sim_infos = []
        for sim_id in self._guest_sim_ids:
            sim_info = sim_info_manager.getsim_id
            if sim_info is not None:
                sim_infos.appendsim_info

        travel_group_manager.create_travel_group_and_rent_zone(sim_infos=sim_infos, zone_id=(self._zone_id), played=False, create_timestamp=create_timestamp,
          end_timestamp=end_timestamp,
          cost=0,
          stayover_situation=(self._behavior_situation))

    @flexmethod
    def get_destination_lot_id(cls, inst):
        if inst is None:
            return services.active_household_lot_id
        return services.get_persistence_service.get_lot_id_from_zone_idinst._zone_id

    @flexmethod
    def get_travel_interaction(cls, inst):
        return VenueEventDramaNode.GO_TO_VENUE_ZONE_INTERACTION

    def schedule(self, resolver, specific_time=None, time_modifier=TimeSpan.ZERO):
        success = super().schedule(resolver, specific_time=specific_time, time_modifier=time_modifier)
        if success:
            services.calendar_service.mark_on_calendarself
        return success

    def _validate_time(self, time_to_check):
        pass

    def cleanup(self, from_service_stop=False):
        services.calendar_service.remove_on_calendarself.uid
        super().cleanup(from_service_stop=from_service_stop)

    def _get_guest_sim_infos(self):
        sim_infos = []
        for sim_id in self._guest_sim_ids:
            sim_info = services.sim_info_manager.getsim_id
            if sim_info is not None:
                sim_infos.appendsim_info

        return sim_infos

    def get_calendar_end_time(self):
        return self.selected_time + create_time_span(days=(self._duration))

    def create_calendar_entry(self):
        calendar_entry = super().create_calendar_entry
        calendar_entry.zone_id = self._zone_id
        calendar_entry.scoring_enabled = False
        calendar_entry.deletable = False
        for sim_id in self._guest_sim_ids:
            calendar_entry.household_sim_ids.appendsim_id

        return calendar_entry

    def _save_custom_data(self, writer):
        if self._zone_id is not None:
            writer.write_uint64(ZONE_ID_TOKEN, self._zone_id)
        if self._household_id is not None:
            writer.write_uint64(HOUSEHOLD_ID_TOKEN, self._household_id)
        if self._duration is not None:
            writer.write_uint64(DURATION_TOKEN, self._duration)
        if self._guest_sim_ids:
            writer.write_uint64s(GUEST_SIM_IDS_TOKEN, self._guest_sim_ids)
        if self._behavior_situation is not None:
            writer.write_uint64(BEHHAVIOR_SITUATION_ID_TOKEN, self._behavior_situation.guid64)

    def _load_custom_data(self, reader):
        super_success = super()._load_custom_datareader
        if not super_success:
            return False
        else:
            self._zone_id = reader.read_uint64(ZONE_ID_TOKEN, None)
            if self._zone_id is None:
                return False
            self._household_id = reader.read_uint64(HOUSEHOLD_ID_TOKEN, None)
            if self._household_id is None:
                return False
            self._duration = reader.read_uint64(DURATION_TOKEN, None)
            if self._duration is None:
                return False
            self._guest_sim_ids = reader.read_uint64s(GUEST_SIM_IDS_TOKEN, ())
            return self._guest_sim_ids or False
        self._behavior_situation = services.get_instance_managersims4.resources.Types.SITUATION.getreader.read_uint64(BEHHAVIOR_SITUATION_ID_TOKEN, 0)
        if self._behavior_situation is None:
            return False
        return True

    def load(self, drama_node_proto, schedule_alarm=True):
        super_success = super().load(drama_node_proto, schedule_alarm=schedule_alarm)
        if not super_success:
            return False
        household = services.household_manager.getself._household_id
        if household is None:
            return False
        if household.home_zone_id != self._zone_id:
            return False
        if household.is_active_household:
            services.calendar_service.mark_on_calendarself
        return True


lock_instance_tunables(PlayerPlannedStayoverDramaNode, ui_display_data=None)