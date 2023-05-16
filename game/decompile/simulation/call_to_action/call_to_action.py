# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\call_to_action\call_to_action.py
# Compiled at: 2022-08-26 18:13:12
# Size of source mod 2**32: 14623 bytes
from distributor.ops import SetCallToAction
from distributor.system import Distributor
from event_testing.resolver import DoubleSimResolver
from event_testing.test_variants import TunableSituationJobTest
from filters.tunable import TunableSimFilter
from sims4.localization import TunableLocalizedString
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, TunableRange, TunableColor, Tunable, TunableList, OptionalTunable, TunableTuple, TunableEnumEntry, TunableReference
from interactions import ParticipantType
import relationships.relationship_tests, enum, services, sims4.log, sims.sim_info_tests, tag
from vfx import TunablePlayEffectVariant
logger = sims4.log.Logger('call_to_action', default_owner='nabaker')

class TunableCallToActionTestVariant(sims4.tuning.tunable.TunableVariant):

    def __init__(self, description='A tunable test support for choosing sims to be highlighted', **kwargs):
        (super().__init__)(has_buff=sims.sim_info_tests.BuffTest.TunableFactory(), has_job=TunableSituationJobTest(locked_args={'participant': ParticipantType.Actor}), 
         relationship=relationships.relationship_tests.TunableRelationshipTest(locked_args={'subject':ParticipantType.Actor,  'target_sim':ParticipantType.TargetSim}), 
         description=description, **kwargs)


class CallToActionActorType(enum.Int):
    ACTIVE_SIM = 0
    SCENARIO_SIM = 1


class CallToAction(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.CALL_TO_ACTION)):
    INSTANCE_TUNABLES = {'_color':TunableColor(description='\n            The color of the call to action.\n            '), 
     '_pulse_frequency':TunableRange(description='\n            The frequency at which the highlight pulses.\n            ',
       tunable_type=float,
       default=1.0,
       minimum=0.1), 
     '_thickness':TunableRange(description='\n            The thickness of the highlight.\n            ',
       tunable_type=float,
       default=0.002,
       minimum=0.001,
       maximum=0.005), 
     '_tags':tag.TunableTags(description='\n            The set of tags that are used to determine which objects to highlight.\n            '), 
     '_on_active_lot':Tunable(description='\n            Whether or not objects on active lot should be highlighted.\n            ',
       tunable_type=bool,
       default=True), 
     '_on_open_street':Tunable(description='\n            Whether or not objects on open street should be highlighted.\n            ',
       tunable_type=bool,
       default=True), 
     '_tutorial_text':OptionalTunable(description='\n            Text for a tutorial call to action.  If this is enabled, the\n            CTA will be a tutorial CTA with the specified text.\n            ',
       tunable=TunableLocalizedString()), 
     '_sim_filter':OptionalTunable(description='\n            Filter to select one or more sims to recieve the CTA.\n            ',
       tunable=TunableSimFilter.TunablePackSafeReference()), 
     '_sim_tests':TunableList(description='\n            Tests used to determine which sims to allow in the call to action.\n            ',
       tunable=TunableTuple(description='\n                A combination of a test and information to choose a sim as the test target.\n                ',
       test=(TunableCallToActionTestVariant()),
       target_type=TunableEnumEntry(description='\n                    How to determine which sim should be chosen as the target of this test.\n                    ',
       tunable_type=CallToActionActorType,
       default=(CallToActionActorType.ACTIVE_SIM)),
       scenario_role=TunableReference(description='\n                    When set and Target Type is SCENARIO_SIM this will be the role used to determine\n                    what sim to target for the test.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
       class_restrictions=('ScenarioRole', ),
       allow_none=True))), 
     '_max_highlighted_objects':TunableRange(description='\n            The maximum number of objects that will be highlighted by this call to action.\n            0 means no limit.\n            ',
       tunable_type=int,
       minimum=0,
       default=0), 
     'highlighted_object_vfx':OptionalTunable(description='\n            If enabled, we will play an effect on the objects highlighted by this call to action.\n            ',
       tunable=TunablePlayEffectVariant(description='\n                Effect to play on the objects when they are highlighted.\n                '))}

    def __init__(self):
        super().__init__()
        self._owner = None
        self._sim_ids = []
        self._num_highlighted_objects = 0
        self._object_vfx_handlers = []

    def get_sim_filter_gsi_name(self):
        return str(self)

    @property
    def owner(self):
        return self._owner

    def sim_passes_tests(self, sim_to_test):
        active_sim = services.client_manager().get_first_client().active_sim.sim_info
        scenario = None
        if active_sim.household:
            if active_sim.household.scenario_tracker:
                scenario = active_sim.household.scenario_tracker.active_scenario
        for test_info in self._sim_tests:
            target_sim = active_sim
            if test_info.target_type == CallToActionActorType.SCENARIO_SIM:
                if scenario is None or test_info.scenario_role is None:
                    return False
                scenario_sims = frozenset(scenario.sim_infos_of_interest_gen([test_info.scenario_role]))
                if active_sim not in scenario_sims:
                    target_sim = next(iter(scenario_sims), None)
            if target_sim is None:
                return False
                return DoubleSimResolver(sim_to_test, target_sim)(test_info.test) or False

        return True

    def reached_max_highlighted_objects(self):
        return self._max_highlighted_objects != 0 and self._num_highlighted_objects >= self._max_highlighted_objects

    def turn_on--- This code section failed: ---

 L. 190         0  LOAD_FAST                'owner'
                2  LOAD_FAST                'self'
                4  STORE_ATTR               _owner

 L. 191         6  SETUP_LOOP           60  'to 60'
                8  LOAD_GLOBAL              services
               10  LOAD_METHOD              object_manager
               12  CALL_METHOD_0         0  '0 positional arguments'
               14  LOAD_ATTR                get_objects_with_tags_gen
               16  LOAD_FAST                'self'
               18  LOAD_ATTR                _tags
               20  CALL_FUNCTION_EX      0  'positional arguments only'
               22  GET_ITER         
             24_0  COME_FROM            50  '50'
             24_1  COME_FROM            32  '32'
               24  FOR_ITER             58  'to 58'
               26  STORE_FAST               'script_object'

 L. 192        28  LOAD_FAST                'script_object'
               30  LOAD_ATTR                visible_to_client
               32  POP_JUMP_IF_FALSE    24  'to 24'

 L. 193        34  LOAD_FAST                'self'
               36  LOAD_METHOD              _turn_on_object
               38  LOAD_FAST                'script_object'
               40  CALL_METHOD_1         1  '1 positional argument'
               42  POP_TOP          

 L. 194        44  LOAD_FAST                'self'
               46  LOAD_METHOD              reached_max_highlighted_objects
               48  CALL_METHOD_0         0  '0 positional arguments'
               50  POP_JUMP_IF_FALSE    24  'to 24'

 L. 195        52  LOAD_CONST               None
               54  RETURN_VALUE     
               56  JUMP_BACK            24  'to 24'
               58  POP_BLOCK        
             60_0  COME_FROM_LOOP        6  '6'

 L. 197        60  BUILD_LIST_0          0 
               62  LOAD_FAST                'self'
               64  STORE_ATTR               _sim_ids

 L. 198        66  LOAD_FAST                'self'
               68  LOAD_ATTR                _sim_filter
               70  LOAD_CONST               None
               72  COMPARE_OP               is-not
               74  POP_JUMP_IF_FALSE   192  'to 192'

 L. 199        76  LOAD_GLOBAL              tuple
               78  LOAD_GENEXPR             '<code_object <genexpr>>'
               80  LOAD_STR                 'CallToAction.turn_on.<locals>.<genexpr>'
               82  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
               84  LOAD_GLOBAL              services
               86  LOAD_METHOD              sim_info_manager
               88  CALL_METHOD_0         0  '0 positional arguments'
               90  LOAD_METHOD              instanced_sims_gen
               92  CALL_METHOD_0         0  '0 positional arguments'
               94  GET_ITER         
               96  CALL_FUNCTION_1       1  '1 positional argument'
               98  CALL_FUNCTION_1       1  '1 positional argument'
              100  STORE_FAST               'constrained_sims'

 L. 200       102  LOAD_GLOBAL              services
              104  LOAD_METHOD              client_manager
              106  CALL_METHOD_0         0  '0 positional arguments'
              108  LOAD_METHOD              get_first_client
              110  CALL_METHOD_0         0  '0 positional arguments'
              112  LOAD_ATTR                active_sim
              114  LOAD_ATTR                sim_info
              116  STORE_FAST               'active_sim'

 L. 201       118  LOAD_GLOBAL              services
              120  LOAD_METHOD              sim_filter_service
              122  CALL_METHOD_0         0  '0 positional arguments'
              124  LOAD_ATTR                submit_filter
              126  LOAD_FAST                'self'
              128  LOAD_ATTR                _sim_filter

 L. 202       130  LOAD_CONST               None

 L. 203       132  LOAD_FAST                'constrained_sims'

 L. 204       134  LOAD_CONST               False

 L. 205       136  LOAD_FAST                'active_sim'

 L. 206       138  LOAD_FAST                'self'
              140  LOAD_ATTR                get_sim_filter_gsi_name
              142  LOAD_CONST               ('sim_filter', 'callback', 'sim_constraints', 'allow_yielding', 'requesting_sim_info', 'gsi_source_fn')
              144  CALL_FUNCTION_KW_6     6  '6 total positional and keyword args'
              146  STORE_FAST               'filter_result'

 L. 208       148  SETUP_LOOP          246  'to 246'
              150  LOAD_FAST                'filter_result'
              152  GET_ITER         
            154_0  COME_FROM           168  '168'
              154  FOR_ITER            188  'to 188'
              156  STORE_FAST               'result'

 L. 210       158  LOAD_FAST                'self'
              160  LOAD_METHOD              sim_passes_tests
              162  LOAD_FAST                'result'
              164  LOAD_ATTR                sim_info
              166  CALL_METHOD_1         1  '1 positional argument'
              168  POP_JUMP_IF_FALSE   154  'to 154'

 L. 211       170  LOAD_FAST                'self'
              172  LOAD_ATTR                _sim_ids
              174  LOAD_METHOD              append
              176  LOAD_FAST                'result'
              178  LOAD_ATTR                sim_info
              180  LOAD_ATTR                sim_id
              182  CALL_METHOD_1         1  '1 positional argument'
              184  POP_TOP          
              186  JUMP_BACK           154  'to 154'
              188  POP_BLOCK        
              190  JUMP_FORWARD        246  'to 246'
            192_0  COME_FROM            74  '74'

 L. 213       192  LOAD_FAST                'self'
              194  LOAD_ATTR                _sim_tests
              196  POP_JUMP_IF_FALSE   246  'to 246'

 L. 214       198  SETUP_LOOP          246  'to 246'
              200  LOAD_GLOBAL              services
              202  LOAD_METHOD              sim_info_manager
              204  CALL_METHOD_0         0  '0 positional arguments'
              206  LOAD_METHOD              instanced_sims_gen
              208  CALL_METHOD_0         0  '0 positional arguments'
              210  GET_ITER         
            212_0  COME_FROM           226  '226'
              212  FOR_ITER            244  'to 244'
              214  STORE_FAST               'instanced_sim'

 L. 215       216  LOAD_FAST                'self'
              218  LOAD_METHOD              sim_passes_tests
              220  LOAD_FAST                'instanced_sim'
              222  LOAD_ATTR                sim_info
              224  CALL_METHOD_1         1  '1 positional argument'
              226  POP_JUMP_IF_FALSE   212  'to 212'

 L. 216       228  LOAD_FAST                'self'
              230  LOAD_ATTR                _sim_ids
              232  LOAD_METHOD              append
              234  LOAD_FAST                'instanced_sim'
              236  LOAD_ATTR                sim_id
              238  CALL_METHOD_1         1  '1 positional argument'
              240  POP_TOP          
              242  JUMP_BACK           212  'to 212'
              244  POP_BLOCK        
            246_0  COME_FROM_LOOP      198  '198'
            246_1  COME_FROM           196  '196'
            246_2  COME_FROM           190  '190'
            246_3  COME_FROM_LOOP      148  '148'

 L. 218       246  LOAD_FAST                'self'
              248  LOAD_ATTR                _sim_ids
          250_252  POP_JUMP_IF_FALSE   314  'to 314'

 L. 219       254  LOAD_GLOBAL              services
              256  LOAD_METHOD              object_manager
              258  CALL_METHOD_0         0  '0 positional arguments'
              260  STORE_FAST               'object_manager'

 L. 220       262  SETUP_LOOP          314  'to 314'
              264  LOAD_FAST                'self'
              266  LOAD_ATTR                _sim_ids
              268  GET_ITER         
            270_0  COME_FROM           300  '300'
              270  FOR_ITER            312  'to 312'
              272  STORE_FAST               'sim_id'

 L. 221       274  LOAD_FAST                'object_manager'
              276  LOAD_METHOD              get
              278  LOAD_FAST                'sim_id'
              280  CALL_METHOD_1         1  '1 positional argument'
              282  STORE_FAST               'sim'

 L. 222       284  LOAD_FAST                'self'
              286  LOAD_METHOD              _turn_on_object
              288  LOAD_FAST                'sim'
              290  CALL_METHOD_1         1  '1 positional argument'
              292  POP_TOP          

 L. 223       294  LOAD_FAST                'self'
              296  LOAD_METHOD              reached_max_highlighted_objects
              298  CALL_METHOD_0         0  '0 positional arguments'
          300_302  POP_JUMP_IF_FALSE   270  'to 270'

 L. 224       304  LOAD_CONST               None
              306  RETURN_VALUE     
          308_310  JUMP_BACK           270  'to 270'
              312  POP_BLOCK        
            314_0  COME_FROM_LOOP      262  '262'
            314_1  COME_FROM           250  '250'

Parse error at or near `LOAD_FAST' instruction at offset 246

    def turn_off(self):
        if self._owner is not None:
            self._owner.on_cta_ended(self.guid64)
        for script_object in (services.object_manager().get_objects_with_tags_gen)(*self._tags):
            Distributor.instance().add_op(script_object, SetCallToAction(0, 0, 0, None))

        object_manager = services.object_manager()
        for sim_id in self._sim_ids:
            sim = object_manager.get(sim_id)
            if sim is not None:
                Distributor.instance().add_op(sim, SetCallToAction(0, 0, 0))

        for object_vfx in self._object_vfx_handlers:
            object_vfx.stop()

        self._sim_ids = []
        self._num_highlighted_objects = 0
        self._object_vfx_handlers = []

    def turn_on_object_on_create(self, script_object):
        if (script_object.definition.has_build_buy_tag)(*self._tags):
            script_object.register_on_location_changed(self._object_location_changed)
        else:
            if script_object.is_sim and self._sim_filter is not None:
                active_sim = services.client_manager().get_first_client().active_sim.sim_info
                results = services.sim_filter_service().submit_filter(sim_filter=(self._sim_filter), callback=None,
                  sim_constraints=(
                 script_object.sim_info.sim_id,),
                  allow_yielding=False,
                  requesting_sim_info=active_sim,
                  gsi_source_fn=(self.get_sim_filter_gsi_name))
                if results and self.sim_passes_tests(script_object.sim_info):
                    script_object.register_on_location_changed(self._object_location_changed)
            elif script_object.is_sim:
                if self._sim_tests:
                    if self.sim_passes_tests(script_object.sim_info):
                        script_object.register_on_location_changed(self._object_location_changed)

    def _turn_on_object(self, script_object):
        if script_object.is_on_active_lot():
            return self._on_active_lot or None
        else:
            if not self._on_open_street:
                return
        Distributor.instance().add_op(script_object, SetCallToAction((self._color), (self._pulse_frequency),
          (self._thickness),
          tutorial_text=(self._tutorial_text)))
        if self.highlighted_object_vfx is not None:
            object_vfx = self.highlighted_object_vfx(script_object)
            object_vfx.start()
            self._object_vfx_handlers.append(object_vfx)
        self._num_highlighted_objects += 1

    def _object_location_changed(self, script_object, old_loc, new_loc):
        script_object.unregister_on_location_changed(self._object_location_changed)
        if script_object.is_sim:
            self._sim_ids.append(script_object.sim_info.sim_id)
        if self.reached_max_highlighted_objects():
            return
        self._turn_on_object(script_object)

    def turn_off_object_on_remove(self, script_object):
        if self._max_highlighted_objects == 0:
            return
        is_matching_object = False
        if (script_object.definition.has_build_buy_tag)(*self._tags):
            is_matching_object = True
        else:
            if script_object.is_sim:
                if script_object.sim_info.sim_id in self._sim_ids:
                    is_matching_object = True
            elif is_matching_object:
                if self._num_highlighted_objects > 0:
                    self._num_highlighted_objects -= 1
                    if self._num_highlighted_objects == self._max_highlighted_objects - 1:
                        self._num_highlighted_objects = 0
                        self.turn_on(self._owner)