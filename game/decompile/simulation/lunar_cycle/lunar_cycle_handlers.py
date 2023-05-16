# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\lunar_cycle\lunar_cycle_handlers.py
# Compiled at: 2022-06-13 18:18:17
# Size of source mod 2**32: 1998 bytes
import services
from date_and_time import TimeSpan
from lunar_cycle.lunar_cycle_enums import LunarPhaseType
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
lunar_phase_schema = GsiGridSchema(label='Lunar Cycle/Lunar Phases')
lunar_phase_schema.add_field('index', label='Phase Index', width=0.1, unique_field=True,
  visualizer=(GsiFieldVisualizers.INT))
lunar_phase_schema.add_field('phase', label='Phase', width=1)
lunar_phase_schema.add_field('start_time', label='Start Time', width=0.2)
lunar_phase_schema.add_field('end_time', label='End Time', width=0.2)
lunar_phase_schema.add_field('expected_length', label='Duration', width=0.1)
lunar_phase_schema.add_field('active', label='Is Active', width=0.1)
with lunar_phase_schema.add_view_cheat('lunar_cycle.set_phase', label='Set Phase') as (set_phase_command):
    set_phase_command.add_token_param('phase')

@GsiHandler('phases_view', lunar_phase_schema)
def generate_phases_view():
    phases = []
    lunar_cycle_service = services.lunar_cycle_service()
    for phase_type in LunarPhaseType:
        active_phase = lunar_cycle_service.current_phase == phase_type
        start_time = 'N/A'
        end_time = 'N/A'
        phase_length = lunar_cycle_service.get_phase_length(phase_type)
        if active_phase:
            start_time = lunar_cycle_service.current_phase_start
            end_time = start_time + phase_length
        phase_data = {'index':phase_type.value,  'phase':str(phase_type.name), 
         'start_time':str(start_time), 
         'end_time':str(end_time), 
         'expected_length':str(phase_length) if phase_length > TimeSpan.ZERO else '', 
         'active':str(active_phase)}
        phases.append(phase_data)

    return phases