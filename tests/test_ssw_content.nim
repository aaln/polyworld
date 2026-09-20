## Seesaw content: the fingerprint and the pair score.

import
  ../examples/seesaw/content

echo "Testing the content fingerprint"
block fingerprintIsStable:
  doAssert contentHash() != 0, "the content fingerprint is empty"
  doAssert contentHash() == contentHash(),
    "the content fingerprint is not deterministic"

echo "Testing pair score fairness"
block pairScoring:
  doAssert pairScore(100, 100) == 250
  doAssert pairScore(150, 50) == 150
  doAssert pairScore(200, 0) == 50
  doAssert pairScore(0, 0) == 0
  doAssert pairScore(120, 80) == 210
  doAssert pairScore(80, 80) > pairScore(150, 10)

echo "Testing preferred intensity"
block traits:
  let wired = preferredIntensity(
    EnergyWired, StomachFed, VestSteady, MoodCheerful, ThirstHydrated)
  let queasy = preferredIntensity(
    EnergyWired, StomachFed, VestNauseous, MoodCheerful, ThirstHydrated)
  doAssert wired > queasy
  doAssert queasy >= 40

echo "Testing name tables"
block names:
  doAssert RiderNames.len == RiderCount
  doAssert ExpressionNames.len == ExpressionCount
  doAssert expressionKey(1) == "ssw_face_1"

echo "Testing match length"
block duration:
  doAssert gameLengthTicks() == MatchTicks
  doAssert gameLengthTicks(0) == MatchTicks
  doAssert gameLengthTicks(MaxMatchTicks + 1) == MaxMatchTicks
  doAssert gameLengthTicks(240) == 240

echo "test_ssw_content: all checks passed"
