# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\ensemble_handlers.py
# Compiled at: 2017-05-11 22:07:54
# Size of source mod 2**32: 1991 bytes
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema
import services
ensemble_service_schema = GsiGridSchema(label='Ensemble Service')
ensemble_service_schema.add_field('ensemble_type', label='Ensemble Type')
ensemble_service_schema.add_field('number_of_sims', label='Number of Sims')
ensemble_service_schema.add_field('last_floor', label='Last Floor')
ensemble_service_schema.add_field('last_center_of_mass', label='Last Center Of Mass')
with ensemble_service_schema.add_has_many('Sims', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('sim_name', label='Sim')
    sub_schema.add_field('floor', label='Floor')
ensemble_service_schema.add_view_cheat('debugvis.ensembles.start', label='Start Visualization')
ensemble_service_schema.add_view_cheat('debugvis.ensembles.stop', label='Stop Visualization')

@GsiHandler('ensemble_service', ensemble_service_schema)
def generate_drama_scheduler_data(zone_id: int=None):
    all_ensembles = []
    ensemble_service = services.ensemble_service()
    if ensemble_service is None:
        return all_ensembles
    for ensemble in ensemble_service.get_all_ensembles():
        sim_data = []
        for sim in ensemble._sims:
            sim_data.append({'sim_name':sim.full_name, 
             'floor':sim.level})

        all_ensembles.append({'ensemble_type':str(ensemble), 
         'number_of_sims':len(ensemble._sims), 
         'last_floor':ensemble.last_selected_level if ensemble.last_selected_level is not None else 0, 
         'last_center_of_mass':str(ensemble.last_center_of_mass) if ensemble.last_center_of_mass is not None else 0, 
         'Sims':sim_data})

    return all_ensembles