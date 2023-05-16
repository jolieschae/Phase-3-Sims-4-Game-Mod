# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_rule_set.py
# Compiled at: 2022-03-10 20:35:10
# Size of source mod 2**32: 3195 bytes
import services, sims4
logger = sims4.log.Logger('StoryProgressionRuleSet', default_owner='bnguyen')

class StoryProgressionRuleSet:
    __slots__ = [
     '_enabled', '_rules']

    def __init__(self, rule_set_proto, **kwargs):
        self._enabled = False
        self._rules = {}
        if rule_set_proto is not None:
            self._enabled = rule_set_proto.enabled
            for rule_data in rule_set_proto.rules:
                self._rules[rule_data.rule_id] = rule_data.enabled

    @property
    def enabled(self):
        return self._enabled

    @property
    def rules(self):
        return self._rules

    def is_rule_enabled(self, rule_id):
        if rule_id in self._rules:
            return self._rules[rule_id]
        return False

    def verify(self, rules):
        if not self.enabled:
            return False
        if rules is not None:
            for rule in rules:
                if not self.is_rule_enabled(rule.guid64):
                    return False

        return True


class HouseholdStoryProgressionRuleSet(StoryProgressionRuleSet):
    __slots__ = [
     '_parent_rule_set']

    def __init__(self, rule_set_proto, household=None, **kwargs):
        (super().__init__)(rule_set_proto, **kwargs)
        self._parent_rule_set = None
        if household is None:
            logger.error('No household provided for HouseholdStoryProgressionRuleSet')
            return
        else:
            story_progression_service = services.get_story_progression_service()
            if household.is_player_household:
                self._parent_rule_set = story_progression_service.protected_households_rule_set
            else:
                self._parent_rule_set = story_progression_service.unprotected_households_rule_set

    @property
    def enabled(self):
        if len(self._rules) == 0:
            if self._parent_rule_set:
                return self._parent_rule_set.enabled
            return False
        return super().enabled

    def is_rule_enabled(self, rule_id):
        if len(self._rules) == 0:
            if self._parent_rule_set:
                return self._parent_rule_set.is_rule_enabled(rule_id)
            return False
        return super().is_rule_enabled(rule_id)