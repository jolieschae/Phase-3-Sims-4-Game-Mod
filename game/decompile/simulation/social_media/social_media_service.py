# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\social_media\social_media_service.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 33058 bytes
from _collections import defaultdict
from date_and_time import DateAndTime, create_time_span, sim_ticks_per_day
from distributor.ops import ShowSocialMediaPanel, SendUIMessage
from distributor.rollback import ProtocolBufferRollback
from distributor.system import Distributor
from event_testing.resolver import DoubleSimResolver, SingleSimResolver
from interactions.context import InteractionContext, InteractionSource
from interactions.priority import Priority
from protocolbuffers import Localization_pb2
from server_commands import ui_commands
from sims4.service_manager import Service
from sims4.utils import classproperty
from social_media.social_media_post import SocialMediaPost, SocialMediaDirectMessage, SocialMediaPostReaction
from social_media import SocialMediaPostType, SocialMediaNarrative, SocialMediaPolarity
from social_media.social_media_tuning import SocialMediaTunables
import alarms, math, persistence_error_types, random, services, sims4.log
logger = sims4.log.Logger('Social Media', default_owner='mbilello')

class SocialMediaService(Service):

    def __init__(self):
        self._posts_per_sim_map = defaultdict(list)
        self._messages_per_sim_map = defaultdict(list)
        self._sims_with_new_posts = []
        self._sims_with_new_messages = []
        self._calculate_followers_handle = None

    def _schedule_calculate_followers_alarm(self):
        if self._calculate_followers_handle is not None:
            self._calculate_followers_handle.cancel()
        self._calculate_followers_handle = alarms.add_alarm(self, self.time_until_next_followers_count(), self._calculate_followers_callback)

    def time_until_next_followers_count(self):
        current_time = services.time_service().sim_now
        time_to_next_day = current_time.time_till_next_day_time(SocialMediaTunables.FOLLOWERS_RECOUNT_TIME_OF_DAY)
        if time_to_next_day.in_ticks() <= 0:
            time_to_next_day = time_to_next_day + create_time_span(days=1)
        return time_to_next_day

    def _calculate_followers_callback(self, _):
        for sim_id in self._posts_per_sim_map.keys():
            self.calculate_social_media_followers(sim_id)

        self._calculate_followers_handle = None
        self._schedule_calculate_followers_alarm()

    def create_post(self, post_type, author_sim_id, target_sim_id, narrative, context_post=None):
        sim_info_manager = services.sim_info_manager()
        author_sim_info = sim_info_manager.get(author_sim_id)
        if target_sim_id is not None:
            narrative_tuning = None
            for narrative_type in SocialMediaTunables.SOCIAL_MEDIA_NARRATIVE_TUNING:
                if narrative == narrative_type.narrative:
                    narrative_tuning = narrative_type
                    break

            if narrative_tuning is not None:
                if len(narrative_tuning.blacklist_rel_bit) > 0:
                    if author_sim_info.relationship_tracker.has_any_bits(target_sim_id, narrative_tuning.blacklist_rel_bit):
                        return
        post_time = services.time_service().sim_now
        target_post_loots = None
        actor_post_loots = None
        post_text = Localization_pb2.LocalizedString()
        post_text.hash = 0
        for type_of_post in SocialMediaTunables.TYPES_OF_POSTS:
            if type_of_post.narrative == narrative:
                if type_of_post.post_type == post_type:
                    if type_of_post.post_type == SocialMediaPostType.DEFAULT:
                        if type_of_post.context_post is not None:
                            if context_post is not None:
                                if not (type_of_post.context_post != context_post or author_sim_info.has_buff(type_of_post.context_post.buff_type)):
                                    continue
                post_text = random.choice(type_of_post.content)
                target_post_loots = type_of_post.target_loots_on_post
                actor_post_loots = type_of_post.loots_on_post
                break
        else:
            return

        if post_type == SocialMediaPostType.FOLLOWERS_UPDATE:
            new_post = SocialMediaPost(author_sim_id, target_sim_id, narrative, post_type, post_time, post_text)
            self.try_add_post_to_map(author_sim_info, new_post, self._posts_per_sim_map)
            self._sim_got_new_posts(author_sim_id)
        else:
            target_sim_info = sim_info_manager.get(target_sim_id)
            new_post = SocialMediaPost(author_sim_id, target_sim_id, narrative, post_type, post_time, post_text)
            if post_type == SocialMediaPostType.DEFAULT or post_type == SocialMediaPostType.PUBLIC_POST:
                if post_type == SocialMediaPostType.PUBLIC_POST:
                    if author_sim_id == target_sim_id:
                        return
                self.try_add_post_to_map(author_sim_info, new_post, self._posts_per_sim_map)
                self._sim_got_new_posts(author_sim_id)
                if target_sim_id is not None:
                    if author_sim_id != target_sim_id:
                        self.try_add_post_to_map(target_sim_info, new_post, self._posts_per_sim_map)
                        self._sim_got_new_posts(target_sim_id)
                self._add_post_to_friends_feed(author_sim_info, new_post)
            else:
                if post_type == SocialMediaPostType.DIRECT_MESSAGE:
                    if author_sim_id == target_sim_id:
                        return
                    new_dm = SocialMediaDirectMessage(new_post)
                    self.try_add_post_to_map(author_sim_info, new_dm, self._messages_per_sim_map)
                    self._sim_got_new_messages(author_sim_id)
                    self.try_add_post_to_map(target_sim_info, new_dm, self._messages_per_sim_map)
                    self._sim_got_new_messages(target_sim_id)
                else:
                    if post_type == SocialMediaPostType.FRIEND_REQUEST:
                        friends = author_sim_info.get_social_media_friends()
                        if any((target_sim_id == friend.sim_id for friend in friends)):
                            return
                        self.try_add_post_to_map(target_sim_info, new_post, self._posts_per_sim_map)
                        self._sim_got_new_posts(target_sim_id)
                    else:
                        if actor_post_loots:
                            resolver = SingleSimResolver(author_sim_info)
                            for loot in actor_post_loots:
                                loot.apply_to_resolver(resolver)

                        if target_post_loots:
                            if target_sim_id is not None and author_sim_id != target_sim_id:
                                resolver = DoubleSimResolver(author_sim_info, target_sim_info)
                                for loot in target_post_loots:
                                    loot.apply_to_resolver(resolver)

                    self.show_social_media_dialog(author_sim_id, is_update=True)

    def _add_post_to_friends_feed(self, author_sim_info, post):
        pc_friends = author_sim_info.get_pc_social_media_friends()
        for friend in pc_friends:
            if post.target_sim_id == friend.sim_id:
                continue
            self.try_add_post_to_map(friend, post, self._posts_per_sim_map)
            self._sim_got_new_posts(friend.sim_id)

    def get_sim_has_new_posts(self, sim_id):
        return sim_id in self._sims_with_new_posts

    def _sim_got_new_posts(self, sim_id):
        if sim_id is not None:
            if sim_id not in self._sims_with_new_posts:
                self._sims_with_new_posts.append(sim_id)
                phone_interaction = SocialMediaTunables.OPEN_SOCIAL_MEDIA_PHONE_INTERACTION
                if phone_interaction is not None:
                    ui_commands.ui_send_phone_notification(sim_id, phone_interaction)

    def mark_posts_seen(self, sim_id):
        if sim_id in self._sims_with_new_posts:
            self._sims_with_new_posts.remove(sim_id)

    def get_sim_has_new_messages(self, sim_id):
        return sim_id in self._sims_with_new_messages

    def _get_sim_can_make_context_post(self, sim_id):
        sim_info_manager = services.sim_info_manager()
        sim_info = sim_info_manager.get(sim_id)
        if sim_info is None:
            return False
        for post_type in SocialMediaTunables.TYPES_OF_POSTS:
            if post_type.context_post is None:
                continue
            if sim_info.Buffs.has_buff(post_type.context_post.buff_type):
                return True

        return False

    def get_sim_can_add_new_contacts(self, sim_id):
        sim_info_manager = services.sim_info_manager()
        sim_info = sim_info_manager.get(sim_id)
        context = InteractionContext(sim_info, InteractionSource.SCRIPT_WITH_USER_INTENT, Priority.Low)
        available_contacts = list(SocialMediaTunables.NEW_FRIEND_PICKER_INTERACTION._get_valid_sim_choices_gen(sim_info, context))
        if available_contacts:
            return True
        return False

    def get_possible_new_social_media_friend(self, sim_info):
        context = InteractionContext(sim_info, InteractionSource.SCRIPT_WITH_USER_INTENT, Priority.Low)
        available_contacts = list(SocialMediaTunables.NEW_FRIEND_PICKER_INTERACTION._get_valid_sim_choices_gen(sim_info, context))
        if len(available_contacts) > 0:
            return random.choice(available_contacts).sim_info

    def _sim_got_new_messages(self, sim_id):
        if sim_id is not None:
            if sim_id not in self._sims_with_new_messages:
                self._sims_with_new_messages.append(sim_id)
                phone_interaction = SocialMediaTunables.OPEN_SOCIAL_MEDIA_PHONE_INTERACTION
                if phone_interaction is not None:
                    ui_commands.ui_send_phone_notification(sim_id, phone_interaction)

    def mark_messages_seen(self, sim_id):
        if sim_id in self._sims_with_new_messages:
            self._sims_with_new_messages.remove(sim_id)

    def add_reaction_to_post_id(self, post_type, author_sim_id, target_sim_id, post_id, reaction_narrative, reaction_polarity):
        posts = []
        new_reaction = SocialMediaPostReaction(SocialMediaNarrative(reaction_narrative), SocialMediaPolarity(reaction_polarity))
        if post_type == SocialMediaPostType.DEFAULT or post_type == SocialMediaPostType.PUBLIC_POST:
            posts = self.get_posts_for_sim(author_sim_id)
            for post in posts:
                if post.post_id != post_id:
                    continue
                self.add_reaction_to_post(author_sim_id, target_sim_id, post, new_reaction)
                return

        else:
            if post_type == SocialMediaPostType.DIRECT_MESSAGE:
                posts = self.get_dms_for_sim(author_sim_id)
                for post in posts:
                    if post.message_post.post_id == post_id:
                        self.add_reaction_to_post(author_sim_id, target_sim_id, post.message_post, new_reaction)
                        return
                        if post.reply_post and post.reply_post.post_id == post_id:
                            self.add_reaction_to_post(author_sim_id, target_sim_id, post.reply_post, new_reaction)
                            return

            else:
                logger.error('Post type not supported for add_reaction_to_post: {}.', post_type)

    def add_reaction_to_post_narrative(self, post_type, author_sim_id, target_sim_id, post_narrative, reaction_narrative, reaction_polarity):
        posts = []
        if post_type == SocialMediaPostType.DEFAULT or post_type == SocialMediaPostType.PUBLIC_POST:
            posts = self.get_posts_for_sim(target_sim_id)
            for post in posts:
                if post.narrative != post_narrative:
                    continue
                new_reaction = SocialMediaPostReaction(SocialMediaNarrative(reaction_narrative), SocialMediaPolarity(reaction_polarity))
                self.add_reaction_to_post(author_sim_id, target_sim_id, post, new_reaction)
                return

        else:
            if post_type == SocialMediaPostType.DIRECT_MESSAGE:
                posts = self.get_dms_for_sim(target_sim_id)
                for post in posts:
                    if post.message_post.narrative != post_narrative:
                        continue
                    new_reaction = SocialMediaPostReaction(SocialMediaNarrative(reaction_narrative), SocialMediaPolarity(reaction_polarity))
                    self.add_reaction_to_post(author_sim_id, target_sim_id, post.message_post, new_reaction)
                    return

            else:
                logger.error('Post type not supported for add_reaction_to_post: {}.', post_type)

    def add_reaction_to_post(self, author_sim_id, target_sim_id, reacted_post, new_reaction):
        if reacted_post.post_type == SocialMediaPostType.FOLLOWERS_UPDATE:
            return
            if reacted_post.post_type == SocialMediaPostType.DIRECT_MESSAGE:
                if reacted_post.target_sim_id != author_sim_id:
                    return
            if reacted_post.sim_has_reacted(author_sim_id):
                return
            if reacted_post.total_reactions() >= SocialMediaTunables.REACTIONS_PER_POST_NUMBER_CAP:
                return
            new_reaction.reacted_sims.append(author_sim_id)
            if reacted_post.reactions:
                found = False
                for reaction in reacted_post.reactions:
                    if reaction == new_reaction:
                        reaction.count = reaction.count + 1
                        reaction.reacted_sims.append(author_sim_id)
                        found = True
                        break

                if not found:
                    reacted_post.reactions.append(new_reaction)
        else:
            reacted_post.reactions.append(new_reaction)
        self.show_social_media_dialog(author_sim_id, is_update=True)
        for reaction_outcome in SocialMediaTunables.SOCIAL_MEDIA_REACTIONS_OUTCOMES:
            if reaction_outcome.reaction_narrative == reacted_post.narrative:
                if reaction_outcome.post_polarity == new_reaction.polarity:
                    if reaction_outcome.loots_on_reaction:
                        sim_info_manager = services.sim_info_manager()
                        author_sim_info = sim_info_manager.get(author_sim_id)
                        target_sim_info = sim_info_manager.get(target_sim_id)
                        resolver = DoubleSimResolver(author_sim_info, target_sim_info)
                        for loot in reaction_outcome.loots_on_reaction:
                            loot.apply_to_resolver(resolver)

                return

    def try_add_post_to_map(self, sim_info, post, posts_map):
        if sim_info is None:
            return
        if sim_info.is_npc:
            return
        posts = posts_map[sim_info.sim_id]
        posts.append(post)
        if len(posts) > SocialMediaTunables.FEED_POSTS_NUMBER_CAP:
            posts.pop(0)

    def get_posts_for_sim(self, sim_id):
        if sim_id in self._posts_per_sim_map.keys():
            return self._posts_per_sim_map[sim_id]
        return []

    def get_dms_for_sim(self, sim_id):
        if sim_id in self._messages_per_sim_map.keys():
            return self._messages_per_sim_map[sim_id]
        return []

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_SOCIAL_MEDIA_SERVICE

    def save(self, save_slot_data=None, **kwargs):
        if save_slot_data is None:
            return
        social_media_service_data = save_slot_data.gameplay_data.social_media_service
        social_media_service_data.Clear()
        for key, posts in self._posts_per_sim_map.items():
            with ProtocolBufferRollback(social_media_service_data.post_entries) as (social_media_data):
                social_media_data.sim_id = key
                for post in posts:
                    with ProtocolBufferRollback(social_media_data.posts) as (posts_data):
                        post.save(posts_data)

        for key, dms in self._messages_per_sim_map.items():
            with ProtocolBufferRollback(social_media_service_data.direct_messages) as (social_media_dm_data):
                social_media_dm_data.sim_id = key
                for dm in dms:
                    with ProtocolBufferRollback(social_media_dm_data.messages) as (dms_data):
                        dm.save_dm(dms_data)

        social_media_service_data.sims_with_new_posts.extend(self._sims_with_new_posts)
        social_media_service_data.sims_with_new_messages.extend(self._sims_with_new_messages)

    def load(self, **_):
        save_slot_data_msg = services.get_persistence_service().get_save_slot_proto_buff()
        social_media_service_data = save_slot_data_msg.gameplay_data.social_media_service
        for post_entry in social_media_service_data.post_entries:
            for post in post_entry.posts:
                new_post = self.build_social_media_post(post)
                self._posts_per_sim_map[post_entry.sim_id].append(new_post)

        for dm_entry in social_media_service_data.direct_messages:
            for dm in dm_entry.messages:
                new_dm = self.build_social_media_post(dm.message_post)
                new_reply = None
                if dm.reply_post.post_id != 0:
                    new_reply = self.build_social_media_post(dm.reply_post)
                new_message = SocialMediaDirectMessage(new_dm, new_reply, dm.message_id)
                self._messages_per_sim_map[dm_entry.sim_id].append(new_message)

        self._sims_with_new_posts.extend(social_media_service_data.sims_with_new_posts)
        self._sims_with_new_messages.extend(social_media_service_data.sims_with_new_messages)
        self._schedule_calculate_followers_alarm()

    def build_social_media_post(self, post_data):
        post_text = Localization_pb2.LocalizedString()
        post_text.MergeFrom(post_data.post_text)
        new_post = SocialMediaPost(post_data.author_sim_id, post_data.target_sim_id, SocialMediaNarrative(post_data.narrative), SocialMediaPostType(post_data.post_type), DateAndTime(post_data.post_time), post_text, post_data.post_id)
        for reaction in post_data.reactions:
            new_reaction = SocialMediaPostReaction(SocialMediaNarrative(reaction.narrative_type), SocialMediaPolarity(reaction.polarity_type), reaction.count)
            new_reaction.reacted_sims.extend(reaction.reacted_sims)
            new_post.reactions.append(new_reaction)

        return new_post

    def get_current_followers_count(self, sim_id):
        sim_info_manager = services.sim_info_manager()
        author_sim_info = sim_info_manager.get(sim_id)
        stat = SocialMediaTunables.FOLLOWERS_TRACKING_COMMODITY
        stat_tracker = author_sim_info.get_tracker(stat)
        followers_count = 0
        if stat_tracker.has_statistic(stat):
            followers_count = int(stat_tracker.get_value(stat))
        return followers_count

    def show_social_media_dialog(self, sim_id, is_update=False):
        feed_items = self.get_posts_for_sim(sim_id)
        followers_count = self.get_current_followers_count(sim_id)
        messages_items = self.get_dms_for_sim(sim_id)
        has_new_posts = self.get_sim_has_new_posts(sim_id)
        has_new_messages = self.get_sim_has_new_messages(sim_id)
        can_make_context_post = self._get_sim_can_make_context_post(sim_id)
        can_add_new_contacts = self.get_sim_can_add_new_contacts(sim_id)
        op = ShowSocialMediaPanel(sim_id, followers_count, feed_items, messages_items,
          is_update=is_update, has_new_posts=has_new_posts,
          has_new_messages=has_new_messages,
          can_make_context_post=can_make_context_post,
          can_add_new_contacts=can_add_new_contacts)
        Distributor.instance().add_op_with_no_owner(op)

    def add_social_media_friend(self, author_sim_id, target_sim_id):
        sim_info_manager = services.sim_info_manager()
        author_sim_info = sim_info_manager.get(author_sim_id)
        if len(author_sim_info.get_social_media_friends()) >= SocialMediaTunables.SOCIAL_MEDIA_FRIENDS_NUMBER_CAP:
            return
        target_sim_info = sim_info_manager.get(target_sim_id)
        if not author_sim_info.relationship_tracker.has_relationship(target_sim_info.id):
            author_sim_info.relationship_tracker.create_relationship(target_sim_info.sim_id)
        author_sim_info.relationship_tracker.add_relationship_bit(target_sim_info.id, SocialMediaTunables.SOCIAL_MEDIA_REL_BIT)
        if target_sim_info.is_npc:
            stat = SocialMediaTunables.NPC_POSTING_COMMODITY
            target_sim_info.set_stat_value(stat, value=0, add=True)
        possible_contacts = self.get_sim_can_add_new_contacts(author_sim_id)
        if not possible_contacts:
            op = SendUIMessage('NoMoreContactsToAdd')
            Distributor.instance().add_op_with_no_owner(op)

    def remove_social_media_friend(self, author_sim_info, target_sim_info):
        author_sim_info.relationship_tracker.remove_relationship_bit(target_sim_info.id, SocialMediaTunables.SOCIAL_MEDIA_REL_BIT)
        self.remove_direct_messages_from_sim(author_sim_info.id, target_sim_info.id)
        stat = SocialMediaTunables.NPC_POSTING_COMMODITY
        tracker = target_sim_info.get_tracker(stat)
        tracker.remove_statistic(stat)
        possible_contacts = self.get_sim_can_add_new_contacts(author_sim_info.id)
        if possible_contacts:
            op = SendUIMessage('MoreContactsToAdd')
            Distributor.instance().add_op_with_no_owner(op)

    def remove_direct_messages_from_sim(self, author_sim_id, target_sim_id):
        self._remove_dms_from_sim_list(author_sim_id, target_sim_id)
        self._remove_dms_from_sim_list(target_sim_id, author_sim_id)

    def _remove_dms_from_sim_list(self, list_sim_id, message_sim_id):
        dms_to_remove = []
        author_dms = self.get_dms_for_sim(list_sim_id)
        for dm in author_dms:
            if not dm.message_post.author_sim_id == message_sim_id:
                if not dm.reply_post or dm.reply_post.author_sim_id == message_sim_id:
                    dms_to_remove.append(dm)

        for dm_to_remove in dms_to_remove:
            author_dms.remove(dm_to_remove)

    def remove_posts_from_sim(self, author_sim_id, target_sim_id):
        self._remove_posts_from_sim_list(author_sim_id, target_sim_id)
        self._remove_posts_from_sim_list(target_sim_id, author_sim_id)

    def _remove_posts_from_sim_list(self, list_sim_id, post_sim_id):
        author_posts = self.get_posts_for_sim(list_sim_id)
        for post in list(author_posts):
            if post.author_sim_id == post_sim_id or post.target_sim_id == post_sim_id:
                author_posts.remove(post)

    def get_base_stat_for_posts(self, sim_id):
        total_posts = self.get_posts_for_sim(sim_id)
        post_count = 0
        contextual_post_count = 0
        reactions_count = 0
        current_time = services.time_service().sim_now
        yesterday = current_time.absolute_ticks() - sim_ticks_per_day()
        for post in total_posts:
            if post.author_sim_id != sim_id or post.post_time.absolute_ticks() <= yesterday:
                continue
            if post.post_type == SocialMediaPostType.PUBLIC_POST:
                post_count = post_count + 1
            if post.post_type == SocialMediaPostType.DEFAULT:
                contextual_post_count = contextual_post_count + 1
            if post.reactions:
                reactions_count = reactions_count + len(post.reactions)

        base_stat = SocialMediaTunables.FOLLOWERS_REGULAR_POST_BASE_STAT
        cont_stat = SocialMediaTunables.FOLLOWERS_CONTEXTUAL_POST_BASE_STAT
        return (post_count * base_stat + contextual_post_count * cont_stat, post_count + contextual_post_count, reactions_count)

    def is_contextual(self, post):
        for post_type in SocialMediaTunables.TYPES_OF_POSTS:
            if post_type.post_type == post.post_type and post_type.narrative == post.narrative:
                return post_type.context_post is not None

        return False

    def get_posts_modifier(self, post_count):
        for modifier in SocialMediaTunables.FOLLOWERS_POSTING_MODIFIER:
            if post_count >= modifier.min and post_count < modifier.max:
                return modifier.modifier

        return 1

    def calculate_social_media_followers(self, author_sim_id):
        sim_info_manager = services.sim_info_manager()
        author_sim_info = sim_info_manager.get(author_sim_id)
        stat = SocialMediaTunables.FOLLOWERS_TRACKING_COMMODITY
        if author_sim_info is None:
            return
        stat_tracker = author_sim_info.get_tracker(stat)
        if stat_tracker is None:
            return
        current_count = stat_tracker.get_value(stat)
        followers_to_remove = math.ceil(current_count * SocialMediaTunables.FOLLOWERS_PERCENTAGE_LOST_PER_DAY / 100)
        base_stat, total_post_count, reactions_count = self.get_base_stat_for_posts(author_sim_id)
        post_count_modifier = self.get_posts_modifier(total_post_count)
        followers_for_reactions = reactions_count * SocialMediaTunables.FOLLOWERS_NPC_REACTION_GAIN
        followers_log = 1 + (math.log(current_count) if current_count > 0 else 0)
        followers_to_gain = int(base_stat * followers_log * post_count_modifier) + followers_for_reactions
        new_followers_count = int(current_count - followers_to_remove + followers_to_gain)
        stat_tracker.set_value(stat, new_followers_count, add=True)
        self.create_post(SocialMediaPostType.FOLLOWERS_UPDATE, author_sim_id, int(followers_to_gain - followers_to_remove), SocialMediaNarrative.FRIENDLY)

    def on_sim_removed(self, sim_id):
        for friend_sim_id in self._messages_per_sim_map.keys():
            if friend_sim_id != sim_id:
                self.remove_direct_messages_from_sim(friend_sim_id, sim_id)

        for friend_sim_id in self._posts_per_sim_map.keys():
            if friend_sim_id != sim_id:
                self.remove_posts_from_sim(friend_sim_id, sim_id)