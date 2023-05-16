# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\rewards\reward_tuning.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 21497 bytes
from bucks.bucks_enums import BucksType
from bucks.bucks_utils import BucksUtils
from buffs.tunable import TunableBuffReference
from business.business_reward_tuning import TunableRewardAdditionalEmployeeSlot, TunableRewardAdditionalCustomerCount, TunableRewardAdditionalMarkup
from clubs.club_enums import ClubGatheringVibe
from objects import ALL_HIDDEN_REASONS
from objects.object_enums import ItemLocation
from objects.system import create_object
from protocolbuffers import Consts_pb2
from protocolbuffers.DistributorOps_pb2 import SetWhimBucks
from rewards.reward_enums import RewardDestination, RewardType
from rewards.tunable_reward_base import TunableRewardBase
from sims4.common import is_available_pack
from sims4.localization import LocalizationHelperTuning
from sims4.resources import Types
from sims4.tuning.dynamic_enum import _get_pack_from_enum_value
from sims4.tuning.tunable import TunableVariant, TunableReference, Tunable, TunableTuple, TunableCasPart, TunableMagazineCollection, TunableLiteralOrRandomValue, TunableEnumEntry, TunableRange, AutoFactoryInit, TunableFactory
from sims4.utils import constproperty
import build_buy, services, sims4.resources
logger = sims4.log.Logger('Rewards', default_owner='trevor')

class TunableRewardObject(TunableRewardBase):
    FACTORY_TUNABLES = {'definition': TunableReference(description='\n            Give an object as a reward.\n            ',
                     manager=(services.definition_manager()))}

    def __init__(self, *args, definition, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._definition = definition

    @constproperty
    def reward_type():
        return RewardType.OBJECT_DEFINITION

    def _try_create_in_mailbox(self, sim_info):
        if sim_info.household is None:
            logger.error('Trying to add an item [{}] to a mailbox but the provided sim [{}] has no household', (self._definition),
              sim_info, owner='trevor')
            return False
        zone = services.get_zone(sim_info.household.home_zone_id)
        if zone is None:
            logger.error('Trying to add an item [{}] to a mailbox but the provided sim [{}] has no home zone.', (self._definition),
              sim_info, owner='trevor')
            return False
        lot_hidden_inventory = zone.lot.get_hidden_inventory()
        if lot_hidden_inventory is None:
            logger.error("Trying to add an item [{}] to the lot's hidden inventory but the provided sim [{}] has no hidden inventory for their lot.", (self._definition),
              sim_info, owner='trevor')
            return False
        obj = create_object(self._definition)
        if obj is None:
            logger.error('Trying to give an object reward to a Sim, {}, and the object created was None. Definition: {}', sim_info, self._definition)
            return False
        try:
            lot_hidden_inventory.system_add_object(obj)
        except:
            logger.error('Could not add object [{}] to the mailbox inventory on the home lot of the Sim [{}].', obj,
              sim_info, owner='trevor')
            obj.destroy(source=self, cause='Could not add object to the mailbox inventory')
            return False
            return True

    def _try_create_in_sim_inventory(self, sim_info, obj=None, force_rewards_to_sim_info_inventory=False):
        sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if sim is None:
            if force_rewards_to_sim_info_inventory:
                obj = create_object(self._definition) if obj is None else obj
                return sim_info.try_add_object_to_inventory_without_component(obj)
        else:
            return (False, None)
            obj = create_object(self._definition) if obj is None else obj
            if obj is None:
                logger.error('Trying to give an object reward to a Sim, {}, and the object created was None. Definition: {}', sim_info, self._definition)
                return (False, None)
            result = sim.inventory_component.player_try_add_object(obj)
            return result or (
             False, obj)
        obj.update_ownership(sim_info)
        return (True, obj)

    def _try_create_in_household_inventory(self, sim_info, obj=None):
        obj = create_object((self._definition), loc_type=(ItemLocation.HOUSEHOLD_INVENTORY)) if obj is None else obj
        if obj is None:
            logger.error('Trying to give an object reward to a Sim, {}, and the object created was None. Definition: {}', sim_info, self._definition)
            return (False, None)
        obj.update_ownership(sim_info, make_sim_owner=False)
        obj.set_post_bb_fixup_needed()
        if not build_buy.move_object_to_household_inventory(obj):
            logger.error('Failed to add reward definition object {} to household inventory.', (self._definition),
              owner='rmccord')

    def open_reward(self, sim_info, reward_destination=RewardDestination.HOUSEHOLD, force_rewards_to_sim_info_inventory=False, **kwargs):
        if reward_destination == RewardDestination.MAILBOX:
            self._try_create_in_mailbox(sim_info)
            return
        reward_object = None
        if reward_destination == RewardDestination.SIM:
            result, reward_object = self._try_create_in_sim_inventory(sim_info, force_rewards_to_sim_info_inventory=force_rewards_to_sim_info_inventory)
            if result:
                return
        self._try_create_in_household_inventory(sim_info, obj=reward_object)

    def _get_display_text(self, resolver=None):
        return LocalizationHelperTuning.get_object_name(self._definition)


class TunableRewardCASPart(TunableRewardBase):
    FACTORY_TUNABLES = {'cas_part': TunableCasPart(description='\n            The cas part for this reward.\n            ')}

    def __init__(self, *args, cas_part, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._cas_part = cas_part

    @constproperty
    def reward_type():
        return RewardType.CAS_PART

    def open_reward(self, sim_info, reward_source=None, **kwargs):
        household = sim_info.household
        household.add_cas_part_to_reward_inventory(self._cas_part)
        if reward_source is not None:
            if self._cas_part is not None:
                self.send_unlock_telemetry(sim_info, self._cas_part, reward_source.guid64)

    def valid_reward(self, sim_info):
        return not sim_info.household.part_in_reward_inventory(self._cas_part)


class TunableRewardMoney(TunableRewardBase):
    FACTORY_TUNABLES = {'money': TunableLiteralOrRandomValue(description='\n            Give money to a sim/household.\n            ',
                tunable_type=int,
                default=10)}

    def __init__(self, *args, money, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._awarded_money = money.random_int()

    @constproperty
    def reward_type():
        return RewardType.MONEY

    def open_reward(self, sim_info, **kwargs):
        household = services.household_manager().get(sim_info.household_id)
        if household is not None:
            household.funds.add(self._awarded_money, Consts_pb2.TELEMETRY_MONEY_ASPIRATION_REWARD, sim_info.get_sim_instance())

    def _get_display_text(self, resolver=None):
        return LocalizationHelperTuning.get_money(self._awarded_money)


class TunableRewardTrait(TunableRewardBase):
    FACTORY_TUNABLES = {'trait': TunableReference(description='\n            Give a trait as a reward\n            ',
                manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)))}

    def __init__(self, *args, trait, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._trait = trait

    @constproperty
    def reward_type():
        return RewardType.TRAIT

    def open_reward(self, sim_info, reward_destination=RewardDestination.HOUSEHOLD, **kwargs):
        if reward_destination == RewardDestination.HOUSEHOLD:
            household = sim_info.household
            for sim in household.sim_info_gen():
                sim.add_trait(self._trait)

        else:
            if reward_destination == RewardDestination.SIM:
                sim_info.add_trait(self._trait)
            else:
                logger.warn('Attempting to open a RewardTrait with an invalid destination: {}. Reward traits can only be given to households or sims.', reward_destination, owner='trevor')

    def valid_reward(self, sim_info):
        return sim_info.trait_tracker.can_add_trait(self._trait)


class TunableRewardBuildBuyUnlockBase(TunableRewardBase):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.instance = None
        self.type = Types.INVALID

    def get_resource_key(self):
        return NotImplementedError

    def get_id_for_telemetry(self):
        return self.instance.id

    def open_reward(self, sim_info, reward_destination=RewardDestination.HOUSEHOLD, reward_source=None, **kwargs):
        key = self.get_resource_key()
        if key is not None:
            if reward_destination == RewardDestination.SIM:
                sim_info.add_build_buy_unlock(key)
            else:
                if reward_destination == RewardDestination.HOUSEHOLD:
                    for household_sim_info in sim_info.household.sim_info_gen():
                        household_sim_info.add_build_buy_unlock(key)

                else:
                    logger.warn('Invalid reward destination () on build buy unlock. The household will still get the buildbuy unlock added.', reward_destination, owner='trevor')
            sim_info.household.add_build_buy_unlock(key)
        else:
            logger.warn('Invalid Build Buy unlock tuned. No reward given.')
        if self.instance is not None:
            if reward_source is not None:
                self.send_unlock_telemetry(sim_info, self.get_id_for_telemetry(), reward_source.guid64)


class TunableBuildBuyObjectDefinitionUnlock(TunableRewardBuildBuyUnlockBase):

    @TunableFactory.factory_option
    def get_definition(pack_safe):
        return {'object_definition': TunableReference(description='\n                The definition of the object to be created.\n                ',
                                manager=(services.definition_manager()),
                                pack_safe=pack_safe)}

    def __init__(self, *args, object_definition, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.instance = object_definition
        self.type = Types.OBJCATALOG

    @constproperty
    def reward_type():
        return RewardType.BUILD_BUY_OBJECT

    def get_resource_key(self):
        return sims4.resources.Key(self.type, self.instance.id)


class TunableBuildBuyMagazineCollectionUnlock(TunableRewardBuildBuyUnlockBase):
    FACTORY_TUNABLES = {'magazine_collection': TunableMagazineCollection(description='\n            Unlock a magazine room to purchase in build/buy.\n            ')}

    def __init__(self, *args, magazine_collection, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.instance = magazine_collection
        self.type = Types.MAGAZINECOLLECTION

    @constproperty
    def reward_type():
        return RewardType.BUILD_BUY_MAGAZINE_COLLECTION

    def get_resource_key(self):
        if self.instance is not None:
            return sims4.resources.Key(self.type, self.instance)
        return

    def get_id_for_telemetry(self):
        return self.instance


class TunableSetClubGatheringVibe(TunableRewardBase):
    FACTORY_TUNABLES = {'vibe_to_set': TunableEnumEntry(description='\n            The vibe that the club gathering will be set to.\n            ',
                      tunable_type=ClubGatheringVibe,
                      default=(ClubGatheringVibe.NO_VIBE))}

    def __init__(self, *args, vibe_to_set=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._vibe_to_set = vibe_to_set

    @constproperty
    def reward_type():
        return RewardType.SET_CLUB_GATHERING_VIBE

    def get_resource_key(self):
        return NotImplementedError

    def open_reward(self, sim_info, **kwargs):
        club_service = services.get_club_service()
        if club_service is None:
            return
        sim = sim_info.get_sim_instance()
        if sim is None:
            return
        gathering = club_service.sims_to_gatherings_map.get(sim, None)
        if gathering is None:
            return
        gathering.set_club_vibe(self._vibe_to_set)


class TunableRewardDisplayText(TunableRewardBase):

    @constproperty
    def reward_type():
        return RewardType.DISPLAY_TEXT

    def open_reward(self, _, **kwargs):
        return True


class TunableRewardBucks(AutoFactoryInit, TunableRewardBase):
    FACTORY_TUNABLES = {'bucks_type':TunableEnumEntry(description='\n            The type of Bucks to grant.\n            ',
       tunable_type=BucksType,
       default=BucksType.INVALID,
       invalid_enums=(
      BucksType.INVALID,),
       pack_safe=True), 
     'amount':TunableRange(description='\n            The amount of Bucks to award. Must be a positive value.\n            ',
       tunable_type=int,
       default=10,
       minimum=1)}

    @constproperty
    def reward_type():
        return RewardType.BUCKS

    def open_reward--- This code section failed: ---

 L. 423         0  LOAD_FAST                'self'
                2  LOAD_ATTR                bucks_type
                4  LOAD_CONST               None
                6  COMPARE_OP               is
                8  POP_JUMP_IF_TRUE     40  'to 40'
               10  LOAD_FAST                'self'
               12  LOAD_ATTR                bucks_type
               14  LOAD_GLOBAL              BucksType
               16  LOAD_ATTR                INVALID
               18  COMPARE_OP               ==
               20  POP_JUMP_IF_TRUE     40  'to 40'

 L. 424        22  LOAD_GLOBAL              is_available_pack
               24  LOAD_GLOBAL              _get_pack_from_enum_value
               26  LOAD_GLOBAL              int
               28  LOAD_FAST                'self'
               30  LOAD_ATTR                bucks_type
               32  CALL_FUNCTION_1       1  '1 positional argument'
               34  CALL_FUNCTION_1       1  '1 positional argument'
               36  CALL_FUNCTION_1       1  '1 positional argument'
               38  POP_JUMP_IF_TRUE     44  'to 44'
             40_0  COME_FROM            20  '20'
             40_1  COME_FROM             8  '8'

 L. 426        40  LOAD_CONST               None
               42  RETURN_VALUE     
             44_0  COME_FROM            38  '38'

 L. 428        44  LOAD_FAST                'sim_info'
               46  LOAD_ATTR                is_npc
               48  POP_JUMP_IF_FALSE    54  'to 54'

 L. 429        50  LOAD_CONST               None
               52  RETURN_VALUE     
             54_0  COME_FROM            48  '48'

 L. 431        54  LOAD_GLOBAL              BucksUtils
               56  LOAD_ATTR                get_tracker_for_bucks_type
               58  LOAD_FAST                'self'
               60  LOAD_ATTR                bucks_type
               62  LOAD_FAST                'sim_info'
               64  LOAD_ATTR                id
               66  LOAD_CONST               True
               68  LOAD_CONST               ('add_if_none',)
               70  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
               72  STORE_FAST               'tracker'

 L. 432        74  LOAD_FAST                'tracker'
               76  LOAD_CONST               None
               78  COMPARE_OP               is
               80  POP_JUMP_IF_FALSE   102  'to 102'

 L. 433        82  LOAD_GLOBAL              logger
               84  LOAD_METHOD              error
               86  LOAD_STR                 'Failed to open a TunableRewardBucks of buck type {} for Sim {}.'
               88  LOAD_FAST                'self'
               90  LOAD_ATTR                bucks_type
               92  LOAD_FAST                'sim_info'
               94  CALL_METHOD_3         3  '3 positional arguments'
               96  POP_TOP          

 L. 434        98  LOAD_CONST               None
              100  RETURN_VALUE     
            102_0  COME_FROM            80  '80'

 L. 436       102  LOAD_FAST                'tracker'
              104  LOAD_METHOD              try_modify_bucks
              106  LOAD_FAST                'self'
              108  LOAD_ATTR                bucks_type
              110  LOAD_FAST                'self'
              112  LOAD_ATTR                amount
              114  CALL_METHOD_2         2  '2 positional arguments'
              116  POP_TOP          

Parse error at or near `CALL_METHOD_2' instruction at offset 114


class TunableRewardBuff(AutoFactoryInit, TunableRewardBase):
    FACTORY_TUNABLES = {'buff': TunableBuffReference(description='\n            Buff to be given as a reward.\n            ')}

    @constproperty
    def reward_type():
        return RewardType.BUFF

    def open_reward(self, sim_info, reward_destination=RewardDestination.HOUSEHOLD, **kwargs):
        if reward_destination == RewardDestination.HOUSEHOLD:
            household = sim_info.household
            for sim_info in household.sim_info_gen():
                sim_info.add_buff_from_op(buff_type=(self.buff.buff_type), buff_reason=(self.buff.buff_reason))

        else:
            if reward_destination == RewardDestination.SIM:
                sim_info.add_buff_from_op(buff_type=(self.buff.buff_type), buff_reason=(self.buff.buff_reason))
            else:
                logger.error('Attempting to open a RewardBuff with an invalid destination: {}. Reward buffs can only be given to households or Sims.', reward_destination)


class TunableRewardWhimBucks(AutoFactoryInit, TunableRewardBase):
    FACTORY_TUNABLES = {'whim_bucks': TunableRange(description='\n            The number of whim bucks to give.\n            ',
                     tunable_type=int,
                     default=1,
                     minimum=1)}

    @constproperty
    def reward_type():
        return RewardType.WHIM_BUCKS

    def open_reward(self, sim_info, reward_destination=RewardDestination.HOUSEHOLD, **kwargs):
        if reward_destination == RewardDestination.HOUSEHOLD:
            household = sim_info.household
            for sim_info in household.sim_info_gen():
                sim_info.apply_satisfaction_points_delta(self.whim_bucks, SetWhimBucks.COMMAND)

        else:
            if reward_destination == RewardDestination.SIM:
                sim_info.apply_satisfaction_points_delta(self.whim_bucks, SetWhimBucks.COMMAND)
            else:
                logger.error('Attempting to open a RewardWhimBucks with an invalid destination: {}. Reward whim bucks can only be given to households or Sims.', reward_destination)


class TunableSpecificReward(TunableVariant):

    def __init__(self, description='A single specific reward.', pack_safe=False, **kwargs):
        (super().__init__)(money=TunableRewardMoney.TunableFactory(), 
         object_definition=TunableRewardObject.TunableFactory(), 
         trait=TunableRewardTrait.TunableFactory(), 
         cas_part=TunableRewardCASPart.TunableFactory(), 
         build_buy_object=TunableBuildBuyObjectDefinitionUnlock.TunableFactory(get_definition=(pack_safe,)), 
         build_buy_magazine_collection=TunableBuildBuyMagazineCollectionUnlock.TunableFactory(), 
         display_text=TunableRewardDisplayText.TunableFactory(), 
         additional_employee_slot=TunableRewardAdditionalEmployeeSlot.TunableFactory(), 
         additional_business_customer_count=TunableRewardAdditionalCustomerCount.TunableFactory(), 
         additional_business_markup=TunableRewardAdditionalMarkup.TunableFactory(), 
         set_club_gathering_vibe=TunableSetClubGatheringVibe.TunableFactory(), 
         bucks=TunableRewardBucks.TunableFactory(), 
         buff=TunableRewardBuff.TunableFactory(), 
         whim_bucks=TunableRewardWhimBucks.TunableFactory(), 
         description=description, **kwargs)


class TunableRandomReward(TunableTuple):

    def __init__(self, description='A list of specific rewards and a weight.', **kwargs):
        super().__init__(reward=(TunableSpecificReward()),
          weight=Tunable(tunable_type=float, default=1),
          description=description)