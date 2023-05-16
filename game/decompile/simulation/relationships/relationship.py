# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relationships\relationship.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 77900 bytes
import itertools
from sims.global_gender_preference_tuning import GlobalGenderPreferenceTuning, GenderPreferenceType
import alarms, date_and_time, event_testing, services, sims4.log
from distributor.ops import GenericProtocolBufferOp
from distributor.rollback import ProtocolBufferRollback
from distributor.shared_messages import send_relationship_op, build_icon_info_msg, IconInfoData
from distributor.system import Distributor
from protocolbuffers import DistributorOps_pb2, Commodities_pb2 as commodity_protocol
from relationships import global_relationship_tuning
from relationships.compatibility_tuning import CompatibilityTuning
from relationships.global_relationship_tuning import RelationshipGlobalTuning
from relationships.relationship_bit import RelationshipBitType
from relationships.relationship_bit_lock import RelationshipBitLock
from relationships.relationship_data import BidirectionalRelationshipData, UnidirectionalRelationshipData
from relationships.relationship_enums import RelationshipDirection, RelationshipTrackType
from sims.sim_info_lod import SimInfoLODLevel
from sims4.common import Pack, is_available_pack
from sims4.localization import LocalizationHelperTuning
from sims4.utils import constproperty, classproperty
from singletons import EMPTY_SET, DEFAULT
logger = sims4.log.Logger('Relationship', default_owner='jjacobson')

class Relationship:
    __slots__ = ('_sim_id_a', '_sim_id_b', '_bi_directional_relationship_data', '_level_change_watcher_id',
                 '_culling_alarm_handle', '_last_update_time', '_relationship_multipliers',
                 '_counts_as_incest', '__weakref__')

    def __init__(self):
        self._bi_directional_relationship_data = BidirectionalRelationshipData(self)
        self._culling_alarm_handle = None
        self._last_update_time = 0
        self._counts_as_incest = False

    @property
    def suppress_client_updates(self):
        return services.relationship_service().suppress_client_updates

    @property
    def sim_id_a(self):
        return self._sim_id_a

    @property
    def sim_id_b(self):
        return self._sim_id_b

    @property
    def considered_incest(self):
        if self._counts_as_incest is not None:
            return self._counts_as_incest
        for rel_bit in self._get_all_bits(self._sim_id_a):
            if rel_bit.counts_as_incest:
                self._counts_as_incest = True
                return True

        self._counts_as_incest = False
        return False

    def get_relationship_key(self):
        return (
         self._sim_id_a, self._sim_id_b)

    def find_sim_info_a(self):
        return services.sim_info_manager().get(self._sim_id_a)

    def find_sim_info_b(self):
        return services.sim_info_manager().get(self._sim_id_b)

    def find_member_obj_b(self):
        return services.definition_manager().get(self._sim_id_b)

    def find_sim_a(self):
        sim_info = self.find_sim_info_a()
        if sim_info is not None:
            return sim_info.get_sim_instance()

    def find_sim_b(self):
        sim_info = self.find_sim_info_b()
        if sim_info is not None:
            return sim_info.get_sim_instance()

    def get_bi_directional_rel_data(self):
        return self._bi_directional_relationship_data

    def get_other_sim_id(self, sim_id):
        if self._sim_id_a == sim_id:
            return self._sim_id_b
        return self._sim_id_a

    def get_other_sim_info(self, sim_id):
        if self._sim_id_a == sim_id:
            return self.find_sim_info_b()
        return self.find_sim_info_a()

    def get_other_sim(self, sim_id):
        if self._sim_id_a == sim_id:
            return self.find_sim_b()
        return self.find_sim_a()

    @property
    def relationship_track_tracker(self):
        return self._bi_directional_relationship_data.track_tracker

    def get_track_relationship_data(self, sim_id, track):
        return self._bi_directional_relationship_data

    def get_relationship_depth(self, sim_id):
        return self._bi_directional_relationship_data.depth

    def _build_relationship_track_proto(self, actor_sim_id, msg):
        client_tracks = [track for track in self.relationship_tracks_gen(actor_sim_id) if track.display_priority > 0]
        client_tracks.sort(key=(lambda track: track.display_priority))
        track_bits = set()
        for track in client_tracks:
            if track.visible_to_client:
                with ProtocolBufferRollback(msg.tracks) as (relationship_track_update):
                    track.build_single_relationship_track_proto(relationship_track_update)
            track_bits.add(track.get_bit_for_client().guid64)

        return track_bits

    def _send_headlines_for_sim(self, sim_info, deltas, headline_icon_modifier=None):
        for track, delta in deltas.items():
            if track.headline is None:
                continue
            track.headline.send_headline_message(sim_info, delta, icon_modifier=headline_icon_modifier)

    def send_relationship_info(self, deltas=None, headline_icon_modifier=None):
        raise NotImplementedError()

    def relationship_tracks_gen(self, sim_id, track_type=None):
        if track_type is None or track_type == RelationshipTrackType.RELATIONSHIP:
            yield from self._bi_directional_relationship_data.track_tracker
        if False:
            yield None

    def get_track_score(self, sim_id, track):
        return self.get_track_relationship_data(sim_id, track).get_track_score(track)

    def set_track_score(self, sim_id, value, track, **kwargs):
        (self.get_track_relationship_data(sim_id, track).set_track_score)(value, track, **kwargs)

    def add_track_score(self, sim_id, increment, track, **kwargs):
        (self.get_track_relationship_data(sim_id, track).add_track_score)(increment, track, **kwargs)

    def set_track_to_max(self, sim_id, track):
        self.get_track_relationship_data(sim_id, track).set_track_to_max(track)

    def enable_player_sim_track_decay(self, to_enable=True):
        self._bi_directional_relationship_data.enable_player_sim_track_decay(to_enable=to_enable)
        if self._culling_alarm_handle is None:
            if self.can_cull_relationship():
                self._create_culling_alarm()

    def get_track_utility_score(self, sim_id, track):
        return self.get_track_relationship_data(sim_id, track).get_track_utility_score(track)

    def get_track_tracker(self, sim_id, track):
        return self._bi_directional_relationship_data.track_tracker

    def get_track(self, sim_id, track, add=False):
        should_add = add and track.track_type != RelationshipTrackType.SENTIMENT
        return self.get_track_relationship_data(sim_id, track).get_track(track, add=should_add)

    def get_highest_priority_track_bit(self, sim_id):
        return self._bi_directional_relationship_data.get_highest_priority_track_bit()

    def get_prevailing_short_term_context_track(self, sim_id):
        return self._bi_directional_relationship_data.get_prevailing_short_term_context_track()

    def apply_social_group_decay(self):
        self._bi_directional_relationship_data.apply_social_group_decay()

    def remove_social_group_decay(self):
        self._bi_directional_relationship_data.remove_social_group_decay()

    def set_relationship_score(self, sim_id, value, track=DEFAULT, threshold=None, **kwargs):
        if track is DEFAULT:
            track = RelationshipGlobalTuning.REL_INSPECTOR_TRACK
        elif threshold is None or threshold.compare(self.get_track_score(sim_id, track)):
            (self.set_track_score)(sim_id, value, track, **kwargs)
            logger.debug('Setting score on track {} for {}: = {}; new score = {}', track, self, value, self.get_track_score(sim_id, track))
        else:
            logger.debug('Attempting to set score on track {} for {} but {} not within threshold {}', track, self, self.get_track_score(sim_id, track), threshold)

    def add_relationship_bit(self, actor_sim_id, target_sim_id, bit_to_add, notify_client=True, pending_bits=EMPTY_SET, force_add=False, from_load=False, send_rel_change_event=True):
        sim_info_manager = services.sim_info_manager()
        actor_sim_info = sim_info_manager.get(actor_sim_id)
        if self.is_object_rel:
            target_sim_info = None
            send_rel_change_event = False
        else:
            target_sim_info = sim_info_manager.get(target_sim_id)
        if send_rel_change_event:
            self._send_relationship_prechange_event(actor_sim_info, target_sim_info, bidirectional=(bit_to_add.directionality == RelationshipDirection.BIDIRECTIONAL),
              bits_of_interest=(
             bit_to_add,))
        elif bit_to_add is None:
            logger.error('Error: Sim Id: {} trying to add a None relationship bit to Sim_Id: {}.', actor_sim_id, target_sim_id)
            return False
            if force_add:
                if bit_to_add.is_track_bit:
                    if bit_to_add.triggered_track is not None:
                        track = bit_to_add.triggered_track
                        mean_list = track.bit_data.get_track_mean_list_for_bit(bit_to_add)
                        for mean_tuple in mean_list:
                            self.set_relationship_score(actor_sim_id, (mean_tuple.mean),
                              track=(mean_tuple.track))

                for required_bit in bit_to_add.required_bits:
                    self.add_relationship_bit(actor_sim_id, target_sim_id, required_bit, force_add=True)

            required_bit_count = len(bit_to_add.required_bits)
            bit_to_remove = None
            for curr_bit in itertools.chain(self._get_all_bits(actor_sim_id), pending_bits):
                if curr_bit is bit_to_add:
                    logger.debug('Attempting to add duplicate bit {} on {}', bit_to_add, actor_sim_info)
                    if curr_bit.is_trope_bit:
                        if curr_bit.directionality == RelationshipDirection.BIDIRECTIONAL:
                            target_sim_info.genealogy.set_relationship_trope(actor_sim_id, curr_bit.guid64)
                    return False
                    if required_bit_count:
                        if curr_bit in bit_to_add.required_bits:
                            required_bit_count -= 1
                    if bit_to_add.group_id != RelationshipBitType.NoGroup:
                        if bit_to_add.group_id == curr_bit.group_id:
                            if bit_to_add.priority >= curr_bit.priority:
                                if bit_to_remove is not None:
                                    logger.error('Multiple relationship bits of the same type are set on a single relationship: {}', self)
                                    return False
                                bit_to_remove = curr_bit
                        else:
                            logger.debug('Failed to add bit {}; existing bit {} has higher priority for {}', bit_to_add, curr_bit, self)
                            return False

            if bit_to_add.remove_on_threshold:
                track_val = self._bi_directional_relationship_data.track_tracker.get_value(bit_to_add.remove_on_threshold.track)
                if bit_to_add.remove_on_threshold.threshold.compare(track_val):
                    logger.debug('Failed to add bit {}; track {} meets the removal threshold {} for {}', bit_to_add, bit_to_add.remove_on_threshold.track, bit_to_add.remove_on_threshold.threshold, self)
                    return False
            if not from_load:
                if required_bit_count > 0:
                    logger.debug('Failed to add bit {}; required bit count is {}', bit_to_add, required_bit_count)
                    return False
        else:
            rel_data = self._get_rel_data_for_bit(actor_sim_id, bit_to_add)
            if rel_data is None:
                logger.debug('Failed to get relationship data for bit {}', bit_to_add)
                return False
            if not force_add:
                if not from_load:
                    if bit_to_add.group_id != RelationshipBitType.NoGroup:
                        lock_type = RelationshipBitLock.get_lock_type_for_group_id(bit_to_add.group_id)
                        if lock_type is not None:
                            lock = rel_data.get_lock(lock_type)
                            if lock is not None:
                                if bit_to_remove is not None:
                                    lock.try_and_aquire_lock_permission() or logger.debug('Failed to add bit {} because of Relationship Bit Lock {}', bit_to_add, lock_type)
                                    return False
                            else:
                                lock = rel_data.add_lock(lock_type)
                            lock.lock()
        if bit_to_remove is not None:
            self.remove_bit(actor_sim_id, target_sim_id, bit_to_remove, notify_client=False)
        if bit_to_add.exclusive:
            services.relationship_service().remove_exclusive_relationship_bit(actor_sim_id, bit_to_add)
            if bit_to_add.directionality == RelationshipDirection.BIDIRECTIONAL:
                services.relationship_service().remove_exclusive_relationship_bit(target_sim_id, bit_to_add)
        if bit_to_add.is_trope_bit:
            if actor_sim_info is not None:
                actor_sim_info.genealogy.set_relationship_trope(target_sim_id, bit_to_add.guid64)
        bit_instance = bit_to_add()
        rel_data.add_bit(bit_to_add, bit_instance, from_load=from_load)
        logger.debug('Added bit {} for {}', bit_to_add, self)
        if bit_to_add.counts_as_incest:
            self._counts_as_incest = True
        self._invoke_bit_added(actor_sim_id, bit_to_add)
        if notify_client is True:
            self.send_relationship_info()
        if send_rel_change_event:
            self._send_relationship_changed_event(actor_sim_info, target_sim_info, bidirectional=(bit_to_add.directionality == RelationshipDirection.BIDIRECTIONAL))
        return True

    def _get_all_bits(self, actor_sim_id):
        return itertools.chain(self._bi_directional_relationship_data.bit_types)

    def _invoke_bit_added(self, actor_sim_id, bit_to_add):
        self._bi_directional_relationship_data.track_tracker.on_relationship_bit_added(bit_to_add, actor_sim_id)

    def add_neighbor_bit_if_necessary(self):
        sim_info_a = self.find_sim_info_a()
        if sim_info_a is None:
            return
        sim_info_b = self.find_sim_info_b()
        if sim_info_b is None:
            return
        household_a = sim_info_a.household
        household_b = sim_info_b.household
        if household_a is None or household_b is None:
            return
        home_zone_id_a = household_a.home_zone_id
        home_zone_id_b = household_b.home_zone_id
        if home_zone_id_a == home_zone_id_b:
            return
        if home_zone_id_a == 0 or home_zone_id_b == 0:
            return
        persistence_service = services.get_persistence_service()
        sim_a_home_zone_proto_buffer = persistence_service.get_zone_proto_buff(home_zone_id_a)
        sim_b_home_zone_proto_buffer = persistence_service.get_zone_proto_buff(home_zone_id_b)
        if sim_a_home_zone_proto_buffer is None or sim_b_home_zone_proto_buffer is None:
            logger.error('Invalid zone protocol buffer in Relationship.add_neighbor_bit_if_necessary() between {} and {}', sim_info_a, sim_info_b)
            return
        if sim_a_home_zone_proto_buffer.world_id != sim_b_home_zone_proto_buffer.world_id:
            return
        self.add_relationship_bit((self._sim_id_a), (self._sim_id_b), (global_relationship_tuning.RelationshipGlobalTuning.NEIGHBOR_RELATIONSHIP_BIT), notify_client=False)

    def _remove_bit(self, actor_sim_id, bit):
        rel_data = self._get_rel_data_for_bit(actor_sim_id, bit)
        rel_data.remove_bit(bit)
        if bit.counts_as_incest:
            self._counts_as_incest = None
        self._invoke_bit_removed(actor_sim_id, bit)

    def remove_bit_by_collection_id(self, actor_sim_id, target_sim_id, collection_id, notify_client=True, send_rel_change_event=True):
        sim_info_manager = services.sim_info_manager()
        actor_sim_info = sim_info_manager.get(actor_sim_id)
        target_sim_info = sim_info_manager.get(target_sim_id)
        has_bidirectional_update = False
        bits_to_remove = []
        for bit_type in self.get_bits(target_sim_id):
            if collection_id in bit_type.collection_ids:
                if bit_type.directionality == RelationshipDirection.BIDIRECTIONAL:
                    has_bidirectional_update = True
                bits_to_remove.append(bit_type)

        if send_rel_change_event:
            self._send_relationship_prechange_event(actor_sim_info, target_sim_info, bidirectional=has_bidirectional_update,
              bits_of_interest=bits_to_remove)
        for bit in bits_to_remove:
            self._remove_bit(actor_sim_id, bit)

        if notify_client:
            self.send_relationship_info()
        if send_rel_change_event:
            self._send_relationship_changed_event(actor_sim_info, target_sim_info, bidirectional=has_bidirectional_update)

    def remove_bit(self, actor_sim_id, target_sim_id, bit, notify_client=True, send_rel_change_event=True):
        if bit is None:
            logger.error('Error: Sim Id: {} trying to remove a None relationship bit to Sim_Id: {}.', actor_sim_id, target_sim_id)
            return
        else:
            sim_info_manager = services.sim_info_manager()
            actor_sim_info = sim_info_manager.get(actor_sim_id)
            target_sim_info = sim_info_manager.get(target_sim_id)
            if bit.is_trope_bit:
                if actor_sim_info is not None:
                    actor_sim_info.genealogy.remove_relationship_trope(target_sim_info.sim_id)
                    if bit.directionality == RelationshipDirection.BIDIRECTIONAL:
                        target_sim_info.genealogy.remove_relationship_trope(actor_sim_info.sim_id)
            if send_rel_change_event:
                self._send_relationship_prechange_event(actor_sim_info, target_sim_info, bidirectional=(bit.directionality == RelationshipDirection.BIDIRECTIONAL),
                  bits_of_interest=(
                 bit,))
            self._remove_bit(actor_sim_id, bit)
            if notify_client is True:
                self.send_relationship_info()
            if not self.is_object_rel:
                if send_rel_change_event:
                    self._send_relationship_changed_event(actor_sim_info, target_sim_info, bidirectional=(bit.directionality == RelationshipDirection.BIDIRECTIONAL))

    def _invoke_bit_removed(self, actor_sim_id, bit):
        self.relationship_track_tracker.on_relationship_bit_removed(bit, actor_sim_id)

    def _get_rel_data_for_bit(self, actor_sim_id, bit):
        if bit.directionality == RelationshipDirection.BIDIRECTIONAL:
            return self._bi_directional_relationship_data

    def has_bit(self, sim_id, bit):
        return any((bit.matches_bit(bit_type) for bit_type in self._bi_directional_relationship_data.bit_types))

    def remove_track(self, actor_sim_id, target_sim_id, track, notify_client=True, send_rel_change_event=True):
        if track is None:
            logger.error('Error: Sim Id: {} trying to remove a None relationship track to Sim_Id: {}.', actor_sim_id, target_sim_id)
            return
        else:
            sim_info_manager = services.sim_info_manager()
            actor_sim_info = sim_info_manager.get(actor_sim_id)
            target_sim_info = sim_info_manager.get(target_sim_id)
            if send_rel_change_event:
                self._send_relationship_prechange_event(actor_sim_info, target_sim_info, bidirectional=(track.track_type != RelationshipTrackType.SENTIMENT))
            self.get_track_relationship_data(actor_sim_id, track).remove_track(track)
            if notify_client is True:
                self.send_relationship_info()
            if not self.is_object_rel:
                if send_rel_change_event:
                    self._send_relationship_changed_event(actor_sim_info, target_sim_info, bidirectional=(track.track_type != RelationshipTrackType.SENTIMENT))

    def has_track(self, sim_id, relationship_track):
        return self.get_track_relationship_data(sim_id, relationship_track).has_track(relationship_track)

    def get_bits(self, sim_id):
        return tuple(self._bi_directional_relationship_data.bit_types)

    def get_bit_instances(self, sim_id):
        return tuple(self._bi_directional_relationship_data.bit_instances)

    def get_highest_priority_bit(self, sim_id):
        highest_priority_bit = None
        for bit in self.get_bits(sim_id):
            if highest_priority_bit is None or bit.priority > highest_priority_bit.priority:
                highest_priority_bit = bit

        return highest_priority_bit

    def add_relationship_appropriateness_buffs(self, sim_id):
        sim_info = services.sim_info_manager().get(sim_id)
        for bit in self.get_bit_instances(sim_id):
            bit.add_appropriateness_buffs(sim_info)

    def _create_culling_alarm(self):
        self._destroy_culling_alarm()
        time_range = date_and_time.create_time_span(minutes=(RelationshipGlobalTuning.DELAY_UNTIL_RELATIONSHIP_IS_CULLED))
        self._culling_alarm_handle = alarms.add_alarm(self, time_range, (self._cull_relationship_callback), cross_zone=True)

    def _destroy_culling_alarm(self):
        if self._culling_alarm_handle is not None:
            alarms.cancel_alarm(self._culling_alarm_handle)
            self._culling_alarm_handle = None

    def _cull_relationship_callback(self, _):
        self._destroy_culling_alarm()
        if self.can_cull_relationship():
            logger.debug('Culling {}', self)
            services.relationship_service().destroy_relationship(self._sim_id_a, self._sim_id_b)
        else:
            logger.warn("Attempting to cull {} but it's no longer allowed.", self)

    def can_cull_relationship(self, consider_convergence=True):
        sim_info_a = self.find_sim_info_a()
        sim_info_b = self.find_sim_info_b()
        if sim_info_a is not None:
            if sim_info_b is not None:
                if sim_info_a.household_id == sim_info_b.household_id:
                    return False
        is_played_relationship = sim_info_a is not None and sim_info_b is not None and (sim_info_a.is_player_sim or sim_info_b.is_player_sim)
        return self._bi_directional_relationship_data.can_cull_relationship(consider_convergence, is_played_relationship)

    def apply_relationship_multipliers(self, sim_id, relationship_multipliers):
        for track_type, multiplier in relationship_multipliers.items():
            relationship_track = self._bi_directional_relationship_data.get_track(track_type, add=False)
            if relationship_track is not None:
                relationship_track.add_statistic_multiplier(multiplier)

    def remove_relationship_multipliers(self, sim_id, relationship_multipliers):
        for track_type, multiplier in relationship_multipliers.items():
            relationship_track = self._bi_directional_relationship_data.get_track(track_type, add=False)
            if relationship_track is not None:
                relationship_track.remove_statistic_multiplier(multiplier)

    def _send_relationship_prechange_event(self, sim_info_a, sim_info_b, bidirectional=True, bits_of_interest=None):
        if sim_info_a is None or sim_info_b is None:
            return
        elif bits_of_interest is not None:
            custom_keys = bits_of_interest
        else:
            custom_keys = ()
        services.get_event_manager().process_event((event_testing.test_events.TestEvent.PrerelationshipChanged), sim_info_a,
          sim_id=(sim_info_a.id),
          target_sim_id=(sim_info_b.id),
          custom_keys=custom_keys)
        if bidirectional:
            services.get_event_manager().process_event((event_testing.test_events.TestEvent.PrerelationshipChanged), sim_info_b,
              sim_id=(sim_info_b.id),
              target_sim_id=(sim_info_a.id),
              custom_keys=custom_keys)

    def _send_relationship_changed_event(self, sim_info_a, sim_info_b, bidirectional=True):
        if sim_info_a is None or sim_info_b is None:
            return
        services.get_event_manager().process_event((event_testing.test_events.TestEvent.RelationshipChanged), sim_info_a,
          sim_id=(sim_info_a.id),
          target_sim_id=(sim_info_b.id))
        if bidirectional:
            services.get_event_manager().process_event((event_testing.test_events.TestEvent.RelationshipChanged), sim_info_b,
              sim_id=(sim_info_b.id),
              target_sim_id=(sim_info_a.id))

    def save_relationship(self, relationship_msg):
        relationship_msg.sim_id_a = self._sim_id_a
        relationship_msg.sim_id_b = self._sim_id_b
        self._bi_directional_relationship_data.save_relationship_data(relationship_msg.bidirectional_relationship_data)
        relationship_msg.last_update_time = self._last_update_time

    def load_relationship(self, relationship_msg):
        self._bi_directional_relationship_data.load_relationship_data(relationship_msg.bidirectional_relationship_data)
        self._last_update_time = relationship_msg.last_update_time

    def build_printable_string_of_bits(self, sim_id):
        return '\t\t{}'.format('\n\t\t'.join(map(str, self.get_bit_instances(sim_id))))

    def build_printable_string_of_tracks(self):
        ret = ''
        for track in self._bi_directional_relationship_data.track_tracker:
            ret += '\t\t{} = {}; decaying? {}; decay rate: {}; track type: {}\n'.format(track, track.get_value(), track.decay_enabled, track.get_decay_rate(), track.track_type)

        return ret

    def _send_destroy_message_to_client(self):
        msg_a = commodity_protocol.RelationshipDelete()
        msg_a.actor_sim_id = self._sim_id_a
        msg_a.target_id = self._sim_id_b
        op_a = GenericProtocolBufferOp(DistributorOps_pb2.Operation.SIM_RELATIONSHIP_DELETE, msg_a)
        distributor = Distributor.instance()
        distributor.add_op(self.find_sim_info_a(), op_a)
        if not self.is_object_rel:
            msg_b = commodity_protocol.RelationshipDelete()
            msg_b.actor_sim_id = self._sim_id_b
            msg_b.target_id = self._sim_id_a
            op_b = GenericProtocolBufferOp(DistributorOps_pb2.Operation.SIM_RELATIONSHIP_DELETE, msg_b)
            distributor.add_op(self.find_sim_info_b(), op_b)

    def notify_relationship_on_lod_change(self, old_lod, new_lod):
        pass

    def destroy(self, notify_client=True):
        if notify_client:
            self._send_destroy_message_to_client()
        self._bi_directional_relationship_data.destroy()
        self._destroy_culling_alarm()

    def get_all_relationship_bit_locks(self, sim_id):
        return list(self._bi_directional_relationship_data.get_all_locks())

    def get_relationship_bit_lock(self, sim_id, lock_type):
        return self._bi_directional_relationship_data.get_lock(lock_type)

    def on_sim_creation(self, sim):
        self._bi_directional_relationship_data.on_sim_creation(sim)

    @classproperty
    def is_object_rel(cls):
        raise NotImplementedError()


class SimRelationship(Relationship):
    __slots__ = ('_sim_id_a', '_sim_id_b', '_bi_directional_relationship_data', '_sim_a_relationship_data',
                 '_sim_b_relationship_data')

    def __init__(self, sim_id_a, sim_id_b):
        if sim_id_a < sim_id_b:
            self._sim_id_a = sim_id_a
            self._sim_id_b = sim_id_b
        else:
            self._sim_id_a = sim_id_b
            self._sim_id_b = sim_id_a
        self._sim_a_relationship_data = UnidirectionalRelationshipData(self, self._sim_id_a)
        self._sim_b_relationship_data = UnidirectionalRelationshipData(self, self._sim_id_b)
        super().__init__()

    @classproperty
    def is_object_rel(cls):
        return False

    def apply_social_group_decay(self):
        self._sim_a_relationship_data.apply_social_group_decay()
        self._sim_b_relationship_data.apply_social_group_decay()
        super().apply_social_group_decay()

    def remove_social_group_decay(self):
        self._sim_a_relationship_data.remove_social_group_decay()
        self._sim_b_relationship_data.remove_social_group_decay()
        super().remove_social_group_decay()

    def _get_uni_directional_rel_data(self, sim_id):
        if sim_id == self._sim_id_a:
            return self._sim_a_relationship_data
        return self._sim_b_relationship_data

    def get_uni_directional_rel_data(self, sim_id):
        return self._get_uni_directional_rel_data(sim_id)

    def enable_player_sim_track_decay(self, to_enable=True):
        self._sim_a_relationship_data.enable_player_sim_track_decay(to_enable=to_enable)
        self._sim_b_relationship_data.enable_player_sim_track_decay(to_enable=to_enable)
        super().enable_player_sim_track_decay(to_enable)

    def get_highest_priority_track_bit(self, sim_id):
        return max(super().get_highest_priority_track_bit(sim_id), self._get_uni_directional_rel_data(sim_id).get_highest_priority_track_bit())

    def has_bit(self, sim_id, bit):
        return super().has_bit(sim_id, bit) or any((bit.matches_bit(bit_type) for bit_type in self._get_uni_directional_rel_data(sim_id).bit_types))

    def on_sim_creation(self, sim):
        super().on_sim_creation(sim)
        self._get_uni_directional_rel_data(sim.sim_id).on_sim_creation(sim)

    def get_relationship_bit_lock(self, sim_id, lock_type):
        lock = super().get_relationship_bit_lock(sim_id, lock_type)
        if lock is None:
            lock = self._get_uni_directional_rel_data(sim_id).get_lock(lock_type)
        return lock

    def get_all_relationship_bit_locks(self, sim_id):
        return list(itertools.chain(super().get_all_relationship_bit_locks(sim_id), self._get_uni_directional_rel_data(sim_id).get_all_locks()))

    def destroy(self, notify_client=True):
        super().destroy(notify_client)
        self._sim_a_relationship_data.destroy()
        self._sim_b_relationship_data.destroy()

    def notify_relationship_on_lod_change(self, old_lod, new_lod):
        super().notify_relationship_on_lod_change(old_lod, new_lod)
        self._sim_a_relationship_data.notify_relationship_on_lod_change(old_lod, new_lod)
        self._sim_b_relationship_data.notify_relationship_on_lod_change(old_lod, new_lod)

    def build_printable_string_of_tracks(self):
        ret = super().build_printable_string_of_tracks()
        for track in self._sim_a_relationship_data.track_tracker:
            ret += '\t\t{} = {}; decaying? {}; decay rate: {}; track type: {}; from sim_id:{} to sim_id:{}\n'.format(track, track.get_value(), track.decay_enabled, track.get_decay_rate(), track.track_type, self.sim_id_a, self.sim_id_b)

        for track in self._sim_b_relationship_data.track_tracker:
            ret += '\t\t{} = {}; decaying? {}; decay rate: {}; track type: {} from sim_id:{} to sim_id:{}\n'.format(track, track.get_value(), track.decay_enabled, track.get_decay_rate(), track.track_type, self.sim_id_b, self.sim_id_a)

        return ret

    def save_relationship(self, relationship_msg):
        super().save_relationship(relationship_msg)
        self._sim_a_relationship_data.save_relationship_data(relationship_msg.sim_a_relationship_data)
        self._sim_b_relationship_data.save_relationship_data(relationship_msg.sim_b_relationship_data)

    def load_relationship(self, relationship_msg):
        super().load_relationship(relationship_msg)
        self._sim_a_relationship_data.load_relationship_data(relationship_msg.sim_a_relationship_data)
        self._sim_b_relationship_data.load_relationship_data(relationship_msg.sim_b_relationship_data)

    def can_cull_relationship(self, consider_convergence=True):
        if not super().can_cull_relationship(consider_convergence):
            return False
        else:
            sim_info_a = self.find_sim_info_a()
            sim_info_b = self.find_sim_info_b()
            is_played_relationship = sim_info_a is not None and sim_info_b is not None and (sim_info_a.is_player_sim or sim_info_b.is_player_sim)
            if not self._sim_a_relationship_data.can_cull_relationship(consider_convergence, is_played_relationship):
                return False
            return self._sim_b_relationship_data.can_cull_relationship(consider_convergence, is_played_relationship) or False
        return True

    def get_bits(self, sim_id):
        return tuple(itertools.chain(super().get_bits(sim_id), self._get_uni_directional_rel_data(sim_id).bit_types))

    def get_bit_instances(self, sim_id):
        return tuple(itertools.chain(super().get_bit_instances(sim_id), self._get_uni_directional_rel_data(sim_id).bit_instances))

    def get_track_tracker(self, sim_id, track):
        if track.track_type == RelationshipTrackType.SENTIMENT:
            return self._get_uni_directional_rel_data(sim_id).track_tracker
        return super().get_track_tracker(sim_id, track)

    def get_track_relationship_data(self, sim_id, track):
        if track.track_type == RelationshipTrackType.SENTIMENT:
            return self._get_uni_directional_rel_data(sim_id)
        return super().get_track_relationship_data(sim_id, track)

    def get_relationship_depth(self, sim_id):
        return super().get_relationship_depth(sim_id) + self._get_uni_directional_rel_data(sim_id).depth

    def refresh_knowledge(self):
        sim_info_manager = services.sim_info_manager()
        sim_info_a = sim_info_manager.get(self._sim_id_a)
        sim_info_b = sim_info_manager.get(self._sim_id_b)
        if sim_info_b.needs_preference_traits_fixup:
            sim_knowledge = self.get_knowledge(self._sim_id_a, self._sim_id_b)
            if sim_knowledge is not None:
                for known_trait in list(sim_knowledge.known_traits):
                    if not sim_info_b.has_trait(known_trait):
                        sim_knowledge.remove_known_trait(known_trait)

                self._fixup_gender_preference_knowledge(sim_knowledge, sim_info_b)
        if sim_info_a.needs_preference_traits_fixup:
            sim_knowledge = self.get_knowledge(self._sim_id_b, self._sim_id_a)
            if sim_knowledge is not None:
                for known_trait in list(sim_knowledge.known_traits):
                    if not sim_info_a.has_trait(known_trait):
                        sim_knowledge.remove_known_trait(known_trait)

                self._fixup_gender_preference_knowledge(sim_knowledge, sim_info_a)

    def get_knowledge(self, actor_sim_id, target_sim_id, initialize=False):
        rel_data = self._get_uni_directional_rel_data(actor_sim_id)
        if initialize:
            if rel_data.knowledge is None:
                rel_data.initialize_knowledge()
        return rel_data.knowledge

    def apply_relationship_multipliers(self, sim_id, relationship_multipliers):
        super().apply_relationship_multipliers(sim_id, relationship_multipliers)
        uni_directional_data = self._get_uni_directional_rel_data(sim_id)
        for track_type, multiplier in relationship_multipliers.items():
            relationship_track = uni_directional_data.get_track(track_type, add=False)
            if relationship_track is not None:
                relationship_track.add_statistic_multiplier(multiplier)

    def remove_relationship_multipliers(self, sim_id, relationship_multipliers):
        super().remove_relationship_multipliers(sim_id, relationship_multipliers)
        uni_directional_data = self._get_uni_directional_rel_data(sim_id)
        for track_type, multiplier in relationship_multipliers.items():
            relationship_track = uni_directional_data.get_track(track_type, add=False)
            if relationship_track is not None:
                relationship_track.remove_statistic_multiplier(multiplier)

    def _fixup_gender_preference_knowledge(self, sim_knowledge, target_sim_info):
        if sim_knowledge.knows_romantic_preference:
            if sim_knowledge.get_known_exploring_sexuality != target_sim_info.is_exploring_sexuality or sim_knowledge.known_romantic_genders != target_sim_info.get_attracted_genders(GenderPreferenceType.ROMANTIC):
                sim_knowledge.remove_knows_romantic_preference()
        if sim_knowledge.knows_woohoo_preference:
            if sim_knowledge.known_woohoo_genders != target_sim_info.get_attracted_genders(GenderPreferenceType.WOOHOO):
                sim_knowledge.remove_knows_woohoo_preference()

    def _get_rel_data_for_bit(self, actor_sim_id, bit):
        rel_data = super()._get_rel_data_for_bit(actor_sim_id, bit)
        if rel_data is None:
            rel_data = self._get_uni_directional_rel_data(actor_sim_id)
        return rel_data

    def _invoke_bit_removed(self, actor_sim_id, bit):
        super()._invoke_bit_removed(actor_sim_id, bit)
        self.sentiment_track_tracker(actor_sim_id).on_relationship_bit_removed(bit, actor_sim_id)

    def _invoke_bit_added(self, actor_sim_id, bit_to_add):
        super()._invoke_bit_added(actor_sim_id, bit_to_add)
        self.sentiment_track_tracker(actor_sim_id).on_relationship_bit_added(bit_to_add, actor_sim_id)

    def _get_all_bits(self, actor_sim_id):
        return itertools.chain(super()._get_all_bits(actor_sim_id), self._get_uni_directional_rel_data(actor_sim_id).bit_types)

    def get_bit_added_buffs(self, sim_id):
        rel_data = self._get_uni_directional_rel_data(sim_id)
        if rel_data.bit_added_buffs is None:
            rel_data.bit_added_buffs = set()
        return rel_data.bit_added_buffs

    def add_bit_added_buffs(self, sim_id, buff):
        rel_data = self._get_uni_directional_rel_data(sim_id)
        if rel_data.bit_added_buffs is None:
            rel_data.bit_added_buff = set()
        rel_data.bit_added_buffs.add(buff.guid64)

    def sentiment_track_tracker(self, sim_id):
        return self._get_uni_directional_rel_data(sim_id).track_tracker

    def relationship_tracks_gen(self, sim_id, track_type=None):
        if track_type is None or track_type == RelationshipTrackType.RELATIONSHIP:
            yield from super().relationship_tracks_gen(sim_id, track_type)
        if track_type is None or track_type == RelationshipTrackType.SENTIMENT:
            yield from self.sentiment_track_tracker(sim_id)
        if False:
            yield None

    def get_compatibility_level(self):
        return self._bi_directional_relationship_data.get_compatibility_level()

    def get_compatibility_score(self):
        return self._bi_directional_relationship_data.get_compatibility_score()

    def update_compatibility(self):
        self._bi_directional_relationship_data.update_compatibility()

    def set_npc_compatibility_preferences(self):
        self._bi_directional_relationship_data.set_npc_compatibility_preferences()

    def send_relationship_info(self, deltas=None, headline_icon_modifier=None):
        if self.suppress_client_updates:
            return
            sim_info_a = self.find_sim_info_a()
            sim_info_b = self.find_sim_info_b()
            if sim_info_a is not None:
                if sim_info_b is not None:
                    if sim_info_a.is_npc:
                        if sim_info_b.is_npc:
                            return
        else:
            if sim_info_a is not None:
                send_relationship_op(sim_info_a, self._build_relationship_update_proto(sim_info_a, (self._sim_id_b), deltas=deltas))
                if deltas is not None:
                    self._send_headlines_for_sim(sim_info_a, deltas, headline_icon_modifier=headline_icon_modifier)
            if sim_info_b is not None:
                send_relationship_op(sim_info_b, self._build_relationship_update_proto(sim_info_b, (self._sim_id_a), deltas=deltas))
                if deltas is not None:
                    self._send_headlines_for_sim(sim_info_b, deltas, headline_icon_modifier=headline_icon_modifier)

    def _build_relationship_update_proto(self, actor_sim_info, target_sim_id, deltas=None):
        msg = commodity_protocol.RelationshipUpdate()
        actor_sim_id = actor_sim_info.sim_id
        msg.actor_sim_id = actor_sim_id
        msg.target_id.object_id = target_sim_id
        msg.target_id.manager_id = services.sim_info_manager().id
        msg.last_update_time = self._last_update_time
        msg.is_load = not services.current_zone().is_zone_running
        tracks = self._build_relationship_track_proto(actor_sim_id, msg)
        self._build_relationship_bit_proto(actor_sim_id, tracks, msg)
        sim_info_manager = services.sim_info_manager()
        target_sim_info = sim_info_manager.get(target_sim_id)
        owner = sim_info_manager.get(actor_sim_id)
        knowledge = self._get_uni_directional_rel_data(actor_sim_id).knowledge
        if knowledge is not None:
            if target_sim_info is not None:
                if target_sim_info.lod != SimInfoLODLevel.MINIMUM:
                    if owner is not None:
                        if owner.lod != SimInfoLODLevel.MINIMUM:
                            if target_sim_info is not None:
                                msg.num_traits = len(target_sim_info.trait_tracker.personality_traits)
                            else:
                                for trait in knowledge.known_traits:
                                    if not trait.is_personality_trait:
                                        msg.known_trait_ids.append(trait.guid64)

                                for trait in target_sim_info.trait_tracker.personality_traits:
                                    if trait in knowledge.known_traits:
                                        msg.known_trait_ids.append(trait.guid64)

                                if knowledge.knows_career:
                                    msg.known_careertrack_ids.extend(knowledge.get_known_careertrack_ids())
                                if knowledge._known_stats is not None:
                                    for stat in knowledge._known_stats:
                                        msg.known_stat_ids.append(stat.guid64)

                                if knowledge.knows_major:
                                    if knowledge.get_known_major() is not None:
                                        msg.known_major_id = knowledge.get_known_major().guid64
                                msg.knows_romantic_preference = knowledge.knows_romantic_preference
                                if knowledge.knows_romantic_preference:
                                    for gender in knowledge.known_romantic_genders:
                                        msg.known_romantic_genders.append(gender)

                                    if knowledge.get_known_exploring_sexuality is not None:
                                        msg.known_exploring_sexuality = knowledge.get_known_exploring_sexuality
                            msg.knows_woohoo_preference = knowledge.knows_woohoo_preference
                            if knowledge.knows_woohoo_preference:
                                for gender in knowledge.known_woohoo_genders:
                                    msg.known_woohoo_genders.append(gender)

        if target_sim_info is not None:
            if target_sim_info.spouse_sim_id is not None:
                msg.target_sim_significant_other_id = target_sim_info.spouse_sim_id
        actor_trait_tracker = actor_sim_info.trait_tracker
        target_trait_tracker = target_sim_info.trait_tracker if target_sim_info else None
        if actor_trait_tracker is not None and target_trait_tracker is not None and not actor_trait_tracker.has_characteristic_preferences():
            if target_trait_tracker.has_characteristic_preferences():
                self._build_compatibility_proto(msg)
        return msg

    def _build_relationship_bit_proto(self, actor_sim_id, track_bits, msg):
        for bit in self.get_bit_instances(actor_sim_id):
            if not bit.visible:
                if not bit.invisible_filterable:
                    continue
            if bit.guid64 in track_bits:
                continue
            with ProtocolBufferRollback(msg.bit_updates) as (bit_update):
                bit_update.bit_id = bit.guid64
                bit_timeout_data = self._get_uni_directional_rel_data(actor_sim_id)._find_timeout_data_by_bit_instance(bit)
                if bit_timeout_data is not None:
                    bit_alarm = bit_timeout_data.alarm_handle
                    if bit_alarm is not None:
                        bit_update.end_time = bit_alarm.finishing_time

    def _build_compatibility_proto(self, msg):
        compatibility_level = self.get_compatibility_level()
        if compatibility_level is not None:
            if compatibility_level in CompatibilityTuning.COMPATIBILITY_LEVEL_ICONS_MAP:
                icon_data = CompatibilityTuning.COMPATIBILITY_LEVEL_ICONS_MAP[compatibility_level]
                msg.compatibility.level = compatibility_level
                msg.compatibility.icon = sims4.resources.get_protobuff_for_key(icon_data.icon)
                msg.compatibility.small_icon = sims4.resources.get_protobuff_for_key(icon_data.small_icon)
                msg.compatibility.name = icon_data.level_name
                msg.compatibility.desc = icon_data.descriptive_text

    def _get_paired_sim_infos(self, actor_is_a):
        sim_info_manager = services.sim_info_manager()
        sim_info_a = sim_info_manager.get(self._sim_id_a)
        sim_info_b = sim_info_manager.get(self._sim_id_b)
        if actor_is_a:
            return (
             sim_info_a, sim_info_b)
        return (
         sim_info_b, sim_info_a)

    def add_track_score(self, sim_id, increment, track, apply_cross_age_multipliers=False, **kwargs):
        if not (track.cross_age_multipliers is None or apply_cross_age_multipliers):
            (super().add_track_score)(sim_id, increment, track, **kwargs)
            return
        actor_sim_info, target_sim_info = self._get_paired_sim_infos(self._sim_id_b == sim_id)
        if not ((actor_sim_info is None or target_sim_info is None or actor_sim_info).is_sim and target_sim_info.is_sim):
            (super().add_track_score)(sim_id, increment, track, **kwargs)
            return
        cross_age_multipliers = track.cross_age_multipliers
        multiplier_data = cross_age_multipliers.gain_multipliers if increment >= 0 else cross_age_multipliers.loss_multipliers
        multiplier = multiplier_data.get_value(actor_sim_info.age, target_sim_info.age)
        increment *= multiplier
        (super().add_track_score)(sim_id, increment, track, **kwargs)


class ObjectRelationship(Relationship):
    __slots__ = ('_target_object_id', '_target_object_manager_id', '_target_object_instance_id',
                 '_object_relationship_name')

    def __init__(self, sim_id, obj_def_id):
        self._sim_id_a = sim_id
        self._sim_id_b = obj_def_id
        self._target_object_id = 0
        self._target_object_manager_id = 0
        self._target_object_instance_id = 0
        self._object_relationship_name = None
        super().__init__()

    @classproperty
    def is_object_rel(cls):
        return True

    def save_relationship(self, relationship_msg):
        super().save_relationship(relationship_msg)
        relationship_msg.target_object_id = self._target_object_id
        relationship_msg.target_object_manager_id = self._target_object_manager_id
        relationship_msg.target_object_instance_id = self._target_object_instance_id
        if self._object_relationship_name is not None:
            relationship_msg.object_relationship_name = self._object_relationship_name

    def load_relationship(self, relationship_msg):
        super().load_relationship(relationship_msg)
        self._target_object_id = relationship_msg.target_object_id
        self._target_object_manager_id = relationship_msg.target_object_manager_id
        self._target_object_instance_id = relationship_msg.target_object_instance_id
        if relationship_msg.object_relationship_name:
            self._object_relationship_name = relationship_msg.object_relationship_name

    def get_object_rel_name(self):
        return self._object_relationship_name

    def set_object_rel_name(self, name):
        self._object_relationship_name = name

    def send_relationship_info(self, deltas=None, headline_icon_modifier=None):
        if self.suppress_client_updates:
            return
        else:
            sim_info_a = self.find_sim_info_a()
            if sim_info_a is not None:
                if sim_info_a.is_npc:
                    return
            if sim_info_a is not None:
                op = self._build_object_relationship_update_proto(sim_info_a, (self._sim_id_b), deltas=deltas, name_override=(self.get_object_rel_name()))
                if op is not None:
                    send_relationship_op(sim_info_a, op)

    def _build_object_relationship_update_proto(self, actor_sim_info, member_obj_def_id, deltas=None, name_override=None):
        msg = commodity_protocol.RelationshipUpdate()
        actor_sim_id = actor_sim_info.sim_id
        msg.actor_sim_id = actor_sim_id
        if name_override is not None:
            loc_custom_name = LocalizationHelperTuning.get_raw_text(name_override)
            build_icon_info_msg(IconInfoData(), loc_custom_name, msg.target_icon_override)
        elif self._target_object_id == 0:
            target_object = None
            tag_set = services.relationship_service().get_mapped_tag_set_of_id(member_obj_def_id)
            definition_ids = services.relationship_service().get_ids_of_tag_set(tag_set)
            for definition_id in definition_ids:
                for obj in services.object_manager().objects:
                    if definition_id == obj.definition.id:
                        target_object = obj
                        break

            if target_object is None:
                logger.error('Failed to find an object with requested object tag set in the world,                             so the initial object type relationship creation for sim {} will not complete.', actor_sim_info)
                return
            msg.target_id.object_id, msg.target_id.manager_id = target_object.icon_info
            msg.target_instance_id = target_object.id
            self._target_object_id = msg.target_id.object_id
            self._target_object_manager_id = msg.target_id.manager_id
            self._target_object_instance_id = msg.target_instance_id
        else:
            msg.target_id.object_id = self._target_object_id
            msg.target_id.manager_id = self._target_object_manager_id
            msg.target_instance_id = self._target_object_instance_id
        msg.last_update_time = self._last_update_time
        track_bits = self._build_relationship_track_proto(actor_sim_id, msg)
        self._build_relationship_bit_proto(actor_sim_id, track_bits, msg)
        return msg

    def _build_relationship_bit_proto(self, actor_sim_id, track_bits, msg):
        for bit in self.get_bit_instances(actor_sim_id):
            if not bit.visible:
                if not bit.invisible_filterable:
                    continue
            if bit.guid64 in track_bits:
                continue
            with ProtocolBufferRollback(msg.bit_updates) as (bit_update):
                bit_update.bit_id = bit.guid64