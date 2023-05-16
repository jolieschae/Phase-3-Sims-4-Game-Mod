# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\object_fashion_marketplace_component.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 32490 bytes
import alarms, random, services
from date_and_time import TimeSpan
from event_testing.resolver import SingleObjectResolver, SingleActorAndObjectResolver
from objects import ALL_HIDDEN_REASONS
from objects.components.state import ObjectStateValue
from objects.components.tooltip_component import CustomTooltipTuningProvidingMixin
from objects.components.types import OBJECT_FASHION_MARKETPLACE_COMPONENT
from protocolbuffers import SimObjectAttributes_pb2, Consts_pb2
from objects.components import Component, types, componentmethod_with_fallback
import sims4
from sims.sim_info_types import Gender
from sims.sim_spawner import SimSpawner
from sims.sim_spawner_enums import SimNameType
from sims4.common import Pack
from sims4.localization import TunableLocalizedStringFactory, LocalizationHelperTuning
from sims4.tuning.tunable import AutoFactoryInit, HasTunableFactory, TunableTuple, TunableList, TunableReference, HasTunableSingletonFactory, TunableEnumEntry, Tunable, OptionalTunable, TunableThreshold
from sims4.utils import classproperty
from tag import TunableTags
from tunable_multiplier import TunableMultiplier
from tunable_time import TunableTimeSpan
logger = sims4.log.Logger('Object Fashion Marketplace Component', default_owner='anchavez')

class _TunableObjectFashionMarketplaceState(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'state_value':ObjectStateValue.TunablePackSafeReference(description='\n            The ObjectStateValue to put an object in when it enters this\n            fashion marketplace state.\n            '), 
     'enter_loot':TunableList(description='\n            Loot actions to apply to an object and the sim selling it when \n            this object enters this fashion marketplace state.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       pack_safe=True)), 
     'tags':TunableTags(description='\n            Tags that will be applied to an object when it enters this\n            fashion marketplace state.\n            '), 
     'inventory_icon_visual_state':OptionalTunable(description='\n            If tuned, a string for the UI to determine what treatment should be\n            done on this object when it is in the inventory. If un-tuned, no\n            treatment will be done.\n            ',
       tunable=Tunable(tunable_type=str,
       default='INVALID'))}

    def enter_state(self, fashion_marketplace_component):
        owner = fashion_marketplace_component.owner
        if self.tags:
            owner.append_tags((self.tags), persist=True)
        owner.set_state(self.state_value.state, self.state_value)
        if self.enter_loot:
            seller_sim_info = services.sim_info_manager().get(fashion_marketplace_component._seller_sim_id)
            resolver = SingleActorAndObjectResolver(seller_sim_info, owner, self)
            for loot_action in self.enter_loot:
                loot_action.apply_to_resolver(resolver)

        owner_inventory = owner.get_inventory()
        if owner_inventory is not None:
            owner_inventory.push_inventory_item_update_msg(owner)

    def leave_state(self, fashion_marketplace_component):
        if self.tags:
            fashion_marketplace_component.owner.remove_dynamic_tags(self.tags)


class TunableObjectFashionMarketplaceCustomTooltip(CustomTooltipTuningProvidingMixin, HasTunableSingletonFactory, AutoFactoryInit):
    pass


class ObjectFashionMarketplaceComponent(Component, HasTunableFactory, component_name=types.OBJECT_FASHION_MARKETPLACE_COMPONENT, allow_dynamic=True, persistence_key=SimObjectAttributes_pb2.PersistenceMaster.PersistableData.ObjectFashionMarketplaceComponent):
    OBJECT_FASHION_MARKETPLACE_BASE_VALUES = TunableTuple(description='\n        The following fields represent the base values for properties of \n        objects listed on the fashion marketplace. To tune specific values for a \n        specific object, tune an ObjectFashionMarketplaceComponent on that object.\n        ',
      base_list_cost_multiplier=TunableMultiplier.TunableFactory(description='\n            This is used to calculate the cost of listing an object on the fashion\n            marketplace. This value will be multiplied by the catalog value of\n            the object.\n            '),
      base_sale_price_multiplier=TunableMultiplier.TunableFactory(description="\n            This is used to calculate the sale price for selling object on the\n            fashion marketplace. This value will be multiplied by the object's value\n            as calculated by gameplay (affected by things like quality) to form\n            a bonus. We will then randomly select a value between .5 times and \n            1 times that bonus and add it to the original value.\n            "),
      base_sale_chance=TunableMultiplier.TunableFactory(description='\n            Base chance an object will sell.\n            '))
    OBJECT_FASHION_MARKETPLACE_STATE_TUNING = TunableTuple(description='\n        Tuning relating to how objects behave as they are modified by the \n        object fashion marketplace.\n        ',
      listed_tuning=_TunableObjectFashionMarketplaceState.TunableFactory(description='\n            The tuning governing an object that is listed in the fashion marketplace.\n            '),
      pending_sale_tuning=_TunableObjectFashionMarketplaceState.TunableFactory(description='\n            The tuning governing an object that is marked as pending sale in \n            the fashion marketplace.\n            '),
      sold_tuning=_TunableObjectFashionMarketplaceState.TunableFactory(description='\n            The tuning governing an object that is sold in the fashion marketplace.\n            ',
      locked_args={'inventory_icon_visual_state': None}),
      expired_tuning=_TunableObjectFashionMarketplaceState.TunableFactory(description='\n            The tuning governing an object that expires in the fashion marketplace.\n            ',
      locked_args={'inventory_icon_visual_state': None}),
      delisted_tuning=_TunableObjectFashionMarketplaceState.TunableFactory(description="\n            The tuning governing an object that has become delisted from\n            the fashion marketplace. This tuning functions slightly differently from\n            other fashion marketplace 'states' in that it is intended to set the object\n            back to defaults that existed prior to the fashion marketplace\n            ",
      locked_args={'inventory_icon_visual_state': None}),
      delivered_tuning=_TunableObjectFashionMarketplaceState.TunableFactory(description="\n            The tuning governing an object that has become delivered to a \n            buyer. This tuning functions slightly differently from other fashion\n            marketplace 'states' in that it is intended to set the object back\n            to defaults that existed prior to the fashion marketplace\n            ",
      locked_args={'inventory_icon_visual_state': None}))
    OBJECT_FASHION_MARKETPLACE_PRICING_STATE_TUNING = TunableList(TunableTuple(description='\n        List to define the marketplace pricing state based on tunable thresholds to be\n        used when selling an outfit on the Trendi marketplace to determine whether the \n        player is selling extremely underpriced, underpriced, even, overpriced, extremely overprice\n        ',
      state=TunableReference(description='\n            A state value to set on the object.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
      class_restrictions=('ObjectStateValue', ),
      pack_safe=True),
      thresholds=TunableList(description='\n            A list of tunable thresholds, all of which must pass for \n            this entry to be chosen as the marketplace price state.\n            ',
      tunable=TunableThreshold(description='\n                A threshold that must be met.\n                ',
      default=(sims4.math.Threshold(0.0, sims4.math.Operator.LESS_OR_EQUAL.function))),
      minlength=1)))
    LISTING_DURATION = TunableTimeSpan(description='\n        This is the duration of a listing on the fashion marketplace. After this time\n        has elapsed, the listing will expire.\n        ',
      default_days=7)
    DELIVERY_DURATION = TunableTimeSpan(description='\n        This is the amount of time between an object being sold and it being\n        delivered.\n        ',
      default_hours=1)
    BUYER_NAME_TYPE = TunableEnumEntry(description='\n        The SimNameType to use for generating buyer names.\n        ',
      tunable_type=SimNameType,
      default=(SimNameType.DEFAULT))
    NO_BUYER_TEXT = TunableLocalizedStringFactory(description='\n        The text that will be used in place of a buyer name if this item does\n        not have a buyer.\n        ')
    CUSTOM_TOOLTIP_TUNING = TunableObjectFashionMarketplaceCustomTooltip.TunableFactory(description='\n        Any object that is listed or pending sale on the object marktplace will\n        have this custom tooltip tuning prepending to its normal tooltip\n        tuning.\n        ')
    FACTORY_TUNABLES = {'list_cost_multiplier':TunableMultiplier.TunableFactory(description="\n            This value is multiplied by base_list_cost_multiplier and the \n            object catalog value to determine the cost of listing it on the \n            fashion marketplace. base_list_cost_multiplier can be found in this\n            component's module tuning.\n            "), 
     'sale_price_multiplier':TunableMultiplier.TunableFactory(description='\n            This value is added to base_sale_price_multiplier (in module \n            tuning) when determine the sale price bonus of selling via the\n            fashion marketplaces.\n            '), 
     'sale_chance_multplier':TunableMultiplier.TunableFactory(description="\n            This value is multiplied by base_sale_chance to determine the chance\n             this item will succesfully find a buyer on the fashion marketplace.\n             base_sale_chance can be found in this component's module tuning.\n            ")}

    @classproperty
    def required_packs(cls):
        return (Pack.EP12,)

    def __init__(self, *args, list_cost_multiplier=None, sale_price_multiplier=None, sale_chance_multplier=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._list_cost_multiplier = list_cost_multiplier
        self._sale_price_multiplier = sale_price_multiplier
        self._sale_chance_multplier = sale_chance_multplier
        self._sale_price = None
        self._buyer_screen_name = None
        self._seller_sim_id = None
        self._expiration_alarm = None
        self._sale_alarm = None
        self._delivery_alarm = None

    @classmethod
    def get_listing_cost(cls, seller_sim_info, obj):
        resolver = SingleActorAndObjectResolver(seller_sim_info, obj, 'Object Fashion Marketplace Valuation')
        cost = cls.OBJECT_FASHION_MARKETPLACE_BASE_VALUES.base_list_cost_multiplier.get_multiplier(resolver)
        if obj.has_component(OBJECT_FASHION_MARKETPLACE_COMPONENT):
            fashion_marketplace_component = obj.get_component(OBJECT_FASHION_MARKETPLACE_COMPONENT)
            if fashion_marketplace_component._list_cost_multiplier is not None:
                cost *= fashion_marketplace_component._list_cost_multiplier.get_multiplier(resolver)
        return cost

    @classmethod
    def calculate_sale_price(cls, obj):
        sale_price = obj.base_value
        resolver = SingleObjectResolver(obj)
        sale_price_bonus = sale_price * cls.OBJECT_FASHION_MARKETPLACE_BASE_VALUES.base_sale_price_multiplier.get_multiplier(resolver)
        fashion_marketplace_component = obj.get_component(OBJECT_FASHION_MARKETPLACE_COMPONENT)
        if fashion_marketplace_component is not None:
            if fashion_marketplace_component._sale_price_multiplier is not None:
                sale_price_bonus += sale_price * fashion_marketplace_component._sale_price_multiplier.get_multiplier(resolver)
        return sale_price + int(sale_price_bonus * random.uniform(0.5, 1))

    def set_sale_price_override(self, sale_price):
        self._sale_price = sale_price

    def _set_sale_price(self):
        if self._sale_price is None:
            self._sale_price = self.calculate_sale_price(self.owner)

    def _calculate_market_price_difference(self):
        sale_price = self._sale_price
        target = self.owner
        market_price_diff_percent = 0
        if target is not None:
            suggested_market_sale_price = self.get_suggested_marketplace_sale_price(target=target)
            if suggested_market_sale_price != 0:
                market_price_diff_percent = float((sale_price - suggested_market_sale_price) / suggested_market_sale_price) * 100
        return market_price_diff_percent

    def _set_market_price_difference_state(self):
        target_outfit = self.owner
        if target_outfit is not None:
            market_price_diff = self._calculate_market_price_difference()
            if self.OBJECT_FASHION_MARKETPLACE_PRICING_STATE_TUNING is not None:
                for pricing_state_tuning in self.OBJECT_FASHION_MARKETPLACE_PRICING_STATE_TUNING:
                    if all((threshold.compare(market_price_diff) for threshold in pricing_state_tuning.thresholds)):
                        if target_outfit.has_state(pricing_state_tuning.state.state):
                            target_outfit.set_state((pricing_state_tuning.state.state), (pricing_state_tuning.state),
                              immediate=True,
                              force_update=True)
                        break

    def set_buyer_name(self):
        self._buyer_screen_name = SimSpawner.get_random_first_name((Gender.MALE), sim_name_type_override=(self.BUYER_NAME_TYPE))

    @componentmethod_with_fallback((lambda: None))
    def list(self, seller_sim_info):
        self._seller_sim_id = seller_sim_info.sim_id
        resolver = SingleActorAndObjectResolver(seller_sim_info, self.owner, self)
        sale_chance = self.OBJECT_FASHION_MARKETPLACE_BASE_VALUES.base_sale_chance.get_multiplier(resolver)
        if self._sale_chance_multplier is not None:
            sale_chance *= self._sale_chance_multplier.get_multiplier(resolver)
        if random.random() < sale_chance:
            timespan_till_sale = self.LISTING_DURATION() * random.random()
            self._sale_alarm = alarms.add_alarm(self, timespan_till_sale, self._set_pending_sale)
            self.set_buyer_name()
        self._expiration_alarm = alarms.add_alarm(self, self.LISTING_DURATION(), self._set_expired)
        self._set_sale_price()
        self._set_market_price_difference_state()
        self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.listed_tuning.enter_state(self)

    def _set_expired(self, *args):
        self._expiration_alarm = None
        if self.is_listed():
            self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.listed_tuning.leave_state(self)
        else:
            self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.pending_sale_tuning.leave_state(self)
        self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.expired_tuning.enter_state(self)

    def _set_pending_sale(self, *args):
        self._sale_alarm = None
        self._expiration_alarm = None
        self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.listed_tuning.leave_state(self)
        self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.pending_sale_tuning.enter_state(self)

    def _set_delivered(self, *args):
        self._delivery_alarm = None
        self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.sold_tuning.leave_state(self)
        self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.delivered_tuning.enter_state(self)
        self.owner.make_transient()

    @componentmethod_with_fallback((lambda: None))
    def delist(self):
        self._sale_alarm = None
        self._expiration_alarm = None
        if self.is_listed():
            self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.listed_tuning.leave_state(self)
        else:
            self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.pending_sale_tuning.leave_state(self)
        self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.delisted_tuning.enter_state(self)

    @componentmethod_with_fallback((lambda: None))
    def sell(self):
        owner = self.owner
        self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.pending_sale_tuning.leave_state(self)
        self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.sold_tuning.enter_state(self)
        seller_sim_info = services.sim_info_manager().get(self._seller_sim_id)
        seller_sim_info.household.funds.add(self._sale_price, Consts_pb2.TELEMETRY_MONEY_OBJECT_FASHION_MARKETPLACE_SALE, seller_sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS))
        self._delivery_alarm = alarms.add_alarm(self, self.DELIVERY_DURATION(), self._set_delivered)
        inventory = owner.get_inventory()
        if inventory is not None:
            inventory.try_move_object_to_hidden_inventory(owner)
        fashion_trend_service = services.fashion_trend_service()
        if fashion_trend_service is not None:
            fashion_trend_service.add_fashion_outfit_to_sold_list(source_object=owner)

    @componentmethod_with_fallback((lambda: None))
    def get_inventory_visual_state(self):
        if self.is_listed():
            return self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.listed_tuning.inventory_icon_visual_state
        if self.is_pending_sale():
            return self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.pending_sale_tuning.inventory_icon_visual_state

    def is_listed(self):
        return self.owner.state_value_active(self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.listed_tuning.state_value)

    def is_pending_sale(self):
        return self.owner.state_value_active(self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.pending_sale_tuning.state_value)

    def is_unlisted(self):
        return self.owner.state_value_active(self.OBJECT_FASHION_MARKETPLACE_STATE_TUNING.delisted_tuning.state_value)

    def get_sale_price(self):
        if self._sale_price is not None:
            return self._sale_price
        return 0

    def get_suggested_sale_price(self, target):
        return self.get_suggested_marketplace_sale_price(target)

    @classmethod
    def get_prevalent_trend_for_listing(cls, target):
        prevalent_trend = None
        fashion_trend_service = services.fashion_trend_service()
        if fashion_trend_service is not None:
            prevalent_trend = fashion_trend_service.get_outfit_prevalent_trend_name(target)
        return prevalent_trend

    @classmethod
    def get_suggested_marketplace_sale_price(cls, target):
        suggested_sale_price = 0
        fashion_trend_service = services.fashion_trend_service()
        if fashion_trend_service is not None:
            suggested_sale_price = fashion_trend_service.get_outfit_suggested_sale_price(target)
        return suggested_sale_price

    def get_buyer_screen_name(self):
        if self._buyer_screen_name is not None:
            return LocalizationHelperTuning.get_raw_text(self._buyer_screen_name)
        return self.NO_BUYER_TEXT()

    def get_custom_tooltips(self):
        if not self.is_unlisted():
            return self.CUSTOM_TOOLTIP_TUNING.custom_tooltips
        return []

    def get_expiration_time(self):
        if self._expiration_alarm is not None:
            return services.time_service().sim_now + self._expiration_alarm.get_remaining_time()

    def save(self, persistence_master_message):
        persistable_data = SimObjectAttributes_pb2.PersistenceMaster.PersistableData()
        persistable_data.type = SimObjectAttributes_pb2.PersistenceMaster.PersistableData.ObjectFashionMarketplaceComponent
        object_fashion_marketplace_component_data = persistable_data.Extensions[SimObjectAttributes_pb2.PersistableObjectFashionMarketplaceComponent.persistable_data]
        if self._sale_price is not None:
            object_fashion_marketplace_component_data.sale_price = self._sale_price
        if self._seller_sim_id is not None:
            object_fashion_marketplace_component_data.seller_sim_id = self._seller_sim_id
        if self._buyer_screen_name is not None:
            object_fashion_marketplace_component_data.buyer_name = self._buyer_screen_name
        if self._expiration_alarm is not None:
            object_fashion_marketplace_component_data.expiration_timer_time = self._expiration_alarm.finishing_time.absolute_ticks()
        if self._sale_alarm is not None:
            object_fashion_marketplace_component_data.sale_timer_time = self._sale_alarm.finishing_time.absolute_ticks()
        if self._delivery_alarm is not None:
            object_fashion_marketplace_component_data.delivery_timer_time = self._delivery_alarm.finishing_time.absolute_ticks()
        persistence_master_message.data.extend([persistable_data])

    def load(self, persistable_data):
        object_fashion_marketplace_component_data = persistable_data.Extensions[SimObjectAttributes_pb2.PersistableObjectFashionMarketplaceComponent.persistable_data]
        self._sale_price = object_fashion_marketplace_component_data.sale_price
        self._seller_sim_id = object_fashion_marketplace_component_data.seller_sim_id
        self._buyer_screen_name = object_fashion_marketplace_component_data.buyer_name
        expiration_time = object_fashion_marketplace_component_data.expiration_timer_time
        sale_time = object_fashion_marketplace_component_data.sale_timer_time
        delivery_time = object_fashion_marketplace_component_data.delivery_timer_time
        now = services.time_service().sim_now
        if sale_time != 0:
            time_till_sale = sale_time - now
            if time_till_sale > 0:
                self._sale_alarm = alarms.add_alarm(self, TimeSpan(time_till_sale), self._set_pending_sale)
                self._expiration_alarm = alarms.add_alarm(self, TimeSpan(expiration_time - now), self._set_expired)
            else:
                self._set_pending_sale()
        else:
            if expiration_time != 0:
                time_till_expire = expiration_time - now
                if time_till_expire > 0:
                    self._expiration_alarm = alarms.add_alarm(self, TimeSpan(time_till_expire), self._set_expired)
                else:
                    self._set_expired()
            else:
                if delivery_time != 0:
                    inventory = self.owner.get_inventory()
                    if inventory is not None:
                        inventory.try_move_object_to_hidden_inventory(self.owner)
                    else:
                        time_till_delivery = delivery_time - now
                        if time_till_delivery > 0:
                            self._delivery_alarm = alarms.add_alarm(self, TimeSpan(time_till_delivery), self._set_delivered)
                        else:
                            self._set_delivered()