## Quiet, opt-in personal combat cues. No assets or simulation state involved.
## Uses the same OpenAL one-shot approach as Pudge Wars.
import std/[math, times], openal

type CombatCue* = enum HitCue, HurtCue, HealCue, DeathCue, RespawnCue

var
  combatAudio* = false
  device: ALCdevice
  context: ALCcontext
  buffers: array[CombatCue, ALuint]
  sources: array[4, ALuint]
  nextSource: int
  lastCue: float64

proc closeCombatAudio*() =
  if context != nil:
    for source in sources: alSourceStop(source)
    alDeleteSources(sources.len.ALsizei, addr sources[0])
    alDeleteBuffers(buffers.len.ALsizei, addr buffers[HitCue])
    discard alcMakeContextCurrent(nil)
    alcDestroyContext(context)
    context = nil
  if device != nil:
    discard alcCloseDevice(device)
    device = nil
  combatAudio = false

proc toggleCombatAudio*(): bool =
  if combatAudio:
    combatAudio = false
    for source in sources: alSourceStop(source)
    return true
  if context == nil:
    device = alcOpenDevice(nil)
    if device == nil: return false
    context = alcCreateContext(device, nil)
    if context == nil or not alcMakeContextCurrent(context):
      closeCombatAudio()
      return false
    discard alGetError()
    alGenSources(sources.len.ALsizei, addr sources[0])
    alGenBuffers(buffers.len.ALsizei, addr buffers[HitCue])
    for cue in CombatCue:
      let duration = if cue in {DeathCue, RespawnCue}: 0.34 else: 0.10
      var pcm = newSeq[int16](int(duration * 22050))
      let frequency = [660.0, 150.0, 880.0, 190.0, 520.0][cue.ord]
      for i in 0 ..< pcm.len:
        let t = i.float / 22050
        let bend = if cue == RespawnCue: 380.0 elif cue == DeathCue: -130.0 else: 0.0
        let envelope = min(1.0, t / 0.005) * (1.0 - t / duration)
        pcm[i] = int16(sin(2 * PI * (frequency * t + bend * t * t / (2 * duration))) * envelope * 6000)
      alBufferData(buffers[cue], AL_FORMAT_MONO16, addr pcm[0], (pcm.len * 2).ALsizei, 22050)
    if alGetError() != AL_NO_ERROR:
      closeCombatAudio()
      return false
  combatAudio = true
  true

proc playCombatCue*(cue: CombatCue) =
  if not combatAudio: return
  let now = epochTime()
  if cue notin {DeathCue, RespawnCue} and now - lastCue < 0.14: return
  lastCue = now
  let source = sources[nextSource]
  nextSource = (nextSource + 1) mod sources.len
  alSourceStop(source)
  alSourcei(source, AL_BUFFER, buffers[cue].ALint)
  alSourcef(source, AL_GAIN, 0.45)
  alSourcePlay(source)
