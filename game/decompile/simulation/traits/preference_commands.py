# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\preference_commands.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 2932 bytes
import services, sims4, sims4.commands
from cas.cas import get_tags_from_outfit
from collections import defaultdict
from server_commands.argument_helpers import SimInfoParam

@sims4.commands.Command('qa.generate_premade_sim_preferences', command_type=(sims4.commands.CommandType.Automation))
def qa_generate_premade_sim_preferences(output_file=None, sim_info: SimInfoParam=None, verbose: bool=True, _connection=None):
    if output_file is not None:
        cheat_output = sims4.commands.FileOutput(output_file, _connection)
    else:
        cheat_output = sims4.commands.CheatOutput(_connection)
    tag_to_preference = defaultdict(list)
    cas_preference_item_manager = services.get_instance_manager(sims4.resources.Types.CAS_PREFERENCE_ITEM)
    for preference_item in cas_preference_item_manager.types.values():
        for tag in preference_item.get_any_tags():
            tag_to_preference[tag].append(preference_item)

    if sim_info is None:
        target_sims = [sim_info for sim_info in services.sim_info_manager().values() if sim_info.is_premade_sim if sim_info.is_human]
        target_sims = sorted(target_sims, key=(lambda sim: sim.full_name))
    else:
        target_sims = [
         sim_info]
    cheat_output('Preferences for:')
    for sim_info in target_sims:
        flattened_tags = []
        for outfit_category, outfits in sim_info.get_all_outfits():
            for index, outfit in enumerate(outfits):
                tags = get_tags_from_outfit(sim_info._base, outfit_category, index)
                flattened_tags.extend(list((item for entry in tags.values() for item in entry)))

        preference_counts = defaultdict(int)
        for tag in flattened_tags:
            if tag in tag_to_preference:
                for preference in tag_to_preference[tag]:
                    preference_counts[preference] += 1

        sorted_preferences = sorted((list(preference_counts.items())), key=(lambda item: item[1]))
        sorted_preferences = reversed(sorted_preferences)
        if verbose:
            preference_entry_strings = ['(Preference: {}, Matches in all outfits: {}), '.format(preference, weight) for preference, weight in sorted_preferences]
            preferences_output_string = '\n\t'.join(preference_entry_strings)
            cheat_output('{}:\n\t{}'.format(sim_info, preferences_output_string))
        else:
            cheat_output('{}: {}'.format(sim_info, list(sorted_preferences)))