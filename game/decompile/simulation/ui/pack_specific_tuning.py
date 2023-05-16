# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\ui\pack_specific_tuning.py
# Compiled at: 2021-04-29 14:56:21
# Size of source mod 2**32: 3993 bytes
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import TunableEnumFlags, TunableMapping, TunableReference, TunableTuple, OptionalTunable
from sims4.tuning.tunable_base import ExportModes
from venues.venue_enums import VenueFlags
import services, sims4.resources
logger = sims4.log.Logger('PackSpecificTuning', default_owner='stjulien')

def verify_venue_tuning(instance_class, tunable_name, source, value, **kwargs):
    venue_manager = services.get_instance_manager(sims4.resources.Types.VENUE)
    remapped_keys = venue_manager.remapped_keys
    if remapped_keys is not None:
        for stripped_key, pack_specific_key in remapped_keys.items():
            if pack_specific_key.group != 0:
                venue_tuning = venue_manager.get(stripped_key)
                if venue_tuning is not None and not venue_tuning.hide_from_buildbuy_ui:
                    if venue_tuning.gallery_upload_venue_type is None and value.get(venue_tuning) is None:
                        logger.error('PackSpecificTuning for venue is missing. {}', venue_tuning)


class PackSpecificTuning:
    VENUE_PACK_TUNING = TunableMapping(description="\n        Venue tuning that is needed by UI when that venue's pack is not installed.\n        ",
      key_name='venue_id',
      key_type=TunableReference(description='\n            Reference to the venue that this data represents\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.VENUE)),
      pack_safe=True),
      value_name='data',
      value_type=TunableTuple(description="\n            Venue data that is shown in the UI when this venue's pack is not installed.\n            ",
      gallery_download_venue=OptionalTunable(description='\n                If tuned, the tuned venue tuning will be substituted if this\n                venue is downloaded from the gallery by a player who is not\n                entitled to it. The default behavior is to substitute the\n                generic venue. This tuned venue will also determine download\n                compatibility (for instance, only residential venues can be \n                downloaded to owned residential venues).\n                ',
      tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.VENUE)))),
      venue_name=TunableLocalizedStringFactory(description='\n                Name that will be displayed for the venue when the pack containing \n                that venue is not installed\n                '),
      venue_flags=TunableEnumFlags(description='\n                Venue flags used to mark a venue with specific properties.\n                ',
      enum_type=VenueFlags,
      allow_no_flags=True,
      default=(VenueFlags.NONE)),
      export_class_name='VenueDataTuple'),
      tuple_name='VenuePackTuning',
      export_modes=(ExportModes.All),
      verify_tunable_callback=verify_venue_tuning)