# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\buff_handlers.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 5224 bytes
from buffs.buff_display_type import BuffDisplayType
from gsi_handlers.gameplay_archiver import GameplayArchiver
from objects.components.buff_component import BuffUpdateType
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
import services, sims4.resources
from protocolbuffers import Sims_pb2
sim_buff_log_schema = GsiGridSchema(label='Buffs Log', sim_specific=True)
sim_buff_log_schema.add_field('buff_id', label='Buff ID', type=(GsiFieldVisualizers.INT), width=0.5)
sim_buff_log_schema.add_field('buff_name', label='Name', width=2)
sim_buff_log_schema.add_field('update_type', label='Update Type', width=1)
sim_buff_log_schema.add_field('buff_reason', label='Reason', width=1)
sim_buff_log_schema.add_field('display_type', label='Display Type', width=2, hidden=True)
sim_buff_log_schema.add_field('timeout', label='Timeout', width=2)
sim_buff_log_schema.add_field('rate', label='Rate', width=2)
sim_buff_log_schema.add_field('is_mood_buff', label='Is Mood Buff', width=2)
sim_buff_log_schema.add_field('progress_arrow', label='Progress Arrow', width=2)
sim_buff_log_schema.add_field('commodity_guid', label='Commodity Guid', type=(GsiFieldVisualizers.INT), hidden=True)
sim_buff_log_schema.add_field('transition_into_buff_id', label='Next Buff ID', type=(GsiFieldVisualizers.INT), hidden=True)
sim_buff_log_archiver = GameplayArchiver('sim_buff_log', sim_buff_log_schema)

def archive_buff_message(buff_msg, shows_timeout, change_rate):
    buff_reason = hex(buff_msg.reason.hash) if buff_msg.HasField('reason') else None
    entry = {'buff_id':buff_msg.buff_id,  'update_type':str(BuffUpdateType(buff_msg.update_type)), 
     'buff_reason':buff_reason, 
     'display_type':str(BuffDisplayType(buff_msg.display_type)), 
     'is_mood_buff':buff_msg.is_mood_buff, 
     'commodity_guid':buff_msg.commodity_guid, 
     'transition_into_buff_id':buff_msg.transition_into_buff_id}
    manager = services.get_instance_manager(sims4.resources.Types.BUFF)
    if manager:
        buff_cls = manager.get(buff_msg.buff_id)
        entry['buff_name'] = buff_cls.__name__
    elif buff_msg.update_type != BuffUpdateType.REMOVE:
        if shows_timeout:
            if buff_msg.timeout:
                entry['timeout'] = buff_msg.timeout
                entry['rate'] = buff_msg.rate_multiplier
            if change_rate is not None:
                if buff_msg.buff_progress == Sims_pb2.BUFF_PROGRESS_NONE:
                    entry['progress_arrow'] = 'No Arrow'
                else:
                    if buff_msg.buff_progress == Sims_pb2.BUFF_PROGRESS_UP:
                        entry['progress_arrow'] = 'Arrow Up'
                    else:
                        entry['progress_arrow'] = 'Arrow Down'
    if buff_msg.HasField('mood_type_override'):
        entry['mood_type_override'] = buff_msg.mood_type_override
    sim_buff_log_archiver.archive(data=entry, object_id=(buff_msg.sim_id))


sim_mood_log_schema = GsiGridSchema(label='Mood Log', sim_specific=True)
sim_mood_log_schema.add_field('mood_id', label='Mood ID', type=(GsiFieldVisualizers.INT), width=0.5)
sim_mood_log_schema.add_field('mood_name', label='Name', width=2)
sim_mood_log_schema.add_field('mood_intensity', label='Intensity', width=2)
with sim_mood_log_schema.add_has_many('active_buffs', GsiGridSchema, label='Buffs at update') as (sub_schema):
    sub_schema.add_field('buff_id', label='Buff ID')
    sub_schema.add_field('buff_name', label='Buff name')
    sub_schema.add_field('buff_mood', label='Buff Mood')
    sub_schema.add_field('buff_mood_override', label='Mood Override (current)')
    sub_schema.add_field('buff_mood_override_pending', label='Mood Override (pending)')
sim_mood_log_archiver = GameplayArchiver('sim_mood_log', sim_mood_log_schema)

def archive_mood_message(sim_id, active_mood, active_mood_intensity, active_buffs, changeable_buffs):
    mood_entry = {'mood_id':active_mood.guid64, 
     'mood_name':active_mood.__name__, 
     'mood_intensity':active_mood_intensity}
    active_buff_entries = []
    for buff_type, buff in active_buffs.items():
        buff_entry = {'buff_id':buff_type.guid64, 
         'buff_name':buff_type.__name__, 
         'buff_mood':buff.mood_type.__name__ if buff.mood_type is not None else 'None', 
         'buff_mood_override':buff.mood_override.__name__ if buff.mood_override is not None else 'None'}
        for changeable_buff, new_mood_override in changeable_buffs:
            if changeable_buff is buff:
                buff_entry['buff_mood_override_pending'] = 'None' if new_mood_override is None else new_mood_override.__name__
                break

        active_buff_entries.append(buff_entry)

    mood_entry['active_buffs'] = active_buff_entries
    sim_mood_log_archiver.archive(data=mood_entry, object_id=sim_id)