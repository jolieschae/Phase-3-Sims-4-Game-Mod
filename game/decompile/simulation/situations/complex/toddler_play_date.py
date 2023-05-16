# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\toddler_play_date.py
# Compiled at: 2019-11-13 19:00:31
# Size of source mod 2**32: 7878 bytes
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable_base import GroupNames
from situations.bouncer.bouncer_types import BouncerExclusivityCategory
from situations.situation_complex import SituationComplexCommon, SituationStateData, TunableSituationJobAndRoleState, CommonInteractionCompletedSituationState, CommonSituationState
from situations.situation_guest_list import SituationGuestInfo, SituationInvitationPurpose
import build_buy, services, sims4
logger = sims4.log.Logger('Situations')

class _PlayDateState(CommonSituationState):

    def timer_expired(self):
        self._change_state(self.owner._leave_state())


class _LeaveState(CommonInteractionCompletedSituationState):
    pass


class ToddlerPlayDateSituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'host_toddler_job_and_role_state':TunableSituationJobAndRoleState(description='\n            The job and role state of toddler who planned the Play Date.\n            ',
       tuning_group=GroupNames.ROLES), 
     'host_parent_job_and_role_state':TunableSituationJobAndRoleState(description='\n            The job and role state of parent who planned the Play Date.\n            ',
       tuning_group=GroupNames.ROLES), 
     'guest_toddler_job_and_role_state':TunableSituationJobAndRoleState(description='\n            The job and role state of toddler who gets invited for Play Date.\n            ',
       tuning_group=GroupNames.ROLES), 
     'guest_parent_job_and_role_state':TunableSituationJobAndRoleState(description='\n            The job and role state of parent who gets invited for Play Date.\n            ',
       tuning_group=GroupNames.ROLES), 
     '_play_date_state':_PlayDateState.TunableFactory(description='\n            The state where Sims will play and take care the toddler.\n            ',
       display_name='1. PlayDate State',
       tuning_group=GroupNames.STATE), 
     '_leave_state':_LeaveState.TunableFactory(description='\n            The state where the Sims are done playing and about to leave\n            the lot. Parent will carry their toddler before leaving the lot.\n            ',
       display_name='2. Leave State',
       tuning_group=GroupNames.STATE)}

    def __init__(self, seed, *args, **kwargs):
        self._add_host_toddler_to_guest_list(seed)
        (super().__init__)(seed, *args, **kwargs)

    @classmethod
    def _states(cls):
        return (SituationStateData(1, _PlayDateState, factory=(cls._play_date_state)),
         SituationStateData(2, _LeaveState, factory=(cls._leave_state)))

    @classmethod
    def default_job(cls):
        pass

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.host_toddler_job_and_role_state.job, cls.host_toddler_job_and_role_state.role_state),
         (
          cls.host_parent_job_and_role_state.job, cls.host_parent_job_and_role_state.role_state),
         (
          cls.guest_toddler_job_and_role_state.job, cls.guest_toddler_job_and_role_state.role_state),
         (
          cls.guest_parent_job_and_role_state.job, cls.guest_parent_job_and_role_state.role_state)]

    @classmethod
    def get_possible_zone_ids_for_situation(cls, host_sim_info=None, guest_ids=None):
        possible_zones = []
        venue_manager = services.get_instance_manager(sims4.resources.Types.VENUE)
        venue_service = services.current_zone().venue_service
        for venue_tuning in cls.compatible_venues:
            if venue_tuning.is_residential:
                if host_sim_info is not None:
                    home_zone_id = host_sim_info.household.home_zone_id
                    home_venue_tuning = venue_manager.get(build_buy.get_current_venue(home_zone_id))
                    if home_venue_tuning.is_residential:
                        possible_zones.append(home_zone_id)
            else:
                possible_zones.extend(venue_service.get_zones_for_venue_type_gen(venue_tuning))

        return possible_zones

    def start_situation(self):
        super().start_situation()
        self._change_state(self._play_date_state())

    def _add_host_toddler_to_guest_list(self, seed):
        host_sim = seed.guest_list.host_sim
        if host_sim is None:
            return
        if host_sim.sim_info.lives_here:
            for sim_info in host_sim.household.sim_info_gen():
                if sim_info.is_toddler and seed.guest_list.get_guest_info_for_sim(sim_info) is None:
                    guest_info = SituationGuestInfo.construct_from_purpose(sim_info.sim_id, self.host_toddler_job_and_role_state.job, SituationInvitationPurpose.HOSTING)
                    seed.guest_list.add_guest_info(guest_info)

    @classmethod
    def _add_guest_parent_to_guest_list--- This code section failed: ---

 L. 148         0  LOAD_GLOBAL              services
                2  LOAD_METHOD              sim_info_manager
                4  CALL_METHOD_0         0  '0 positional arguments'
                6  STORE_DEREF              'm'

 L. 149         8  LOAD_CLOSURE             'm'
               10  BUILD_TUPLE_1         1 
               12  LOAD_SETCOMP             '<code_object <setcomp>>'
               14  LOAD_STR                 'ToddlerPlayDateSituation._add_guest_parent_to_guest_list.<locals>.<setcomp>'
               16  MAKE_FUNCTION_8          'closure'
               18  LOAD_FAST                'guest_list'
               20  LOAD_METHOD              get_guest_infos_for_job
               22  LOAD_FAST                'cls'
               24  LOAD_ATTR                guest_toddler_job_and_role_state
               26  LOAD_ATTR                job
               28  CALL_METHOD_1         1  '1 positional argument'
               30  GET_ITER         
               32  CALL_FUNCTION_1       1  '1 positional argument'
               34  STORE_FAST               'households'

 L. 152        36  SETUP_LOOP          124  'to 124'
               38  LOAD_FAST                'households'
               40  GET_ITER         
               42  FOR_ITER            122  'to 122'
               44  STORE_FAST               'household'

 L. 153        46  SETUP_LOOP          120  'to 120'
               48  LOAD_FAST                'household'
               50  LOAD_METHOD              sim_info_gen
               52  CALL_METHOD_0         0  '0 positional arguments'
               54  GET_ITER         
             56_0  COME_FROM            64  '64'
               56  FOR_ITER            102  'to 102'
               58  STORE_FAST               'sim_info'

 L. 154        60  LOAD_FAST                'sim_info'
               62  LOAD_ATTR                is_young_adult_or_older
               64  POP_JUMP_IF_FALSE    56  'to 56'

 L. 156        66  LOAD_GLOBAL              SituationGuestInfo
               68  LOAD_METHOD              construct_from_purpose
               70  LOAD_FAST                'sim_info'
               72  LOAD_ATTR                sim_id

 L. 157        74  LOAD_FAST                'cls'
               76  LOAD_ATTR                guest_parent_job_and_role_state
               78  LOAD_ATTR                job

 L. 158        80  LOAD_GLOBAL              SituationInvitationPurpose
               82  LOAD_ATTR                INVITED
               84  CALL_METHOD_3         3  '3 positional arguments'
               86  STORE_FAST               'guest_info'

 L. 159        88  LOAD_FAST                'guest_list'
               90  LOAD_METHOD              add_guest_info
               92  LOAD_FAST                'guest_info'
               94  CALL_METHOD_1         1  '1 positional argument'
               96  POP_TOP          

 L. 160        98  BREAK_LOOP       
              100  JUMP_BACK            56  'to 56'
              102  POP_BLOCK        

 L. 163       104  LOAD_GLOBAL              logger
              106  LOAD_ATTR                error
              108  LOAD_STR                 'Failed to find young adult or older Sim in household {}.'
              110  LOAD_FAST                'household'
              112  LOAD_STR                 'mkartika'
              114  LOAD_CONST               ('owner',)
              116  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              118  POP_TOP          
            120_0  COME_FROM_LOOP       46  '46'
              120  JUMP_BACK            42  'to 42'
              122  POP_BLOCK        
            124_0  COME_FROM_LOOP       36  '36'

Parse error at or near `LOAD_SETCOMP' instruction at offset 12

    @classmethod
    def get_extended_guest_list(cls, guest_list=None):
        if guest_list is None:
            return
        cls._add_guest_parent_to_guest_list(guest_list)
        return guest_list


lock_instance_tunables(ToddlerPlayDateSituation, exclusivity=(BouncerExclusivityCategory.NORMAL))