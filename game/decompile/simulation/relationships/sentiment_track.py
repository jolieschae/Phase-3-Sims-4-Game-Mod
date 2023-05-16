# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relationships\sentiment_track.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 5117 bytes
from interactions.utils.loot import LootActions
from relationships.relationship_track import RelationshipTrack
from relationships.relationship_enums import SentimentDurationType
from relationships.relationship_enums import SentimentSignType
from relationships.relationship_enums import RelationshipTrackType
from relationships.tunable import SentimentRelationshipTrackData
from sims4.localization import TunableLocalizedString
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableList, TunableEnumEntry, OptionalTunable, TunableRange, Tunable
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import classproperty
from tunable_multiplier import TunableMultiplier

class SentimentTrack(RelationshipTrack):
    INSTANCE_TUNABLES = {'duration':TunableEnumEntry(description='\n            The duration of this sentiment. Must be either long or short type.  \n            ',
       tunable_type=SentimentDurationType,
       default=SentimentDurationType.INVALID,
       invalid_enums=(
      SentimentDurationType.INVALID,)), 
     'sign':TunableEnumEntry(description='\n            The sign of this sentiment. Must be either positive or negative \n            type.  \n            ',
       tunable_type=SentimentSignType,
       default=SentimentSignType.INVALID,
       invalid_enums=(
      SentimentDurationType.INVALID,)), 
     'archetype_name':TunableLocalizedString(description='\n            The localized archetype name for this sentiment.\n            Eg: hurt/ecstatic/glad  \n            '), 
     'loot_on_proximity':TunableList(description='\n            A list of loot actions that will be applied to the subject Sim if \n            the subject sim comes in proximity of the target sim, and the \n            subject sim is not in a cooldown period for the target sim.\n            Resolver Participants:\n            actor - sim owning the sentiment\n            target - target of the sentiment\n            ',
       tunable=LootActions.TunableReference(description='\n                A loot action applied to the subject Sim.\n                ',
       tuning_group=(GroupNames.SENTIMENT_LOOT))), 
     'proximity_loot_chance_weight':TunableMultiplier.TunableFactory(description='\n            The random weight for this loot to be applied when in proximity of \n            a sim that this sim has a sentiment towards.\n            Resolver Participants:\n            actor - sim owning the sentiment\n            target - target of the sentiment\n            ',
       tuning_group=GroupNames.SENTIMENT_LOOT), 
     'long_term_priority':OptionalTunable(description='\n            Priority for long term sentiments.\n            Long term sentiment with higher priority will always replace\n            existing sentiment with lower (or No) priority.\n            Long term sentiment with lower (or No) priority will only\n            replace existing sentiment with higher priority if existing sentiments\n            remaining duration is shorter than the long term priority value threshold\n            in sentiment track tracker module tuning.\n            \n            (NOte: 0 priority beats No priority)\n            ',
       tunable=TunableRange(tunable_type=int,
       default=0,
       minimum=0)), 
     'should_proximity_loot_include_bassinet':Tunable(description="\n            If True, we will apply the proximity loot if target sim is a bassinet.\n            If False, we won't apply the proximity loot if target sim is a bassinet.\n            \n            For example, we want to set this to True on sentimentTrack_Bitter_ST_SiblingJealousy,\n            so the sim will feel jealousy when near the bassinet baby.\n            ",
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.SENTIMENT_LOOT)}

    @classproperty
    def track_type(cls):
        return RelationshipTrackType.SENTIMENT

    def build_single_relationship_track_proto(self, relationship_track_update):
        super().build_single_relationship_track_proto(relationship_track_update)
        relationship_track_update.track_type = RelationshipTrackType.SENTIMENT
        relationship_track_update.sign_type = self.sign
        relationship_track_update.duration_type = self.duration
        relationship_track_update.archetype_name = self.archetype_name


lock_instance_tunables(SentimentTrack, bit_data_tuning=SentimentRelationshipTrackData,
  _add_bit_on_threshold=None,
  display_priority=1)