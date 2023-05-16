# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\object_fashion_marketplace_loot.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 3038 bytes
from interactions.utils.loot_basic_op import BaseLootOperation, BaseTargetedLootOperation
import sims4.log
from objects.components.types import OBJECT_FASHION_MARKETPLACE_COMPONENT
from sims4.tuning.tunable import TunableVariant, AutoFactoryInit, HasTunableSingletonFactory
logger = sims4.log.Logger('ObjectFashionMarketplaceLootOp', default_owner='anchavez')

class ListOnMarketplace(HasTunableSingletonFactory, AutoFactoryInit):

    def __call__(self, seller, obj):
        if not obj.has_component(OBJECT_FASHION_MARKETPLACE_COMPONENT):
            obj.add_dynamic_component(OBJECT_FASHION_MARKETPLACE_COMPONENT, list_cost_multiplier=None, sale_price_multiplier=None, sale_chance_multplier=None)
        obj.list(seller)


class DelistOnMarketplace(HasTunableSingletonFactory, AutoFactoryInit):

    def __call__(self, seller, obj):
        if not obj.has_component(OBJECT_FASHION_MARKETPLACE_COMPONENT):
            return
        fashion_marketplace_component = obj.get_component(OBJECT_FASHION_MARKETPLACE_COMPONENT)
        if not fashion_marketplace_component.is_listed():
            if not fashion_marketplace_component.is_pending_sale():
                return
        obj.delist()


class SellOnMarketplace(HasTunableSingletonFactory, AutoFactoryInit):

    def __call__(self, owner, obj):
        if not obj.has_component(OBJECT_FASHION_MARKETPLACE_COMPONENT):
            logger.error('Attempting to sell an object {} that is not listed on fashion marketplace', obj)
            return
        obj.sell()


class ObjectFashionMarketplaceLootOp(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'marketplace_operation': TunableVariant(description='\n            The marketplace operation to perform.\n            ',
                                list=(ListOnMarketplace.TunableFactory()),
                                delist=(DelistOnMarketplace.TunableFactory()),
                                sell=(SellOnMarketplace.TunableFactory()),
                                default='list')}

    def __init__(self, marketplace_operation, **kwargs):
        (super().__init__)(**kwargs)
        self.marketplace_operation = marketplace_operation

    def _apply_to_subject_and_target(self, subject, target, resolver):
        self.marketplace_operation(subject, target)
        return True