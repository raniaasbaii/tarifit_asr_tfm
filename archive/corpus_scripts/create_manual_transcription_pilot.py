from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "transcription_pilot.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "manual_transcription_pilot.csv"
)

KEEP_COLUMNS = [
    "segment_id",
    "recording_id",
    "speaker_group_id",
    "dataset_split",
    "duration_seconds",
    "audio_path",
]


if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Pilot file not found:\n{INPUT_FILE}"
    )

pilot_df = pd.read_csv(INPUT_FILE)

missing_columns = [
    column
    for column in KEEP_COLUMNS
    if column not in pilot_df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

manual_df = pilot_df[KEEP_COLUMNS].copy()

manual_df["manual_transcription"] = ""
manual_df["transcription_status"] = "not_started"
manual_df["uncertainty_notes"] = ""
manual_df["review_status"] = "not_reviewed"
manual_df["transcription_time_seconds"] = ""

manual_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8",
)

print(f"Rows created: {len(manual_df)}")
print(f"Saved to: {OUTPUT_FILE}")