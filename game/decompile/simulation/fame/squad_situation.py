# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\fame\squad_situation.py
# Compiled at: 2018-10-08 18:45:16
# Size of source mod 2**32: 6274 bytes
from interactions.context import InteractionContext, QueueInsertStrategy
from sims.outfits.outfit_enums import OutfitCategory, BodyTypeFlag
from sims4.tuning.tunable import TunableReference
from situations.base_situation import _RequestUserData
from situations.bouncer.bouncer_request import BouncerRequest
from situations.bouncer.bouncer_types import BouncerRequestPriority
from situations.situation import Situation
from situations.situation_complex import SituationComplexCommon, CommonSituationState, SituationStateData
import interactions.priority, services, sims4.resources

class _BeInSquadState(CommonSituationState):
    pass


class SquadSituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'_be_in_squad_state':_BeInSquadState.TunableFactory(description='\n            The situation state used for sims in this situation.\n            ',
       tuning_group=SituationComplexCommon.SITUATION_STATE_GROUP,
       display_name='01_be_in_squad_state'), 
     'leader_job':TunableReference(description='\n            The job that the leader will have. This will be used to identify\n            the leader.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)), 
     'squad_member_job':TunableReference(description='\n            The job that each member of the squad will get when they are added\n            to this situation.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)), 
     'ensemble_type':TunableReference(description='    \n            The type of ensemble you want the squad to start.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.ENSEMBLE))}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._ensemble = None

    @classmethod
    def _states(cls):
        return [SituationStateData(1, _BeInSquadState, factory=(cls._be_in_squad_state))]

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return list(cls._be_in_squad_state._tuned_values.job_and_role_changes.items())

    @classmethod
    def default_job(cls):
        pass

    def start_situation(self):
        super().start_situation()
        self._change_state(self._be_in_squad_state())

    def _on_set_sim_job--- This code section failed: ---

 L.  79         0  LOAD_GLOBAL              super
                2  CALL_FUNCTION_0       0  '0 positional arguments'
                4  LOAD_METHOD              _on_set_sim_job
                6  LOAD_FAST                'sim'
                8  LOAD_FAST                'job_type'
               10  CALL_METHOD_2         2  '2 positional arguments'
               12  POP_TOP          

 L.  80        14  LOAD_FAST                'job_type'
               16  LOAD_FAST                'self'
               18  LOAD_ATTR                leader_job
               20  COMPARE_OP               is
               22  POP_JUMP_IF_FALSE    88  'to 88'

 L.  81        24  SETUP_LOOP          176  'to 176'
               26  LOAD_FAST                'sim'
               28  LOAD_ATTR                sim_info
               30  LOAD_ATTR                squad_members
               32  GET_ITER         
               34  FOR_ITER             84  'to 84'
               36  STORE_FAST               'sim_info_id'

 L.  82        38  LOAD_GLOBAL              BouncerRequest
               40  LOAD_FAST                'self'

 L.  83        42  LOAD_GLOBAL              _RequestUserData
               44  CALL_FUNCTION_0       0  '0 positional arguments'

 L.  84        46  LOAD_FAST                'sim_info_id'

 L.  85        48  LOAD_FAST                'self'
               50  LOAD_ATTR                squad_member_job

 L.  86        52  LOAD_GLOBAL              BouncerRequestPriority
               54  LOAD_ATTR                BACKGROUND_HIGH

 L.  87        56  LOAD_CONST               False

 L.  88        58  LOAD_FAST                'self'
               60  LOAD_ATTR                exclusivity
               62  LOAD_CONST               ('callback_data', 'requested_sim_id', 'job_type', 'request_priority', 'user_facing', 'exclusivity')
               64  CALL_FUNCTION_KW_7     7  '7 total positional and keyword args'
               66  STORE_FAST               'request'

 L.  90        68  LOAD_FAST                'self'
               70  LOAD_ATTR                manager
               72  LOAD_ATTR                bouncer
               74  LOAD_METHOD              submit_request
               76  LOAD_FAST                'request'
               78  CALL_METHOD_1         1  '1 positional argument'
               80  POP_TOP          
               82  JUMP_BACK            34  'to 34'
               84  POP_BLOCK        
               86  JUMP_FORWARD        176  'to 176'
             88_0  COME_FROM            22  '22'

 L.  92        88  LOAD_FAST                'self'
               90  LOAD_ATTR                _ensemble
               92  LOAD_CONST               None
               94  COMPARE_OP               is
               96  POP_JUMP_IF_FALSE   144  'to 144'

 L.  93        98  LOAD_GLOBAL              services
              100  LOAD_METHOD              ensemble_service
              102  CALL_METHOD_0         0  '0 positional arguments'
              104  LOAD_METHOD              create_ensemble
              106  LOAD_FAST                'self'
              108  LOAD_ATTR                ensemble_type

 L.  94       110  LOAD_FAST                'self'
              112  LOAD_ATTR                _situation_sims
              114  LOAD_METHOD              keys
              116  CALL_METHOD_0         0  '0 positional arguments'
              118  CALL_METHOD_2         2  '2 positional arguments'
              120  POP_TOP          

 L.  95       122  LOAD_GLOBAL              services
              124  LOAD_METHOD              ensemble_service
              126  CALL_METHOD_0         0  '0 positional arguments'
              128  LOAD_METHOD              get_ensemble_for_sim
              130  LOAD_FAST                'self'
              132  LOAD_ATTR                ensemble_type
              134  LOAD_FAST                'sim'
              136  CALL_METHOD_2         2  '2 positional arguments'
              138  LOAD_FAST                'self'
              140  STORE_ATTR               _ensemble
              142  JUMP_FORWARD        156  'to 156'
            144_0  COME_FROM            96  '96'

 L.  98       144  LOAD_FAST                'self'
              146  LOAD_ATTR                _ensemble
              148  LOAD_METHOD              add_sim_to_ensemble
              150  LOAD_FAST                'sim'
              152  CALL_METHOD_1         1  '1 positional argument'
              154  POP_TOP          
            156_0  COME_FROM           142  '142'

 L.  99       156  LOAD_FAST                'job_type'
              158  LOAD_ATTR                job_uniform
              160  LOAD_CONST               None
              162  COMPARE_OP               is
              164  POP_JUMP_IF_FALSE   176  'to 176'

 L. 100       166  LOAD_FAST                'self'
              168  LOAD_METHOD              _fixup_sims_outfit
              170  LOAD_FAST                'sim'
              172  CALL_METHOD_1         1  '1 positional argument'
              174  POP_TOP          
            176_0  COME_FROM           164  '164'
            176_1  COME_FROM            86  '86'
            176_2  COME_FROM_LOOP       24  '24'

Parse error at or near `COME_FROM' instruction at offset 176_1

    def _fixup_sims_outfit(self, sim):
        sim_info = sim.sim_info
        if sim_info.is_child_or_younger:
            return
        leader_sim_info = self.requesting_sim_info
        if sim_info.species != leader_sim_info.species or sim_info.clothing_preference_gender != leader_sim_info.clothing_preference_gender:
            return
        leader_current_outfit = leader_sim_info.get_current_outfit()
        if leader_current_outfit[0] == OutfitCategory.BATHING:
            leader_current_outfit = (
             OutfitCategory.EVERYDAY, 0)
        else:
            with leader_sim_info.set_temporary_outfit_flags(leader_current_outfit[0], leader_current_outfit[1], BodyTypeFlag.CLOTHING_ALL):
                sim_info.generate_merged_outfit(leader_sim_info, (OutfitCategory.SITUATION, 0), (sim_info.get_current_outfit()), leader_current_outfit, preserve_outfit_flags=True)
            if not self.manager.sim_being_created is sim:
                services.current_zone().is_zone_running or sim.set_current_outfit((OutfitCategory.SITUATION, 0))
            else:
                context = InteractionContext(sim, (InteractionContext.SOURCE_SCRIPT),
                  (interactions.priority.Priority.High),
                  insert_strategy=(QueueInsertStrategy.NEXT),
                  bucket=(interactions.context.InteractionBucketType.DEFAULT))
                sim.push_super_affordance(self.CHANGE_TO_SITUATION_OUTFIT, None, context)

    def on_remove(self):
        super().on_remove()
        if self._ensemble is not None:
            self._ensemble.end_ensemble()
            self._ensemble = None