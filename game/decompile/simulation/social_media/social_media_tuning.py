# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\social_media\social_media_tuning.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 12208 bytes
from buffs.buff import Buff
from event_testing.tests import TunableTestSet
from interactions.utils.loot import LootActions
from interactions.utils.tunable_icon import TunableIcon, TunableIconVariant
from tunable_time import TunableTimeOfDay
from sims4.localization import TunableLocalizedString
from sims4.tuning.tunable import TunableTuple, TunableEnumEntry, TunableReference, TunableList, TunableRange, OptionalTunable
from sims4.tuning.tunable_base import ExportModes
from social_media import SocialMediaPostType, SocialMediaNarrative, SocialMediaPolarity
from relationships.relationship_bit import RelationshipBit
import enum, services, sims4
logger = sims4.log.Logger('Social Media', default_owner='mbilello')

class SocialMediaTunables:
    SOCIAL_MEDIA_POST_REACTIONS = TunableList(description='\n        A set of Reactions for Social Media Posts.\n        ',
      tunable=TunableTuple(export_class_name='SocialMediaPostReactionsList',
      name=TunableLocalizedString(description='\n                The name to associate with this reaction.\n                '),
      icon=TunableIcon(description='\n                The icon to associate with this reaction.\n                '),
      narrative=TunableEnumEntry(description='\n                A SocialMediaNarrative enum entry.\n                ',
      tunable_type=SocialMediaNarrative,
      default=(SocialMediaNarrative.FRIENDLY)),
      polarity=TunableEnumEntry(description='\n                A SocialMediaPolarity enum entry.\n                ',
      tunable_type=SocialMediaPolarity,
      default=(SocialMediaPolarity.POSITIVE))),
      export_modes=(
     ExportModes.ClientBinary,))
    SOCIAL_MEDIA_REACTIONS_OUTCOMES = TunableList(description='\n        A set of Reactions for Social Media Posts.\n        ',
      tunable=TunableTuple(reaction_narrative=TunableEnumEntry(description='\n                The SocialMediaNarrative to match in the reaction.\n                ',
      tunable_type=SocialMediaNarrative,
      default=(SocialMediaNarrative.FRIENDLY)),
      post_polarity=TunableEnumEntry(description='\n                The SocialMediaPolarity to match in the post.\n                ',
      tunable_type=SocialMediaPolarity,
      default=(SocialMediaPolarity.POSITIVE)),
      loots_on_reaction=TunableList(description='\n                Loots applied when the reaction is made.\n                ',
      tunable=LootActions.TunableReference(description='\n                    A loot applied when the reaction is made.\n                    '))))
    SOCIAL_MEDIA_REL_BIT = RelationshipBit.TunableReference(description='\n        The relationship bit that will be used to track Social Media friends.\n        ')
    FEED_POSTS_NUMBER_CAP = TunableRange(description='\n        Cap for how many posts the Feed will show and the service will save.\n        ',
      tunable_type=int,
      default=30,
      minimum=0)
    SOCIAL_MEDIA_FRIENDS_NUMBER_CAP = TunableRange(description='\n        Cap for how many Social Media Friends a sim can have.\n        ',
      tunable_type=int,
      default=30,
      minimum=0)
    REACTIONS_PER_POST_NUMBER_CAP = TunableRange(description='\n        Cap for how many reactions each post can have.\n        ',
      tunable_type=int,
      default=10,
      minimum=0)
    NPC_POSTING_COMMODITY = TunableReference(description='\n        Commodity to assign to NPC friends for Social Media posting.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
      class_restrictions='Commodity')
    FOLLOWERS_RECOUNT_TIME_OF_DAY = TunableTimeOfDay(description='\n        The time of day in hours to calculate current followers.\n        ',
      default_hour=6)
    FOLLOWERS_NPC_REACTION_GAIN = TunableRange(description="\n        Number of followers that will be gained by an NPC reaction to a \n        player's post.\n        ",
      tunable_type=int,
      default=10,
      minimum=0)
    FOLLOWERS_PERCENTAGE_LOST_PER_DAY = TunableRange(description='\n        Percentage of followers lost per day from current follower count.\n        ',
      tunable_type=int,
      default=1,
      minimum=0,
      maximum=100)
    FOLLOWERS_REGULAR_POST_BASE_STAT = TunableRange(description='\n        How many followers will be gained by making a regular post.\n        ',
      tunable_type=int,
      default=50,
      minimum=0)
    FOLLOWERS_CONTEXTUAL_POST_BASE_STAT = TunableRange(description='\n        How many followers will be gained by making a contextual post.\n        ',
      tunable_type=int,
      default=50,
      minimum=0)
    FOLLOWERS_TRACKING_COMMODITY = TunableReference(description='\n        Commodity to assign for tracking Social Media followers.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
      class_restrictions='Commodity')
    FOLLOWERS_POSTING_MODIFIER = TunableList(description='\n        Modifiers for followers calculation.\n        ',
      tunable=TunableTuple(modifier=TunableRange(description='\n                Modifier to be applied for followers calculation.\n                ',
      tunable_type=float,
      default=1.0),
      min=TunableRange(description='\n                Min of the post range for this modifier.\n                ',
      tunable_type=int,
      default=0,
      minimum=0),
      max=TunableRange(description='\n                Max of the post range for this modifier.\n                ',
      tunable_type=int,
      default=0,
      minimum=0)))
    NEW_POST_PICKER_INTERACTION = TunableReference(description='\n        The interaction to bring a new post picker up.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
      export_modes=(
     ExportModes.ClientBinary,))
    NEW_FRIEND_PICKER_INTERACTION = TunableReference(description='\n        The interaction to bring a new Sim friend picker up.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
      export_modes=(
     ExportModes.ClientBinary,))
    NEW_MESSAGE_TYPE_PICKER_INTERACTION = TunableReference(description='\n        The interaction to bring a new type of message picker up.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
      export_modes=(
     ExportModes.ClientBinary,))
    NEW_DIRECT_MESSAGE_PICKER_INTERACTION = TunableReference(description='\n        The interaction to bring a new direct message picker up.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
      export_modes=(
     ExportModes.ClientBinary,))
    NEW_EVENT_POST_PICKER_INTERACTION = TunableReference(description='\n        The interaction to bring a new post picker up.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
      export_modes=(
     ExportModes.ClientBinary,))
    OPEN_SOCIAL_MEDIA_PHONE_INTERACTION = TunableReference(description='\n        The phone interaction to open the social media dialog.\n        Used to infer which interaction to badge.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
      pack_safe=True)
    SOCIAL_MEDIA_NARRATIVE_TUNING = TunableList(description='\n        Tuning to show the narratives in a picker.\n        ',
      tunable=TunableTuple(narrative=TunableEnumEntry(description='\n                A SocialMediaNarrative enum entry.\n                ',
      tunable_type=SocialMediaNarrative,
      default=(SocialMediaNarrative.FRIENDLY)),
      picker_name=TunableLocalizedString(description='\n                The name used in the picker for this narrative.\n                '),
      picker_description=TunableLocalizedString(description='\n                The description used in the picker for this narrative.\n                '),
      picker_icon=TunableIconVariant(description='\n                The icon used in the picker for this narrative.\n                ',
      icon_pack_safe=True),
      picker_tooltip=TunableLocalizedString(description='\n                The tooltip used in the picker for this narrative.\n                '),
      blacklist_rel_bit=TunableList(description='\n                The relationship bits that will be blacklisted for this narrative.\n                ',
      tunable=(RelationshipBit.TunableReference())),
      targeted_availability_tests=TunableTestSet(description='\n                A set of tests that must pass in order for this narrative to be available. These \n                tests will only be run when there is an Actor and a Target Sim.\n                ')))
    TYPES_OF_POSTS = TunableList(description='\n        A set of the different Posts that can be made in Social Media.\n        ',
      tunable=TunableTuple(post_type=TunableEnumEntry(description='\n                A SocialMediaPostType enum entry.\n                ',
      tunable_type=SocialMediaPostType,
      default=(SocialMediaPostType.DEFAULT)),
      narrative=TunableEnumEntry(description='\n                A SocialMediaNarrative enum entry.\n                ',
      tunable_type=SocialMediaNarrative,
      default=(SocialMediaNarrative.FRIENDLY)),
      polarity=TunableEnumEntry(description='\n                A SocialMediaPolarity enum entry.\n                ',
      tunable_type=SocialMediaPolarity,
      default=(SocialMediaPolarity.POSITIVE)),
      content=TunableList(description='\n                The list of strings that can be randomly used for this post.\n                ',
      tunable=(TunableLocalizedString())),
      context_post=OptionalTunable(description='\n                The Buff that will allow for this contextual post to be made.\n                ',
      tunable=(Buff.TunablePackSafeReference())),
      loots_on_post=TunableList(description='\n                Loots applied to the actor when the post is made.\n                ',
      tunable=LootActions.TunableReference(description='\n                    A loot applied to the actor when the post is made.\n                    ',
      pack_safe=True)),
      target_loots_on_post=TunableList(description='\n                Loots applied to the target when the post is made.\n                ',
      tunable=LootActions.TunableReference(description='\n                    A loot applied to the target when the post is made.\n                    ',
      pack_safe=True))))