# Prepare final manually transcribed test set for V1.3

from pathlib import Path
import pandas as pd

INPUT = Path(
    "data/metadata/"
    "transcription_queue_test_REC052_REC059_mms_drafts - "
    "transcription_queue_test_REC052_REC059_mms_drafts.csv"
)

OUTPUT = Path(
    "data/metadata/final_test_v1_3_pre_normalization.csv"
)

df = pd.read_csv(INPUT)

# Repair metadata COLUMN NAMES only.
df = df.rename(
    columns={
        "audio_paṭ": "audio_path",
        "colab_audio_paṭ": "colab_audio_path",
    }
)

# Keep only rows that I manually transcribed.
mask = (
    df["transcription"]
    .fillna("")
    .astype(str)
    .str.strip()
    .ne("")
)

test = df.loc[mask].copy()

# Basic sanity checks.
assert len(test) == 115

test["duration_seconds"] = pd.to_numeric(
    test["duration_seconds"],
    errors="raise",
)

assert set(test["recording_id"]) == {
    "REC052",
    "REC059",
}

assert set(test["speaker_group_id"]) == {
    "SPK003",
    "SPK004",
}

assert test["segment_id"].is_unique

# This is now explicitly the final held-out test split.
test["dataset_split"] = "test"

test.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8",
)

print("Saved:", OUTPUT)
print("Segments:", len(test))
print(
    "Duration:",
    round(test["duration_seconds"].sum() / 60, 2),
    "minutes",
)

print("\nBy recording:")
print(
    test.groupby(
        ["recording_id", "speaker_group_id"]
    )
    .agg(
        segments=("segment_id", "count"),
        seconds=("duration_seconds", "sum"),
    )
    .assign(
        minutes=lambda x: x["seconds"] / 60
    )
)