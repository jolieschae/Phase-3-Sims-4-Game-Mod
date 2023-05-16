# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\photo_commands.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 6530 bytes
from crafting.photography import Photography
from crafting.photography_enums import CameraMode, CameraQuality, PhotoStyleType, PhotoSize, PhotoOrientation
from event_testing import test_events
from interactions.interaction_finisher import FinishingType
import services, sims4.commands
logger = sims4.log.Logger('Photography')

@sims4.commands.Command('photography.get_photo_list', command_type=(sims4.commands.CommandType.Live))
def get_photo_list(*photo_list: str, _connection=None):
    services.get_event_manager().process_event(test_events.TestEvent.ExitedPhotoMode)
    if photo_list:
        photo_service = services.get_photography_service()
        photo_iter = iter(photo_list)
        session_data_string = next(photo_iter)
        camera_mode, camera_quality, target_obj_id, photographer_sim_id, *target_sim_ids = session_data_string.split(',')
        camera_mode = CameraMode(camera_mode)
        camera_quality = CameraQuality(camera_quality)
        target_obj_id = int(target_obj_id)
        photographer_sim_id = int(photographer_sim_id)
        target_sim_ids = [int(sim_id) for sim_id in target_sim_ids]
        sim_info_manager = services.sim_info_manager()
        photographer_sim_info = sim_info_manager.get(photographer_sim_id)
        if photographer_sim_info is None:
            logger.error('create_photo_from_photo_data: photographer_sim_info could not be found.', owner='jwilkinson')
            photo_service.cleanup()
            return
        photographer_sim = photographer_sim_info.get_sim_instance()
        if photographer_sim is None:
            logger.error('create_photo_from_photo_data: photographer_sim could not be found.', owner='jwilkinson')
            photo_service.cleanup()
            return
        user_took_photo = False
        for photo_string in photo_iter:
            user_took_photo = True
            photo_data = photo_string.split(',')
            resource_key = int(photo_data[0])
            resource_key_type = int(photo_data[1])
            resource_key_group = int(photo_data[2])
            res_key = sims4.resources.Key(resource_key_type, resource_key, resource_key_group)
            photo_style = PhotoStyleType(photo_data[3])
            photo_size = PhotoSize(photo_data[4])
            photo_orientation = PhotoOrientation(photo_data[5])
            time_stamp = photo_data[6]
            if len(photo_data) > 7:
                selected_mood_param = photo_data[7]
            else:
                selected_mood_param = None
            second_res_key = None
            if camera_mode is CameraMode.DECORATOR_MODE:
                large_photo_string = next(photo_iter)
                large_photo_data = large_photo_string.split(',')
                large_resource_key = int(large_photo_data[0])
                large_resource_key_type = int(large_photo_data[1])
                large_resource_key_group = int(large_photo_data[2])
                second_res_key = sims4.resources.Key(large_resource_key_type, large_resource_key, large_resource_key_group)
            Photography.create_photo_from_photo_data(camera_mode, camera_quality, photographer_sim_id, target_obj_id, target_sim_ids, res_key, second_res_key, photo_style, photo_size, photo_orientation, photographer_sim_info, photographer_sim, time_stamp, selected_mood_param)

        if user_took_photo:
            photo_service.apply_loot_for_photo(photographer_sim_info)
        else:
            photo_for_reference = CameraMode.is_for_reference(camera_mode)
            if photo_for_reference:
                for si in photographer_sim.get_running_and_queued_interactions_by_tag({Photography.PAINTING_INTERACTION_TAG}):
                    if si.target is None:
                        continue
                    painting = si.target
                    if painting.id != target_obj_id:
                        continue
                    si.cancel((FinishingType.OBJECT_CHANGED), cancel_reason_msg='Did not take reference photo.')
                    if painting is not None:
                        si.set_target(None)
                        break

                current_zone = services.current_zone()
                painting = current_zone.object_manager.get(target_obj_id)
                if not painting:
                    painting = current_zone.inventory_manager.get(target_obj_id)
                if painting:
                    painting.make_transient()
            photo_service.cleanup()