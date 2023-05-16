# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\paths.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 10355 bytes
import argparse, os.path, sys, sims4.resources
try:
    import __app_paths__
except ImportError:

    class __app_paths__:

        @staticmethod
        def configure_app_paths(pathroot, from_archive, user_script_roots, layers):
            pass


IS_ARCHIVE = False
DEBUG_AVAILABLE = False
LOCAL_WORK_ENABLED = False
DATA_ROOT = None
APP_ROOT = None
SCRIPT_ROOT = None
USER_SCRIPT_ROOTS = None
TUNING_ROOTS = None
LAYERS = None
_CORE = None
AUTOMATION_MODE = False
SUPPORT_RELOADING_RESOURCES = False
IS_DESKTOP = True
DUMP_ROOT = None
DLL_PATH = None
TRACEMALLOC_TUNING_SNAPSHOT = False
TREE_DUMP_TUNING_SNAPSHOT_BEFORE_ZONE = False
TREE_DUMP_TUNING_SNAPSHOT_AFTER_ZONE = False
MEM_REPORT_ZONE_SNAPSHOT = False

def init(pathroot, localwork, from_archive, deploy_override=None, app_directory=None, debug_available=False, local_work_enabled=False, automation_mode=False, tracemalloc_tuning_snapshot=False, dump_root=None):
    global APP_ROOT
    global AUTOMATION_MODE
    global DATA_ROOT
    global DEBUG_AVAILABLE
    global DLL_PATH
    global DUMP_ROOT
    global IS_ARCHIVE
    global LAYERS
    global MEM_REPORT_ZONE_SNAPSHOT
    global SCRIPT_ROOT
    global TRACEMALLOC_TUNING_SNAPSHOT
    global TREE_DUMP_TUNING_SNAPSHOT_AFTER_ZONE
    global TREE_DUMP_TUNING_SNAPSHOT_BEFORE_ZONE
    global TUNING_ROOTS
    global USER_SCRIPT_ROOTS
    global _CORE
    parser = argparse.ArgumentParser()
    parser.add_argument('--enable_tuning_reload', default=False, action='store_true', help='Enable the tuning reload hooks')
    parser.add_argument('--tree_dump_tuning_snapshot_before_zone', default=False, action='store_true')
    parser.add_argument('--tree_dump_tuning_snapshot_after_zone', default=False, action='store_true')
    parser.add_argument('--mem_report_zone_snapshot', default=False, action='store_true')
    args, unused_args = parser.parse_known_args()
    TREE_DUMP_TUNING_SNAPSHOT_BEFORE_ZONE = args.tree_dump_tuning_snapshot_before_zone
    TREE_DUMP_TUNING_SNAPSHOT_AFTER_ZONE = args.tree_dump_tuning_snapshot_after_zone
    MEM_REPORT_ZONE_SNAPSHOT = args.mem_report_zone_snapshot
    IS_ARCHIVE = from_archive
    APP_ROOT = app_directory
    if debug_available:
        try:
            import pydevd, debugger
            DEBUG_AVAILABLE = True
        except ImportError:
            pass

    else:
        AUTOMATION_MODE = automation_mode
        TRACEMALLOC_TUNING_SNAPSHOT = tracemalloc_tuning_snapshot
        pathroot = os.path.abspath(os.path.normpath(pathroot + os.path.sep))
        DATA_ROOT = os.path.join(pathroot, 'Data')
        TUNING_ROOTS = {}
        for definition in sims4.resources.INSTANCE_TUNING_DEFINITIONS:
            TUNING_ROOTS[definition.resource_type] = os.path.join(DATA_ROOT, definition.TypeNames)

        if not from_archive:
            SCRIPT_ROOT = os.path.join(pathroot, 'Scripts')
            core_path = os.path.join(pathroot, 'Scripts', 'Core')
            lib_path = os.path.join(pathroot, 'Scripts', 'lib')
            debug_path = os.path.join(pathroot, 'Scripts', 'Debug')
            tests_path = os.path.join(pathroot, 'Scripts', 'Tests')
            build_path = os.path.join(pathroot, 'Scripts', 'Build')
            native_tuning_path = os.path.join(pathroot, 'Scripts', 'NativeTuning')
        else:
            SCRIPT_ROOT = None
            core_path = os.path.join(pathroot, 'Gameplay', 'core.zip')
            lib_path = os.path.join(pathroot, 'Gameplay', 'lib.zip')
            debug_path = os.path.join(pathroot, 'Gameplay', 'debug.zip')
            tests_path = os.path.join(pathroot, 'Gameplay', 'tests.zip')
            build_path = os.path.join(pathroot, 'Gameplay', 'build.zip')
            native_tuning_path = os.path.join(pathroot, 'Gameplay', 'nativetuning.zip')
        _CORE = core_path
        google_path = os.path.join(core_path, 'google')
        if sys.platform == 'win32' or sys.platform == 'ps4':
            DLL_PATH = os.path.join(app_directory, 'Python', 'DLLs')
        else:
            if sys.platform == 'darwin':
                DLL_PATH = os.path.join(app_directory, 'Frameworks', 'lib-dynload')
            else:
                DLL_PATH = None
        generated_path = os.path.join(app_directory, 'Python', 'Generated')
        deployed_path = deploy_override if deploy_override else os.path.join(app_directory, 'Python', 'Deployed')
        USER_SCRIPT_ROOTS = [
         core_path]
        LAYERS = [
         DLL_PATH,
         lib_path,
         google_path,
         os.path.join(core_path, 'api_config.py'),
         generated_path,
         deployed_path,
         debug_path,
         core_path]
        __app_paths__.configure_app_paths(pathroot, from_archive, USER_SCRIPT_ROOTS, LAYERS)
        LAYERS += [
         tests_path,
         build_path,
         native_tuning_path]
        if dump_root:
            DUMP_ROOT = dump_root
        else:
            DUMP_ROOT = '.'
    from sims4.tuning.merged_tuning_manager import create_manager, get_manager
    create_manager()
    mtg = get_manager()
    mtg.load()


# global LOCAL_WORK_ENABLED ## Warning: Unused global
# global SUPPORT_RELOADING_RESOURCES ## Warning: Unused global