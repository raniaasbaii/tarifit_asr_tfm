from pathlib import Path
import shutil

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PILOT_FILE = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "transcription_pilot.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "pilot_audio"
)


if not PILOT_FILE.exists():
    raise FileNotFoundError(
        f"Pilot file not found:\n{PILOT_FILE}"
    )

pilot_df = pd.read_csv(PILOT_FILE)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

copied = 0
missing = []

for _, row in pilot_df.iterrows():

    source_path = (
        PROJECT_ROOT
        / row["audio_path"]
    )

    destination_path = (
        OUTPUT_DIR
        / f"{row['segment_id']}.wav"
    )

    if not source_path.exists():
        missing.append(str(source_path))
        continue

    shutil.copy2(
        source_path,
        destination_path,
    )

    copied += 1


print(f"Copied files: {copied}")
print(f"Output folder: {OUTPUT_DIR}")
print(f"Missing files: {len(missing)}")

if missing:
    print("\nMissing paths:")
    for path in missing:
        print(path)