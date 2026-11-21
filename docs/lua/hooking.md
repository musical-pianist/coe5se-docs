---
added: 3.8.2
---
# Hooking the Game

CoE5SE scripts interact with the game through four core functions. `coe5.wrap` and `coe5.observe` hook into game calls, while `coe5.get` and `coe5.set` read and write game values and content records. Check [`coe5.lua`](https://github.com/musical-pianist/coe5se/blob/main/coe5.lua) for the complete `coe5.Site`, `coe5.ObservedSite`, and `coe5.Variable` lists.

## Wrapping calls with `coe5.wrap`

`coe5.wrap(site, fn, priority)` wraps a game call so your function runs before and after it. `fn` receives `next` as its first argument, followed by the site's arguments:

```lua
coe5.wrap("AI_CONQUER", function(next, commander, comstr)
  local score, x, y = next(commander, comstr)
  if score > -999 and avoidSquare(x, y) then
    return -999
  end
  return score, x, y
end, 10)
```

- **Chaining:** Call `next(...)` to pass control to inner wraps and the game. Modify arguments before calling `next`, alter return values afterward, or return without calling `next` to skip the game call.
- **Priority order:** Higher `priority` runs first (outermost), defaulting to `0`. Ties run last-registered first. Plugin DLL wraps always run outside Lua wraps.
- **Rules:** Call `next` only while `fn` is executing, and never from inside a coroutine.
- **Inspecting inner wraps:** Inside a wrap after calling `next()`, `coe5.changedBy()` lists the inner script wraps that changed their arguments or return values, innermost first. It returns an empty table outside a wrap or before `next()`.
- **Platform availability:** `coe5.wrap` returns `false` if a site is not mapped on the current platform. Mac lags behind Windows, so some sites are missing on Mac builds (always progressing).

## Watching calls with `coe5.observe`

`coe5.observe(site, before, after)` attaches read-only callbacks to a `coe5.ObservedSite` without changing its behavior:

```lua
coe5.observe("MONTH_START", nil, function(result)
  coe5.log("Turn " .. coe5.turn())
end)
```

- Pass `before(args...)`, `after(result, args...)`, or both (at least one must be non-`nil`). Return values are ignored.
- Observers run *inside* all wraps, so they see modified arguments and the game's actual result. If an outer wrap skips `next`, observers do not fire.
- `coe5.wrap` also accepts a `coe5.ObservedSite`. See each site's note in `coe5.lua` for what `next` can change there.

## Reading and writing state with `coe5.get` and `coe5.set`

<!-- vale CoE5SE.Reports = NO -->
`coe5.get(name, ...)` and `coe5.set(name, ...)` access game state and table entries by name:

- **Per-slot values:** Pass a player slot (`0` to `31`, or `32` to `47` for custom factions) or a faction's name string.
- **Strict types and bounds:** Boolean values require `true` or `false` (`0` or `nil` is refused with `needs_boolean`). Out-of-range integers fail with `out_of_range` without modifying state. Read-only variables raise an error on `coe5.set`.
- **World-generation-only fields:** Writing `squareTerrain`, `squarePortal`, `squareGround`, `squareTemperature`, or `squareName` only works during world building (inside a `PLAY_GAME_NEW_WORLD` wrap or a custom plane generator). Elsewhere it is refused with `not_world_building`, or `outside_plane` when writing outside the plane being built.
<!-- vale CoE5SE.Reports = YES -->

## Modifying content records

<!-- vale CoE5SE.Reports = NO -->
`coe5.set` can modify any vanilla or mod content record (`"monster"`, `"weapon"`, `"item"`, `"class"`, `"terrain"`, `"ritual"`) using the same field and flag names as `.c5m` files:

```lua
coe5.observe("MODS_READ", nil, function()
  local knight = coe5.findMonster("Knight")
  if knight then
    coe5.set("monster", knight, "hp", 30)
  end
end)
```

- **Baseline edits (`MODS_READ`):** Put deterministic load-time edits inside a `MODS_READ` observer. CoE5 resets content tables on level-2 mod passes (startup, leaving the **Mods** screen, or initial load) and then fires `MODS_READ`. Later LAN client turns and host restarts at Setup Server skip the mod pass. Content-record edits persist across those turns, while Lua tables built only inside `MODS_READ` are wiped on script restart.
- **Play-time edits:** Content writes made during gameplay are saved in the save file (`CWRT` chunk) and reapplied on load while the same content mods are loaded. In LAN games, the host's play-time content writes travel to clients in each turn's save; clients cannot make play-time content writes (`client_write_lost`).
<!-- vale CoE5SE.Reports = YES -->
