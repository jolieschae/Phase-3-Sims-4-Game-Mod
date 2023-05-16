# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\spawner_component.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 57657 bytes
from random import randint
import operator, random, weakref
from objects.components.spawner_component_enums import SpawnerType, SpawnLocation
from protocolbuffers import SimObjectAttributes_pb2 as protocols
from autonomy.autonomy_modifier import AutonomyModifier
from event_testing.resolver import GlobalResolver
from event_testing.tests import TunableTestSet
from objects.components import Component, types, componentmethod, componentmethod_with_fallback
from objects.components.state_references import TunableStateValueReference
from objects.components.types import SPAWNER_COMPONENT, PORTAL_COMPONENT
from objects.object_enums import ItemLocation
from routing.portals.portal_component import PortalComponent
from scheduler import WeeklySchedule
from server_commands.argument_helpers import RequiredTargetParam
from sims4.random import weighted_random_item
from sims4.tuning.geometric import TunableVector3
from sims4.tuning.instances import TunedInstanceMetaclass
from sims4.tuning.tunable import TunableVariant, TunableReference, HasTunableReference, HasTunableSingletonFactory, TunableList, AutoFactoryInit, HasTunableFactory, TunableRange, TunableTuple, TunableMapping, OptionalTunable, Tunable, TunablePercent, TunableEnumEntry, TunableInterval
from sims4.utils import flexmethod
from tunable_utils.create_object import ObjectCreator, RecipeCreator
from tunable_utils.placement_tuning import TunableOrientationRestriction, TunablePlacementScoringFunction
import alarms, date_and_time, enum, objects.components.types, placement, services, sims4, sims4.log
logger = sims4.log.Logger('SpawnerComponent', default_owner='camilogarcia')

class GlobalObjectSpawnerTuning:
    SPAWN_ON_GROUND_FGL_HEIGHT_TOLERANCE = Tunable(description='\n        Maximum height tolerance on the terrain we will use for the placement \n        of the spawned object.\n        If the spawned objects have interactions on them, this value will\n        generate a height difference between the object and the sim.  Because\n        of this if this value changes all animations on spawned objects should\n        be verified.  Include a GPE and an Animator when making changes to \n        this value. \n        ',
      tunable_type=float,
      default=0.1)


class SpawnerTuning(HasTunableReference, HasTunableSingletonFactory, AutoFactoryInit, metaclass=TunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.RECIPE)):
    INSTANCE_TUNABLES = {'object_reference':TunableList(description='\n            List of objects the spawner can create.  When the random check \n            picks this value from the weight calculation it will give all\n            the items tuned on this list.\n            ',
       tunable=TunableVariant(description='\n                Specify the means by which will the spawner will create the object.\n                ',
       object_definition=ObjectCreator.TunableFactory(get_definition=(True, )),
       recipe=(RecipeCreator.TunableFactory()),
       default='object_definition')), 
     'spawn_weight':TunableRange(description='\n            Weight that object will have on the probability calculation \n            of which object to spawn.\n            ',
       tunable_type=int,
       default=1,
       minimum=0), 
     'spawn_chance':TunablePercent(description='\n             The chance that the spawned object will actually be created.\n             This is in case we want spawned objects to not be created in a \n             predictable behavior and the change of "nothing happening" be \n             available.\n             ',
       default=100), 
     'spawner_option':TunableVariant(description='\n            Type of spawners to create:\n            Ground type - Spawned object will appear on the floor at a tunable \n            radius from the spawner object.\n            Slot type - Spawned object will appear on an available slot of \n            a tunable slot type in the spawner object.\n            Interaction type - Spawned objects will appear on the inventory\n            when player makes a gather-harvest-scavenge interaction on them. \n            ',
       ground_spawning=TunableTuple(radius=TunableRange(description='\n                    Max radius at which the spawned object should appear\n                    ',
       tunable_type=int,
       default=1,
       minimum=0),
       min_radius=TunableRange(description='\n                    Minimum distance away from the portal location to\n                    start looking for a good location.\n                    ',
       tunable_type=int,
       default=0,
       minimum=0),
       restrictions=TunableList(description='\n                    List of orientation restrictions used by FGL \n                    when searching for a place to put the object.\n                    \n                    Will only apply to off-lot spawners.\n                    ',
       tunable=(TunableOrientationRestriction())),
       placement_scoring=TunableList(description='\n                    List of scoring functions used by FGL to determine\n                    best places to put the object.\n\n                    Will only apply to off-lot spawners.\n                    ',
       tunable=(TunablePlacementScoringFunction())),
       force_states=TunableList(description='\n                    List of states the created object will be pushed to.\n                    ',
       tunable=TunableStateValueReference(pack_safe=True)),
       force_initialization_spawn=OptionalTunable(description='\n                    If checked, objects with this component will force a \n                    spawning of objects on initialization.  This is mainly used\n                    for objects on the open street where we want to fake that \n                    some time has already passed.  \n                    Additionally, if checked, objects will force the states\n                    on this list instead of the force_states list on the \n                    general spawner tuning, this way we can add some custom\n                    states only for the initialization spawn.\n                    ',
       tunable=TunableList(description='\n                        List of states the created object will have when\n                        initialized.\n                        ',
       tunable=(TunableStateValueReference()))),
       location_test=TunableTuple(is_outside=OptionalTunable(description='\n                        If checked, will verify if the spawned object is \n                        located outside. \n                        If unchecked will test the object is not outside\n                        ',
       disabled_name="Don't_Test",
       tunable=(Tunable(bool, True))),
       is_natural_ground=OptionalTunable(description='\n                        If checked, will verify the spawned object is on \n                        natural ground.\n                        If unchecked will test the object is not on natural \n                        ground\n                        ',
       disabled_name="Don't_Test",
       tunable=(Tunable(bool, True)))),
       starting_location=TunableVariant(description='\n                    The location at which we want to start attempting to place\n                    the object we are creating.\n                    ',
       spawner_location=TunableTuple(description='\n                        If selected the object will be spawned near the\n                        location of the spawner object.\n                        ',
       consider_source_object_footprint=Tunable(description="\n                            If True, then the source object's footprints will\n                            be considered in the creation of FGL context.\n                            \n                            Example: If the source is invisible, then setting\n                            this to False would allow the spawned object to be\n                            located at its spawner's location. If the source\n                            is a visible object, then setting this to True would\n                            force the spawned object to be offset by any existing\n                            footprints on the source.\n                            ",
       tunable_type=bool,
       default=False),
       locked_args={'location_type': SpawnLocation.SPAWNER}),
       portal_location=TunableTuple(description='\n                        If selected the object will be spanwed near the\n                        location of the specified portal type and start or end\n                        location\n                        ',
       portal_type=TunableReference(description='\n                            A reference to the type of portal to use for the\n                            starting location.\n                            ',
       manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
       class_restrictions=('PortalData', )),
       portal_direction=TunableVariant(description='\n                            Choose between the There and Back of the portal.\n                            This will not work properly if the portal is\n                            missing a Back and Back is specified here.\n                            ',
       locked_args={'there':PortalComponent.PORTAL_DIRECTION_THERE, 
      'back':PortalComponent.PORTAL_DIRECTION_BACK},
       default='there'),
       portal_location=TunableVariant(description='\n                            Choose between the entry and exit location of the\n                            portal.\n                            ',
       locked_args={'entry':PortalComponent.PORTAL_LOCATION_ENTRY, 
      'exit':PortalComponent.PORTAL_LOCATION_EXIT},
       default='entry'),
       locked_args={'location_type': SpawnLocation.PORTAL}),
       default='spawner_location'),
       initial_location_offset=TunableTuple(default_offset=TunableVector3(description="\n                        The default Vector3 offset from the location target's\n                        position.\n                        ",
       default=(sims4.math.Vector3.ZERO())),
       x_randomization_range=OptionalTunable(tunable=TunableInterval(description='\n                            A random number in this range will be applied to the\n                            default offset along the x axis.\n                            ',
       tunable_type=float,
       default_lower=0,
       default_upper=0)),
       z_randomization_range=OptionalTunable(tunable=TunableInterval(description='\n                            A random number in this range will be applied to the\n                            default offset along the z axis.\n                            ',
       tunable_type=float,
       default_lower=0,
       default_upper=0))),
       locked_args={'spawn_type': SpawnerType.GROUND}),
       slot_spawning=TunableTuple(slot_type=TunableReference(description='\n                    Slot type where spawned objects should appear\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SLOT_TYPE))),
       force_initialization_spawn=OptionalTunable(description='\n                    If enabled, objects with this component will force a \n                    spawning of objects on initialization.  This is mainly used\n                    for objects on the open street where we want to fake that \n                    some time has already passed.\n                    ',
       tunable=TunableRange(description='\n                        The number of objects to be created.\n                        ',
       tunable_type=int,
       minimum=1,
       default=1)),
       state_mapping=TunableMapping(description='\n                    Mapping of states from the spawner object into the possible\n                    states that the spawned object may have\n                    ',
       key_type=(TunableStateValueReference()),
       value_type=TunableList(description='\n                        List of possible children for a parent state\n                        ',
       tunable=TunableTuple(description='\n                            Pair of weight and possible state that the spawned \n                            object may have\n                            ',
       weight=TunableRange(description='\n                                Weight that object will have on the probability calculation \n                                of which object to spawn.\n                                ',
       tunable_type=int,
       default=1,
       minimum=0),
       child_state=(TunableStateValueReference())))),
       locked_args={'spawn_type': SpawnerType.SLOT}),
       interaction_spawning=TunableTuple(locked_args={'spawn_type': SpawnerType.INTERACTION})), 
     'spawn_times':OptionalTunable(description='\n            Schedule of when the spawners should trigger.\n            If this time is tuned spawners will trigger according to this \n            schedule instead of the spawner commodities.   \n            This should be used for spawners that are on the open neighborhood \n            so that those spawners are time based instead of commodity based.\n            ',
       tunable=WeeklySchedule.TunableFactory(),
       disabled_name='No_custom_spawn_times',
       enabled_name='Set_custom_spawn_times'), 
     'tests':TunableTestSet(description='\n            Conditional tests to determine if spawning occurs.\n            ')}
    FACTORY_TUNABLES = INSTANCE_TUNABLES

    @flexmethod
    def create_spawned_object(cls, inst, spawner_object, definition, loc_type=ItemLocation.ON_LOT):
        try:
            obj = definition(loc_type=loc_type)
        except KeyError:
            logger.exception('Failed to spawn object {} for {}', definition, spawner_object)
            obj = None

        if obj is not None:
            spawner_object.spawner_component.spawned_object_created(obj)
        return obj


with sims4.reload.protected(globals()):
    SpawnerInitializerSingleton = None

class SpawnerActionEnum(enum.Int):
    SPAWNER_DISABLE = 0
    SPAWNER_ENABLE = 1


class SpawnerComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=types.SPAWNER_COMPONENT, persistence_key=protocols.PersistenceMaster.PersistableData.SpawnerComponent):
    GROUND_SPAWNER_DECAY_COMMODITY = TunableReference(description='\n        Commodity which will trigger the ground spawner of an object on decay.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)))
    SLOT_SPAWNER_DECAY_COMMODITY = TunableReference(description='\n        Commodity which will trigger the slot spawner of an object on decay.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)))
    SPAWNER_COMMODITY_RESET_VARIANCE = TunableRange(description='\n        Max variance to apply when the spawn commodity is being reset to its\n        threshold value.  This is meant to add some randomness on how spawners\n        will create objects.\n        \n        e.g.  After a spawner creates an objects its spawn statistic will go\n        back to 100-RandomValue from 0 to Variance this way it wont always start\n        at the same time\n        ',
      tunable_type=int,
      default=0,
      minimum=0)

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, **kwargs):
        for spawner_data in kwargs['spawner_data']:
            if spawner_data.spawner_option.spawn_type == SpawnerType.GROUND and spawner_data.spawner_option.min_radius > spawner_data.spawner_option.radius:
                logger.error("The tuning for a spawner component ({}) has a min_distance value that is greater than the max_distance value. This doesn't make sense, please fix this tuning.", instance_class)

    class _SpawnFiremeterGlobal(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'value': Tunable(description='\n                The maximum number of objects that this spawner can have created\n                at one point.\n                ',
                    tunable_type=int,
                    default=1)}

        def __call__(self, obj):
            return self.value

    class _SpawnFiremeterStateBased(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'state_values': TunableMapping(description='\n                A mapping of state value to cap. If the object has the specified\n                state set, the associated value is used as a cap. The order is\n                evaluated arbitrarily, so avoid tuning states that are not\n                mutually exclusive.\n                \n                If the object has no state set, no firemeter cap applies.\n                ',
                           key_type=TunableStateValueReference(pack_safe=True),
                           value_type=Tunable(tunable_type=int,
                           default=1))}

        def __call__(self, obj):
            for state_value, value in self.state_values.items():
                if obj.state_value_active(state_value):
                    return value

    FACTORY_TUNABLES = {'spawner_data':TunableList(description='\n            Data corresponding at what objects will the spawner create and \n            their type which will define how they will be created\n            ',
       tunable=TunableVariant(description='\n                Option to tune the spawner data through a factory which will\n                be tuned per object, or through a reference which may be reused \n                by multiple objects \n                ',
       spawnerdata_factory=(SpawnerTuning.TunableFactory()),
       spawnerdata_reference=(SpawnerTuning.TunableReference()),
       default='spawnerdata_reference')), 
     'spawn_firemeter':OptionalTunable(description='\n            If set, spawner will be limited to spawn this number of objects\n            at the same time.  \n            ',
       tunable=TunableVariant(global_firemeter=(_SpawnFiremeterGlobal.TunableFactory()),
       state_based_firemeter=(_SpawnFiremeterStateBased.TunableFactory()),
       default='global_firemeter')), 
     'reset_spawner_count':OptionalTunable(description='\n            If enabled then we only reset the commodity a specific number of\n            times.\n            ',
       tunable=TunableTuple(description='\n                Data associated with reset_spawner_count. \n                ',
       max_count=TunableRange(description='\n                    If checked we will reset the spawner commodity when we spawn an\n                    object using it.\n                    ',
       tunable_type=int,
       default=1,
       minimum=1),
       respawn_destroyed_objects=Tunable(description='\n                    If this is checked then we will keep an up to date count\n                    on number of objects spawned, and if enough are destroyed\n                    to get back below the max_count we will start spawning them\n                    again.    \n                    ',
       tunable_type=bool,
       default=False))), 
     'spawned_object_count_triggers':TunableMapping(description='\n            A list of paired triggers and spawner actions. At each trigger,\n            the paired action is completed on the spawner. The trigger occurs \n            at a total spawned object threshold.\n            ',
       key_type=Tunable(description='\n                Total spawned object threshold.\n                ',
       tunable_type=int,
       default=1),
       value_type=TunableVariant(description='\n                Spawner Action, disable or enable. Disabling prevents objects\n                from spawning and removes all timers. Enabling the spawner resets\n                the object count and creates alarms.\n                ',
       tunable_enum=TunableEnumEntry(description='\n                    The game state of the Spawner Object that triggers the spawner action.\n                    ',
       tunable_type=SpawnerActionEnum,
       default=(SpawnerActionEnum.SPAWNER_DISABLE)))), 
     'spawn_time_span_override':OptionalTunable(description='\n            A start and end delay that override the zone information and \n            determine a time span within which a random time is selected for \n            the spawned object to be created.\n            ',
       tunable=TunableTuple(spawn_delayed_start_override=TunableRange(description='\n                    This is the minimum amount of sim minutes we wait before we\n                    start spawning objects.\n                    ',
       tunable_type=int,
       default=15,
       minimum=0),
       spawn_delayed_end_override=TunableRange(description='\n                    This is the maximum amount of sim minutes we wait before we\n                    start spawning objects for the first time.\n                    ',
       tunable_type=int,
       default=60,
       minimum=0))), 
     'verify_tunable_callback':_verify_tunable_callback}

    def __init__(self, owner, *args, **kwargs):
        (super().__init__)(owner, *args, **kwargs)
        self._disabled = False
        self._spawner_stats = {}
        self._spawned_objects = weakref.WeakSet()
        self._spawned_object_ids = []
        self._spawner_data = []
        self._spawner_initialized = False
        self._spawner_data_spawn_index = -1
        self._spawn_object_alarm = None
        self._scheduler = None
        self._times_commodity_reset = 0

    def on_add(self):
        for spawner_data_item in self.spawner_data:
            self.add_spawner_data(spawner_data_item)

    @componentmethod
    def interaction_spawner_data(self):
        return [(data.spawn_weight,
         (
          [object_ref.get_object_definition() for object_ref in data.object_reference], ())) for data in self._spawner_data if data.spawner_option.spawn_type == SpawnerType.INTERACTION]

    @componentmethod
    def slot_spawner_definitions(self):
        return [[object_ref.get_object_definition() for object_ref in data.object_reference] for data in self._spawner_data if data.spawner_option.spawn_type == SpawnerType.SLOT]

    def _disable_spawner(self):
        if self._disabled:
            return
        self._disabled = True
        self._destroy_spawner_alarm()
        self._destroy_time_based_spawners()

    def _enable_spawner(self):
        if not self._disabled:
            return
        self._disabled = False
        if self._spawner_data:
            self._spawner_data_spawn_index = 0
            self._create_spawner_alarm()

    def _process_spawner_action(self, action):
        if action == SpawnerActionEnum.SPAWNER_DISABLE:
            self._disable_spawner()
        if action == SpawnerActionEnum.SPAWNER_ENABLE:
            self._enable_spawner()

    def spawned_object_created(self, obj):
        self._spawned_objects.add(obj)
        if self.spawned_object_count_triggers:
            if self.spawned_object_count_triggers[len(self._spawned_objects)] is not None:
                self._process_spawner_action(self.spawned_object_count_triggers[len(self._spawned_objects)])

    def _get_non_interaction_spawner_data(self):
        return [(data.spawn_weight, data) for data in self._spawner_data if data.spawner_option.spawn_type != SpawnerType.INTERACTION]

    def spawn_object_from_commodity(self, stat):
        if self._disabled:
            return
        if self.reset_spawner_count is None:
            self.reset_spawn_commodity(stat)
        else:
            if self.reset_spawner_count.respawn_destroyed_objects:
                self._times_commodity_reset = 0
                for obj in self._spawned_objects:
                    if obj is not None:
                        self._times_commodity_reset += 1

            elif self._times_commodity_reset < self.reset_spawner_count.max_count:
                self._times_commodity_reset += 1
                self.reset_spawn_commodity(stat)
            else:
                if not self.reset_spawner_count.respawn_destroyed_objects:
                    statistic_modifier = AutonomyModifier(locked_stats=(stat.stat_type,))
                    self.owner.add_statistic_modifier(statistic_modifier)
                else:
                    self.reset_spawn_commodity(stat)
                return
        self._spawn_object()

    def trigger_time_spawner(self, scheduler, alarm_data, trigger_cooldown):
        self._spawn_object()

    @componentmethod_with_fallback((lambda *_, **__: None))
    def force_spawn_object(self, spawn_type=None, ignore_firemeter=False, create_slot_obj_count=1):
        self._spawn_object(spawn_type=spawn_type, ignore_firemeter=ignore_firemeter, create_slot_obj_count=create_slot_obj_count)

    def _spawn_object--- This code section failed: ---

 L. 716         0  LOAD_FAST                'ignore_firemeter'
                2  POP_JUMP_IF_TRUE     26  'to 26'
                4  LOAD_FAST                'self'
                6  LOAD_ATTR                spawn_firemeter
                8  LOAD_CONST               None
               10  COMPARE_OP               is-not
               12  POP_JUMP_IF_FALSE    26  'to 26'
               14  LOAD_FAST                'self'
               16  LOAD_METHOD              spawn_firemeter
               18  LOAD_FAST                'self'
               20  LOAD_ATTR                owner
               22  CALL_METHOD_1         1  '1 positional argument'
               24  JUMP_FORWARD         28  'to 28'
             26_0  COME_FROM            12  '12'
             26_1  COME_FROM             2  '2'
               26  LOAD_CONST               None
             28_0  COME_FROM            24  '24'
               28  STORE_FAST               'spawn_firemeter_value'

 L. 717        30  LOAD_FAST                'spawn_firemeter_value'
               32  LOAD_CONST               None
               34  COMPARE_OP               is-not
               36  POP_JUMP_IF_FALSE    56  'to 56'

 L. 718        38  LOAD_GLOBAL              len
               40  LOAD_FAST                'self'
               42  LOAD_ATTR                _spawned_objects
               44  CALL_FUNCTION_1       1  '1 positional argument'
               46  LOAD_FAST                'spawn_firemeter_value'
               48  COMPARE_OP               >=
               50  POP_JUMP_IF_FALSE    56  'to 56'

 L. 720        52  LOAD_CONST               None
               54  RETURN_VALUE     
             56_0  COME_FROM            50  '50'
             56_1  COME_FROM            36  '36'

 L. 722        56  LOAD_DEREF               'spawn_type'
               58  LOAD_CONST               None
               60  COMPARE_OP               is-not
               62  POP_JUMP_IF_FALSE    90  'to 90'

 L. 723        64  LOAD_CLOSURE             'spawn_type'
               66  BUILD_TUPLE_1         1 
               68  LOAD_LISTCOMP            '<code_object <listcomp>>'
               70  LOAD_STR                 'SpawnerComponent._spawn_object.<locals>.<listcomp>'
               72  MAKE_FUNCTION_8          'closure'
               74  LOAD_FAST                'self'
               76  LOAD_ATTR                _spawner_data
               78  GET_ITER         
               80  CALL_FUNCTION_1       1  '1 positional argument'
               82  STORE_FAST               'weight_pairs'

 L. 724        84  LOAD_CONST               True
               86  STORE_FAST               'force_initialization_spawn'
               88  JUMP_FORWARD        102  'to 102'
             90_0  COME_FROM            62  '62'

 L. 726        90  LOAD_FAST                'self'
               92  LOAD_METHOD              _get_non_interaction_spawner_data
               94  CALL_METHOD_0         0  '0 positional arguments'
               96  STORE_FAST               'weight_pairs'

 L. 727        98  LOAD_CONST               False
              100  STORE_FAST               'force_initialization_spawn'
            102_0  COME_FROM            88  '88'

 L. 728       102  LOAD_GLOBAL              weighted_random_item
              104  LOAD_FAST                'weight_pairs'
              106  CALL_FUNCTION_1       1  '1 positional argument'
              108  STORE_FAST               'spawn_result'

 L. 730       110  LOAD_FAST                'spawn_result'
              112  LOAD_CONST               None
              114  COMPARE_OP               is
              116  POP_JUMP_IF_FALSE   138  'to 138'

 L. 731       118  LOAD_GLOBAL              logger
              120  LOAD_METHOD              error
              122  LOAD_STR                 "Spawner {} didn't found an object to spawn for spawntype {}.  This can be caused by an empty set ofspawn tunables or an infinite recursion force_spawnwhile trying to have a spawner spawn spawners"

 L. 734       124  LOAD_FAST                'self'
              126  LOAD_ATTR                owner
              128  LOAD_DEREF               'spawn_type'
              130  CALL_METHOD_3         3  '3 positional arguments'
              132  POP_TOP          

 L. 736       134  LOAD_CONST               None
              136  RETURN_VALUE     
            138_0  COME_FROM           116  '116'

 L. 738       138  LOAD_GLOBAL              random
              140  LOAD_METHOD              random
              142  CALL_METHOD_0         0  '0 positional arguments'
              144  LOAD_FAST                'spawn_result'
              146  LOAD_ATTR                spawn_chance
              148  COMPARE_OP               >
              150  POP_JUMP_IF_FALSE   156  'to 156'

 L. 739       152  LOAD_CONST               None
              154  RETURN_VALUE     
            156_0  COME_FROM           150  '150'

 L. 741       156  LOAD_FAST                'spawn_result'
              158  LOAD_ATTR                tests
              160  LOAD_METHOD              run_tests
              162  LOAD_GLOBAL              GlobalResolver
              164  CALL_FUNCTION_0       0  '0 positional arguments'
              166  CALL_METHOD_1         1  '1 positional argument'
              168  POP_JUMP_IF_TRUE    174  'to 174'

 L. 742       170  LOAD_CONST               None
              172  RETURN_VALUE     
            174_0  COME_FROM           168  '168'

 L. 744       174  LOAD_FAST                'spawn_result'
          176_178  POP_JUMP_IF_FALSE   318  'to 318'

 L. 745       180  LOAD_FAST                'spawn_result'
              182  LOAD_ATTR                spawner_option
              184  LOAD_ATTR                spawn_type
              186  STORE_DEREF              'spawn_type'

 L. 746       188  LOAD_DEREF               'spawn_type'
              190  LOAD_GLOBAL              SpawnerType
              192  LOAD_ATTR                GROUND
              194  COMPARE_OP               ==
              196  POP_JUMP_IF_FALSE   230  'to 230'

 L. 747       198  LOAD_FAST                'spawn_result'
              200  LOAD_ATTR                spawner_option
              202  LOAD_ATTR                radius
              204  STORE_FAST               'radius'

 L. 748       206  LOAD_FAST                'spawn_result'
              208  LOAD_ATTR                spawner_option
              210  LOAD_ATTR                min_radius
              212  STORE_FAST               'min_radius'

 L. 749       214  LOAD_FAST                'self'
              216  LOAD_METHOD              _create_object_on_ground
              218  LOAD_FAST                'spawn_result'
              220  LOAD_FAST                'radius'
              222  LOAD_FAST                'min_radius'
              224  LOAD_FAST                'force_initialization_spawn'
              226  CALL_METHOD_4         4  '4 positional arguments'
              228  POP_TOP          
            230_0  COME_FROM           196  '196'

 L. 750       230  LOAD_DEREF               'spawn_type'
              232  LOAD_GLOBAL              SpawnerType
              234  LOAD_ATTR                SLOT
              236  COMPARE_OP               ==
          238_240  POP_JUMP_IF_FALSE   318  'to 318'

 L. 751       242  LOAD_FAST                'spawn_result'
              244  LOAD_ATTR                spawner_option
              246  LOAD_ATTR                slot_type
              248  BUILD_SET_1           1 
              250  STORE_FAST               'slot_types'

 L. 754       252  LOAD_FAST                'force_initialization_spawn'
          254_256  POP_JUMP_IF_FALSE   282  'to 282'
              258  LOAD_FAST                'spawn_result'
              260  LOAD_ATTR                spawner_option
              262  LOAD_ATTR                force_initialization_spawn
              264  LOAD_CONST               None
              266  COMPARE_OP               is-not
          268_270  POP_JUMP_IF_FALSE   282  'to 282'

 L. 755       272  LOAD_FAST                'spawn_result'
              274  LOAD_ATTR                spawner_option
              276  LOAD_ATTR                force_initialization_spawn
              278  STORE_FAST               'create_object_count'
              280  JUMP_FORWARD        286  'to 286'
            282_0  COME_FROM           268  '268'
            282_1  COME_FROM           254  '254'

 L. 757       282  LOAD_FAST                'create_slot_obj_count'
              284  STORE_FAST               'create_object_count'
            286_0  COME_FROM           280  '280'

 L. 758       286  SETUP_LOOP          318  'to 318'
              288  LOAD_GLOBAL              range
              290  LOAD_FAST                'create_object_count'
              292  CALL_FUNCTION_1       1  '1 positional argument'
              294  GET_ITER         
              296  FOR_ITER            316  'to 316'
              298  STORE_FAST               '_'

 L. 759       300  LOAD_FAST                'self'
              302  LOAD_METHOD              _create_object_on_slot
              304  LOAD_FAST                'spawn_result'
              306  LOAD_FAST                'slot_types'
              308  CALL_METHOD_2         2  '2 positional arguments'
              310  POP_TOP          
          312_314  JUMP_BACK           296  'to 296'
              316  POP_BLOCK        
            318_0  COME_FROM_LOOP      286  '286'
            318_1  COME_FROM           238  '238'
            318_2  COME_FROM           176  '176'

Parse error at or near `None' instruction at offset -1

    def _create_object_on_slot(self, spawner_data, slot_types):
        spawn_list = list(spawner_data.object_reference)
        parent_loc_type = self._get_inherited_spawn_location_type()
        source_object = self.owner
        source_object_parent = source_object.parent
        gardening_component = source_object.get_component(types.GARDENING_COMPONENT)
        for runtime_slot in source_object.get_runtime_slots_gen(slot_types=slot_types):
            if not spawn_list:
                return
                if runtime_slot.empty:
                    if gardening_component is not None:
                        if gardening_component.is_prohibited_spawn_slot(runtime_slot.slot_name_hash, source_object_parent):
                            continue
                    obj_def = spawn_list.pop(0)
                    obj = spawner_data.create_spawned_object(source_object, obj_def, loc_type=parent_loc_type)
                    if obj is not None:
                        self.transfer_parent_states(obj, spawner_data.spawner_option.state_mapping)
                        runtime_slot.add_child(obj)

    def _get_inherited_spawn_location_type(self):
        parent_loc_type = self.owner.item_location
        if parent_loc_type == ItemLocation.FROM_WORLD_FILE or parent_loc_type == ItemLocation.FROM_CONDITIONAL_LAYER:
            parent_loc_type = ItemLocation.FROM_OPEN_STREET
        return parent_loc_type

    def transfer_parent_states(self, child_obj, state_mapping):
        if state_mapping is None:
            return
        for parent_state in state_mapping.keys():
            if self.owner.state_value_active(parent_state):
                weight_pairs = [(data.weight, data.child_state) for data in state_mapping.get(parent_state)]
                state_result = weighted_random_item(weight_pairs)
                child_obj.set_state(state_result.state, state_result)

    def _create_object_on_ground(self, spawner_data, max_distance, min_distance, force_initialization_spawn):
        source_object = self.owner
        spawn_list = list(spawner_data.object_reference)
        parent_loc_type = self._get_inherited_spawn_location_type()
        starting_location_tuning = spawner_data.spawner_option.starting_location
        if spawner_data.spawner_option.starting_location.location_type == SpawnLocation.PORTAL:
            portal_component = self.owner.get_component(PORTAL_COMPONENT)
            if portal_component is None:
                logger.error("Trying to spawn objects relative to a portal position and the spawner object ({}) doesn't have a portal component. No objects will be spawned.", self.owner)
                return
            portal_location = portal_component.get_portal_location_by_type(starting_location_tuning.portal_type, starting_location_tuning.portal_direction, starting_location_tuning.portal_location)
            if portal_location is None:
                logger.error('Unable to find a location relative to the specified portal type, location, and direction. No objects will be spawned.')
                return
        elif starting_location_tuning.location_type == SpawnLocation.PORTAL:
            starting_transform = portal_location.transform
            starting_orientation = portal_location.orientation
            routing_surface = portal_location.routing_surface
        else:
            starting_transform = source_object.transform
            starting_orientation = source_object.orientation
            routing_surface = source_object.routing_surface
        offset_tuning = spawner_data.spawner_option.initial_location_offset
        x_range = offset_tuning.x_randomization_range
        z_range = offset_tuning.z_randomization_range
        for obj in spawn_list:
            default_offset = sims4.math.Vector3(offset_tuning.default_offset.x, offset_tuning.default_offset.y, offset_tuning.default_offset.z)
            if x_range is not None:
                x_axis = starting_orientation.transform_vector(sims4.math.Vector3.X_AXIS())
                default_offset += x_axis * random.uniform(x_range.lower_bound, x_range.upper_bound)
            else:
                if z_range is not None:
                    z_axis = starting_orientation.transform_vector(sims4.math.Vector3.Z_AXIS())
                    default_offset += z_axis * random.uniform(z_range.lower_bound, z_range.upper_bound)
                offset = sims4.math.Transform(default_offset, sims4.math.Quaternion.IDENTITY())
                start_position = sims4.math.Transform.concatenate(offset, starting_transform).translation
                starting_location = placement.create_starting_location(position=start_position, routing_surface=routing_surface)
                created_obj_location = sims4.math.Location(sims4.math.Transform(source_object.position, source_object.orientation), source_object.routing_surface)
                if source_object.is_on_active_lot():
                    fgl_context = placement.create_fgl_context_for_object(starting_location, obj, test_buildbuy_allowed=False,
                      max_distance=max_distance,
                      min_distance=min_distance,
                      height_tolerance=(GlobalObjectSpawnerTuning.SPAWN_ON_GROUND_FGL_HEIGHT_TOLERANCE))
                else:
                    restrictions = [restriction(location=created_obj_location) for restriction in spawner_data.spawner_option.restrictions] or None
                scoring_functions = [placement_scoring(location=created_obj_location) for placement_scoring in spawner_data.spawner_option.placement_scoring] or None
                ignored_object_ids = (source_object.id,) if not spawner_data.spawner_option.starting_location.consider_source_object_footprint else ()
                fgl_context = placement.create_fgl_context_for_object_off_lot(starting_location, None, location=created_obj_location,
                  footprint=(obj.definition.get_footprint()),
                  max_distance=max_distance,
                  min_distance=min_distance,
                  height_tolerance=(GlobalObjectSpawnerTuning.SPAWN_ON_GROUND_FGL_HEIGHT_TOLERANCE),
                  restrictions=restrictions,
                  scoring_functions=scoring_functions,
                  ignored_object_ids=ignored_object_ids)
            position, orientation, _ = fgl_context.find_good_location()
            if position is not None:
                created_obj_location = sims4.math.Location(sims4.math.Transform(position, orientation), starting_location.routing_surface)
                created_obj = spawner_data.create_spawned_object(source_object, obj, loc_type=parent_loc_type)
                if created_obj is None:
                    logger.error('SpawnerComponent: Spawner {} failed to create object: {}', source_object, obj, owner='shouse')
                    return
                else:
                    created_obj.location = created_obj_location
                    created_obj.opacity = 0
                    if force_initialization_spawn:
                        force_states = spawner_data.spawner_option.force_initialization_spawn
                        created_obj.force_spawn_object(spawn_type=(SpawnerType.SLOT))
                    else:
                        force_states = spawner_data.spawner_option.force_states
                if force_states is not None:
                    for force_state in force_states:
                        created_obj.set_state(force_state.state, force_state)

                created_obj.fade_in()
            else:
                logger.info('SpawnerComponent: FGL failed, object {} will not spawn for spawner {}', obj.definition, source_object)

    def reset_spawn_commodity(self, stat):
        reset_value = stat.max_value - randint(0, self.SPAWNER_COMMODITY_RESET_VARIANCE)
        self.owner.commodity_tracker.set_value(stat.stat_type, reset_value)

    def _update_spawn_stat_listeners(self):
        existing_commodities = set(self._spawner_stats)
        spawn_commodities = set()
        for spawn_data in self._spawner_data:
            spawn_type = spawn_data.spawner_option.spawn_type
            if spawn_type == SpawnerType.GROUND:
                spawn_commodities.add(self.GROUND_SPAWNER_DECAY_COMMODITY)
            if spawn_type == SpawnerType.SLOT:
                spawn_commodities.add(self.SLOT_SPAWNER_DECAY_COMMODITY)

        for stat in spawn_commodities - existing_commodities:
            spawn_stat = self.owner.commodity_tracker.add_statistic(stat)
            threshold = sims4.math.Threshold(spawn_stat.min_value, operator.le)
            self._spawner_stats[stat] = self.owner.commodity_tracker.create_and_add_listener(spawn_stat.stat_type, threshold, self.spawn_object_from_commodity)

        for stat in existing_commodities - spawn_commodities:
            self.owner.commodity_tracker.remove_listener(self._spawner_stats[stat])

    def _setup_time_based_spawners(self, weekly_schedule):
        if self._scheduler is None:
            self._scheduler = weekly_schedule(start_callback=(self.trigger_time_spawner))

    def _destroy_time_based_spawners(self):
        if self._scheduler is not None:
            self._scheduler.destroy()
            self._scheduler = None

    @componentmethod_with_fallback((lambda *_: None))
    def add_spawner_data(self, spawner_data):
        self._spawner_data.append(spawner_data)
        if spawner_data.spawn_times is None:
            self._update_spawn_stat_listeners()
        else:
            self._setup_time_based_spawners(spawner_data.spawn_times)
            spawn_type = spawner_data.spawner_option.spawn_type
            if spawn_type == SpawnerType.GROUND:
                self.owner.commodity_tracker.remove_statistic(self.GROUND_SPAWNER_DECAY_COMMODITY)
            if spawn_type == SpawnerType.SLOT:
                self.owner.commodity_tracker.remove_statistic(self.SLOT_SPAWNER_DECAY_COMMODITY)

    def on_remove(self, *_, **__):
        self._destroy_spawner_alarm()
        self._destroy_time_based_spawners()

    def on_child_removed(self, child, new_parent=None):
        if child in self._spawned_objects:
            self._spawned_objects.remove(child)

    def on_client_connect(self, client):
        for created_obj_id in self._spawned_object_ids:
            spawned_object = services.object_manager().get(created_obj_id)
            if spawned_object is not None:
                self._spawned_objects.add(spawned_object)

        self._spawned_object_ids = []
        SpawnerInitializer.create(client.zone_id)

    def initialize_spawning(self):
        if self._spawner_initialized:
            return
        self._spawner_initialized = True
        if self._spawner_data:
            self._spawner_data_spawn_index = 0
            self._create_spawner_alarm()

    def _create_spawner_alarm(self):
        if self._disabled or self._spawner_data_spawn_index >= len(self._spawner_data):
            return
        start_delay = SpawnerInitializer.SPAWN_DELAYED_START
        end_delay = SpawnerInitializer.SPAWN_DELAYED_END
        if self.spawn_time_span_override is not None:
            start_delay = self.spawn_time_span_override.spawn_delayed_start_override
            end_delay = self.spawn_time_span_override.spawn_delayed_end_override
        time_span = date_and_time.create_time_span(minutes=(randint(start_delay, end_delay)))
        repeating_time_span = date_and_time.create_time_span(minutes=(SpawnerInitializer.SPAWN_FREQUENCY))
        self._spawn_object_alarm = alarms.add_alarm(self, time_span, (self._spawn_one_object), repeating=True,
          repeating_time_span=repeating_time_span)

    def _destroy_spawner_alarm(self):
        if self._spawn_object_alarm is not None:
            alarms.cancel_alarm(self._spawn_object_alarm)
            self._spawn_object_alarm = None
            self._spawner_data_spawn_index = -1

    def _spawn_one_object(self, _):
        if self._disabled:
            self._destroy_spawner_alarm()
            return
        else:
            if self._spawner_data_spawn_index >= len(self._spawner_data):
                self._destroy_spawner_alarm()
                return
            spawn_data = self._spawner_data[self._spawner_data_spawn_index]
            self._spawner_data_spawn_index += 1
            if spawn_data.spawner_option.spawn_type == SpawnerType.GROUND or spawn_data.spawner_option.spawn_type == SpawnerType.SLOT:
                if spawn_data.spawner_option.force_initialization_spawn is not None:
                    self._spawn_object(spawn_data.spawner_option.spawn_type)

    def save(self, persistence_master_message):
        persistable_data = protocols.PersistenceMaster.PersistableData()
        persistable_data.type = protocols.PersistenceMaster.PersistableData.SpawnerComponent
        spawner_data = persistable_data.Extensions[protocols.PersistableSpawnerComponent.persistable_data]
        spawner_data.spawned_obj_ids.extend((obj.id for obj in self._spawned_objects))
        spawner_data.spawner_initialized = self._spawner_initialized
        spawner_data.spawner_data_spawn_index = self._spawner_data_spawn_index
        spawner_data.times_commodity_reset = self._times_commodity_reset
        spawner_data.spawner_disabled = self._disabled
        persistence_master_message.data.extend([persistable_data])

    def load(self, persistence_master_message):
        spawner_data = persistence_master_message.Extensions[protocols.PersistableSpawnerComponent.persistable_data]
        for object_id in spawner_data.spawned_obj_ids:
            self._spawned_object_ids.append(object_id)

        self._spawner_initialized = spawner_data.spawner_initialized
        self._spawner_data_spawn_index = spawner_data.spawner_data_spawn_index
        self._times_commodity_reset = spawner_data.times_commodity_reset
        if spawner_data.spawner_disabled:
            self._disable_spawner()
        if self._spawner_data_spawn_index != -1:
            self._create_spawner_alarm()


class SpawnerInitializer:
    SPAWN_FREQUENCY = Tunable(description='\n        This is the frequency at which the spawner components spawn the\n        individual objects for the first time you are playing in the zone.\n        Please talk with a GPE about performance concerns if you tune this\n        value.\n        ',
      tunable_type=int,
      default=5)
    SPAWN_DELAYED_START = TunableRange(description='\n        This is the minimum amount of sim minutes we wait before we start\n        spawning objects for the first time in the zone at SPAWN_FREQUENCY. We\n        pick a random time between the start and end delayed time.\n        ',
      tunable_type=int,
      minimum=0,
      default=15)
    SPAWN_DELAYED_END = TunableRange(description='\n        This is the maximum amount of sim minutes we wait before we start\n        spawning objects for the first time in the zone at SPAWN_FREQUENCY. We\n        pick a random time between the start and end delayed time.\n        ',
      tunable_type=int,
      minimum=0,
      default=60)

    @classmethod
    def create(cls, zone_id):
        global SpawnerInitializerSingleton
        if SpawnerInitializerSingleton is not None:
            if SpawnerInitializerSingleton.zone_id != zone_id:
                SpawnerInitializerSingleton.destroy()
        if SpawnerInitializerSingleton is None:
            SpawnerInitializerSingleton = SpawnerInitializer(zone_id)

    @classmethod
    def destroy(cls):
        global SpawnerInitializerSingleton
        SpawnerInitializerSingleton = None

    def __init__(self, zone_id):
        self._zone_id = zone_id

    @property
    def zone_id(self):
        return self._zone_id

    def spawner_spawn_objects_post_nav_mesh_load(self, zone_id):
        if zone_id == self._zone_id:
            for obj in services.object_manager(self._zone_id).get_all_objects_with_component_gen(SPAWNER_COMPONENT):
                obj.spawner_component.initialize_spawning()

        else:
            logger.info('Mismatched zone id in Spawner initialization. Fence Zone id: {}. Registered Zone id: {}', zone_id, self._zone_id)
            self.destroy()


@sims4.commands.Command('spawners.force_spawn_objects')
def force_spawn_objects(_connection=None):
    for obj in services.object_manager().get_all_objects_with_component_gen(objects.components.types.SPAWNER_COMPONENT):
        obj.force_spawn_object()


@sims4.commands.Command('spawners.slot_spawn')
def force_spawn_slot_objects(obj_id: RequiredTargetParam, _connection=None):
    obj = obj_id.get_target()
    if obj is None or obj.spawner_component is None:
        return
    empty_slot_count = sum((1 for runtime_slot in obj.get_runtime_slots_gen() if runtime_slot.empty))
    obj.force_spawn_object(spawn_type=(SpawnerType.SLOT), ignore_firemeter=True, create_slot_obj_count=empty_slot_count)