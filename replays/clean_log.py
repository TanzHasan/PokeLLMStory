from pprint import pprint
import argparse
from parse_log import parse_log_file
from data_model import Battle


def process_output(battle: Battle):
    translation = {
        "p1a": "Player A",
        "p2a": "Player B",
    }

    status = {
        "frz": "frozen",
        "slp": "asleep",
        "par": "paralyzed",
        "brn": "burned",
        "psn": "poisoned",
        "tox": "badly poisoned",
        "partiallytrapped": "partially trapped",
        "": "",
    }

    output = []

    for turn in battle.turns:
        if turn.turn_num == 0:
            output.append("Battle start:")
            for action in turn.actions:
                output.append(f"{translation[action.source]} sent out {action.name}")
            continue

        output.append(f"Turn {turn.turn_num}:")

        active_pokemon = {
            "p1a": turn.pokemon["p1a"].pokemon_name,
            "p2a": turn.pokemon["p2a"].pokemon_name,
        }

        for action in turn.actions:
            source_player = translation[action.source]
            source_pokemon = turn.pokemon[action.source].pokemon_name

            match action.type:
                case "switch":
                    output.append(
                        f"{source_player}: Switched out {source_pokemon} for {action.name}"
                    )
                    active_pokemon[action.source] = action.name
                
                case "drag":
                    output.append(
                        f"{source_player}: {source_pokemon} got dragged out for {action.name} by opponent's move"
                    )
                    active_pokemon[action.source] = action.name

                case "move":
                    line = f"{source_player}: {source_pokemon} used {action.name}"
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
                                new_line = f"{line} on {target_pokemon}"
                                if damage:
                                    new_line += f"{' and crit' if crit else ''} for {damage} damage"
                                if target_status:
                                    new_line += f" and they are now {status[target_status]}"
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
                            output.append(new_line)

                    if not action.results:
                        if action.targets:
                            output.append(line + " on " + ", ".join(active_pokemon[target] for target in action.targets))
                        else:
                            output.append(line + " on self")

                case "cant":
                    output.append(
                        f"{source_player}: {source_pokemon} can't move because it is {status.get(action.name, action.name)}"
                    )

                case "faint":
                    output.append(f"{source_player}: {source_pokemon} fainted")

                case _:
                    output.append(f"  ERROR  {action.source} {action.type}")

    return "\n".join(output)


def parse_args() -> Battle:
    # Set up arguments
    parser = argparse.ArgumentParser(
        description="Parse replay logs from Pokemon Showdown"
    )
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(
        prog, max_help_position=32
    )
    parser.add_argument(
        "path",
        help="Path to replay .log file",
    )
    parser.add_argument(
        "-o",
        help="Should output be saved to a file (debug_clean_log.txt) for debugging",
        action="store_true",
    )
    args = parser.parse_args()

    # Save replays
    return parse_log_file(args.path), args.o


def main():
    battle, write_debug_file = parse_args()
    if write_debug_file:
        with open("output.txt", "w") as f:
            pprint(battle, f)
    output = process_output(battle)
    print(output)



if __name__ == "__main__":
    main()
