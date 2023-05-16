# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\object_relationship_component.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 36262 bytes
from collections import defaultdict
from event_testing.test_events import TestEvent
from protocolbuffers import DistributorOps_pb2
from protocolbuffers import SimObjectAttributes_pb2 as protocols, Commodities_pb2 as commodity_protocol
from date_and_time import DateAndTime
from distributor.ops import GenericProtocolBufferOp
from distributor.rollback import ProtocolBufferRollback
from distributor.shared_messages import send_relationship_op, build_icon_info_msg, IconInfoData
from distributor.system import Distributor
from interactions.utils.loot_basic_op import BaseTargetedLootOperation
from objects.components import Component, types
from objects.components.object_relationship_social import ObjectRelationshipSocialMixin
from objects.components.state_references import TunableStateValueReference
from relationships.relationship_track import RelationshipTrack
from sims4.callback_utils import CallableList
from sims4.math import Threshold
from sims4.tuning.tunable import TunableRange, Tunable, HasTunableFactory, OptionalTunable, TunableTuple, TunableList, TunableThreshold, TunableResourceKey, AutoFactoryInit
from sims4.tuning.tunable_base import ExportModes
from sims4.tuning.tunable import TunableReference
import statistics.statistic, alarms, date_and_time, services, sims4.log, zone_types
logger = sims4.log.Logger('ObjectRelationshipComponent')

class ObjectRelationshipComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=types.OBJECT_RELATIONSHIP_COMPONENT, persistence_key=protocols.PersistenceMaster.PersistableData.ObjectRelationshipComponent):
    FACTORY_TUNABLES = {'number_of_allowed_relationships':OptionalTunable(description='\n            Number of Sims who can have a relationship with this object at one\n            time.  If not specified, an infinite number of Sims can have a \n            relationship with the object.\n            ',
       tunable=TunableRange(tunable_type=int,
       default=1,
       minimum=1)), 
     'icon_consider_geo_mat_state':Tunable(description="\n            If True, we will consider geometry state and material state of this\n            object when we generate its thumbnail.\n            If False, we will just send this object's catalog id to thumbnail system\n            and its thumbnail will use default geometry/material state. \n            ",
       tunable_type=bool,
       default=False), 
     'icon_override':OptionalTunable(description="\n            If enabled, this will override the object's thumbnail generated \n            default icon on Relationship panel.\n            ",
       tunable=TunableResourceKey(description='\n                The icon to be displayed in the Relationship panel.\n                ',
       resource_types=(sims4.resources.CompoundTypes.IMAGE),
       export_modes=(ExportModes.All))), 
     'relationship_stat':TunableReference(description="\n            The statistic which will be created for each of this object's\n            relationships.\n            ",
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC),
       class_restrictions=('Statistic', 'Commodity')), 
     'relationship_track_visual':OptionalTunable(description='\n            If enabled, the relationship track to send the client and where\n            it should be displayed. If this is None then this relationship will \n            not be sent down to the client.\n            ',
       tunable=TunableTuple(relationship_track=RelationshipTrack.TunableReference(description='\n                    The relationship that this track will visually try and imitate in\n                    regards to static track tack data.\n                    '),
       visible_in_relationship_panel=Tunable(description="\n                    By default the relationship is visible in the relationship \n                    panel and the object's tooltip. If this is set to false, \n                    hide the relationship from the relationship panel. \n                    ",
       tunable_type=bool,
       default=True))), 
     'relationship_based_state_change_tuning':OptionalTunable(TunableTuple(description='\n            A list of value ranges and associated states.  If the active Sim\n            has a relationship with this object  that falls within one of the\n            value ranges specified here, the object will change state to match\n            the specified state.\n            \n            These state changes exist on a per Sim basis, so this tuning will\n            effectively make the same object appear different depending on\n            which Sim is currently active.\n            ',
       state_changes=TunableList(tunable=TunableTuple(value_threshold=TunableThreshold(description="\n                        The range that the active Sim's relationship with this\n                        object must fall within in order for this state change to\n                        take place.\n                        "),
       state=TunableStateValueReference(description="\n                        The state this object will change to if it's relationship\n                        with the active Sim falls within the specified range.\n                        "))),
       default_state=TunableStateValueReference(description='\n                The state this object will change to if there is no other tuned\n                relationship based state change for the currently active Sim.\n                ')))}

    def __init__(self, owner, **kwargs):
        (super().__init__)(owner, **kwargs)
        self._state_changes = None
        self._default_state = None
        self._object_social_mixin = None
        self._relationships = {}
        self._change_rate_changed_alarms = {}
        self._relationship_changed_callbacks = defaultdict(CallableList)
        self._definition_changed_in_buildbuy = False

    @staticmethod
    def setup_relationship(sim, target_object):
        if target_object.objectrelationship_component is None:
            logger.error("Failed to add object relationship because {} doesn't have objectrelationship_component tuned", target_object)
            return
        else:
            if target_object.objectrelationship_component.has_relationship(sim.id):
                logger.error('Relationship already exists between {} and {}.', sim, target_object)
                return
            target_object.objectrelationship_component.add_relationship(sim.id) or logger.error('Failed to add new object relationship between {} and {}.', sim, target_object)

    @property
    def relationships(self):
        return self._relationships

    def get_number_of_allowed_relationships(self):
        return self.number_of_allowed_relationships

    def _on_active_sim_change(self, _, new_sim):
        if new_sim is None:
            return
        relationship = self._get_relationship_stat(new_sim.id)
        self._update_state(relationship)

    def _update_state(self, relationship_stat):
        if self._default_state is None:
            return
        if relationship_stat is None:
            new_state = self._default_state
        else:
            if self._state_changes is None:
                new_state = self._default_state
            else:
                for state_change in self._state_changes:
                    if state_change.value_threshold.compare(relationship_stat.get_value()):
                        new_state = state_change.state
                        break
                else:
                    new_state = self._default_state

                self.owner.set_state(new_state.state, new_state)

    @property
    def _can_add_new_relationship(self):
        if self.number_of_allowed_relationships is not None:
            if len(self._relationships) >= self.number_of_allowed_relationships:
                return False
        return True

    def on_add(self):
        services.current_zone().register_callback(zone_types.ZoneState.HOUSEHOLDS_AND_SIM_INFOS_LOADED, self._publish_relationship_data)
        if self.relationship_based_state_change_tuning is None:
            return
        self._state_changes = self.relationship_based_state_change_tuning.state_changes
        self._default_state = self.relationship_based_state_change_tuning.default_state
        services.current_zone().register_callback(zone_types.ZoneState.CLIENT_CONNECTED, self._register_active_sim_change)

    def on_remove(self):
        client = services.client_manager().get_first_client()
        if client is not None:
            client.unregister_active_sim_changed(self._on_active_sim_change)
        self.owner.remove_name_changed_callback(self._on_name_changed)
        self.destroy_all_relationship()

    def apply_definition(self, definition, obj_state=0):
        if not services.current_zone().is_in_build_buy:
            return
        self._definition_changed_in_buildbuy |= self.owner.definition != definition

    def on_buildbuy_exit(self):
        if not self._definition_changed_in_buildbuy:
            return
        self._publish_relationship_data()
        self._definition_changed_in_buildbuy = False

    def _create_stat_tracker(self, relationship_proto=None):
        if relationship_proto is not None:
            if relationship_proto.HasField('statistics_tracker'):
                if self.relationship_stat.is_commodity:
                    return
            elif relationship_proto.HasField('commodity_tracker'):
                if not self.relationship_stat.is_commodity:
                    return
            else:
                return relationship_proto.HasField('statistics_tracker') or relationship_proto.HasField('commodity_tracker') or None
        if self.relationship_stat.is_commodity:
            return statistics.commodity_tracker.CommodityTracker(self.owner)
        return statistics.statistic_tracker.StatisticTracker(self.owner)

    def _register_active_sim_change(self):
        client = services.client_manager().get_first_client()
        if client is not None:
            client.register_active_sim_changed(self._on_active_sim_change)

    def _publish_relationship_data(self):
        if self.relationship_track_visual is None:
            return
        for sim_id in self._relationships.keys():
            self._send_relationship_data(sim_id)
            self._refresh_change_rate_changed_alarm(sim_id)

    def _update_object_relationship_name(self):
        ownable_component = self.owner.get_component(types.OWNABLE_COMPONENT)
        if ownable_component is not None:
            sim_owner_id = ownable_component.get_sim_owner_id()
            obj_def_id = self.owner.definition.id
            relationship_service = services.relationship_service()
            obj_tag_set = relationship_service.get_mapped_tag_set_of_id(obj_def_id)
            if obj_tag_set is not None:
                obj_relationship = relationship_service.get_object_relationship(sim_owner_id, obj_tag_set)
                if obj_relationship is not None:
                    if self.owner.has_custom_name():
                        obj_relationship.set_object_rel_name(self.owner.custom_name)

    def _on_name_changed(self, *_, **__):
        self._publish_relationship_data()
        self._update_object_relationship_name()

    def _change_rate_changed_callback(self, alarm_handle):
        sim_id = self._change_rate_changed_alarms.get(alarm_handle)
        if sim_id is not None:
            self._send_relationship_data(sim_id)
            self._refresh_change_rate_changed_alarm(sim_id)

    def _remove_change_rate_changed_alarm(self, sim_id):
        for alarm_handle in self._change_rate_changed_alarms:
            if self._change_rate_changed_alarms[alarm_handle] == sim_id:
                alarms.cancel_alarm(alarm_handle)
                del self._change_rate_changed_alarms[alarm_handle]
                return

    def _refresh_change_rate_changed_alarm(self, sim_id):
        self._remove_change_rate_changed_alarm(sim_id)
        stat = self._get_relationship_stat(sim_id)
        if stat is not None:
            if stat.continuous:
                decay_time_minutes = stat.get_decay_time(Threshold(0))
                if decay_time_minutes is None:
                    decay_time_minutes = stat.get_time_till_decay_starts()
                    if decay_time_minutes >= 0:
                        decay_time_minutes += 1
                if decay_time_minutes > 0:
                    decay_time_span = date_and_time.create_time_span(minutes=decay_time_minutes)
                    alarm_handle = alarms.add_alarm(self, decay_time_span, self._change_rate_changed_callback)
                    self._change_rate_changed_alarms[alarm_handle] = sim_id

    def add_relationship_changed_callback_for_sim_id(self, sim_id, callback):
        self._relationship_changed_callbacks[sim_id].append(callback)

    def remove_relationship_changed_callback_for_sim_id(self, sim_id, callback):
        if sim_id in self._relationship_changed_callbacks:
            if callback in self._relationship_changed_callbacks[sim_id]:
                self._relationship_changed_callbacks[sim_id].remove(callback)

    def _trigger_relationship_changed_callbacks_for_sim_id(self, sim_id):
        callbacks = self._relationship_changed_callbacks[sim_id]
        if callbacks is not None:
            callbacks()
        sim_info = services.sim_info_manager().get(sim_id)
        if sim_info is not None:
            services.get_event_manager().process_event((TestEvent.ObjectRelationshipChanged), sim_info=sim_info)

    def add_relationship(self, sim_id, tracker=None):
        if sim_id in self._relationships:
            return False
        else:
            return self._can_add_new_relationship or False
        self.owner.on_hovertip_requested()
        if tracker is None:
            tracker = self._create_stat_tracker()
            tracker.add_statistic(self.relationship_stat)
        self._relationships[sim_id] = tracker
        self._send_relationship_data(sim_id)
        self._trigger_relationship_changed_callbacks_for_sim_id(sim_id)
        self._refresh_change_rate_changed_alarm(sim_id)
        self.owner.add_name_changed_callback(self._on_name_changed)
        return True

    def remove_relationship(self, sim_id):
        if sim_id not in self._relationships:
            return
        del self._relationships[sim_id]
        self._trigger_relationship_changed_callbacks_for_sim_id(sim_id)
        self._remove_change_rate_changed_alarm(sim_id)
        self._send_relationship_destroy(sim_id)

    def destroy_all_relationship(self):
        sim_ids = list(self._relationships.keys())
        for sim_id in sim_ids:
            self.remove_relationship(sim_id)

    def modify_relationship(self, sim_id, value, add=True, set_value=False):
        if sim_id not in self._relationships:
            if not add:
                return
            if not self.add_relationship(sim_id):
                return
        else:
            stat = self._get_relationship_stat(sim_id)
            if set_value:
                stat.set_value(value)
            else:
                stat.add_value(value)
        self._send_relationship_data(sim_id)
        self._trigger_relationship_changed_callbacks_for_sim_id(sim_id)
        self._refresh_change_rate_changed_alarm(sim_id)
        client = services.client_manager().get_first_client()
        if client is not None:
            if client.active_sim is not None:
                if client.active_sim.sim_id == sim_id:
                    self._update_state(stat)

    def on_social_start(self, sim):
        if self.has_relationship(sim.id) or self.add_relationship(sim.id):
            self._object_social_mixin = ObjectRelationshipSocialMixin(sim, self.owner.id, self._get_relationship_stat(sim.id))
            self._object_social_mixin.send_social_start_message()

    def on_social_end(self):
        if self._object_social_mixin is not None:
            self._object_social_mixin.send_social_end_message()
            self._object_social_mixin = None

    def _get_relationship(self, sim_id):
        return self._relationships.get(sim_id)

    def _get_relationship_stat(self, sim_id):
        relationship_tracker = self._get_relationship(sim_id)
        if relationship_tracker is None:
            return
        stat = relationship_tracker.get_statistic(self.relationship_stat)
        if stat is None:
            stat = relationship_tracker.add_statistic(self.relationship_stat)
        return stat

    def has_relationship(self, sim_id):
        return sim_id in self._relationships

    def get_relationship_value(self, sim_id):
        stat = self._get_relationship_stat(sim_id)
        if stat is not None:
            return stat.get_value()
        return self.relationship_stat.initial_value

    def get_relationship_initial_value(self):
        return self.relationship_stat.initial_value

    def get_relationship_max_value(self):
        return self.relationship_stat.max_value

    def get_relationship_min_value(self):
        return self.relationship_stat.min_value

    def get_relationship_change_rate(self, sim_id):
        relationship_stat = self._get_relationship_stat(sim_id)
        if relationship_stat is not None:
            if relationship_stat.continuous:
                return relationship_stat.get_change_rate()
        return 0

    def _send_relationship_data(self, sim_id):
        if self.relationship_track_visual is None:
            return
        else:
            relationship_to_send = self._get_relationship_stat(sim_id)
            if not relationship_to_send:
                return
                sim_info = services.sim_info_manager().get(sim_id)
                if sim_info is None:
                    return
                msg = commodity_protocol.RelationshipUpdate()
                msg.actor_sim_id = sim_id
                msg.target_id.object_id, msg.target_id.manager_id = self.owner.icon_info
                msg.target_instance_id = self.owner.id
                if self.icon_override is not None:
                    build_icon_info_msg(IconInfoData(icon_resource=(self.icon_override)), None, msg.target_icon_override)
            elif self.icon_consider_geo_mat_state:
                icon_info = IconInfoData(obj_def_id=(self.owner.definition.id), obj_geo_hash=(self.owner.geometry_state),
                  obj_material_hash=(self.owner.material_hash))
                build_icon_info_msg(icon_info, None, msg.target_icon_override)
        with ProtocolBufferRollback(msg.tracks) as (relationship_track_update):
            relationship_value = relationship_to_send.get_value()
            relationship_track_update.track_score = relationship_value
            relationship_track_update.track_bit_id = self.relationship_track_visual.relationship_track.get_bit_at_relationship_value(relationship_value).guid64
            relationship_track_update.track_id = self.relationship_track_visual.relationship_track.guid64
            relationship_track_update.track_popup_priority = self.relationship_track_visual.relationship_track.display_popup_priority
            relationship_track_update.visible_in_relationship_panel = self.relationship_track_visual.visible_in_relationship_panel
            relationship_track_update.change_rate = self.get_relationship_change_rate(sim_id)
        send_relationship_op(sim_info, msg)
        if self._object_social_mixin is not None:
            self._object_social_mixin.send_social_update_message()

    def _send_relationship_destroy(self, sim_id):
        if self.relationship_track_visual is None or self.relationship_track_visual.relationship_track is None:
            return
        sim_info = services.sim_info_manager().get(sim_id)
        if sim_info is None:
            return
        msg = commodity_protocol.RelationshipDelete()
        msg.actor_sim_id = sim_id
        msg.target_id = self.owner.id
        op = GenericProtocolBufferOp(DistributorOps_pb2.Operation.SIM_RELATIONSHIP_DELETE, msg)
        distributor = Distributor.instance()
        distributor.add_op(services.sim_info_manager().get(sim_id), op)

    def save(self, persistence_master_message):
        if not self._relationships:
            return
        persistable_data = protocols.PersistenceMaster.PersistableData()
        persistable_data.type = protocols.PersistenceMaster.PersistableData.ObjectRelationshipComponent
        relationship_component_data = persistable_data.Extensions[protocols.PersistableObjectRelationshipComponent.persistable_data]
        for key, value in self._relationships.items():
            stat = value.get_statistic(self.relationship_stat)
            if not stat is None:
                if not stat.persisted_tuning:
                    continue
                with ProtocolBufferRollback(relationship_component_data.relationships) as (relationship_data):
                    relationship_data.sim_id = key
                    relationship_data.value = stat.get_value()
                    if self.relationship_stat.is_commodity:
                        commodities_save, _, _ = value.save()
                        relationship_data.commodity_tracker.commodities.extend(commodities_save)
                        relationship_data.commodity_tracker.time_of_last_save = services.time_service().sim_now.absolute_ticks()
                    else:
                        statistic_save = value.save()
                        relationship_data.statistics_tracker.statistics.extend(statistic_save)

        persistence_master_message.data.extend([persistable_data])

    def load(self, persistable_data):
        relationship_component_data = persistable_data.Extensions[protocols.PersistableObjectRelationshipComponent.persistable_data]
        for relationship in relationship_component_data.relationships:
            tracker = self._create_stat_tracker(relationship_proto=relationship)
            if tracker is None:
                self.modify_relationship((relationship.sim_id), (relationship.value), set_value=True)
                continue
            elif self.relationship_stat.is_commodity:
                tracker.load(relationship.commodity_tracker.commodities)
            else:
                tracker.load(relationship.statistics_tracker.statistics)
            self.add_relationship(relationship.sim_id, tracker)


class ObjectRelationshipLootOp(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'description':'\n            This loot will modify the relationship between an object and a Sim.\n            The target object must have an ObjectRelationshipComponent attached\n            to it for this loot operation to be valid.\n            ', 
     'amount_to_add':Tunable(description='\n            The amount tuned here will be added to the relationship between the\n            tuned object and Sim.\n            ',
       tunable_type=int,
       default=0), 
     'add_if_nonexistant':Tunable(description="\n            If checked, this relationship will be added if it doesn't currently\n            exist.  If unchecked, it will not be added if it doesn't currently\n            exist.\n            ",
       tunable_type=bool,
       default=True), 
     'remove_relationship':Tunable(description='\n            If checked, the relationship between the tuned object and Sim will\n            be remove if it currently exists.\n            ',
       tunable_type=bool,
       default=False)}

    def __init__(self, amount_to_add, add_if_nonexistant, remove_relationship, **kwargs):
        (super().__init__)(**kwargs)
        self.amount_to_add = amount_to_add
        self.add_if_nonexistant = add_if_nonexistant
        self.remove_relationship = remove_relationship

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None or target is None:
            logger.error('Invalid subject or target specified for this loot operation. {}  Please fix in tuning.', self)
            return
        object_relationship = target.objectrelationship_component
        if object_relationship is None:
            logger.error('Target {} has no object relationship component.  Please fix in tuning.', target)
            return
        if self.remove_relationship:
            object_relationship.remove_relationship(subject.id)
            return
        object_relationship.modify_relationship((subject.id), (self.amount_to_add), add=(self.add_if_nonexistant))