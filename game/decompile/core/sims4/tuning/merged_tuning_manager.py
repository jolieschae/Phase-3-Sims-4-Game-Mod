# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\tuning\merged_tuning_manager.py
# Compiled at: 2019-06-06 13:53:41
# Size of source mod 2**32: 13450 bytes
from collections import defaultdict
from sims4.resources import get_all_resources_of_type
import assertions, sims4.log, sims4.reload, sims4.resources
import xml.etree.ElementTree as ET
try:
    import _tuning
except ImportError:
    _tuning = None

DEBUG_MERGED_TUNING_DATA = False
NAME_ABBR = {
 'Tunable': "'T'", 
 'TunableEnum': "'E'", 
 'TunableTuple': "'U'", 
 'TunableVariant': "'V'", 
 'TunableList': "'L'", 
 'Class': "'C'", 
 'Module': "'M'", 
 'Instance': "'I'", 
 'class': "'c'", 
 'name': "'n'", 
 'module': "'m'", 
 'type': "'t'", 
 'instance_type': "'i'", 
 'is_none': "'o'", 
 'TOOL_path': "'p'", 
 'ref': "'r'", 
 'ix': "'x'", 
 'merged': "'g'", 
 'res_inst': "'s'", 
 'Res_Type': "'R'"}
ABBR_NAME = {NAME_ABBR[key]: key for key in NAME_ABBR.keys()}
COMBINED_TUNING_NAME = 'combined_tuning.xml'
with sims4.reload.protected(globals()):
    MERGED_TUNING_MANAGER = None
    merged_tuning_log_enabled = False
logger = sims4.log.Logger('Tuning')

class UnavailablePackSafeResourceError(ValueError):
    pass


class MergedTuningAttr:
    Reference = 'r'
    Index = 'x'
    Merged = 'g'


class MergedTuningManager:
    USE_CACHE = True

    def __init__(self):
        self.indexed_tunables = {}
        self.indexed_constructed_tunables = {}
        self._tuning_resources = defaultdict(dict)
        self._res_id_group_map = {}
        self.binxml_list = []
        self.local_key_map = defaultdict(set)
        self.local_deleted_key_map = defaultdict(set)
        if DEBUG_MERGED_TUNING_DATA:
            self.index_ref_record = defaultdict(list)

    def load(self, silent_fail=True):
        for combined_tuning_key in get_all_resources_of_type(type_id=(sims4.resources.Types.COMBINED_TUNING)):
            self._load_combined_file_by_key(combined_tuning_key, silent_fail=silent_fail)

    def _load_combined_file_by_key(self, combined_tuning_key, silent_fail=True):
        loader = sims4.resources.ResourceLoader(combined_tuning_key)
        raw_tuning_file = loader.load_raw(silent_fail=silent_fail)
        if raw_tuning_file is not None:
            if _tuning:
                if _tuning.is_binary_merged_tuning(raw_tuning_file):
                    binxml = _tuning.BinaryTuning(raw_tuning_file)
                    self.binxml_list.append(binxml)
                    root = binxml.root
                else:
                    tree = ET.parse(loader.cook(raw_tuning_file))
                    root = tree.getroot()
            else:
                for child_node in root:
                    if child_node.tag == 'g':
                        self._load_merged_file(child_node)

                tuning_resource_types = {td.resource_type for td in sims4.resources.INSTANCE_TUNING_DEFINITIONS}
                local_key_list = []
                local_deleted_list = []
                if sims4.resources.RESMAN_API_VERSION >= 2:
                    local_files_tuple = sims4.resources.list_local(key=(loader.resource_key), packed_types=tuning_resource_types)
                else:
                    local_files_tuple = sims4.resources.list_local(key=(loader.resource_key))
            if local_files_tuple is not None:
                local_key_list, local_deleted_list = local_files_tuple
            for key in local_key_list:
                if key.type in tuning_resource_types:
                    self.local_key_map[key.type].add((key.group, key.instance))

            for key in local_deleted_list:
                if key.type in tuning_resource_types:
                    self.local_deleted_key_map[key.type].add((key.group, key.instance))

    def clear(self):
        self.indexed_tunables.clear()
        self.indexed_constructed_tunables.clear()
        self._tuning_resources.clear()
        self.local_key_map.clear()
        self.local_deleted_key_map.clear()
        if DEBUG_MERGED_TUNING_DATA:
            self.index_ref_record.clear()
        self.binxml_list = []

    def _load_merged_file(self, merge_node):
        for child_node in merge_node:
            index = child_node.get(MergedTuningAttr.Index)
            self.indexed_tunables[index] = child_node

    def _load_res_node(self, res_node, group_id):
        res_type_name = res_node.get('n')
        for child_node in res_node:
            res_id = int(child_node.get('s'))
            self._tuning_resources[res_type_name][res_id] = child_node
            if group_id != 0:
                self._res_id_group_map[res_id] = group_id

    def get_tuning_res(self, res_key, silent_fail=False):
        if res_key.type not in sims4.resources.TYPE_RES_DICT:
            assert silent_fail, 'Resource type {0:x} is not defined in resources.py'.format(res_key.type)
            return
        res_ext = sims4.resources.TYPE_RES_DICT[res_key.type]
        if res_ext not in self._tuning_resources:
            assert silent_fail, "Resource type {0:x} with ext {1} doesn't exist in combined file".format(res_key.type, res_ext)
            return
        res_dict = self._tuning_resources[res_ext]
        if res_key.instance not in res_dict:
            if not silent_fail:
                logger.warn('Resource id {:x} is missing in resource type {}', res_key.instance, res_ext)
            return
        return res_dict[res_key.instance]

    def local_key_exists(self, res_key):
        if res_key.type not in self.local_key_map:
            return False
        return (
         res_key.group, res_key.instance) in self.local_key_map[res_key.type]

    def register_change(self, res_key):
        self.local_key_map[res_key.type].add((res_key.group, res_key.instance))

    def deleted_local_key_exists(self, res_key):
        if res_key.type not in self.local_deleted_key_map:
            return False
        return (
         res_key.group, res_key.instance) in self.local_deleted_key_map[res_key.type]

    def get_all_res_ids(self, res_type):
        res_ext = sims4.resources.TYPE_RES_DICT[res_type]
        result_set = set()
        if res_ext in self._tuning_resources:
            res_dict = self._tuning_resources[res_ext]
            result_set.update(((self._res_id_group_map.get(r, 0), r) for r in res_dict))
        if res_type in self.local_key_map:
            result_set.update(self.local_key_map[res_type])
        if res_type in self.local_deleted_key_map:
            result_set -= set(self.local_deleted_key_map[res_type])
        return result_set

    def get_tunable_node(self, index):
        return self.indexed_tunables[index]

    @assertions.hot_path
    def get_tunable(self, index, tunable_template, source):
        if self.USE_CACHE:
            cache_key = tunable_template.cache_key
            loaded_key = (index, cache_key)
            if loaded_key in self.indexed_constructed_tunables:
                tuned_value = self.indexed_constructed_tunables[loaded_key]
                if DEBUG_MERGED_TUNING_DATA:
                    self.index_ref_record[loaded_key].append((source, tunable_template, tuned_value))
                    if isinstance(tuned_value, (int, float, str, bool)):
                        real_value = tunable_template.load_etree_node(self.indexed_tunables[index], source, False)
                        if real_value != tuned_value:
                            logger.error('Cache key error: {} != {} ({})', real_value, tuned_value, source)
                return tuned_value
        node = self.indexed_tunables[index]
        tuned_value = tunable_template.load_etree_node(node, source, False)
        if self.USE_CACHE:
            self.indexed_constructed_tunables[loaded_key] = tuned_value
            if DEBUG_MERGED_TUNING_DATA:
                self.index_ref_record[loaded_key].append((source, tunable_template, tuned_value))
        return tuned_value

    def get_name(self, res_key):
        res_inst = self.get_tuning_res(res_key, silent_fail=True)
        if res_inst is not None:
            return res_inst.get('n')

    @property
    def has_combined_tuning_loaded(self):
        if self._tuning_resources:
            return True
        return False


def create_manager():
    global MERGED_TUNING_MANAGER
    if MERGED_TUNING_MANAGER is None:
        MERGED_TUNING_MANAGER = MergedTuningManager()


def clear_manager():
    global MERGED_TUNING_MANAGER
    if MERGED_TUNING_MANAGER is not None:
        MERGED_TUNING_MANAGER.clear()
    MERGED_TUNING_MANAGER = None


def get_manager():
    return MERGED_TUNING_MANAGER