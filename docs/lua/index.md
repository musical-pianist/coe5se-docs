---
added: 3.0
---
# Lua

Script what a `.c5m` cannot. Custom screens, hotkeys, scripted campaigns, custom mod commands, and smarter AI are all possible with Lua in CoE5SE.

CoE5SE exposes over 500 functions, hook sites, game variables, and constants. The complete annotated API reference is two files: [`coe5.lua`](https://github.com/musical-pianist/coe5se/blob/main/coe5.lua) has the cheat sheet, the game's words, the hook sites, and the game variables, and [`coe5_calls.lua`](https://github.com/musical-pianist/coe5se/blob/main/coe5_calls.lua) has every function (copies also ship inside the `CoE5SE` mod folder). Place both in your workspace for autocomplete and hovers in VS Code or Cursor with the Lua language server (LuaLS). For the language itself, see the [Lua 5.5 manual](https://www.lua.org/manual/5.5/).

CoE5SE never ships Conquest of Elysium 5 or its executable, and every Lua function, hook site, and variable requires the player's installed game binary at launch. The API is built with the strict intention of extending the game for modders, not reverse-engineering or exposing Illwinter's code.

## Choose your mod type early

Every Lua mod falls into one of three classes in LAN games. Pick the right one up front, especially if you are building UI or hotkeys:

| Mod type | Declare in `.c5se` or `#!@` | Runs on | Every player needs it |
| --- | --- | --- | --- |
| **Content** | *(nothing)* | Host and every client | Yes (identical files) |
| **Personal** | [`personalmod`](../commands/mod-loading.md#personalmod) | Only players who enable it (and a host that has it) | No |
| **No multiplayer** | [`nomultiplayer`](../commands/mod-loading.md#nomultiplayer) | Single player and hotseat only | No |

!!! important "Personal mods only reach UI and client-safe sites"
    A `personalmod` can do anything its player can do in-game. In LAN games, it can only wrap 30 UI and screen sites, its observers are fog-filtered to player sight, and gameplay writes return `nil`. Adding gameplay content (monsters, spells, or events) turns a `personalmod` into a content mod. See [LAN Games](lan-games.md#personal-mods) for the full site list and rules before designing a client-side mod.

## Script files and load order

Place Lua files in your mod folder beside your `.c5m` using the exact same base filename:

- **`<ModName>.lua`:** Main script. Runs once on the first main menu frame after DLLs load, only while the mod is enabled.
- **`<ModName>_commands.lua`:** Optional script that loads before the startup mod pass reads `.c5m` and `.c5se` files. Use it to register custom commands or patch vanilla commands (see [Custom Commands](commands.md)).
- **Helper modules:** Split code across files inside your mod folder and load them with `require("subfolder.file")`. Dots map to subfolders, names are case-sensitive, and symlinks are blocked.

Enabling or disabling a mod on the **Mods** screen starts or retires its script without restarting CoE5. Editing an already-loaded `.lua` file requires restarting CoE5 (unlike `.c5m` and `.c5se` edits).

See [Getting Started](../getting-started.md#lua) for a working script (`Istari.lua`) inside a complete mod.

<!-- vale CoE5SE.Reports = NO -->
## Logging and debugging

`coe5.log`, `print`, and `warn` write lines to `coe5se_logs/coe5mod.log` in the CoE5 game folder:

- **`coe5.log` and `print`:** Written only while **Enable copious logs** (`script_log`) is on under CoE5SE in **Mod Settings** (off by default).
- **`warn`:** Always written, even when copious logs are off (unless turned off with `warn("@off")`).
<!-- vale CoE5SE.Reports = YES -->

## Sandbox and limits

CoE5SE runs **Lua 5.5** in an isolated sandbox per mod:

- **Available libraries:** `base` (without `load`, `dofile`, `loadfile`, or `collectgarbage`), `string`, `table`, `math`, `utf8`, `coroutine`, CoE5SE's folder-scoped `require`, and sandboxed `print` and `xpcall`. No `io`, `os`, `package`, or `debug`.
- **Step budget:** Each outermost call gets 20,000,000 Lua steps (counting coroutines, `__gc` finalizers, `table` and `string` library loops, and 10,000 steps per `coe5.route` call). Inside a long call, the count resets at `coe5.ui.wait` and `nameBox`, and at `next()` or a nested call when a game frame passed. Exceeding the budget stops the script permanently and cannot be caught by `pcall` or `xpcall`.
- **Memory cap:** 1.5 GB per script and 6 GB across all scripts combined. Exceeding 1.5 GB stops that script; exceeding 6 GB stops the script holding the most memory.
- **No raw pointers:** `tostring`, `print`, and `%p` mask real memory addresses while keeping stable per-object IDs.

## Pages

- [LAN Games](lan-games.md): mod classes, personal mod site lists, fog filtering, battle replays, host/client sync, and file hashing.
- [Hooking the Game](hooking.md): `coe5.wrap`, `coe5.observe`, priority order, and reading or modifying game and content values with `coe5.get` and `coe5.set`.
- [State and Storage](state.md): save-persisted `coe5.gameData` and `coe5.playerData`, battle determinism, and per-mod INI files.
- [UI and Hotkeys](ui.md): menu and commander entry points, `coe5.ui` screens, messages, settings, translations, and key rebinding.
- [Custom Commands](commands.md): registering new mod commands and intercepting vanilla commands in `<ModName>_commands.lua`.
