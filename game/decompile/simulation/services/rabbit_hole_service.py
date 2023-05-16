# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\services\rabbit_hole_service.py
# Compiled at: 2021-05-11 16:16:57
# Size of source mod 2**32: 42990 bytes
from event_testing.resolver import SingleSimResolver
from interactions.interaction_finisher import FinishingType
from protocolbuffers import GameplaySaveData_pb2
from distributor.rollback import ProtocolBufferRollback
from event_testing.test_events import TestEvent
from filters.sim_filter_service import SimFilterGlobalBlacklistReason
from interactions.context import InteractionContext, QueueInsertStrategy
from interactions.priority import Priority
from interactions.utils.exit_condition_manager import ConditionalActionManager
from objects import ALL_HIDDEN_REASONS
from rabbit_hole.rabbit_hole import RabbitHolePhase, RabbitHoleTimingPolicy
from sims.sim_spawner import SimSpawner
from sims4.service_manager import Service
from sims4.tuning.tunable import TunablePackSafeReference, TunableReference
from sims4.utils import classproperty
import persistence_error_types, services, sims4
logger = sims4.log.Logger('Rabbit Hole Service', default_owner='rrodgers')
NUM_MAX_RABBIT_HOLES = 10

class RabbitHoleService(Service):
    LEAVE_EARLY_INTERACTION = TunableReference(description='\n        The interaction that causes a sim to leave their rabbit hole early\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
      class_restrictions='RabbitHoleLeaveEarlyInteraction')
    FAMILIAR_RABBIT_HOLE = TunablePackSafeReference(description='\n        A special rabbit hole that is used by familiars when their master is also put into a rabbit hole.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.RABBIT_HOLE)))
    GENERIC_GO_HOME_AND_ATTEND = TunableReference(description=' \n        An interaction that will be used to travel sims who need to rabbit hole\n        at their home zone.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)))

    def __init__(self):
        self._rabbit_holes = {}
        self._conditional_actions_manager = ConditionalActionManager()

    def put_sim_in_managed_rabbithole(self, sim_info, rabbit_hole_type=None, rabbit_hole_id=None, **rabbit_hole_kwargs):
        sim_id = sim_info.id
        rabbit_hole = None
        if rabbit_hole_id is not None:
            rabbit_hole = self._get_rabbit_hole(sim_id, rabbit_hole_id)
            if rabbit_hole is None:
                logger.error('put_sim_in_managed_rabbithole called on rabbit hole {} of type {} for sim {} but no such rabbit hole exists', rabbit_hole_id, rabbit_hole_type, sim_info)
                return
            else:
                if sim_info.id in self._rabbit_holes:
                    if len(self._rabbit_holes[sim_id]) >= NUM_MAX_RABBIT_HOLES:
                        logger.error('Tried to put the sim {} in a managed rabbit hole of type {}, but they already had too many rabbit hole requests! Stopping extra requests', sim_info.id, rabbit_hole_type)
                        return
                    rabbit_hole = rabbit_hole_type(sim_id, starting_phase=RabbitHolePhase.QUEUED, **rabbit_hole_kwargs)
                    self._rabbit_holes[sim_id].append(rabbit_hole)
                else:
                    rabbit_hole = rabbit_hole_type(sim_id, **rabbit_hole_kwargs)
                    self._rabbit_holes[sim_id] = [rabbit_hole]
            result = True
            rabbit_hole_id = rabbit_hole.rabbit_hole_id
            is_starting = rabbit_hole.current_phase == RabbitHolePhase.STARTING
            if rabbit_hole is not self._rabbit_holes[sim_id][0]:
                result = self._setup_queued(sim_id, rabbit_hole_id)
            else:
                if sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS):
                    if rabbit_hole.select_affordance() is not None:
                        result = self._setup_instantiated_no_travel(sim_id, rabbit_hole_id)
                else:
                    result = self._setup_instantiated_travel(sim_id, rabbit_hole_id)
        else:
            if sim_info.is_at_home or sim_info.should_send_home_to_rabbit_hole():
                result = self._setup_uninstantiated_no_travel(sim_id, rabbit_hole_id)
            else:
                if rabbit_hole.current_phase is RabbitHolePhase.STARTING:
                    result = self._setup_uninstantiated_travel(sim_id, rabbit_hole_id)
                else:
                    if result:
                        if is_starting:
                            result = self._setup_linked_rabbit_holes(sim_id, rabbit_hole_id)
                    result or self.remove_sim_from_rabbit_hole(sim_id, rabbit_hole_id, canceled=True)
                    return
                return rabbit_hole_id

    def try_remove_sim_from_rabbit_hole(self, sim_id, rabbit_hole_id, callback=None):
        sim_info = services.sim_info_manager().get(sim_id)
        sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        rabbit_hole = self._get_rabbit_hole(sim_id, rabbit_hole_id)
        if sim is not None and rabbit_hole is not None:
            affordance = rabbit_hole.select_affordance()
            cancel_result = False
            if affordance:
                interaction = sim.find_interaction_by_affordance(affordance)
                if callback is not None:
                    binded_callback = lambda *_, **__: callback(True)
                    interaction.add_exit_function(binded_callback)
                cancel_result = interaction.cancel_user(cancel_reason_msg='Interaction canceled by the rabbit hole service')
                if not cancel_result:
                    if callback is not None:
                        callback(False)
        elif rabbit_hole is not None:
            self.remove_sim_from_rabbit_hole(sim_id, rabbit_hole_id, canceled=True)
            if callback is not None:
                callback(True)

    def remove_sim_from_rabbit_hole(self, sim_id, rabbit_hole_id, canceled=False):
        rabbit_hole = self._get_rabbit_hole(sim_id, rabbit_hole_id)
        if rabbit_hole is None:
            return
        self._rabbit_holes[sim_id].remove(rabbit_hole)
        if rabbit_hole.current_phase is RabbitHolePhase.QUEUED:
            rabbit_hole.on_remove(canceled=canceled)
            return
        if len(self._rabbit_holes[sim_id]) == 0:
            del self._rabbit_holes[sim_id]
        else:
            sim_info = services.sim_info_manager().get(sim_id)
            if sim_info is None:
                return
            sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if sim is not None:
                affordance = rabbit_hole.select_affordance()
                interaction = sim.find_interaction_by_affordance(affordance)
                if interaction is not None:
                    if canceled and sim_info.is_selectable:
                        interaction.cancel_user(cancel_reason_msg='Interaction canceled by the rabbit hole service')
                    else:
                        interaction.cancel((FinishingType.NATURAL), cancel_reason_msg='Interaction canceled by the rabbit hole service')
        if not canceled:
            resolver = SingleSimResolver(sim_info)
            for loot_action in rabbit_hole.loot_list:
                loot_action.apply_to_resolver(resolver)

        rabbit_hole.on_remove(canceled=canceled)
        sim_filter_service = services.sim_filter_service()
        if sim_id in sim_filter_service.get_global_blacklist():
            sim_filter_service.remove_sim_id_from_global_blacklist(sim_id, SimFilterGlobalBlacklistReason.RABBIT_HOLE)
        self._conditional_actions_manager.detach_conditions(rabbit_hole)
        if rabbit_hole.away_action is not None:
            if sim_info.away_action_tracker is not None:
                sim_info.away_action_tracker.reset_to_default_away_action()
        for linked_sim_id, linked_rabbithole_id in rabbit_hole.linked_rabbit_holes:
            self.remove_sim_from_rabbit_hole(linked_sim_id, linked_rabbithole_id, canceled=canceled)

        if sim_id not in self._rabbit_holes:
            return
        for next_rabbit_hole in tuple(self._rabbit_holes[sim_id]):
            if not next_rabbit_hole.is_valid_to_restore(sim_info):
                self.remove_sim_from_rabbit_hole(sim_id, next_rabbit_hole.rabbit_hole_id)

    def get_rabbit_hole_id_by_type(self, sim_id, rabbit_hole_type):
        if sim_id not in self._rabbit_holes:
            return
        return next((rh for rh in self._rabbit_holes[sim_id] if type(rh) is rabbit_hole_type), None)

    def get_head_rabbit_hole_id(self, sim_id):
        if sim_id in self._rabbit_holes:
            return self._rabbit_holes[sim_id][0].rabbit_hole_id

    def set_rabbit_hole_expiration_callback(self, sim_id, rabbit_hole_id, callback):
        rabbit_hole = self._get_rabbit_hole(sim_id, rabbit_hole_id)
        if rabbit_hole is not None:
            rabbit_hole.callbacks.register(callback)
        else:
            logger.error('Failed to setup rabbit hole with id {} for sim id {}', callback, rabbit_hole_id, sim_id)

    def remove_rabbit_hole_expiration_callback(self, sim_id, rabbit_hole_id, callback):
        rabbit_hole = self._get_rabbit_hole(sim_id, rabbit_hole_id)
        if rabbit_hole is not None:
            rabbit_hole.callbacks.unregister(callback)
        else:
            logger.error('Trying to remove a callback: {} that does not exist for sim: {} in rabbit hole service.', callback, sim_id)
            return

    def set_ignore_travel_cancel_for_sim_id_in_rabbit_hole(self, sim_id):
        self._rabbit_holes[sim_id][0].ignore_travel_cancel_callbacks = True

    def should_override_selector_visual_type(self, sim_id):
        if sim_id in self._rabbit_holes:
            if self._rabbit_holes[sim_id][0].is_active():
                return True
        return False

    def is_head_rabbit_hole_user_cancelable(self, sim_id):
        return self._rabbit_holes[sim_id][0].select_affordance().never_user_cancelable

    def will_override_spin_up_action(self, sim_id):
        return sim_id in self._rabbit_holes

    def get_time_for_head_rabbit_hole(self, sim_id):
        if sim_id in self._rabbit_holes:
            rabbit_hole = self._rabbit_holes[sim_id][0]
            alarm_handle = rabbit_hole.alarm_handle
            if alarm_handle is None:
                return rabbit_hole.time_remaining_on_load
            return alarm_handle.get_remaining_time()

    def is_in_rabbit_hole(self, sim_id, rabbit_hole_id=None):
        if rabbit_hole_id is None:
            return sim_id in self._rabbit_holes
        return self._get_rabbit_hole(sim_id, rabbit_hole_id)

    def get_head_rabbit_hole_home_interaction_name(self, sim_id, target=None, context=None, **interaction_parameters):
        if sim_id not in self._rabbit_holes:
            return
        rabbit_hole = self._rabbit_holes[sim_id][0]
        if context is None:
            sim = services.sim_info_manager().get(sim_id).get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            context = InteractionContext(sim, InteractionContext.SOURCE_SCRIPT, Priority.High)
        return (rabbit_hole.affordance.get_name)(target=target, context=context, **interaction_parameters)

    def get_head_rabbit_hole_home_interaction_icon(self, sim_id, target=None, context=None):
        if sim_id not in self._rabbit_holes:
            return
        rabbit_hole = self._rabbit_holes[sim_id][0]
        if context is None:
            sim = services.sim_info_manager().get(sim_id).get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            context = InteractionContext(sim, InteractionContext.SOURCE_SCRIPT, Priority.High)
        return rabbit_hole.affordance.get_icon_info(target=target, context=context)

    def sim_skewer_rabbit_hole_affordances_gen(self, sim_info, context, **kwargs):
        for aop in (self.LEAVE_EARLY_INTERACTION.potential_interactions)(None,
 context, sim_info=sim_info, **kwargs):
            yield aop

    def _get_rabbit_hole(self, sim_id, rabbit_hole_id):
        if sim_id in self._rabbit_holes:
            matching_rabbit_hole = next((rh for rh in self._rabbit_holes[sim_id] if rh.rabbit_hole_id == rabbit_hole_id), None)
            if matching_rabbit_hole is not None:
                return matching_rabbit_hole

    def _setup_linked_rabbit_holes(self, sim_id, rabbit_hole_id):
        rabbit_hole = self._get_rabbit_hole(sim_id, rabbit_hole_id)
        familiar_tracker = services.sim_info_manager().get(sim_id).familiar_tracker
        if familiar_tracker is not None:
            familiar = familiar_tracker.get_active_familiar()
            if familiar is not None:
                if familiar.is_sim:
                    linked_rabbit_hole_id = self.put_sim_in_managed_rabbithole(familiar.sim_info, RabbitHoleService.FAMILIAR_RABBIT_HOLE)
                    if linked_rabbit_hole_id is None:
                        return False
                    rabbit_hole.linked_rabbit_holes.append((familiar.sim_id, linked_rabbit_hole_id))
        return True

    def _setup_queued--- This code section failed: ---

 L. 499         0  LOAD_DEREF               'self'
                2  LOAD_METHOD              _get_rabbit_hole
                4  LOAD_FAST                'sim_id'
                6  LOAD_DEREF               'rabbit_hole_id'
                8  CALL_METHOD_2         2  '2 positional arguments'
               10  STORE_FAST               'rabbit_hole'

 L. 500        12  LOAD_GLOBAL              RabbitHolePhase
               14  LOAD_ATTR                QUEUED
               16  LOAD_FAST                'rabbit_hole'
               18  STORE_ATTR               current_phase

 L. 502        20  LOAD_FAST                'rabbit_hole'
               22  LOAD_ATTR                time_tracking_policy
               24  LOAD_GLOBAL              RabbitHoleTimingPolicy
               26  LOAD_ATTR                COUNT_ALL_TIME
               28  COMPARE_OP               ==
               30  POP_JUMP_IF_FALSE    60  'to 60'

 L. 503        32  LOAD_FAST                'sim_id'
               34  BUILD_TUPLE_1         1 
               36  LOAD_CLOSURE             'rabbit_hole_id'
               38  LOAD_CLOSURE             'self'
               40  BUILD_TUPLE_2         2 
               42  LOAD_LAMBDA              '<code_object <lambda>>'
               44  LOAD_STR                 'RabbitHoleService._setup_queued.<locals>.<lambda>'
               46  MAKE_FUNCTION_9          'default, closure'
               48  STORE_FAST               'time_expired_callback'

 L. 504        50  LOAD_FAST                'rabbit_hole'
               52  LOAD_METHOD              set_expiration_alarm
               54  LOAD_FAST                'time_expired_callback'
               56  CALL_METHOD_1         1  '1 positional argument'
               58  POP_TOP          
             60_0  COME_FROM            30  '30'

 L. 505        60  LOAD_CONST               True
               62  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `MAKE_FUNCTION_9' instruction at offset 46

    def _setup_instantiated_no_travel(self, sim_id, rabbit_hole_id):
        rabbit_hole = self._get_rabbit_hole(sim_id, rabbit_hole_id)
        affordance = rabbit_hole.select_affordance()
        if rabbit_hole.is_active():
            sim_info = services.sim_info_manager().get(sim_id)
            sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            sim.set_allow_route_instantly_when_hitting_marks(True)
            services.sim_info_manager().set_sim_to_skip_preroll(sim_id)
            if rabbit_hole.current_phase == RabbitHolePhase.ACTIVE_PERSISTED:
                services.get_event_manager().register_with_custom_key(self, TestEvent.InteractionStart, affordance)
            else:
                rabbit_hole.current_phase = RabbitHolePhase.TRANSITIONING
                services.get_event_manager().register_with_custom_key(self, TestEvent.InteractionStart, affordance)
        else:
            result = self._push_affordance_with_cancel_callback(sim_id, rabbit_hole_id, affordance, picked_skill=(rabbit_hole.picked_skill))
            return result or False
        return True

    def _setup_instantiated_travel(self, sim_id, rabbit_hole_id):
        rabbit_hole = self._get_rabbit_hole(sim_id, rabbit_hole_id)
        rabbit_hole.current_phase = RabbitHolePhase.TRAVELING
        affordance = rabbit_hole.select_travel_affordance() or self.GENERIC_GO_HOME_AND_ATTEND
        result = self._push_affordance_with_cancel_callback(sim_id, rabbit_hole_id, affordance, picked_skill=(rabbit_hole.picked_skill))
        if not result:
            return False

        def _on_travel_finished(interaction, sim_id=sim_id, rabbit_hole_id=rabbit_hole_id):
            if not interaction.is_finishing_naturally:
                self._on_cancel(interaction, sim_id=sim_id, rabbit_hole_id=rabbit_hole_id)
            else:
                if not self.is_in_rabbit_hole(sim_id, rabbit_hole_id):
                    return
                sim_info = services.sim_info_manager().get(sim_id)
                home_zone_id = sim_info.is_at_home or sim_info.household.home_zone_id
                sim_info.inject_into_inactive_zone(home_zone_id, skip_instanced_check=True)
            self._activate_rabbit_hole(sim_id, rabbit_hole_id)

        result.interaction.register_on_finishing_callback(_on_travel_finished)
        return True

    def _setup_uninstantiated_no_travel(self, sim_id, rabbit_hole_id):
        self._activate_rabbit_hole(sim_id, rabbit_hole_id)
        return True

    def _setup_uninstantiated_travel(self, sim_id, rabbit_hole_id):
        sim_info = services.sim_info_manager().get(sim_id)
        home_zone_id = sim_info.household.home_zone_id
        if services.current_zone_id() != home_zone_id:
            sim_info.inject_into_inactive_zone(home_zone_id)
            return self._setup_uninstantiated_no_travel(sim_id, rabbit_hole_id)
        return SimSpawner.spawn_sim(sim_info, spawn_action=(lambda _: self._setup_instantiated_no_travel(sim_info.id, rabbit_hole_id)), update_skewer=False)

    def _activate_rabbit_hole--- This code section failed: ---

 L. 610         0  LOAD_DEREF               'self'
                2  LOAD_METHOD              _get_rabbit_hole
                4  LOAD_FAST                'sim_id'
                6  LOAD_DEREF               'rabbit_hole_id'
                8  CALL_METHOD_2         2  '2 positional arguments'
               10  STORE_FAST               'rabbit_hole'

 L. 614        12  LOAD_FAST                'rabbit_hole'
               14  LOAD_ATTR                current_phase
               16  LOAD_GLOBAL              RabbitHolePhase
               18  LOAD_ATTR                ACTIVE
               20  COMPARE_OP               ==
               22  POP_JUMP_IF_FALSE    28  'to 28'

 L. 615        24  LOAD_CONST               None
               26  RETURN_VALUE     
             28_0  COME_FROM            22  '22'

 L. 617        28  LOAD_GLOBAL              RabbitHolePhase
               30  LOAD_ATTR                ACTIVE
               32  LOAD_FAST                'rabbit_hole'
               34  STORE_ATTR               current_phase

 L. 618        36  LOAD_GLOBAL              services
               38  LOAD_METHOD              sim_info_manager
               40  CALL_METHOD_0         0  '0 positional arguments'
               42  LOAD_METHOD              get
               44  LOAD_FAST                'sim_id'
               46  CALL_METHOD_1         1  '1 positional argument'
               48  STORE_FAST               'sim_info'

 L. 620        50  LOAD_FAST                'rabbit_hole'
               52  LOAD_METHOD              on_activate
               54  CALL_METHOD_0         0  '0 positional arguments'
               56  POP_TOP          

 L. 623        58  LOAD_GLOBAL              services
               60  LOAD_METHOD              sim_filter_service
               62  CALL_METHOD_0         0  '0 positional arguments'
               64  STORE_FAST               'sim_filter_service'

 L. 624        66  LOAD_FAST                'sim_filter_service'
               68  LOAD_METHOD              add_sim_id_to_global_blacklist
               70  LOAD_FAST                'sim_id'
               72  LOAD_GLOBAL              SimFilterGlobalBlacklistReason
               74  LOAD_ATTR                RABBIT_HOLE
               76  CALL_METHOD_2         2  '2 positional arguments'
               78  POP_TOP          

 L. 627        80  LOAD_FAST                'sim_id'
               82  BUILD_TUPLE_1         1 
               84  LOAD_CLOSURE             'rabbit_hole_id'
               86  LOAD_CLOSURE             'self'
               88  BUILD_TUPLE_2         2 
               90  LOAD_LAMBDA              '<code_object <lambda>>'
               92  LOAD_STR                 'RabbitHoleService._activate_rabbit_hole.<locals>.<lambda>'
               94  MAKE_FUNCTION_9          'default, closure'
               96  STORE_FAST               'exit_condition_callback'

 L. 628        98  LOAD_GLOBAL              SingleSimResolver
              100  LOAD_FAST                'sim_info'
              102  CALL_FUNCTION_1       1  '1 positional argument'
              104  STORE_DEREF              'exit_condition_test_resolver'

 L. 629       106  LOAD_CLOSURE             'exit_condition_test_resolver'
              108  BUILD_TUPLE_1         1 
              110  LOAD_GENEXPR             '<code_object <genexpr>>'
              112  LOAD_STR                 'RabbitHoleService._activate_rabbit_hole.<locals>.<genexpr>'
              114  MAKE_FUNCTION_8          'closure'
              116  LOAD_FAST                'rabbit_hole'
              118  LOAD_ATTR                exit_conditions
              120  GET_ITER         
              122  CALL_FUNCTION_1       1  '1 positional argument'
              124  STORE_FAST               'exit_conditions'

 L. 630       126  LOAD_FAST                'exit_conditions'
              128  POP_JUMP_IF_FALSE   146  'to 146'

 L. 631       130  LOAD_DEREF               'self'
              132  LOAD_ATTR                _conditional_actions_manager
              134  LOAD_METHOD              attach_conditions
              136  LOAD_FAST                'rabbit_hole'

 L. 632       138  LOAD_FAST                'exit_conditions'

 L. 633       140  LOAD_FAST                'exit_condition_callback'
              142  CALL_METHOD_3         3  '3 positional arguments'
              144  POP_TOP          
            146_0  COME_FROM           128  '128'

 L. 635       146  LOAD_FAST                'rabbit_hole'
              148  LOAD_ATTR                time_tracking_policy
              150  LOAD_GLOBAL              RabbitHoleTimingPolicy
              152  LOAD_ATTR                NO_TIME_LIMIT
              154  COMPARE_OP               is-not
              156  POP_JUMP_IF_FALSE   186  'to 186'

 L. 642       158  LOAD_FAST                'sim_id'
              160  BUILD_TUPLE_1         1 
              162  LOAD_CLOSURE             'rabbit_hole_id'
              164  LOAD_CLOSURE             'self'
              166  BUILD_TUPLE_2         2 
              168  LOAD_LAMBDA              '<code_object <lambda>>'
              170  LOAD_STR                 'RabbitHoleService._activate_rabbit_hole.<locals>.<lambda>'
              172  MAKE_FUNCTION_9          'default, closure'
              174  STORE_FAST               'time_expired_callback'

 L. 643       176  LOAD_FAST                'rabbit_hole'
              178  LOAD_METHOD              set_expiration_alarm
              180  LOAD_FAST                'time_expired_callback'
              182  CALL_METHOD_1         1  '1 positional argument'
              184  POP_TOP          
            186_0  COME_FROM           156  '156'

 L. 646       186  LOAD_FAST                'rabbit_hole'
              188  LOAD_ATTR                away_action
              190  LOAD_CONST               None
              192  COMPARE_OP               is-not
              194  POP_JUMP_IF_FALSE   220  'to 220'
              196  LOAD_FAST                'sim_info'
              198  LOAD_ATTR                away_action_tracker
              200  LOAD_CONST               None
              202  COMPARE_OP               is-not
              204  POP_JUMP_IF_FALSE   220  'to 220'

 L. 647       206  LOAD_FAST                'sim_info'
              208  LOAD_ATTR                away_action_tracker
              210  LOAD_METHOD              create_and_apply_away_action
              212  LOAD_FAST                'rabbit_hole'
              214  LOAD_ATTR                away_action
              216  CALL_METHOD_1         1  '1 positional argument'
              218  POP_TOP          
            220_0  COME_FROM           204  '204'
            220_1  COME_FROM           194  '194'

Parse error at or near `MAKE_FUNCTION_9' instruction at offset 94

    def _on_cancel(self, interaction, sim_id=None, rabbit_hole_id=None):
        if services.current_zone().is_zone_shutting_down:
            return
        else:
            if not self.is_in_rabbit_hole(sim_id, rabbit_hole_id):
                return
            rabbit_hole = self._get_rabbit_hole(sim_id, rabbit_hole_id)
            if rabbit_hole is None:
                return
            if interaction.affordance is self.GENERIC_GO_HOME_AND_ATTEND or interaction.affordance is rabbit_hole.select_travel_affordance():
                if rabbit_hole.ignore_travel_cancel_callbacks:
                    return
        if interaction.is_finishing_naturally:
            return
        self.remove_sim_from_rabbit_hole(sim_id, rabbit_hole_id, canceled=True)

    def _push_affordance_with_cancel_callback(self, sim_id, rabbit_hole_id, affordance, picked_skill=None):
        sim = services.sim_info_manager().get(sim_id).get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        context = InteractionContext(sim, (InteractionContext.SOURCE_SCRIPT),
          (Priority.High),
          insert_strategy=(QueueInsertStrategy.NEXT))
        result = sim.push_super_affordance(affordance, sim, context, rabbit_hole_id=rabbit_hole_id, picked_statistic=picked_skill)
        if not result:
            return result
        cancel = lambda interaction: self._on_cancel(interaction, sim_id=sim_id, rabbit_hole_id=rabbit_hole_id)
        result.interaction.register_on_cancelled_callback(cancel)
        return result

    def restore_rabbit_hole_state(self):
        sim_info_manager = services.sim_info_manager()
        rabbit_holes_with_linked_master = []
        rabbit_holes_to_cancel = []
        for sim_id, rabbit_holes in self._rabbit_holes.copy().items():
            sim_info = sim_info_manager.get(sim_id)
            if sim_info is None:
                for rabbit_hole in list(rabbit_holes):
                    self.remove_sim_from_rabbit_hole(sim_id, (rabbit_hole.rabbit_hole_id), canceled=True)

                continue
            for rabbit_hole in list(rabbit_holes):
                if not rabbit_hole.is_valid_to_restore(sim_info):
                    rabbit_holes_to_cancel.append((sim_id, rabbit_hole.rabbit_hole_id))
                    logger.error('Rabbit hole id:{} was not valid to be restored for sim {}.  \n Please note any changes were done prior to save.', rabbit_hole.guid64, sim_info)
                    continue
                rabbit_hole.on_restore()
                self.put_sim_in_managed_rabbithole(sim_info, rabbit_hole_id=(rabbit_hole.rabbit_hole_id))
                rabbit_holes_with_linked_master.extend(rabbit_hole.linked_rabbit_holes)

        for sim_id, rabbit_holes in self._rabbit_holes.items():
            for rabbit_hole in rabbit_holes:
                if self.FAMILIAR_RABBIT_HOLE is not None and rabbit_hole.guid64 == self.FAMILIAR_RABBIT_HOLE.guid64 and rabbit_hole.rabbit_hole_id not in rabbit_holes_with_linked_master:
                    rabbit_holes_to_cancel.append((sim_id, rabbit_hole.rabbit_hole_id))

        for sim_id, rabbit_hole_id in rabbit_holes_to_cancel:
            self.remove_sim_from_rabbit_hole(sim_id, rabbit_hole_id, canceled=True)

    def save(self, save_slot_data=None, **kwargs):
        rabbit_hole_service_proto = GameplaySaveData_pb2.PersistableRabbitHoleService()
        for sim_id, rabbit_holes in self._rabbit_holes.items():
            for rabbit_hole in rabbit_holes:
                with ProtocolBufferRollback(rabbit_hole_service_proto.rabbit_holes) as (entry):
                    entry.sim_id = sim_id
                    entry.rabbit_hole_id = rabbit_hole.guid64
                    entry.rabbit_hole_instance_id = rabbit_hole.rabbit_hole_id
                    rabbit_hole.save(entry)
                    if rabbit_hole.linked_rabbit_holes:
                        linked_sim_ids, linked_rabbit_hole_ids = zip(*rabbit_hole.linked_rabbit_holes)
                        entry.linked_sim_ids.extend(linked_sim_ids)
                        entry.linked_rabbit_hole_ids.extend(linked_rabbit_hole_ids)

        save_slot_data.gameplay_data.rabbit_hole_service = rabbit_hole_service_proto

    def load(self, **_):
        save_slot_data = services.get_persistence_service().get_save_slot_proto_buff()
        rabbit_holes_to_fixup_links = []
        for entry in save_slot_data.gameplay_data.rabbit_hole_service.rabbit_holes:
            rabbit_hole_type = services.get_instance_manager(sims4.resources.Types.RABBIT_HOLE).get(entry.rabbit_hole_id)
            if rabbit_hole_type is None:
                continue
            sim_id = entry.sim_id
            rabbit_hole_instance_id = None
            if entry.HasField('rabbit_hole_instance_id'):
                rabbit_hole_instance_id = entry.rabbit_hole_instance_id
            if sim_id not in self._rabbit_holes:
                self._rabbit_holes[sim_id] = []
            if len(self._rabbit_holes[sim_id]) >= NUM_MAX_RABBIT_HOLES:
                logger.error('Attempted to load rabbit holes for sim {}, but there too many rabbit hole requests! Stopping extra requests', sim_id)
                continue
            rabbit_hole = rabbit_hole_type(sim_id, rabbit_hole_id=rabbit_hole_instance_id)
            self._rabbit_holes[sim_id].append(rabbit_hole)
            rabbit_hole.load(entry)
            if entry.linked_sim_ids:
                if entry.linked_rabbit_hole_ids:
                    rabbit_hole.linked_rabbit_holes.extend(zip(entry.linked_sim_ids, entry.linked_rabbit_hole_ids))
                else:
                    rabbit_hole.linked_rabbit_holes.extend(((linked_sim_id, None) for linked_sim_id in entry.linked_sim_ids))
                    rabbit_holes_to_fixup_links = (sim_id, rabbit_hole.rabbit_hole_id)

        for sim_id, rabbit_hole_id in rabbit_holes_to_fixup_links:
            rabbit_hole = self._get_rabbit_hole(sim_id, rabbit_hole_id)
            new_linked_rabbit_holes = []
            for linked_sim_id, _ in rabbit_hole.linked_rabbit_holes:
                linked_rabbit_hole = self._rabbit_holes.get(linked_sim_id, None)
                if linked_rabbit_hole is not None:
                    new_linked_rabbit_holes.append((linked_sim_id, linked_rabbit_hole.rabbit_hole_id))

            rabbit_hole.linked_rabbit_holes = new_linked_rabbit_holes

    def start(self):
        services.get_event_manager().register_single_event(self, TestEvent.OnSimReset)

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_RABBIT_HOLE_SERVICE

    def handle_event(self, sim_info, event, *_):
        sim_id = sim_info.id
        if event == TestEvent.OnSimReset:
            if sim_id in self._rabbit_holes:
                rabbit_hole_id = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS).is_being_destroyed or self.get_head_rabbit_hole_id(sim_id)
                self.remove_sim_from_rabbit_hole(sim_id, rabbit_hole_id, canceled=True)
        elif event == TestEvent.InteractionStart:
            if sim_id in self._rabbit_holes:
                rabbit_hole_id = self.get_head_rabbit_hole_id(sim_id)
                self._activate_rabbit_hole(sim_id, rabbit_hole_id)