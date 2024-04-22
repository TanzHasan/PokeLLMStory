"""Recursively process all logs in replays/logs and save cleaned logs to replays/cleaned_logs/REVISION"""

from pathlib import Path
import subprocess

REVISION = 2
path = Path("replays/logs")
cleaned_logs_dir = Path("replays/cleaned_logs")

for format in path.iterdir():
    if format.is_dir():
        for log in format.glob("*.log"):
            # Process log file and capture output
            process = subprocess.run(
                ["python", "replays/clean_log.py", str(log)], capture_output=True
            )

            # Save output to cleaned_logs_dir/REVISION
            output_dir = f"{cleaned_logs_dir}/{REVISION}/{format.stem}"
            # Make parent directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            with open(f"{output_dir}/{log.stem}.txt", "w") as f:
                f.write(process.stdout.decode())
