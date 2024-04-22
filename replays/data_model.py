from dataclasses import dataclass, field
from enum import Enum


class Unit(Enum):
    p1a = "p1a"
    p1b = "p1b"  # b used for double battles
    p2a = "p2a"
    p2b = "p2b"


@dataclass
class Pokemon:
    nickname: str
    pokemon_name: str
    hp: int
    max_hp: int
    status: str | None  # sleep, freeze, burn, poison, paralysis, bad poison, none
    held_item: str | None  # TODO: implement items
    effects: dict[str, int] = field(default_factory=dict)  # buffs, debuffs, etc
    boosts: list[str] = field(
        default_factory=list
    )  # TODO: stat boosts, stat drops, etc


@dataclass
class ActionResult:
    result: str = ""  # hit, miss, fail, immune, heal, etc
    damage: int = 0  # How much damage/heal did the move do
    crit: bool = False  # Did the move crit
    status: str = ""  # Did the cause any status effects
    effectiveness: str = ""  # Was the move super effective, not very effective, etc


@dataclass
class Action:
    source: Unit
    type: str  # switch, move, terastallize, singleturn, damage, supereffective, etc.
    name: str  # Name of the move or pokemon being switched to
    targets: list[Unit] = field(default_factory=list)
    results: dict[Unit, ActionResult] = field(default_factory=dict)


@dataclass
class Turn:
    turn_num: int = 0
    pokemon: dict[Unit, Pokemon] = field(default_factory=dict)
    actions: list[Action] = field(default_factory=list)
    weather: str = ""  # TODO: get weather
    item_effects: dict[str, str] = field(default_factory=dict)  # TODO: item effects


@dataclass
class Battle:
    turns: list[Turn] = field(default_factory=list)


# Parse log line into:
# @dataclass
# class LogInfo:
#     action: str  # switch, move, terastallize, singleturn, damage, supereffective, etc.
#     action_source_unit: Unit
#     action_source_player: str
#     action_source_nickname: str
#     action_target_unit: Unit
#     action_target_player: str
#     action_target_nickname: str

#     current_hp: int
#     max_hp: int
#     status_effect: str

#     item: str
#     item_effect: str

#     weather: str
#     hazard: str
