"""Initial attempt at cleaning the log. Might not work for every log file."""

import argparse
import re


def parse_log_file(file_path):
    # Regular expressions to match different types of lines in the log
    regex_turn = re.compile(r"^\|turn\|(\d+)$")
    regex_move = re.compile(r"^\|move\|([^|]+)\|([^|]+)\|([^|]*)")
    regex_switch = re.compile(r"^\|switch\|([^|]+)\|([^|]+)")
    regex_faint = re.compile(r"^\|faint\|([^|]+)$")
    regex_cant = re.compile(r"^\|cant\|([^|]+)\|([^|]+)")

    # Store nickname to Pokemon mapping
    nickname_to_pokemon = {}

    with open(file_path, "r") as file:
        current_turn = 0
        for line in file:
            line = line.strip()
            # Check if the line represents a turn
            match_turn = regex_turn.match(line)
            if match_turn:
                current_turn = int(match_turn.group(1))
                print(f"Turn {current_turn}:")
                continue

            # Check if the line represents a move
            match_move = regex_move.match(line)
            if match_move:
                source = match_move.group(1)
                source_player = source.split(":")[0][:-1]
                move = match_move.group(2)
                target = match_move.group(3)
                if target == "":
                    print(
                        f"{source_player}: {nickname_to_pokemon.get(source, source)} failed to use {move}"
                    )
                    continue
                print(
                    f"{source_player}: {nickname_to_pokemon.get(source, source)} used {move} on {nickname_to_pokemon.get(target, target)}"
                )
                continue

            # Check if the line represents a switch
            match_switch = regex_switch.match(line)
            if match_switch:
                nickname = match_switch.group(1)
                nickname_player = nickname.split(":")[0][:-1]
                pokemon = match_switch.group(2).split(",")[0]
                nickname_to_pokemon[nickname] = pokemon
                print(f"{nickname_player}: Switched to {pokemon}")
                continue

            # Check if the line represents a faint
            match_faint = regex_faint.match(line)
            if match_faint:
                pokemon = match_faint.group(1)
                pokemon_player = pokemon.split(":")[0][:-1]
                print(
                    f"{pokemon_player}: {nickname_to_pokemon.get(pokemon, pokemon)} fainted"
                )
                continue

            # Check if line represents a Pokemon being unable to move
            match_cant = regex_cant.match(line)
            if match_cant:
                pokemon = match_cant.group(1)
                pokemon_player = pokemon.split(":")[0][:-1]
                move = match_cant.group(2)
                print(
                    f"{pokemon_player}: {nickname_to_pokemon.get(pokemon, pokemon)} can't move"
                )
                continue


def main():
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
    args = parser.parse_args()

    # Save replays
    parse_log_file(args.path)


if __name__ == "__main__":
    main()
