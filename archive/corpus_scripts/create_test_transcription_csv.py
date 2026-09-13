from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SEGMENTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "test_segments_for_transcription.csv"
)

TEST_SPEAKERS = {
    "SPK003",
    "SPK004",
    "SPK006",
    "SPK008",
}


segments_df = pd.read_csv(SEGMENTS_FILE)

test_df = segments_df[
    segments_df["speaker_group_id"]
    .astype(str)
    .isin(TEST_SPEAKERS)
].copy()

# Safety check: test CSV must contain test rows only.
if not (test_df["dataset_split"] == "test").all():
    raise ValueError(
        "Some selected rows are not assigned to the test split. "
        "Run apply_final_split.py first."
    )

# Add these only if they are not already present.
if "transcription_status" not in test_df.columns:
    test_df["transcription_status"] = "not_started"

if "transcription_notes" not in test_df.columns:
    test_df["transcription_notes"] = ""

test_df = test_df.sort_values(
    ["speaker_group_id", "recording_id", "start_seconds"]
)

test_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8",
)

minutes = test_df["duration_seconds"].sum() / 60

print(f"Created: {OUTPUT_FILE}")
print(f"Segments: {len(test_df)}")
print(f"Total test speech: {minutes:.1f} minutes")
print("\nMinutes by speaker:")
print(
    (test_df.groupby("speaker_group_id")["duration_seconds"].sum() / 60)
    .round(1)
)