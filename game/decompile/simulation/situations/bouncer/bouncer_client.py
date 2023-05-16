# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\bouncer\bouncer_client.py
# Compiled at: 2013-07-05 21:27:35
# Size of source mod 2**32: 2216 bytes


class IBouncerClient:

    def on_sim_assigned_to_request(self, sim, request):
        raise NotImplementedError

    def on_sim_unassigned_from_request(self, sim, request):
        raise NotImplementedError

    def on_sim_replaced_in_request(self, old_sim, new_sim, request):
        raise NotImplementedError

    def on_failed_to_spawn_sim_for_request(self, request):
        raise NotImplementedError

    def on_tardy_request(self, request):
        raise NotImplementedError

    def on_first_assignment_pass_completed(self):
        raise NotImplementedError