# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relationships\relationship_bit.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 26905 bytes
from contextlib import contextmanager
from event_testing.resolver import DoubleSimResolver
from objects.mixins import SuperAffordanceProviderMixin, MixerProviderMixin
from relationships.relationship_enums import RelationshipBitCullingPrevention, RelationshipDirection
from sims4.localization import TunableLocalizedString, TunableLocalizedStringFactory
from sims4.resources import CompoundTypes
from sims4.tuning.dynamic_enum import DynamicEnum, DynamicEnumLocked, validate_locked_enum_id
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableResourceKey, Tunable, TunableList, TunableEnumEntry, TunableReference, TunableTuple, OptionalTunable, TunableSimMinute, HasTunableReference, TunableRange, TunableThreshold
from sims4.tuning.tunable_base import ExportModes, EnumBinaryExportType
from sims4.utils import classproperty
from ui.ui_dialog_notification import TunableUiDialogNotificationSnippet
from ui.ui_utils import hide_selected_notifications, UIUtils
import buffs.tunable, services, sims.sim_info_types, sims4.log, sims4.resources
logger = sims4.log.Logger('Relationship', default_owner='msantander')

class RelationshipBitType(DynamicEnum):
    Invalid = 0
    NoGroup = 1


class RelationshipBitCollectionUid(DynamicEnumLocked, display_sorted=True):
    Invalid = 0
    All = 1


class RelationshipBit(HasTunableReference, SuperAffordanceProviderMixin, MixerProviderMixin, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)):
    INSTANCE_TUNABLES = {'display_name':TunableLocalizedStringFactory(description='\n            Localized name of this bit\n            ',
       allow_none=True,
       export_modes=ExportModes.All), 
     'bit_description':TunableLocalizedStringFactory(description='\n            Localized description of this bit\n            ',
       allow_none=True,
       export_modes=ExportModes.All), 
     'icon':TunableResourceKey(description='\n            Icon to be displayed for the relationship bit.\n            ',
       allow_none=True,
       resource_types=CompoundTypes.IMAGE,
       export_modes=ExportModes.All), 
     'bit_added_notification':OptionalTunable(description='\n            If enabled, a notification will be displayed when this bit is added.\n            ',
       tunable=TunableTuple(notification=(TunableUiDialogNotificationSnippet()),
       show_if_unselectable=Tunable(description='\n                    If this is checked, then the notification is displayed if\n                    the owning Sim is not selectable, but the target is.\n                    Normally, notifications are only displayed if the owning Sim\n                    is selectable.\n                    ',
       tunable_type=bool,
       default=False))), 
     'bit_removed_notification':OptionalTunable(description='\n            If enabled, a notification will be displayed when this bit is removed.\n            ',
       tunable=TunableUiDialogNotificationSnippet()), 
     'depth':Tunable(description='\n            The amount of depth provided by the bit.\n            ',
       tunable_type=int,
       default=0), 
     'priority':Tunable(description='\n            Priority of the bit.  This is used when a bit turns on while a\n            mutually exclusive bit is already on.\n            ',
       tunable_type=float,
       default=0), 
     'display_priority':Tunable(description='\n            The priority of this bit with regards to UI.  Only the highest\n            priority bits are displayed.\n            ',
       tunable_type=int,
       default=0,
       export_modes=ExportModes.All), 
     'exclusive':Tunable(description="\n            Whether or not the bit is exclusive. This means that a sim can only have \n            this bit with one other sim.  If you attempt to add an exclusive bit to \n            a sim that already has the same one with another sim, it will remove the \n            old bit.\n            \n            Example: A sim can only be BFF's with one other sim.  If the sim asks \n            another sim to be their BFF, the old bit is removed.\n            ",
       tunable_type=bool,
       default=False), 
     'visible':Tunable(description="\n            If True, this bit has the potential to be visible when applied,\n            depending on display_priority and the other active bits.  If False,\n            the bit will not be displayed unless it's part of the\n            REL_INSPECTOR_TRACK bit track.\n            ",
       tunable_type=bool,
       default=True,
       export_modes=ExportModes.All), 
     'invisible_filterable':Tunable(description="\n            If True, this bit can be used by the UI for filtering even though it isn't visible.\n            ",
       tunable_type=bool,
       default=False), 
     'group_id':TunableEnumEntry(description='\n            The group this bit belongs to.  Two bits of the same group cannot\n            belong in the same set of bits for a given relationship.\n            ',
       tunable_type=RelationshipBitType,
       default=RelationshipBitType.NoGroup), 
     'triggered_track':TunableReference(description='\n            If set, the track that is triggered when this bit is set\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC),
       allow_none=True,
       class_restrictions='RelationshipTrack'), 
     'required_bits':TunableList(description='\n            List of all bits that are required to be on in order to allow this\n            bit to turn on.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)))), 
     'timeout':TunableSimMinute(description='\n            The length of time this bit will last in sim minutes.  0 means the\n            bit will never timeout.\n            ',
       default=0), 
     'remove_on_threshold':OptionalTunable(tunable=TunableTuple(description='\n                If enabled, this bit will be removed when the referenced track\n                reaches the appropriate threshold.\n                ',
       track=TunableReference(description='\n                    The track to be tested.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
       class_restrictions='RelationshipTrack'),
       threshold=TunableThreshold(description='\n                    The threshold at which to remove this bit.\n                    '))), 
     'collection_ids':TunableList(tunable=TunableEnumEntry(description='\n                The bit collection id this bit belongs to, like family,\n                friends, romance. Default to be All.\n                ',
       tunable_type=RelationshipBitCollectionUid,
       default=(RelationshipBitCollectionUid.All),
       export_modes=(ExportModes.All))), 
     'buffs_on_add_bit':TunableList(tunable=TunableTuple(buff_ref=buffs.tunable.TunableBuffReference(description='\n                    Buff that gets added to sim when bit is added.\n                    ',
       pack_safe=True),
       amount=Tunable(description='\n                    If buff is tied to commodity the amount to add to the\n                    commodity.\n                    ',
       tunable_type=float,
       default=1),
       only_add_once=Tunable(description='\n                    If True, the buff should only get added once no matter how\n                    many times this bit is being applied.\n                    ',
       tunable_type=bool,
       default=False))), 
     'buffs_to_add_if_on_active_lot':TunableList(description="\n            List of buffs to add when a sim that I share this relationship with\n            is in the household that owns the lot that I'm on.\n            ",
       tunable=buffs.tunable.TunableBuffReference(description='\n                Buff that gets added to sim when bit is added.\n                ')), 
     'autonomy_multiplier':Tunable(description='\n            This value is multiplied to the autonomy score of any interaction\n            performed between the two Sims.  For example, when the Sim decides\n            to socialize, she will start looking at targets to socialize with.\n            If there is a Sim who she shares this bit with, her final score for\n            socializing with that Sim will be multiplied by this value.\n            ',
       tunable_type=float,
       default=1), 
     'relationship_culling_prevention':TunableEnumEntry(description='\n            Determine if bit should prevent relationship culling.  \n            \n            ALLOW_ALL = all culling\n            PLAYED_ONLY = only cull if not a played household\n            PLAYED_AND_UNPLAYED = disallow culling for played and unplayed sims. (e.g. family bits)\n            ',
       tunable_type=RelationshipBitCullingPrevention,
       default=RelationshipBitCullingPrevention.ALLOW_ALL), 
     'persisted_tuning':Tunable(description='\n            Whether this bit will persist when saving a Sim. \n            \n            For example, a Sims is good_friends should be set to true, but\n            romantic_gettingMarried should not be saved.\n            ',
       tunable_type=bool,
       default=True), 
     'bit_added_loot_list':TunableList(description='\n            A list of loot operations to apply when this relationship bit is\n            added.\n            \n            Bidirectional bits apply the loot to both source and target sims \n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', ),
       pack_safe=True)), 
     'bit_removed_loot_list':TunableList(description='\n            A list of loot operations to apply when this relationship bit is\n            removed.\n            \n            Bidirectional bits apply the loot to both source and target sims\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', ),
       pack_safe=True)), 
     'directionality':TunableEnumEntry(description='\n            The direction that this Relationship bit points.  Bidirectional\n            means that both Sims will be given this bit if it is added.\n            Unidirectional means that only one Sim will be given this bit.\n            If it is coming from loot that bit will be given to the Actor.\n            ',
       tunable_type=RelationshipDirection,
       default=RelationshipDirection.BIDIRECTIONAL,
       binary_type=EnumBinaryExportType.EnumUint32,
       export_modes=ExportModes.All), 
     'whim_set':OptionalTunable(description='\n            If enabled then this relationship bit will offer a whim set to the sim\n            when it is active.\n            ',
       tunable=TunableTuple(whim_set=TunableReference(description='\n                    A whim set that is active when this relationship bit is on the sim.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.ASPIRATION)),
       class_restrictions=('ObjectivelessWhimSet', )),
       apply_to_target=Tunable(description='\n                    If true, for Unidirectional relbits the whimset will be added to the TARGET of the relationship.\n                    Not the sim that actually has the relbit.  \n                    \n                    Primarily intended to be used for sentiment related bits as sentiments are tuned backwards.\n                    ',
       tunable_type=bool,
       default=False))), 
     'counts_as_incest':Tunable(description='\n            If true, romantic relationships between sims with this bet are prevented because it would be incestuous.\n            \n            Note:  This is mainly a backup for bits added outside of genealogy.\n            ',
       tunable_type=bool,
       default=False)}
    is_track_bit = False
    trait_replacement_bits = None
    _cached_commodity_flags = None
    is_trope_bit = False

    def __init__(self):
        self._buff_handles = None
        self._conditional_removal_listener = None
        self._appropriate_buffs_handles = None

    @classproperty
    def persisted(cls):
        return cls.persisted_tuning

    @classproperty
    def is_collection(cls):
        return False

    def add_buffs_for_bit_add(self, sim, relationship, from_load):
        for buff_data in self.buffs_on_add_bit:
            buff_type = buff_data.buff_ref.buff_type
            if from_load:
                if buff_type.commodity:
                    continue
            if buff_data.only_add_once:
                if buff_type.guid64 in relationship.get_bit_added_buffs(sim.sim_id):
                    continue
                relationship.add_bit_added_buffs(sim.sim_id, buff_type)
            if buff_type.commodity:
                tracker = sim.get_tracker(buff_type.commodity)
                tracker.add_value(buff_type.commodity, buff_data.amount)
                sim.set_buff_reason(buff_type, buff_data.buff_ref.buff_reason)
            else:
                buff_handle = sim.add_buff(buff_type, buff_reason=(buff_data.buff_ref.buff_reason))
                if self._buff_handles is None:
                    self._buff_handles = []
                self._buff_handles.append((sim.sim_id, buff_handle))

    def _apply_bit_added_loot(self, sim_info, target_sim_info):
        resolver = DoubleSimResolver(sim_info, target_sim_info)
        for loot in self.bit_added_loot_list:
            loot.apply_to_resolver(resolver)

    def on_add_to_relationship(self, sim, target_sim_info, relationship, from_load):
        if relationship.is_object_rel:
            return
        else:
            target_sim = target_sim_info.get_sim_instance()
            self.add_buffs_for_bit_add(sim, relationship, from_load)
            if target_sim is not None:
                if self.directionality == RelationshipDirection.BIDIRECTIONAL:
                    self.add_buffs_for_bit_add(target_sim, relationship, from_load)
            if not from_load:
                self._apply_bit_added_loot(sim.sim_info, target_sim_info)
                if self.directionality == RelationshipDirection.BIDIRECTIONAL:
                    self._apply_bit_added_loot(target_sim_info, sim.sim_info)

    def _apply_bit_removed_loot(self, sim_info, target_sim_info):
        resolver = DoubleSimResolver(sim_info, target_sim_info)
        for loot in self.bit_removed_loot_list:
            loot.apply_to_resolver(resolver)

    def on_remove_from_relationship(self, sim, target_sim_info):
        target_sim = target_sim_info.get_sim_instance()
        if self._buff_handles is not None:
            for sim_id, buff_handle in self._buff_handles:
                if sim.sim_id == sim_id:
                    sim.remove_buff(buff_handle)

            self._buff_handles = None
        self._apply_bit_removed_loot(sim.sim_info, target_sim_info)
        if self.directionality == RelationshipDirection.BIDIRECTIONAL:
            self._apply_bit_removed_loot(target_sim_info, sim.sim_info)

    def add_appropriateness_buffs(self, sim_info):
        if not self._appropriate_buffs_handles:
            if self.buffs_to_add_if_on_active_lot:
                self._appropriate_buffs_handles = []
                for buff in self.buffs_to_add_if_on_active_lot:
                    handle = sim_info.add_buff((buff.buff_type), buff_reason=(buff.buff_reason))
                    self._appropriate_buffs_handles.append(handle)

    def remove_appropriateness_buffs(self, sim_info):
        if self._appropriate_buffs_handles is not None:
            for buff in self._appropriate_buffs_handles:
                sim_info.remove_buff(buff)

            self._appropriate_buffs_handles = None

    def add_conditional_removal_listener(self, listener):
        if self._conditional_removal_listener is not None:
            logger.error('Attempting to add a conditional removal listener when one already exists; old one will be overwritten.', owner='jjacobson')
        self._conditional_removal_listener = listener

    def remove_conditional_removal_listener(self):
        listener = self._conditional_removal_listener
        self._conditional_removal_listener = None
        return listener

    def __repr__(self):
        bit_type = type(self)
        return '<({}) Type: {}.{}>'.format(bit_type.__name__, bit_type.__mro__[1].__module__, bit_type.__mro__[1].__name__)

    @classmethod
    def commodity_flags(cls):
        if cls._cached_commodity_flags is None:
            commodity_flags = set()
            for super_affordance in cls.get_provided_super_affordances_gen():
                commodity_flags.update(super_affordance.commodity_flags)

            cls._cached_commodity_flags = frozenset(commodity_flags)
        return cls._cached_commodity_flags

    def show_bit_added_dialog(self, owner, sim, target_sim_info):
        if UIUtils.get_hide_selected_notification_status():
            return
        dialog = self.bit_added_notification.notification(owner, DoubleSimResolver(sim, target_sim_info))
        dialog.show_dialog(additional_tokens=(sim, target_sim_info))

    def show_bit_removed_dialog(self, sim, target_sim_info):
        if UIUtils.get_hide_selected_notification_status():
            return
        dialog = self.bit_removed_notification(sim, DoubleSimResolver(sim, target_sim_info))
        dialog.show_dialog(additional_tokens=(sim, target_sim_info))

    @classmethod
    def matches_bit(cls, bit_type):
        return cls is bit_type


class SocialContextBit(RelationshipBit):
    INSTANCE_TUNABLES = {'size_limit':OptionalTunable(description='\n            If enabled, this bit will only be available if the owner Sim is in a\n            social context with the specified number of Sims. If there are more\n            Sims than the specified limit, the bit will transform to another\n            form, i.e. to a different bit.\n            ',
       tunable=TunableTuple(size=TunableRange(description='\n                    The maximum number of Sims that can share a social context\n                    in order for this bit to be visible.\n                    ',
       tunable_type=int,
       default=2,
       minimum=0),
       transformation=RelationshipBit.TunableReference(description='\n                    The bit that is going to replace this bit if the size limit\n                    is violated.\n                    ',
       class_restrictions='SocialContextBit'))), 
     'attention_cost':Tunable(description='\n            Any Sim in this social context will add this amount to the attention\n            cost of any social super interaction they are running.\n            ',
       tunable_type=float,
       default=0)}

    def on_add_to_relationship(self, sim, target_sim_info, relationship, from_load):
        sim.on_social_context_changed()
        target_sim = target_sim_info.get_sim_instance()
        if target_sim is not None:
            target_sim.on_social_context_changed()
        return super().on_add_to_relationship(sim, target_sim_info, relationship, from_load)

    def on_remove_from_relationship(self, sim, target_sim_info):
        sim.on_social_context_changed()
        target_sim = target_sim_info.get_sim_instance()
        if target_sim is not None:
            target_sim.on_social_context_changed()
        return super().on_remove_from_relationship(sim, target_sim_info)


class RelationshipBitCollection(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)):
    INSTANCE_TUNABLES = {'name':TunableLocalizedString(description='\n            Name to be displayed for the collection.\n            ',
       export_modes=ExportModes.All), 
     'icon':TunableResourceKey(description='\n            Icon to be displayed for the collection.\n            ',
       allow_none=True,
       resource_types=CompoundTypes.IMAGE,
       export_modes=ExportModes.All), 
     'collection_id':TunableEnumEntry(description='\n            The unique id of the relationship bit\n            ',
       tunable_type=RelationshipBitCollectionUid,
       default=RelationshipBitCollectionUid.Invalid,
       export_modes=ExportModes.All)}

    @classproperty
    def is_collection(cls):
        return True

    @classmethod
    def _verify_tuning_callback(cls):
        validate_locked_enum_id(RelationshipBitCollection, cls.collection_id, cls, RelationshipBitCollectionUid.Invalid)

    @classmethod
    def matches_bit(cls, bit_type):
        return cls.collection_id in bit_type.collection_ids