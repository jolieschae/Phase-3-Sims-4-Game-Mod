# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\weekly_schedule_zone_director.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 51796 bytes
import itertools
from _collections import defaultdict
from careers.career_event_zone_director import CareerEventZoneDirectorMixin
from date_and_time import create_date_and_time, create_time_span, DATE_AND_TIME_ZERO, sim_ticks_per_day, DateAndTime
from event_testing.resolver import GlobalResolver, SingleSimResolver, DoubleSimResolver
from event_testing.tests import TunableTestSet
from interactions import ParticipantType
from sims4 import random
from sims4.tuning.tunable import TunableList, TunableReference, TunableTuple, TunableInterval, TunableMapping, TunableEnumEntry, HasTunableReference, OptionalTunable, TunableRange, Tunable
from situations.bouncer.bouncer_types import RequestSpawningOption, BouncerRequestPriority
from situations.situation_guest_list import SituationGuestList, SituationGuestInfo
from situations.situation_serialization import GLOBAL_SITUATION_LINKED_SIM_ID
from tunable_multiplier import TunableMultiplier
from tunable_time import Days, TunableTimeOfDayMapping, TunableTimeOfDay
from zone_director import ZoneDirectorBase
import alarms, enum, sims4.tuning, services, sims4.resources
logger = sims4.log.Logger('WeeklyScheduleZoneDirector', default_owner='nabaker')

class UserFacingType(enum.Int):
    NEVER = 0
    ALWAYS = 1
    LINK_SELECTABLE_SIMS = 2
    LINK_CAREER_SIMS = 3


class WeeklyScheduleSituationData(HasTunableReference, metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SNIPPET)):
    INSTANCE_TUNABLES = {'situation':TunableReference(description='\n            Situation to run.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION)), 
     'user_facing':TunableEnumEntry(description='\n            NEVER: Never make user facing.\n            ALWAYS: Make user facing if at least 1 selectable sim in in situation.\n            LINK_SELECTABLE_SIMS: Make user facing and link to selectable sim if only 1 selectable sim is in the situation.\n            LINK_CAREER_SIMS: Make user facing and link to career sim if only 1 career sim is in the situation.\n            ',
       tunable_type=UserFacingType,
       default=UserFacingType.NEVER), 
     'job_assignments':TunableList(description='\n            List of jobs with associated test of sims who can fulfill that job and min/max number of\n            sims assigned to that job.\n            \n            Will make two passes attempting to assign instantiated sims to jobs.  The first pass will\n            assign instantiated sims that pass the test into jobs until the jobs meets the minimum requirements.\n            The second pass will assign instantiated sims into jobs until the job meets the maximum requirements.\n            ',
       tunable=TunableTuple(job=TunableReference(description='\n                    The situation job. \n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB))),
       tests=TunableTestSet(description='\n                    Tests used to determine if the instanced sim should be assigned to this job.\n                    '),
       sim_count=TunableInterval(description='\n                    Number of sims for this job.\n                    Minimum of 0 means job is optional.\n                    Will attempt to assign up to the max before moving on to next job/situation.\n                    ',
       tunable_type=int,
       default_lower=1,
       default_upper=1,
       minimum=0),
       upper_bound_count_modifiers=TunableList(description='\n                    Reduce Max sim count by 1 for every sim previously assigned (in this time period)\n                    to specified situation/job.\n                    ',
       tunable=TunableTuple(situation=TunableReference(description='\n                            The Situation.\n                            ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION))),
       job=TunableReference(description='\n                            The situation job. \n                            ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)))))))}

    @classmethod
    def _tuning_loaded_callback(cls):
        cls.default_job_order = []
        cls.default_met_minimum_jobs = {}
        cls.default_need_minimum_jobs = {}
        for entry in cls.job_assignments:
            cls.default_job_order.append(entry.job)
            if entry.sim_count.lower_bound == 0:
                cls.default_met_minimum_jobs[entry.job] = entry
            else:
                cls.default_need_minimum_jobs[entry.job] = entry

    @classmethod
    def try_start--- This code section failed: ---

 L. 136         0  LOAD_CONST               0
                2  STORE_FAST               'minimum_required_sims'

 L. 137         4  BUILD_MAP_0           0 
                6  STORE_FAST               'modified_upper_bounds'

 L. 138         8  LOAD_GLOBAL              len
               10  LOAD_FAST                'sims'
               12  CALL_FUNCTION_1       1  '1 positional argument'
               14  STORE_FAST               'num_sims'

 L. 141        16  LOAD_FAST                'cls'
               18  LOAD_ATTR                default_job_order
               20  LOAD_METHOD              copy
               22  CALL_METHOD_0         0  '0 positional arguments'
               24  STORE_FAST               'job_order'

 L. 143        26  SETUP_LOOP          180  'to 180'
               28  LOAD_FAST                'cls'
               30  LOAD_ATTR                job_assignments
               32  GET_ITER         
             34_0  COME_FROM           170  '170'
               34  FOR_ITER            178  'to 178'
               36  STORE_FAST               'entry'

 L. 144        38  LOAD_FAST                'entry'
               40  LOAD_ATTR                sim_count
               42  LOAD_ATTR                upper_bound
               44  STORE_FAST               'upper_bound'

 L. 145        46  LOAD_FAST                'entry'
               48  LOAD_ATTR                sim_count
               50  LOAD_ATTR                lower_bound
               52  STORE_FAST               'lower_bound'

 L. 146        54  SETUP_LOOP          146  'to 146'
               56  LOAD_FAST                'entry'
               58  LOAD_ATTR                upper_bound_count_modifiers
               60  GET_ITER         
             62_0  COME_FROM           136  '136'
               62  FOR_ITER            144  'to 144'
               64  STORE_FAST               'upper_bound_count_modifier'

 L. 147        66  LOAD_FAST                'upper_bound'
               68  LOAD_FAST                'situation_job_count'
               70  LOAD_FAST                'upper_bound_count_modifier'
               72  LOAD_ATTR                situation
               74  LOAD_FAST                'upper_bound_count_modifier'
               76  LOAD_ATTR                job
               78  BUILD_TUPLE_2         2 
               80  BINARY_SUBSCR    
               82  INPLACE_SUBTRACT 
               84  STORE_FAST               'upper_bound'

 L. 148        86  LOAD_FAST                'upper_bound'
               88  LOAD_CONST               0
               90  COMPARE_OP               <=
               92  POP_JUMP_IF_FALSE   130  'to 130'

 L. 150        94  LOAD_FAST                'lower_bound'
               96  LOAD_CONST               0
               98  COMPARE_OP               >
              100  POP_JUMP_IF_FALSE   106  'to 106'

 L. 151       102  LOAD_CONST               None
              104  RETURN_VALUE     
            106_0  COME_FROM           100  '100'

 L. 153       106  LOAD_FAST                'job_order'
              108  LOAD_METHOD              remove
              110  LOAD_FAST                'entry'
              112  LOAD_ATTR                job
              114  CALL_METHOD_1         1  '1 positional argument'
              116  POP_TOP          

 L. 155       118  LOAD_FAST                'job_order'
              120  POP_JUMP_IF_TRUE    126  'to 126'

 L. 156       122  LOAD_CONST               None
              124  RETURN_VALUE     
            126_0  COME_FROM           120  '120'

 L. 157       126  BREAK_LOOP       
              128  JUMP_BACK            62  'to 62'
            130_0  COME_FROM            92  '92'

 L. 159       130  LOAD_FAST                'upper_bound'
              132  LOAD_FAST                'lower_bound'
              134  COMPARE_OP               <
              136  POP_JUMP_IF_FALSE    62  'to 62'

 L. 160       138  LOAD_CONST               None
              140  RETURN_VALUE     
              142  JUMP_BACK            62  'to 62'
              144  POP_BLOCK        
            146_0  COME_FROM_LOOP       54  '54'

 L. 161       146  LOAD_FAST                'upper_bound'
              148  LOAD_FAST                'modified_upper_bounds'
              150  LOAD_FAST                'entry'
              152  LOAD_ATTR                job
              154  STORE_SUBSCR     

 L. 162       156  LOAD_FAST                'minimum_required_sims'
              158  LOAD_FAST                'lower_bound'
              160  INPLACE_ADD      
              162  STORE_FAST               'minimum_required_sims'

 L. 163       164  LOAD_FAST                'minimum_required_sims'
              166  LOAD_FAST                'num_sims'
              168  COMPARE_OP               >
              170  POP_JUMP_IF_FALSE    34  'to 34'

 L. 164       172  LOAD_CONST               None
              174  RETURN_VALUE     
              176  JUMP_BACK            34  'to 34'
              178  POP_BLOCK        
            180_0  COME_FROM_LOOP       26  '26'

 L. 166       180  LOAD_GLOBAL              defaultdict
              182  LOAD_GLOBAL              list
              184  CALL_FUNCTION_1       1  '1 positional argument'
              186  STORE_FAST               'job_assignments'

 L. 167       188  LOAD_GLOBAL              set
              190  CALL_FUNCTION_0       0  '0 positional arguments'
              192  STORE_FAST               'assigned_sims'

 L. 170       194  LOAD_FAST                'cls'
              196  LOAD_ATTR                default_need_minimum_jobs
              198  LOAD_METHOD              copy
              200  CALL_METHOD_0         0  '0 positional arguments'
              202  STORE_FAST               'need_minimum_jobs'

 L. 171       204  LOAD_FAST                'cls'
              206  LOAD_ATTR                default_met_minimum_jobs
              208  LOAD_METHOD              copy
              210  CALL_METHOD_0         0  '0 positional arguments'
              212  STORE_FAST               'met_minimum_jobs'

 L. 173   214_216  SETUP_LOOP          476  'to 476'
              218  LOAD_FAST                'sims'
              220  GET_ITER         
            222_0  COME_FROM           468  '468'
            222_1  COME_FROM           454  '454'
            222_2  COME_FROM           404  '404'
          222_224  FOR_ITER            474  'to 474'
              226  STORE_FAST               'sim'

 L. 174       228  LOAD_GLOBAL              DoubleSimResolver
              230  LOAD_FAST                'sim'
              232  LOAD_ATTR                sim_info
              234  LOAD_FAST                'sim_info'
              236  CALL_FUNCTION_2       2  '2 positional arguments'
              238  STORE_FAST               'resolver'

 L. 176       240  LOAD_CONST               None
              242  STORE_FAST               'assigned_job_entry'

 L. 178       244  SETUP_LOOP          398  'to 398'
              246  LOAD_FAST                'job_order'
              248  GET_ITER         
            250_0  COME_FROM           286  '286'
              250  FOR_ITER            336  'to 336'
              252  STORE_FAST               'job'

 L. 179       254  LOAD_FAST                'need_minimum_jobs'
              256  LOAD_METHOD              get
              258  LOAD_FAST                'job'
              260  CALL_METHOD_1         1  '1 positional argument'
              262  STORE_FAST               'job_entry'

 L. 180       264  LOAD_FAST                'job_entry'
              266  LOAD_CONST               None
              268  COMPARE_OP               is
          270_272  POP_JUMP_IF_FALSE   276  'to 276'

 L. 181       274  CONTINUE            250  'to 250'
            276_0  COME_FROM           270  '270'

 L. 182       276  LOAD_FAST                'job_entry'
              278  LOAD_ATTR                tests
              280  LOAD_METHOD              run_tests
              282  LOAD_FAST                'resolver'
              284  CALL_METHOD_1         1  '1 positional argument'
              286  POP_JUMP_IF_FALSE   250  'to 250'

 L. 183       288  LOAD_FAST                'job_entry'
              290  STORE_FAST               'assigned_job_entry'

 L. 184       292  LOAD_GLOBAL              len
              294  LOAD_FAST                'job_assignments'
              296  LOAD_FAST                'job'
              298  BINARY_SUBSCR    
              300  CALL_FUNCTION_1       1  '1 positional argument'
              302  LOAD_CONST               1
              304  BINARY_ADD       
              306  LOAD_FAST                'job_entry'
              308  LOAD_ATTR                sim_count
              310  LOAD_ATTR                lower_bound
              312  COMPARE_OP               >=
          314_316  POP_JUMP_IF_FALSE   332  'to 332'

 L. 185       318  LOAD_FAST                'job_entry'
              320  LOAD_FAST                'met_minimum_jobs'
              322  LOAD_FAST                'job'
              324  STORE_SUBSCR     

 L. 186       326  LOAD_FAST                'need_minimum_jobs'
              328  LOAD_FAST                'job'
              330  DELETE_SUBSCR    
            332_0  COME_FROM           314  '314'

 L. 187       332  BREAK_LOOP       
              334  JUMP_BACK           250  'to 250'
              336  POP_BLOCK        

 L. 191       338  SETUP_LOOP          398  'to 398'
              340  LOAD_FAST                'job_order'
              342  GET_ITER         
            344_0  COME_FROM           382  '382'
              344  FOR_ITER            396  'to 396'
              346  STORE_FAST               'job'

 L. 192       348  LOAD_FAST                'met_minimum_jobs'
              350  LOAD_METHOD              get
              352  LOAD_FAST                'job'
              354  CALL_METHOD_1         1  '1 positional argument'
              356  STORE_FAST               'job_entry'

 L. 193       358  LOAD_FAST                'job_entry'
              360  LOAD_CONST               None
              362  COMPARE_OP               is
          364_366  POP_JUMP_IF_FALSE   372  'to 372'

 L. 194   368_370  CONTINUE            344  'to 344'
            372_0  COME_FROM           364  '364'

 L. 195       372  LOAD_FAST                'job_entry'
              374  LOAD_ATTR                tests
              376  LOAD_METHOD              run_tests
              378  LOAD_FAST                'resolver'
              380  CALL_METHOD_1         1  '1 positional argument'
          382_384  POP_JUMP_IF_FALSE   344  'to 344'

 L. 196       386  LOAD_FAST                'job_entry'
              388  STORE_FAST               'assigned_job_entry'

 L. 197       390  BREAK_LOOP       
          392_394  JUMP_BACK           344  'to 344'
              396  POP_BLOCK        
            398_0  COME_FROM_LOOP      338  '338'
            398_1  COME_FROM_LOOP      244  '244'

 L. 202       398  LOAD_FAST                'assigned_job_entry'
              400  LOAD_CONST               None
              402  COMPARE_OP               is-not
              404  POP_JUMP_IF_FALSE   222  'to 222'

 L. 203       406  LOAD_FAST                'assigned_job_entry'
              408  LOAD_ATTR                job
              410  STORE_FAST               'job'

 L. 204       412  LOAD_FAST                'job_assignments'
              414  LOAD_FAST                'job'
              416  BINARY_SUBSCR    
              418  LOAD_METHOD              append
              420  LOAD_FAST                'sim'
              422  CALL_METHOD_1         1  '1 positional argument'
              424  POP_TOP          

 L. 205       426  LOAD_FAST                'assigned_sims'
              428  LOAD_METHOD              add
              430  LOAD_FAST                'sim'
              432  CALL_METHOD_1         1  '1 positional argument'
              434  POP_TOP          

 L. 206       436  LOAD_GLOBAL              len
              438  LOAD_FAST                'job_assignments'
              440  LOAD_FAST                'job'
              442  BINARY_SUBSCR    
              444  CALL_FUNCTION_1       1  '1 positional argument'
              446  LOAD_FAST                'modified_upper_bounds'
              448  LOAD_FAST                'job'
              450  BINARY_SUBSCR    
              452  COMPARE_OP               >=
              454  POP_JUMP_IF_FALSE   222  'to 222'

 L. 207       456  LOAD_FAST                'job_order'
              458  LOAD_METHOD              remove
              460  LOAD_FAST                'job'
              462  CALL_METHOD_1         1  '1 positional argument'
              464  POP_TOP          

 L. 208       466  LOAD_FAST                'job_order'
              468  POP_JUMP_IF_TRUE    222  'to 222'

 L. 209       470  BREAK_LOOP       
              472  JUMP_BACK           222  'to 222'
              474  POP_BLOCK        
            476_0  COME_FROM_LOOP      214  '214'

 L. 212       476  LOAD_FAST                'need_minimum_jobs'
          478_480  POP_JUMP_IF_FALSE   486  'to 486'

 L. 213       482  LOAD_CONST               None
              484  RETURN_VALUE     
            486_0  COME_FROM           478  '478'

 L. 215       486  LOAD_FAST                'sim_info'
              488  LOAD_CONST               None
              490  COMPARE_OP               is
          492_494  POP_JUMP_IF_FALSE   502  'to 502'

 L. 216       496  LOAD_CONST               None
              498  STORE_FAST               'requesting_sim_id'
              500  JUMP_FORWARD        508  'to 508'
            502_0  COME_FROM           492  '492'

 L. 218       502  LOAD_FAST                'sim_info'
              504  LOAD_ATTR                sim_id
              506  STORE_FAST               'requesting_sim_id'
            508_0  COME_FROM           500  '500'

 L. 219       508  LOAD_GLOBAL              SituationGuestList

 L. 220       510  LOAD_CONST               True

 L. 221       512  LOAD_FAST                'requesting_sim_id'
              514  LOAD_CONST               ('invite_only', 'filter_requesting_sim_id')
              516  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              518  STORE_FAST               'guest_list'

 L. 223       520  BUILD_LIST_0          0 
              522  STORE_FAST               'sim_ids_of_interest'

 L. 224       524  SETUP_LOOP          650  'to 650'
              526  LOAD_FAST                'job_assignments'
              528  LOAD_METHOD              items
              530  CALL_METHOD_0         0  '0 positional arguments'
              532  GET_ITER         
              534  FOR_ITER            648  'to 648'
              536  UNPACK_SEQUENCE_2     2 
              538  STORE_FAST               'job'
              540  STORE_FAST               'sim_list'

 L. 225       542  SETUP_LOOP          644  'to 644'
              544  LOAD_FAST                'sim_list'
              546  GET_ITER         
            548_0  COME_FROM           622  '622'
              548  FOR_ITER            642  'to 642'
              550  STORE_FAST               'sim'

 L. 226       552  LOAD_FAST                'guest_list'
              554  LOAD_METHOD              add_guest_info
              556  LOAD_GLOBAL              SituationGuestInfo
              558  LOAD_FAST                'sim'
              560  LOAD_ATTR                sim_id

 L. 227       562  LOAD_FAST                'job'

 L. 228       564  LOAD_GLOBAL              RequestSpawningOption
              566  LOAD_ATTR                DONT_CARE

 L. 229       568  LOAD_GLOBAL              BouncerRequestPriority
              570  LOAD_ATTR                EVENT_VIP
              572  CALL_FUNCTION_4       4  '4 positional arguments'
              574  CALL_METHOD_1         1  '1 positional argument'
              576  POP_TOP          

 L. 230       578  LOAD_FAST                'cls'
              580  LOAD_ATTR                user_facing
              582  LOAD_GLOBAL              UserFacingType
              584  LOAD_ATTR                LINK_CAREER_SIMS
              586  COMPARE_OP               ==
          588_590  POP_JUMP_IF_FALSE   618  'to 618'

 L. 231       592  LOAD_FAST                'sim'
              594  LOAD_ATTR                sim_id
              596  LOAD_FAST                'additional_sim_ids'
              598  COMPARE_OP               in
          600_602  POP_JUMP_IF_FALSE   638  'to 638'

 L. 232       604  LOAD_FAST                'sim_ids_of_interest'
              606  LOAD_METHOD              append
              608  LOAD_FAST                'sim'
              610  LOAD_ATTR                sim_id
              612  CALL_METHOD_1         1  '1 positional argument'
              614  POP_TOP          
              616  JUMP_BACK           548  'to 548'
            618_0  COME_FROM           588  '588'

 L. 233       618  LOAD_FAST                'sim'
              620  LOAD_ATTR                is_selectable
          622_624  POP_JUMP_IF_FALSE   548  'to 548'

 L. 234       626  LOAD_FAST                'sim_ids_of_interest'
              628  LOAD_METHOD              append
              630  LOAD_FAST                'sim'
              632  LOAD_ATTR                sim_id
              634  CALL_METHOD_1         1  '1 positional argument'
              636  POP_TOP          
            638_0  COME_FROM           600  '600'
          638_640  JUMP_BACK           548  'to 548'
              642  POP_BLOCK        
            644_0  COME_FROM_LOOP      542  '542'
          644_646  JUMP_BACK           534  'to 534'
              648  POP_BLOCK        
            650_0  COME_FROM_LOOP      524  '524'

 L. 237       650  LOAD_FAST                'guest_list'
          652_654  POP_JUMP_IF_TRUE    660  'to 660'

 L. 238       656  LOAD_CONST               None
              658  RETURN_VALUE     
            660_0  COME_FROM           652  '652'

 L. 241       660  LOAD_FAST                'cls'
              662  LOAD_ATTR                user_facing
              664  LOAD_GLOBAL              UserFacingType
              666  LOAD_ATTR                NEVER
              668  COMPARE_OP               ==
          670_672  POP_JUMP_IF_FALSE   684  'to 684'

 L. 242       674  LOAD_GLOBAL              GLOBAL_SITUATION_LINKED_SIM_ID
              676  STORE_FAST               'linked_sim_id'

 L. 243       678  LOAD_CONST               False
              680  STORE_FAST               'user_facing'
              682  JUMP_FORWARD        748  'to 748'
            684_0  COME_FROM           670  '670'

 L. 244       684  LOAD_FAST                'cls'
              686  LOAD_ATTR                user_facing
              688  LOAD_GLOBAL              UserFacingType
              690  LOAD_ATTR                ALWAYS
              692  COMPARE_OP               ==
          694_696  POP_JUMP_IF_FALSE   712  'to 712'

 L. 245       698  LOAD_GLOBAL              GLOBAL_SITUATION_LINKED_SIM_ID
              700  STORE_FAST               'linked_sim_id'

 L. 246       702  LOAD_GLOBAL              bool
              704  LOAD_FAST                'sim_ids_of_interest'
              706  CALL_FUNCTION_1       1  '1 positional argument'
              708  STORE_FAST               'user_facing'
              710  JUMP_FORWARD        748  'to 748'
            712_0  COME_FROM           694  '694'

 L. 247       712  LOAD_GLOBAL              len
              714  LOAD_FAST                'sim_ids_of_interest'
              716  CALL_FUNCTION_1       1  '1 positional argument'
              718  LOAD_CONST               1
              720  COMPARE_OP               ==
          722_724  POP_JUMP_IF_FALSE   740  'to 740'

 L. 248       726  LOAD_FAST                'sim_ids_of_interest'
              728  LOAD_CONST               0
              730  BINARY_SUBSCR    
              732  STORE_FAST               'linked_sim_id'

 L. 249       734  LOAD_CONST               True
              736  STORE_FAST               'user_facing'
              738  JUMP_FORWARD        748  'to 748'
            740_0  COME_FROM           722  '722'

 L. 251       740  LOAD_GLOBAL              GLOBAL_SITUATION_LINKED_SIM_ID
              742  STORE_FAST               'linked_sim_id'

 L. 252       744  LOAD_CONST               False
              746  STORE_FAST               'user_facing'
            748_0  COME_FROM           738  '738'
            748_1  COME_FROM           710  '710'
            748_2  COME_FROM           682  '682'

 L. 255       748  LOAD_GLOBAL              services
              750  LOAD_METHOD              get_zone_situation_manager
              752  CALL_METHOD_0         0  '0 positional arguments'
              754  STORE_FAST               'situation_manager'

 L. 256       756  LOAD_FAST                'situation_manager'
              758  LOAD_ATTR                create_situation

 L. 257       760  LOAD_FAST                'cls'
              762  LOAD_ATTR                situation

 L. 258       764  LOAD_FAST                'user_facing'

 L. 259       766  LOAD_FAST                'duration'

 L. 260       768  LOAD_FAST                'guest_list'

 L. 261       770  LOAD_CONST               True

 L. 262       772  LOAD_FAST                'linked_sim_id'

 L. 263       774  LOAD_GLOBAL              str
              776  LOAD_FAST                'cls'
              778  CALL_FUNCTION_1       1  '1 positional argument'
              780  LOAD_CONST               ('user_facing', 'duration_override', 'guest_list', 'spawn_sims_during_zone_spin_up', 'linked_sim_id', 'creation_source')
              782  CALL_FUNCTION_KW_7     7  '7 total positional and keyword args'
              784  STORE_FAST               'situation_id'

 L. 266       786  LOAD_FAST                'situation_id'
              788  LOAD_CONST               None
              790  COMPARE_OP               is-not
          792_794  POP_JUMP_IF_FALSE   856  'to 856'

 L. 267       796  LOAD_FAST                'sims'
              798  LOAD_METHOD              difference_update
              800  LOAD_FAST                'assigned_sims'
              802  CALL_METHOD_1         1  '1 positional argument'
              804  POP_TOP          

 L. 268       806  SETUP_LOOP          856  'to 856'
              808  LOAD_FAST                'job_assignments'
              810  LOAD_METHOD              items
              812  CALL_METHOD_0         0  '0 positional arguments'
              814  GET_ITER         
              816  FOR_ITER            854  'to 854'
              818  UNPACK_SEQUENCE_2     2 
              820  STORE_FAST               'job'
              822  STORE_FAST               'sim_list'

 L. 269       824  LOAD_FAST                'situation_job_count'
              826  LOAD_FAST                'cls'
              828  LOAD_ATTR                situation
              830  LOAD_FAST                'job'
              832  BUILD_TUPLE_2         2 
              834  DUP_TOP_TWO      
              836  BINARY_SUBSCR    
              838  LOAD_GLOBAL              len
              840  LOAD_FAST                'sim_list'
              842  CALL_FUNCTION_1       1  '1 positional argument'
              844  INPLACE_ADD      
              846  ROT_THREE        
              848  STORE_SUBSCR     
          850_852  JUMP_BACK           816  'to 816'
              854  POP_BLOCK        
            856_0  COME_FROM_LOOP      806  '806'
            856_1  COME_FROM           792  '792'

 L. 270       856  LOAD_FAST                'situation_id'
              858  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM_LOOP' instruction at offset 476_0


class WeeklyScheduleSituationSet(HasTunableReference, metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SNIPPET)):
    INSTANCE_TUNABLES = {'required_situations':TunableList(description='\n            Situations that will always attempt to run as long as required jobs are sufficiently filled.\n            ',
       tunable=TunableTuple(situation_data=WeeklyScheduleSituationData.TunableReference(description='\n                    The situation data to run.\n                    '),
       max_created=OptionalTunable(description='\n                    Maximum number of this situation to create.\n                    ',
       tunable=TunableTuple(count=TunableRange(description='\n                            Maximum number of this situation to create.\n                            ',
       tunable_type=int,
       default=1,
       minimum=1),
       count_modifiers=TunableList(description='\n                            Reduce number of situations by 1 for every sim previously assigned (in this time period)\n                            to specified situation/job.\n                            ',
       tunable=TunableTuple(situation=TunableReference(description='\n                                    The Situation.\n                                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION))),
       job=TunableReference(description='\n                                    The situation job. \n                                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)))))),
       enabled_by_default=True,
       disabled_name='unlimited',
       enabled_name='limited'))), 
     'random_situations':TunableList(description='\n            Situations in which remaining instantiated sims will attempt to be placed\n            ',
       tunable=TunableTuple(weight=TunableMultiplier.TunableFactory(description='\n                    Weight for this situation. Used for random selection until all\n                    available sims are used.\n                    '),
       situation_data=WeeklyScheduleSituationData.TunableReference(description='\n                    The situation data to run.\n                    '))), 
     'start_on_time_loot':TunableList(description="\n             A list of loot operations that will be given if the situation set\n             starts at the beginning of it's scheduled time.  (i.e. Didn't \n             travel to the lot mid period.)\n             ",
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True)), 
     'start_any_time_loot':TunableList(description="\n             A list of loot operations that will be given when this situation \n             set starts regardless of whether it's at the start.  (i.e. Even if \n             user travelled to the lot mid period.)\n             ",
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True))}

    @classmethod
    def start(cls, resolver, sim_info, duration, additional_sim_ids, sims=None, start=True, on_time=False, delayed_loots=None):
        started_situation_ids = []
        if sims is None:
            sims = set(services.sim_info_manager.instanced_sims_gen)
        situation_job_count = defaultdict(int)
        for situation_data_info in cls.required_situations:
            max_created = situation_data_info.max_created
            if max_created is not None:
                count = max_created.count
                for count_modifier in max_created.count_modifiers:
                    count -= situation_job_count[(count_modifier.situation, count_modifier.job)]

            while not max_created is None:
                if count > 0:
                    situation_id = situation_data_info.situation_data.try_start(sims, sim_info, duration, additional_sim_ids, situation_job_count)
                    if situation_id is not None:
                        if max_created is not None:
                            count -= 1
                        started_situation_ids.append(situation_id)
                        if not sims:
                            break
                else:
                    break

            if not sims:
                break

        if sims:
            weighted_options = []
            for entry in cls.random_situations:
                weight = entry.weight.get_multiplier(resolver)
                if weight > 0:
                    weighted_options.append((weight, entry.situation_data))

            while sims and weighted_options:
                situation_data = sims4.random.pop_weighted(weighted_options)
                situation_id = situation_data.try_start(sims, sim_info, duration, additional_sim_ids, situation_job_count)
                if situation_id is not None:
                    started_situation_ids.append(situation_id)

        if start:
            for loot_action in cls.start_any_time_loot:
                if delayed_loots is not None:
                    delayed_loots.append(loot_action)
                else:
                    loot_action.apply_to_resolver(resolver)

            if on_time:
                for loot_action in cls.start_on_time_loot:
                    if delayed_loots is not None:
                        delayed_loots.append(loot_action)
                    else:
                        loot_action.apply_to_resolver(resolver)

        return started_situation_ids


class WeeklyScheduleDay(HasTunableReference, metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SNIPPET)):
    INSTANCE_TUNABLES = {'schedule':TunableTimeOfDayMapping.TunableFactory(description='\n            Each entry in the map has 3 columns. The first column is\n            the hour of the day (0-24), 2nd column is minute of that hour, and\n            the third maps to a weighted selection of situations for that time slot.\n            \n            The entry with starting hour that is closest to, but before\n            the current hour will be chosen.\n            \n            Given this tuning: \n                hour_of_day           possible situation sets\n                6                     [(w1, s1), (w2, s2)]\n                10                    [(w1, s2)]\n                14                    [(w2, s5)]\n                20                    [(w9, s0)]\n                \n            If the current hour is 11, hour_of_day will be 10 and desired is [(w1, s2)].\n            If the current hour is 19, hour_of_day will be 14 and desired is [(w2, s5)].\n            If the current hour is 23, hour_of_day will be 20 and desired is [(w9, s0)].\n            If the current hour is 2, hour_of_day will be 20 and desired is [(w9, s0)]. (uses 20 tuning because it is not 6 yet)\n            \n            The entries will be automatically sorted by time.\n            ',
       hours={'value_name':'Situation_sets', 
      'value_type':TunableList(tunable=TunableTuple(weight=TunableMultiplier.TunableFactory(description='\n                            Weight for this set of situations.\n                            '),
        situation_set=WeeklyScheduleSituationSet.TunableReference(description='\n                            Set of situations for this time period.\n                            ')))}), 
     'long_term_situations':TunableList(description='\n            Long term situations that exist outside the schedule.\n            ',
       tunable=TunableTuple(situation=TunableReference(description='\n                    Situation to run.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION)),
       pack_safe=True),
       start_time=TunableTimeOfDay(description='\n                    Time when this situation should start running.\n                    '),
       stop_time=TunableTimeOfDay(description='\n                    Time when this situation should stop running. 0:00 means\n                    should stop at end of day midnight.\n                    '),
       count=TunableInterval(description='\n                    Number of this situation to spin up.\n                    ',
       tunable_type=int,
       default_lower=1,
       default_upper=1,
       minimum=0),
       count_modifiers=TunableList(description='\n                    For each sim/siminfo that is a valid participant that \n                    passes the test, reduce max and min count by 1.\n                      \n                    Participant based on SingleSimResolver \n                    using either sim in career event or active sim.\n                    ',
       tunable=TunableTuple(subject=TunableEnumEntry(description='\n                            Who or what to apply this test to.\n                            ',
       tunable_type=ParticipantType,
       default=(ParticipantType.Actor)),
       tests=TunableTestSet(description='\n                            Tests used to determine if specified participant(s)\n                            should be counted.\n                            ')))))}
    MIN_COUNT_INDEX = 0
    MAX_COUNT_INDEX = 1
    SITUATION_INDEX = 2

    @classmethod
    def get_current_situation_sets(cls):
        return cls.schedule.get_entry_data(services.time_service.sim_now + create_time_span(minutes=1))

    @classmethod
    def start_situations(cls, situation_sets, resolver, sim_info, duration, additional_sim_ids, on_time, delayed_loots=None):
        weighted_options = [(entry.weight.get_multiplier(resolver), entry.situation_set) for entry in situation_sets]
        situation_set = sims4.random.weighted_random_item(weighted_options)
        return (situation_set.start(resolver, sim_info, duration, additional_sim_ids, on_time=on_time, delayed_loots=delayed_loots), situation_set)

    @classmethod
    def start_long_term_situation(cls, situation, start_time, stop_time, min_count, max_count, requesting_sim_info, situation_ids):
        now = services.time_service.sim_now.time_of_day
        time_span = now.time_till_next_day_time(stop_time, rollover_same_time=True)
        duration = time_span.in_minutes
        if requesting_sim_info is None:
            requesting_sim_id = None
        else:
            requesting_sim_id = requesting_sim_info.sim_id
        situation_manager = services.get_zone_situation_manager
        for _ in range(random.random.randint(min_count, max_count)):
            guest_list = SituationGuestList(filter_requesting_sim_id=requesting_sim_id)
            situation_id = situation_manager.create_situation(situation, guest_list=guest_list,
              spawn_sims_during_zone_spin_up=True,
              user_facing=False,
              duration_override=duration,
              creation_source=(str(cls)))
            if situation_id is not None:
                situation_ids.append(situation_id)

    @classmethod
    def get_long_term_situation_count(cls, long_term_situation_data, resolver):
        min_count = long_term_situation_data.count.lower_bound
        max_count = long_term_situation_data.count.upper_bound
        valid_sim_infos = set
        for count_modifier in long_term_situation_data.count_modifiers:
            for sim in resolver.get_participants(count_modifier.subject):
                test_resolver = SingleSimResolver(sim.sim_info)
                if count_modifier.tests.run_tests(test_resolver):
                    valid_sim_infos.add(sim.sim_info)

        delta = len(valid_sim_infos)
        max_count -= delta
        min_count -= delta
        if min_count < 0:
            min_count = 0
        return (
         min_count, max_count)

    @classmethod
    def request_new_long_term_situations(cls, time_to_start, resolver, requesting_sim_info, situation_ids):
        next_time = DATE_AND_TIME_ZERO + create_time_span(hours=24)
        for long_term_situation_data in cls.long_term_situations:
            if long_term_situation_data.start_time != time_to_start:
                if time_to_start < long_term_situation_data.start_time < next_time:
                    next_time = long_term_situation_data.start_time
                    continue
                min_count, max_count = cls.get_long_term_situation_count(long_term_situation_data, resolver)
                if max_count <= 0:
                    continue
                cls.start_long_term_situation(long_term_situation_data.situation, long_term_situation_data.start_time, long_term_situation_data.stop_time, min_count, max_count, requesting_sim_info, situation_ids)

        return next_time

    @classmethod
    def get_expected_situations(cls, resolver):
        now = services.time_service.sim_now.time_of_day
        next_time = DATE_AND_TIME_ZERO + create_time_span(hours=24)
        expected_situations = {}
        for long_term_situation_data in cls.long_term_situations:
            stop_time = long_term_situation_data.stop_time
            start_time = long_term_situation_data.start_time
            if now > stop_time:
                if stop_time != DATE_AND_TIME_ZERO:
                    continue
                elif now < start_time:
                    if start_time < next_time:
                        next_time = start_time
                        continue
                    min_count, max_count = cls.get_long_term_situation_count(long_term_situation_data, resolver)
                    if max_count <= 0:
                        continue
                    guid = long_term_situation_data.situation.guid64
                    situation_times = expected_situations.get(guid)
                    if situation_times is None:
                        situation_times = {}
                        expected_situations[guid] = situation_times
                        situation_datas = None
                else:
                    situation_datas = situation_times.get(stop_time)
                if situation_datas is not None:
                    situation_datas[cls.MIN_COUNT_INDEX] += min_count
                    situation_datas[cls.MAX_COUNT_INDEX] += max_count
                else:
                    situation_times[stop_time] = [
                     min_count, max_count, long_term_situation_data.situation]

        return (
         expected_situations, next_time)

    @classmethod
    def request_initial_long_term_situations(cls, resolver, requesting_sim_info, existing_ids):
        requested_situations, next_time = cls.get_expected_situations(resolver)
        situation_manager = services.get_zone_situation_manager
        now = services.time_service.sim_now.time_of_day
        was_existing = bool(existing_ids)
        existing_situations = [situation_manager.get(uid) for uid in existing_ids if uid in situation_manager]
        existing_ids.clear
        while existing_situations:
            situation = existing_situations.pop
            situation_times = requested_situations.get(situation.guid64)
            if situation_times is None:
                situation_manager.destroy_situation_by_id(situation.id)
                continue
            closest_time = None
            closest_ticks = sim_ticks_per_day * 2
            closest_situation_data = None
            for time, situation_data in situation_times.items:
                new_ticks = abs((now + situation.get_remaining_time - time).in_ticks)
                if new_ticks < closest_ticks:
                    closest_ticks = new_ticks
                    closest_time = time
                    closest_situation_data = situation_data

            closest_situation_data[cls.MIN_COUNT_INDEX] -= 1
            if closest_situation_data[cls.MAX_COUNT_INDEX] == 1:
                del situation_times[closest_time]
                if not situation_times:
                    del requested_situations[situation.guid64]
            closest_situation_data[cls.MAX_COUNT_INDEX] -= 1
            situation.change_duration(now.time_till_next_day_time(closest_time).in_minutes)
            existing_ids.append(situation.id)

        for _, situation_times in requested_situations.items:
            for time, situation_data in situation_times.items:
                if was_existing:
                    if situation_data[cls.MIN_COUNT_INDEX] < 1:
                        continue
                cls.start_long_term_situation(situation_data[cls.SITUATION_INDEX], now, time, situation_data[cls.MIN_COUNT_INDEX], situation_data[cls.MIN_COUNT_INDEX] if was_existing else situation_data[cls.MAX_COUNT_INDEX], requesting_sim_info, existing_ids)

        return next_time


class WeeklyScheduleZoneDirector(CareerEventZoneDirectorMixin, ZoneDirectorBase):
    SCHEDULE_SPINUP_DELAY = 5
    SCHEDULED_SITUATION_LIST_GUID = 4213659598
    LONG_TERM_SITUATION_LIST_GUID = 1568893620
    CURRENT_HOUR_TOKEN = 'current_hour'
    CURRENT_DAY_TOKEN = 'current_day'
    SCHEDULE_GUID_TOKEN = 'schedule_guid'
    SITUATION_SET_GUID_TOKEN = 'situation_set_guid'
    INSTANCE_TUNABLES = {'scheduled_situations':TunableMapping(description='\n            Mapping of week to possible schedule of situations for that day of the week.\n            ',
       key_type=TunableEnumEntry(description='\n                Day of the week.\n                ',
       tunable_type=Days,
       default=(Days.SUNDAY)),
       value_type=TunableList(tunable=TunableTuple(weight=TunableMultiplier.TunableFactory(description='\n                        Weight for this daily schedule.\n                        '),
       schedule=WeeklyScheduleDay.TunableReference(description='\n                        A schedule for the day.\n                        ')))), 
     'allow_open_street_director':Tunable(description="\n            When set this will allow a weekly schedule zone director to start an open street \n            director. However if this is False then the open street zone director won't start up\n            and that can lead to things like seasonal conditional layers not spawning and such.\n            ",
       tunable_type=bool,
       default=False)}

    def __init__(self, *args, **kwargs):
        (super.__init__)(*args, **kwargs)
        self._long_term_situation_ids = list
        self._situation_ids = []
        self._long_term_situation_alarm_handle = None
        self._situation_alarm_handle = None
        self._schedule = None
        self._situation_set = None
        self._current_hour = None
        self._current_day = None
        self._next_long_term_time = None
        self._delayed_loots = []

    def on_startup(self):
        super.on_startup
        if services.current_zone.is_zone_running:
            self._on_scheduled_situation_request
            services.sim_spawner_service.register_sim_spawned_callback(self.on_sim_spawned)

    def _update_schedule(self):
        time_of_day = services.time_service.sim_now
        day = time_of_day.day
        if self._current_day != day:
            self._current_day = day
            if day in self.scheduled_situations:
                resolver = self._get_resolver
                weighted_options = [(entry.weight.get_multiplier(resolver), entry.schedule) for entry in self.scheduled_situations[day]]
                self._schedule = sims4.random.weighted_random_item(weighted_options)
            else:
                self._schedule = None

    def on_shutdown(self):
        if self._situation_alarm_handle is not None:
            alarms.cancel_alarm(self._situation_alarm_handle)
            self._situation_alarm_handle = None
        if self._long_term_situation_alarm_handle is not None:
            alarms.cancel_alarm(self._long_term_situation_alarm_handle)
            self._long_term_situation_alarm_handle = None
        situation_manager = services.get_zone_situation_manager
        for uid in itertools.chain(self._long_term_situation_ids, self._situation_ids):
            situation = situation_manager.get(uid)
            if situation:
                situation_manager.destroy_situation_by_id(situation.id)

        services.sim_spawner_service.unregister_sim_spawned_callback(self.on_sim_spawned)
        super.on_shutdown

    @property
    def supports_open_street_director(self):
        return self.allow_open_street_director

    def _load_custom_zone_director(self, zone_director_proto, reader):
        for situation_data_proto in zone_director_proto.situations:
            if situation_data_proto.situation_list_guid == self.SCHEDULED_SITUATION_LIST_GUID:
                self._situation_ids.extend(situation_data_proto.situation_ids)

        self._current_hour = None
        current_hour_ticks = reader.read_uint32(self.CURRENT_HOUR_TOKEN, None)
        if current_hour_ticks is not None:
            self._current_hour = DateAndTime(current_hour_ticks)
        else:
            self._current_hour = None
        self._current_day = reader.read_uint32(self.CURRENT_DAY_TOKEN, None)
        schedule_guid = reader.read_uint64(self.SCHEDULE_GUID_TOKEN, None)
        if schedule_guid:
            self._schedule = services.get_instance_manager(sims4.resources.Types.SNIPPET).get(schedule_guid)
            _, current_hour, _ = self._schedule.get_current_situation_sets
            if current_hour != self._current_hour:
                self._situation_ids.clear
            else:
                situation_set_guid = reader.read_uint64(self.SITUATION_SET_GUID_TOKEN, None)
                if situation_set_guid:
                    self._situation_set = services.get_instance_manager(sims4.resources.Types.SNIPPET).get(situation_set_guid)
        super._load_custom_zone_director(zone_director_proto, reader)

    def _save_custom_zone_director(self, zone_director_proto, writer):
        if self._current_hour is not None:
            writer.write_uint32(self.CURRENT_HOUR_TOKEN, self._current_hour)
        if self._current_day is not None:
            writer.write_uint32(self.CURRENT_DAY_TOKEN, self._current_day)
        if self._schedule is not None:
            writer.write_uint64(self.SCHEDULE_GUID_TOKEN, self._schedule.guid64)
        if self._situation_set is not None:
            writer.write_uint64(self.SITUATION_SET_GUID_TOKEN, self._situation_set.guid64)
        situation_data_proto = zone_director_proto.situations.add
        situation_data_proto.situation_list_guid = self.SCHEDULED_SITUATION_LIST_GUID
        situation_data_proto.situation_ids.extend(self._prune_stale_situations(self._situation_ids))
        long_term_data_proto = zone_director_proto.situations.add
        long_term_data_proto.situation_list_guid = self.LONG_TERM_SITUATION_LIST_GUID
        long_term_data_proto.situation_ids.extend(self._prune_stale_situations(self._long_term_situation_ids))
        super._save_custom_zone_director(zone_director_proto, writer)

    def _get_resolver(self):
        sim_info = self._get_relevant_sim_info
        if sim_info is not None:
            return SingleSimResolver(sim_info)
        return GlobalResolver

    def _get_relevant_sim_info(self):
        for career_event in self._career_events:
            career_sim_info = career_event.sim_info
            if career_sim_info:
                return career_sim_info

        client = services.client_manager.get_first_client
        if client is not None:
            return client.active_sim_info

    def _on_scheduled_situation_request(self, *_, delayed_loots=None, **__):
        self._situation_ids = self._prune_stale_situations(self._situation_ids)
        self._update_schedule
        now = services.time_service.sim_now
        if self._schedule is None:
            time_span = create_date_and_time(days=1) - now.time_of_day
            self._situation_alarm_handle = alarms.add_alarm(self, time_span, self._on_scheduled_situation_request)
            self._situation_set = None
            return
        situation_sets, current_hour, next_hour = self._schedule.get_current_situation_sets
        time_span = now.time_till_next_day_time(next_hour, rollover_same_time=True)
        self._situation_alarm_handle = alarms.add_alarm(self, time_span, self._on_scheduled_situation_request)
        if self._situation_ids:
            if current_hour == self._current_hour:
                return
        self._current_hour = current_hour
        if not situation_sets:
            self._situation_ids.clear
            self._situation_set = None
            return
        on_time = abs((now.time_of_day - current_hour).in_minutes) < 1
        self._situation_ids, self._situation_set = self._schedule.start_situations(situation_sets, (self._get_resolver),
          (self._get_relevant_sim_info),
          (time_span.in_minutes),
          (set((career_event.sim_info.sim_id for career_event in self._career_events if career_event.sim_info is not None))),
          on_time,
          delayed_loots=delayed_loots)

    def _decide_whether_to_load_zone_situation_seed(self, seed):
        if not super._decide_whether_to_load_zone_situation_seed(seed):
            return False
        if self._is_career_event_seed(seed) or seed.situation_id in self._situation_ids or seed.situation_id in self._long_term_situation_ids:
            return True
        return False

    def _decide_whether_to_load_open_street_situation_seed(self, seed):
        return False

    def _request_long_term_situations(self, *_, **__):
        self._long_term_situation_ids = self._prune_stale_situations(self._long_term_situation_ids)
        self._update_schedule
        now = services.time_service.sim_now
        if self._schedule is None:
            time_span = create_date_and_time(days=1) - now.time_of_day
            self._long_term_situation_alarm_handle = alarms.add_alarm(self, time_span, self._request_long_term_situations)
            return
        elif self._next_long_term_time is None:
            self._next_long_term_time = self._schedule.request_initial_long_term_situations(self._get_resolver, self._get_relevant_sim_info, self._long_term_situation_ids)
        else:
            self._next_long_term_time = self._schedule.request_new_long_term_situations(self._next_long_term_time.time_of_day, self._get_resolver, self._get_relevant_sim_info, self._long_term_situation_ids)
        time_span = now.time_till_next_day_time((self._next_long_term_time), rollover_same_time=True)
        self._long_term_situation_alarm_handle = alarms.add_alarm(self, time_span, self._request_long_term_situations)

    def transfer_from_zone_director(self, zone_director):
        if isinstancezone_directorWeeklyScheduleZoneDirector:
            self._long_term_situation_ids = zone_director._long_term_situation_ids.copy
            zone_director._long_term_situation_ids.clear

    def create_situations_during_zone_spin_up(self):
        self._request_long_term_situations
        return super.create_situations_during_zone_spin_up

    def create_situations(self):
        self._request_long_term_situations
        return super.create_situations

    def on_spawn_sim_for_zone_spin_up_completed(self):
        super.on_spawn_sim_for_zone_spin_up_completed
        self._delayed_loots = []
        self._on_scheduled_situation_request(delayed_loots=(self._delayed_loots))
        services.sim_spawner_service.register_sim_spawned_callback(self.on_sim_spawned)

    def on_bouncer_assigned_all_sims_during_zone_spin_up(self):
        resolver = self._get_resolver
        for delayed_loot in self._delayed_loots:
            delayed_loot.apply_to_resolver(resolver)

    def on_sim_spawned(self, sim):
        if self._situation_set:
            if sim.is_selectable:
                time_span = self._situation_alarm_handle.get_remaining_time
                self._situation_ids.extend(self._situation_set.start((self._get_resolver), (self._get_relevant_sim_info),
                  (time_span.in_minutes),
                  (set((career_event.sim_info.sim_id for career_event in self._career_events if career_event.sim_info is not None))),
                  sims={
                 sim},
                  start=False))