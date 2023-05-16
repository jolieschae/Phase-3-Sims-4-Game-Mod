# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\postures\posture_state.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 41201 bytes
from animation.posture_manifest import Hand, SlotManifest
from carry.carry_tuning import CarryPostureStaticTuning
from carry.carry_utils import hand_to_track, create_carry_constraint, track_to_hand
from interactions.constraints import Anywhere, Constraint
from objects.definition import Definition
from postures import PostureTrack, posture_specs
from postures.posture_specs import PostureSpecVariable, PostureAspectCarry, PostureAspectSurface, get_carry_posture_aop
from postures.posture_state_spec import PostureStateSpec
from sims4.collections import frozendict
from sims4.repr_utils import standard_repr
from tag import Tag
import postures, sims4.log
logger = sims4.log.Logger('Postures')

class PostureState:

    def __init__--- This code section failed: ---

 L.  46         0  LOAD_CLOSURE             'carry_posture_overrides'
                2  LOAD_CLOSURE             'sim'
                4  BUILD_TUPLE_2         2 
                6  LOAD_CODE                <code_object _get_default_carry_aspect>
                8  LOAD_STR                 'PostureState.__init__.<locals>._get_default_carry_aspect'
               10  MAKE_FUNCTION_8          'closure'
               12  STORE_FAST               '_get_default_carry_aspect'

 L.  51        14  LOAD_CONST               None
               16  LOAD_FAST                'self'
               18  STORE_ATTR               _constraint_intersection

 L.  52        20  LOAD_CONST               True
               22  LOAD_FAST                'self'
               24  STORE_ATTR               _constraint_intersection_dirty

 L.  53        26  LOAD_FAST                'posture_spec'
               28  LOAD_FAST                'self'
               30  STORE_ATTR               _spec

 L.  54        32  LOAD_DEREF               'sim'
               34  LOAD_METHOD              ref
               36  CALL_METHOD_0         0  '0 positional arguments'
               38  LOAD_FAST                'self'
               40  STORE_ATTR               _sim_ref

 L.  55        42  LOAD_CONST               None
               44  LOAD_FAST                'self'
               46  STORE_ATTR               _linked_posture_state

 L.  56        48  LOAD_CONST               True
               50  LOAD_FAST                'self'
               52  STORE_ATTR               _valid

 L.  57        54  BUILD_MAP_0           0 
               56  LOAD_FAST                'self'
               58  STORE_ATTR               _constraints

 L.  58        60  LOAD_FAST                'invalid_expected'
               62  LOAD_FAST                'self'
               64  STORE_ATTR               _invalid_expected

 L.  59        66  LOAD_FAST                'body_state_spec_only'
               68  LOAD_FAST                'self'
               70  STORE_ATTR               body_state_spec_only

 L.  60        72  LOAD_CONST               None
               74  LOAD_FAST                'self'
               76  STORE_ATTR               _posture_constraint

 L.  61        78  LOAD_CONST               None
               80  LOAD_FAST                'self'
               82  STORE_ATTR               _posture_constraint_strict

 L.  63        84  LOAD_FAST                'posture_spec'
               86  LOAD_ATTR                body
               88  STORE_FAST               'spec_body'

 L.  65        90  LOAD_FAST                'spec_body'
               92  LOAD_ATTR                target
               94  LOAD_FAST                'self'
               96  STORE_ATTR               body_target

 L.  67        98  LOAD_FAST                'current_posture_state'
              100  LOAD_CONST               None
              102  COMPARE_OP               is
              104  POP_JUMP_IF_TRUE    134  'to 134'

 L.  68       106  LOAD_FAST                'spec_body'
              108  LOAD_ATTR                posture_type
              110  LOAD_FAST                'current_posture_state'
              112  LOAD_ATTR                body
              114  LOAD_ATTR                posture_type
              116  COMPARE_OP               !=
              118  POP_JUMP_IF_TRUE    134  'to 134'

 L.  69       120  LOAD_FAST                'spec_body'
              122  LOAD_ATTR                target
              124  LOAD_FAST                'current_posture_state'
              126  LOAD_ATTR                body
              128  LOAD_ATTR                target
              130  COMPARE_OP               !=
              132  POP_JUMP_IF_FALSE   200  'to 200'
            134_0  COME_FROM           118  '118'
            134_1  COME_FROM           104  '104'

 L.  72       134  LOAD_CONST               None
              136  STORE_FAST               'animation_context'

 L.  73       138  LOAD_FAST                'current_posture_state'
              140  LOAD_CONST               None
              142  COMPARE_OP               is-not
              144  POP_JUMP_IF_FALSE   170  'to 170'

 L.  74       146  LOAD_FAST                'current_posture_state'
              148  LOAD_ATTR                body
              150  LOAD_ATTR                mobile
              152  POP_JUMP_IF_TRUE    170  'to 170'

 L.  75       154  LOAD_FAST                'spec_body'
              156  LOAD_ATTR                posture_type
              158  LOAD_ATTR                mobile
              160  POP_JUMP_IF_TRUE    170  'to 170'

 L.  76       162  LOAD_FAST                'current_posture_state'
              164  LOAD_ATTR                body
              166  LOAD_ATTR                animation_context
              168  STORE_FAST               'animation_context'
            170_0  COME_FROM           160  '160'
            170_1  COME_FROM           152  '152'
            170_2  COME_FROM           144  '144'

 L.  81       170  LOAD_GLOBAL              postures
              172  LOAD_ATTR                create_posture
              174  LOAD_FAST                'spec_body'
              176  LOAD_ATTR                posture_type

 L.  82       178  LOAD_FAST                'self'
              180  LOAD_ATTR                sim

 L.  83       182  LOAD_FAST                'self'
              184  LOAD_ATTR                body_target

 L.  84       186  LOAD_FAST                'animation_context'

 L.  85       188  LOAD_FAST                'is_throwaway'
              190  LOAD_CONST               ('animation_context', 'is_throwaway')
              192  CALL_FUNCTION_KW_5     5  '5 total positional and keyword args'
              194  LOAD_FAST                'self'
              196  STORE_ATTR               _aspect_body
              198  JUMP_FORWARD        208  'to 208'
            200_0  COME_FROM           132  '132'

 L.  87       200  LOAD_FAST                'current_posture_state'
              202  LOAD_ATTR                body
              204  LOAD_FAST                'self'
              206  STORE_ATTR               _aspect_body
            208_0  COME_FROM           198  '198'

 L.  95       208  LOAD_FAST                'self'
              210  LOAD_ATTR                _aspect_body
              212  LOAD_ATTR                get_provided_postures
              214  LOAD_FAST                'self'
              216  LOAD_ATTR                surface_target

 L.  96       218  LOAD_CONST               True
              220  LOAD_CONST               ('surface_target', 'concrete')
              222  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              224  STORE_FAST               'posture_manifest'

 L.  98       226  LOAD_FAST                'posture_manifest'
              228  LOAD_METHOD              get_constraint_version
              230  LOAD_FAST                'self'
              232  LOAD_ATTR                sim
              234  CALL_METHOD_1         1  '1 positional argument'
              236  STORE_FAST               'posture_manifest'

 L. 100       238  LOAD_GLOBAL              PostureStateSpec
              240  LOAD_FAST                'posture_manifest'
              242  LOAD_GLOBAL              SlotManifest
              244  CALL_FUNCTION_0       0  '0 positional arguments'
              246  LOAD_FAST                'self'
              248  LOAD_ATTR                _aspect_body
              250  LOAD_ATTR                target
          252_254  JUMP_IF_TRUE_OR_POP   260  'to 260'
              256  LOAD_GLOBAL              PostureSpecVariable
              258  LOAD_ATTR                ANYTHING
            260_0  COME_FROM           252  '252'
              260  CALL_FUNCTION_3       3  '3 positional arguments'
              262  STORE_FAST               'posture_state_spec'

 L. 102       264  LOAD_GLOBAL              Constraint
              266  LOAD_STR                 'PostureStateManifestConstraint'

 L. 103       268  LOAD_FAST                'posture_state_spec'
              270  LOAD_CONST               ('debug_name', 'posture_state_spec')
              272  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              274  LOAD_FAST                'self'
              276  STORE_ATTR               body_posture_state_constraint

 L. 105       278  LOAD_FAST                'body_state_spec_only'
          280_282  POP_JUMP_IF_FALSE   300  'to 300'

 L. 106       284  LOAD_FAST                'self'
              286  LOAD_ATTR                body_posture_state_constraint
              288  LOAD_FAST                'self'
              290  LOAD_ATTR                _constraints
              292  LOAD_CONST               None
              294  STORE_SUBSCR     

 L. 109       296  LOAD_CONST               None
              298  RETURN_VALUE     
            300_0  COME_FROM           280  '280'

 L. 120       300  LOAD_FAST                'self'
              302  LOAD_ATTR                _aspect_body
              304  LOAD_ATTR                slot_constraint
              306  STORE_FAST               'body_slot_constraint'

 L. 121       308  LOAD_FAST                'body_slot_constraint'
              310  LOAD_CONST               None
              312  COMPARE_OP               is-not
          314_316  POP_JUMP_IF_FALSE   362  'to 362'

 L. 122       318  LOAD_FAST                'self'
              320  LOAD_ATTR                _aspect_body
              322  LOAD_ATTR                is_vehicle
          324_326  POP_JUMP_IF_FALSE   348  'to 348'
              328  LOAD_FAST                'current_posture_state'
              330  LOAD_CONST               None
              332  COMPARE_OP               is-not
          334_336  POP_JUMP_IF_FALSE   348  'to 348'
              338  LOAD_FAST                'current_posture_state'
              340  LOAD_ATTR                body
              342  LOAD_ATTR                is_vehicle
          344_346  POP_JUMP_IF_TRUE    362  'to 362'
            348_0  COME_FROM           334  '334'
            348_1  COME_FROM           324  '324'

 L. 123       348  LOAD_FAST                'self'
              350  LOAD_ATTR                body_posture_state_constraint
              352  LOAD_METHOD              intersect
              354  LOAD_FAST                'body_slot_constraint'
              356  CALL_METHOD_1         1  '1 positional argument'
              358  STORE_FAST               'body_posture_constraint'
              360  JUMP_FORWARD        368  'to 368'
            362_0  COME_FROM           344  '344'
            362_1  COME_FROM           314  '314'

 L. 125       362  LOAD_FAST                'self'
              364  LOAD_ATTR                body_posture_state_constraint
              366  STORE_FAST               'body_posture_constraint'
            368_0  COME_FROM           360  '360'

 L. 127       368  LOAD_FAST                'body_posture_constraint'
              370  LOAD_FAST                'self'
              372  LOAD_ATTR                _constraints
              374  LOAD_CONST               None
              376  STORE_SUBSCR     

 L. 129       378  LOAD_FAST                'current_posture_state'
              380  LOAD_CONST               None
              382  COMPARE_OP               is-not
          384_386  POP_JUMP_IF_FALSE   402  'to 402'

 L. 130       388  LOAD_FAST                'current_posture_state'
              390  LOAD_METHOD              get_posture_spec
              392  LOAD_FAST                'var_map'
              394  CALL_METHOD_1         1  '1 positional argument'
              396  LOAD_ATTR                carry
              398  LOAD_ATTR                target
              400  STORE_FAST               'curr_spec_carry_target'
            402_0  COME_FROM           384  '384'

 L. 132       402  LOAD_FAST                'posture_spec'
              404  LOAD_ATTR                carry
              406  STORE_FAST               'spec_carry'

 L. 133       408  LOAD_FAST                'spec_carry'
              410  LOAD_ATTR                target
              412  STORE_FAST               'spec_carry_target'

 L. 134       414  LOAD_FAST                'current_posture_state'
              416  LOAD_CONST               None
              418  COMPARE_OP               is-not
          420_422  POP_JUMP_IF_FALSE  1068  'to 1068'
              424  LOAD_FAST                'spec_carry_target'
              426  LOAD_FAST                'curr_spec_carry_target'
              428  COMPARE_OP               !=
          430_432  POP_JUMP_IF_FALSE  1068  'to 1068'

 L. 135       434  LOAD_FAST                'spec_carry_target'
              436  LOAD_CONST               None
              438  COMPARE_OP               is
          440_442  POP_JUMP_IF_FALSE   580  'to 580'

 L. 137       444  LOAD_FAST                'var_map'
              446  LOAD_METHOD              get
              448  LOAD_FAST                'curr_spec_carry_target'
              450  CALL_METHOD_1         1  '1 positional argument'
              452  STORE_FAST               'current_carry_target'

 L. 138       454  LOAD_FAST                'current_posture_state'
              456  LOAD_METHOD              get_carry_track
              458  LOAD_FAST                'current_carry_target'
              460  CALL_METHOD_1         1  '1 positional argument'
              462  STORE_FAST               'current_carry_track'

 L. 139       464  LOAD_FAST                'current_carry_track'
              466  LOAD_GLOBAL              PostureTrack
              468  LOAD_ATTR                RIGHT
              470  COMPARE_OP               ==
          472_474  POP_JUMP_IF_FALSE   506  'to 506'

 L. 140       476  LOAD_FAST                '_get_default_carry_aspect'
              478  LOAD_GLOBAL              PostureTrack
              480  LOAD_ATTR                RIGHT
              482  CALL_FUNCTION_1       1  '1 positional argument'
              484  LOAD_FAST                'self'
              486  STORE_ATTR               _aspect_carry_right

 L. 141       488  LOAD_FAST                'current_posture_state'
              490  LOAD_ATTR                left
              492  LOAD_FAST                'self'
              494  STORE_ATTR               _aspect_carry_left

 L. 142       496  LOAD_FAST                'current_posture_state'
              498  LOAD_ATTR                back
              500  LOAD_FAST                'self'
              502  STORE_ATTR               _aspect_carry_back
              504  JUMP_ABSOLUTE      1422  'to 1422'
            506_0  COME_FROM           472  '472'

 L. 143       506  LOAD_FAST                'current_carry_track'
              508  LOAD_GLOBAL              PostureTrack
              510  LOAD_ATTR                LEFT
              512  COMPARE_OP               ==
          514_516  POP_JUMP_IF_FALSE   548  'to 548'

 L. 144       518  LOAD_FAST                '_get_default_carry_aspect'
              520  LOAD_GLOBAL              PostureTrack
              522  LOAD_ATTR                LEFT
              524  CALL_FUNCTION_1       1  '1 positional argument'
              526  LOAD_FAST                'self'
              528  STORE_ATTR               _aspect_carry_left

 L. 145       530  LOAD_FAST                'current_posture_state'
              532  LOAD_ATTR                right
              534  LOAD_FAST                'self'
              536  STORE_ATTR               _aspect_carry_right

 L. 146       538  LOAD_FAST                'current_posture_state'
              540  LOAD_ATTR                back
              542  LOAD_FAST                'self'
              544  STORE_ATTR               _aspect_carry_back
              546  JUMP_ABSOLUTE      1422  'to 1422'
            548_0  COME_FROM           514  '514'

 L. 148       548  LOAD_FAST                '_get_default_carry_aspect'
              550  LOAD_GLOBAL              PostureTrack
              552  LOAD_ATTR                BACK
              554  CALL_FUNCTION_1       1  '1 positional argument'
              556  LOAD_FAST                'self'
              558  STORE_ATTR               _aspect_carry_back

 L. 149       560  LOAD_FAST                'current_posture_state'
              562  LOAD_ATTR                left
              564  LOAD_FAST                'self'
              566  STORE_ATTR               _aspect_carry_left

 L. 150       568  LOAD_FAST                'current_posture_state'
              570  LOAD_ATTR                right
              572  LOAD_FAST                'self'
              574  STORE_ATTR               _aspect_carry_right
          576_578  JUMP_ABSOLUTE      1422  'to 1422'
            580_0  COME_FROM           440  '440'

 L. 152       580  LOAD_FAST                'spec_carry'
              582  LOAD_ATTR                posture_type
              584  STORE_FAST               'spec_carry_posture_type'

 L. 153       586  LOAD_FAST                'spec_carry_target'
              588  LOAD_FAST                'var_map'
              590  COMPARE_OP               not-in
          592_594  POP_JUMP_IF_FALSE   618  'to 618'

 L. 154       596  LOAD_GLOBAL              KeyError
              598  LOAD_STR                 'spec_carry_target {} not in var_map:{}. Sim posture state {} and carry aspects {}, '
              600  LOAD_METHOD              format
              602  LOAD_FAST                'spec_carry_target'
              604  LOAD_FAST                'var_map'
              606  LOAD_FAST                'current_posture_state'
              608  LOAD_FAST                'current_posture_state'
              610  LOAD_ATTR                carry_aspects
              612  CALL_METHOD_4         4  '4 positional arguments'
              614  CALL_FUNCTION_1       1  '1 positional argument'
              616  RAISE_VARARGS_1       1  'exception instance'
            618_0  COME_FROM           592  '592'

 L. 155       618  LOAD_FAST                'spec_carry_posture_type'
              620  LOAD_FAST                'var_map'
              622  COMPARE_OP               not-in
          624_626  POP_JUMP_IF_FALSE   720  'to 720'

 L. 158       628  LOAD_FAST                'var_map'
              630  LOAD_FAST                'spec_carry_target'
              632  BINARY_SUBSCR    
              634  STORE_FAST               'carry_target'

 L. 159       636  LOAD_GLOBAL              posture_specs
              638  LOAD_ATTR                get_carry_posture_aop
              640  LOAD_DEREF               'sim'
              642  LOAD_FAST                'carry_target'
              644  LOAD_FAST                'var_map'
              646  LOAD_GLOBAL              PostureSpecVariable
              648  LOAD_ATTR                HAND
              650  BINARY_SUBSCR    
              652  LOAD_CONST               ('hand',)
              654  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              656  STORE_FAST               'aop'

 L. 160       658  LOAD_FAST                'aop'
              660  LOAD_CONST               None
              662  COMPARE_OP               is
          664_666  POP_JUMP_IF_FALSE   684  'to 684'

 L. 161       668  LOAD_GLOBAL              RuntimeError
              670  LOAD_STR                 'Sim {} failed to find carry posture aop for carry target {}.'
              672  LOAD_METHOD              format
              674  LOAD_DEREF               'sim'
              676  LOAD_FAST                'carry_target'
              678  CALL_METHOD_2         2  '2 positional arguments'
              680  CALL_FUNCTION_1       1  '1 positional argument'
              682  RAISE_VARARGS_1       1  'exception instance'
            684_0  COME_FROM           664  '664'

 L. 162       684  LOAD_FAST                'aop'
              686  LOAD_ATTR                affordance
              688  LOAD_ATTR                _carry_posture_type
              690  STORE_FAST               'carry_posture_type'

 L. 163       692  LOAD_FAST                'carry_posture_type'
              694  LOAD_CONST               None
              696  COMPARE_OP               is
          698_700  POP_JUMP_IF_FALSE   706  'to 706'

 L. 164       702  LOAD_GLOBAL              KeyError
              704  RAISE_VARARGS_1       1  'exception instance'
            706_0  COME_FROM           698  '698'

 L. 165       706  LOAD_FAST                'var_map'
              708  LOAD_GLOBAL              PostureSpecVariable
              710  LOAD_ATTR                POSTURE_TYPE_CARRY_OBJECT
              712  LOAD_FAST                'carry_posture_type'
              714  BUILD_MAP_1           1 
              716  INPLACE_ADD      
              718  STORE_FAST               'var_map'
            720_0  COME_FROM           624  '624'

 L. 167       720  LOAD_FAST                'var_map'
              722  LOAD_FAST                'spec_carry_target'
              724  BINARY_SUBSCR    
              726  STORE_FAST               'carry_target'

 L. 168       728  LOAD_FAST                'var_map'
              730  LOAD_FAST                'spec_carry_posture_type'
              732  BINARY_SUBSCR    
              734  STORE_FAST               'carry_posture_type'

 L. 169       736  LOAD_FAST                'spec_carry'
              738  LOAD_ATTR                hand
              740  LOAD_FAST                'var_map'
              742  COMPARE_OP               in
          744_746  POP_JUMP_IF_FALSE   760  'to 760'

 L. 170       748  LOAD_FAST                'var_map'
              750  LOAD_FAST                'spec_carry'
              752  LOAD_ATTR                hand
              754  BINARY_SUBSCR    
              756  STORE_FAST               'hand'
              758  JUMP_FORWARD        808  'to 808'
            760_0  COME_FROM           744  '744'

 L. 182       760  SETUP_LOOP          808  'to 808'
              762  LOAD_DEREF               'sim'
              764  LOAD_ATTR                posture_state
              766  LOAD_METHOD              get_free_hands
              768  CALL_METHOD_0         0  '0 positional arguments'
              770  GET_ITER         
            772_0  COME_FROM           788  '788'
              772  FOR_ITER            798  'to 798'
              774  STORE_FAST               'hand'

 L. 183       776  LOAD_FAST                'hand'
              778  LOAD_FAST                'carry_target'
              780  LOAD_METHOD              get_allowed_hands
              782  LOAD_DEREF               'sim'
              784  CALL_METHOD_1         1  '1 positional argument'
              786  COMPARE_OP               in
          788_790  POP_JUMP_IF_FALSE   772  'to 772'

 L. 184       792  BREAK_LOOP       
          794_796  JUMP_BACK           772  'to 772'
              798  POP_BLOCK        

 L. 186       800  LOAD_GLOBAL              RuntimeError
              802  LOAD_STR                 'No allowable free hand was empty.'
              804  CALL_FUNCTION_1       1  '1 positional argument'
              806  RAISE_VARARGS_1       1  'exception instance'
            808_0  COME_FROM_LOOP      760  '760'
            808_1  COME_FROM           758  '758'

 L. 188       808  LOAD_GLOBAL              postures
              810  LOAD_ATTR                create_posture
              812  LOAD_FAST                'carry_posture_type'

 L. 189       814  LOAD_FAST                'self'
              816  LOAD_ATTR                sim

 L. 190       818  LOAD_FAST                'carry_target'

 L. 191       820  LOAD_GLOBAL              hand_to_track
              822  LOAD_FAST                'hand'
              824  CALL_FUNCTION_1       1  '1 positional argument'

 L. 192       826  LOAD_FAST                'is_throwaway'
              828  LOAD_CONST               ('track', 'is_throwaway')
              830  CALL_FUNCTION_KW_5     5  '5 total positional and keyword args'
              832  STORE_FAST               'new_carry_aspect'

 L. 194       834  LOAD_FAST                'hand'
              836  LOAD_GLOBAL              Hand
              838  LOAD_ATTR                LEFT
              840  COMPARE_OP               ==
          842_844  POP_JUMP_IF_FALSE   906  'to 906'

 L. 195       846  LOAD_FAST                'new_carry_aspect'
              848  LOAD_FAST                'self'
              850  STORE_ATTR               _aspect_carry_left

 L. 196       852  LOAD_FAST                'current_posture_state'
              854  LOAD_CONST               None
              856  COMPARE_OP               is-not
          858_860  POP_JUMP_IF_FALSE   880  'to 880'

 L. 197       862  LOAD_FAST                'current_posture_state'
              864  LOAD_ATTR                right
              866  LOAD_FAST                'self'
              868  STORE_ATTR               _aspect_carry_right

 L. 198       870  LOAD_FAST                'current_posture_state'
              872  LOAD_ATTR                back
              874  LOAD_FAST                'self'
              876  STORE_ATTR               _aspect_carry_back
              878  JUMP_FORWARD        904  'to 904'
            880_0  COME_FROM           858  '858'

 L. 200       880  LOAD_FAST                '_get_default_carry_aspect'
              882  LOAD_GLOBAL              PostureTrack
              884  LOAD_ATTR                RIGHT
              886  CALL_FUNCTION_1       1  '1 positional argument'
              888  LOAD_FAST                'self'
              890  STORE_ATTR               _aspect_carry_right

 L. 201       892  LOAD_FAST                '_get_default_carry_aspect'
              894  LOAD_GLOBAL              PostureTrack
              896  LOAD_ATTR                BACK
              898  CALL_FUNCTION_1       1  '1 positional argument'
              900  LOAD_FAST                'self'
              902  STORE_ATTR               _aspect_carry_back
            904_0  COME_FROM           878  '878'
              904  JUMP_FORWARD       1422  'to 1422'
            906_0  COME_FROM           842  '842'

 L. 202       906  LOAD_FAST                'hand'
              908  LOAD_GLOBAL              Hand
              910  LOAD_ATTR                RIGHT
              912  COMPARE_OP               ==
          914_916  POP_JUMP_IF_FALSE   978  'to 978'

 L. 203       918  LOAD_FAST                'new_carry_aspect'
              920  LOAD_FAST                'self'
              922  STORE_ATTR               _aspect_carry_right

 L. 205       924  LOAD_FAST                'current_posture_state'
              926  LOAD_CONST               None
              928  COMPARE_OP               is-not
          930_932  POP_JUMP_IF_FALSE   952  'to 952'

 L. 206       934  LOAD_FAST                'current_posture_state'
              936  LOAD_ATTR                left
              938  LOAD_FAST                'self'
              940  STORE_ATTR               _aspect_carry_left

 L. 207       942  LOAD_FAST                'current_posture_state'
              944  LOAD_ATTR                back
              946  LOAD_FAST                'self'
              948  STORE_ATTR               _aspect_carry_back
              950  JUMP_FORWARD        976  'to 976'
            952_0  COME_FROM           930  '930'

 L. 209       952  LOAD_FAST                '_get_default_carry_aspect'
              954  LOAD_GLOBAL              PostureTrack
              956  LOAD_ATTR                LEFT
              958  CALL_FUNCTION_1       1  '1 positional argument'
              960  LOAD_FAST                'self'
              962  STORE_ATTR               _aspect_carry_left

 L. 210       964  LOAD_FAST                '_get_default_carry_aspect'
              966  LOAD_GLOBAL              PostureTrack
              968  LOAD_ATTR                BACK
              970  CALL_FUNCTION_1       1  '1 positional argument'
              972  LOAD_FAST                'self'
              974  STORE_ATTR               _aspect_carry_back
            976_0  COME_FROM           950  '950'
              976  JUMP_FORWARD       1422  'to 1422'
            978_0  COME_FROM           914  '914'

 L. 211       978  LOAD_FAST                'hand'
              980  LOAD_GLOBAL              Hand
              982  LOAD_ATTR                BACK
              984  COMPARE_OP               ==
          986_988  POP_JUMP_IF_FALSE  1050  'to 1050'

 L. 212       990  LOAD_FAST                'new_carry_aspect'
              992  LOAD_FAST                'self'
              994  STORE_ATTR               _aspect_carry_back

 L. 214       996  LOAD_FAST                'current_posture_state'
              998  LOAD_CONST               None
             1000  COMPARE_OP               is-not
         1002_1004  POP_JUMP_IF_FALSE  1024  'to 1024'

 L. 215      1006  LOAD_FAST                'current_posture_state'
             1008  LOAD_ATTR                left
             1010  LOAD_FAST                'self'
             1012  STORE_ATTR               _aspect_carry_left

 L. 216      1014  LOAD_FAST                'current_posture_state'
             1016  LOAD_ATTR                right
             1018  LOAD_FAST                'self'
             1020  STORE_ATTR               _aspect_carry_right
             1022  JUMP_FORWARD       1048  'to 1048'
           1024_0  COME_FROM          1002  '1002'

 L. 218      1024  LOAD_FAST                '_get_default_carry_aspect'
             1026  LOAD_GLOBAL              PostureTrack
             1028  LOAD_ATTR                LEFT
             1030  CALL_FUNCTION_1       1  '1 positional argument'
             1032  LOAD_FAST                'self'
             1034  STORE_ATTR               _aspect_carry_left

 L. 219      1036  LOAD_FAST                '_get_default_carry_aspect'
             1038  LOAD_GLOBAL              PostureTrack
             1040  LOAD_ATTR                RIGHT
             1042  CALL_FUNCTION_1       1  '1 positional argument'
             1044  LOAD_FAST                'self'
             1046  STORE_ATTR               _aspect_carry_right
           1048_0  COME_FROM          1022  '1022'
             1048  JUMP_FORWARD       1422  'to 1422'
           1050_0  COME_FROM           986  '986'

 L. 221      1050  LOAD_GLOBAL              RuntimeError
             1052  LOAD_STR                 'Invalid value specified for hand: {}'
             1054  LOAD_METHOD              format
             1056  LOAD_FAST                'hand'
             1058  CALL_METHOD_1         1  '1 positional argument'
             1060  CALL_FUNCTION_1       1  '1 positional argument'
             1062  RAISE_VARARGS_1       1  'exception instance'
         1064_1066  JUMP_FORWARD       1422  'to 1422'
           1068_0  COME_FROM           430  '430'
           1068_1  COME_FROM           420  '420'

 L. 224      1068  LOAD_FAST                'current_posture_state'
             1070  LOAD_CONST               None
             1072  COMPARE_OP               is-not
         1074_1076  POP_JUMP_IF_FALSE  1106  'to 1106'

 L. 225      1078  LOAD_FAST                'current_posture_state'
             1080  LOAD_ATTR                left
             1082  LOAD_FAST                'self'
             1084  STORE_ATTR               _aspect_carry_left

 L. 226      1086  LOAD_FAST                'current_posture_state'
             1088  LOAD_ATTR                right
             1090  LOAD_FAST                'self'
             1092  STORE_ATTR               _aspect_carry_right

 L. 227      1094  LOAD_FAST                'current_posture_state'
             1096  LOAD_ATTR                back
             1098  LOAD_FAST                'self'
             1100  STORE_ATTR               _aspect_carry_back
         1102_1104  JUMP_FORWARD       1422  'to 1422'
           1106_0  COME_FROM          1074  '1074'

 L. 229      1106  LOAD_FAST                'spec_carry_target'
             1108  LOAD_CONST               None
             1110  COMPARE_OP               is-not
         1112_1114  POP_JUMP_IF_FALSE  1386  'to 1386'

 L. 230      1116  LOAD_FAST                'var_map'
             1118  LOAD_FAST                'spec_carry_target'
             1120  BINARY_SUBSCR    
             1122  STORE_FAST               'carry_target'

 L. 231      1124  LOAD_FAST                'spec_carry'
             1126  LOAD_ATTR                posture_type
             1128  STORE_FAST               'spec_carry_posture_type'

 L. 232      1130  LOAD_FAST                'var_map'
             1132  LOAD_METHOD              get
             1134  LOAD_FAST                'spec_carry_posture_type'
             1136  CALL_METHOD_1         1  '1 positional argument'
             1138  STORE_FAST               'carry_posture_type'

 L. 233      1140  LOAD_FAST                'carry_posture_type'
             1142  LOAD_CONST               None
             1144  COMPARE_OP               is
         1146_1148  POP_JUMP_IF_FALSE  1198  'to 1198'

 L. 234      1150  LOAD_GLOBAL              get_carry_posture_aop
             1152  LOAD_DEREF               'sim'
             1154  LOAD_FAST                'carry_target'
             1156  LOAD_FAST                'var_map'
             1158  LOAD_GLOBAL              PostureSpecVariable
             1160  LOAD_ATTR                HAND
             1162  BINARY_SUBSCR    
             1164  LOAD_CONST               ('hand',)
             1166  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
             1168  STORE_FAST               'aop'

 L. 235      1170  LOAD_FAST                'aop'
             1172  LOAD_CONST               None
             1174  COMPARE_OP               is
         1176_1178  POP_JUMP_IF_FALSE  1190  'to 1190'
             1180  LOAD_FAST                'invalid_expected'
         1182_1184  POP_JUMP_IF_FALSE  1190  'to 1190'

 L. 236      1186  LOAD_CONST               None
             1188  RETURN_VALUE     
           1190_0  COME_FROM          1182  '1182'
           1190_1  COME_FROM          1176  '1176'

 L. 237      1190  LOAD_FAST                'aop'
             1192  LOAD_ATTR                affordance
             1194  LOAD_ATTR                _carry_posture_type
             1196  STORE_FAST               'carry_posture_type'
           1198_0  COME_FROM          1146  '1146'

 L. 239      1198  LOAD_FAST                'spec_carry'
             1200  LOAD_ATTR                hand
             1202  LOAD_FAST                'var_map'
             1204  COMPARE_OP               in
         1206_1208  POP_JUMP_IF_FALSE  1222  'to 1222'

 L. 240      1210  LOAD_FAST                'var_map'
             1212  LOAD_FAST                'spec_carry'
             1214  LOAD_ATTR                hand
             1216  BINARY_SUBSCR    
             1218  STORE_FAST               'hand'
             1220  JUMP_FORWARD       1240  'to 1240'
           1222_0  COME_FROM          1206  '1206'

 L. 242      1222  LOAD_FAST                'carry_target'
             1224  LOAD_METHOD              get_allowed_hands
             1226  LOAD_DEREF               'sim'
             1228  CALL_METHOD_1         1  '1 positional argument'
             1230  STORE_FAST               'allowed_hands'

 L. 243      1232  LOAD_FAST                'allowed_hands'
             1234  LOAD_CONST               0
             1236  BINARY_SUBSCR    
             1238  STORE_FAST               'hand'
           1240_0  COME_FROM          1220  '1220'

 L. 245      1240  LOAD_GLOBAL              postures
             1242  LOAD_ATTR                create_posture
             1244  LOAD_FAST                'carry_posture_type'

 L. 246      1246  LOAD_FAST                'self'
             1248  LOAD_ATTR                sim

 L. 247      1250  LOAD_FAST                'carry_target'

 L. 248      1252  LOAD_GLOBAL              hand_to_track
             1254  LOAD_FAST                'hand'
             1256  CALL_FUNCTION_1       1  '1 positional argument'

 L. 249      1258  LOAD_FAST                'is_throwaway'
           1260_0  COME_FROM           904  '904'
             1260  LOAD_CONST               ('track', 'is_throwaway')
             1262  CALL_FUNCTION_KW_5     5  '5 total positional and keyword args'
             1264  STORE_FAST               'new_carry_aspect'

 L. 250      1266  LOAD_FAST                'hand'
             1268  LOAD_GLOBAL              Hand
             1270  LOAD_ATTR                LEFT
             1272  COMPARE_OP               ==
         1274_1276  POP_JUMP_IF_FALSE  1310  'to 1310'

 L. 251      1278  LOAD_FAST                'new_carry_aspect'
             1280  LOAD_FAST                'self'
             1282  STORE_ATTR               _aspect_carry_left

 L. 252      1284  LOAD_FAST                '_get_default_carry_aspect'
             1286  LOAD_GLOBAL              PostureTrack
             1288  LOAD_ATTR                RIGHT
             1290  CALL_FUNCTION_1       1  '1 positional argument'
             1292  LOAD_FAST                'self'
             1294  STORE_ATTR               _aspect_carry_right

 L. 253      1296  LOAD_FAST                '_get_default_carry_aspect'
             1298  LOAD_GLOBAL              PostureTrack
             1300  LOAD_ATTR                BACK
             1302  CALL_FUNCTION_1       1  '1 positional argument'
             1304  LOAD_FAST                'self'
             1306  STORE_ATTR               _aspect_carry_back
             1308  JUMP_FORWARD       1384  'to 1384'
           1310_0  COME_FROM          1274  '1274'

 L. 254      1310  LOAD_FAST                'hand'
             1312  LOAD_GLOBAL              Hand
             1314  LOAD_ATTR                RIGHT
             1316  COMPARE_OP               ==
         1318_1320  POP_JUMP_IF_FALSE  1354  'to 1354'

 L. 255      1322  LOAD_FAST                'new_carry_aspect'
             1324  LOAD_FAST                'self'
             1326  STORE_ATTR               _aspect_carry_right

 L. 256      1328  LOAD_FAST                '_get_default_carry_aspect'
             1330  LOAD_GLOBAL              PostureTrack
           1332_0  COME_FROM           976  '976'
             1332  LOAD_ATTR                LEFT
             1334  CALL_FUNCTION_1       1  '1 positional argument'
             1336  LOAD_FAST                'self'
             1338  STORE_ATTR               _aspect_carry_left

 L. 257      1340  LOAD_FAST                '_get_default_carry_aspect'
             1342  LOAD_GLOBAL              PostureTrack
             1344  LOAD_ATTR                BACK
             1346  CALL_FUNCTION_1       1  '1 positional argument'
             1348  LOAD_FAST                'self'
             1350  STORE_ATTR               _aspect_carry_back
             1352  JUMP_FORWARD       1384  'to 1384'
           1354_0  COME_FROM          1318  '1318'

 L. 259      1354  LOAD_FAST                'new_carry_aspect'
             1356  LOAD_FAST                'self'
             1358  STORE_ATTR               _aspect_carry_back

 L. 260      1360  LOAD_FAST                '_get_default_carry_aspect'
             1362  LOAD_GLOBAL              PostureTrack
             1364  LOAD_ATTR                LEFT
             1366  CALL_FUNCTION_1       1  '1 positional argument'
             1368  LOAD_FAST                'self'
             1370  STORE_ATTR               _aspect_carry_left

 L. 261      1372  LOAD_FAST                '_get_default_carry_aspect'
             1374  LOAD_GLOBAL              PostureTrack
             1376  LOAD_ATTR                RIGHT
             1378  CALL_FUNCTION_1       1  '1 positional argument'
             1380  LOAD_FAST                'self'
             1382  STORE_ATTR               _aspect_carry_right
           1384_0  COME_FROM          1352  '1352'
           1384_1  COME_FROM          1308  '1308'
             1384  JUMP_FORWARD       1422  'to 1422'
           1386_0  COME_FROM          1112  '1112'

 L. 263      1386  LOAD_FAST                '_get_default_carry_aspect'
             1388  LOAD_GLOBAL              PostureTrack
             1390  LOAD_ATTR                LEFT
             1392  CALL_FUNCTION_1       1  '1 positional argument'
             1394  LOAD_FAST                'self'
             1396  STORE_ATTR               _aspect_carry_left

 L. 264      1398  LOAD_FAST                '_get_default_carry_aspect'
             1400  LOAD_GLOBAL              PostureTrack
             1402  LOAD_ATTR                RIGHT
           1404_0  COME_FROM          1048  '1048'
             1404  CALL_FUNCTION_1       1  '1 positional argument'
             1406  LOAD_FAST                'self'
             1408  STORE_ATTR               _aspect_carry_right

 L. 265      1410  LOAD_FAST                '_get_default_carry_aspect'
             1412  LOAD_GLOBAL              PostureTrack
             1414  LOAD_ATTR                BACK
             1416  CALL_FUNCTION_1       1  '1 positional argument'
             1418  LOAD_FAST                'self'
             1420  STORE_ATTR               _aspect_carry_back
           1422_0  COME_FROM          1384  '1384'
           1422_1  COME_FROM          1102  '1102'
           1422_2  COME_FROM          1064  '1064'

Parse error at or near `COME_FROM' instruction at offset 1260_0

    def __repr__(self):
        return standard_repr(self, *self.aspects)

    @property
    def valid(self):
        return self._valid and bool(self.constraint_intersection)

    @property
    def spec(self):
        return self._spec

    def get_posture_spec(self, var_map):
        if not var_map:
            return self._spec.clone
        else:
            carry_target = var_map.get(PostureSpecVariable.CARRY_TARGET)
            if carry_target is not None:
                if carry_target.definition is not carry_target:
                    carry_posture = self.get_carry_posture(carry_target)
                else:
                    carry_posture = None
            elif carry_posture is not None:
                if PostureSpecVariable.HAND in var_map:
                    required_hand = track_to_hand(carry_posture.track)
                    if required_hand != var_map[PostureSpecVariable.HAND]:
                        return
                source_carry = PostureAspectCarryPostureSpecVariable.POSTURE_TYPE_CARRY_OBJECTPostureSpecVariable.CARRY_TARGETPostureSpecVariable.HAND
            else:
                source_carry = PostureAspectCarryPostureSpecVariable.POSTURE_TYPE_CARRY_NOTHINGNonePostureSpecVariable.HAND
            surface_spec = self._spec.surface
            surface_target = surface_spec.target
            if surface_target is not None:
                var_map_surface_target = var_map.getPostureSpecVariable.SURFACE_TARGETNone
                if var_map_surface_target is None or surface_target == var_map_surface_target:
                    if carry_target is not None:
                        if carry_posture is None:
                            if carry_target.definition is not carry_target:
                                surface_spec = PostureAspectSurfacesurface_targetPostureSpecVariable.SLOTPostureSpecVariable.CARRY_TARGET
                                spec = self._spec.clone(carry=source_carry, surface=surface_spec)
                                if spec._validate_surface(var_map):
                                    if carry_target.parent is surface_target:
                                        return spec
                    interaction_target = var_map.getPostureSpecVariable.INTERACTION_TARGETPostureSpecVariable.INTERACTION_TARGET
                    if interaction_target is not None:
                        surface_spec = PostureAspectSurfacesurface_targetPostureSpecVariable.SLOTPostureSpecVariable.SLOT_TARGET
                        spec = self._spec.clone(carry=source_carry, surface=surface_spec)
                        if spec._validate_surface(var_map) and not isinstance(interaction_target, PostureSpecVariable):
                            if interaction_target.parent is surface_target:
                                return spec
                    surface_spec = PostureAspectSurfacesurface_targetPostureSpecVariable.SLOTNone
                    spec = self._spec.clone(carry=source_carry, surface=surface_spec)
                    if spec._validate_surface(var_map):
                        return spec
                surface_spec = PostureAspectSurfacesurface_targetNoneNone
                spec = self._spec.clone(carry=source_carry, surface=surface_spec)
                if spec._validate_surface(var_map):
                    return spec
        surface_spec = PostureAspectSurfaceNoneNoneNone
        spec = self._spec.clone(carry=source_carry, surface=surface_spec)
        if spec._validate_surface(var_map):
            return spec

    def _get_posture_constraint(self, strict=False):
        posture_state_constraint = self.body_posture_state_constraint
        posture_state_constraint = posture_state_constraint.get_holster_version
        if posture_state_constraint.valid:
            if not self.body_state_spec_only:
                carry_left_constraint = create_carry_constraint((self.left.target), (Hand.LEFT), strict=strict)
                posture_state_constraint = posture_state_constraint.intersect(carry_left_constraint)
                if posture_state_constraint.valid:
                    carry_right_constraint = create_carry_constraint((self.right.target), (Hand.RIGHT), strict=strict)
                    posture_state_constraint = posture_state_constraint.intersect(carry_right_constraint)
                    if posture_state_constraint.valid:
                        carry_back_constraint = create_carry_constraint((self.back.target), (Hand.BACK), strict=strict)
                        posture_state_constraint = posture_state_constraint.intersect(carry_back_constraint)
        return posture_state_constraint

    @property
    def posture_constraint(self):
        if self._posture_constraint is None:
            self._posture_constraint = self._get_posture_constraint
        return self._posture_constraint

    @property
    def posture_constraint_strict(self):
        if self._posture_constraint_strict is None:
            self._posture_constraint_strict = self._get_posture_constraint(strict=True)
        return self._posture_constraint_strict

    @property
    def sim(self):
        if self._sim_ref is not None:
            return self._sim_ref

    @property
    def linked_posture_state(self):
        return self._linked_posture_state

    @linked_posture_state.setter
    def linked_posture_state(self, posture_state):
        self._set_linked_posture_state(posture_state)
        posture_state._set_linked_posture_state(self)
        self.body.linked_posture = posture_state.body

    def _set_linked_posture_state(self, posture_state):
        self._linked_posture_state = posture_state

    @property
    def body(self):
        return self._aspect_body

    @property
    def left(self):
        return self._aspect_carry_left

    @property
    def right(self):
        return self._aspect_carry_right

    @property
    def back(self):
        return self._aspect_carry_back

    @property
    def aspects(self):
        if self.body_state_spec_only:
            return ()
        return (
         self.body, self.left, self.right, self.back)

    @property
    def carry_aspects(self):
        return (self.left, self.right, self.back)

    @property
    def surface_target(self):
        target = self._spec.surface.target
        if target is None or self.body.mobile:
            if self.body.target is not None:
                if self.body.target.is_surface:
                    return self.body.target
        return target

    @property
    def carry_targets(self):
        return (self.left.target, self.right.target, self.back.target)

    def get_aspect(self, track):
        if track == PostureTrack.BODY:
            return self.body
        if track == PostureTrack.LEFT:
            return self.left
        if track == PostureTrack.RIGHT:
            return self.right
        if track == PostureTrack.BACK:
            return self.back

    def add_constraint(self, handle, constraint):
        if not self._invalid_expected:
            if not constraint.valid:
                logger.warn('Attempt to add an invalid constraint {} to posture_state {}.', constraint, self, owner='bhill', trigger_breakpoint=True)
            test_constraint = self.constraint_intersection.intersect(constraint)
            if not test_constraint.valid:
                logger.warn'Attempt to add a constraint to {} which is incompatible with already-registered constraints: {} + {}.'selfconstraintself.constraint_intersection
        self._constraints[handle] = constraint
        self._constraint_intersection_dirty = True

    def remove_constraint(self, handle):
        if handle in self._constraints:
            del self._constraints[handle]
            self._constraint_intersection_dirty = True
            self._constraint_intersection = None

    @property
    def constraint_intersection(self):
        if self._constraint_intersection_dirty or self._constraint_intersection is None:
            intersection = Anywhere()
            for constraint in set(self._constraints.values):
                new_intersection = intersection.intersect(constraint)
                if not self._invalid_expected:
                    if not new_intersection.valid:
                        indent_text = '                '
                        logger.error('Invalid constraint intersection for PostureState: {}.\n    A: {} \n    A Geometry: {}    B: {} \n    B Geometry: {}', self, intersection, intersection.get_geometry_text(indent_text), constraint, constraint.get_geometry_text(indent_text))
                        intersection = new_intersection
                        break
                intersection = new_intersection

            self._constraint_intersection_dirty = False
            self._constraint_intersection = intersection
        return self._constraint_intersection

    def compatible_with(self, constraint):
        intersection = self.constraint_intersection
        if not intersection.valid:
            return False
        else:
            intersection = constraint.intersect(intersection)
            return intersection.valid or False
        return True

    def compatible_with_pre_resolve(self, constraint):
        for constraint_existing in self._constraints.values:
            if constraint_existing is constraint:
                return True

        return self.compatible_with(constraint)

    def get_slot_info(self):
        surface = self._spec.surface
        return (surface.target, surface.slot_type)

    def is_source_interaction(self, si):
        if si is not None:
            for aspect in self.aspects:
                if aspect.source_interaction is si:
                    return True

        return False

    def is_source_or_owning_interaction(self, si):
        return self.get_source_or_owned_posture_for_si(si) is not None

    def is_carry_source_or_owning_interaction(self, si):
        return self.get_source_or_owned_posture_for_si(si, carry_only=True) is not None

    def get_source_or_owned_posture_for_si(self, si, carry_only=False):
        if self.left.source_interaction is si or si in self.left.owning_interactions:
            return self.left
        if self.right.source_interaction is si or si in self.right.owning_interactions:
            return self.right
        if self.back.source_interaction is si or si in self.back.owning_interactions:
            return self.back
        if carry_only:
            return
        if self.body.source_interaction is si or si in self.body.owning_interactions:
            return self.body

    @property
    def connectivity_handles(self):
        if self.body.target is not None:
            return self.body.target.connectivity_handles

    def kickstart_gen(self, timeline, routing_surface, target_override=None):
        for aspect in self.aspects:
            yield from aspect.kickstart_gen(timeline, self, routing_surface, target_override=target_override)

        self._valid = True
        if False:
            yield None

    def on_reset(self, reset_reason):
        for aspect in self.aspects:
            aspect.reset

        self._valid = False

    def _carrying(self, track, **kwargs):
        if track == PostureTrack.LEFT:
            posture = self.left
        else:
            if track == PostureTrack.RIGHT:
                posture = self.right
            else:
                posture = self.back
        return (self._carrying_posture)(posture, **kwargs)

    def _carrying_posture(self, posture, ignore_target=None, only_target=None):
        if posture is not None:
            if posture.is_active_carry:
                if ignore_target is None:
                    if only_target is None:
                        return True
                else:
                    target = posture.target

                    def target_is(other):
                        if target is None:
                            return False
                        if isinstance(other, Tag):
                            return target.has_tag(other)
                        if isinstance(other, int):
                            return target.definition.id == other
                        if isinstance(other, Definition):
                            return target.definition is other
                        return target is other

                    if not (ignore_target is None or target_is(ignore_target)):
                        if only_target is None or target_is(only_target):
                            return True
        return False

    def get_carry_state(self, target=None, override_posture=None):
        if override_posture is not None:
            if override_posture.track == PostureTrack.LEFT:
                carry_state = (
                 self._carrying_posture(override_posture, ignore_target=target),
                 self._carrying((PostureTrack.RIGHT), ignore_target=target),
                 self._carrying((PostureTrack.BACK), ignore_target=target))
            elif override_posture.track == PostureTrack.RIGHT:
                carry_state = (
                 self._carrying((PostureTrack.LEFT), ignore_target=target),
                 self._carrying_posture(override_posture, ignore_target=target),
                 self._carrying((PostureTrack.BACK), ignore_target=target))
            else:
                carry_state = (
                 self._carrying((PostureTrack.LEFT), ignore_target=target),
                 self._carrying((PostureTrack.RIGHT), ignore_target=target),
                 self._carrying_posture(override_posture, ignore_target=target))
        else:
            carry_state = (
             self._carrying((PostureTrack.LEFT), ignore_target=target),
             self._carrying((PostureTrack.RIGHT), ignore_target=target),
             self._carrying((PostureTrack.BACK), ignore_target=target))
        return carry_state

    def get_carry_track(self, target):
        if target is None:
            return
        if self._carrying((PostureTrack.LEFT), only_target=target):
            return PostureTrack.LEFT
        if self._carrying((PostureTrack.RIGHT), only_target=target):
            return PostureTrack.RIGHT
        if self._carrying((PostureTrack.BACK), only_target=target):
            return PostureTrack.BACK

    def is_carrying(self, target):
        if self.get_carry_track(target) is not None:
            return True
        return False

    def get_carry_posture(self, target):
        if self.left.target is target:
            return self.left
        if self.right.target is target:
            return self.right
        if self.back.target is target:
            return self.back

    def get_posture_for_si(self, si):
        for posture in self.aspects:
            if posture is not None and posture.source_interaction == si:
                return posture

    def get_other_carry_posture(self, target):
        track = self.get_carry_track(target)
        if track is None:
            return
        elif track is PostureTrack.LEFT:
            result = self.get_aspect(PostureTrack.RIGHT)
        else:
            if track is PostureTrack.RIGHT:
                result = self.get_aspect(PostureTrack.LEFT)
            else:
                return
        if result is not None:
            if result.target is not None:
                return result

    def get_free_carry_track(self, obj=None) -> PostureTrack:
        if obj is not None:
            if obj.carryable_component is None:
                logger.error('Obj {} has no carryable component.', obj, owner='tastle')
                return
            elif obj is None:
                allowed_hands = (
                 Hand.RIGHT, Hand.LEFT, Hand.BACK)
            else:
                allowed_hands = obj.get_allowed_hands(self.sim)
            preferred_hand = self.sim.get_preferred_hand
            if preferred_hand == Hand.RIGHT:
                preferred_track = PostureTrack.RIGHT
                unpreferred_track = PostureTrack.LEFT
            else:
                preferred_track = PostureTrack.LEFT
                unpreferred_track = PostureTrack.RIGHT
            back_track = PostureTrack.BACK
            if track_to_hand(preferred_track) in allowed_hands:
                if not self._carrying(preferred_track):
                    return preferred_track
        else:
            if track_to_hand(unpreferred_track) in allowed_hands:
                if not self._carrying(unpreferred_track):
                    return unpreferred_track
            if track_to_hand(back_track) in allowed_hands:
                return self._carrying(back_track) or back_track

    def get_free_hands(self):
        free_hands = []
        if not self._carrying(PostureTrack.RIGHT):
            free_hands.append(Hand.RIGHT)
        if not self._carrying(PostureTrack.LEFT):
            free_hands.append(Hand.LEFT)
        if not self._carrying(PostureTrack.BACK):
            free_hands.append(Hand.BACK)
        return tuple(free_hands)