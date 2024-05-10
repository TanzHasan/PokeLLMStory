import re
from data_model import Battle, Turn, Action, ActionResult, Pokemon
from collections import defaultdict

from copy import deepcopy

# Regular expressions to match different types of lines in the log
regex_turn = re.compile(r"^\|turn\|(\d+)$")
regex_move = re.compile(r"\|move\|(([^|]+): ([^|]+))\|([^|]+)\|(([^|]+): ([^|]+))?")
regex_switch = re.compile(r"^\|switch\|((.+): ([^|]+))\|([^,|]+).*\|(\d+)\/(\d+)")
regex_drag = re.compile(r"^\|drag\|((.+): ([^|]+))\|([^,|]+).*\|(\d+)\/(\d+)")
regex_faint = re.compile(r"^\|faint\|(([^|]+): ([^|]+))$")
regex_cant = re.compile(r"^\|cant\|(([^|]+): ([^|]+))\|([^|]+)")

regex_damage = re.compile(r"\|-damage\|((.+): (.+))\|((\d+)\/(\d+)|\d fnt)")
regex_heal = re.compile(r"\|-heal\|((.+): (.+))\|((\d+)\/(\d+)|\d fnt)")
regex_status = re.compile(r"\|-status\|(([^|]+): ([^|]+))\|([^|]+)")
regex_miss = re.compile(r"\|-miss\|((.+): (.+))")  # 1: target, 2: unit, 3: nickname
regex_immune = re.compile(r"\|-immune\|((.+): (.+))")  # 1: target, 2: unit, 3: nickname
regex_fail = re.compile(r"\|-fail\|((.+): (.+))")  # 1: target, 2: unit, 3: nickname
regex_supereffective = re.compile(r"\|-supereffective\|((.+): (.+))")
regex_crit = re.compile(r"\|-crit\|((.+): (.+))")  # 1: target, 2: unit, 3: nickname


def parse_log_file(file_path):
    # Maps [player][nickname] to Pokemon object
    known_pokemon = {
        "p1": {},
        "p2": {},
    }

    # Maps [unit] to Pokemon object
    active_pokemon = {}

    battle = Battle()
    turns = []

    with open(file_path, "r") as file:
        turn_num = 0
        file_contents = file.read().split("\n")

        index = 0
        current_turn = Turn(turn_num=turn_num)
        while index < len(file_contents):
            line = file_contents[index].strip()
            index += 1

            # Check if the line represents a turn
            match_turn = regex_turn.match(line)
            if match_turn:
                turn_num = int(match_turn.group(1))
                # print(f"Turn {turn_num}:")
                turns.append(current_turn)

                current_turn = Turn(turn_num=turn_num)
                current_turn.pokemon = deepcopy(active_pokemon)
                continue

            # Check if the line represents a move
            match_move = regex_move.match(line)
            if match_move:
                targets = []

                source_unit = match_move.group(2)
                source_player = source_unit[:-1]
                source_nickname = match_move.group(3)
                move = match_move.group(4)
                target = match_move.group(5) or ""
                target_unit = match_move.group(6) or ""
                targets.append(target_unit)
                target_player = target_unit[:-1] or ""
                target_nickname = match_move.group(7) or ""

                # Get results of the move
                results = defaultdict(ActionResult)
                line = file_contents[index].strip()
                while index < len(file_contents) and line.startswith("|-"):
                    # Damage
                    match_damage = regex_damage.match(line)
                    if match_damage:
                        target = match_damage.group(1)
                        target_unit = match_damage.group(2)
                        if target_unit != source_unit:
                            if target_unit not in targets:
                                targets.append(target_unit)
                            target_player = target_unit[:-1]
                            target_nickname = match_damage.group(3)
                            if match_damage.group(4) == "0 fnt":
                                # dead
                                health = 0
                            else:
                                health = int(match_damage.group(5))
                                max_hp = int(match_damage.group(6))

                            prev_health = known_pokemon[target_player][target_nickname].hp

                            # bug: pokemon can be healed/damaged within same "move" due to status effects like burn or poison
                            # need to modify data model to allow for multiple results per target
                            if results[target_unit].result != "heal":
                                results[target_unit].result = "hit"
                            results[target_unit].damage = prev_health - health
                            known_pokemon[target_player][target_nickname].hp = health

                    # Heal
                    match_heal = regex_heal.match(line)
                    if match_heal:
                        target = match_heal.group(1)
                        target_unit = match_heal.group(2)
                        if target_unit not in targets:
                            targets.append(target_unit)
                        target_player = target_unit[:-1]
                        target_nickname = match_heal.group(3)
                        if match_heal.group(4) == "0 fnt":
                            # dead
                            health = 0
                        else:
                            health = int(match_heal.group(5))
                            max_hp = int(match_heal.group(6))

                        prev_health = known_pokemon[target_player][target_nickname].hp

                        results[target_unit].result = "heal"
                        results[target_unit].damage = health - prev_health
                        known_pokemon[target_player][target_nickname].hp = health

                    # Status effect
                    match_status = regex_status.match(line)
                    if match_status:
                        target = match_status.group(1)
                        target_unit = match_status.group(2)
                        if target_unit not in targets:
                            targets.append(target_unit)
                        target_player = target_unit[:-1]
                        target_nickname = match_status.group(3)
                        status = match_status.group(4)

                        results[target_unit].result = "hit"
                        results[target_unit].status = status
                        known_pokemon[target_player][target_nickname].status = status

                    # Move missed
                    match_miss = regex_miss.match(line)
                    if match_miss:
                        # Should use target from parent move, not the line that says "miss"
                        # because this line doesn't have the target
                        # source = match_miss.group(1)
                        # source_unit = match_miss.group(2)
                        if target_unit not in targets:
                            targets.append(target_unit)
                        # source_player = source_unit[:-1]
                        # source_nickname = match_miss.group(3)

                        results[target_unit].result = "miss"

                    # Move failed
                    match_fail = regex_fail.match(line)
                    if match_fail:
                        target = match_fail.group(1)
                        target_unit = match_fail.group(2)
                        if target_unit not in targets:
                            targets.append(target_unit)
                        target_player = target_unit[:-1]
                        target_nickname = match_fail.group(3)

                        results[target_unit].result = "fail"

                    # Move supereffective
                    match_supereffective = regex_supereffective.match(line)
                    if match_supereffective:
                        target = match_supereffective.group(1)
                        target_unit = match_supereffective.group(2)
                        if target_unit not in targets:
                            targets.append(target_unit)
                        target_player = target_unit[:-1]
                        target_nickname = match_supereffective.group(3)

                        results[target_unit].effectiveness = "supereffective"

                    # Move crit
                    match_crit = regex_crit.match(line)
                    if match_crit:
                        target = match_crit.group(1)
                        target_unit = match_crit.group(2)
                        if target_unit not in targets:
                            targets.append(target_unit)
                        target_player = target_unit[:-1]
                        target_nickname = match_crit.group(3)

                        results[target_unit].crit = True

                    # Move immune
                    match_immune = regex_immune.match(line)
                    if match_immune:
                        target = match_immune.group(1)
                        target_unit = match_immune.group(2)
                        if target_unit not in targets:
                            targets.append(target_unit)
                        target_player = target_unit[:-1]
                        target_nickname = match_immune.group(3)

                        results[target_unit].result = "immune"

                    index += 1
                    line = file_contents[index].strip()

                # Update turn
                current_turn.actions.append(
                    Action(source_unit, "move", move, targets, results)
                )
                continue

            # Check if the line represents a switch or drag
            match_switch = regex_switch.match(line) or regex_drag.match(line)
            if match_switch:
                target = match_switch.group(1)
                unit = match_switch.group(2)
                player = unit[:-1]
                nickname = match_switch.group(3)
                pokemon_name = match_switch.group(4)
                current_hp = int(match_switch.group(5))
                max_hp = int(match_switch.group(6))

                # Use known pokemon info if available
                if nickname not in known_pokemon[player]:
                    # Possible bug if pokemon takes damage while not active? burning, etc
                    known_pokemon[player][nickname] = Pokemon(
                        nickname, pokemon_name, current_hp, max_hp, None, None
                    )

                # Update active pokemon
                active_pokemon[unit] = known_pokemon[player][nickname]

                # Update turn
                action = "switch" if regex_switch.match(line) else "drag"
                current_turn.actions.append(
                    Action(unit, action, pokemon_name, [unit], {})
                )
                continue

            # Check if the line represents a faint
            match_faint = regex_faint.match(line)
            if match_faint:
                target = match_faint.group(1)
                target_unit = match_faint.group(2)
                target_player = target_unit[:-1]
                target_nickname = match_faint.group(3)

                current_turn.actions.append(Action(target_unit, "faint", "", [], {}))
                continue

            # Check if line represents a Pokemon being unable to move
            match_cant = regex_cant.match(line)
            if match_cant:
                source = match_cant.group(1)
                source_unit = match_cant.group(2)
                source_player = source_unit[:-1]
                source_nickname = match_cant.group(3)
                reason = match_cant.group(4)

                # print(
                #     f"{source_player}: {source_nickname} can't move because {reason}"
                # )

                # update turn
                current_turn.actions.append(Action(source_unit, "cant", reason, [], {}))
                continue

        # Add last turn
        turns.append(current_turn)

    battle.turns = turns
    return battle

def action_to_string(turn: Turn, action: Action, translation: dict, active_pokemon: dict):
        status =   {
            "frz": "it is frozen",
            "slp": "it is asleep",
            "par": "it is paralyzed",
            "brn": "it is burned",
            "psn": "it is poisoned",
            "tox": "it is badly poisoned",
            "partiallytrapped": "it is partially trapped",
            "": "",
        }

        if turn.turn_num == 0:
            return f'{translation[action.source]} sent out {action.name}'

        source_player = translation[action.source]
        source_pokemon = turn.pokemon[action.source].pokemon_name
        # print(active_pokemon)

        match action.type:
            case "switch":

                active_pokemon[action.source] = action.name
                return f'{source_player}: {source_pokemon} switched out for {action.name}'
                
            case "move":
                line = f"{source_player}: {source_player}'s {source_pokemon} used {action.name}"
                for target, action_result in action.results.items():
                    result = action_result.result
                    damage = action_result.damage
                    crit = action_result.crit
                    target_status = action_result.status
                    effectiveness = action_result.effectiveness
                    target_player = translation[target]
                    target_pokemon = active_pokemon[target]

                    match result:
                        case "hit":
                            new_line = (
                                line
                                + f" on {target_player}'s {target_pokemon}{' and crit' if crit else ''} for {damage} damage"
                            )
                            if effectiveness:
                                new_line += f" ({effectiveness})"

                        case "miss":
                            new_line = line + f" on {target_pokemon} but it missed"

                        case "fail":
                            new_line = line + " but it failed"

                        case "heal":
                            new_line = line + f" and healed for {damage}"

                        case "immune":
                            new_line = (
                                line + f" but it had no effect on {target_pokemon}"
                            )

                        case _:
                            new_line = line
                            # print(f"Unknown result: {result}")

                    # ignore self hits for now
                    # need to look at item self damage, status effects from pokemon abilities
                    if action.source == target and result != "heal":
                        pass
                    else:
                        return new_line

                if not action.results:
                    return line + " on self"

            case "cant":
                return f"{source_player}: {source_pokemon} can't move because {status.get(action.name, action.name)}"

            case "faint":
                return f"{source_player}: {source_pokemon} fainted"

            case _:
                return f"  ERROR  {action.source} {action.type}"
