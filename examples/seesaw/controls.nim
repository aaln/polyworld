## Human rider commands for Seesaw.
##
## Graphics queues intents. The decide tick applies them through the Game
## `apply*` wrappers that also record the tape.

import
  sim

type
  PlayerCommandKind = enum
    CommandLean
    CommandPump
    CommandExpress
    CommandRest

  PlayerCommand = object
    kind: PlayerCommandKind
    player: int32
    first: int32

var pending: seq[PlayerCommand]

proc queueLean*(player, dir: int32) =
  pending.add PlayerCommand(kind: CommandLean, player: player, first: dir)

proc queuePump*(player, on: int32) =
  pending.add PlayerCommand(kind: CommandPump, player: player, first: on)

proc queueExpress*(player, face: int32) =
  pending.add PlayerCommand(
    kind: CommandExpress, player: player, first: face)

proc queueRest*(player: int32) =
  pending.add PlayerCommand(kind: CommandRest, player: player)

proc applyCommand(game: Game, command: PlayerCommand): bool =
  case command.kind
  of CommandLean:
    game.applyLean(command.player, command.first)
  of CommandPump:
    game.applyPump(command.player, command.first)
  of CommandExpress:
    game.applyExpress(command.player, command.first)
  of CommandRest:
    game.applyRest(command.player)

proc flushPlayerCommands*(game: Game) =
  if pending.len == 0:
    return
  let commands = pending
  pending.setLen(0)
  for command in commands:
    discard game.applyCommand(command)
