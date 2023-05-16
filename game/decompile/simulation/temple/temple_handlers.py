# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\temple\temple_handlers.py
# Compiled at: 2017-08-28 21:07:17
# Size of source mod 2**32: 2030 bytes
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
from temple.temple_tuning import TempleTuning
from temple.temple_utils import TempleUtils
temple_schema = GsiGridSchema(label='Temple', sim_specific=False)
temple_schema.add_field('temple_id', label='Temple ID', unique_field=True)
temple_schema.add_field('room_count', label='Room Count')
temple_schema.add_field('current_room', label='Current Room')
with temple_schema.add_has_many('rooms', GsiGridSchema, label='Rooms') as (gates_schema):
    gates_schema.add_field('room_number', label='Room', width=1)
    gates_schema.add_field('gate_state', label='Gate State', type=(GsiFieldVisualizers.STRING), width=4)
    gates_schema.add_field('trigger_object', label='Trigger Object', type=(GsiFieldVisualizers.STRING), width=4)
    gates_schema.add_field('trigger_interaction', label='Trigger Interaction', type=(GsiFieldVisualizers.STRING), width=4)

@GsiHandler('temple', temple_schema)
def generate_temple_view(zone_id: int=None):
    zone_director = TempleUtils.get_temple_zone_director()
    if zone_director is None:
        return (
         {'temple_id':0,  'room_count':0, 
          'current_room':0},)
    temple_data = {'temple_id':zone_director._temple_id, 
     'room_count':zone_director.room_count, 
     'current_room':zone_director._current_room}
    rooms = []
    temple_data['rooms'] = rooms
    for i, room_data in enumerate(zone_director.room_data):
        rooms.append({'room_number':i, 
         'gate_state':str(room_data.gate.get_state(TempleTuning.GATE_STATE)) if room_data.gate is not None else 'None', 
         'trigger_object':str(room_data.trigger_object), 
         'trigger_interaction':str(room_data.trigger_interaction)})

    return (temple_data,)