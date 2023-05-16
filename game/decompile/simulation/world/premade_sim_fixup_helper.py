# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\premade_sim_fixup_helper.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 11616 bytes
from _collections import defaultdict
from sims.pregnancy.pregnancy_tracker import PregnancyTracker
from sims.sim_info_base_wrapper import SimInfoBaseWrapper
from world import get_lot_id_from_instance_id
from world.premade_sim_relationships import PremadeSimRelationships
import services, sims4.resources
logger = sims4.log.Logger('PremadeSimManager', default_owner='tingyul')

class PremadeSimFixupHelper:

    def __init__(self):
        self._premade_sim_infos = {}

    def fix_up_premade_sims(self):
        for sim_info in services.sim_info_manager().values():
            if sim_info.sim_template_id:
                if sim_info.premade_sim_fixup_completed:
                    continue
                sim_template = self._get_sim_template_from_id(sim_info.sim_template_id)
                self._premade_sim_infos[sim_template] = sim_info
                sim_info.premade_sim_fixup_completed = True

        if not self._premade_sim_infos:
            return
        self._apply_household_fixup()
        PremadeSimRelationships.apply_relationships(self._premade_sim_infos)
        self._apply_clans()
        self._apply_clubs()
        self._apply_careers()
        self._apply_pregnancy()
        self._apply_occult()
        self._apply_template_data()
        self._apply_aspiration()
        self._add_fixups()

    def _get_sim_template_from_id(self, template_id):
        template_manager = services.get_instance_manager(sims4.resources.Types.SIM_TEMPLATE)
        sim_template = template_manager.get(template_id)
        return sim_template

    def _apply_household_fixup--- This code section failed: ---

 L.  74         0  LOAD_SETCOMP             '<code_object <setcomp>>'
                2  LOAD_STR                 'PremadeSimFixupHelper._apply_household_fixup.<locals>.<setcomp>'
                4  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
                6  LOAD_FAST                'self'
                8  LOAD_ATTR                _premade_sim_infos
               10  LOAD_METHOD              values
               12  CALL_METHOD_0         0  '0 positional arguments'
               14  GET_ITER         
               16  CALL_FUNCTION_1       1  '1 positional argument'
               18  STORE_FAST               'households'

 L.  77        20  LOAD_DICTCOMP            '<code_object <dictcomp>>'
               22  LOAD_STR                 'PremadeSimFixupHelper._apply_household_fixup.<locals>.<dictcomp>'
               24  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
               26  LOAD_FAST                'self'
               28  LOAD_ATTR                _premade_sim_infos
               30  LOAD_METHOD              items
               32  CALL_METHOD_0         0  '0 positional arguments'
               34  GET_ITER         
               36  CALL_FUNCTION_1       1  '1 positional argument'
               38  STORE_DEREF              'sim_info_to_template'

 L.  79        40  SETUP_LOOP          134  'to 134'
               42  LOAD_FAST                'households'
               44  GET_ITER         
               46  FOR_ITER            132  'to 132'
               48  STORE_FAST               'household'

 L.  89        50  LOAD_CLOSURE             'sim_info_to_template'
               52  BUILD_TUPLE_1         1 
               54  LOAD_SETCOMP             '<code_object <setcomp>>'
               56  LOAD_STR                 'PremadeSimFixupHelper._apply_household_fixup.<locals>.<setcomp>'
               58  MAKE_FUNCTION_8          'closure'

 L.  90        60  LOAD_FAST                'household'
               62  GET_ITER         
               64  CALL_FUNCTION_1       1  '1 positional argument'
               66  STORE_FAST               'household_templates'

 L.  91        68  LOAD_CONST               None
               70  LOAD_FAST                'household_templates'
               72  COMPARE_OP               in
               74  POP_JUMP_IF_TRUE     88  'to 88'
               76  LOAD_GLOBAL              len
               78  LOAD_FAST                'household_templates'
               80  CALL_FUNCTION_1       1  '1 positional argument'
               82  LOAD_CONST               1
               84  COMPARE_OP               !=
               86  POP_JUMP_IF_FALSE   104  'to 104'
             88_0  COME_FROM            74  '74'

 L.  92        88  LOAD_GLOBAL              logger
               90  LOAD_METHOD              error
               92  LOAD_STR                 'Premade Household {} has members in different PremadeHouseholdTemplates: {}'

 L.  93        94  LOAD_FAST                'household'
               96  LOAD_FAST                'household_templates'
               98  CALL_METHOD_3         3  '3 positional arguments'
              100  POP_TOP          

 L.  94       102  CONTINUE             46  'to 46'
            104_0  COME_FROM            86  '86'

 L.  97       104  LOAD_GLOBAL              next
              106  LOAD_GLOBAL              iter
              108  LOAD_FAST                'household_templates'
              110  CALL_FUNCTION_1       1  '1 positional argument'
              112  CALL_FUNCTION_1       1  '1 positional argument'
              114  STORE_FAST               'household_template'

 L.  98       116  LOAD_FAST                'household_template'
              118  LOAD_METHOD              apply_fixup_to_household
              120  LOAD_FAST                'household'
              122  LOAD_FAST                'self'
              124  LOAD_ATTR                _premade_sim_infos
              126  CALL_METHOD_2         2  '2 positional arguments'
              128  POP_TOP          
              130  JUMP_BACK            46  'to 46'
              132  POP_BLOCK        
            134_0  COME_FROM_LOOP       40  '40'

Parse error at or near `LOAD_SETCOMP' instruction at offset 54

    def _apply_clans(self):
        clan_service = services.clan_service()
        if clan_service is None:
            return
        for premade_sim_template, sim_info in self._premade_sim_infos.items():
            clan_info = premade_sim_template.clan_info
            if clan_info is not None:
                clan_service.add_sim_to_clansim_infoclan_info.clan
                if clan_info.leader:
                    clan_service.reassign_clan_leadersim_infoclan_info.clan

    def _apply_clubs(self):

        class PremadeClubInfo:

            def __init__(self):
                self.leader = None
                self.members = []

        clubs = defaultdict(PremadeClubInfo)
        for premade_sim_template, sim_info in self._premade_sim_infos.items():
            for club_info in premade_sim_template.clubs:
                clubs[club_info.seed].members.append(sim_info)
                if club_info.leader:
                    if clubs[club_info.seed].leader is not None:
                        logger.error('Club {} has multiple leaders: {}, {}', club_info.seed, sim_info, clubs[club_info.seed].leader)
                    clubs[club_info.seed].leader = sim_info

        if not clubs:
            return
        club_service = services.get_club_service()
        with club_service.defer_club_distribution():
            for club_seed, info in clubs.items():
                club_seed.create_club(leader=(info.leader), members=(info.members), refresh_cache=False)

        club_service.update_affordance_cache()

    def _apply_careers(self):
        persistence_service = services.get_persistence_service()
        for premade_sim_template, sim_info in self._premade_sim_infos.items():
            sim_info.update_school_data()
            career_level = premade_sim_template.career_level
            if career_level is not None:
                career_type = career_level.career
                if not career_type.is_valid_career(sim_info=sim_info, from_join=True):
                    continue
                career = career_type(sim_info)
                if sim_info.career_tracker.has_career_by_uid(career.guid64):
                    sim_info.career_tracker.remove_career((career.guid64), post_quit_msg=False)
                career_lot = premade_sim_template.career_lot
                if career_lot is not None:
                    lot_id = get_lot_id_from_instance_id(career_lot)
                    zone_id = persistence_service.resolve_lot_id_into_zone_id(lot_id, ignore_neighborhood_id=True)
                    if zone_id is not None:
                        career_location = career.get_career_location()
                        career_location.set_zone_id(zone_id)
                sim_info.career_tracker.add_career(career, career_level_override=career_level, give_skipped_rewards=False,
                  defer_rewards=True,
                  allow_outfit_generation=False)

    def _apply_pregnancy(self):
        for premade_sim_template, sim_info in self._premade_sim_infos.items():
            pregnancy_tuning = premade_sim_template.pregnancy
            if pregnancy_tuning is None:
                continue
            other_parent = self._premade_sim_infos.getpregnancy_tuning.other_parentNone
            if other_parent is None:
                logger.error'Could not find sim info for other parent {}'pregnancy_tuning.other_parent
                continue
            sim_info.pregnancy_tracker.start_pregnancy(sim_info, other_parent, pregnancy_origin=(pregnancy_tuning.origin))
            sim_info.set_stat_valuePregnancyTracker.PREGNANCY_COMMODITY_MAP.get(sim_info.species)(pregnancy_tuning.progress * 100)

    def _apply_occult(self):
        for premade_sim_template, sim_info in self._premade_sim_infos.items():
            occult_tuning = premade_sim_template.occult
            if occult_tuning is None:
                continue
            sim_info_wrapper = SimInfoBaseWrapper(gender=(sim_info.gender), age=(sim_info.age),
              species=(sim_info.species),
              first_name=(sim_info.first_name),
              last_name=(sim_info.last_name),
              breed_name=(sim_info.breed_name),
              full_name_key=(sim_info.full_name_key),
              breed_name_key=(sim_info.breed_name_key))
            sim_info_wrapper.load_from_resource(occult_tuning.occult_sim_info)
            sim_info.occult_tracker.add_occult_for_premade_simsim_info_wrapperoccult_tuning.occult_type

    def _apply_template_data(self):
        for premade_sim_template, sim_info in self._premade_sim_infos.items():
            premade_sim_template.add_perks(sim_info, suppress_telemetry=True)
            premade_sim_template.add_rank(sim_info, suppress_telemetry=True)

    def _apply_aspiration(self):
        for premade_sim_template, sim_info in self._premade_sim_infos.items():
            if premade_sim_template.primary_aspiration is not None:
                with sim_info.primary_aspiration_telemetry_suppressed():
                    sim_info.primary_aspiration = premade_sim_template.primary_aspiration

    def _add_fixups(self):
        for premade_sim_template, sim_info in self._premade_sim_infos.items():
            fixup_tracker = sim_info.fixup_tracker
            if fixup_tracker is not None:
                for fixup in premade_sim_template._fixups:
                    fixup_tracker.add_fixup(fixup)