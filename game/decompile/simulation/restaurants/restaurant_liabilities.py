# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\restaurants\restaurant_liabilities.py
# Compiled at: 2018-08-27 21:57:31
# Size of source mod 2**32: 5099 bytes
from gsi_handlers import business_handlers
from interactions import ParticipantTypeSingle, ParticipantTypeObject
from interactions.liability import Liability
from restaurants import restaurant_utils
from restaurants.restaurant_tuning import get_restaurant_zone_director
from sims4.tuning.tunable import AutoFactoryInit, HasTunableFactory, TunableEnumEntry, TunableReference
import services, sims4.resources

class RestaurantDeliverFoodLiability(Liability, HasTunableFactory, AutoFactoryInit):
    LIABILITY_TOKEN = 'RestaurantDeliverFoodLiability'
    FACTORY_TUNABLES = {'table_participant':TunableEnumEntry(description='\n            The participant of this interaction that is going to have\n            the specified affordance pushed upon them.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Object), 
     'platter_participant':TunableEnumEntry(description='\n            The participant of this interaction that is going to have\n            the specified affordance pushed upon them.\n            ',
       tunable_type=ParticipantTypeObject,
       default=ParticipantTypeObject.CarriedObject), 
     'drop_plate_interaction':TunableReference(description="\n            The interaction for dropping the plate. IF the liability is\n            transfered to this interaction then we don't want to cancel the\n            order when the interaction finishes because it is going to be\n            given back to the chef to prepare again. YOU REALLY SHOULDN'T EVER\n           NEED TO RETUNE THIS. I'LL CHECK IT IN WITH THE CORRET TUNING.\n           ",
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION))}

    def __init__(self, interaction, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._interaction = interaction
        self._should_cancel = True

    def on_add(self, interaction):
        self._interaction = interaction

    def on_reset(self):
        current_zone = services.current_zone()
        if current_zone is None or current_zone.is_zone_shutting_down:
            return
        platter_obj = self._interaction.get_participant(self.platter_participant)
        if platter_obj is not None:
            platter_obj.make_transient()
        zone_director = get_restaurant_zone_director()
        if zone_director is None:
            return
        group_order = self.get_group_order(zone_director=zone_director)
        if group_order is None:
            return
        zone_director.create_food_for_group_order(group_order)

    def transfer(self, interaction):
        if interaction.affordance == self.drop_plate_interaction:
            self._should_cancel = False
        else:
            self._should_cancel = True

    def on_run(self):
        self._should_cancel = False

    def release(self):
        platter_obj = self._interaction.get_participant(self.platter_participant)
        if platter_obj is not None:
            if not platter_obj.transient:
                platter_obj.make_transient()
        elif not self._should_cancel:
            return
        else:
            zone_director = get_restaurant_zone_director()
            if zone_director is None:
                return
            group_order = self.get_group_order(zone_director)
            if group_order is not None:
                if group_order.is_order_ready and not self._interaction.is_finishing_naturally:
                    if business_handlers.business_archiver.enabled:
                        business_handlers.archive_business_event('RestaurantLiabilities', None, 'Group Ordered canceled from interaction:{}'.format(self._interaction))
                    zone_director.cancel_group_order(group_order, refund_cost=True)

    def get_group_order(self, zone_director):
        table_object = self._interaction.get_participant(self.table_participant)
        if table_object is None:
            return
        return zone_director.get_active_group_order_for_table(table_object.id)