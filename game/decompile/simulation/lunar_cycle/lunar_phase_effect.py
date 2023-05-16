# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\lunar_cycle\lunar_phase_effect.py
# Compiled at: 2022-06-13 18:18:17
# Size of source mod 2**32: 9128 bytes
import services, sims4.resources
from buffs.tunable import TunableBuffReference, BuffReference
from event_testing.resolver import SingleSimResolver
from interactions.utils.loot_ops import DialogLootOp, AddTraitLootOp
from sims4.localization import TunableLocalizedString
from sims4.tuning.instances import TunedInstanceMetaclass
from sims4.tuning.tunable import TunableSimMinute, TunableVariant, TunableList, OptionalTunable
from sims4.utils import classproperty
from statistics.commodity import RuntimeCommodity, CommodityTimePassageFixupType, CommodityState
from statistics.statistic_ops import TunableStatisticChange, StatisticOperation
logger = sims4.log.Logger('LunarPhaseEffect', default_owner='jdimailig')

class LunarPhaseEffect(metaclass=TunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.LUNAR_CYCLE)):
    INSTANCE_SUBCLASSES_ONLY = True

    @classproperty
    def is_tracked_effect(cls):
        return False

    @classmethod
    def apply_lunar_effect(cls, tracker, start_time):
        raise NotImplementedError('LunarPhaseEffect apply_lunar_effect must be implemented in subclasses')

    @classmethod
    def get_lunar_effect_tooltip(cls, sim_info):
        pass


class _LunarEffectBuffReference(BuffReference):
    __slots__ = ('_tooltip_text', )

    def __init__(self, tooltip_text=None, **kwargs):
        (super().__init__)(**kwargs)
        self._tooltip_text = tooltip_text

    @property
    def tooltip_text(self):
        return self._tooltip_text


class _TunableLunarEffectBuffReference(TunableBuffReference):
    __slots__ = ()
    FACTORY_TYPE = _LunarEffectBuffReference

    def __init__(self, **kwargs):
        (super().__init__)(tooltip_text=OptionalTunable(description='\n                            If set, specify a tooltip text to describe the effect in lunar cycle tooltip \n                            when this buff is active on the Sim.\n                            ',
                         tunable=TunableLocalizedString(description='\n                                The description of the lunar effect. This will be displayed in the lunar cycle tooltip.\n                                ')), **kwargs)


class LunarPhaseEffectBuffs(LunarPhaseEffect):
    INSTANCE_TUNABLES = {'effect_duration':TunableSimMinute(description='\n            The duration of the effect.  This duration will be enforced so that the buffs are aligned with \n            the expected length of the lunar effect.\n            \n            e.g. lunar effect was expected to be started at 8pm and last 180 minutes.  Sim is created/spun up and\n            gets a lunar effect buff applied at 9:15pm.  The lunar effect buff will be updated so it properly ends\n            at 11pm, as expected by the lunar effect duration.\n            ',
       default=240,
       minimum=1,
       maximum=1440), 
     'effect_buffs':TunableList(description='\n            List of buffs to attempt to apply during this lunar phase.  If a buff reason tooltip is tuned for a\n            successfully applied buff, that tooltip is used to populate a lunar effect tooltip in the UI.\n            ',
       tunable=_TunableLunarEffectBuffReference(pack_safe=True))}

    @classmethod
    def _tuning_loaded_callback(cls):
        for buff_reference in cls.effect_buffs:
            if buff_reference.buff_type.commodity is not None:
                buff_type = buff_reference.buff_type
                logger.error('\n                    Lunar effect buff {} should not have a commodity {} attached as we will generate a unique one\n                    for the lunar phase effect {}.  If it is linked to another lunar effect, please create a new buff\n                    unique to this effect.\n                    ', buff_type, buff_type.commodity, cls)
                continue
            cls._create_runtime_commodity_for_buff(buff_reference)

    @classmethod
    def _create_runtime_commodity_for_buff(cls, buff_reference):
        buff_type = buff_reference.buff_type
        lunar_effect_duration = cls.effect_duration
        lunar_effect_commodity_name = '{}_{}'.format(cls.__name__, buff_type.__name__)
        lunar_effect_commodity = RuntimeCommodity.generate(lunar_effect_commodity_name)
        lunar_effect_commodity.decay_rate = 1
        lunar_effect_commodity.convergence_value = 0
        lunar_effect_commodity.remove_on_convergence = True
        lunar_effect_commodity.visible = False
        lunar_effect_commodity.max_value_tuning = lunar_effect_duration
        lunar_effect_commodity.min_value_tuning = 0
        lunar_effect_commodity.initial_value = lunar_effect_duration
        lunar_effect_commodity._time_passage_fixup_type = CommodityTimePassageFixupType.FIXUP_USING_TIME_ELAPSED
        lunar_effect_commodity.persisted_tuning = True
        new_state_add_buff = CommodityState(value=0.1, buff=buff_reference)
        new_state_remove_buff = CommodityState(value=0, buff=(BuffReference()))
        lunar_effect_commodity.commodity_states = [
         new_state_remove_buff, new_state_add_buff]
        buff_type.add_owning_commodity(lunar_effect_commodity)

    @classproperty
    def is_tracked_effect(cls):
        return True

    @classmethod
    def apply_lunar_effect(cls, tracker, start_time):
        if not tracker.should_apply_lunar_effect(cls, start_time):
            return
        sim_info = tracker.sim_info
        for buff_reference in cls.effect_buffs:
            buff_type = buff_reference.buff_type
            if sim_info.add_buff_from_op(buff_type, buff_reason=(buff_reference.buff_reason)):
                effect_buff_commodity = sim_info.get_statistic((buff_type.commodity), add=False)
                effect_buff_commodity.update_commodity_to_time(start_time, update_callbacks=True)

        tracker.track_lunar_effect_applied(cls, start_time)

    @classmethod
    def get_lunar_effect_tooltip(cls, sim_info):
        for buff_reference in cls.effect_buffs:
            if buff_reference.tooltip_text is not None and sim_info.has_buff(buff_reference.buff_type):
                return buff_reference.tooltip_text


class LunarPhaseEffectOperation(TunableVariant):

    def __init__(self, **kwargs):
        (super().__init__)(dialog=DialogLootOp.TunableFactory(), 
         trait_add=AddTraitLootOp.TunableFactory(), 
         statistics=TunableStatisticChange(statistic_override=StatisticOperation.get_statistic_override(pack_safe=True)), 
         default='dialog', **kwargs)


class LunarPhaseEffectOneShot(LunarPhaseEffect):
    INSTANCE_TUNABLES = {'effects': TunableList(description='\n            Operations to run as part of this lunar effect.\n            ',
                  tunable=(LunarPhaseEffectOperation()))}

    @classmethod
    def apply_lunar_effect(cls, tracker, _start_time):
        resolver = SingleSimResolver(tracker.sim_info)
        for effect in cls.effects:
            effect.apply_to_resolver(resolver)