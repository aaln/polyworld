## Hash canonical actions, excluding replay header/config/seed metadata.
import std/[os, sha1, json]
import ../replays
let tape = loadReplay(paramStr(1))
echo $(%*{"canonical_commands_sha1": $secureHash($tape.actions),
  "actions": tape.actions.len, "ticks": tape.hashes.len})
