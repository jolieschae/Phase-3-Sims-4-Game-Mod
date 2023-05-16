# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\bouncer\bouncer.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 98896 bytes
from _collections import defaultdict
from collections import namedtuple
import heapq
from objects import ALL_HIDDEN_REASONS
from sims.sim_info_types import SimZoneSpinUpAction
from situations.bouncer.bouncer_types import BouncerRequestPriority, BouncerRequestStatus, BouncerExclusivityCategory, BouncerExclusivityOption
from situations.situation_types import SituationCommonBlacklistCategory
from tag import Tag
from world.spawn_point import SpawnPointOption
import enum, services, sims.sim_spawner_service, sims4.log, sims4.random, situations
logger = sims4.log.Logger('Bouncer')

class BouncerSimData:

    def __init__(self, bouncer, sim):
        self._sim_ref = sim.ref(lambda _: bouncer._sim_weakref_callback(sim))
        self._requests = []
        self.looking_for_new_situation = False

    def destroy(self):
        self._sim_ref = None
        self._requests.clear()
        self._requests = None

    def add_request(self, request, trump_all_exclusions=False):
        excluded = self._get_excluded_requests(request, trump_all_exclusions=trump_all_exclusions)
        self._requests.append(request)
        return excluded

    def remove_request(self, request):
        try:
            self._requests.remove(request)
        except ValueError:
            pass

    @property
    def requests(self):
        return set(self._requests)

    @property
    def is_obsolete(self):
        return len(self._requests) == 0

    def can_assign_to_request(self, new_request, check_exclusivity=True):
        if new_request in self._requests:
            return False
        for cur_request in self._requests:
            if not new_request._reassign_within_situation:
                if cur_request._situation is new_request._situation:
                    return False
            if check_exclusivity and cur_request._exclusivity_compare(new_request) > 0:
                return False

        return True

    def get_request_with_best_klout(self):
        best_klout = None
        best_request = None
        for request in self._requests:
            klout = request._get_request_klout()
            if not best_request is None:
                if not klout is not None or klout < best_klout:
                    best_klout = klout
                    best_request = request

        return best_request

    def _get_excluded_requests(self, new_request, trump_all_exclusions=False):
        excluded = []
        for cur_request in self._requests:
            if new_request._reassign_within_situation:
                if cur_request._situation is new_request._situation:
                    excluded.append(cur_request)
                    continue
                else:
                    compare_result = cur_request._exclusivity_compare(new_request)
                    if compare_result > 0:
                        if trump_all_exclusions:
                            excluded.append(cur_request)
                        else:
                            logger.error('New request: {} is excluded by existing request: {}', new_request, cur_request)
                if compare_result < 0:
                    excluded.append(cur_request)

        return excluded


class _BouncerSituationData:

    def __init__(self, situation):
        self._situation = situation
        self._requests = set()
        self._first_assignment_pass_completed = False
        self._reservation_requests = set()

    def add_request(self, request):
        self._requests.add(request)

    def remove_request(self, request):
        self._requests.discard(request)

    @property
    def requests(self):
        return set(self._requests)

    def add_reservation_request(self, request):
        self._reservation_requests.add(request)

    def remove_reservation_request(self, request):
        self._reservation_requests.discard(request)

    @property
    def reservation_requests(self):
        return set(self._reservation_requests)

    @property
    def first_assignment_pass_completed(self):
        return self._first_assignment_pass_completed

    def on_first_assignment_pass_completed(self):
        self._first_assignment_pass_completed = True


class SimRequestScore(namedtuple('SimRequestScore', 'sim_id, request, score')):

    def __eq__(self, o):
        return self.score == o.score

    def __ne__(self, o):
        return self.score != o.score

    def __lt__(self, o):
        return self.score > o.score

    def __le__(self, o):
        return self.score >= o.score

    def __gt__(self, o):
        return self.score < o.score

    def __ge__(self, o):
        return self.score <= o.score


class _BestRequestKlout(namedtuple('BestRequestKlout', 'request, klout')):

    def __eq__(self, o):
        return self.klout == o.klout

    def __ne__(self, o):
        return self.klout != o.klout

    def __lt__(self, o):
        return self.klout < o.klout

    def __le__(self, o):
        return self.klout <= o.klout

    def __gt__(self, o):
        return self.klout > o.klout

    def __ge__(self, o):
        return self.klout >= o.klout


class _WorstRequestKlout(namedtuple('WorstRequestKlout', 'request, klout')):

    def __eq__(self, o):
        return self.klout == o.klout

    def __ne__(self, o):
        return self.klout != o.klout

    def __lt__(self, o):
        return self.klout > o.klout

    def __le__(self, o):
        return self.klout >= o.klout

    def __gt__(self, o):
        return self.klout < o.klout

    def __ge__(self, o):
        return self.klout <= o.klout


class _BouncerUpdateMode(enum.Int, export=False):
    OFFLINE = 0
    FULLY_OPERATIONAL = 1


class Bouncer(sims.sim_spawner_service.ISimSpawnerServiceCustomer):
    SPAWN_COOLDOWN_MINUTES = 5
    EXCLUSIVITY_RULES = [
     (
      BouncerExclusivityCategory.NORMAL, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.EXPECTATION_PREFERENCE),
     (
      BouncerExclusivityCategory.NORMAL, BouncerExclusivityCategory.PRE_VISIT, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.NORMAL, BouncerExclusivityCategory.WALKBY_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.NORMAL, BouncerExclusivityCategory.FESTIVAL_GOER_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.NORMAL_UNPOSSESSABLE, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.EXPECTATION_PREFERENCE),
     (
      BouncerExclusivityCategory.NORMAL_UNPOSSESSABLE, BouncerExclusivityCategory.PRE_VISIT, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.NORMAL_UNPOSSESSABLE, BouncerExclusivityCategory.WALKBY_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.NORMAL_UNPOSSESSABLE, BouncerExclusivityCategory.INFECTED, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.NORMAL_UNPOSSESSABLE, BouncerExclusivityCategory.FESTIVAL_GOER_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.WALKBY, BouncerExclusivityCategory.NORMAL, BouncerExclusivityOption.EXPECTATION_PREFERENCE),
     (
      BouncerExclusivityCategory.WALKBY, BouncerExclusivityCategory.NORMAL_UNPOSSESSABLE, BouncerExclusivityOption.EXPECTATION_PREFERENCE),
     (
      BouncerExclusivityCategory.WALKBY, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.EXPECTATION_PREFERENCE),
     (
      BouncerExclusivityCategory.WALKBY, BouncerExclusivityCategory.WALKBY, BouncerExclusivityOption.ALREADY_ASSIGNED),
     (
      BouncerExclusivityCategory.WALKBY, BouncerExclusivityCategory.VENUE_BACKGROUND, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.WALKBY, BouncerExclusivityCategory.NON_WALKBY_BACKGROUND, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.WALKBY, BouncerExclusivityCategory.FESTIVAL_GOER_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.SERVICE, BouncerExclusivityCategory.WALKBY, BouncerExclusivityOption.ALREADY_ASSIGNED),
     (
      BouncerExclusivityCategory.SERVICE, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.EXPECTATION_PREFERENCE),
     (
      BouncerExclusivityCategory.SERVICE, BouncerExclusivityCategory.NORMAL, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.SERVICE, BouncerExclusivityCategory.NORMAL_UNPOSSESSABLE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.SERVICE, BouncerExclusivityCategory.SERVICE, BouncerExclusivityOption.ALREADY_ASSIGNED),
     (
      BouncerExclusivityCategory.SERVICE, BouncerExclusivityCategory.FESTIVAL_GOER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.SERVICE, BouncerExclusivityCategory.WALKBY_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.SERVICE, BouncerExclusivityCategory.FESTIVAL_GOER_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.SERVICE, BouncerExclusivityCategory.INSTRUCTED_CLASS, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.VISIT, BouncerExclusivityCategory.WALKBY, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.VISIT, BouncerExclusivityCategory.SERVICE, BouncerExclusivityOption.EXPECTATION_PREFERENCE),
     (
      BouncerExclusivityCategory.VISIT, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.VISIT, BouncerExclusivityCategory.UNGREETED, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.VISIT, BouncerExclusivityCategory.WALKBY_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.VISIT, BouncerExclusivityCategory.PRE_VISIT, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.VISIT, BouncerExclusivityCategory.FESTIVAL_GOER_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.NORMAL, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.NORMAL_UNPOSSESSABLE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.WALKBY, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.SERVICE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.VISIT, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.PRE_VISIT, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityOption.ALREADY_ASSIGNED),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.UNGREETED, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.NEUTRAL, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.VENUE_EMPLOYEE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.VENUE_BACKGROUND, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.CLUB_GATHERING, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.FESTIVAL_BACKGROUND, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.FESTIVAL_GOER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.WALKBY_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.ROOMMATE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.FESTIVAL_GOER_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.LEAVE_NOW, BouncerExclusivityCategory.INSTRUCTED_CLASS, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.UNGREETED, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.EXPECTATION_PREFERENCE),
     (
      BouncerExclusivityCategory.UNGREETED, BouncerExclusivityCategory.NORMAL, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.UNGREETED, BouncerExclusivityCategory.NORMAL_UNPOSSESSABLE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.UNGREETED, BouncerExclusivityCategory.WALKBY, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.UNGREETED, BouncerExclusivityCategory.SERVICE, BouncerExclusivityOption.ALREADY_ASSIGNED),
     (
      BouncerExclusivityCategory.UNGREETED, BouncerExclusivityCategory.WALKBY_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.UNGREETED, BouncerExclusivityCategory.FESTIVAL_GOER_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.PRE_VISIT, BouncerExclusivityCategory.WALKBY, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.PRE_VISIT, BouncerExclusivityCategory.SERVICE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.PRE_VISIT, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.PRE_VISIT, BouncerExclusivityCategory.UNGREETED, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.PRE_VISIT, BouncerExclusivityCategory.WALKBY_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.PRE_VISIT, BouncerExclusivityCategory.FESTIVAL_GOER_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.WORKER, BouncerExclusivityCategory.WALKBY, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.WORKER, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.WORKER, BouncerExclusivityCategory.NORMAL, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.WORKER, BouncerExclusivityCategory.NORMAL_UNPOSSESSABLE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.WORKER, BouncerExclusivityCategory.SERVICE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.WORKER, BouncerExclusivityCategory.VISIT, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.WORKER, BouncerExclusivityCategory.PRE_VISIT, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.WORKER, BouncerExclusivityCategory.NEUTRAL, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.WORKER, BouncerExclusivityCategory.WALKBY_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.WORKER, BouncerExclusivityCategory.FESTIVAL_GOER_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.WORKER, BouncerExclusivityCategory.INSTRUCTED_CLASS, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.VENUE_EMPLOYEE, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.EXPECTATION_PREFERENCE),
     (
      BouncerExclusivityCategory.VENUE_EMPLOYEE, BouncerExclusivityCategory.NORMAL, BouncerExclusivityOption.EXPECTATION_PREFERENCE),
     (
      BouncerExclusivityCategory.VENUE_EMPLOYEE, BouncerExclusivityCategory.NORMAL_UNPOSSESSABLE, BouncerExclusivityOption.EXPECTATION_PREFERENCE),
     (
      BouncerExclusivityCategory.VENUE_EMPLOYEE, BouncerExclusivityCategory.WALKBY, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.VENUE_EMPLOYEE, BouncerExclusivityCategory.VENUE_BACKGROUND, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.VENUE_EMPLOYEE, BouncerExclusivityCategory.VENUE_EMPLOYEE, BouncerExclusivityOption.ALREADY_ASSIGNED),
     (
      BouncerExclusivityCategory.VENUE_EMPLOYEE, BouncerExclusivityCategory.CLUB_GATHERING, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.VENUE_EMPLOYEE, BouncerExclusivityCategory.FESTIVAL_GOER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.VENUE_EMPLOYEE, BouncerExclusivityCategory.WALKBY_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.VENUE_EMPLOYEE, BouncerExclusivityCategory.SQUAD, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.VENUE_EMPLOYEE, BouncerExclusivityCategory.FESTIVAL_GOER_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.VENUE_EMPLOYEE, BouncerExclusivityCategory.INSTRUCTED_CLASS, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.CLUB_GATHERING, BouncerExclusivityCategory.CLUB_GATHERING, BouncerExclusivityOption.ALREADY_ASSIGNED),
     (
      BouncerExclusivityCategory.CLUB_GATHERING, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.CLUB_GATHERING, BouncerExclusivityCategory.WALKBY, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.CLUB_GATHERING, BouncerExclusivityCategory.WALKBY_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.FESTIVAL_BACKGROUND, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.FESTIVAL_BACKGROUND, BouncerExclusivityCategory.WALKBY_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.FESTIVAL_BACKGROUND, BouncerExclusivityCategory.FESTIVAL_GOER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.FESTIVAL_GOER, BouncerExclusivityCategory.FESTIVAL_GOER, BouncerExclusivityOption.ALREADY_ASSIGNED),
     (
      BouncerExclusivityCategory.FESTIVAL_GOER, BouncerExclusivityCategory.NORMAL, BouncerExclusivityOption.EXPECTATION_PREFERENCE),
     (
      BouncerExclusivityCategory.FESTIVAL_GOER, BouncerExclusivityCategory.NORMAL_UNPOSSESSABLE, BouncerExclusivityOption.EXPECTATION_PREFERENCE),
     (
      BouncerExclusivityCategory.FESTIVAL_GOER, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.EXPECTATION_PREFERENCE),
     (
      BouncerExclusivityCategory.FESTIVAL_GOER, BouncerExclusivityCategory.WALKBY, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.FESTIVAL_GOER, BouncerExclusivityCategory.WALKBY_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.FESTIVAL_GOER, BouncerExclusivityCategory.ROOMMATE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.FESTIVAL_EMPLOYEE, BouncerExclusivityCategory.FESTIVAL_GOER, BouncerExclusivityOption.ALREADY_ASSIGNED),
     (
      BouncerExclusivityCategory.FESTIVAL_EMPLOYEE, BouncerExclusivityCategory.FESTIVAL_EMPLOYEE, BouncerExclusivityOption.ALREADY_ASSIGNED),
     (
      BouncerExclusivityCategory.FESTIVAL_EMPLOYEE, BouncerExclusivityCategory.NORMAL, BouncerExclusivityOption.EXPECTATION_PREFERENCE),
     (
      BouncerExclusivityCategory.FESTIVAL_EMPLOYEE, BouncerExclusivityCategory.NORMAL_UNPOSSESSABLE, BouncerExclusivityOption.EXPECTATION_PREFERENCE),
     (
      BouncerExclusivityCategory.FESTIVAL_EMPLOYEE, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.EXPECTATION_PREFERENCE),
     (
      BouncerExclusivityCategory.FESTIVAL_EMPLOYEE, BouncerExclusivityCategory.WALKBY, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.FESTIVAL_EMPLOYEE, BouncerExclusivityCategory.WALKBY_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.FESTIVAL_EMPLOYEE, BouncerExclusivityCategory.ROOMMATE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.FESTIVAL_EMPLOYEE, BouncerExclusivityCategory.FESTIVAL_GOER_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.FESTIVAL_EMPLOYEE, BouncerExclusivityCategory.INSTRUCTED_CLASS, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.WALKBY_SNATCHER, BouncerExclusivityCategory.WALKBY, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.WALKBY_SNATCHER, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.CAREGIVER, BouncerExclusivityCategory.WALKBY, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.CAREGIVER, BouncerExclusivityCategory.WALKBY_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.CAREGIVER, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.CAREGIVER, BouncerExclusivityCategory.FESTIVAL_GOER_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.VENUE_GOER, BouncerExclusivityCategory.VENUE_GOER, BouncerExclusivityOption.ALREADY_ASSIGNED),
     (
      BouncerExclusivityCategory.VENUE_GOER, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.VENUE_GOER, BouncerExclusivityCategory.WALKBY_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.VENUE_GOER, BouncerExclusivityCategory.FESTIVAL_GOER_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.SQUAD, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.SQUAD, BouncerExclusivityCategory.FESTIVAL_GOER_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.NEUTRAL_UNPOSSESSABLE, BouncerExclusivityCategory.INFECTED, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.ROOMMATE, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.ROOMMATE, BouncerExclusivityCategory.FESTIVAL_GOER_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.FIRE_BRIGADE, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.FIRE_BRIGADE, BouncerExclusivityCategory.FIRE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.FIRE_BRIGADE, BouncerExclusivityCategory.FESTIVAL_GOER_SNATCHER, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.INSTRUCTED_CLASS, BouncerExclusivityCategory.INSTRUCTED_CLASS, BouncerExclusivityOption.ALREADY_ASSIGNED),
     (
      BouncerExclusivityCategory.INSTRUCTED_CLASS, BouncerExclusivityCategory.LEAVE, BouncerExclusivityOption.NONE),
     (
      BouncerExclusivityCategory.INSTRUCTED_CLASS, BouncerExclusivityCategory.FESTIVAL_GOER_SNATCHER, BouncerExclusivityOption.NONE)]
    INDEXES_PER_BOUNCER_REQUEST_PRIORITY = 4
    MAX_UNFULFILLED_INDEX = len(BouncerRequestPriority) * INDEXES_PER_BOUNCER_REQUEST_PRIORITY
    _exclusivity_rules = None
    _spawning_freeze_enabled = False
    _cap_cheat_enabled = False

    def __init__(self):
        self._unfulfilled_requests = []
        for unfulfilled_index in range(Bouncer.MAX_UNFULFILLED_INDEX):
            self._unfulfilled_requests.insert(unfulfilled_index, [])

        self._sim_filter_service_in_progress = False
        self._fulfilled_requests = []
        self._sim_to_bouncer_sim_data = {}
        self._situation_to_bouncer_situation_data = {}
        self._update_mode = _BouncerUpdateMode.OFFLINE
        self._reserved_sims = defaultdict(list)
        self._situation_id_for_filter_gsi = None

    def destroy(self):
        self.stop()
        self._clear_silently()

    def request_all_sims_during_zone_spin_up(self):
        self._spawn_all_during_zone_spin_up()

    def assign_all_sims_during_zone_spin_up(self):
        self._assign_instanced_sims_to_unfulfilled_requests()
        services.venue_service().get_zone_director().on_bouncer_assigned_all_sims_during_zone_spin_up()

    def start_full_operations(self):
        self._update_mode = _BouncerUpdateMode.FULLY_OPERATIONAL
        services.sim_spawner_service().register_on_npc_count_updated(self._monitor_npc_soft_cap)

    def stop(self):
        services.sim_spawner_service().unregister_on_npc_count_updated(self._monitor_npc_soft_cap)
        self._update_mode = _BouncerUpdateMode.OFFLINE

    def reset(self):
        self.stop()
        self._clear_silently()
        self.start_full_operations()

    def _clear_silently(self):
        for priority_list in self._unfulfilled_requests:
            for request in priority_list:
                request._destroy()

            priority_list.clear()

        self._sim_filter_service_in_progress = False
        for request in self._fulfilled_requests:
            request._destroy()

        self._fulfilled_requests.clear()
        for data in self._sim_to_bouncer_sim_data.values():
            data.destroy()

        self._sim_to_bouncer_sim_data.clear()
        self._situation_to_bouncer_situation_data.clear()

    def submit_request(self, request):
        self._unfulfilled_requests[request._unfulfilled_index].append(request)
        request._submit()
        situation_data = self._situation_to_bouncer_situation_data.setdefault(request._situation, _BouncerSituationData(self))
        situation_data.add_request(request)

    def withdraw_request(self, request, silently=False, reason=None):
        if request is None or request._status == BouncerRequestStatus.DESTROYED:
            return
        sims_removed_from_request = []
        if request._assigned_sim is not None:
            sims_removed_from_request.append(request._assigned_sim)
            self._unassign_sim_from_request((request._assigned_sim), request, silently=silently)
        if request in self._fulfilled_requests:
            self._fulfilled_requests.remove(request)
        else:
            if request in self._unfulfilled_requests[request._unfulfilled_index]:
                self._unfulfilled_requests[request._unfulfilled_index].remove(request)
            else:
                if request._status == BouncerRequestStatus.SIM_FILTER_SERVICE:
                    self._sim_filter_service_in_progress = False
                if request._status == BouncerRequestStatus.SPAWN_REQUESTED and request._sim_spawner_service_request is not None:
                    services.sim_spawner_service().withdraw_request(request._sim_spawner_service_request)
            situation_data = self._situation_to_bouncer_situation_data.get(request._situation, None)
            if situation_data:
                situation_data.remove_request(request)
            request._destroy(reason=reason)
            for sim in sims_removed_from_request:
                data = self._sim_to_bouncer_sim_data.get(sim, None)
                if data is None:
                    continue
                if data.is_obsolete:
                    data.destroy()
                    self._sim_to_bouncer_sim_data.pop(sim)

    def submit_reservation_request(self, reservation_request):
        if reservation_request.sim_id in self._reserved_sims:
            requests_to_withdraw = []
            for current_request in self._reserved_sims[reservation_request.sim_id]:
                exclusivity_result = current_request.exclusivity_compare(reservation_request)
                if exclusivity_result == 1:
                    return
                    if exclusivity_result == -1:
                        requests_to_withdraw.append(current_request)

            for request in requests_to_withdraw:
                self.withdraw_reservation_request(request)

        else:
            sim_spawner_service = services.sim_spawner_service()
            sim_spawner_service.add_npc_cap_modifier(1)
        situation_data = self._situation_to_bouncer_situation_data.setdefault(reservation_request.situation, _BouncerSituationData(self))
        situation_data.add_reservation_request(reservation_request)
        self._reserved_sims[reservation_request.sim_id].append(reservation_request)

    def withdraw_reservation_request(self, reservation_request):
        if reservation_request.sim_id not in self._reserved_sims:
            return
        else:
            situation_data = self._situation_to_bouncer_situation_data.get(reservation_request.situation, None)
            if situation_data:
                situation_data.remove_reservation_request(reservation_request)
            self._reserved_sims[reservation_request.sim_id].remove(reservation_request)
            sim_spawner_service = self._reserved_sims[reservation_request.sim_id] or services.sim_spawner_service()
            sim_spawner_service.add_npc_cap_modifier(-1)
            del self._reserved_sims[reservation_request.sim_id]

    def replace_reservation_request(self, bouncer_request):
        if bouncer_request.requested_sim_id == 0:
            logger.error("Attempting to replace a bouncer reservation request with a bouncer request that isn't explicit for .  This is unsupported behavior.")
        reservation_requests = self._reserved_sims.get(bouncer_request.requested_sim_id, tuple())
        for reservation_request in reservation_requests:
            if reservation_request.situation is bouncer_request.situation and reservation_request.sim_id == bouncer_request.requested_sim_id:
                self.withdraw_reservation_request(reservation_request)

        self.submit_request(bouncer_request)

    def remove_sim_from_situation(self, sim, situation):
        data = self._sim_to_bouncer_sim_data.get(sim, None)
        if data is None:
            return
        for request in data.requests:
            if request._situation == situation:
                self._unassign_sim_from_request_and_optionally_withdraw(sim, request)
                break

    def on_situation_destroy(self, situation):
        situation_data = self._situation_to_bouncer_situation_data.get(situation, None)
        if not situation_data:
            return
        for request in situation_data.requests:
            self.withdraw_request(request, silently=True, reason='Situation Destroyed')

        for reservation_request in situation_data.reservation_requests:
            self.withdraw_reservation_request(reservation_request)

        del self._situation_to_bouncer_situation_data[situation]

    def situation_requests_gen(self, situation):
        situation_data = self._situation_to_bouncer_situation_data.get(situation, None)
        if not situation_data:
            return
        for request in situation_data.requests:
            if request._is_obsolete == False and request._status != BouncerRequestStatus.DESTROYED:
                yield request

    def situation_reservation_requests_gen(self, situation):
        situation_data = self._situation_to_bouncer_situation_data.get(situation, None)
        if not situation_data:
            return
        for request in situation_data.reservation_requests:
            yield request

    def pending_situation_requests_gen(self, situation):
        for request in self.situation_requests_gen(situation):
            if request._is_fulfilled or request._allows_spawning:
                yield request

    def get_most_important_request_for_sim(self, sim):
        data = self._sim_to_bouncer_sim_data.get(sim, None)
        if not data is None:
            return data.requests or None
        else:
            best_requests = []
            best_klout = None
            for request in data.requests:
                klout = request._get_request_klout()
                if klout is None:
                    continue
                if best_klout is None:
                    best_requests.append(request)
                    best_klout = klout
                elif klout == best_klout:
                    best_requests.append(request)
                elif klout < best_klout:
                    best_requests.clear()
                    best_requests.append(request)
                    best_klout = klout

            return best_requests or None
        best_requests.sort(key=(lambda request: request._creation_id))
        return best_requests[0]

    def get_most_important_situation_for_sim(self, sim):
        request = self.get_most_important_request_for_sim(sim)
        if request is None:
            return
        return request._situation

    def get_unfulfilled_situations_by_tag(self, situation_tag):
        unfulfilled_situations = {}
        for unfulfilled_index in range(self.MAX_UNFULFILLED_INDEX):
            requests = self._unfulfilled_requests[unfulfilled_index]
            for request in requests:
                situation = request._situation
                if situation_tag in situation.tags and situation.id not in unfulfilled_situations:
                    unfulfilled_situations[situation.id] = situation

        return unfulfilled_situations

    @classmethod
    def are_mutually_exclusive(cls, cat1, cat2):
        cls._construct_exclusivity()
        key = cat1 | cat2
        rule = cls._exclusivity_rules.get(key, None)
        return rule

    def spawning_freeze(self, value):
        self._spawning_freeze_enabled = value

    def cap_cheat(self, value):
        self._cap_cheat_enabled = value

    def _set_request_for_sim_filter_gsi(self, request):
        self._situation_id_for_filter_gsi = request.situation.id

    def get_sim_filter_gsi_name(self):
        situation_manager = services.get_zone_situation_manager()
        situation = situation_manager.get(self._situation_id_for_filter_gsi) if situation_manager is not None else None
        return 'Bouncer for Situation: {}'.format(situation)

    @classmethod
    def _construct_exclusivity(cls):
        if cls._exclusivity_rules is not None:
            return
        cls._exclusivity_rules = {}
        for rule in cls.EXCLUSIVITY_RULES:
            cat1 = rule[0]
            cat2 = rule[1]
            key = cat1 | cat2
            if cls._exclusivity_rules.get(key) is not None:
                logger.error('Duplicate situation exclusivity rule for {} and {}', cat1, cat2)
            cls._exclusivity_rules[key] = rule

    def _update(self):
        if self._update_mode == _BouncerUpdateMode.OFFLINE:
            return
        with situations.situation_manager.DelayedSituationDestruction():
            self._assign_instanced_sims_to_unfulfilled_requests()
            self._assigned_sims_looking_for_new_situations_to_unfulfilled_requests()
            self._spawn_sim_for_next_request()
            self._check_for_tardy_requests()

    def _assign_instanced_sims_to_unfulfilled_requests--- This code section failed: ---

 L. 965         0  LOAD_GLOBAL              situations
                2  LOAD_ATTR                situation_manager
                4  LOAD_METHOD              DelayedSituationDestruction
                6  CALL_METHOD_0         0  '0 positional arguments'
             8_10  SETUP_WITH          542  'to 542'
               12  POP_TOP          

 L. 968        14  LOAD_GLOBAL              set
               16  CALL_FUNCTION_0       0  '0 positional arguments'
               18  STORE_FAST               'all_candidate_sim_ids'

 L. 969        20  SETUP_LOOP           70  'to 70'
               22  LOAD_GLOBAL              services
               24  LOAD_METHOD              sim_info_manager
               26  CALL_METHOD_0         0  '0 positional arguments'
               28  LOAD_METHOD              instanced_sims_gen
               30  CALL_METHOD_0         0  '0 positional arguments'
               32  GET_ITER         
               34  FOR_ITER             68  'to 68'
               36  STORE_FAST               'sim'

 L. 974        38  LOAD_FAST                'sim'
               40  LOAD_ATTR                is_simulating
               42  POP_JUMP_IF_TRUE     46  'to 46'

 L. 975        44  CONTINUE             34  'to 34'
             46_0  COME_FROM            42  '42'

 L. 976        46  LOAD_FAST                'sim'
               48  LOAD_ATTR                visible_to_client
               50  POP_JUMP_IF_TRUE     54  'to 54'

 L. 977        52  CONTINUE             34  'to 34'
             54_0  COME_FROM            50  '50'

 L. 978        54  LOAD_FAST                'all_candidate_sim_ids'
               56  LOAD_METHOD              add
               58  LOAD_FAST                'sim'
               60  LOAD_ATTR                id
               62  CALL_METHOD_1         1  '1 positional argument'
               64  POP_TOP          
               66  JUMP_BACK            34  'to 34'
               68  POP_BLOCK        
             70_0  COME_FROM_LOOP       20  '20'

 L. 980        70  LOAD_GLOBAL              len
               72  LOAD_FAST                'all_candidate_sim_ids'
               74  CALL_FUNCTION_1       1  '1 positional argument'
               76  LOAD_CONST               0
               78  COMPARE_OP               ==
               80  POP_JUMP_IF_FALSE    86  'to 86'

 L. 981        82  LOAD_CONST               None
               84  RETURN_VALUE     
             86_0  COME_FROM            80  '80'

 L. 983        86  LOAD_DEREF               'self'
               88  LOAD_METHOD              _get_common_blacklists
               90  CALL_METHOD_0         0  '0 positional arguments'
               92  UNPACK_SEQUENCE_3     3 
               94  STORE_FAST               'spawning_sim_ids'
               96  STORE_FAST               'active_household_sim_ids'
               98  STORE_FAST               'active_lot_household_sim_ids'

 L. 985       100  LOAD_GLOBAL              services
              102  LOAD_METHOD              sim_filter_service
              104  CALL_METHOD_0         0  '0 positional arguments'
              106  STORE_FAST               'sim_filter_service'

 L. 988   108_110  SETUP_LOOP          488  'to 488'
              112  LOAD_GLOBAL              range
              114  LOAD_GLOBAL              Bouncer
              116  LOAD_ATTR                MAX_UNFULFILLED_INDEX
              118  CALL_FUNCTION_1       1  '1 positional argument'
              120  GET_ITER         
          122_124  FOR_ITER            486  'to 486'
              126  STORE_FAST               'unfulfilled_index'

 L. 989       128  LOAD_GLOBAL              list
              130  LOAD_DEREF               'self'
              132  LOAD_ATTR                _unfulfilled_requests
              134  LOAD_FAST                'unfulfilled_index'
              136  BINARY_SUBSCR    
              138  CALL_FUNCTION_1       1  '1 positional argument'
              140  STORE_FAST               'candidate_requests'

 L. 991       142  BUILD_LIST_0          0 
              144  STORE_FAST               'sim_request_score_heap'

 L. 993       146  SETUP_LOOP          358  'to 358'
              148  LOAD_FAST                'candidate_requests'
              150  GET_ITER         
            152_0  COME_FROM           160  '160'
              152  FOR_ITER            356  'to 356'
              154  STORE_DEREF              'request'

 L. 995       156  LOAD_DEREF               'request'
              158  LOAD_ATTR                _requires_spawning
              160  POP_JUMP_IF_TRUE    152  'to 152'
              162  LOAD_DEREF               'request'
              164  LOAD_ATTR                _status
              166  LOAD_GLOBAL              BouncerRequestStatus
              168  LOAD_ATTR                SUBMITTED
              170  COMPARE_OP               !=
              172  POP_JUMP_IF_FALSE   176  'to 176'

 L. 996       174  CONTINUE            152  'to 152'
            176_0  COME_FROM           172  '172'

 L. 999       176  LOAD_CLOSURE             'request'
              178  LOAD_CLOSURE             'self'
              180  BUILD_TUPLE_2         2 
              182  LOAD_SETCOMP             '<code_object <setcomp>>'
              184  LOAD_STR                 'Bouncer._assign_instanced_sims_to_unfulfilled_requests.<locals>.<setcomp>'
              186  MAKE_FUNCTION_8          'closure'
              188  LOAD_FAST                'all_candidate_sim_ids'
              190  GET_ITER         
              192  CALL_FUNCTION_1       1  '1 positional argument'
              194  STORE_FAST               'candidate_sim_ids'

 L.1001       196  LOAD_DEREF               'request'
              198  LOAD_ATTR                _constrained_sim_ids
              200  POP_JUMP_IF_FALSE   212  'to 212'

 L.1002       202  LOAD_FAST                'candidate_sim_ids'
              204  LOAD_DEREF               'request'
              206  LOAD_ATTR                _constrained_sim_ids
              208  BINARY_AND       
              210  STORE_FAST               'candidate_sim_ids'
            212_0  COME_FROM           200  '200'

 L.1007       212  LOAD_FAST                'candidate_sim_ids'
              214  POP_JUMP_IF_TRUE    218  'to 218'

 L.1008       216  CONTINUE            152  'to 152'
            218_0  COME_FROM           214  '214'

 L.1010       218  LOAD_DEREF               'request'
              220  LOAD_ATTR                job_type
              222  LOAD_ATTR                sim_auto_invite_use_common_blacklists_on_instanced_sims
              224  POP_JUMP_IF_FALSE   252  'to 252'

 L.1011       226  LOAD_GLOBAL              set
              228  CALL_FUNCTION_0       0  '0 positional arguments'
              230  STORE_FAST               'blacklist'

 L.1012       232  LOAD_DEREF               'self'
              234  LOAD_METHOD              _apply_common_blacklists
              236  LOAD_DEREF               'request'
              238  LOAD_FAST                'blacklist'
              240  LOAD_FAST                'spawning_sim_ids'
              242  LOAD_FAST                'active_household_sim_ids'
              244  LOAD_FAST                'active_lot_household_sim_ids'
              246  CALL_METHOD_5         5  '5 positional arguments'
              248  POP_TOP          
              250  JUMP_FORWARD        260  'to 260'
            252_0  COME_FROM           224  '224'

 L.1014       252  LOAD_DEREF               'request'
              254  LOAD_METHOD              _get_blacklist
              256  CALL_METHOD_0         0  '0 positional arguments'
              258  STORE_FAST               'blacklist'
            260_0  COME_FROM           250  '250'

 L.1016       260  LOAD_DEREF               'self'
              262  LOAD_METHOD              _set_request_for_sim_filter_gsi
              264  LOAD_DEREF               'request'
              266  CALL_METHOD_1         1  '1 positional argument'
              268  POP_TOP          

 L.1018       270  LOAD_FAST                'sim_filter_service'
              272  LOAD_ATTR                submit_filter
              274  LOAD_DEREF               'request'
              276  LOAD_ATTR                _sim_filter

 L.1019       278  LOAD_CONST               None

 L.1020       280  LOAD_GLOBAL              list
              282  LOAD_FAST                'candidate_sim_ids'
              284  CALL_FUNCTION_1       1  '1 positional argument'

 L.1021       286  LOAD_FAST                'blacklist'

 L.1022       288  LOAD_DEREF               'request'
              290  LOAD_ATTR                _requesting_sim_info

 L.1023       292  LOAD_CONST               False

 L.1024       294  LOAD_DEREF               'request'
              296  LOAD_METHOD              get_additional_filter_terms
              298  CALL_METHOD_0         0  '0 positional arguments'

 L.1025       300  LOAD_DEREF               'self'
              302  LOAD_ATTR                get_sim_filter_gsi_name
              304  LOAD_CONST               ('callback', 'sim_constraints', 'blacklist_sim_ids', 'requesting_sim_info', 'allow_yielding', 'additional_filter_terms', 'gsi_source_fn')
              306  CALL_FUNCTION_KW_8     8  '8 total positional and keyword args'
              308  STORE_FAST               'filter_results'

 L.1028       310  SETUP_LOOP          354  'to 354'
              312  LOAD_FAST                'filter_results'
              314  GET_ITER         
              316  FOR_ITER            352  'to 352'
              318  STORE_FAST               'filter_result'

 L.1029       320  LOAD_GLOBAL              heapq
              322  LOAD_METHOD              heappush
              324  LOAD_FAST                'sim_request_score_heap'
              326  LOAD_GLOBAL              SimRequestScore
              328  LOAD_FAST                'filter_result'
              330  LOAD_ATTR                sim_info
              332  LOAD_ATTR                id
              334  LOAD_DEREF               'request'
              336  LOAD_FAST                'filter_result'
              338  LOAD_ATTR                score
              340  LOAD_CONST               ('sim_id', 'request', 'score')
              342  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              344  CALL_METHOD_2         2  '2 positional arguments'
              346  POP_TOP          
          348_350  JUMP_BACK           316  'to 316'
              352  POP_BLOCK        
            354_0  COME_FROM_LOOP      310  '310'
              354  JUMP_BACK           152  'to 152'
              356  POP_BLOCK        
            358_0  COME_FROM_LOOP      146  '146'

 L.1032       358  SETUP_LOOP          484  'to 484'
            360_0  COME_FROM           434  '434'
              360  LOAD_FAST                'sim_request_score_heap'
          362_364  POP_JUMP_IF_FALSE   482  'to 482'

 L.1033       366  LOAD_GLOBAL              heapq
              368  LOAD_METHOD              heappop
              370  LOAD_FAST                'sim_request_score_heap'
              372  CALL_METHOD_1         1  '1 positional argument'
              374  STORE_FAST               'sim_request_score'

 L.1034       376  LOAD_FAST                'sim_request_score'
              378  LOAD_ATTR                request
              380  STORE_DEREF              'request'

 L.1037       382  LOAD_DEREF               'request'
              384  LOAD_ATTR                _is_fulfilled
          386_388  POP_JUMP_IF_FALSE   394  'to 394'

 L.1038   390_392  CONTINUE            360  'to 360'
            394_0  COME_FROM           386  '386'

 L.1040       394  LOAD_GLOBAL              services
              396  LOAD_METHOD              object_manager
              398  CALL_METHOD_0         0  '0 positional arguments'
              400  LOAD_METHOD              get
              402  LOAD_FAST                'sim_request_score'
              404  LOAD_ATTR                sim_id
              406  CALL_METHOD_1         1  '1 positional argument'
              408  STORE_FAST               'sim'

 L.1041       410  LOAD_FAST                'sim'
              412  LOAD_CONST               None
              414  COMPARE_OP               is
          416_418  POP_JUMP_IF_FALSE   424  'to 424'

 L.1042   420_422  CONTINUE            360  'to 360'
            424_0  COME_FROM           416  '416'

 L.1045       424  LOAD_DEREF               'self'
              426  LOAD_METHOD              _can_assign_sim_to_request
              428  LOAD_FAST                'sim'
              430  LOAD_DEREF               'request'
              432  CALL_METHOD_2         2  '2 positional arguments'
          434_436  POP_JUMP_IF_FALSE   360  'to 360'

 L.1046       438  LOAD_DEREF               'request'
              440  LOAD_ATTR                _is_factory
          442_444  POP_JUMP_IF_FALSE   466  'to 466'

 L.1047       446  LOAD_DEREF               'request'
              448  LOAD_METHOD              _create_request
              450  LOAD_FAST                'sim'
              452  CALL_METHOD_1         1  '1 positional argument'
              454  STORE_DEREF              'request'

 L.1048       456  LOAD_DEREF               'self'
              458  LOAD_METHOD              submit_request
              460  LOAD_DEREF               'request'
              462  CALL_METHOD_1         1  '1 positional argument'
              464  POP_TOP          
            466_0  COME_FROM           442  '442'

 L.1049       466  LOAD_DEREF               'self'
              468  LOAD_METHOD              _assign_sim_to_request
              470  LOAD_FAST                'sim'
              472  LOAD_DEREF               'request'
              474  CALL_METHOD_2         2  '2 positional arguments'
              476  POP_TOP          
          478_480  JUMP_BACK           360  'to 360'
            482_0  COME_FROM           362  '362'
              482  POP_BLOCK        
            484_0  COME_FROM_LOOP      358  '358'
              484  JUMP_BACK           122  'to 122'
              486  POP_BLOCK        
            488_0  COME_FROM_LOOP      108  '108'

 L.1052       488  SETUP_LOOP          538  'to 538'
              490  LOAD_DEREF               'self'
              492  LOAD_ATTR                _situation_to_bouncer_situation_data
              494  LOAD_METHOD              items
              496  CALL_METHOD_0         0  '0 positional arguments'
              498  GET_ITER         
            500_0  COME_FROM           512  '512'
              500  FOR_ITER            536  'to 536'
              502  UNPACK_SEQUENCE_2     2 
              504  STORE_FAST               'situation'
              506  STORE_FAST               'situation_data'

 L.1053       508  LOAD_FAST                'situation_data'
              510  LOAD_ATTR                first_assignment_pass_completed
          512_514  POP_JUMP_IF_TRUE    500  'to 500'

 L.1054       516  LOAD_FAST                'situation'
              518  LOAD_METHOD              on_first_assignment_pass_completed
              520  CALL_METHOD_0         0  '0 positional arguments'
              522  POP_TOP          

 L.1055       524  LOAD_FAST                'situation_data'
              526  LOAD_METHOD              on_first_assignment_pass_completed
              528  CALL_METHOD_0         0  '0 positional arguments'
              530  POP_TOP          
          532_534  JUMP_BACK           500  'to 500'
              536  POP_BLOCK        
            538_0  COME_FROM_LOOP      488  '488'
              538  POP_BLOCK        
              540  LOAD_CONST               None
            542_0  COME_FROM_WITH        8  '8'
              542  WITH_CLEANUP_START
              544  WITH_CLEANUP_FINISH
              546  END_FINALLY      

Parse error at or near `LOAD_SETCOMP' instruction at offset 182

    def _assigned_sims_looking_for_new_situations_to_unfulfilled_requests--- This code section failed: ---

 L.1065         0  LOAD_GLOBAL              situations
                2  LOAD_ATTR                situation_manager
                4  LOAD_METHOD              DelayedSituationDestruction
                6  CALL_METHOD_0         0  '0 positional arguments'
             8_10  SETUP_WITH          452  'to 452'
               12  POP_TOP          

 L.1066        14  LOAD_LISTCOMP            '<code_object <listcomp>>'
               16  LOAD_STR                 'Bouncer._assigned_sims_looking_for_new_situations_to_unfulfilled_requests.<locals>.<listcomp>'
               18  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
               20  LOAD_DEREF               'self'
               22  LOAD_ATTR                _sim_to_bouncer_sim_data
               24  LOAD_METHOD              items
               26  CALL_METHOD_0         0  '0 positional arguments'
               28  GET_ITER         
               30  CALL_FUNCTION_1       1  '1 positional argument'
               32  STORE_FAST               'all_candidate_sim_ids'

 L.1068        34  LOAD_FAST                'all_candidate_sim_ids'
               36  POP_JUMP_IF_TRUE     42  'to 42'

 L.1069        38  LOAD_CONST               None
               40  RETURN_VALUE     
             42_0  COME_FROM            36  '36'

 L.1071        42  LOAD_GLOBAL              services
               44  LOAD_METHOD              sim_filter_service
               46  CALL_METHOD_0         0  '0 positional arguments'
               48  STORE_FAST               'sim_filter_service'

 L.1075     50_52  SETUP_LOOP          398  'to 398'
               54  LOAD_GLOBAL              range
               56  LOAD_GLOBAL              Bouncer
               58  LOAD_ATTR                MAX_UNFULFILLED_INDEX
               60  CALL_FUNCTION_1       1  '1 positional argument'
               62  GET_ITER         
            64_66  FOR_ITER            396  'to 396'
               68  STORE_FAST               'unfulfilled_index'

 L.1076        70  LOAD_GLOBAL              list
               72  LOAD_DEREF               'self'
               74  LOAD_ATTR                _unfulfilled_requests
               76  LOAD_FAST                'unfulfilled_index'
               78  BINARY_SUBSCR    
               80  CALL_FUNCTION_1       1  '1 positional argument'
               82  STORE_FAST               'candidate_requests'

 L.1078        84  BUILD_LIST_0          0 
               86  STORE_FAST               'sim_request_score_heap'

 L.1080        88  SETUP_LOOP          260  'to 260'
               90  LOAD_FAST                'candidate_requests'
               92  GET_ITER         
             94_0  COME_FROM           112  '112'
               94  FOR_ITER            258  'to 258'
               96  STORE_DEREF              'request'

 L.1081        98  LOAD_DEREF               'self'
              100  LOAD_METHOD              _set_request_for_sim_filter_gsi
              102  LOAD_DEREF               'request'
              104  CALL_METHOD_1         1  '1 positional argument'
              106  POP_TOP          

 L.1082       108  LOAD_DEREF               'request'
              110  LOAD_ATTR                _accept_looking_for_more_work
              112  POP_JUMP_IF_FALSE    94  'to 94'
              114  LOAD_DEREF               'request'
              116  LOAD_ATTR                _status
              118  LOAD_GLOBAL              BouncerRequestStatus
              120  LOAD_ATTR                SUBMITTED
              122  COMPARE_OP               !=
              124  POP_JUMP_IF_FALSE   128  'to 128'

 L.1083       126  CONTINUE             94  'to 94'
            128_0  COME_FROM           124  '124'

 L.1088       128  LOAD_CLOSURE             'request'
              130  LOAD_CLOSURE             'self'
              132  BUILD_TUPLE_2         2 
              134  LOAD_SETCOMP             '<code_object <setcomp>>'
              136  LOAD_STR                 'Bouncer._assigned_sims_looking_for_new_situations_to_unfulfilled_requests.<locals>.<setcomp>'
              138  MAKE_FUNCTION_8          'closure'
              140  LOAD_FAST                'all_candidate_sim_ids'
              142  GET_ITER         
              144  CALL_FUNCTION_1       1  '1 positional argument'
              146  STORE_FAST               'candidate_sim_ids'

 L.1090       148  LOAD_DEREF               'request'
              150  LOAD_ATTR                _constrained_sim_ids
              152  POP_JUMP_IF_FALSE   164  'to 164'

 L.1091       154  LOAD_FAST                'candidate_sim_ids'
              156  LOAD_DEREF               'request'
              158  LOAD_ATTR                _constrained_sim_ids
              160  BINARY_AND       
              162  STORE_FAST               'candidate_sim_ids'
            164_0  COME_FROM           152  '152'

 L.1096       164  LOAD_FAST                'candidate_sim_ids'
              166  POP_JUMP_IF_TRUE    170  'to 170'

 L.1097       168  CONTINUE             94  'to 94'
            170_0  COME_FROM           166  '166'

 L.1100       170  LOAD_FAST                'sim_filter_service'
              172  LOAD_ATTR                submit_filter
              174  LOAD_DEREF               'request'
              176  LOAD_ATTR                _sim_filter

 L.1101       178  LOAD_CONST               None

 L.1102       180  LOAD_GLOBAL              list
              182  LOAD_FAST                'candidate_sim_ids'
              184  CALL_FUNCTION_1       1  '1 positional argument'

 L.1103       186  LOAD_DEREF               'request'
              188  LOAD_METHOD              _get_blacklist
              190  CALL_METHOD_0         0  '0 positional arguments'

 L.1104       192  LOAD_DEREF               'request'
              194  LOAD_ATTR                _requesting_sim_info

 L.1105       196  LOAD_CONST               False

 L.1106       198  LOAD_DEREF               'request'
              200  LOAD_METHOD              get_additional_filter_terms
              202  CALL_METHOD_0         0  '0 positional arguments'

 L.1107       204  LOAD_DEREF               'self'
              206  LOAD_ATTR                get_sim_filter_gsi_name
              208  LOAD_CONST               ('callback', 'sim_constraints', 'blacklist_sim_ids', 'requesting_sim_info', 'allow_yielding', 'additional_filter_terms', 'gsi_source_fn')
              210  CALL_FUNCTION_KW_8     8  '8 total positional and keyword args'
              212  STORE_FAST               'filter_results'

 L.1110       214  SETUP_LOOP          256  'to 256'
              216  LOAD_FAST                'filter_results'
              218  GET_ITER         
              220  FOR_ITER            254  'to 254'
              222  STORE_FAST               'filter_result'

 L.1111       224  LOAD_GLOBAL              heapq
              226  LOAD_METHOD              heappush
              228  LOAD_FAST                'sim_request_score_heap'
              230  LOAD_GLOBAL              SimRequestScore
              232  LOAD_FAST                'filter_result'
              234  LOAD_ATTR                sim_info
              236  LOAD_ATTR                id
              238  LOAD_DEREF               'request'
              240  LOAD_FAST                'filter_result'
              242  LOAD_ATTR                score
              244  LOAD_CONST               ('sim_id', 'request', 'score')
              246  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              248  CALL_METHOD_2         2  '2 positional arguments'
              250  POP_TOP          
              252  JUMP_BACK           220  'to 220'
              254  POP_BLOCK        
            256_0  COME_FROM_LOOP      214  '214'
              256  JUMP_BACK            94  'to 94'
              258  POP_BLOCK        
            260_0  COME_FROM_LOOP       88  '88'

 L.1114       260  SETUP_LOOP          394  'to 394'
            262_0  COME_FROM           340  '340'
              262  LOAD_FAST                'sim_request_score_heap'
          264_266  POP_JUMP_IF_FALSE   392  'to 392'

 L.1115       268  LOAD_GLOBAL              heapq
              270  LOAD_METHOD              heappop
              272  LOAD_FAST                'sim_request_score_heap'
              274  CALL_METHOD_1         1  '1 positional argument'
              276  STORE_FAST               'sim_request_score'

 L.1116       278  LOAD_FAST                'sim_request_score'
              280  LOAD_ATTR                request
              282  STORE_DEREF              'request'

 L.1119       284  LOAD_DEREF               'request'
              286  LOAD_ATTR                _is_fulfilled
          288_290  POP_JUMP_IF_FALSE   296  'to 296'

 L.1120   292_294  CONTINUE            262  'to 262'
            296_0  COME_FROM           288  '288'

 L.1122       296  LOAD_GLOBAL              services
              298  LOAD_METHOD              object_manager
              300  CALL_METHOD_0         0  '0 positional arguments'
              302  LOAD_METHOD              get
              304  LOAD_FAST                'sim_request_score'
              306  LOAD_ATTR                sim_id
              308  CALL_METHOD_1         1  '1 positional argument'
              310  STORE_FAST               'sim'

 L.1123       312  LOAD_FAST                'sim'
              314  LOAD_CONST               None
              316  COMPARE_OP               is
          318_320  POP_JUMP_IF_FALSE   326  'to 326'

 L.1124   322_324  CONTINUE            262  'to 262'
            326_0  COME_FROM           318  '318'

 L.1127       326  LOAD_DEREF               'self'
              328  LOAD_ATTR                _can_assign_sim_to_request
              330  LOAD_FAST                'sim'
              332  LOAD_DEREF               'request'
              334  LOAD_CONST               False
              336  LOAD_CONST               ('check_exclusivity',)
              338  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
          340_342  POP_JUMP_IF_FALSE   262  'to 262'

 L.1128       344  LOAD_DEREF               'request'
              346  LOAD_ATTR                _is_factory
          348_350  POP_JUMP_IF_FALSE   372  'to 372'

 L.1129       352  LOAD_DEREF               'request'
              354  LOAD_METHOD              _create_request
              356  LOAD_FAST                'sim'
              358  CALL_METHOD_1         1  '1 positional argument'
              360  STORE_DEREF              'request'

 L.1130       362  LOAD_DEREF               'self'
              364  LOAD_METHOD              submit_request
              366  LOAD_DEREF               'request'
              368  CALL_METHOD_1         1  '1 positional argument'
              370  POP_TOP          
            372_0  COME_FROM           348  '348'

 L.1131       372  LOAD_DEREF               'self'
              374  LOAD_ATTR                _assign_sim_to_request
              376  LOAD_FAST                'sim'
              378  LOAD_DEREF               'request'
              380  LOAD_CONST               True
              382  LOAD_CONST               ('trump_all_exclusions',)
              384  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              386  POP_TOP          
          388_390  JUMP_BACK           262  'to 262'
            392_0  COME_FROM           264  '264'
              392  POP_BLOCK        
            394_0  COME_FROM_LOOP      260  '260'
              394  JUMP_BACK            64  'to 64'
              396  POP_BLOCK        
            398_0  COME_FROM_LOOP       50  '50'

 L.1134       398  SETUP_LOOP          448  'to 448'
              400  LOAD_DEREF               'self'
              402  LOAD_ATTR                _situation_to_bouncer_situation_data
              404  LOAD_METHOD              items
              406  CALL_METHOD_0         0  '0 positional arguments'
              408  GET_ITER         
            410_0  COME_FROM           422  '422'
              410  FOR_ITER            446  'to 446'
              412  UNPACK_SEQUENCE_2     2 
              414  STORE_FAST               'situation'
              416  STORE_FAST               'situation_data'

 L.1135       418  LOAD_FAST                'situation_data'
              420  LOAD_ATTR                first_assignment_pass_completed
          422_424  POP_JUMP_IF_TRUE    410  'to 410'

 L.1136       426  LOAD_FAST                'situation'
              428  LOAD_METHOD              on_first_assignment_pass_completed
              430  CALL_METHOD_0         0  '0 positional arguments'
              432  POP_TOP          

 L.1137       434  LOAD_FAST                'situation_data'
              436  LOAD_METHOD              on_first_assignment_pass_completed
              438  CALL_METHOD_0         0  '0 positional arguments'
              440  POP_TOP          
          442_444  JUMP_BACK           410  'to 410'
              446  POP_BLOCK        
            448_0  COME_FROM_LOOP      398  '398'
              448  POP_BLOCK        
              450  LOAD_CONST               None
            452_0  COME_FROM_WITH        8  '8'
              452  WITH_CLEANUP_START
              454  WITH_CLEANUP_FINISH
              456  END_FINALLY      

Parse error at or near `LOAD_SETCOMP' instruction at offset 134

    def _assign_sim_to_request(self, sim, request, trump_all_exclusions=False):
        with situations.situation_manager.DelayedSituationDestruction():
            data = self._sim_to_bouncer_sim_data.setdefault(sim, BouncerSimData(self, sim))
            excluded = data.add_request(request, trump_all_exclusions=trump_all_exclusions)
            for ex_request in excluded:
                self._unassign_sim_from_request_and_optionally_withdraw(sim, ex_request)

            request._assign_sim(sim)
            if request._is_fulfilled:
                self._unfulfilled_requests[request._unfulfilled_index].remove(request)
                self._fulfilled_requests.append(request)

    def _unassign_sim_from_request(self, sim, request, silently=False):
        data = self._sim_to_bouncer_sim_data.get(sim, None)
        if data:
            data.remove_request(request)
        request._unassign_sim(sim, silently)

    def _unassign_sim_from_request_and_optionally_withdraw(self, sim, request, silently=False):
        self._unassign_sim_from_request(sim, request, silently)
        if request._status != BouncerRequestStatus.DESTROYED:
            if request._is_obsolete:
                self.withdraw_request(request, reason='Sim reassigned')

    def _check_request_against_reservation_request(self, sim_id, request, check_exclusivity):
        if not check_exclusivity:
            return True
        if sim_id in self._reserved_sims:
            for request in self._reserved_sims[sim_id]:
                if request.exclusivity_compare(request) > 0:
                    return False

        return True

    def _can_assign_sim_id_to_request(self, sim_id, new_request, check_exclusivity=True):
        sim_info = services.sim_info_manager().get(sim_id)
        sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS) if sim_info is not None else None
        if sim is None:
            return True
        else:
            return self._check_request_against_reservation_request(sim_id, new_request, check_exclusivity) or False
        return self._can_assign_sim_to_request(sim, new_request, check_exclusivity=check_exclusivity)

    def _can_assign_sim_to_request(self, sim, new_request, check_exclusivity=True):
        if not new_request._can_assign_sim_to_request(sim):
            return False
        else:
            data = self._sim_to_bouncer_sim_data.get(sim, None)
            if data is None:
                return True
            return self._check_request_against_reservation_request(sim.sim_id, new_request, check_exclusivity) or False
        return data.can_assign_to_request(new_request, check_exclusivity=check_exclusivity)

    def _get_common_blacklists(self):
        active_household = services.active_household()
        sim_spawner_service = services.sim_spawner_service()
        spawning_sim_ids = sim_spawner_service.get_set_of_requested_sim_ids()
        if active_household is None:
            active_household_sim_ids = set()
        else:
            active_household_sim_ids = {sim_info.sim_id for sim_info in active_household.sim_info_gen()}
        active_lot_household = services.current_zone().get_active_lot_owner_household()
        if active_lot_household is None:
            active_lot_household_sim_ids = set()
        else:
            active_lot_household_sim_ids = {sim_info.sim_id for sim_info in active_lot_household.sim_info_gen()}
        return (spawning_sim_ids, active_household_sim_ids, active_lot_household_sim_ids)

    def _apply_common_blacklists(self, request, blacklist, spawning_sim_ids, active_household_sim_ids, active_lot_household_sim_ids):
        blacklist.update(request._get_blacklist())
        if request.common_blacklist_categories & SituationCommonBlacklistCategory.ACTIVE_HOUSEHOLD:
            blacklist.update(active_household_sim_ids)
        else:
            if request.common_blacklist_categories & SituationCommonBlacklistCategory.ACTIVE_LOT_HOUSEHOLD:
                blacklist.update(active_lot_household_sim_ids)
            if not request._constrained_sim_ids:
                blacklist.update(spawning_sim_ids)
            else:
                if request._for_persisted_sim:
                    blacklist -= request._constrained_sim_ids

    def _spawn_sim_for_next_request(self):
        if self._spawning_freeze_enabled:
            return
        if self._sim_filter_service_in_progress:
            return
        active_household = services.active_household()
        if active_household is None:
            return
        spawning_sim_ids, active_household_sim_ids, active_lot_household_sim_ids = self._get_common_blacklists()
        for unfulfilled_index in range(Bouncer.MAX_UNFULFILLED_INDEX):
            requests = self._unfulfilled_requests[unfulfilled_index]
            if not requests:
                continue
            requests = [request for request in requests if request._can_spawn_now(False) if request._status == BouncerRequestStatus.SUBMITTED]
            if not requests:
                continue
            request = sims4.random.random.choice(requests)
            self._sim_filter_service_in_progress = True
            request._status = BouncerRequestStatus.SIM_FILTER_SERVICE
            sim_constraints = list(request._constrained_sim_ids) if request._constrained_sim_ids else None
            blacklist = set()
            self._apply_common_blacklistsrequestblacklistspawning_sim_idsactive_household_sim_idsactive_lot_household_sim_ids
            self._set_request_for_sim_filter_gsi(request)
            services.sim_filter_service().submit_matching_filter(number_of_sims_to_find=1, sim_filter=(request._sim_filter),
              callback=(self._sim_filter_service_callback),
              callback_event_data=request,
              sim_constraints=sim_constraints,
              continue_if_constraints_fail=(request._continue_if_constraints_fail),
              blacklist_sim_ids=blacklist,
              requesting_sim_info=(request._requesting_sim_info),
              additional_filter_terms=(request.get_additional_filter_terms()),
              gsi_source_fn=(self.get_sim_filter_gsi_name))

    def _spawn_all_during_zone_spin_up(self):
        spawning_sim_ids, active_household_sim_ids, active_lot_household_sim_ids = self._get_common_blacklists()
        spawning_sim_ids = set()
        for unfulfilled_index in range(Bouncer.MAX_UNFULFILLED_INDEX):
            requests = tuple(self._unfulfilled_requests[unfulfilled_index])
            for request in requests:
                if request._status != BouncerRequestStatus.SUBMITTED:
                    continue
                if request._for_persisted_sim or request._can_spawn_now(True):
                    request._status = BouncerRequestStatus.SIM_FILTER_SERVICE
                    sim_constraints = list(request._constrained_sim_ids) if request._constrained_sim_ids else None
                    blacklist = set()
                    self._apply_common_blacklistsrequestblacklistspawning_sim_idsactive_household_sim_idsactive_lot_household_sim_ids
                    logger.debug('_spawn_all_during_zone_spin_up request:{} blacklist:{}', request, blacklist)
                    if request._for_persisted_sim:
                        sim_filter = request._job_type.should_revalidate_sim_on_load or None
                    else:
                        sim_filter = request._sim_filter
                    self._set_request_for_sim_filter_gsi(request)
                    filter_results = services.sim_filter_service().submit_matching_filter(number_of_sims_to_find=1, sim_filter=sim_filter,
                      sim_constraints=sim_constraints,
                      continue_if_constraints_fail=(request._continue_if_constraints_fail),
                      blacklist_sim_ids=blacklist,
                      requesting_sim_info=(request._requesting_sim_info),
                      allow_yielding=False,
                      additional_filter_terms=(request.get_additional_filter_terms()),
                      gsi_source_fn=(self.get_sim_filter_gsi_name))
                    if filter_results:
                        spawning_sim_ids.add(filter_results[0].sim_info.sim_id)
                    self._sim_filter_service_callback(filter_results, request)

    def _check_for_tardy_requests(self):
        for unfulfilled_index in range(Bouncer.MAX_UNFULFILLED_INDEX):
            requests = list(self._unfulfilled_requests[unfulfilled_index])
            for request in requests:
                if request._is_tardy:
                    request._situation.on_tardy_request(request)
                    if request._status != BouncerRequestStatus.DESTROYED:
                        request._reset_tardy()

    def _is_request_with_assigned_npc_who_is_not_leaving(self, request):
        sim = request.assigned_sim
        if not (sim is None or sim.sim_info).is_npc or sim.sim_info.lives_here:
            return False
        return services.sim_spawner_service().sim_is_leaving(sim) == False

    def _is_request_for_npc(self, request):
        sim = services.object_manager().get(request.requested_sim_id)
        if sim is None:
            return True
        return sim.sim_info.is_npc

    def _monitor_npc_soft_cap(self):
        if self._cap_cheat_enabled:
            return
            if services.active_household() is None:
                return
            if not services.current_zone().is_zone_running:
                return
            situation_manager = services.get_zone_situation_manager()
            sim_spawner_service = services.sim_spawner_service()
            if sim_spawner_service.number_of_npcs_instantiated > sim_spawner_service.npc_soft_cap:
                situation_manager.expedite_leaving()
            num_here_but_not_leaving = sim_spawner_service.number_of_npcs_instantiated - sim_spawner_service.number_of_npcs_leaving
            excess_npcs_not_leaving = num_here_but_not_leaving - sim_spawner_service.npc_soft_cap
            if excess_npcs_not_leaving > 0:
                self._make_npcs_leave_now_must_run(excess_npcs_not_leaving)
        elif excess_npcs_not_leaving == 0:
            unfulfilled_heap = self._get_unfulfilled_request_heap_by_best_klout(filter_func=(self._is_request_for_npc))
            fulfilled_heap = self._get_assigned_request_heap_by_worst_klout(filter_func=(self._is_request_with_assigned_npc_who_is_not_leaving))
            if unfulfilled_heap:
                if fulfilled_heap:
                    best_unfulfilled = heapq.heappop(unfulfilled_heap)
                    worst_fulfilled = heapq.heappop(fulfilled_heap)
                    if best_unfulfilled.klout < worst_fulfilled.klout:
                        situation_manager.make_sim_leave_now_must_run(worst_fulfilled.request.assigned_sim)

    def _get_assigned_request_heap_by_worst_klout(self, filter_func=None):
        klout_heap = []
        for sim_data in self._sim_to_bouncer_sim_data.values():
            request = sim_data.get_request_with_best_klout()
            if request is None:
                continue
            if filter_func is not None:
                if not filter_func(request):
                    continue
            klout = request._get_request_klout()
            if klout is None:
                continue
            heapq.heappush(klout_heap, _WorstRequestKlout(request=request, klout=klout))

        return klout_heap

    def _get_unfulfilled_request_heap_by_best_klout(self, filter_func=None):
        klout_heap = []
        for unfulfilled_index in range(Bouncer.MAX_UNFULFILLED_INDEX):
            requests = self._unfulfilled_requests[unfulfilled_index]
            for request in requests:
                klout = request._get_request_klout()
                if klout is not None:
                    if filter_func is not None:
                        if not filter_func(request):
                            continue
                    heapq.heappush(klout_heap, _BestRequestKlout(request=request, klout=klout))

        return klout_heap

    def _make_npcs_leave_now_must_run(self, sim_count):
        situation_manager = services.get_zone_situation_manager()
        klout_heap = self._get_assigned_request_heap_by_worst_klout(filter_func=(self._is_request_with_assigned_npc_who_is_not_leaving))
        while klout_heap and sim_count > 0:
            worst = heapq.heappop(klout_heap)
            situation_manager.make_sim_leave_now_must_run(worst.request.assigned_sim)
            sim_count -= 1

    def _sim_filter_service_callback(self, filter_results, bouncer_request):
        self._sim_filter_service_in_progress = False
        logger.debug('_sim_filter_service_callback for sims {} for request {}', filter_results, bouncer_request)
        if bouncer_request._status == BouncerRequestStatus.DESTROYED:
            return
        if bouncer_request._status != BouncerRequestStatus.SIM_FILTER_SERVICE:
            logger.error('_sim_filter_service_callback for wrong request!')
            return
        current_zone = services.current_zone()
        if current_zone.is_zone_shutting_down:
            return
        during_zone_spin_up = not current_zone.is_zone_running
        if filter_results:
            sim_info = filter_results[0].sim_info
            if sim_info.is_baby:
                logger.error('Bouncer request tried spawning baby which is invalid: {}', bouncer_request)
                bouncer_request._situation.on_failed_to_spawn_sim_for_request(bouncer_request)
                self.withdraw_request(bouncer_request, reason='Trying to spawn baby')
                return
            spin_up_action = bouncer_request._for_persisted_sim or SimZoneSpinUpAction.NONE
            if during_zone_spin_up:
                if bouncer_request.should_preroll_during_zone_spin_up:
                    spin_up_action = SimZoneSpinUpAction.PREROLL
                else:
                    bouncer_request._status = BouncerRequestStatus.SPAWN_REQUESTED
                    if bouncer_request.specific_location is not None:
                        spawn_strategy = sims.sim_spawner_service.SimSpawnLocationStrategy(bouncer_request.specific_location)
                    else:
                        if bouncer_request.specific_spawn_point is not None:
                            spawn_strategy = sims.sim_spawner_service.SimSpawnSpecificPointStrategy(spawn_point=(bouncer_request.specific_spawn_point), spawn_point_option=(bouncer_request.spawn_point_option),
                              spawn_action=(bouncer_request._spawn_action),
                              saved_spawner_tags=(bouncer_request.saved_spawner_tags))
                        else:
                            spawn_strategy = sims.sim_spawner_service.SimSpawnPointStrategy(spawner_tags=(bouncer_request.spawner_tags(during_zone_spin_up)), spawn_point_option=(bouncer_request.spawn_point_option),
                              spawn_action=(bouncer_request._spawn_action),
                              saved_spawner_tags=(bouncer_request.saved_spawner_tags),
                              spawn_at_lot=(bouncer_request.spawn_at_lot),
                              use_random_sim_spawner_tag=(bouncer_request.use_random_sim_spawner_tag))
                sim_spawn_request = sims.sim_spawner_service.SimSpawnRequest(sim_info,
                  (bouncer_request.sim_spawn_reason),
                  spawn_strategy,
                  secondary_priority=(bouncer_request._unfulfilled_index),
                  customer=self,
                  customer_data=bouncer_request,
                  spin_up_action=spin_up_action,
                  game_breaker=(bouncer_request.request_priority == BouncerRequestPriority.GAME_BREAKER))
                bouncer_request._sim_spawner_service_request = sim_spawn_request
                services.sim_spawner_service().submit_request(sim_spawn_request)
            else:
                listener_request = sims.sim_spawner_service.SimListenerRequest(sim_info,
                  customer=self, customer_data=bouncer_request)
                bouncer_request._sim_spawner_service_request = listener_request
                services.sim_spawner_service().submit_listener(listener_request)
        else:
            bouncer_request._situation.on_failed_to_spawn_sim_for_request(bouncer_request)
            self.withdraw_request(bouncer_request, reason='Failed to find/create SimInfo')

    def on_sim_creation_callback(self, sim, sim_spawner_service_request):
        logger.debug('on_sim_creation_callback request:{}', sim_spawner_service_request)
        bouncer_request = sim_spawner_service_request.customer_data
        if bouncer_request._status == BouncerRequestStatus.DESTROYED:
            return
            bouncer_request._sim_spawner_service_request = None
            if self._can_assign_sim_to_request(sim, bouncer_request):
                self._assign_sim_to_request(sim, bouncer_request)
                if sim.sim_info.is_npc and services.current_zone().is_zone_running:
                    sim.run_full_autonomy_next_ping()
        else:
            bouncer_request._status = BouncerRequestStatus.SUBMITTED

    def on_sim_creation_denied_callback(self, sim_spawner_service_request):
        logger.debug('on_sim_creation_denied_callback request:{}', sim_spawner_service_request)
        bouncer_request = sim_spawner_service_request.customer_data
        bouncer_request._situation.on_failed_to_spawn_sim_for_request(bouncer_request)
        self.withdraw_request(bouncer_request, reason='Failed to spawn in sim')

    def _on_end_sim_creation_notification(self, sim):
        if self._update_mode == _BouncerUpdateMode.FULLY_OPERATIONAL:
            self._assign_instanced_sims_to_unfulfilled_requests()

    def _sim_weakref_callback(self, sim):
        logger.debug('Bouncer:_sim_weakref_callback: {}', sim, owner='sscholl')
        data = self._sim_to_bouncer_sim_data.get(sim, None)
        if data is None:
            return
        requests_sim_was_in = list(data.requests)
        data.destroy()
        self._sim_to_bouncer_sim_data.pop(sim)
        for request in requests_sim_was_in:
            self._unassign_sim_from_request_and_optionally_withdraw(sim, request)

    def _all_requests_gen(self):
        for unfulfilled_index in range(Bouncer.MAX_UNFULFILLED_INDEX):
            for request in self._unfulfilled_requests[unfulfilled_index]:
                yield request

        for request in self._fulfilled_requests:
            yield request

    def set_sim_looking_for_new_situation(self, sim):
        data = self._sim_to_bouncer_sim_data.get(sim, None)
        if data is None:
            return
        data.looking_for_new_situation = True