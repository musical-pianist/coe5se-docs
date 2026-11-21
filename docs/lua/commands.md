---
added: 3.8.2
---
# Custom Commands

Normal `<ModName>.lua` scripts load on the first main menu frame, after CoE5 has finished its startup mod pass. To add new `.c5m` and `.c5se` commands or alter vanilla commands and events as mods load, place your registrations in **`<ModName>_commands.lua`** next to `<ModName>.c5m`.

## Load lifecycle and restrictions

<!-- vale CoE5SE.Reports = NO -->
- **Loads before mods parse:** `<ModName>_commands.lua` runs before the startup mod pass reads any mod's `.c5m` or `.c5se`, in load order (controlled by `requires` in the `.c5m`).
- **Shared state:** `<ModName>_commands.lua` and `<ModName>.lua` share one Lua state. Globals defined in the commands file stay visible to `<ModName>.lua`, and `require("<ModName>_commands")` returns whatever the commands file returned.
- **Error propagation:** If `<ModName>_commands.lua` stops with an error, `<ModName>.lua` does not load.
- **Allowed calls during load:** While `<ModName>_commands.lua` executes, CoE5SE allows only `coe5.addModCommand`, `coe5.alterCommand`, `coe5.alterCommandAfter`, `coe5.alterEventTrigger`, `coe5.alterEventAction`, `coe5.log`, `require`, `print`, `warn`, and Lua's standard libraries. Any other `coe5.*` call returns `nil` (`commands_file`).
- **Registration window:** All five functions below can only be called while `<ModName>_commands.lua` is loading (`not_in_commands_file` elsewhere).
<!-- vale CoE5SE.Reports = YES -->

## Pass levels

Handlers receive `level` (`t.level` on alter hooks) showing which mod pass is running:

| Level | What CoE5 is reading |
| --- | --- |
| `1` | Mod info (`icon`, `description`, `modprio`, `coeversion`, `modversion`) |
| `2` | Content definitions (monsters, weapons, items, classes, rituals, terrains) |
| `3` | Event execution during play (`t.event`, `t.player`, `t.squareEvent`, `t.x`, `t.y`) |
| `4` | Asset checks (`spr1`, `spr2`, `spr`, `sample`) |

## Hook summary

| Function | Targets | LAN scope |
| --- | --- | --- |
| `coe5.addModCommand(name, handler)` | New custom `.c5m` and `.c5se` command | Host for content mods; level 2 on clients for content and personal mods |
| `coe5.alterCommand(command, fn)` | Vanilla command line before parsing (content or events) | Content mods only |
| `coe5.alterCommandAfter(command, fn)` | Active record after a vanilla content command parses | Content mods only |
| `coe5.alterEventTrigger(trigger, fn)` | Vanilla `+` or `-` event trigger | Content mods only (host) |
| `coe5.alterEventAction(action, fn)` | Vanilla event action | Content mods only (host) |

## Adding a new command

```lua
coe5.addModCommand("mymod_bonus", function(args, mod, level)
  if level == 2 then
    coe5.log((mod or "map") .. ": " .. args)
  end
end)
```

- `name` must be under 48 characters, contain no spaces or tabs, and not collide with a vanilla command or another mod's command (case-insensitive). Use a mod prefix such as `mymod_` to avoid collisions.
- `handler(args, mod, level)` runs from the startup pass onward, before `<ModName>.lua` loads. Keep everything it needs during level-2 loading inside `<ModName>_commands.lua` or required helpers.

## Altering vanilla commands

- **`coe5.alterCommand(command, fn)`:** Runs before parsing on every line starting with `command` across all enabled `.c5m` and `.c5se` files and map events, in mod load order. Return `nil` to keep the line unchanged, a single-line replacement string under 50,000 bytes (fed to later hooks and the parser, CoE5SE commands included), or `false` or `""` to drop it.
- **`coe5.alterCommandAfter(command, fn)`:** Runs after a vanilla content command parses. Its table `t` carries the active record indices (`t.monster`, `t.weapon`, `t.item`, `t.class`, `t.terrain`, `t.ritual`, each `-1` if none) so you can adjust fields immediately with `coe5.set`.

## Altering vanilla events

- **`coe5.alterEventTrigger(trigger, fn)`:** Runs wherever CoE5 checks `trigger` (on the event's square in a `playerevent`, or per marked square in a `squareevent`). Return `true` or `false` (written for `+`, since CoE5SE flips the answer for `-`), a unit index for unit-finding triggers (`hascom`, `hascomhere`, `hasunit`, `hasunithere`, `hasaffunithere`), or `nil` to pass through to the next hook or vanilla.
- **`coe5.alterEventAction(action, fn)`:** Runs where CoE5 executes `action`. Return `true` if you handled the square (skipping vanilla), or `nil` or `false` to pass through to the next hook or vanilla.
