# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\core_services.py
# Compiled at: 2017-06-06 14:11:39
# Size of source mod 2**32: 6834 bytes
import paths, sims4.reload
SUPPORT_RELOADING_SCRIPTS = False and not paths.IS_ARCHIVE and paths.SCRIPT_ROOT is not None
SUPPORT_GSI = False
with sims4.reload.protected(globals()):
    service_manager = None
    if paths.SUPPORT_RELOADING_RESOURCES:
        _file_change_manager = None
    if SUPPORT_RELOADING_SCRIPTS:
        _directory_watcher_manager = None
    if SUPPORT_GSI:
        _command_buffer_service = None
    _http_service = None
    defer_tuning_references = True

def file_change_manager():
    global _file_change_manager
    if paths.SUPPORT_RELOADING_RESOURCES:
        return _file_change_manager
    raise RuntimeError('The FileChangeService is not available')


def directory_watcher_manager():
    global _directory_watcher_manager
    if SUPPORT_RELOADING_SCRIPTS:
        return _directory_watcher_manager
    raise RuntimeError('The DirectoryWatcherService is not available')


def command_buffer_service():
    global _command_buffer_service
    if SUPPORT_GSI:
        return _command_buffer_service
    raise RuntimeError('The CommandBufferService is not available')


def http_service():
    global _http_service
    return _http_service


def start_services(init_critical_services, services):
    global _command_buffer_service
    global _directory_watcher_manager
    global _file_change_manager
    global _http_service
    global defer_tuning_references
    global service_manager
    service_manager = sims4.service_manager.ServiceManager()
    defer_tuning_references = False
    if paths.SUPPORT_RELOADING_RESOURCES:
        if _file_change_manager is not None:
            raise RuntimeError('The FileChangeService has already been created.')
        from sims4.file_change_service import FileChangeService
        _file_change_manager = FileChangeService()
        services.insert(0, _file_change_manager)
    if SUPPORT_RELOADING_SCRIPTS:
        if _directory_watcher_manager is not None:
            raise RuntimeError('The DirectoryWatcherService has already been created.')
        from sims4.reload_service import ReloadService
        from sims4.directory_watcher_service import DirectoryWatcherService
        _directory_watcher_manager = DirectoryWatcherService()
        _directory_watcher_manager.set_paths([paths.SCRIPT_ROOT], 'script_root')
        services.insert(0, _directory_watcher_manager)
        services.append(ReloadService)
    if SUPPORT_GSI:
        if _command_buffer_service is not None:
            raise RuntimeError('The CommandBufferService has already been created.')
        if _http_service is not None:
            raise RuntimeError('The HttpService has already been created.')
        from sims4.gsi.command_buffer import CommandBufferService
        from sims4.gsi.http_service import HttpService
        _command_buffer_service = CommandBufferService()
        _http_service = HttpService()
        services.insert(0, _command_buffer_service)
        services.insert(1, _http_service)
    for service in init_critical_services:
        service_manager.register_service(service, is_init_critical=True)

    for service in services:
        service_manager.register_service(service)

    service_manager.start_services(defer_start_to_tick=True)


def start_service_tick():
    if service_manager is None:
        raise RuntimeError('Service manager is is not initialized')
    return service_manager.start_single_service()


def stop_services():
    global _command_buffer_service
    global _directory_watcher_manager
    global _file_change_manager
    global _http_service
    global service_manager
    service_manager.stop_services()
    service_manager = None
    if paths.SUPPORT_RELOADING_RESOURCES:
        _file_change_manager = None
    if SUPPORT_RELOADING_SCRIPTS:
        _directory_watcher_manager = None
    if SUPPORT_GSI:
        _command_buffer_service = None
        _http_service = None


def on_tick():
    if SUPPORT_RELOADING_SCRIPTS:
        _directory_watcher_manager.on_tick()
    if SUPPORT_GSI:
        _command_buffer_service.on_tick()
        _http_service.on_tick()