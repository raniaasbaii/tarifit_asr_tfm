# Check — Verify REC052 and REC059 are safe for the test set

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path("/Users/mac/masterAI/tarifit_asr_tfm")

METADATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata_v1_2.csv"
)

df = pd.read_csv(METADATA_PATH)

TEST_RECORDINGS = ["REC052", "REC059"]

test_candidates = df[
    df["recording_id"].isin(TEST_RECORDINGS)
].copy()

print("TEST RECORDINGS")
print("=" * 60)

print(
    test_candidates[
        [
            "recording_id",
            "speaker_group_id",
            "dataset_split",
            "final_selection",
            "duration_seconds",
        ]
    ]
    .drop_duplicates()
    .to_string(index=False)
)

test_speakers = (
    test_candidates["speaker_group_id"]
    .dropna()
    .unique()
)

print("\nTest speakers:", test_speakers)


# Find ALL recordings belonging to those speakers
same_speaker_rows = df[
    df["speaker_group_id"].isin(test_speakers)
]

print("\nALL RECORDINGS FROM TEST SPEAKERS")
print("=" * 60)

print(
    same_speaker_rows[
        [
            "recording_id",
            "speaker_group_id",
            "dataset_split",
        ]
    ]
    .drop_duplicates()
    .sort_values(
        ["speaker_group_id", "recording_id"]
    )
    .to_string(index=False)
)