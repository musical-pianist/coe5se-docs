---
added: 3.8.2
---
# UI and Hotkeys

CoE5SE lets Lua scripts add menu entries, custom commander orders, full custom screens, message boxes, and hotkeys. In LAN games, UI belongs in a [`personalmod`](lan-games.md#personal-mods) because no player sits at the host.

## Entry points

Register UI hooks once when your script loads:

| Function | Where it appears |
| --- | --- |
| `coe5.addMainMenuButton(label, onClick, afterId)` | Main menu, above Quit or after a vanilla button like `coe5.mainMenu.mods`. Hide **Read Tip** (`coe5.mainMenu.readTip`) with `coe5.hideMainMenuButton`. |
| `coe5.addGameMenuLine{label, onClick, section, visible}` | In-game Game Menu: Saving & Exiting (default), `coe5.gameMenuSection.settings`, or a custom named section shared across mods. |
| `coe5.addCommanderLine{label, tooltip, visible, onClick}` | Selected commander's order column on the map. |
| `coe5.addMapEditorLine{...}` | Map editor toolbox, right under **Create Fancy Terrain**. |
| `coe5.addScreen(label, open, tooltip)` | Button inside your mod's page in **Mod Settings**. |

## Building custom screens (`coe5.ui`)

Custom screens run in a draw-and-wait loop: build the widgets, call `coe5.ui.wait()`, handle the returned button ID, and repeat until the player closes the screen.

```lua
local CLOSE = 99
local function openScreen()
  local enabled = true
  while true do
    coe5.ui.screenBegin("My Mod")
    coe5.ui.sectionBegin("Options")
    coe5.ui.checkbox(1, enabled, "Enable feature")
    coe5.ui.tooltip("Toggles the feature on or off.")
    coe5.ui.sectionEnd()
    coe5.ui.buttonRow()
    coe5.ui.text(CLOSE, "Close")
    coe5.ui.bindEscape(CLOSE)
    local id = coe5.ui.wait()
    if id == CLOSE then return end
    if id == 1 then enabled = not enabled end
  end
end
```

- **Widget IDs:** Pass `0` for non-clickable text. Any non-zero integer makes a widget clickable and returns that ID from `coe5.ui.wait()`.
- **Booleans:** Always pass `true` or `false` to `checkbox` and `choice` (in Lua, `0` is truthy).
- **Layouts:** `sectionBegin` and `sectionEnd` draw framed sections; `listBegin`, `listRow`, and `listEnd` match the Load Game list; `monsterRow` draws a Recruit-style row with a monster sprite; `buttonRow` starts the bottom button bar (always last).
- **Keyboard input:** Bind shortcuts with `coe5.ui.bindEscape(id)` and `coe5.ui.bindKey(id, key)`. For text fields, call `coe5.ui.setTextFocus(true)` each frame between `screenBegin` and `wait` and drain `coe5.ui.takeTextEvents()`, or call `coe5.ui.nameBox(...)` for a standalone text prompt.
- **Custom drawing:** `coe5.ui` also provides drawing primitives (`drawRect`, `drawLine`, `drawText`, `drawMonsterSprite`, `drawItemSprite`, `drawResourceIcon`, `textWidth`) documented in `coe5.lua`.

## Messages, settings, and translations

<!-- vale CoE5SE.Reports = NO -->
- **`coe5.showMessageBox(title, text)`:** Displays a modal Ok box immediately during a human turn and blocks until closed. Lines do not wrap automatically, so insert `\n` manually. Returns `false` when refused (LAN host, LAN client outside a turn, wait screens, AI turns, or route planning).
- **`coe5.sendMessage(player, title, text)`:** Adds a message to a human player's **Messages** window (or `coe5.message.everyHuman` for all humans). Refused on LAN clients.
- **`coe5.setting(name)`:** Reads a setting declared in `<ModName>.c5se` ([Mod Settings](../commands/mod-settings.md)), matching case-insensitively. Returns `true` or `false` for `onoff`, a `0`-based index for `choice`, or a key code for `key`. Read it live each time you need it; if cached at startup, add `restart` to the setting declaration.
- **`coe5.translate(text)`:** Returns the active translation from [language blocks](../commands/languages.md) (or `text` unchanged if none matches or `%` format codes differ). Store untranslated strings and translate where displayed. Translate format strings before calling `string.format`: `string.format(coe5.translate("Rolled %d of %d"), a, b)`.
<!-- vale CoE5SE.Reports = YES -->

## Hotkeys and key actions

Use `coe5.rebindKey(action, key)` to replace a vanilla key binding, `coe5.addActionKey(action, key)` to add an extra key for an action, and `coe5.actionKey(action)` to read the current binding (action constants live under `coe5.keyAction` in `coe5.lua`).

Bindings set from Lua are not saved to disk: they last until CoE5 closes, and across mods the last call wins. Combine them with `key` settings in [Mod Settings](../commands/mod-settings.md#key) so players can pick custom bindings. On LAN clients, only a `personalmod` can set or rebind keys (`rebindKey` returns `false` for other mods).
