# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\ui\ui_dialog.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 46144 bytes
from protocolbuffers import Dialog_pb2, Consts_pb2
import sims
from audio.primitive import TunablePlayAudio, play_tunable_audio
from distributor.rollback import ProtocolBufferRollback
from distributor.shared_messages import build_icon_info_msg, IconInfoData
from distributor.system import Distributor
from interactions import ParticipantTypeSingleSim, ParticipantType
from interactions.utils.localization_tokens import LocalizationTokens
from interactions.utils.tunable_icon import TunableIcon, TunableIconVariant
from objects import ALL_HIDDEN_REASONS
from sims4.callback_utils import CallableList
from sims4.localization import TunableLocalizedStringFactory, TunableLocalizedStringFactoryVariant
from sims4.tuning.tunable import TunableEnumEntry, HasTunableFactory, AutoFactoryInit, OptionalTunable, HasTunableSingletonFactory, TunableList, Tunable, TunableEnumFlags, TunableFactory, TunableTuple, TunableVariant, TunableSimMinute, TunableResourceKey, TunableReference
from singletons import DEFAULT
from snippets import define_snippet
from uid import unique_id
import enum, pythonutils, services, sims4.log
logger = sims4.log.Logger('Dialog')

class ButtonType(enum.Int):
    DIALOG_RESPONSE_CLOSED = -1
    DIALOG_RESPONSE_NO_RESPONSE = 10000
    DIALOG_RESPONSE_OK = 10001
    DIALOG_RESPONSE_OK_ALT = 10003
    DIALOG_RESPONSE_CANCEL = 10002
    DIALOG_RESPONSE_CUSTOM_1 = 10004
    DIALOG_RESPONSE_CUSTOM_2 = 10005


class CustomButtonType(enum.Int):
    DIALOG_RESPONSE_CUSTOM_1 = ButtonType.DIALOG_RESPONSE_CUSTOM_1
    DIALOG_RESPONSE_CUSTOM_2 = ButtonType.DIALOG_RESPONSE_CUSTOM_2


class FooterType(enum.Int):
    AUTOMATIC = 0
    YES_BUTTONS_FOOTER = 1
    YES_NO_FOOTER = 2


class PhoneRingType(enum.Int):
    NO_RING = 0
    BUZZ = 1
    RING = 2
    ALARM = 3


def get_defualt_ui_dialog_response(**kwargs):
    return (UiDialogResponse.TunableFactory)(locked_args={'sort_order':0, 
                   'dialog_response_id':ButtonType.DIALOG_RESPONSE_NO_RESPONSE}, **kwargs)


class UiDialogOption(enum.IntFlags):
    DISABLE_CLOSE_BUTTON = 1
    SMALL_TITLE = 2
    DISABLE_PICKER_CLOSE_BUTTON = 8


class UiDialogStyle(enum.Int):
    DEFAULT = 0
    CHANCE_CARD = 1
    CELEBRATION = 2
    VET_CHECK_IN = 3
    LARGE_ICON = 4
    TRAIT_REASSIGNMENT = 5
    LIFESTYLE_BRAND = 6
    LARGE_ICON_TEXT_HORIZONTAL = 7
    LIFESTYLE_TRAITS = 8
    LARGE_ICON_WIDE = 9
    NPC_DISPLAY = 10
    GUIDANCE_WARNING = 11
    ICON_SWAP = 12


class UiDialogBGStyle(enum.Int):
    BG_DEFAULT = 0
    BG_CHANCE_CARD = 1
    BG_CELEBRATION = 2
    BG_LIFESTYLE_BRAND = 3
    BG_CELEBRATION_LARGE = 4
    BG_UNIVERSITY = 5
    BG_DROIDS = 6
    BG_VENDORS = 7
    BG_CHANCE_CARDS_HAUNTED = 8
    BG_MUSIC_FESTIVAL = 9
    BG_DYNAMIC_IMAGE = 10
    BG_MANI_PEDI = 11
    BG_CAKE_TOPPER = 12
    BG_TRENDI = 13
    BG_GUIDANCE = 14


class CommandArgType(enum.Int):
    ARG_TYPE_BOOL = 0
    ARG_TYPE_STRING = 1
    ARG_TYPE_FLOAT = 2
    ARG_TYPE_INT = 3
    ARG_TYPE_SPECIAL = 4
    ARG_TYPE_RESOLVED = 5


class UiResponseParticipant(enum.LongFlags):
    Actor = ParticipantType.Actor
    Object = ParticipantType.Object
    TargetSim = ParticipantType.TargetSim
    ObjectParent = ParticipantType.ObjectParent
    SavedActor1 = ParticipantType.SavedActor1


class UiResponseParticipantId(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'participant': TunableEnumEntry(description='\n            The participant to resolve for this response argument.\n            The value sent will be the id of the specified participant.\n            If more than one participant is found, it will only send the id of the first participant found.\n            ',
                      tunable_type=UiResponseParticipant,
                      default=(UiResponseParticipant.Actor))}

    @property
    def arg_type(self):
        return CommandArgType.ARG_TYPE_RESOLVED

    def resolve_response_arg(self, resolver=None):
        if resolver is None:
            return (None, None)
        participant = resolver.get_participant(self.participant)
        if participant is None:
            logger.error('Participant not {} found in resolver {}', (self.participant), resolver, owner='jdimailig')
            return (None, None)
        if participant.is_sim:
            return (
             CommandArgType.ARG_TYPE_INT, participant.sim_id)
        return (CommandArgType.ARG_TYPE_INT, participant.id)


class _UiResponseCommand(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'command':Tunable(description='The command.', tunable_type=str, default=''), 
     'arguments':TunableList(description='\n            The arguments for this command. Arguments will be added after the\n            command.\n            ',
       tunable=TunableVariant(description='\n                An argument being passed to the command.\n                ',
       boolean=TunableTuple(description='\n                    A boolean value.\n                    ',
       arg_value=Tunable(tunable_type=bool,
       default=False),
       locked_args={'arg_type': CommandArgType.ARG_TYPE_BOOL}),
       string=TunableTuple(description='\n                    A string.\n                    ',
       arg_value=Tunable(tunable_type=str,
       default=''),
       locked_args={'arg_type': CommandArgType.ARG_TYPE_STRING}),
       floating_point=TunableTuple(description='\n                    A floating point number.\n                    ',
       arg_value=Tunable(tunable_type=float,
       default=0.0),
       locked_args={'arg_type': CommandArgType.ARG_TYPE_FLOAT}),
       integer=TunableTuple(description='\n                    An integer number.\n                    ',
       arg_value=Tunable(tunable_type=int,
       default=0),
       locked_args={'arg_type': CommandArgType.ARG_TYPE_INT}),
       participant_id=(UiResponseParticipantId.TunableFactory()),
       special_command_data=TunableTuple(description='\n                    This will use the data passed into the show_dialog()\n                    function. This must be supported with GPE work, so\n                    only use this if you have talked to a GPE.\n                    ',
       locked_args={'arg_type': CommandArgType.ARG_TYPE_SPECIAL})))}


_, TunableUiResponseCommandSnippet = define_snippet('u_i_response_command', _UiResponseCommand.TunableFactory())

class UiDialogResponse(HasTunableSingletonFactory, AutoFactoryInit):

    class UiDialogUiRequest(enum.Int):
        NO_REQUEST = 0
        SHOW_LESSONS = 1
        SHOW_ACHIEVEMENTS = 2
        SHOW_GALLERY = 3
        SHOW_FAMILY_INVENTORY = 4
        SHOW_SKILL_PANEL = 5
        SHOW_SUMMARY_PANEL = 6
        SHOW_ASPIRATION_PANEL = 7
        SHOW_ASPIRATION_UI = 8
        SHOW_EVENT_UI = 9
        SHOW_CAREER_PANEL = 10
        SHOW_RELATIONSHIP_PANEL = 11
        SHOW_SIM_INVENTORY = 12
        SHOW_REWARD_STORE = 13
        SHOW_MOTIVE_PANEL = 14
        SHOW_STATS = 15
        SHOW_COLLECTIBLES = 16
        SHOW_CAREER_UI = 17
        TRANSITION_TO_NEIGHBORHOOD_SAVE = 18
        TRANSITION_TO_MAIN_MENU_NO_SAVE = 19
        SHOW_SHARE_PLAYER_PROFILE = 20
        SHOW_ASPIRATION_SELECTOR = 21
        SHOW_NOTEBOOK = 23
        SEND_COMMAND = 24
        CAREER_GO_TO_WORK = 25
        CAREER_WORK_FROM_HOME = 26
        CAREER_TAKE_PTO = 27
        CAREER_CALL_IN_SICK = 28
        SHOW_OCCULT_POWERS_PANEL = 29
        SHOW_FAME_PERKS_PANEL = 30
        SHOW_FACTION_REP_PANEL = 31

    @TunableFactory.factory_option
    def show_text(_):
        return {'text': TunableLocalizedStringFactory(description="\n                The prompt's text.\n                ")}

    FACTORY_TUNABLES = {'sort_order':Tunable(description='\n            The sorting order of the response button.  If the items of the\n            same order will be placed in the order that they are added.\n            ',
       tunable_type=int,
       default=0), 
     'dialog_response_id':TunableEnumEntry(description='\n            ',
       tunable_type=ButtonType,
       default=ButtonType.DIALOG_RESPONSE_NO_RESPONSE), 
     'ui_request':TunableEnumEntry(description="\n            This prompt's associated UI action.\n            ",
       tunable_type=UiDialogUiRequest,
       default=UiDialogUiRequest.NO_REQUEST), 
     'response_command':OptionalTunable(description='\n            If enabled, specifies a command to be called by the client.\n            ',
       tunable=TunableUiResponseCommandSnippet()), 
     'audio_event_name':OptionalTunable(description='\n            If enabled, this is the audio event sent by this button.\n            ',
       tunable=Tunable(description='\n                The button audio event name.\n                ',
       tunable_type=str,
       default='')), 
     'tutorial_id':OptionalTunable(description='\n            If set, this tutorial ID will be used for SHOW_LESSONS requests.\n            ',
       tunable=Tunable(description='\n                ID of a Tutorial, TutorialCategory, or TutorialSubcategory to be displayed.\n                ',
       tunable_type=int,
       default=0)), 
     'tooltip_text':OptionalTunable(description='\n            If enabled, this is the tooltip text to be shown on hover for this button.\n            ',
       tunable=TunableLocalizedStringFactory(description="\n                The tooltip's text.\n                ")), 
     'button_icon':OptionalTunable(description='\n            If enabled, this is the icon to be shown on this button.\n            ',
       tunable=TunableIcon()), 
     'loots_for_response':OptionalTunable(description='\n            If enabled, specify loots to apply and dialog response id for this response.\n            ',
       tunable=TunableTuple(description='\n                Loots to apply for the response and dialog response id that will override the original id.\n                ',
       loots=TunableList(description='\n                    A list of loots that will be applied when the player selects this response.\n                    ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True)),
       dialog_response_id_override=TunableEnumEntry(description='\n                    The dialog response id for this response that will override the default response\n                    id. Make sure this is unique for each response.\n                    ',
       tunable_type=CustomButtonType,
       default=(CustomButtonType.DIALOG_RESPONSE_CUSTOM_1))))}

    def __init__(self, sort_order=0, dialog_response_id=ButtonType.DIALOG_RESPONSE_NO_RESPONSE, text=None, subtext=None, ui_request=UiDialogUiRequest.NO_REQUEST, response_command=None, disabled_text=None, audio_event_name=None, tutorial_id=None, tooltip_text=None, button_icon=None, loots_for_response=None):
        self.text = text
        self.subtext = subtext
        self.disabled_text = disabled_text
        loot_list = None
        if loots_for_response:
            dialog_response_id = loots_for_response.dialog_response_id_override
            loot_list = loots_for_response.loots
        super().__init__(sort_order=sort_order, dialog_response_id=dialog_response_id,
          ui_request=ui_request,
          response_command=response_command,
          audio_event_name=audio_event_name,
          tutorial_id=tutorial_id,
          tooltip_text=tooltip_text,
          button_icon=button_icon,
          loots_for_response=loot_list)


@unique_id('dialog_id', 1)
class UiDialogBase:

    def __init__(self, resolver=None, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.response = None
        self._listeners = CallableList()
        self._resolver = resolver

    def add_listener(self, listener_callback):
        self._listeners.append(listener_callback)

    def distribute_dialog(self, dialog_type, dialog_msg, immediate=False):
        distributor = Distributor.instance()
        distributor.add_event(dialog_type, dialog_msg, immediate=immediate)

    def get_phone_ring_type(self):
        return PhoneRingType.NO_RING

    @property
    def responses(self):
        return tuple()

    def has_responses(self):
        if self.ui_responses:
            for ui_response in self.ui_responses:
                if ui_response.dialog_response_id != ButtonType.DIALOG_RESPONSE_NO_RESPONSE:
                    return True

        return self.responses or self._additional_responses

    def on_response_received(self):
        pass

    def respond(self, response: int) -> bool:
        try:
            self.response = response
            if self.ui_responses:
                for ui_response in self.ui_responses:
                    if ui_response.dialog_response_id == self.response:
                        for loot_action in ui_response.loots_for_response:
                            loot_action.apply_to_resolver(self._resolver)

            self._listeners(self)
            return True
        finally:
            self.on_response_received()

        return False

    def show_dialog(self, on_response=None, **kwargs):
        if on_response is not None:
            self.add_listener(on_response)
        pythonutils.try_highwater_gc()
        (services.ui_dialog_service().dialog_show)(self, (self.get_phone_ring_type()), **kwargs)

    def do_auto_respond(self, auto_response=DEFAULT):
        if auto_response is not DEFAULT:
            response = auto_response
        else:
            if ButtonType.DIALOG_RESPONSE_CANCEL in self.responses:
                response = ButtonType.DIALOG_RESPONSE_CANCEL
            else:
                if ButtonType.DIALOG_RESPONSE_OK in self.responses:
                    response = ButtonType.DIALOG_RESPONSE_OK
                else:
                    response = ButtonType.DIALOG_RESPONSE_CLOSED
        services.ui_dialog_service().dialog_respond(self.dialog_id, response)


class UiDialog(UiDialogBase, HasTunableFactory, AutoFactoryInit):
    DIALOG_MSG_TYPE = Consts_pb2.MSG_UI_DIALOG_SHOW

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, dialog_bg_style=None, background_image=None, ui_responses=None, **kwargs):
        if background_image is not None:
            if dialog_bg_style != UiDialogBGStyle.BG_DYNAMIC_IMAGE:
                logger.error("UiDialog {} has background_image set but the dialog bg style isn't BG_DYNAMIC_IMAGE.", instance_class,
                  owner='madang')
        if len(ui_responses) > 0:
            dialog_id_set = set()
            count = 0
            for response_item in ui_responses:
                if response_item.loots_for_response:
                    dialog_id_set.add(response_item.dialog_response_id)
                    count += 1
                    if len(dialog_id_set) != count:
                        logger.error('Duplicated dialog_response_id found in dialog tuning {}, tunable {}.', instance_class, tunable_name,
                          owner='yecao')
                        break

    FACTORY_TUNABLES = {'title':OptionalTunable(description='\n            If enabled, this dialog will include title text.\n            ',
       tunable=TunableLocalizedStringFactory(description="\n                The dialog's title.\n                ")), 
     'text':TunableLocalizedStringFactoryVariant(description="\n            The dialog's text.\n            "), 
     'text_tokens':OptionalTunable(description='\n            If enabled, define text tokens to be used to localized text.\n            ',
       tunable=LocalizationTokens.TunableFactory(description='\n                Define the text tokens that are available to all text fields in\n                the dialog, such as title, text, responses, default and initial\n                text values, tooltips, etc.\n                '),
       disabled_value=DEFAULT), 
     'icon':OptionalTunable(description='\n            If enabled, specify an icon to be displayed.\n            ',
       tunable=TunableIconVariant()), 
     'secondary_icon':OptionalTunable(description='\n            If enabled, specify a secondary icon to be displayed. Only certain\n            dialog types may support this field.\n            ',
       tunable=TunableIconVariant()), 
     'phone_ring_type':TunableEnumEntry(description='\n             The phone ring type of this dialog.  If tuned to anything other\n             than None this dialog will only appear after clicking on the phone.\n             ',
       tunable_type=PhoneRingType,
       default=PhoneRingType.NO_RING), 
     'anonymous_target_sim':Tunable(description='\n            If this dialog is using a target sim id to give a conversation type view and this is checked, then the\n            target sim icon will instead be replaced by an anonymous caller.\n            ',
       tunable_type=bool,
       default=False), 
     'audio_sting':OptionalTunable(description='\n            If enabled, play an audio sting when the dialog is shown.\n            ',
       tunable=TunablePlayAudio()), 
     'audio_sting_owner':OptionalTunable(description='\n            If enabled, this will set the owner of the audio sting when the\n            dialog is shown.\n            ',
       tunable=TunableEnumEntry(description='\n                The participant of the interaction who will play the audio_sting.\n                ',
       tunable_type=ParticipantType,
       default=(ParticipantType.Actor))), 
     'background_audio':OptionalTunable(description='\n            If enabled, play background audio while the dialog is open.\n            ',
       tunable=Tunable(description='\n                The background audio event string.\n                ',
       tunable_type=str,
       default='')), 
     'ui_responses':TunableList(description='\n            A list of buttons that are mapped to UI commands.\n            ',
       tunable=get_defualt_ui_dialog_response(show_text=True)), 
     'dialog_style':TunableEnumEntry(description='\n            The style layout to apply to this dialog.\n            ',
       tunable_type=UiDialogStyle,
       default=UiDialogStyle.DEFAULT), 
     'dialog_bg_style':TunableEnumEntry(description='\n            The style background to apply to this dialog.\n            ',
       tunable_type=UiDialogBGStyle,
       default=UiDialogBGStyle.BG_DEFAULT), 
     'dialog_options':TunableEnumFlags(description='\n            Options to apply to the dialog.\n            ',
       enum_type=UiDialogOption,
       allow_no_flags=True,
       default=UiDialogOption.DISABLE_CLOSE_BUTTON), 
     'dialog_footer_type':TunableEnumEntry(description='\n            An enumeration of the type for YES BUTTONS and DIALOG BUTTON footers.\n            AUTOMATIC lets the code decide which footer to use.\n            YES_BUTTONS_FOOTER is a footer with an OK BUTTON by default.\n            DIALOG_BUTTONS_FOOTER is a footer with only DIALOG BUTTONS.\n            ',
       tunable_type=FooterType,
       default=FooterType.AUTOMATIC), 
     'timeout_duration':OptionalTunable(description='\n            If enabled, override the timeout duration for this dialog in game\n            time.\n            ',
       tunable=TunableSimMinute(description='\n                The time, in sim minutes, that this dialog should time out.\n                ',
       default=5,
       minimum=5)), 
     'icon_override_participant':OptionalTunable(description='\n            If enabled, allows a different participant to be considered the\n            owner of this dialog. Typically, this will only affect the Sim\n            portrait used at the top of the dialog, but there could be other\n            adverse affects so be sure to talk to your UI partner before tuning\n            this.\n            ',
       tunable=TunableEnumEntry(description="\n                The participant to be used as the owner of this dialog. If this\n                participant doesn't exist, the default owner will be used\n                instead.\n                ",
       tunable_type=ParticipantTypeSingleSim,
       default=(ParticipantTypeSingleSim.Invalid),
       invalid_enums=(ParticipantTypeSingleSim.Invalid))), 
     'additional_texts':OptionalTunable(description='\n            If enabled, add additional text to the dialog\n            ',
       tunable=TunableList(tunable=(TunableLocalizedStringFactory()))), 
     'background_image':OptionalTunable(description='\n            If enabled, add a background image to the dialog.  This will only \n            be used in the case where dialog_bg_style is BG_DYNAMIC_IMAGE.\n            ',
       tunable=TunableResourceKey(description='\n                The background image for the family portrait.\n                ',
       resource_types=(sims4.resources.CompoundTypes.IMAGE),
       default=None)), 
     'verify_tunable_callback':_verify_tunable_callback}

    def __init__(self, owner, resolver=None, target_sim_id=None, *args, **kwargs):
        (super().__init__)(args, resolver=resolver, **kwargs)
        self._owner = owner.ref() if owner is not None else None
        self._additional_responses = {}
        self._timestamp = None
        self._target_sim_id = target_sim_id

    @property
    def accepted(self) -> bool:
        return self.response is not None and self.response != ButtonType.DIALOG_RESPONSE_CLOSED

    @property
    def closed(self) -> bool:
        return self.response == ButtonType.DIALOG_RESPONSE_CLOSED

    @property
    def owner(self):
        if self._owner is not None:
            return self._owner()

    @property
    def dialog_type(self):
        return self._dialog_type

    def set_responses(self, responses):
        self._additional_responses = tuple(responses)

    def _get_responses_gen(self):
        yield from self.responses
        yield from self._additional_responses
        yield from self.ui_responses
        if False:
            yield None

    def get_phone_ring_type(self):
        return self.phone_ring_type

    def update(self) -> bool:
        return True

    def show_dialog(self, **kwargs):
        if self.audio_sting is not None:
            sting_owner = None
            if self.audio_sting_owner is not None:
                sting_owner = self._resolver.get_participant(self.audio_sting_owner)
                if sting_owner is not None:
                    if isinstance(sting_owner, sims.sim_info.SimInfo):
                        sting_owner = sting_owner.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            play_tunable_audio((self.audio_sting), owner=sting_owner)
        if self.phone_ring_type == PhoneRingType.ALARM:
            return (super().show_dialog)(caller_id=self._owner().id, **kwargs)
        return (super().show_dialog)(caller_id=self._target_sim_id, **kwargs)

    def _build_localized_string_msg(self, string, *additional_tokens):
        if string is None:
            logger.callstack('_build_localized_string_msg received None for the string to build. This is probably not intended.', owner='tingyul')
            return
            tokens = ()
            if self._resolver is not None:
                if self.text_tokens is DEFAULT:
                    tokens = self._resolver.get_localization_tokens()
        elif self.text_tokens is not None:
            tokens = self.text_tokens.get_tokens(self._resolver)
        return string(*tokens + additional_tokens)

    def _build_response_arg(self, response, response_msg, tutorial_id=None, additional_tokens=(), response_command_tuple=None, **kwargs):
        response_msg.choice_id = response.dialog_response_id
        response_msg.ui_request = response.ui_request
        if response.text is not None:
            response_msg.text = (self._build_localized_string_msg)(response.text, *additional_tokens)
        else:
            if response.subtext is not None:
                response_msg.subtext = response.subtext
            if response.disabled_text is not None:
                response_msg.disabled_text = response.disabled_text
            if response.tooltip_text is not None:
                response_msg.tooltip_text = (self._build_localized_string_msg)(response.tooltip_text, *additional_tokens)
            if response.button_icon is not None:
                icon_info = IconInfoData(icon_resource=(response.button_icon))
                build_icon_info_msg(icon_info, None, response_msg.button_icon)
            if response.audio_event_name is not None:
                response_msg.audio_event_name = response.audio_event_name
            if response.tutorial_id is not None:
                response_msg.tutorial_args.tutorial_id = response.tutorial_id
            else:
                if tutorial_id is not None:
                    response_msg.tutorial_args.tutorial_id = tutorial_id
        if response.response_command:
            response_msg.command_with_args.command_name = response.response_command.command
            for argument in response.response_command.arguments:
                with ProtocolBufferRollback(response_msg.command_with_args.command_remote_args.args) as (entry):
                    if argument.arg_type == CommandArgType.ARG_TYPE_SPECIAL:
                        arg_type = response_command_tuple[0]
                        arg_value = response_command_tuple[1]
                    else:
                        if argument.arg_type == CommandArgType.ARG_TYPE_RESOLVED:
                            arg_type, arg_value = argument.resolve_response_arg(self._resolver)
                        else:
                            arg_type = argument.arg_type
                            arg_value = argument.arg_value
                    if arg_type == CommandArgType.ARG_TYPE_BOOL:
                        entry.bool = arg_value
                    else:
                        if arg_type == CommandArgType.ARG_TYPE_STRING:
                            entry.string = arg_value
                        else:
                            if arg_type == CommandArgType.ARG_TYPE_FLOAT:
                                entry.float = arg_value
                            else:
                                if arg_type == CommandArgType.ARG_TYPE_INT:
                                    entry.int64 = arg_value

    def build_msg(self, additional_tokens=(), icon_override=DEFAULT, secondary_icon_override=DEFAULT, text_override=DEFAULT, **kwargs):
        msg = Dialog_pb2.UiDialogMessage()
        msg.dialog_id = self.dialog_id
        msg.owner_id = self.owner.id if self.owner is not None else 0
        msg.dialog_type = Dialog_pb2.UiDialogMessage.DEFAULT
        msg.dialog_style = self.dialog_style
        msg.dialog_bg_style = self.dialog_bg_style
        if self._target_sim_id is not None:
            msg.target_id = self._target_sim_id
        elif self.title is not None:
            msg.title = (self._build_localized_string_msg)(self.title, *additional_tokens)
        else:
            if text_override is DEFAULT:
                msg.text = (self._build_localized_string_msg)(self.text, *additional_tokens)
            else:
                msg.text = (self._build_localized_string_msg)(text_override, *additional_tokens)
            if self.timeout_duration is not None:
                msg.timeout_duration = self.timeout_duration
            if icon_override is DEFAULT:
                if self.icon is not None:
                    icon_info = self.icon(self._resolver)
                    key = icon_info[0]
                    if key is not None:
                        msg.icon.type = key.type
                        msg.icon.group = key.group
                        msg.icon.instance = key.instance
                    build_icon_info_msg(icon_info, None, msg.icon_info)
            else:
                if icon_override is not None:
                    build_icon_info_msg(icon_override, None, msg.icon_info)
                if secondary_icon_override is DEFAULT:
                    if self.secondary_icon is not None:
                        icon_info = self.secondary_icon(self._resolver)
                        build_icon_info_msg(icon_info, icon_info.obj_name, msg.secondary_icon_info)
                elif secondary_icon_override is not None:
                    build_icon_info_msg(secondary_icon_override, secondary_icon_override.obj_name, msg.secondary_icon_info)
        if self.icon_override_participant is not None:
            msg.override_sim_icon_id = self._resolver.get_participants(self.icon_override_participant)[0].id
        msg.dialog_options = self.dialog_options
        msg.footer_type = self.dialog_footer_type
        msg.anonymous_target_sim = self.anonymous_target_sim
        responses = []
        responses.extend(self._get_responses_gen())
        responses.sort(key=(lambda response: response.sort_order))
        for response in responses:
            response_msg = msg.choices.add()
            (self._build_response_arg)(response,
 response_msg, additional_tokens=additional_tokens, **kwargs)

        if self.additional_texts:
            for additional_text in self.additional_texts:
                msg.additional_texts.append((self._build_localized_string_msg)(additional_text, *additional_tokens))

        if self.background_audio:
            msg.background_audio_event = self.background_audio
        if self.background_image:
            msg.background_image = sims4.resources.get_protobuff_for_key(self.background_image)
        return msg


class UiDialogOk(UiDialog):
    OK_BUTTON_ICON = TunableResourceKey(description='\n        The default icon for this OK Button.\n        ',
      default=None,
      resource_types=(sims4.resources.CompoundTypes.IMAGE))
    FACTORY_TUNABLES = {'text_ok':TunableLocalizedStringFactory(description='\n            The OK button text.\n            ',
       default=3648501874), 
     'icon_ok':OptionalTunable(tunable=TunableResourceKey(description='\n                The OK button icon. This does not need to be tuned unless the OK button is\n                supposed to have an icon instead of text.\n                ',
       default=None,
       resource_types=(sims4.resources.CompoundTypes.IMAGE))), 
     'is_special_dialog':Tunable(description='\n            If checked, UI will treat this as a special ok or ok/cancel dialog \n            and represent the ok or ok/cancel options in a special way. \n            They will use the text as a tooltip for ok or ok/cancel options \n            and use particular icons for the buttons.\n            ',
       tunable_type=bool,
       default=False), 
     'audio_ok':OptionalTunable(description='\n            If enabled, this is the audio event sent by the Ok button.\n            ',
       tunable=Tunable(description='\n                The Ok button audio event name.\n                ',
       tunable_type=str,
       default=''))}

    def build_msg(self, **kwargs):
        msg = (super().build_msg)(**kwargs)
        msg.is_special_dialog = self.is_special_dialog
        if self.is_special_dialog:
            msg.dialog_type = Dialog_pb2.UiDialogMessage.OK_CANCEL_ICONS
        return msg

    @property
    def accepted(self) -> bool:
        return self.response == ButtonType.DIALOG_RESPONSE_OK

    @property
    def responses(self):
        return (
         UiDialogResponse(dialog_response_id=(ButtonType.DIALOG_RESPONSE_OK), text=(self.text_ok),
           ui_request=(UiDialogResponse.UiDialogUiRequest.NO_REQUEST),
           audio_event_name=(self.audio_ok),
           button_icon=(self.icon_ok if self.icon_ok is not None else self.OK_BUTTON_ICON)),)


class UiDialogOkCancel(UiDialogOk):
    FACTORY_TUNABLES = {'text_cancel':TunableLocalizedStringFactory(description='\n            The Cancel button text.\n            ',
       default=3497542682), 
     'secondary_picker_icon_data':OptionalTunable(description='\n            If enabled, specify the texts to be displayed below the \n            secondary_icon image in the dialog panel.\n            ',
       tunable=TunableTuple(description='\n                Tuning for the title and description texts to accompany the\n                secondary_icon image.\n                ',
       title=TunableLocalizedStringFactory(description="\n                    The dialog's title.\n                    "),
       description_text=TunableLocalizedStringFactory(description="\n                    The dialog's title.\n                    "))), 
     'audio_cancel':OptionalTunable(description='\n            If enabled, this is the audio event sent by the Cancel button.\n            ',
       tunable=Tunable(description='\n                The Cancel button audio event name.\n                ',
       tunable_type=str,
       default=''))}

    def build_msg(self, **kwargs):
        msg = (super().build_msg)(**kwargs)
        if self.secondary_icon is not None:
            if self.secondary_picker_icon_data is not None:
                icon_info = self.secondary_icon(self._resolver)
                build_icon_info_msg(icon_info, (self.secondary_picker_icon_data.title()), (msg.secondary_icon_info), desc=(self.secondary_picker_icon_data.description_text()))
        return msg

    @property
    def responses(self):
        return (
         UiDialogResponse(dialog_response_id=(ButtonType.DIALOG_RESPONSE_OK), text=(self.text_ok),
           ui_request=(UiDialogResponse.UiDialogUiRequest.NO_REQUEST),
           audio_event_name=(self.audio_ok)),
         UiDialogResponse(dialog_response_id=(ButtonType.DIALOG_RESPONSE_CANCEL), text=(self.text_cancel),
           ui_request=(UiDialogResponse.UiDialogUiRequest.NO_REQUEST),
           audio_event_name=(self.audio_cancel)))


class UiEndSituationDialogOkCancel(UiDialogOkCancel):
    FACTORY_TUNABLES = {'text_alt_action': OptionalTunable(description='\n            If enabled, specify the text for the alternate action button\n            ',
                          tunable=TunableTuple(description='\n                Tuning for the alternate action texts\n                ',
                          text_alt=TunableLocalizedStringFactory(description='\n                    The alternate action button text\n                    NOTE: button or text not display if Is Special Dialog is set to True\n                    '),
                          disable=Tunable(description='\n                    Whether to disable the alternate action button and text at runtime\n                    ',
                          tunable_type=bool,
                          default=False)))}

    def __init__(self, owner, resolver=None, target_sim_id=None, disable_alt=False, *args, **kwargs):
        self._alt_disabled = disable_alt
        (super().__init__)(owner, resolver, target_sim_id, *args, **kwargs)

    @property
    def alt_disabled(self) -> bool:
        return self._alt_disabled and self.text_alt_action.disable

    @alt_disabled.setter
    def alt_disabled(self, disabled):
        self._alt_disabled = disabled

    @property
    def accepted_alt(self) -> bool:
        return self.response == ButtonType.DIALOG_RESPONSE_OK_ALT

    @property
    def canceled(self) -> bool:
        return self.response == ButtonType.DIALOG_RESPONSE_CANCEL

    def _get_responses_gen(self):
        for r in self.responses:
            if r.dialog_response_id == ButtonType.DIALOG_RESPONSE_OK_ALT:
                if self.text_alt_action and self.alt_disabled is False:
                    yield r
            else:
                yield r

        yield from self._additional_responses
        yield from self.ui_responses

    @property
    def responses(self):
        dialog_responses = [
         UiDialogResponse(dialog_response_id=(ButtonType.DIALOG_RESPONSE_OK), text=(self.text_ok),
           ui_request=(UiDialogResponse.UiDialogUiRequest.NO_REQUEST))]
        if self.text_alt_action:
            dialog_responses.append(UiDialogResponse(dialog_response_id=(ButtonType.DIALOG_RESPONSE_OK_ALT), text=(self.text_alt_action.text_alt),
              ui_request=(UiDialogResponse.UiDialogUiRequest.NO_REQUEST)))
        dialog_responses.append(UiDialogResponse(dialog_response_id=(ButtonType.DIALOG_RESPONSE_CANCEL), text=(self.text_cancel),
          ui_request=(UiDialogResponse.UiDialogUiRequest.NO_REQUEST)))
        return dialog_responses


TunableUiDialogOkCancelReference, TunableUiDialogOkCancelSnippet = define_snippet('dialog_ok_cancel', UiDialogOkCancel.TunableFactory())