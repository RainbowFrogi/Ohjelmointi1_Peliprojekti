# [#](#tower-defense) TOWER DEFENSE

## [#](#COMMANDS) COMMANDS

### [#](#global-commands) GLOBAL COMMANDS

**Global commans** can be used at any time.

COMMANDS | DESCRIPTION | EXAMPLE
|-|-|-|
clear | Clear from the screen the commands previously used. | ``` clear ```
info | Shows you helpful information about the game. Like commands, tower names specifications and other information. | ``` info ```
<!-- help | Shows you helpful information about the game. Like commands, tower names specifications and other information. | ``` help ```
? | Shows you helpful information about the game. Like commands, tower names specifications and other information. | ``` ? ``` -->

### [#](#game-commands) GAME COMMANDS

**Global commans** can be used at any time.

COMMANDS | DESCRIPTION | EXAMPLE
|-|-|-|
create | Clear from the screen the commands previously used. | ``` create soldier ```
place | Clear from the screen the commands previously used. | ``` place mk5 5 5 ```
select | Clear from the screen the commands previously used. | ``` select 5 5```
grid | Clear from the screen the commands previously used. | ``` grid ```
beginwave | Clear from the screen the commands previously used. | ``` beginwave ```

game_commands = {
  "create": create_enemy_command,
  "place": place_turret_command,
  "select": select_turret_command,
  "grid": show_grid_command,
  "beginwave": begin_wave_command
}
### [#](#game-over-commands) GAME OVER COMMANDS

**Global commans** can be used at any time.

COMMANDS | DESCRIPTION | EXAMPLE
|-|-|-|
restart | Restart the game to the First Wave and the player to the default status. | ``` restart ```

## [#](#TURRET) TURRET

NICKNAME | NAME
|-|-|
mk5 | turret_1
mk10 | turret_2
mk15 | turret_3
mk20 | turret_4

## [#](#ENEMIES) EMEMIES

name | speed
|-|-|
rogue | fast
soldier | normal
heavy | slow
elite | slow
