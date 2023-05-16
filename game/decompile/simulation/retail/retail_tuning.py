# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\retail\retail_tuning.py
# Compiled at: 2016-05-10 19:22:35
# Size of source mod 2**32: 1573 bytes
from business.business_enums import BusinessAdvertisingType
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry, TunableReference
import services, sims4.resources

class RetailTuning:
    ADVERTISING_COMMODITY_MAP = TunableMapping(description='\n        The mapping between advertising enum and the advertising data for\n        that type.\n        ',
      key_name='advertising_enum',
      key_type=TunableEnumEntry(description='\n            The Advertising Type .\n            ',
      tunable_type=BusinessAdvertisingType,
      default=(BusinessAdvertisingType.INVALID),
      invalid_enums=(
     BusinessAdvertisingType.INVALID,)),
      value_name='advertising_commodity',
      value_type=TunableReference(description='\n            The commodity that will be added to the lot when this\n            advertising type is chosen. This commodity is applied via\n            the Advertising Interaction. This makes it easier for design\n            to tune differences in how each business handles\n            advertising. i.e. Retail allows advertising on multiple\n            channels at the same time while restaurants only allow one\n            advertisement at a time.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
      class_restrictions=('Commodity', ),
      pack_safe=True))