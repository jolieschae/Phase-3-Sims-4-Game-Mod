# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\social_media\social_media_commands.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 10920 bytes
from distributor.ops import TogglePhoneBadge
from distributor.system import Distributor
from server_commands.argument_helpers import RequiredTargetParam, OptionalTargetParam, get_optional_target
from sims4.commands import CommandType
from social_media import SocialMediaPostType, SocialMediaNarrative, SocialMediaPolarity
import services, sims4

def _get_social_media_service(_connection):
    social_media_service = services.get_social_media_service()
    if social_media_service is None:
        sims4.commands.output('Social Media Service not loaded.', _connection)
    return social_media_service


@sims4.commands.Command('social_media.create_post', command_type=(CommandType.Automation))
def create_social_media_post(author_sim, target_sim=None, post_type='DEFAULT', narrative='FRIENDLY', _connection=None):
    author_sim_info = author_sim.get_target(manager=(services.sim_info_manager()))
    if author_sim_info is None:
        sims4.commands.output('Not a valid SimID.', _connection)
        return
    social_media_service = _get_social_media_service(_connection)
    if social_media_service is None:
        return
    post_type_value = SocialMediaPostType[post_type]
    narrative_value = SocialMediaNarrative[narrative]
    target_sim_info = get_optional_target(target_sim, _connection)
    target_sim_id = target_sim_info.sim_id if target_sim_info is not None else None
    social_media_service.create_post(post_type_value, author_sim_info.sim_id, target_sim_id, narrative_value)


@sims4.commands.Command('social_media.create_dm', command_type=(CommandType.Automation))
def create_social_media_dm(author_sim: RequiredTargetParam, target_sim: RequiredTargetParam, _connection=None):
    manager = services.sim_info_manager()
    author_sim_info = author_sim.get_target(manager)
    target_sim_info = target_sim.get_target(manager)
    if author_sim_info is None:
        sims4.commands.output('Not valid author SimID.', _connection)
        return
    if target_sim_info is None:
        sims4.commands.output('Not valid target SimID.', _connection)
        return
    social_media_service = _get_social_media_service(_connection)
    if social_media_service is None:
        return
    social_media_service.create_post(SocialMediaPostType.DIRECT_MESSAGE, author_sim_info.sim_id, target_sim_info.sim_id, SocialMediaNarrative.FRIENDLY)


@sims4.commands.Command('social_media.get_posts', command_type=(CommandType.Automation))
def social_media_get_posts(_connection):
    social_media_service = _get_social_media_service(_connection)
    if social_media_service is None:
        return
    sims4.commands.output('Social Media; Status:Begin', _connection)
    for sim_id, posts in social_media_service._posts_per_sim_map.items():
        sims4.commands.output('Post for Sim: {};'.format(sim_id), _connection)
        for post in posts:
            sims4.commands.output('Post:{}; data:{},{},{},{},{},{}'.format(post.post_id, post.author_sim_id, post.target_sim_id, post.narrative, post.post_type, post.post_time, post.post_text), _connection)

    sims4.commands.output('Social Media; Status:End', _connection)


@sims4.commands.Command('social_media.show_social_media_dialog', command_type=(CommandType.Live))
def show_social_media_dialog(sim_id: RequiredTargetParam, _connection=None):
    sim_info = sim_id.get_target(manager=(services.sim_info_manager()))
    if sim_info is None or sim_info.is_npc:
        sims4.commands.output('Not a valid SimID.', _connection)
        return
    social_media_service = _get_social_media_service(_connection)
    if social_media_service is None:
        return
    social_media_service.show_social_media_dialog(sim_info.sim_id)


@sims4.commands.Command('social_media.social_media_add_friend', command_type=(CommandType.Live))
def social_media_add_friend(author_sim: RequiredTargetParam, target_sim: RequiredTargetParam, _connection=None):
    manager = services.sim_info_manager()
    author_sim_info = author_sim.get_target(manager)
    target_sim_info = target_sim.get_target(manager)
    if author_sim_info is None:
        sims4.commands.output('Not valid author SimID.', _connection)
        return
    if target_sim_info is None:
        sims4.commands.output('Not valid target SimID.', _connection)
        return
    social_media_service = _get_social_media_service(_connection)
    if social_media_service is None:
        return
    social_media_service.add_social_media_friend(author_sim_info.sim_id, target_sim_info.sim_id)


@sims4.commands.Command('social_media.social_media_remove_friend', command_type=(CommandType.Live))
def social_media_remove_friend(author_sim: RequiredTargetParam, target_sim: RequiredTargetParam, _connection=None):
    manager = services.sim_info_manager()
    author_sim_info = author_sim.get_target(manager)
    target_sim_info = target_sim.get_target(manager)
    if author_sim_info is None:
        sims4.commands.output('Not valid author SimID.', _connection)
        return
    if target_sim_info is None:
        sims4.commands.output('Not valid target SimID.', _connection)
        return
    social_media_service = _get_social_media_service(_connection)
    if social_media_service is None:
        return
    social_media_service.remove_social_media_friend(author_sim_info, target_sim_info)


@sims4.commands.Command('social_media.social_media_mark_posts_seen', command_type=(CommandType.Live))
def social_media_mark_posts_seen(author_sim: RequiredTargetParam, _connection=None):
    manager = services.sim_info_manager()
    author_sim_info = author_sim.get_target(manager)
    if author_sim_info is None:
        sims4.commands.output('Not valid author SimID.', _connection)
        return
    social_media_service = _get_social_media_service(_connection)
    if social_media_service is None:
        return
    author_sim_id = author_sim_info.sim_id
    social_media_service.mark_posts_seen(author_sim_id)
    if not social_media_service.get_sim_has_new_messages(author_sim_id):
        op = TogglePhoneBadge(author_sim_info.sim_id, False)
        Distributor.instance().add_op_with_no_owner(op)


@sims4.commands.Command('social_media.social_media_mark_messages_seen', command_type=(CommandType.Live))
def social_media_mark_messages_seen(author_sim: RequiredTargetParam, _connection=None):
    manager = services.sim_info_manager()
    author_sim_info = author_sim.get_target(manager)
    if author_sim_info is None:
        sims4.commands.output('Not valid author SimID.', _connection)
        return
    social_media_service = _get_social_media_service(_connection)
    if social_media_service is None:
        return
    author_sim_id = author_sim_info.sim_id
    social_media_service.mark_messages_seen(author_sim_id)
    if not social_media_service.get_sim_has_new_posts(author_sim_id):
        op = TogglePhoneBadge(author_sim_id, False)
        Distributor.instance().add_op_with_no_owner(op)


@sims4.commands.Command('social_media.calculate_followers', command_type=(CommandType.Automation))
def calculate_social_media_followers(sim_id: RequiredTargetParam, _connection=None):
    sim_info = sim_id.get_target(manager=(services.sim_info_manager()))
    if sim_info is None or sim_info.is_npc:
        sims4.commands.output('Not a valid SimID.', _connection)
        return
    social_media_service = _get_social_media_service(_connection)
    if social_media_service is None:
        return
    social_media_service.calculate_social_media_followers(sim_info.sim_id)


@sims4.commands.Command('social_media.add_reaction_to_post_ids', command_type=(CommandType.Live))
def add_social_media_reaction_to_post_ids(author_sim: RequiredTargetParam, target_sim: RequiredTargetParam, post_id=0, post_type=0, narrative=0, polarity=0, _connection=None):
    post_type_value = SocialMediaPostType(post_type).name
    narrative_value = SocialMediaNarrative(narrative).name
    polarity_value = SocialMediaPolarity(polarity).name
    add_social_media_reaction_to_post(author_sim, target_sim, post_id, post_type_value, narrative_value, polarity_value, _connection)


@sims4.commands.Command('social_media.add_reaction_to_post', command_type=(CommandType.Automation))
def add_social_media_reaction_to_post(author_sim, target_sim, post_id=0, post_type='DEFAULT', narrative='FRIENDLY', polarity='POSITIVE', _connection=None):
    manager = services.sim_info_manager()
    author_sim_info = author_sim.get_target(manager)
    target_sim_info = target_sim.get_target(manager)
    if author_sim_info is None:
        sims4.commands.output('Not valid author SimID.', _connection)
        return
    if target_sim_info is None:
        sims4.commands.output('Not valid target SimID.', _connection)
        return
    social_media_service = _get_social_media_service(_connection)
    if social_media_service is None:
        return
    post_type_value = SocialMediaPostType[post_type]
    narrative_value = SocialMediaNarrative[narrative]
    polarity_value = SocialMediaPolarity[polarity]
    social_media_service.add_reaction_to_post_id(post_type_value, author_sim_info.sim_id, target_sim_info.sim_id, int(post_id), narrative_value, polarity_value)