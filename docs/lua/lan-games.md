---
added: 3.0
---
# LAN Games

!!! info "Work in progress"
    The Lua section is still being written. Expect more pages and changes.

[`coe5.lua`](https://github.com/musical-pianist/coe5se/blob/main/coe5.lua) documents every call. This page is how they tie together in a LAN game, and the gotchas.

| Your mod | Declare | Script runs on | Every player needs it |
| --- | --- | --- | --- |
| Content | Nothing | Every machine | Yes, the same files |
| Personal | [`personalmod`](../commands/mod-loading.md#personalmod) | Its player's client | No |
| No multiplayer | [`nomultiplayer`](../commands/mod-loading.md#nomultiplayer) | Nowhere | No |

Single player and hotseat are unchanged. Lua never runs in multiplayer on Illwinter servers. `coe5.netRole()` tells your script which machine it is on.

## Content mods

- The host runs your hooks for events, the AI, battles and months; a client runs them in its player's turn. Not in a client's battle replay (for now).
- Globals don't last: each machine builds your script a new state at every load, and a client at every turn. Keep state in `coe5.gameData`, which the host sends every client, and `coe5.playerData[slot]`, which a client writes for its own player and sends the host.
- Don't write either table at your file's top level. The file runs again at every load and turn, so the write is undone (`during_load`). Set first values in `GAME_START`.
- A client writes only what CoE5 carries in its turn file: its own player's resources, units and commanders. Ask the host for the rest through `coe5.playerData`:

```lua
-- Client: Gondor's player calls for aid as the turn ends
local function callForAid(_, player)
  coe5.playerData[player].lightBeacons = true
end
coe5.observe("CLIENT_TURN", nil, callForAid)
coe5.observe("HUMAN_TURN", nil, callForAid)   -- single player and hotseat

-- Host: answer at the month's start
coe5.observe("MONTH_START", nil, function()
  for slot = 0, 47 do
    if coe5.playerData[slot].lightBeacons then
      coe5.playerData[slot].lightBeacons = nil
      coe5.set("eventVar", 7900, 1)   -- +varequal 7900 1 in your .c5m sends the Rohirrim
    end
  end
end)
```

- No player sits at the host, so UI calls fail there. Put UI in a personal mod.
- Test with one machine: "Rehearse LAN games in single player" in CoE5SE's Mod Settings restarts content scripts each human turn and refuses what a client can't write.
- A script that errors restarts next turn, and every player is told.

## Personal mods

- For UI and hotkeys each player sets up. A personal mod does anything its player can by clicking, End Turn included. Calls a player can't make (gold, spawning units, `coe5.revealMap`) return `nil`.
- Reads are fogged to its player's sight: a fogged unit, army or square reads `nil`, and lists skip it. Game Over lifts the fog.
- `HUMAN_TURN` never fires in a LAN game. Use `CLIENT_TURN`.
- UI calls fail while its player waits for a turn. A script that errors stays off, and no one else is told.
- Players see each other's personal mods on Setup Participants.

??? info "Sites a personal mod can wrap"
    `ARMY_WAIT`, `BATTLE_DRAW`, `BATTLE_WAIT`, `FILE_BROWSER_HOVERED`, `FILE_BROWSER_ROW_DATE`, `FILE_BROWSER_WAIT`, `GAME_MENU_SAVING_SECTION_END`, `GAME_MENU_WAIT`, `GAME_OVER_WAIT`, `KEYBOARD_SHORTCUTS_WAIT`, `MAP_DRAW`, `MAP_MENU_BUTTON_TEXT`, `MAP_SCREEN_WAIT`, `MESSAGES_WAIT`, `MESSAGE_BOX_WAIT`, `MOD_BANNER_DRAW`, `RECRUIT_WAIT`, `RITUAL_SCREEN_ROW`, `SQUARE_INFO_BUTTON_ROW`, `SQUARE_INFO_SCREEN`, `SQUARE_INFO_WAIT`, `TOOLTIP_LINE_DRAW`, `TOP_BAR_INCOME`, `UNIT_LIST_WAIT`, `VIEW_ARMY_WAIT`, `WARN_WAIT`.

    Its observers run at every observe-only site that fires on its player's machine.

## No multiplayer mods

For single player tools, like a restart button or game presets. The whole mod is off in a LAN game, content included, and a single player save holding its content can't be hosted.

## Settings and keys

`coe5.setting` returns the host's pick in a content mod and its own player's pick in a personal mod. On a client only a personal mod can set keys.

## Mod files must match

A content mod's .c5m, .c5se or .lua differing between machines ends the game for everyone with "CoE5SE: Mod files differ". In the .c5m and .c5se, `description`, comments, spacing and settings blocks are ignored. Personal and `nomultiplayer` mods aren't compared.

!!! warning "Ship .lua changes to every player at once"
    Each .lua in your mod's folder is hashed whole, comments included, loaded or not. One player with an edited copy ends the game.
