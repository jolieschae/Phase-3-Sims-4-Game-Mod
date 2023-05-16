# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\reload_service.py
# Compiled at: 2017-09-03 18:13:38
# Size of source mod 2**32: 2120 bytes
from sims4.service_manager import Service
import sims4.core_services, sims4.log, sims4.reload, sims4.callback_utils, sims4.tuning.tunable
if sims4.core_services.SUPPORT_RELOADING_SCRIPTS:
    __all__ = ('ReloadService', 'trigger_reload')
    logger = sims4.log.Logger('Reload')
    SET_NAME = 'ReloadService'

    class ReloadService(Service):

        def start(self):
            sims4.core_services.directory_watcher_manager().create_set(SET_NAME)

        def stop(self):
            sims4.core_services.directory_watcher_manager().remove_set(SET_NAME)


    def trigger_reload(output=None):
        sims4.callback_utils.invoke_callbacks(sims4.callback_utils.CallbackEvent.TUNING_CODE_RELOAD)
        filenames = list(sims4.core_services.directory_watcher_manager().consume_set(SET_NAME))
        reload_files(filenames, output=output)


    def reload_files(file_list, output=None):
        sims4.tuning.tunable.clear_class_scan_cache()
        for filename in sorted(file_list):
            if sims4.reload.get_module_for_filename(filename) is None:
                continue
            msg = 'Reload: {}'.format(filename)
            logger.warn(msg)
            if output:
                output(msg)
            try:
                sims4.reload.reload_file(filename)
            except BaseException:
                msg = 'Exception caught while reloading {}'.format(filename)
                logger.exception(msg)
                if output:
                    output(msg)
                    for line in sims4.log.format_exc().split('\n'):
                        output(line)

                sims4.core_services.directory_watcher_manager().register_change(filename, SET_NAME)