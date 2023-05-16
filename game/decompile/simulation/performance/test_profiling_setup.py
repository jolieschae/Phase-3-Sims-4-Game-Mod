# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\performance\test_profiling_setup.py
# Compiled at: 2020-11-20 16:46:28
# Size of source mod 2**32: 2833 bytes
import profile_utils, services, caches
from sims.sim_info_tests import TraitTest
from weather.weather_enums import WeatherType
from weather.weather_tests import WeatherTypeTest

class TestProfilingSetup:
    tests_to_run = {}

    @staticmethod
    @profile_utils.profile_function(output_filename='tests_data')
    def start_tests(number_of_runs, clear_ratio):
        TestProfilingSetup._init_tests()
        profile_utils.add_string('number of runs : {}, clear ratio : {}'.format(number_of_runs, clear_ratio))
        for test in TestProfilingSetup.tests_to_run:
            args = TestProfilingSetup.tests_to_run[test]
            profile_utils.sub_time_start()
            for iteration in range(number_of_runs):
                if iteration > 0:
                    if iteration % clear_ratio == 0:
                        caches.skip_cache_once = True
                (test.default)(**args)

            profile_utils.sub_time_end('test {}'.format(test))

    @staticmethod
    def _init_tests():
        TestProfilingSetup.tests_to_run.clear()
        TestProfilingSetup._init_weather_type_test()
        TestProfilingSetup._init_trait_test()

    @staticmethod
    def _init_weather_type_test():
        weather_type_test = WeatherTypeTest.TunableFactory(locked_args={'weather_types': frozenset({WeatherType.AnyRain})})
        TestProfilingSetup.tests_to_run[weather_type_test] = {}

    @staticmethod
    def _init_trait_test():
        active_sim_info = services.active_sim_info()
        if active_sim_info:
            traits = active_sim_info.trait_tracker.equipped_traits
            trait_test = TraitTest.TunableFactory(locked_args={'whitelist_traits': frozenset(traits)})
            TestProfilingSetup.tests_to_run[trait_test] = {'test_targets': (active_sim_info,)}