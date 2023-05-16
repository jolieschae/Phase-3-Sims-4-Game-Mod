# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\prep_tasks\prep_task_tracker_mixin.py
# Compiled at: 2020-02-13 14:06:36
# Size of source mod 2**32: 1890 bytes
from careers.prep_tasks.prep_tasks_tracker import PrepTaskTracker
import sims4.log
logger = sims4.log.Logger('Prep Tasks', default_owner='jdimailig')

class PrepTaskTrackerMixin:

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._prep_task_tracker = None

    def prep_time_start(self, owning_sim_info, prep_tasks, gig_uid, audio_on_task_complete, from_load=False):
        if not from_load:
            if self._prep_task_tracker is not None:
                logger.error('Attempting to start prep task time when tracker is already populated.')
                self._prep_task_tracker.on_prep_time_end()
                self._prep_task_tracker.cleanup_prep_statistics()
        self._prep_task_tracker = PrepTaskTracker(owning_sim_info, gig_uid, prep_tasks, audio_on_task_complete)
        self._prep_task_tracker.on_prep_time_start()

    def prep_time_end(self):
        if self._prep_task_tracker is not None:
            self._prep_task_tracker.on_prep_time_end()

    def prep_task_cleanup(self):
        if self._prep_task_tracker is not None:
            self._prep_task_tracker.cleanup_prep_statistics()
            self._prep_task_tracker = None