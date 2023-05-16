# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\canvas_component.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 39321 bytes
import random
from protocolbuffers import SimObjectAttributes_pb2 as persistence_protocols, DistributorOps_pb2
from distributor.ops import CompositeThumbnail
from distributor.system import Distributor
from event_testing.resolver import SingleSimResolver
from interactions import ParticipantTypeSingle, ParticipantType, ParticipantTypeSim, ParticipantTypeSingleSim
from interactions.utils.interaction_elements import XevtTriggeredElement
from objects import PaintingState, PuzzleState
from typing import Union
from objects.components import Component, componentmethod_with_fallback
from objects.components.types import STORED_SIM_INFO_COMPONENT
from objects.hovertip import TooltipFieldsComplete
from objects.system import create_object
from sims.outfits.outfit_enums import OutfitCategory
from sims4.tuning.dynamic_enum import DynamicEnumFlags
from sims4.tuning.tunable import HasTunableFactory, TunableEnumFlags, TunableEnumEntry, TunableVariant, TunableResourceKey, HasTunableSingletonFactory, AutoFactoryInit, TunableList, TunableTuple, OptionalTunable, Tunable, TunableColor, TunableReference, TunableRange
from tunable_multiplier import TunableMultiplier
import distributor.fields, distributor.ops, enum, objects.components.types, services, sims4, zone_types

class CanvasType(DynamicEnumFlags):
    NONE = 0


class CanvasStateType(enum.Int, export=False):
    PAINTING_CROSSSTITCH = 0
    PUZZLE = 1


class PortraitType(enum.Int):
    NONE = 0
    AUTOGRAPH = 1
    GRADUATION = 2
    HS_GRADUATION = 3


logger = sims4.log.Logger('Canvas')

class CanvasComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=objects.components.types.CANVAS_COMPONENT, persistence_key=persistence_protocols.PersistenceMaster.PersistableData.CanvasComponent):
    FACTORY_TUNABLES = {'canvas_types': TunableEnumFlags(CanvasType, (CanvasType.NONE), description="\n            A painting texture must support at least one of these canvas types\n            to be applied to this object's painting area.\n            ")}

    def __init__(self, owner, *args, **kwargs):
        (super().__init__)(owner, *args, **kwargs)
        self.time_stamp = None
        self._painting_state = None
        self._canvas_state_type = None

    def save_additional_data(self, canvas_data):
        pass

    def load_additional_data(self, canvas_data):
        pass

    def save(self, persistence_master_message):
        if self._painting_state is not None:
            persistable_data = persistence_protocols.PersistenceMaster.PersistableData()
            persistable_data.type = persistence_protocols.PersistenceMaster.PersistableData.CanvasComponent
            canvas_data = persistable_data.Extensions[persistence_protocols.PersistableCanvasComponent.persistable_data]
            canvas_data.texture_id = self._painting_state.texture_id
            canvas_data.reveal_level = self._painting_state.reveal_level
            canvas_data.effect = self._painting_state.effect
            if self._painting_state.overlay_texture_id is not None:
                canvas_data.overlay_texture_id = self._painting_state.overlay_texture_id
            if self._painting_state.reveal_texture_id is not None:
                canvas_data.reveal_texture_id = self._painting_state.reveal_texture_id
            if self._canvas_state_type == CanvasStateType.PUZZLE:
                if self._painting_state.reveal_texture_id_b is not None:
                    canvas_data.reveal_texture_id_B = self._painting_state.reveal_texture_id_b
                if self._painting_state.is_linked_canvas is not None:
                    canvas_data.is_linked_canvas = self._painting_state.is_linked_canvas
            if self._painting_state.stage_texture_id is not None:
                canvas_data.stage_texture_id = self._painting_state.stage_texture_id
            if self.time_stamp:
                canvas_data.time_stamp = self.time_stamp
            self.save_additional_data(canvas_data)
            persistence_master_message.data.extend([persistable_data])

    def load(self, persistable_data):
        canvas_data = persistable_data.Extensions[persistence_protocols.PersistableCanvasComponent.persistable_data]
        if canvas_data.time_stamp:
            self.time_stamp = canvas_data.time_stamp
        else:
            if canvas_data.HasField('stage_texture_id'):
                stage_texture_id = canvas_data.stage_texture_id
            else:
                stage_texture_id = None
            if canvas_data.HasField('overlay_texture_id'):
                overlay_texture_id = canvas_data.overlay_texture_id
            else:
                overlay_texture_id = None
            if canvas_data.HasField('reveal_texture_id'):
                reveal_texture_id = canvas_data.reveal_texture_id
            else:
                reveal_texture_id = None
            if canvas_data.HasField('reveal_texture_id_B'):
                reveal_texture_id_b = canvas_data.reveal_texture_id_B
            else:
                reveal_texture_id_b = None
            if canvas_data.HasField('is_linked_canvas'):
                is_linked_canvas = canvas_data.is_linked_canvas
            else:
                is_linked_canvas = None
            self.load_additional_data(canvas_data)
            self._canvas_state_type = CanvasStateType.PUZZLE if reveal_texture_id_b is not None else CanvasStateType.PAINTING_CROSSSTITCH
            if self._canvas_state_type == CanvasStateType.PUZZLE:
                self.painting_state = PuzzleState((canvas_data.texture_id), (canvas_data.reveal_level),
                  False,
                  (canvas_data.effect),
                  overlay_texture_id=overlay_texture_id,
                  reveal_texture_id=reveal_texture_id,
                  reveal_texture_id_b=reveal_texture_id_b,
                  is_linked_canvas=is_linked_canvas)
            else:
                self.painting_state = PaintingState(canvas_data.texture_id, canvas_data.reveal_level, False, canvas_data.effect, stage_texture_id, overlay_texture_id, reveal_texture_id)

    @distributor.fields.ComponentField(op=(distributor.ops.SetPaintingState), default=None)
    def painting_state(self) -> Union[(PaintingState, PuzzleState)]:
        return self._painting_state

    @painting_state.setter
    def painting_state(self, value: Union[(PaintingState, PuzzleState)]):
        self._painting_state = value
        if self._canvas_state_type is None:
            self._canvas_state_type = CanvasStateType.PUZZLE if isinstance(value, PuzzleState) else CanvasStateType.PAINTING_CROSSSTITCH
        if self.owner.linked_object_component is not None:
            if self._canvas_state_type == CanvasStateType.PUZZLE:
                if not self._painting_state.is_linked_canvas:
                    self.owner.linked_object_component.register_relink_callback(self._update_linked_objects)

    def _update_linked_objects(self):
        value = self._painting_state.get_at_level(self._painting_state.REVEAL_LEVEL_MAX)
        value = value.set_is_linked_canvas(True)
        for linked_object in self.owner.linked_object_component.get_linked_objects_gen():
            if linked_object.canvas_component is not None:
                linked_object.canvas_component.painting_state = value

    @property
    def canvas_state_type(self):
        return self._canvas_state_type

    @property
    def painting_reveal_level(self) -> int:
        if self.painting_state is not None:
            return self.painting_state.reveal_level

    @painting_reveal_level.setter
    def painting_reveal_level(self, reveal_level: int):
        if self.painting_state is not None:
            self.painting_state = self.painting_state.get_at_level(reveal_level)

    @property
    def painting_effect(self) -> int:
        if self.painting_state is not None:
            return self.painting_state.effect

    @painting_effect.setter
    def painting_effect(self, effect: int):
        if self.painting_state is not None:
            self.painting_state = self.painting_state.get_with_effect(effect)

    def set_painting_texture_id(self, texture_id):
        if self.painting_state is not None:
            self.painting_state = self.painting_state.set_texture_id(texture_id)
        else:
            logger.error('Object {} has no painting or puzzle state and its trying to set a custom texture', (self.owner), owner='camilogarcia')

    @componentmethod_with_fallback((lambda msg: None))
    def populate_icon_canvas_texture_info(self, msg):
        if self.painting_state is not None:
            if msg is not None:
                msg.texture_id = self.painting_state.texture_id
                msg.texture_effect = self.painting_state.effect
                msg.canvas_state_type = int(self._canvas_state_type)

    @componentmethod_with_fallback((lambda *_, **__: None))
    def get_canvas_texture_id(self):
        if self.painting_state is not None:
            return self.painting_state.texture_id

    @componentmethod_with_fallback((lambda *_, **__: None))
    def get_canvas_texture_effect(self):
        return self.painting_effect

    def set_composite_image(self, resource_key, resource_key_type, resource_key_group, *args, **kwargs):
        res_key = sims4.resources.Key(resource_key_type, resource_key, resource_key_group)
        painting_state = PaintingState.from_key(res_key, PaintingState.REVEAL_LEVEL_MAX, False, 0)
        self.painting_state = painting_state


class FamilyPortraitComponent(CanvasComponent):
    FACTORY_TUNABLES = {'background_image': TunableResourceKey(description='\n            The background image for the family portrait.\n            ',
                           resource_types=(sims4.resources.CompoundTypes.IMAGE),
                           default=None)}

    def __init__(self, owner, *args, **kwargs):
        (super().__init__)(owner, *args, **kwargs)
        self.outfit_category = OutfitCategory.EVERYDAY
        self.locked = False
        self.no_op_version = 0
        self.ignore_last_update_composite_image = False

    def _should_update_new_composite_image(self):
        if self._painting_state is None:
            return True
        return not self.ignore_last_update_composite_image

    def set_composite_image(self, resource_key, resource_key_type, resource_key_group, no_op_version):
        if self._should_update_new_composite_image():
            super().set_composite_image(resource_key, resource_key_type, resource_key_group)
            self.no_op_version = no_op_version
        self.ignore_last_update_composite_image = False

    def save_additional_data(self, canvas_data):
        canvas_data.locked = self.locked
        canvas_data.outfit_category = self.outfit_category
        canvas_data.no_op_version = self.no_op_version

    def load_additional_data(self, canvas_data):
        if canvas_data.HasField('outfit_category'):
            self.outfit_category = canvas_data.outfit_category
        else:
            if canvas_data.HasField('locked'):
                self.locked = canvas_data.locked
            if canvas_data.HasField('no_op_version'):
                self.no_op_version = canvas_data.no_op_version
            current_zone = services.current_zone()
            if current_zone is not None and current_zone.is_zone_running:
                self.ignore_last_update_composite_image = True

    def on_add(self, *_, **__):
        services.current_zone().register_callback(zone_types.ZoneState.HOUSEHOLDS_AND_SIM_INFOS_LOADED, self._on_households_loaded)

    def _on_households_loaded(self, *_, **__):
        self.update_composite_image()

    def update_composite_image(self, force_rebuild_thumb=False):
        if self.locked:
            return
        household_id = self.owner.get_household_owner_id()
        if household_id is None:
            return
        thumb_url = 'img://thumbs/sims/h_0x{:016x}_x_{:d}'.format(household_id, int(self.outfit_category))
        op = CompositeThumbnail(thumb_url, (self.background_image.instance), (self.owner.id), (self.no_op_version), force_rebuild_thumb=force_rebuild_thumb)
        Distributor.instance().add_op_with_no_owner(op)


class SimPortraitComponent(CanvasComponent):
    FACTORY_TUNABLES = {'background_image':TunableResourceKey(description='\n            The background image for the portrait.\n            ',
       resource_types=sims4.resources.CompoundTypes.IMAGE,
       default=None), 
     'fame_autograph_signatures':TunableList(description='\n            A list of autograph signature ResourceKeys.\n            ',
       tunable=TunableResourceKey(description='\n                The autograph signature image.\n                ',
       resource_types=[
      sims4.resources.Types.TGA],
       default=None),
       unique_entries=True), 
     'composite_params':OptionalTunable(description='\n            The base (portrait) and overlay (signature) image parameters.\n            ',
       tunable=TunableTuple(base_scale_x=Tunable(description='\n                    Scale x of the base image.\n                    ',
       tunable_type=float,
       default=1.0),
       base_scale_y=Tunable(description='\n                    Scale y of the base image.\n                    ',
       tunable_type=float,
       default=1.0),
       base_offset_x=Tunable(description='\n                    Offset the x of the base image.\n                    ',
       tunable_type=float,
       default=0),
       base_offset_y=Tunable(description='\n                    Offset the y of the base image.\n                    ',
       tunable_type=float,
       default=0),
       overlay_scale_x=Tunable(description='\n                    Scale x of the overlay image.\n                    ',
       tunable_type=float,
       default=1.0),
       overlay_scale_y=Tunable(description='\n                    Scale y of the overlay image.\n                    ',
       tunable_type=float,
       default=1.0),
       overlay_offset_x=Tunable(description='\n                    Offset the x of the overlay image.\n                    ',
       tunable_type=float,
       default=0),
       overlay_offset_y=Tunable(description='\n                    Offset the y of the overlay image.\n                    ',
       tunable_type=float,
       default=0),
       technique=Tunable(description='\n                    The compositing technique, where 0 is the alpha overlay. \n                    See Client for options.\n                    ',
       tunable_type=int,
       default=0),
       overlay_color=TunableColor(description='\n                    Color of the overlay image.\n                    '))), 
     'portrait_type':TunableEnumEntry(tunable_type=PortraitType,
       default=PortraitType.AUTOGRAPH,
       invalid_enums=(
      PortraitType.NONE,))}

    def __init__(self, owner, *args, **kwargs):
        (super().__init__)(owner, *args, **kwargs)
        self.outfit_category = OutfitCategory.EVERYDAY
        self.signature = None
        self.sim_id = 0
        self.no_op_version = 0

    def set_signature(self):
        sim_info_component = self.owner.get_component(STORED_SIM_INFO_COMPONENT)
        if sim_info_component is not None:
            sim_info = sim_info_component.get_stored_sim_info()
            if sim_info is not None:
                self.sim_id = sim_info.id
                r = random.Random()
                r.seed(self.sim_id)
                self.signature = r.choice(self.fame_autograph_signatures)

    def on_before_added_to_inventory(self):
        if self.painting_state is None:
            self.set_signature()
            self.update_composite_image()

    def set_composite_image(self, resource_key, resource_key_type, resource_key_group, no_op_version):
        super().set_composite_image(resource_key, resource_key_type, resource_key_group)
        inventory_owner = self.owner.inventoryitem_component.last_inventory_owner
        if inventory_owner is not None:
            self.owner.get_inventory().visible_storage.distribute_owned_inventory_update_message(self.owner, inventory_owner)
        else:
            logger.error('SimPortraitComponent image {} somehow has no inventory owner', self.owner)

    def update_composite_image(self, force_rebuild_thumb=False):
        if self.portrait_type == PortraitType.AUTOGRAPH:
            thumb_url = 'img://thumbs/sims/b_0x{:016x}_x_{:d}'.format(self.sim_id, int(self.outfit_category))
        else:
            if self.portrait_type == PortraitType.GRADUATION:
                robe_color = 'b'
                thumb_url = 'img://thumbs/sims/d_0x{:016x}_x_{:s}'.format(self.sim_id, robe_color)
            else:
                if self.portrait_type == PortraitType.HS_GRADUATION:
                    thumb_url = 'img://thumbs/sims/d_0x{:016x}_x_h'.format(self.sim_id)
        composite_operations = [self._create_composite_operation_msg()]
        op = CompositeThumbnail(thumb_url, (self.background_image.instance), (self.owner.id), (self.no_op_version), force_rebuild_thumb=force_rebuild_thumb, additional_composite_operations=composite_operations)
        Distributor.instance().add_op_with_no_owner(op)

    def _create_composite_operation_msg(self):
        msg = DistributorOps_pb2.CompositeParams()
        if self.signature is not None:
            msg.texture_hash = self.signature.instance
        if self.composite_params is not None:
            msg.base_scale_x = self.composite_params.base_scale_x
            msg.base_scale_y = self.composite_params.base_scale_y
            msg.base_offset_x = self.composite_params.base_offset_x
            msg.base_offset_y = self.composite_params.base_offset_y
            if self.portrait_type == PortraitType.GRADUATION or self.portrait_type == PortraitType.HS_GRADUATION:
                msg.overlay_scale_x = 0
                msg.overlay_scale_y = 0
            else:
                msg.overlay_scale_x = self.composite_params.overlay_scale_x
                msg.overlay_scale_y = self.composite_params.overlay_scale_y
            msg.overlay_offset_x = self.composite_params.overlay_offset_x
            msg.overlay_offset_y = self.composite_params.overlay_offset_y
            msg.technique = self.composite_params.technique
            msg.overlay_color.x, msg.overlay_color.y, msg.overlay_color.z, _ = sims4.color.to_rgba(self.composite_params.overlay_color)
        return msg


class PhotoboothPortraitComponent(CanvasComponent):
    FACTORY_TUNABLES = {'background_image': TunableResourceKey(description='\n            The background image for the portrait.\n            ',
                           resource_types=(sims4.resources.CompoundTypes.IMAGE),
                           default=None)}

    def __init__(self, owner, *args, **kwargs):
        (super().__init__)(owner, *args, **kwargs)
        self.no_op_version = 0

    def set_composite_image(self, resource_key, resource_key_type, resource_key_group, no_op_version):
        super().set_composite_image(resource_key, resource_key_type, resource_key_group)
        inventory_owner = self.owner.inventoryitem_component.last_inventory_owner
        if inventory_owner is not None:
            self.owner.get_inventory().visible_storage.distribute_owned_inventory_update_message(self.owner, inventory_owner)
        else:
            logger.error('PhotoboothPortraitComponent image {} somehow has no inventory owner', self.owner)

    def update_composite_image(self, sims, pose_index):
        if not sims:
            logger.error('Photobooth portrait object {} expects a non-zero number of sims.', (self.owner), owner='amwu')
            return
        num_sims = len(sims)
        thumb_url = f"img://thumbs/sims/multi/p_{num_sims}_"
        for sim in sims:
            thumb_url += f"0x{sim.id:016x}_"

        thumb_url += f"{pose_index}_l"
        op = CompositeThumbnail(thumb_url, (self.background_image.instance), (self.owner.id), (self.no_op_version), force_rebuild_thumb=True)
        Distributor.instance().add_op_with_no_owner(op)


class UpdateFamilyPortrait(XevtTriggeredElement):

    class SpecifyOutfitCategory(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'outfit_category': TunableEnumEntry(description='\n                Specifies a particular outfit category for the family portrait,\n                and randomizes the pose.\n                \n                If disabled, the portrait will just randomize the pose without\n                changing the outfit.\n                ',
                              tunable_type=OutfitCategory,
                              default=(OutfitCategory.EVERYDAY))}

        def do_action(self, canvas_component):
            canvas_component.outfit_category = self.outfit_category

    class LockPortrait(HasTunableSingletonFactory, AutoFactoryInit):

        def do_action(self, canvas_component):
            canvas_component.locked = True

    class UnlockPortrait(HasTunableSingletonFactory, AutoFactoryInit):

        def do_action(self, canvas_component):
            canvas_component.locked = False

    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            The participant object that is the family portrait.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantType.Object), 
     'update_action':TunableVariant(description='\n            Specify whether to lock or unlock the portrait, randomize the\n            pose, or specify the outfit category.\n            ',
       lock_portrait=LockPortrait.TunableFactory(),
       unlock_portrait=UnlockPortrait.TunableFactory(),
       specify_outfit_category=SpecifyOutfitCategory.TunableFactory(),
       locked_args={'randomize_pose': None},
       default='randomize_pose')}

    def _do_behavior(self):
        family_portrait_obj = self.interaction.get_participant(self.participant)
        if family_portrait_obj is None:
            logger.error('update_family_portrait basic extra tuned participant does not exist.', owner='jwilkinson')
            return False
        elif family_portrait_obj.canvas_component is None:
            logger.error('update_family_portrait basic extra tuned participant does not have a family portrait component.', owner='jwilkinson')
            return False
            force_rebuild_thumb = False
            if self.update_action is None:
                force_rebuild_thumb = True
        else:
            self.update_action.do_action(family_portrait_obj.canvas_component)
        family_portrait_obj.canvas_component.update_composite_image(force_rebuild_thumb)
        return True


class UpdateObjectValue(XevtTriggeredElement):
    FACTORY_TUNABLES = {'object_value_multipliers': TunableMultiplier.TunableFactory(description='\n            A list of test and multiplier pairs used for re-calculating (via\n            appraisal) the value of a portrait object.\n            ')}

    def _do_behavior(self):
        portrait_obj = self.interaction.target
        if portrait_obj is not None:
            if portrait_obj.canvas_component is not None:
                sim_info = portrait_obj.get_component(STORED_SIM_INFO_COMPONENT).get_stored_sim_info()
                if sim_info is not None:
                    portrait_obj.current_value = portrait_obj.catalog_value * self._get_total_multiplier(sim_info)
                    update_tooltip = portrait_obj.get_tooltip_field(TooltipFieldsComplete.simoleon_value) is not None
                    portrait_obj.update_current_value(update_tooltip)
                    return True
        return False

    def _get_total_multiplier(self, sim_info):
        sim_resolver = SingleSimResolver(sim_info)
        multiplier = self.object_value_multipliers.get_multiplier(sim_resolver)
        return multiplier


class PaintingStateTransfer(XevtTriggeredElement):
    FACTORY_TUNABLES = {'_source_participant':TunableEnumEntry(description='\n            The object to get the painting state from.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Object), 
     '_target_participant':TunableEnumEntry(description='\n            The object to set the painting state of.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Object)}

    def _do_behavior(self):
        source_participant = self.interaction.get_participant(self._source_participant)
        target_participant = self.interaction.get_participant(self._target_participant)
        if source_participant is not None:
            if target_participant is not None:
                source_canvas = source_participant.canvas_component
                if source_canvas is None:
                    logger.error('Painting State Transfer: Source object {} has no canvas_component', source_participant)
                    return
                target_canvas = target_participant.canvas_component
                if target_participant.canvas_component is None:
                    logger.error('Painting State Transfer: target object {} has no canvas_component', target_participant)
                    return
                if target_canvas.painting_state != source_canvas.painting_state:
                    target_canvas.painting_state = source_canvas.painting_state


class CreatePhotoboothPortrait(XevtTriggeredElement):
    MAX_PHOTO_SIMS = 3
    FACTORY_TUNABLES = {'object_definition':TunableReference(description='\n            Definition of the photobooth portrait that will be created.\n            ',
       manager=services.definition_manager()), 
     'inventory_sim':OptionalTunable(description='\n            Optional Sim in the interaction whose inventory to add the photo to.\n            If this is not tuned or fails we will attempt to give it to the photo Sim(s) in order.\n            ',
       tunable=TunableEnumEntry(tunable_type=ParticipantTypeSingleSim,
       default=(ParticipantTypeSingleSim.Actor))), 
     'participants':TunableList(description='\n            Sim(s) that will be in the photo. \n            No more than three total Sims are currently allowed.\n            ',
       tunable=TunableEnumEntry(tunable_type=ParticipantTypeSim,
       default=(ParticipantTypeSim.Actor)),
       minlength=1,
       maxlength=MAX_PHOTO_SIMS), 
     'expected_number_of_sims':TunableRange(description='\n            Expected number of sims in the photo. If the number of\n            participants ends up being different from this number,\n            we will cancel and log an error. \n            ',
       tunable_type=int,
       default=1,
       minimum=1,
       maximum=MAX_PHOTO_SIMS), 
     'pose_index':Tunable(description="\n            The reference pose index to use when generating the thumbnail for\n            this portrait on client. The relevant ASMs are currently hardcoded,\n            and holds states matching the following objects in tuning:\n            \n            * photoboothObject_Poses_Solo\n            * photoboothObject_Poses_Paired\n            * photoboothObject_Poses_ThreeSims\n            \n            Select the index of the desired pose state, which must be available \n            under the corresponding ASM for the expected number of Sims.\n            Make sure the ASM you're referencing matches the expected number\n            of sims tunable.\n            ",
       tunable_type=int,
       default=0)}

    def _do_behavior(self):
        sims = []
        for participant in self.participants:
            sims += list(self.interaction.get_participants(participant))

        sims_len = len(sims)
        if sims_len != self.expected_number_of_sims:
            logger.error('Unable to create photobooth portrait: expected {} sims, but got {}', (self.expected_number_of_sims),
              sims_len, owner='amwu')
            return
        photo = create_object(self.object_definition)
        if photo is None:
            logger.error('Unable to create a photobooth portrait with definition {}.', (self.object_definition), owner='amwu')
            return
        if photo.canvas_component is None:
            logger.error('Created photo {} does not have a Photobooth Portrait Component.', photo, owner='amwu')
        photo.canvas_component.update_composite_image(sims, self.pose_index)
        inventory_sim = self.interaction.get_participant(self.inventory_sim) if self.inventory_sim is not None else None
        result = False
        if inventory_sim is not None:
            result = inventory_sim.inventory_component.player_try_add_object(photo)
        attempts = 0
        while not result:
            if attempts < sims_len:
                result = sims[attempts].inventory_component.player_try_add_object(photo)
                attempts += 1

        if not result:
            photo.destroy(source=self, cause='Failed to add Photobooth Portrait to any Sim inventory.')
            logger.error('Failed to add a photobooth portrait to the desired Sim inventory.',
              owner='amwu')
            return
        owner = photo.inventoryitem_component.inventory_owner
        if owner is not None:
            photo.update_ownership(owner)