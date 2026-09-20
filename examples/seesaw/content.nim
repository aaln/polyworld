## Seesaw static game content: weather bands, inner lives, expressions,
## and the integer tuning table.
##
## Every value here is folded into `contentHash`, so a tuning change makes
## older replays fail at load with a named error instead of diverging
## silently at some later tick.

import
  polyworld/[cli, hashes]

const
  GridSide* = 128'i32
    ## Tiles along one edge of the map, matching `pathing.GridTiles`.
  GridCells* = GridSide * GridSide
  TickRate* = SharedTickRate
    ## Simulation ticks per second.
  DecisionTicks* = 8'i32
    ## Ticks between rider decisions.
  RiderCount* = 2
  DefaultSeed* = 2026'i32
  MatchMinutes* = 5'i32
    ## A live game is five real minutes on the board.
  MatchTicks* = MatchMinutes * 60 * TickRate
  MaxMatchTicks* = 20 * 60 * TickRate
  ExpressionCount* = 16
    ## 0 is a clear; 1 .. 15 are generated faces.
  ExpressionHoldTicks* = 48'i32
    ## Two seconds on the face before it is only history.
  MaxLean* = 2'i32
  MaxAngleMilli* = 500'i32
    ## About twenty-nine degrees from level. Positive is the west seat down.
  BounceMilli* = 350'i32
    ## How much angular velocity survives a wooden stop, in thousandths.
  Inertia* = 90'i32
    ## Larger is a heavier board.
  ArmScale* = 8'i32
  BottomBias* = 14'i32
    ## Geometry that wants the already-low side to stay low.
  SpringMilli* = 6'i32
    ## Weak centering from the fulcrum bushing.
  BaseWeight* = 100'i32
  LeanWeight* = 18'i32
  PumpPush* = 24'i32
  PumpLighten* = 16'i32
  IntensityScale* = 12'i32
    ## |omega| milliradians-per-tick times this is felt intensity, 0 .. 1000.
  ComfortWindow* = 90'i32
  TogetherBonusNum* = 14'i32
  TogetherBonusDen* = 10'i32
  MismatchNum* = 7'i32
  MismatchDen* = 10'i32
  NauseaGainDiv* = 40'i32
  NauseaRecover* = 10'i32
  SickLimit* = 1000'i32
  SickEventPenalty* = 12000'i32
  NauseaPenalty* = 2'i32
  FatiguePumpDiv* = 50'i32
  HeatFatigue* = 2'i32
  WetSlip* = 8'i32
  WetNauseaExtra* = 3'i32
  DampBase* = 20'i32
  WindForceScale* = 6'i32
  WindForceJitter* = 5'i32
  WalkStepTicks* = 5'i32
    ## Ticks to walk one tile toward a bench or back to the board.
  RestComfort* = 2'i32
    ## Fun per tick while recovering off the board.
  RestNauseaRecover* = 22'i32
  RestFatigueRecover* = 4'i32
  MountOffset* = 4'i32
    ## Tiles from the fulcrum to the hop-on pad, in the sand beside each seat.
  RestDeltaX*: array[RiderCount, int32] = [-11'i32, 13]
  RestDeltaY*: array[RiderCount, int32] = [-5'i32, 6]
    ## Bench tiles relative to the map centre. Lila west, Nico east.

type
  TempBand* = enum
    TempCold, TempCool, TempMild, TempWarm, TempHot
  WindBand* = enum
    WindStill, WindBreeze, WindWindy, WindGusty
  WetBand* = enum
    WetDry, WetDamp, WetWet
  EnergyKind* = enum
    EnergyExhausted, EnergyTired, EnergyFresh, EnergyEnergized, EnergyWired
  StomachKind* = enum
    StomachHungry, StomachFed, StomachOverfull
  VestibularKind* = enum
    VestSteady, VestQueasy, VestNauseous
  MoodKind* = enum
    MoodGrumpy, MoodCheerful
  ThirstKind* = enum
    ThirstThirsty, ThirstHydrated
  Expression* = enum
    FaceClear,
    FaceSmile,
    FaceFrown,
    FaceDelighted,
    FaceAnxious,
    FaceNauseous,
    FaceTired,
    FaceHot,
    FaceCold,
    FaceNervous,
    FaceStrain,
    FaceContent,
    FaceDizzy,
    FaceBliss,
    FaceGrimace,
    FaceCheer
  AnimationSlot* = enum
    SitAnimation, PumpAnimation, FunAnimation, DizzyAnimation,
    SickAnimation, WalkAnimation

const
  RiderNames*: array[RiderCount, string] = ["Lila", "Nico"]
  TempNames*: array[TempBand, string] = [
    "cold", "cool", "mild", "warm", "hot"]
  WindNames*: array[WindBand, string] = [
    "still", "breeze", "windy", "gusty"]
  WetNames*: array[WetBand, string] = ["dry", "damp", "wet"]
  ExpressionNames*: array[Expression, string] = [
    "clear", "smile", "frown", "delighted", "anxious", "nauseous",
    "tired", "hot", "cold", "nervous", "strain", "content", "dizzy",
    "bliss", "grimace", "cheer"
  ]
  EnergyPreferred*: array[EnergyKind, int32] = [
    120'i32, 220, 360, 540, 720]
  VestibularThreshold*: array[VestibularKind, int32] = [
    700'i32, 420, 250]
  RiderColors*: array[RiderCount, array[3, uint8]] = [
    [226'u8, 108, 92],
    [92'u8, 148, 214]
  ]

proc preferredIntensity*(
    energy: EnergyKind,
    stomach: StomachKind,
    vestibular: VestibularKind,
    mood: MoodKind,
    thirst: ThirstKind
): int32 =
  ## Hidden sweet-spot for one inner life, 0 .. 1000.
  result = EnergyPreferred[energy]
  case stomach
  of StomachHungry: result -= 40
  of StomachFed: discard
  of StomachOverfull: result -= 70
  case vestibular
  of VestSteady: discard
  of VestQueasy: result = result * 3 div 4
  of VestNauseous: result = result div 2
  if mood == MoodGrumpy:
    result -= 30
  if thirst == ThirstThirsty:
    result -= 25
  if result < 40:
    result = 40
  if result > 900:
    result = 900

proc comfortWindow*(mood: MoodKind): int32 =
  ## How wide a rider's "this is fun" band is.
  if mood == MoodCheerful: ComfortWindow + 40 else: ComfortWindow - 20

proc pairScore*(first, second: int32): int32 =
  ## Combined cooperative score. The less-happy rider is the binding term.
  let
    lo = min(first, second)
    total = first + second
  if lo < 0 or total < 0:
    return 0
  2'i32 * lo + total div 4

proc expressionKey*(face: int32): string =
  ## Atlas name for one generated face, including the clear glyph.
  "ssw_face_" & $face

proc gameLengthTicks*(maximumTicks: int32 = MatchTicks): int32 =
  ## Match length used by the tape and the clock.
  if maximumTicks <= 0:
    MatchTicks
  elif maximumTicks > MaxMatchTicks:
    MaxMatchTicks
  else:
    maximumTicks

proc contentHash*(): uint64 =
  ## Hashes every tuning value that can change how a game plays out.
  var hash = HashySeed
  for value in [
    GridSide, TickRate, DecisionTicks, int32(RiderCount), MatchMinutes,
    MatchTicks, ExpressionHoldTicks, MaxLean, MaxAngleMilli, BounceMilli,
    Inertia, ArmScale, BottomBias, SpringMilli, BaseWeight, LeanWeight,
    PumpPush, PumpLighten, IntensityScale, ComfortWindow, TogetherBonusNum,
    TogetherBonusDen, MismatchNum, MismatchDen, NauseaGainDiv, NauseaRecover,
    SickLimit, SickEventPenalty, NauseaPenalty, FatiguePumpDiv, HeatFatigue,
    WetSlip, WetNauseaExtra, DampBase, WindForceScale, WindForceJitter,
    WalkStepTicks, RestComfort, RestNauseaRecover, RestFatigueRecover,
    MountOffset
  ]:
    hash.addHashy(value)
  for value in RestDeltaX:
    hash.addHashy(value)
  for value in RestDeltaY:
    hash.addHashy(value)
  for value in EnergyPreferred:
    hash.addHashy(value)
  for value in VestibularThreshold:
    hash.addHashy(value)
  uint64(hash)
