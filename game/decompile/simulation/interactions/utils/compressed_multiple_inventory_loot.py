# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\compressed_multiple_inventory_loot.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 13735 bytes
from bucks.bucks_enums import BucksType
from bucks.bucks_recycling import BucksRecycling
from bucks.bucks_utils import BucksUtils
from event_testing.resolver import SingleActorAndObjectResolver
from interactions import ParticipantTypeSingle
from interactions.utils.loot_basic_op import BaseLootOperation
from objects.gallery_tuning import ContentSource
from sims4.tuning.tunable import TunableList, TunableVariant, HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunableTuple, TunableReference
from tunable_multiplier import TunableMultiplier
import build_buy, services, sims4
logger = sims4.log.Logger('CompressedMultipleInventoryLoot', default_owner='nabaker')

class CompressedMultipleInventoryLoot(BaseLootOperation):

    @staticmethod
    def _verify_loot_list_callback(instance_class, tunable_name, source, value):
        if not value:
            logger.error('No loot tuned for {}', instance_class)
        for loot in value[:-1]:
            if loot.finalizes:
                logger.error("Loot {} isn't last loot in {} but must be", loot, value)

    class _ObjectLootBase:

        @property
        def finalizes(self):
            return True

        @property
        def require_individual_extract(self):
            return False

        def apply(self, obj, subject, count, resolver):
            raise NotImplementedError

    class _DestroyObject(_ObjectLootBase, HasTunableSingletonFactory, AutoFactoryInit):

        def apply(self, obj, subject, count, resolver):
            obj.destroy(source=self, cause='Destroying specified objects from compressed_multiple_inventory_loot.')

    class _MoveToInventory(_ObjectLootBase, HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'inventory_owner': TunableEnumEntry(description='"\n                The owner of the inventory in which the object should be placed..\n                ',
                              tunable_type=ParticipantTypeSingle,
                              default=(ParticipantTypeSingle.Object))}

        def apply(self, obj, subject, count, resolver):
            inventory_owner = resolver.get_participant(self.inventory_owner)
            if inventory_owner.is_sim:
                inventory_owner = inventory_owner.get_sim_instance()
            if inventory_owner is None or inventory_owner.inventory_component is None:
                logger.error('{} Compressed multiple inventory loot move to inventory  fail. {} has no inventory', resolver, subject)
                return
            inventory_owner.inventory_component.system_add_object(obj)

    class _RecycleBucksLoot(_ObjectLootBase, HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'bucks_types':TunableList(description='\n                The type of Bucks to grant.\n                ',
           tunable=TunableTuple(buck_type=TunableEnumEntry(tunable_type=BucksType,
           default=(BucksType.INVALID)),
           buck_multiplier=TunableMultiplier.TunableFactory(description='\n                        Multipliers to apply only to this buck type when recycling an object.\n                        '))), 
         'bucks_multipliers':TunableMultiplier.TunableFactory(description='\n                Multipliers to apply to all bucks amounts granted by recycling an object.\n                ')}

        @property
        def finalizes(self):
            return False

        @property
        def require_individual_extract(self):
            return False

        def apply(self, obj, subject, count, resolver):
            bucks_multiplier = self.bucks_multipliers.get_multiplier(resolver) * count
            for buck_type_tuning in self.bucks_types:
                amount = BucksRecycling.get_recycling_value_for_object(buck_type_tuning.buck_type, obj)
                if amount == 0:
                    continue
                final_multiplier = bucks_multiplier * buck_type_tuning.buck_multiplier.get_multiplier(resolver)
                amount *= final_multiplier
                tracker = BucksUtils.get_tracker_for_bucks_type((buck_type_tuning.buck_type), owner_id=(subject.id), add_if_none=True)
                if tracker is None:
                    logger.error('Attempting to apply a BucksLoot op to the subject {} of amount {} but they have no tracker for that bucks type {}.', subject, amount, buck_type_tuning.buck_type)
                    continue
                result = tracker.try_modify_bucks(buck_type_tuning.buck_type, int(amount))
                if not result:
                    logger.error("Failed to modify the Sim {}'s bucks of type {} by amount {}.", subject, buck_type_tuning.buck_type, self._amount)

            resolver = SingleActorAndObjectResolver(subject, obj, self)
            for _ in range(count):
                for loot_action in obj.recycling_data.recycling_loot:
                    loot_action.apply_to_resolver(resolver)

    FACTORY_TUNABLES = {'object_loot_list':TunableList(description='\n            A list of loot operations.  Destruction or inventory transfer must\n            be last. (If either is used.)\n            ',
       tunable=TunableVariant(destroy_object=(_DestroyObject.TunableFactory()),
       move_to_inventory=(_MoveToInventory.TunableFactory()),
       recycle_bucks_loot=(_RecycleBucksLoot.TunableFactory()),
       default='destroy_object'),
       verify_tunable_callback=_verify_loot_list_callback), 
     'found_objects_loot':TunableList(description="\n           List of loots that will be awarded if at least one of\n           the expected objects is still in inventory.  Doesn't reference\n           the individual objects picked.\n           ",
       tunable=TunableReference(description='\n                A loot to be applied if at least one of the expected objects\n                is in inventory when this loot is ru\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot')))}

    def __init__(self, *args, object_loot_list=None, found_objects_loot=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.object_loot_list = object_loot_list
        self.found_objects_loot = found_objects_loot
        self.individual_extract = False
        for loot in self.object_loot_list:
            if loot.require_individual_extract:
                self.individual_extract = True
                break

    def _apply_to_subject_and_target(self, subject, target, resolver):
        interaction = resolver.interaction
        if interaction is None:
            logger.error('Attempting to use CompressedMultipleInventoryLoot {} with a non interaction resolver', self)
            return
        object_infos = interaction.interaction_parameters.get('compressed_multiple_inventory_items')
        if object_infos is None:
            logger.error("Attempting to use CompressedMultipleInventoryLoot {} with an interaction that isn't a continuation {} of a ObjectsInMultipleInventoriesPurchasePickerInteraction", self, interaction)
            return
        if subject.is_sim:
            subject = subject.get_sim_instance()
        if subject is None:
            logger.error('Attempting to use CompressedMultipleInventoryLoot {} with uninstantiated sim info for interaction {}', self, interaction)
            return
        object_manager = services.object_manager()
        inventory_manager = services.current_zone().inventory_manager
        household = subject.household if subject.is_sim else None
        inventory_component = subject.inventory_component
        found_one = False
        for object_info in object_infos:
            object_id, count = object_info
            obj = object_manager.get(object_id)
            if obj is None:
                obj = inventory_manager.get(object_id)
            elif obj is None:
                continue
            else:
                obj_list = []
                if obj.content_source == ContentSource.HOUSEHOLD_INVENTORY_PROXY:
                    if household is None:
                        logger.error('Attempting to retrieve item from household of entity {} that has no household in {}', subject, self)
                        continue
                    removed_from_household_inventory = build_buy.remove_object_from_household_inventory(obj.id, household)
                    if removed_from_household_inventory:
                        obj_list.append(obj)
                elif inventory_component is None:
                    logger.error("Attempting to remove object from {}'s inventory that has no inventory component in CompressedMultipleInventoryLoot {}.  Ensure the subject matches up with the picker's", subject, self)
                    continue
                if self.individual_extract:
                    for _ in range(count):
                        new_obj = inventory_component.try_split_object_from_stack_by_id(obj.id)
                        if inventory_component.try_remove_object_by_id(obj, on_manager_remove=True):
                            obj_list.append(obj)
                        if new_obj is None:
                            break
                        obj = new_obj

                    count = 1
                else:
                    if inventory_component.try_remove_object_by_id((obj.id), count=count, on_manager_remove=True):
                        obj_list.append(obj)
                    count = obj.stack_count()
            if obj_list:
                found_one = True
            for obj in obj_list:
                for loot in self.object_loot_list:
                    loot.apply(obj, subject, count, resolver)

                if loot.finalizes or obj.content_source == ContentSource.HOUSEHOLD_INVENTORY_PROXY:
                    if not build_buy.move_object_to_household_inventory(obj):
                        logger.error('Failed to move {} to household inventory {} in {}', obj, household, self)
                else:
                    inventory_component.system_add_object(obj)

        if found_one:
            for loot in self.found_objects_loot:
                loot.apply_to_resolver(resolver)