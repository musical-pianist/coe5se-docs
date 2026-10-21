# CoE5SE: Small Modding Tidbits

## Overview

Random things about CoE5SE that don't have a home elsewhere, useful for specific modders to know.

## .c5se is just another .c5m

Simply put, the .c5se is an extended version of a .c5m. Everything can go in the .c5se except the lines in the tables below. And inversely, with CoE5SE running, the .c5m could just be your one mod-to-rule-them-all: it takes every CoE5SE command.

All examples in all guides are going to assume that CoE5SE is being tacked on as an extension to a mod you are already making, but this assumption can also be myopic. I did my best during this early build to allow YOUR creative preferences to happen, not constrain you.

As such, you SHOULD have 3 files in your mod:

| File | Desc. |
| --- | --- |
| The banner | The mod's icon |
| .c5m | All things that work with the base game modding tools |
| .c5se | All commands that add functionality |

Result: players without CoE5SE will have reduced spells, reduced rituals, reduced functionality, but the mod will work. The game never reads the .c5se without CoE5SE.

But you also COULD do it any number of ways:

| Layout | Result |
| --- | --- |
| Code entirely in the .c5m, with the line `needs_glu32.dll_and_CoE5SE_enabled_at_launch` | You work directly in the .c5m for the whole mod. If CoE5SE ever breaks, so does your mod. |
| Code entirely or mostly in the .c5se, with the same line in the .c5m | Same as coding entirely in the .c5m. This one is more per your preference and workflow. |

Mod Settings are the one exception, whatever you pick: `newsetting`, `newsettingheader`, and `newsettingpage` only go in the .c5se.

As a first example, here's a unit in the .c5m who gets a new spell from a CoE5SE sidecar, cut down from the Machine Cult (`ToolsAndExamples/MachineCult/` in [CoE5SE](https://www.nexusmods.com/mods/1?game_id=10486)'s folder). If CoE5SE ever gets disabled, the spell would fail, but the mod would still work.

``` c5m title="MyMod.c5m"
newmonster "Tech-Priest"
copystats "Captain"
copyspr "Illusionist"
```

``` c5se title="MyMod.c5se"
newspellpath "Machine Cult"

newspell "Blessing of the Omnissiah"
path "Machine Cult"
level 1
weapon 5 "Heal"
healhumanarmy

selectmonster "Tech-Priest"
spellweapon "Machine Cult" 1
```

As a second example, here is Elysium Remastered's .c5m, with everything else in its .c5se:

``` c5m title="ElysiumRemastered.c5m"
icon "Smallbanner.tga"
description "An overhaul mod. Flavor, balance and content."
needs_glu32.dll_and_CoE5SE_enabled_at_launch
modprio 1
```

Here is a table of items that should remain in .c5m

CoE5 mod commands:

| Line | Example |
| --- | --- |
| `icon` | `icon "Smallbanner.tga"` |
| `description` | `description "An overhaul mod. Flavor, balance and content."` |
| `modprio` | `modprio 1` |
| `coeversion` | `coeversion 5.40` |
| `modversion` | `modversion 1.0` |

CoE5SE mod commands:

| Line | Example |
| --- | --- |
| `Disallow loading the mod without CoE5SE`, right after `description`(optional) | `needs_glu32.dll_and_CoE5SE_enabled_at_launch` |
| `requires(optional)` | `requires CoE5SE 3.0` |

## Mod Settings in Network Games

Network games don't take Mod Settings:

- Every event with `+setting` or `-setting` fails.
- Lua scripts and DLL plugins don't run, so nothing reads a setting.

This stays for the foreseeable future unless requested. Other things take priority.
