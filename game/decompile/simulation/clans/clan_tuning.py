# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\clans\clan_tuning.py
# Compiled at: 2022-06-13 18:18:17
# Size of source mod 2**32: 4040 bytes
import enum, services, sims4.resources
from interactions.utils.display_mixin import get_display_mixin
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableList, TunableReference, TunableEnumEntry, TunablePackSafeReference
from sims4.tuning.tunable_base import ExportModes
_ClanDisplayMixin = get_display_mixin(has_description=True, has_icon=True, has_tooltip=True, has_secondary_icon=True, export_modes=(ExportModes.All),
  enabled_by_default=True)

class ClanValue(_ClanDisplayMixin, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.CLAN_VALUE)):
    INSTANCE_TUNABLES = {'discipline_ranked_stat': TunableReference(description='\n            The ranked statistic representing how well a Sim is following this clan value.\n            ',
                                 manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
                                 class_restrictions=('RankedStatistic', ),
                                 export_modes=(ExportModes.All))}


class Clan(_ClanDisplayMixin, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.CLAN)):
    INSTANCE_TUNABLES = {'clan_values':TunableList(description='\n            The list of values that members of this clan should follow.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.CLAN_VALUE))),
       export_modes=ExportModes.All), 
     'clan_hierarchy_ranked_stat':TunableReference(description='\n            The ranked statistic that is used to represent a Sims hierarchy within the clan.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC),
       class_restrictions=('RankedStatistic', ),
       export_modes=ExportModes.All), 
     'clan_trait':TunableReference(description='\n            The trait that represents being a member of this clan.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.TRAIT))}


class ClanOpType(enum.Int):
    ADD_SIM_TO_CLAN = ...
    REMOVE_SIM_FROM_CLAN = ...
    MAKE_CLAN_LEADER = ...


class ClanLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'operation':TunableEnumEntry(description='\n            The operation to perform.\n            ',
       tunable_type=ClanOpType,
       default=ClanOpType.ADD_SIM_TO_CLAN), 
     'clan':TunablePackSafeReference(description='\n            A reference to the clan for which this operation is being applied.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CLAN))}

    def __init__(self, *args, operation=None, clan=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._operation = operation
        self._clan = clan

    def _apply_to_subject_and_target(self, subject, target, resolver):
        clan_service = services.clan_service()
        if clan_service is None:
            return
        elif self._operation == ClanOpType.ADD_SIM_TO_CLAN:
            clan_service.add_sim_to_clan(subject, self._clan)
        else:
            if self._operation == ClanOpType.REMOVE_SIM_FROM_CLAN:
                clan_service.remove_sim_from_clan(subject, self._clan)
            else:
                if self._operation == ClanOpType.MAKE_CLAN_LEADER:
                    clan_service.reassign_clan_leader(subject, self._clan)