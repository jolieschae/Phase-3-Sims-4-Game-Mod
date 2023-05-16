# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\relationship_metrics_handlers.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 17270 bytes
import services
from gsi_handlers.gsi_utils import parse_filter_to_list
from objects import ALL_HIDDEN_REASONS
from objects.components.types import OBJECT_RELATIONSHIP_COMPONENT
from relationships.relationship_enums import RelationshipDirection
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
FILTER_INSTANCED_SIM_INFOS = 'instanced_sim_infos'
FILTER_ALL_SIM_INFOS = 'all_sim_infos'
FILTER_INSTANCED_OBJECTS = 'instanced_objects'
FIELD_TARGET_NAME = 'target'
FIELD_TOTAL_SENTIMENT = 'total_sentiments'
FIELD_SENTIMENTS_TO = 'sentiments_to'
FIELD_SENTIMENT_FROM = 'sentiments_from'
FIELD_TOTAL_REL_BITS = 'total_rel_bits'
FIELD_TRACK_NAME = 'track_name'
FIELD_VALUE = 'value'
FIELD_TYPE = 'type'
FIELD_BIT_NAME = 'bit_name'
FIELD_TIME_OUT = 'time_out'
FIELD_SENTIMENT_NAME = 'sentiment_name'
FIELD_IS_BIDIRECTIONAL_BIT = 'is_bidirectional_bit'
relationship_metrics_schema = GsiGridSchema(label='Relationship Metrics')
relationship_metrics_schema.add_field('name', label='Name')
relationship_metrics_schema.add_field('instanced', label='Instanced')
relationship_metrics_schema.add_field('lod', label='LOD')
relationship_metrics_schema.add_field('num_total_stats', label='Total Stats(tracks + sentiments)', type=(GsiFieldVisualizers.INT))
relationship_metrics_schema.add_field('num_total_relationships', label='Total Relationships', type=(GsiFieldVisualizers.INT))
relationship_metrics_schema.add_field('num_sentiments_to', label='Sentiments To', type=(GsiFieldVisualizers.INT))
relationship_metrics_schema.add_field('num_sentiments_from', label='Sentiments From', type=(GsiFieldVisualizers.INT))
with relationship_metrics_schema.add_has_many('total', GsiGridSchema) as (sub_schema):
    sub_schema.add_field(FIELD_TARGET_NAME, label='Target Name', width=2)
    sub_schema.add_field(FIELD_TOTAL_SENTIMENT, label='Total Sentiments', width=2)
    sub_schema.add_field(FIELD_SENTIMENTS_TO, label='Sentiments To', width=2)
    sub_schema.add_field(FIELD_SENTIMENT_FROM, label='Sentiments From', width=2)
    sub_schema.add_field(FIELD_TOTAL_REL_BITS, label='Total relationship bits', width=2)
with relationship_metrics_schema.add_has_many('tracks', GsiGridSchema) as (sub_schema):
    sub_schema.add_field(FIELD_TRACK_NAME, label='Track', width=2)
    sub_schema.add_field(FIELD_TARGET_NAME, label='Target Sim', width=2)
    sub_schema.add_field(FIELD_VALUE, label='Value', width=2)
    sub_schema.add_field(FIELD_TYPE, label='Type', width=2)
with relationship_metrics_schema.add_has_many('bits', GsiGridSchema) as (sub_schema):
    sub_schema.add_field(FIELD_BIT_NAME, label='Bit', width=2)
    sub_schema.add_field(FIELD_TARGET_NAME, label='Target Sim', width=2)
    sub_schema.add_field(FIELD_TIME_OUT, label='Time Out', width=2)
    sub_schema.add_field(FIELD_IS_BIDIRECTIONAL_BIT, label='Is Bidirectional Bit', width=2)
with relationship_metrics_schema.add_has_many(FIELD_SENTIMENTS_TO, GsiGridSchema) as (sub_schema):
    sub_schema.add_field(FIELD_SENTIMENT_NAME, label='Sentiment', width=2)
    sub_schema.add_field(FIELD_TARGET_NAME, label='Target Sim', width=2)
    sub_schema.add_field(FIELD_VALUE, label='Value', width=2)
    sub_schema.add_field(FIELD_TYPE, label='Term(Short/Long)', width=2)
with relationship_metrics_schema.add_has_many(FIELD_SENTIMENT_FROM, GsiGridSchema) as (sub_schema):
    sub_schema.add_field(FIELD_SENTIMENT_NAME, label='Sentiment', width=2)
    sub_schema.add_field(FIELD_TARGET_NAME, label='From Sim', width=2)
    sub_schema.add_field(FIELD_VALUE, label='Value', width=2)
    sub_schema.add_field(FIELD_TYPE, label='Term(Short/Long)', width=2)
    relationship_metrics_schema.add_filter(FILTER_INSTANCED_SIM_INFOS)
    relationship_metrics_schema.add_filter(FILTER_ALL_SIM_INFOS)
    relationship_metrics_schema.add_filter(FILTER_INSTANCED_OBJECTS)

def _find_bit_time_out_data(rel, sim_id, bit):
    time_out_seconds = None
    bit_timeout_data = rel.get_bi_directional_rel_data().find_timeout_data_by_bit(bit)
    if bit_timeout_data is None:
        if not rel.is_object_rel:
            bit_timeout_data = rel.get_uni_directional_rel_data(sim_id).find_timeout_data_by_bit(bit)
    if bit_timeout_data is not None:
        bit_alarm = bit_timeout_data.alarm_handle
        time_out_remaining = bit_alarm.get_remaining_time()
        time_out_seconds = time_out_remaining.in_seconds()
    return time_out_seconds


def _populate_data(data, general_info_data, track_data, bit_data, sentiment_to_data, sentiment_from_data, total_stats, total_sentiments_to, total_sentiments_from, total_relationship):
    data['total'] = general_info_data
    data['tracks'] = track_data
    data['bits'] = bit_data
    data[FIELD_SENTIMENTS_TO] = sentiment_to_data
    data[FIELD_SENTIMENT_FROM] = sentiment_from_data
    data['num_total_stats'] = total_stats
    data['num_sentiments_to'] = total_sentiments_to
    data['num_sentiments_from'] = total_sentiments_from
    data['num_total_relationships'] = total_relationship


def _build_track_data(track, target_name, is_object_track=False):
    if is_object_track:
        track_type = 'OBJECT_TRACK'
    else:
        if track.is_short_term_context:
            track_type = 'SHORT'
        else:
            track_type = 'LONG'
    track_data_for_one = {FIELD_TRACK_NAME: track.__class__.__name__, 
     FIELD_TARGET_NAME: target_name, 
     FIELD_VALUE: track.get_user_value(), 
     FIELD_TYPE: track_type}
    return track_data_for_one


def _build_sentiment_data(sentiment, target_name):
    sentiment_data_for_one = {FIELD_SENTIMENT_NAME: sentiment.__class__.__name__, 
     FIELD_TARGET_NAME: target_name, 
     FIELD_VALUE: sentiment.get_user_value(), 
     FIELD_TYPE: sentiment.duration.name}
    return sentiment_data_for_one


def _build_bit_data(bit, target_name, rel, sim_id):
    bit_data_for_one = {FIELD_BIT_NAME: bit.__name__, 
     FIELD_TARGET_NAME: target_name, 
     FIELD_TIME_OUT: _find_bit_time_out_data(rel, sim_id, bit), 
     FIELD_IS_BIDIRECTIONAL_BIT: 'True' if bit.directionality == RelationshipDirection.BIDIRECTIONAL else 'False'}
    return bit_data_for_one


def _build_general_info_data(target_name, total_sentiments, sentiments_to, sentiments_from, total_rel_bits):
    general_info_for_one = {FIELD_TARGET_NAME: target_name, 
     FIELD_TOTAL_SENTIMENT: total_sentiments, 
     FIELD_SENTIMENTS_TO: sentiments_to, 
     FIELD_SENTIMENT_FROM: sentiments_from, 
     FIELD_TOTAL_REL_BITS: total_rel_bits}
    return general_info_for_one


def populate_object_data_from_relationship_component(obj, data):
    obj_rel_component = obj.get_component(OBJECT_RELATIONSHIP_COMPONENT)
    obj_relationships = obj_rel_component.relationships
    general_info_data = []
    num_stats = 0
    for target_sim_id in obj_relationships:
        general_info_for_one = {}
        target_sim_info = services.sim_info_manager().get(target_sim_id)
        if target_sim_info is not None:
            general_info_for_one[FIELD_TARGET_NAME] = target_sim_info.full_name
        num_stats = num_stats + len(obj_relationships[target_sim_id])
        general_info_data.append(general_info_for_one)

    _populate_data(data, general_info_data, [], [], [], [], num_stats, 0, 0, len(obj_relationships))


def populate_object_data_from_relationship_tracker(all_obj_relationships, data):
    general_info_data = []
    track_data = []
    bit_data = []
    total_stats = 0
    for rel in all_obj_relationships:
        target_sim_id = rel.sim_id_a
        target_sim_info = rel.find_sim_info_a()
        for track in rel.relationship_track_tracker:
            track_data.append(_build_track_data(track, (target_sim_info.full_name), is_object_track=True))
            total_stats += 1

        current_total_bits = 0
        for bit in rel.get_bits(target_sim_id):
            bit_data.append(_build_bit_data(bit, target_sim_info.full_name, rel, target_sim_id))
            current_total_bits = current_total_bits + 1

        general_info_data.append(_build_general_info_data(target_sim_info.full_name, 0, 0, 0, current_total_bits))

    _populate_data(data, general_info_data, track_data, bit_data, [], [], total_stats, 0, 0, len(all_obj_relationships))


def populate_data_from_relationship(sim_info, data):
    sim_id = sim_info.sim_id
    relationship_service = services.relationship_service()
    all_sim_relationships = relationship_service.get_all_sim_relationships(sim_id)
    all_sim_obj_relationship = relationship_service.get_all_sim_object_relationships(sim_id)
    general_info_data = []
    track_data = []
    bit_data = []
    sentiment_to_data = []
    sentiment_from_data = []
    total_stats = 0
    total_sentiments_to = 0
    total_sentiments_from = 0
    for rel in all_sim_relationships:
        target_sim_id = rel.get_other_sim_id(sim_id)
        target_sim_info = services.sim_info_manager().get(target_sim_id)
        current_total_tracks = 0
        for track in rel.relationship_track_tracker:
            track_data.append(_build_track_data(track, target_sim_info.full_name))
            current_total_tracks = current_total_tracks + 1

        current_total_sentiments_to = 0
        for sentiment in rel.sentiment_track_tracker(sim_id):
            sentiment_to_data.append(_build_sentiment_data(sentiment, target_sim_info.full_name))
            current_total_sentiments_to = current_total_sentiments_to + 1

        current_total_sentiments_from = 0
        for sentiment in rel.sentiment_track_tracker(target_sim_id):
            sentiment_from_data.append(_build_sentiment_data(sentiment, target_sim_info.full_name))
            current_total_sentiments_from = current_total_sentiments_from + 1

        current_total_bits = 0
        for bit in rel.get_bits(sim_id):
            current_total_bits = current_total_bits + 1
            bit_data.append(_build_bit_data(bit, target_sim_info.full_name, rel, sim_id))

        general_info_data.append(_build_general_info_data(target_sim_info.full_name, current_total_sentiments_from + current_total_sentiments_to, current_total_sentiments_to, current_total_sentiments_from, current_total_bits))
        total_sentiments_to += current_total_sentiments_to
        total_sentiments_from += current_total_sentiments_from
        total_stats += current_total_tracks + current_total_sentiments_from + current_total_sentiments_to

    for rel in all_sim_obj_relationship:
        obj_def = rel.find_member_obj_b()
        target_name = None
        if obj_def is not None:
            target_name = str(obj_def)
        current_total_tracks = 0
        for track in rel.relationship_track_tracker:
            track_data.append(_build_track_data(track, target_name, is_object_track=True))
            current_total_tracks = current_total_tracks + 1

        current_total_bits = 0
        for bit in rel.get_bits(sim_id):
            bit_data.append(_build_bit_data(bit, target_name, rel, sim_id))
            current_total_bits = current_total_bits + 1

        general_info_data.append(_build_general_info_data(target_name, 0, 0, 0, current_total_bits))
        total_stats += current_total_tracks

    _populate_data(data, general_info_data, track_data, bit_data, sentiment_to_data, sentiment_from_data, total_stats, total_sentiments_to, total_sentiments_from, len(all_sim_relationships) + len(all_sim_obj_relationship))


@GsiHandler('relationship_metrics_handlers.py', relationship_metrics_schema)
def generate_relationship_metric_data(*args, zone_id: int=None, filter=None, **kwargs):
    filter_list = parse_filter_to_list(filter)
    all_data = []
    if filter_list is None:
        return all_data
    if FILTER_ALL_SIM_INFOS in filter_list or FILTER_INSTANCED_SIM_INFOS in filter_list:
        for sim_info in list(services.sim_info_manager().objects):
            data = {}
            is_instanced = sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if FILTER_ALL_SIM_INFOS not in filter_list:
                if not is_instanced:
                    continue
            data['name'] = str(sim_info)
            data['instanced'] = str(is_instanced)
            data['lod'] = str(sim_info.lod)
            populate_data_from_relationship(sim_info, data)
            all_data.append(data)

    if FILTER_INSTANCED_OBJECTS in filter_list:
        for obj in list(services.object_manager(zone_id).objects):
            data = {}
            relationship_service = services.relationship_service()
            obj_tag_set = relationship_service.get_mapped_tag_set_of_id(obj.definition.id)
            object_relationship_list = relationship_service.get_all_object_sim_relationships(obj_tag_set)
            if obj_tag_set:
                if len(object_relationship_list) > 0:
                    data['name'] = str(obj)
                    data['instanced'] = 'Yes'
                    data['lod'] = 'NO LOD SUPPORT'
                    populate_object_data_from_relationship_tracker(object_relationship_list, data)
                    all_data.append(data)
            if obj.has_component(OBJECT_RELATIONSHIP_COMPONENT):
                data['name'] = str(obj)
                data['instanced'] = 'Yes'
                data['lod'] = 'NO LOD SUPPORT'
                populate_object_data_from_relationship_component(obj, data)
                all_data.append(data)

    return all_data