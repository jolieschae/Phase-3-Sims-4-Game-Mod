# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\looping_object_situation_start_immediate_interaction.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 5144 bytes
from interactions.aop import AffordanceObjectPair
from interactions.base.basic import BasicExtraVariant
from interactions.base.super_interaction import SuperInteraction
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableTuple, TunableReference, OptionalTunable, TunablePackSafeReference, TunableList
from sims4.utils import flexmethod
from singletons import DEFAULT
from situations.tunable import TunableSituationStart
import services, sims4.resources

class LoopingObjectSituationStartImmediateInteraction(SuperInteraction):
    INSTANCE_TUNABLES = {'object_data':TunableList(description='\n            All of the data needed to run the specified interaction and have\n            it create an object.\n            ',
       tunable=TunableTuple(description='\n                A tuple that holds the needed information for each interaction\n                created by this interaction.\n                ',
       new_display_name=TunableLocalizedStringFactory(description='\n                    The localized name of this interaction.  It takes two tokens, the\n                    actor (0) and target object (1) of the interaction.\n                    '),
       pie_menu_category=OptionalTunable(description='\n                    Pie menu category for the interaction created with this\n                    object data.\n                    ',
       tunable=TunableReference(description='\n                        Reference to the pie menu data used for this object\n                        data.\n                        ',
       manager=(services.get_instance_manager(sims4.resources.Types.PIE_MENU_CATEGORY)),
       pack_safe=True)),
       basic_extra=BasicExtraVariant(description='\n                    Basic extra to add to the looping interaction when it gets\n                    run. \n                    \n                    Example: tuning a create object basic extra to place down\n                    a placemat.\n                    '))), 
     'reuseable_affordance':TunableReference(description='\n            The interaction to be passed to the situation and used to \n            repeatedly run the tuned basic extras.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION)), 
     'looping_situation':TunableSituationStart()}

    def __init__(self, *args, selected_object_data=None, reuseable_affordance=None, looping_situation=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.selected_object_data = selected_object_data
        self.reuseable_affordance = reuseable_affordance
        self.looping_situation = looping_situation

    @flexmethod
    def get_pie_menu_category(cls, inst, **interaction_parameters):
        if inst is not None:
            return inst.selected_object_data.pie_menu_category
        return interaction_parameters['selected_object_data'].pie_menu_category

    @flexmethod
    def _get_name(cls, inst, target=DEFAULT, context=DEFAULT, service_tuning=None, outfit_index=None, **interaction_parameters):
        if inst is not None:
            return inst.selected_object_data.new_display_name()
        return interaction_parameters['selected_object_data'].new_display_name()

    @classmethod
    def potential_interactions(cls, target, context, **kwargs):
        for data in cls.object_data:
            yield AffordanceObjectPair(cls, target, cls, None, selected_object_data=data, 
             reuseable_affordance=cls.reuseable_affordance, 
             looping_situation=cls.looping_situation, **kwargs)

    def _run_interaction_gen(self, timeline):
        kwargs = {}
        kwargs['interaction'] = self.reuseable_affordance
        kwargs['basic_extra'] = self.selected_object_data.basic_extra
        (self.looping_situation)((self.get_resolver()), **kwargs)()
        if False:
            yield None


lock_instance_tunables(LoopingObjectSituationStartImmediateInteraction, _saveable=None)