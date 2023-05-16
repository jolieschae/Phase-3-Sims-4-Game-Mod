# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\stereo_component.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 7457 bytes
from event_testing.resolver import SingleObjectResolver
from event_testing.tests import TunableTestSet
from objects.components import Component, types
from objects.components.state_references import TunableStateTypeReference, TunableStateValueReference
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableList, TunableReference, Tunable, TunableTuple, TunableSet
import services, sims4.resources
from snippets import define_snippet

class StereoComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=types.STEREO_COMPONENT):
    FACTORY_TUNABLES = {'channel_state':TunableStateTypeReference(description='\n            The state used to populate the radio stations'), 
     'off_state':TunableStateValueReference(description='\n            The channel that represents the off state.'), 
     'listen_affordances':TunableList(description='\n            An ordered list of affordances that define "listening" to this\n            stereo. The first succeeding affordance is used.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       pack_safe=True)), 
     'play_on_active_sim_only':Tunable(description='\n            If enabled, and audio target is Sim, the audio will only be \n            played on selected Sim. Otherwise it will be played regardless \n            Sim is selected or not.\n            \n            If audio target is Object, always set this to False. Otherwise\n            the audio will never be played.\n            \n            ex. This will be useful for Earbuds where we want to hear the\n            music only when the Sim is selected.\n            \n            This is passed down to the audio state when it is triggered, and thus\n            will overwrite any tuning on the state value.\n            ',
       tunable_type=bool,
       default=False), 
     'immediate':Tunable(description='\n            If checked, this audio will be triggered immediately, nothing\n            will block.\n            \n            ex. Earbuds audio will be played immediately while \n            the Sim is routing or animating.\n            \n            This is passed down to the audio state when it is triggered, and thus\n            will overwrite any tuning on the state value.\n            ',
       tunable_type=bool,
       default=False), 
     'whitelist_channels':TunableList(description='\n            This acts like a filter. Items in this list who pass their test \n            will be combined together and become a whitelist. We will check \n            against this whitelist to generate available picker channel states.\n            If this list is empty, the filter will be disabled.\n            ',
       tunable=TunableTuple(channel_states=TunableSet(description='\n                    If the test passes, channel states in this list will be in \n                    the whitelist and become available.\n                    ',
       tunable=TunableStateValueReference(pack_safe=True)),
       test=TunableTestSet(description='\n                    Tests for whitelist channel states. Note that we also have \n                    tests on listen affordances, please make sure they are not \n                    duplicated so to save performance.\n                    '))), 
     'unavailable_channels':TunableList(description='\n            Items in this list that past tests will not be available, even if \n            the whitelist is empty. \n            ',
       tunable=TunableTuple(channel_states=TunableSet(description='\n                    If the test passes, channel states in this list will be not \n                    be available. \n                    ',
       tunable=TunableStateValueReference(pack_safe=True)),
       test=TunableTestSet(description='\n                    Tests for unavailable channel states. Note that we also have \n                    tests on listen affordances, please make sure they are not \n                    duplicated so to save performance.\n                    ')))}

    def is_stereo_turned_on(self):
        current_channel = self.owner.get_state(self.channel_state)
        return current_channel != self.off_state

    def get_available_picker_channel_states(self, context):
        whitelist_channels = self._get_filtered_channels(self.whitelist_channels)
        unavailable_channels = self._get_filtered_channels(self.unavailable_channels)
        for client_state in self.owner.get_client_states(self.channel_state):
            if whitelist_channels is not None:
                if client_state not in whitelist_channels or unavailable_channels is not None:
                    if client_state in unavailable_channels:
                        continue
                if client_state.show_in_picker and client_state.test_channel(self.owner, context):
                    yield client_state

    def component_potential_interactions_gen(self, context, **kwargs):
        current_channel = self.owner.get_state(self.channel_state)
        if current_channel != self.off_state:
            for listen_affordance in self.listen_affordances:
                yield from (listen_affordance.potential_interactions)(self.owner, context, required_station=current_channel, 
                 off_state=self.off_state, **kwargs)

        if False:
            yield None

    def _get_filtered_channels(self, filter_list):
        if not filter_list:
            return
        resolver = SingleObjectResolver(self.owner)
        tested_channels_sets = []
        for channels_to_test in filter_list:
            if channels_to_test.test.run_tests(resolver):
                tested_channels_sets.append(channels_to_test.channel_states)

        if tested_channels_sets:
            return (frozenset.union)(*tested_channels_sets)
        return frozenset()


_, TunableStereoComponentSnippet = define_snippet('stereo_component', StereoComponent.TunableFactory())