# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\headlines\headline_op.py
# Compiled at: 2021-05-05 20:20:43
# Size of source mod 2**32: 3524 bytes
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import TunableReference, TunableSet, Tunable, TunableVariant, TunableTuple, OptionalTunable, TunablePackSafeReference
import services, sims4.resources, telemetry_helper
logger = sims4.log.Logger('HeadlineOp', default_owner='yozhang')
TELEMETRY_GROUP_HEADLINES = 'HDLN'
TELEMETRY_FIELD_HEADLINE = 'hdln'
TELEMETRY_FIELD_AMOUNT = 'amnt'
TELEMETRY_FIELD_LTUN = 'ltun'
headline_telemetry_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_HEADLINES)

class HeadlineOp(BaseLootOperation):
    FACTORY_TUNABLES = {'headline':TunableReference(description='\n            The headline that we want to send down when this loot is applied.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.HEADLINE)), 
     'amount':Tunable(description='\n            The amount we want to apply to the headline message. Value applied here has no gameplay impact.\n            ',
       tunable_type=float,
       default=0.0), 
     'telemetry_headline_info':TunableTuple(send_telemetry_event=Tunable(description='\n                If True, send a telemetry message when this loot is run.\n                ',
       tunable_type=bool,
       default=False),
       linked_tuning_instance=OptionalTunable(description='\n                If enabled, send the tuning instance id of the linked tuning\n                as an extra field with the headline telemetry message.\n                ',
       tunable=TunableVariant(description='\n                    The tuning instance associated with this headline.\n                    ',
       preference_instance=TunablePackSafeReference(description='\n                        The preference associated with this headline.\n                        ',
       manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
       class_restrictions='Preference'))))}

    def __init__(self, *args, headline, amount, telemetry_headline_info, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.headline = headline
        self.amount = amount
        self.telemetry_headline_info = telemetry_headline_info

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not subject.is_sim:
            logger.error('Attempting to play a headline on subject: {}, that is not a Sim. Loot: {}', self.subject, self)
            return
        self.headline.send_headline_message(subject.sim_info, self.amount)
        if self.telemetry_headline_info.send_telemetry_event:
            with telemetry_helper.begin_hook(headline_telemetry_writer, TELEMETRY_GROUP_HEADLINES, sim_info=(subject.sim_info)) as (hook):
                hook.write_guid(TELEMETRY_FIELD_HEADLINE, self.headline.guid64)
                hook.write_int(TELEMETRY_FIELD_AMOUNT, self.amount)
                if self.telemetry_headline_info.linked_tuning_instance is not None:
                    hook.write_guid(TELEMETRY_FIELD_LTUN, self.telemetry_headline_info.linked_tuning_instance.guid64)