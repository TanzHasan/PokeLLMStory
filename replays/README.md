# Pokemon Showdown Replay Saver

Simple Python script to download Pokemon Showdown replays for a specific [format](https://github.com/smogon/pokemon-showdown-client/blob/2e86d7e921a93875d83b21e726b3c8d62944d671/pokemonshowdown.com/users.php#L78).

## Usage

### Saving replays

Saves the 5 most recent replays from the Gen 1 OU format in the `replays/logs` directory.

```bash
python replays/get_replays.py --limit 5 --output_format log --output_dir replays/logs gen1ou
```

### Cleaning replays

Process the `gen9ou-2093373501.log` replay file and print only the relevant information to stdout.

```bash
python replays/clean_log.py replays/logs/gen9ou/gen9ou-2093373501.log
```
