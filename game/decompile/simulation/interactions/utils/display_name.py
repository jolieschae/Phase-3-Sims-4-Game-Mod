# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\display_name.py
# Compiled at: 2021-06-07 16:34:04
# Size of source mod 2**32: 14051 bytes
from event_testing.results import TestResult
from interactions.utils.tunable_icon import TunableIconVariant
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import HasTunableSingletonFactory, TunableList, TunableTuple, TunableVariant, AutoFactoryInit, TunableSimMinute, OptionalTunable, TunableReference, Tunable
from singletons import DEFAULT
import event_testing.tests, services, sims4.log, sims4.resources
logger = sims4.log.Logger('DisplayName')

class TestableDisplayName(HasTunableSingletonFactory, AutoFactoryInit):

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, value):
        for index, override_data in enumerate(value.overrides):
            if override_data.new_display_name is not None:
                override_data.new_display_name or logger.error('name override not set for display name override in {} at index:{}', instance_class, index)

    FACTORY_TUNABLES = {'overrides':TunableList(description='\n            Potential name overrides for this interaction. The first test in\n            this list which passes will be the new display name show to the\n            player. If none pass the tuned display_name will be used.\n            ',
       tunable=TunableTuple(description='\n                A tuple of a test and the name that would be chosen if the test\n                passes.\n                ',
       test=event_testing.tests.TunableTestSet(description='\n                    The test to run to see if the display_name should be\n                    overridden.\n                    '),
       new_display_name=OptionalTunable(description='\n                    If enabled, we will override the display name. Sometimes\n                    you might not want to do this, such as with crafting\n                    interactions that show the recipe name.\n                    ',
       tunable=TunableLocalizedStringFactory(description='\n                        The localized name of this interaction. it takes two tokens,\n                        the actor (0) and target object (1) of the interaction.\n                        '),
       enabled_by_default=True),
       new_pie_menu_icon=OptionalTunable(description='\n                    If this display name overrides the default display name,\n                    this will be the icon that is shown. If this is not tuned\n                    then the default pie menu icon for this interaction will be\n                    used.\n                    ',
       tunable=TunableIconVariant(description='\n                        The icon to display in the pie menu.\n                        ',
       icon_pack_safe=True)),
       new_display_tooltip=OptionalTunable(description='\n                    Tooltip to show on this pie menu option.\n                    ',
       tunable=(TunableLocalizedStringFactory())),
       new_pie_menu_category=TunableReference(description='\n                    Pie menu category to put interaction under.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.PIE_MENU_CATEGORY)),
       allow_none=True),
       parent_name=OptionalTunable(description='\n                    If enabled, we will insert the name into this parent string\n                    in the pie menu.\n                    ',
       tunable=TunableLocalizedStringFactory(description='\n                        The localized parent name of this interaction.\n                        token 0 is actor, token 1 is normal pie name\n                        ')))), 
     'verify_tunable_callback':_verify_tunable_callback}

    def get_display_names_gen(self):
        for override in self.overrides:
            if override.new_display_name is not None:
                yield override.new_display_name

    def get_display_name_and_result(self, interaction, target=DEFAULT, context=DEFAULT, **interaction_parameters):
        resolver = (interaction.get_resolver)(target=target, context=context, **interaction_parameters)
        for override in self.overrides:
            result = override.test.run_tests(resolver)
            if result:
                return (
                 override, result)

        return (
         None, TestResult.NONE)


class RandomDisplayName(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'overrides':TunableList(description='\n            A list of random strings and icons to select randomly using their weights.\n            Will only select options whose tests pass.\n            ',
       tunable=TunableTuple(new_display_name=OptionalTunable(description='\n                    If enabled, we will override the display name. Sometimes\n                    you might not want to do this, such as with crafting\n                    interactions that show the recipe name.\n                    ',
       tunable=TunableLocalizedStringFactory(description='\n                        The localized name of this interaction. it takes two tokens,\n                        the actor (0) and target object (1) of the interaction.\n                        '),
       enabled_by_default=True),
       new_pie_menu_icon=OptionalTunable(description='\n                    If this display name overrides the default display name,\n                    this will be the icon that is shown. If this is not tuned\n                    then the default pie menu icon for this interaction will be\n                    used.\n                    ',
       tunable=TunableIconVariant(description='\n                        The icon to display in the pie menu.\n                        ',
       icon_pack_safe=True)),
       new_display_tooltip=OptionalTunable(description='\n                    Tooltip to show on this pie menu option.\n                    ',
       tunable=(TunableLocalizedStringFactory())),
       parent_name=OptionalTunable(description='\n                    If enabled, we will insert the name into this parent string\n                    in the pie menu.\n                    ',
       tunable=TunableLocalizedStringFactory(description='\n                        The localized parent name of this interaction.\n                        token 0 is actor, token 1 is normal pie name\n                        ')),
       test=event_testing.tests.TunableTestSet(description='\n                    The test to run to see if the display_name can be overwritten\n                    by this random choice.\n                    '),
       weight=Tunable(description='\n                    The weight to apply to this option when randomly selecting.\n                    ',
       default=1,
       tunable_type=float),
       new_pie_menu_category=TunableReference(description='\n                    Pie menu category to put interaction under.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.PIE_MENU_CATEGORY)),
       allow_none=True))), 
     'timeout':TunableSimMinute(description='\n            The time it will take for a new string to be generated given the\n            same set of data.\n            ',
       minimum=0,
       default=10)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._key_map = {}

    def get_display_names_gen(self):
        for override in self.overrides:
            if override.new_display_name is not None:
                yield override.new_display_name

    def get_display_name_and_result(self, interaction, target=DEFAULT, context=DEFAULT, **interaction_parameters):
        context = interaction.context if context is DEFAULT else context
        target = interaction.target if target is DEFAULT else target
        resolver = (interaction.get_resolver)(target=target, context=context, **interaction_parameters)
        key = (
         context.sim.id, 0 if target is None else target.id, interaction.affordance)
        random_names = getattr(context, 'random_names', dict())
        result = random_names.get(key)
        if result is not None:
            test_result = result.test.run_tests(resolver)
            if test_result:
                return (
                 result, test_result)
        else:
            now = services.time_service().sim_now
            result, time_stamp = self._key_map.get(key, (None, None))
            if result is not None:
                test_result = result.test.run_tests(resolver)
                if test_result:
                    time_delta = now - time_stamp
                    if self.timeout > time_delta.in_minutes():
                        self._key_map[key] = (result, now)
                        return (result, TestResult.NONE)
            valid_choices = []
            for potential_override in self.overrides:
                test_result = potential_override.test.run_tests(resolver)
                if test_result:
                    valid_choices.append((potential_override.weight, (potential_override, test_result)))

            return valid_choices or (
             None, TestResult.NONE)
        result, test_result = sims4.random.weighted_random_item(valid_choices)
        random_names[key] = result
        setattr(context, 'random_names', random_names)
        self._key_map[key] = (result, now)
        return (
         result, test_result)


class TunableDisplayNameVariant(TunableVariant):

    def __init__(self, **kwargs):
        (super().__init__)(testable=TestableDisplayName.TunableFactory(), 
         random=RandomDisplayName.TunableFactory(), **kwargs)


class TunableDisplayNameWrapper(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'wrappers': TunableList(description='\n            Each wrapper is a localized string matched with a test set. The \n            wrapper that tests in first is applied to the display name.\n            \n            NOTE: The wrapper is override independent, and if enabled will be \n            applied to all display name variants. Anything that depends on override\n            context should not be tuned here, but instead be tuned manually under\n            Display Name Overrides.\n            \n            NOTE: The format of the wrapper will take in the original string\n            and should be written in this form: "[0.String] Wrapper" .\n            ',
                   tunable=TunableTuple(description='\n                A tuple of test sets and the wrapper.\n                ',
                   test=event_testing.tests.TunableTestSet(description='\n                    The tests that control the condition of when the wrapper is\n                    displayed.\n                    '),
                   wrapper=TunableLocalizedStringFactory(description='\n                    The localized wrapper.\n                    ')))}

    def get_first_passing_wrapper(self, interaction, target=DEFAULT, context=DEFAULT, **interaction_parameters):
        resolver = (interaction.get_resolver)(target=target, context=context, **interaction_parameters)
        for wrapper in self.wrappers:
            result = wrapper.test.run_tests(resolver)
            if result:
                return wrapper