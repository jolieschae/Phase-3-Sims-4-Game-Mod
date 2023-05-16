# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\__init__.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 36461 bytes
from sims4.log import Logger
from sims4.tuning.dynamic_enum import DynamicEnum
import enum
logger = Logger('Interactions')

class PipelineProgress(enum.Int, export=False):
    NONE = 0
    QUEUED = 1
    PRE_TRANSITIONING = 2
    PREPARED = 3
    RUNNING = 4
    STAGED = 5
    EXITED = 6


class TargetType(enum.IntFlags):
    ACTOR = 1
    TARGET = 2
    GROUP = 4
    OBJECT = 8
    FILTERED_TARGET = 16
    TARGET_AND_GROUP = TARGET | GROUP


def get_number_of_bit_shifts_by_participant_type(participant_type):
    if participant_type == ParticipantType.Invalid:
        return
    participant_type_value = int(participant_type)
    number_of_shifts = 0
    while participant_type_value != 1:
        participant_type_value = participant_type_value >> 1
        number_of_shifts += 1

    return number_of_shifts


class ParticipantType(enum.LongFlags):
    _enum_export_path = 'interactions.ParticipantType'
    Invalid = 0
    Actor = 1
    Object = 2
    TargetSim = 4
    Listeners = 8
    All = 16
    AllSims = 32
    Lot = 64
    CraftingProcess = 128
    JoinTarget = 256
    CarriedObject = 512
    Affordance = 1024
    InteractionContext = 2048
    CustomSim = 4096
    AllRelationships = 8192
    CraftingObject = 16384
    ActorSurface = 32768
    ObjectChildren = 65536
    LotOwners = 131072
    CreatedObject = 262144
    PickedItemId = 524288
    StoredSim = 1048576
    PickedObject = 2097152
    SocialGroup = 4194304
    OtherSimsInteractingWithTarget = 8388608
    PickedSim = 16777216
    ObjectParent = 33554432
    SignificantOtherActor = 67108864
    SignificantOtherTargetSim = 134217728
    OwnerSim = 268435456
    StoredSimOnActor = 536870912
    Unlockable = 1073741824
    LiveDragActor = 2147483648
    LiveDragTarget = 4294967296
    PickedZoneId = 8589934592
    SocialGroupSims = 17179869184
    PregnancyPartnerActor = 34359738368
    PregnancyPartnerTargetSim = 68719476736
    SocialGroupAnchor = 137438953472
    TargetSurface = 274877906944
    ActiveHousehold = 549755813888
    ActorPostureTarget = 1099511627776
    InventoryObjectStack = 2199023255552
    AllOtherInstancedSims = 4398046511104
    CareerEventSim = 8796093022208
    StoredSimOnPickedObject = 17592186044416
    SavedActor1 = 35184372088832
    SavedActor2 = 70368744177664
    SavedActor3 = 140737488355328
    SavedActor4 = 281474976710656
    LotOwnerSingleAndInstanced = 562949953421312
    LinkedPostureSim = 1125899906842624
    AssociatedClub = 2251799813685248
    AssociatedClubMembers = 4503599627370496
    AssociatedClubLeader = 9007199254740992
    AssociatedClubGatheringMembers = 18014398509481984
    ActorEnsemble = 36028797018963968
    TargetEnsemble = 72057594037927936
    TargetSimPostureTarget = 144115188075855872
    ActorEnsembleSansActor = 288230376151711744
    ActorDiningGroupMembers = 576460752303423488
    TableDiningGroupMembers = 1152921504606846976
    StoredSimOrNameData = 2305843009213693952
    TargetDiningGroupMembers = 4611686018427387904
    LinkedObjects = 9223372036854775808
    RoutingMaster = 18446744073709551616
    RoutingSlaves = 36893488147419103232
    SituationParticipants1 = 73786976294838206464
    SituationParticipants2 = 147573952589676412928
    ObjectCrafter = 295147905179352825856
    MissingPet = 590295810358705651712
    TargetTeleportPortalObjectDestinations = 1180591620717411303424
    ActorFeudTarget = 2361183241434822606848
    TargetFeudTarget = 4722366482869645213696
    ActorSquadMembers = 9444732965739290427392
    TargetSquadMembers = 18889465931478580854784
    AllInstancedSims = 37778931862957161709568
    StoredObjectsOnActor = 75557863725914323419136
    StoredObjectsOnTarget = 151115727451828646838272
    ObjectInventoryOwner = 302231454903657293676544
    LotOwnersOrRenters = 604462909807314587353088
    ActorFiance = 1208925819614629174706176
    TargetFiance = 2417851639229258349412352
    RandomInventoryObject = 4835703278458516698824704
    SituationParticipants3 = 9671406556917033397649408
    Familiar = 19342813113834066795298816
    ObjectProvidingTargetAffordance = 38685626227668133590597632
    StoredSimOnObjectProvidingTargetAffordance = 77371252455336267181195264
    PhotographyTargets = 154742504910672534362390528
    FamiliarOfTarget = 309485009821345068724781056
    PickedStatistic = 618970019642690137449562112
    ActorHousehold = 1237940039285380274899124224
    TargetHousehold = 2475880078570760549798248448
    AllInstancedActiveHouseholdSims = 4951760157141521099596496896
    Street = 9903520314283042199192993792
    VenuePolicyProvider = 19807040628566084398385987584
    ActorLot = 39614081257132168796771975168
    ObjectIngredients = 79228162514264337593543950336
    CreatedObjectIngredients = 158456325028528675187087900672
    StoredCASPartsOnObject = 316912650057057350374175801344
    RoutingOwner = 633825300114114700748351602688
    RoutingTarget = 1267650600228229401496703205376
    CurrentRegion = 2535301200456458802993406410752
    ActorLotLevel = 5070602400912917605986812821504
    ObjectLotLevel = 10141204801825835211973625643008
    TargetHouseholdMembers = 20282409603651670423947251286016
    ObjectAnimalHome = 40564819207303340847894502572032
    AnimalHomeAssignees = 81129638414606681695789005144064
    SituationCraftingItem = 162259276829213363391578010288128
    ObjectRelationshipsComponent = 324518553658426726783156020576256
    ActorHouseholdMembers = 649037107316853453566312041152512
    SavedStoryProgressionSim1 = 1298074214633706907132624082305024
    SavedStoryProgressionSim2 = 2596148429267413814265248164610048
    SavedStoryProgressionZone1 = 5192296858534827628530496329220096
    SavedStoryProgressionZone2 = 10384593717069655257060992658440192
    SavedStoryProgressionString1 = 20769187434139310514121985316880384
    SavedStoryProgressionString2 = 41538374868278621028243970633760768
    SavedStoryProgressionString3 = 83076749736557242056487941267521536
    SavedStoryProgressionString4 = 166153499473114484112975882535043072
    SavedStoryProgressionString5 = 332306998946228968225951765070086144
    ActorClanLeader = 664613997892457936451903530140172288
    TargetClanLeader = 1329227995784915872903807060280344576
    ObjectTrendiOutfitTrend = 2658455991569831745807614120560689152
    ObjectTrendiOutfitTrendTag = 5316911983139663491615228241121378304
    GraduatesCurrent = 10633823966279326983230456482242756608
    GraduatesWaiting = 21267647932558653966460912964485513216
    FashionTrends = 42535295865117307932921825928971026432
    CarryCancellationOriginatorTarget = 85070591730234615865843651857942052864
    TargetSimFrontCarriedSim = 170141183460469231731687303715884105728
    TargetSimBackCarriedSim = 1 << 128
    CarriedSim = 1 << 129
    PurchasedObject = 1 << 130
    StoredSimOrNameDataList = 1 << 131
    StoredSim2 = 1 << 132
    ActorBassinet = 1 << 133
    TargetBassinet = 1 << 134


class ParticipantTypeSavedActor(enum.LongFlags):
    SavedActor1 = ParticipantType.SavedActor1
    SavedActor2 = ParticipantType.SavedActor2
    SavedActor3 = ParticipantType.SavedActor3
    SavedActor4 = ParticipantType.SavedActor4


class ParticipantTypeSituationSims(enum.LongFlags):
    SituationParticipants1 = ParticipantType.SituationParticipants1
    SituationParticipants2 = ParticipantType.SituationParticipants2
    SituationParticipants3 = ParticipantType.SituationParticipants3


class ParticipantTypeAnimation(enum.LongFlags):
    Invalid = ParticipantType.Invalid
    Actor = ParticipantType.Actor
    TargetSim = ParticipantType.TargetSim
    Listeners = ParticipantType.Listeners
    AllSims = ParticipantType.AllSims


class ParticipantTypeSingle(enum.LongFlags):
    Actor = ParticipantType.Actor
    TargetSim = ParticipantType.TargetSim
    Lot = ParticipantType.Lot
    CarriedObject = ParticipantType.CarriedObject
    CraftingObject = ParticipantType.CraftingObject
    StoredSim = ParticipantType.StoredSim
    StoredSim2 = ParticipantType.StoredSim2
    StoredSimOnActor = ParticipantType.StoredSimOnActor
    StoredSimOnPickedObject = ParticipantType.StoredSimOnPickedObject
    SignificantOtherActor = ParticipantType.SignificantOtherActor
    SignificantOtherTargetSim = ParticipantType.SignificantOtherTargetSim
    PregnancyPartnerActor = ParticipantType.PregnancyPartnerActor
    PregnancyPartnerTargetSim = ParticipantType.PregnancyPartnerTargetSim
    Object = ParticipantType.Object
    SocialGroupAnchor = ParticipantType.SocialGroupAnchor
    ActiveHousehold = ParticipantType.ActiveHousehold
    ActorPostureTarget = ParticipantType.ActorPostureTarget
    PickedSim = ParticipantType.PickedSim
    PickedObject = ParticipantType.PickedObject
    SavedActor1 = ParticipantType.SavedActor1
    SavedActor2 = ParticipantType.SavedActor2
    SavedActor3 = ParticipantType.SavedActor3
    SavedActor4 = ParticipantType.SavedActor4
    LotOwnerSingleAndInstanced = ParticipantType.LotOwnerSingleAndInstanced
    ObjectCrafter = ParticipantType.ObjectCrafter
    MissingPet = ParticipantType.MissingPet
    OwnerSim = ParticipantType.OwnerSim
    ObjectInventoryOwner = ParticipantType.ObjectInventoryOwner
    ActorFiance = ParticipantType.ActorFiance
    TargetFiance = ParticipantType.TargetFiance
    CreatedObject = ParticipantType.CreatedObject
    RandomInventoryObject = ParticipantType.RandomInventoryObject
    Familiar = ParticipantType.Familiar
    FamiliarOfTarget = ParticipantType.FamiliarOfTarget
    ObjectProvidingTargetAffordance = ParticipantType.ObjectProvidingTargetAffordance
    StoredSimOnObjectProvidingTargetAffordance = ParticipantType.StoredSimOnObjectProvidingTargetAffordance
    PickedStatistic = ParticipantType.PickedStatistic
    ActorHousehold = ParticipantType.ActorHousehold
    TargetHousehold = ParticipantType.TargetHousehold
    Street = ParticipantType.Street
    VenuePolicyProvider = ParticipantType.VenuePolicyProvider
    ObjectAnimalHome = ParticipantType.ObjectAnimalHome
    ObjectParent = ParticipantType.ObjectParent
    ActorClanLeader = ParticipantType.ActorClanLeader
    TargetClanLeader = ParticipantType.TargetClanLeader
    CarryCancellationOriginatorTarget = ParticipantType.CarryCancellationOriginatorTarget


class ParticipantTypeReactionlet(enum.LongFlags):
    Invalid = ParticipantType.Invalid
    TargetSim = ParticipantType.TargetSim
    Listeners = ParticipantType.Listeners


class ParticipantTypeCASPart(enum.LongFlags):
    StoredCASPartsOnObject = ParticipantType.StoredCASPartsOnObject


class ParticipantTypeActorTargetSim(enum.LongFlags):
    Actor = ParticipantType.Actor
    TargetSim = ParticipantType.TargetSim


class ParticipantTypeResponse(enum.LongFlags):
    Invalid = ParticipantType.Invalid
    Actor = ParticipantType.Actor
    TargetSim = ParticipantType.TargetSim
    Listeners = ParticipantType.Listeners
    AllSims = ParticipantType.AllSims
    AllOtherInstancedSims = ParticipantType.AllOtherInstancedSims


class ParticipantTypeSingleSim(enum.LongFlags):
    Invalid = ParticipantType.Invalid
    Actor = ParticipantType.Actor
    TargetSim = ParticipantType.TargetSim
    PickedSim = ParticipantType.PickedSim
    StoredSim = ParticipantType.StoredSim
    StoredSim2 = ParticipantType.StoredSim2
    RoutingMaster = ParticipantType.RoutingMaster
    ObjectCrafter = ParticipantType.ObjectCrafter
    LotOwnerSingleAndInstanced = ParticipantType.LotOwnerSingleAndInstanced
    SavedActor1 = ParticipantType.SavedActor1
    SavedActor2 = ParticipantType.SavedActor2
    SavedActor3 = ParticipantType.SavedActor3
    SavedActor4 = ParticipantType.SavedActor4
    ActorFiance = ParticipantType.ActorFiance
    TargetFiance = ParticipantType.TargetFiance
    SignificantOtherTargetSim = ParticipantType.SignificantOtherTargetSim
    ActorClanLeader = ParticipantType.ActorClanLeader
    TargetClanLeader = ParticipantType.TargetClanLeader
    ActorHouseholdMembers = ParticipantType.ActorHouseholdMembers
    CarriedSim = ParticipantType.CarriedSim


class ParticipantTypeResponsePaired(enum.LongFlags):
    TargetSim = ParticipantType.TargetSim


class ParticipantTypeLot(enum.LongFlags):
    Lot = ParticipantType.Lot
    PickedZoneId = ParticipantType.PickedZoneId
    ActorLot = ParticipantType.ActorLot


class ParticipantTypeLotLevel(enum.LongFlags):
    ActorLotLevel = ParticipantType.ActorLotLevel
    ObjectLotLevel = ParticipantType.ObjectLotLevel


class ParticipantTypeObject(enum.LongFlags):
    Actor = ParticipantType.Actor
    ActorSurface = ParticipantType.ActorSurface
    CarriedObject = ParticipantType.CarriedObject
    CraftingObject = ParticipantType.CraftingObject
    CreatedObject = ParticipantType.CreatedObject
    CreatedObjectIngredients = ParticipantType.CreatedObjectIngredients
    Object = ParticipantType.Object
    ObjectIngredients = ParticipantType.ObjectIngredients
    PickedObject = ParticipantType.PickedObject
    SocialGroupAnchor = ParticipantType.SocialGroupAnchor
    ObjectInventoryOwner = ParticipantType.ObjectInventoryOwner
    RandomInventoryObject = ParticipantType.RandomInventoryObject
    ObjectAnimalHome = ParticipantType.ObjectAnimalHome
    AnimalHomeAssignees = ParticipantType.AnimalHomeAssignees
    SituationCraftingItem = ParticipantType.SituationCraftingItem
    ObjectTrendiOutfitTrend = ParticipantType.ObjectTrendiOutfitTrend
    ObjectTrendiOutfitTrendTag = ParticipantType.ObjectTrendiOutfitTrendTag


class ParticipantTypeSim(enum.LongFlags):
    Actor = ParticipantType.Actor
    TargetSim = ParticipantType.TargetSim
    Listeners = ParticipantType.Listeners
    AllSims = ParticipantType.AllSims
    JoinTarget = ParticipantType.JoinTarget
    CustomSim = ParticipantType.CustomSim
    AllRelationships = ParticipantType.AllRelationships
    LotOwners = ParticipantType.LotOwners
    StoredSim = ParticipantType.StoredSim
    StoredSim2 = ParticipantType.StoredSim2
    SocialGroup = ParticipantType.SocialGroup
    OtherSimsInteractingWithTarget = ParticipantType.OtherSimsInteractingWithTarget
    PickedSim = ParticipantType.PickedSim
    SignificantOtherActor = ParticipantType.SignificantOtherActor
    SignificantOtherTargetSim = ParticipantType.SignificantOtherTargetSim
    OwnerSim = ParticipantType.OwnerSim
    StoredSimOnActor = ParticipantType.StoredSimOnActor
    SocialGroupSims = ParticipantType.SocialGroupSims
    PregnancyPartnerActor = ParticipantType.PregnancyPartnerActor
    PregnancyPartnerTargetSim = ParticipantType.PregnancyPartnerTargetSim
    AllOtherInstancedSims = ParticipantType.AllOtherInstancedSims
    CareerEventSim = ParticipantType.CareerEventSim
    StoredSimOnPickedObject = ParticipantType.StoredSimOnPickedObject
    SavedActor1 = ParticipantType.SavedActor1
    SavedActor2 = ParticipantType.SavedActor2
    SavedActor3 = ParticipantType.SavedActor3
    SavedActor4 = ParticipantType.SavedActor4
    LotOwnerSingleAndInstanced = ParticipantType.LotOwnerSingleAndInstanced
    LinkedPostureSim = ParticipantType.LinkedPostureSim
    AssociatedClubMembers = ParticipantType.AssociatedClubMembers
    AssociatedClubLeader = ParticipantType.AssociatedClubLeader
    AssociatedClubGatheringMembers = ParticipantType.AssociatedClubGatheringMembers
    ActorEnsemble = ParticipantType.ActorEnsemble
    TargetEnsemble = ParticipantType.TargetEnsemble
    TargetSimPostureTarget = ParticipantType.TargetSimPostureTarget
    ActorEnsembleSansActor = ParticipantType.ActorEnsembleSansActor
    ActorDiningGroupMembers = ParticipantType.ActorDiningGroupMembers
    TableDiningGroupMembers = ParticipantType.TableDiningGroupMembers
    RoutingMaster = ParticipantType.RoutingMaster
    RoutingSlaves = ParticipantType.RoutingSlaves
    ObjectCrafter = ParticipantType.ObjectCrafter
    MissingPet = ParticipantType.MissingPet
    AllInstancedSims = ParticipantType.AllInstancedSims
    LotOwnersOrRenters = ParticipantType.LotOwnersOrRenters
    ActorFiance = ParticipantType.ActorFiance
    TargetFiance = ParticipantType.TargetFiance
    AllInstancedActiveHouseholdSims = ParticipantType.AllInstancedActiveHouseholdSims
    ActiveHousehold = ParticipantType.ActiveHousehold
    TargetHouseholdMembers = ParticipantType.TargetHouseholdMembers
    ActorHouseholdMembers = ParticipantType.ActorHouseholdMembers
    ActorClanLeader = ParticipantType.ActorClanLeader
    TargetClanLeader = ParticipantType.TargetClanLeader


class ParticipantTypeSavedStoryProgression(enum.LongFlags):
    SavedStoryProgressionSim1 = ParticipantType.SavedStoryProgressionSim1
    SavedStoryProgressionSim2 = ParticipantType.SavedStoryProgressionSim2
    SavedStoryProgressionZone1 = ParticipantType.SavedStoryProgressionZone1
    SavedStoryProgressionZone2 = ParticipantType.SavedStoryProgressionZone2
    SavedStoryProgressionString1 = ParticipantType.SavedStoryProgressionString1
    SavedStoryProgressionString2 = ParticipantType.SavedStoryProgressionString2
    SavedStoryProgressionString3 = ParticipantType.SavedStoryProgressionString3
    SavedStoryProgressionString4 = ParticipantType.SavedStoryProgressionString4
    SavedStoryProgressionString5 = ParticipantType.SavedStoryProgressionString5


class ParticipantTypeSavedStoryProgressionSim(enum.LongFlags):
    SavedStoryProgressionSim1 = ParticipantType.SavedStoryProgressionSim1
    SavedStoryProgressionSim2 = ParticipantType.SavedStoryProgressionSim2


STORY_PROGRESSION_SIM_PARTICIPANTS = ParticipantType.SavedStoryProgressionSim1 | ParticipantType.SavedStoryProgressionSim2

class ParticipantTypeSavedStoryProgressionZone(enum.LongFlags):
    SavedStoryProgressionZone1 = ParticipantType.SavedStoryProgressionZone1
    SavedStoryProgressionZone2 = ParticipantType.SavedStoryProgressionZone2


STORY_PROGRESSION_ZONE_PARTICIPANTS = ParticipantType.SavedStoryProgressionZone1 | ParticipantType.SavedStoryProgressionZone2

class ParticipantTypeSavedStoryProgressionString(enum.LongFlags):
    SavedStoryProgressionString1 = ParticipantType.SavedStoryProgressionString1
    SavedStoryProgressionString2 = ParticipantType.SavedStoryProgressionString2
    SavedStoryProgressionString3 = ParticipantType.SavedStoryProgressionString3
    SavedStoryProgressionString4 = ParticipantType.SavedStoryProgressionString4
    SavedStoryProgressionString5 = ParticipantType.SavedStoryProgressionString5


STORY_PROGRESSION_STRING_PARTICIPANTS = ParticipantType.SavedStoryProgressionString1 | ParticipantType.SavedStoryProgressionString2 | ParticipantType.SavedStoryProgressionString3 | ParticipantType.SavedStoryProgressionString4 | ParticipantType.SavedStoryProgressionString5

class MixerInteractionGroup(DynamicEnum):
    DEFAULT = 0


DEFAULT_MIXER_GROUP_SET = frozenset((MixerInteractionGroup.DEFAULT,))

class ParticipantTypeReaction(enum.LongFlags):
    Actor = ParticipantType.Actor
    Object = ParticipantType.Object
    TargetSim = ParticipantType.TargetSim
    Listeners = ParticipantType.Listeners
    AllSims = ParticipantType.AllSims
    OtherSimsInteractingWithTarget = ParticipantType.OtherSimsInteractingWithTarget
    SignificantOtherActor = ParticipantType.SignificantOtherActor
    SignificantOtherTargetSim = ParticipantType.SignificantOtherTargetSim
    OwnerSim = ParticipantType.OwnerSim
    SocialGroupSims = ParticipantType.SocialGroupSims
    LinkedPostureSim = ParticipantType.LinkedPostureSim


class ParticipantTypeRoutingBehavior(enum.LongFlags):
    Object = ParticipantType.Object
    Actor = ParticipantType.Actor
    ObjectParent = ParticipantType.ObjectParent
    ObjectChildren = ParticipantType.ObjectChildren
    AllInstancedActiveHouseholdSims = ParticipantType.AllInstancedActiveHouseholdSims
    AllInstancedSims = ParticipantType.AllInstancedSims
    RoutingOwner = ParticipantType.RoutingOwner
    RoutingTarget = ParticipantType.RoutingTarget
    ObjectAnimalHome = ParticipantType.ObjectAnimalHome