---
added: 3.8.2
---
# State and Storage

How you store data in CoE5SE depends on whether it belongs to a single match or persists across games.

## Do not rely on Lua globals

Lua globals and file-level locals are never written to save files. In single player, globals can also carry stale values from an earlier game when you load another save. Globals are wiped whenever CoE5SE rebuilds a script's state, such as on LAN start, join, or leave, LAN error restarts, mod toggles, or Rehearse LAN games.

## Save-persisted state: `coe5.gameData` and `coe5.playerData`

Keep per-match state in two CoE5SE-managed tables saved inside save files and synced across LAN turns:

<!-- vale CoE5SE.Reports = NO -->
- **`coe5.gameData`:** Whole-match table for your mod. In LAN games, the host writes it and sends it to every client in each turn's save. Client edits to `coe5.gameData` are discarded next turn (`game_data_not_sent`).
- **`coe5.playerData[slot]`:** One table per player slot (`0` to `47`). In LAN games, each client's turn file sends its active player's table to the host so clients can pass requests back. Writes to another slot stay local to that client.

### Rules and limits

- **Plain values only:** Store booleans, numbers, strings, and nested tables with string, number, or boolean keys. Functions, userdata, metatables, cyclic tables, and values nested past 100 levels are skipped on save (`not_plain_value`, `bad_key`, `has_metatable`, `holds_itself`, `too_deep`).
- **Store limits:** Up to 4 MB per mod (`too_big`), 100 levels deep, and a 2,000 ms fill budget when loading tables back.
- **Do not cache sub-tables across loads:** Loading a save empties and refills `coe5.gameData` and `coe5.playerData` in place. Always read through `coe5.gameData` or `coe5.playerData[slot]` instead of keeping a local reference to an inner table.
- **Do not write at file top level:** Top-level writes to either table while a script loads are refused and undone (`during_load`). Set initial values in `GAME_START` or on first access.
- **Expect empty tables:** Both tables start empty in a New World and in older saves created before your script stored data. Always check for `nil`.
<!-- vale CoE5SE.Reports = YES -->

## Battle determinism

<!-- vale CoE5SE.Reports = NO -->
CoE5 fights a battle once (on the host or in single player) and re-runs it during every replay. Inside wraps and observers of sites that fire during battle rounds (not UI or drawing sites):

- `math.random` draws from a deterministic stream seeded by the battle and your mod name, and `math.randomseed` does nothing.
- `pairs` and `next` iterate keys in deterministic sorted order: numbers, then strings, then booleans. Table, function, and userdata keys come last in unordered sequence (logged once per fight as `lua_battle_pairs_unordered`).
- During a replay, `coe5.gameData` and `coe5.playerData` hold the snapshot from the start of the fight and restore afterward.

In LAN games, a content script's string-key iteration seed is shared across machines for the whole life of its state. `math.random` is also deterministically seeded during each load phase (script load and `.c5m` command passes).
<!-- vale CoE5SE.Reports = YES -->

## Per-mod INI data files

For data that lives outside a single match (such as campaign presets or user preferences), use CoE5SE's isolated INI storage:

- **`coe5.readIni(name)`:** Returns `t[section][key] = value`. Values are always strings (use `tonumber` for numbers), and keys before the first section live in `t[""]`.
- **`coe5.writeIni(name, t)`:** Writes sections and keys in sorted order, replacing the file.
- **`coe5.listIni()`:** Returns sorted file names without `.ini`.
- **`coe5.deleteIni(name)`:** Deletes `<name>.ini`.
- **`coe5.dataFolder(name)`:** Selects a subfolder inside your mod's data area.

### Storage location and limits

<!-- vale CoE5SE.Reports = NO -->
- **Location:** `<user folder>/coe5se_data/<ModName>/` (`%APPDATA%\coe5` on Windows, `~/.coe5` on Mac). Mods cannot read or write another mod's folder.
- **Size caps:** 1 MB per file and 10 MB total per mod by default. Raise the total cap up to 100 MB with [`maxdata`](../commands/other-commands.md#maxdata) in your `.c5se`.
- **Atomic writes:** Section names, keys, and values are capped at 1,024 bytes. Values cannot contain line breaks or NUL bytes; section names cannot contain `]`; keys cannot be empty, start with `[`, `;`, or `#`, or contain `]` or `=`; none may start or end with a space. One invalid entry fails the whole write and keeps the existing file intact.
- **LAN restriction:** In LAN games, `readIni` and `listIni` are refused for content mods (`lan_local_data`) so matches stay in sync. Personal mods can still read and write local INI files.
<!-- vale CoE5SE.Reports = YES -->
