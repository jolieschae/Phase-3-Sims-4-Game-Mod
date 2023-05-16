# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\walkstyle_handlers.py
# Compiled at: 2021-06-02 19:59:55
# Size of source mod 2**32: 3305 bytes
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.schema import GsiGridSchema
walkstyle_event_archive_schema = GsiGridSchema(label='Walkstyle Event Archive', sim_specific=True)
walkstyle_event_archive_schema.add_field('default_walkstyle', label='Default Walkstyle')
walkstyle_event_archive_schema.add_field('combo_replacement_walkstyle_found', label='Combo Replacement Walkstyle Found')
walkstyle_event_archive_schema.add_field('default_walkstyle_replaced_by_short_walkstyle', label='Default Walkstyle Replaced by Short Walkstyle')
walkstyle_event_archive_schema.add_field('default_walkstyle_replaced_by_swimming_walkstyle', label='Default Walkstyle Replaced by Swimming Walkstyle')
walkstyle_event_archive_schema.add_field('default_walkstyle_replaced_by_posture_walkstyle', label='Default Walkstyle Replaced by Posture Walkstyle')
with walkstyle_event_archive_schema.add_has_many('Walkstyle Requests', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('walkstyle', label='Walkstyle', width=1)
    sub_schema.add_field('priority', label='Priority', width=1)
    sub_schema.add_field('can_replace_with_short_walkstyle', label='Can Replace With Short Walkstyle', width=1)
archiver = GameplayArchiver('WalkstyleEvents', walkstyle_event_archive_schema, add_to_archive_enable_functions=True)

class WalkstyleGSIArchiver:

    def __init__(self, actor):
        self.sim = actor
        self.default_walkstyle = None
        self.combo_replacement_walkstyle_found = None
        self.default_walkstyle_replaced_by_short_walkstyle = None
        self.default_walkstyle_replaced_by_swimming_walkstyle = None
        self.default_walkstyle_replaced_by_posture_walkstyle = None
        self.walkstyle_requests = None

    def gsi_archive_entry(self):
        entry = {'default_walkstyle':str(self.default_walkstyle), 
         'combo_replacement_walkstyle_found':str(self.combo_replacement_walkstyle_found), 
         'default_walkstyle_replaced_by_short_walkstyle':str(self.default_walkstyle_replaced_by_short_walkstyle), 
         'default_walkstyle_replaced_by_swimming_walkstyle':str(self.default_walkstyle_replaced_by_swimming_walkstyle), 
         'default_walkstyle_replaced_by_posture_walkstyle':str(self.default_walkstyle_replaced_by_posture_walkstyle)}
        requests = []
        entry['Walkstyle Requests'] = requests
        for walkstyle_request in self.walkstyle_requests:
            rel_entry = {'walkstyle':str(walkstyle_request.walkstyle),  'priority':walkstyle_request.priority, 
             'can_replace_with_short_walkstyle':walkstyle_request.can_replace_with_short_walkstyle}
            requests.append(rel_entry)

        archiver.archive(data=entry, object_id=(self.sim.id))