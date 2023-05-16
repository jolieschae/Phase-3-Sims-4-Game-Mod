# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\civic_policies\street_civic_policy_provider.py
# Compiled at: 2021-05-28 12:49:20
# Size of source mod 2**32: 16911 bytes
from collections import defaultdict
from civic_policies.base_civic_policy_provider import BaseCivicPolicyProvider
from conditional_layers.conditional_layer_enums import ConditionalLayerRequestSpeedType
from distributor.ops import CivicPolicyPanelUpdate
from distributor.rollback import ProtocolBufferRollback
from distributor.system import Distributor
from eco_footprint.eco_footprint_state_provider_mixin import EcoFootprintStateProviderMixin
from event_testing.resolver import SingleSimResolver, StreetResolver
from event_testing.tests import TunableTestSet
from sims4.resources import Types
from sims4.tuning.tunable import TunableList, TunableReference, TunableSet
from sims4.tuning.tunable_base import ExportModes
from sims4.utils import classproperty
import world, services, sims4.log
logger = sims4.log.Logger('StreetProvider', default_owner='jjacobson')

class StreetProvider(BaseCivicPolicyProvider, EcoFootprintStateProviderMixin):
    FACTORY_TUNABLES = {'initial_vote_test_for_street':TunableTestSet(description='\n            If the NPC Voting user option is enabled, these tests are run before the Initial \n            Random Vote Tests to see if initial voting will be performed when voting opens. \n            While the Initial Vote Test is done for each Resident Sim, this test is run for \n            the Street specifically.\n            ',
       export_modes=ExportModes.ServerXML), 
     'daily_random_vote_test_for_street':TunableTestSet(description='\n            If the NPC Voting user option is enabled, these tests are run before the Daily Random \n            Vote Tests to see if daily random voting will be performed at midnight.  While the \n            Daily Random Vote Tests is done for each Resident Sim, this test is run for the Street \n            specifically.\n            ',
       export_modes=ExportModes.ServerXML), 
     'default_layers':TunableList(description='\n            A list of default layers that should be loaded on this street.\n            Street policies may turn these off.\n            ',
       tunable=TunableReference(description='\n                The default conditional layer.\n                ',
       manager=(services.get_instance_manager(Types.CONDITIONAL_LAYER))),
       unique_entries=True)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._requires_initial_layer_setup = True
        self._conditional_layers_loaded = []
        self._default_layers_turned_off = defaultdict(list)

    def get_resident_sim_infos(self):
        street_service = services.street_service()
        zone_ids = world.street.get_zone_ids_from_street(street_service.get_street(self))
        if zone_ids is None:
            return []
        persistence_service = services.get_persistence_service()
        sim_info_manager = services.sim_info_manager()
        sim_infos = []
        for zone_id in zone_ids:
            zone_data = persistence_service.get_zone_proto_buff(zone_id)
            if zone_data is None or zone_data.household_id == 0:
                continue
            household_proto = persistence_service.get_household_proto_buff(zone_data.household_id)
            if household_proto is None:
                continue
            if household_proto.sims.ids:
                for sim_id in household_proto.sims.ids:
                    sim_info = sim_info_manager.get(sim_id)
                    if sim_info is not None:
                        sim_infos.append(sim_info)

        return sim_infos

    def finalize_startup(self):
        super().finalize_startup()
        EcoFootprintStateProviderMixin.finalize_startup(self)
        if not self._requires_initial_layer_setup:
            return
        current_street = services.current_street()
        street = services.street_service().get_street(self)
        if street is not current_street:
            return
        self._requires_initial_layer_setup = False
        conditional_layer_service = services.conditional_layer_service()
        for layer in self.default_layers:
            if layer in self._default_layers_turned_off:
                continue
            conditional_layer_service.load_conditional_layer(layer, fade_in=False)

    @property
    def requires_initial_layer_setup(self):
        return self._requires_initial_layer_setup

    @property
    def max_enacted_policy_count(self):
        return 4

    @property
    def max_balloted_policy_count(self):
        return 8

    @property
    def initial_balloted_policy_count(self):
        return 7

    @property
    def max_repealable_policy_count(self):
        return 1

    @property
    def open_close_voting_loot_resolver_list(self):
        resolvers = list()
        residents = self.get_resident_sim_infos()
        for resident in residents:
            resolvers.append(SingleSimResolver(resident))

        return resolvers

    @classproperty
    def provider_type_id(cls):
        return 2

    def get_world_description_id(self):
        street_service = services.street_service()
        if street_service is not None:
            world_description_id = world.street.get_world_description_id_from_street(street_service.get_street(self))
            if world_description_id is None:
                return 0
            return world_description_id
        return 0

    def run_auto_voting_tests(self, test_set):
        street_service = services.street_service()
        if not street_service.enable_automatic_voting:
            return False
        else:
            if test_set is self.initial_vote_test:
                street_test_set = self.initial_vote_test_for_street
            else:
                if test_set is self.daily_random_vote_test:
                    street_test_set = self.daily_random_vote_test_for_street
                else:
                    street_test_set = None
            if street_test_set:
                if not street_test_set.run_tests(StreetResolver(street_service.get_street(self))):
                    return False
            return test_set or True
        resolvers = list(self.open_close_voting_loot_resolver_list)
        for resolver in resolvers:
            if test_set.run_tests(resolver):
                return True

        return False

    def save(self, parent_data_msg):
        super().save(parent_data_msg)
        parent_data_msg.requires_initial_layer_setup = self._requires_initial_layer_setup
        parent_data_msg.ClearField('loaded_conditional_layers')
        for layer in self._conditional_layers_loaded:
            parent_data_msg.loaded_conditional_layers.append(layer.guid64)

        parent_data_msg.ClearField('turned_off_default_conditional_layers')
        for layer, policies in self._default_layers_turned_off.items():
            with ProtocolBufferRollback(parent_data_msg.turned_off_default_conditional_layers) as (default_layer_msg):
                default_layer_msg.layer = layer.guid64
                for policy in policies:
                    default_layer_msg.policies.append(policy.guid64)

    def save_street_eco_footprint_data(self, parent_data_msg):
        super()._save_street_eco_footprint_data(parent_data_msg)

    def load(self, parent_data_msg):
        super().load(parent_data_msg)
        self._requires_initial_layer_setup = parent_data_msg.requires_initial_layer_setup
        layer_manager = services.get_instance_manager(sims4.resources.Types.CONDITIONAL_LAYER)
        for layer_guid in parent_data_msg.loaded_conditional_layers:
            layer = layer_manager.get(layer_guid)
            if layer is None:
                continue
            self._conditional_layers_loaded.append(layer)

        snippet_manager = services.get_instance_manager(sims4.resources.Types.SNIPPET)
        for default_layer_data in parent_data_msg.turned_off_default_conditional_layers:
            layer = layer_manager.get(default_layer_data.layer)
            if layer is None:
                continue
            for policy_guid in default_layer_data.policies:
                policy = snippet_manager.get(policy_guid)
                if policy is None:
                    continue
                self._default_layers_turned_off[layer].append(policy)

    def load_street_eco_footprint_data(self, parent_data_msg):
        super()._load_street_eco_footprint_data(parent_data_msg)

    def is_eligible_voter(self, sim_info):
        household = sim_info.household
        if household is None:
            return False
        street = services.street_service().get_street(self)
        return street is world.street.get_street_instance_from_world_id(household.get_home_world_id())

    def is_new_policy_allowed(self, sim_info):
        if len(self._balloted_policies) >= self.max_balloted_policy_count:
            return False
        else:
            if len(self._enacted_policies) >= self.max_enacted_policy_count:
                return False
            return self.get_dormant_policies() or False
        return self.is_eligible_voter(sim_info)

    def populate_community_board_op(self, sim_info, op, target_id):
        if self.new_enact_max_count() == 0:
            op.disabled_tooltip = self.COMMUNITY_BOARD_TEXT.no_room_confirm_tooltip_text()
            op.policy_disabled_tooltip = self.COMMUNITY_BOARD_TEXT.no_room_policy_tooltip_text()
        super().populate_community_board_op(sim_info, op, target_id)

    def add_for_repeal(self, policy):
        super().add_for_repeal(policy)
        if self.is_eligible_voter(services.active_sim_info()):
            self.send_update_message()

    def remove_from_repeal(self, policy):
        super().remove_from_repeal(policy)
        if self.is_eligible_voter(services.active_sim_info()):
            self.send_update_message()

    def vote_by_instance(self, policy_instance, count=1, user_directed=False, lobby_interaction=False):
        result = super().vote_by_instance(policy_instance, count=count, user_directed=user_directed, lobby_interaction=lobby_interaction)
        if policy_instance in self._up_for_repeal_policies:
            if self.is_eligible_voter(services.active_sim_info()):
                self.send_update_message()
        return result

    def send_update_message(self):
        repeal_policy_id = 0
        repeal_sigs = 0
        for policy in self._up_for_repeal_policies:
            if policy.vote_count_statistic is None:
                repeal_sigs = 0
            else:
                repeal_sigs = int(self.get_stat_value(policy.vote_count_statistic))
            repeal_policy_id = policy.guid64

        op = CivicPolicyPanelUpdate(services.street_service().voting_open, repeal_policy_id, repeal_sigs, self.get_schedule_text())
        Distributor.instance().add_op_with_no_owner(op)

    def show_conditional_layer(self, layer):
        if layer in self._conditional_layers_loaded:
            return
        services.conditional_layer_service().load_conditional_layer(layer)
        self._conditional_layers_loaded.append(layer)

    def hide_conditional_layer(self, layer):
        if layer not in self._conditional_layers_loaded:
            return
        elif services.current_zone().is_zone_running:
            speed = ConditionalLayerRequestSpeedType.GRADUALLY
        else:
            speed = ConditionalLayerRequestSpeedType.IMMEDIATELY
        services.conditional_layer_service().destroy_conditional_layer(layer, speed=speed)
        self._conditional_layers_loaded.remove(layer)

    def show_default_conditional_layer(self, layer, policy):
        if layer not in self._default_layers_turned_off:
            return
        if policy not in self._default_layers_turned_off[layer]:
            logger.error('Attempting to show default layer {} from policy {} being removed that did not previously turn off such layer.', layer, policy)
            return
        self._default_layers_turned_off[layer].remove(policy)
        if self._default_layers_turned_off[layer]:
            return
        del self._default_layers_turned_off[layer]
        services.conditional_layer_service().load_conditional_layer(layer)

    def hide_default_conditional_layer(self, layer, policy):
        if layer not in self._default_layers_turned_off:
            if services.current_zone().is_zone_running:
                speed = ConditionalLayerRequestSpeedType.GRADUALLY
            else:
                speed = ConditionalLayerRequestSpeedType.IMMEDIATELY
            services.conditional_layer_service().destroy_conditional_layer(layer, speed=speed)
        if policy in self._default_layers_turned_off[layer]:
            return
        self._default_layers_turned_off[layer].append(policy)

    def mark_legacy_layer_loaded(self, layer):
        if layer in self._conditional_layers_loaded:
            return
        self._conditional_layers_loaded.append(layer)

    def mark_legacy_default_layer_hidden(self, layer, policy):
        if policy in self._default_layers_turned_off[layer]:
            return
        self._default_layers_turned_off[layer].append(policy)