# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\notebook\notebook_commands.py
# Compiled at: 2021-03-08 17:04:21
# Size of source mod 2**32: 3003 bytes
from server_commands.argument_helpers import OptionalSimInfoParam, get_optional_target, RequiredTargetParam
from sims4.commands import CommandType
from ui.notebook_tuning import NotebookCategories, NotebookSubCategories
import services, sims4

@sims4.commands.Command('notebook.generate_notebook', command_type=(CommandType.Live))
def generate_notebook(opt_sim: OptionalSimInfoParam=None, initial_category: int=None, initial_subcategory: int=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is not None:
        if sim_info.notebook_tracker is not None:
            initial_selected_category = None if initial_category is None else NotebookCategories(initial_category)
            initial_selected_subcategory = None if initial_subcategory is None else NotebookSubCategories(initial_subcategory)
            sim_info.notebook_tracker.generate_notebook_information(initial_selected_category=initial_selected_category, initial_selected_subcategory=initial_selected_subcategory)
    return True


@sims4.commands.Command('notebook.mark_entry_as_seen', command_type=(CommandType.Live))
def mark_entry_as_seen(sim: RequiredTargetParam, subcategory_id: int, entry_id: int, _connection=None):
    sim_info = sim.get_target(manager=(services.sim_info_manager()))
    if sim_info is None:
        sims4.commands.output('Sim with id {} is not found to mark notebook entry as seen.'.format(sim.target_id), _connection)
        return False
    if sim_info.notebook_tracker is None:
        sims4.commands.output('Notebook tracker is not found on Sim {} to mark notebook entry as seen'.format(sim_info), _connection)
        return False
    sim_info.notebook_tracker.mark_entry_as_seen(subcategory_id, entry_id)
    return True


@sims4.commands.Command('notebook.hide_category', command_type=(CommandType.Live))
def hide_category(sim: RequiredTargetParam, category_id: int, _connection=None):
    sim_info = sim.get_target(manager=(services.sim_info_manager()))
    if sim_info is None:
        sims4.commands.output('Sim with id {} is not found to mark notebook entry as seen.'.format(sim.target_id), _connection)
        return False
    if sim_info.notebook_tracker is None:
        sims4.commands.output('Notebook tracker is not found on Sim {} to mark notebook entry as seen'.format(sim_info), _connection)
        return False
    sim_info.notebook_tracker.remove_entries_by_category(NotebookCategories(category_id))
    return True