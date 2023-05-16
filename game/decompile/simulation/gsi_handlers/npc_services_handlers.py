# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\npc_services_handlers.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 3046 bytes
import services
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema
from sims.sim_info import SimInfo
npc_service_schema = GsiGridSchema(label='NPC Services')
npc_service_schema.add_field('service', label='Service Tuning', width=1, unique_field=True)
npc_service_schema.add_field('scheduled_arrival_time', label='Scheduled Arrival time', width=1)
npc_service_schema.add_field('arrival_time', label='Estimated Arrival time (Randomly picked in service work hours)', width=1)
with npc_service_schema.add_has_many('mailman_delivery', GsiGridSchema, label='Mailman') as (sub_schema):
    sub_schema.add_field('content', label='Contents', width=1)
    sub_schema.add_field('household', label='Household Recipient', width=1)
    sub_schema.add_field('sim', label='Sim Recipient', width=1)

@GsiHandler('npc_services', npc_service_schema)
def generate_mail_data(zone_id: int=None):
    zone = services.get_zone(zone_id)
    npc_service_data = []
    active_household = services.active_household()
    mailbox_inventory = zone.lot.get_hidden_inventory()
    npc_service = services.get_service_npc_service()
    if npc_service is None:
        return npc_service_data
    pending_npc_requests = npc_service.get_service_npc_requests()
    now = services.time_service().sim_now
    mailman_npc_service = 'ServiceNpc_Mailman'
    for service_request in pending_npc_requests:
        alarm_finishing_time = service_request.get_alarm_finishing_time()
        if alarm_finishing_time is None:
            continue
        scheduled_arrival_time = str(alarm_finishing_time - now)
        random_handles = service_request.get_random_alarm_handles()
        arrival_time = 'Unknown' if len(random_handles) == 0 else str(random_handles[0].finishing_time - now)
        service_entry = {'service':str(service_request.extra_data.service_npc_type), 
         'scheduled_arrival_time':scheduled_arrival_time, 
         'arrival_time':arrival_time}
        if service_request.extra_data.service_npc_type.__name__ == mailman_npc_service:
            mail_entries = []
            for item in mailbox_inventory:
                stored_sim_info_component = item.storedsiminfo_component
                sim_name = None
                if stored_sim_info_component is not None:
                    sim_name_data = stored_sim_info_component.get_stored_sim_name_data()
                    sim_name = sim_name_data.first_name + ' ' + sim_name_data.last_name
                mail_entries.append({'content':str(item.definition), 
                 'household':active_household.name, 
                 'sim':sim_name})

            service_entry['mailman_delivery'] = mail_entries
        npc_service_data.append(service_entry)

    return npc_service_data