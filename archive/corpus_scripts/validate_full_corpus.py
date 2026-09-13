from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path("/Users/mac/masterAI/tarifit_asr_tfm")

CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata.csv"
)

df = pd.read_csv(CSV_PATH)

print("Total rows:", len(df))

print("\nSplits:")
print(df["dataset_split"].value_counts(dropna=False))

print("\nSpeakers:")
print(df["speaker_group_id"].value_counts(dropna=False))

print("\nReview status:")
print(df["review_status"].value_counts(dropna=False))

# Duplicate segment IDs
print(
    "\nDuplicate segment IDs:",
    df["segment_id"].duplicated().sum()
)

# Duplicate audio paths
print(
    "Duplicate audio paths:",
    df["audio_path"].duplicated().sum()
)

# Missing audio
missing_audio = []

for p in df["audio_path"]:
    full_path = PROJECT_ROOT / p

    if not full_path.exists():
        missing_audio.append(p)

print("Missing audio files:", len(missing_audio))

# Empty transcriptions
empty_transcriptions = (
    df["transcription"]
    .fillna("")
    .str.strip()
    .eq("")
)

print(
    "Empty transcriptions:",
    empty_transcriptions.sum()
)

# Long segments
print(
    "Segments >20 s:",
    (df["duration_seconds"] > 20).sum()
)

# SPK009 check
spk009 = df[
    df["speaker_group_id"] == "SPK009"
]

print("\nSPK009 rows:", len(spk009))

print("SPK009 splits:")
print(
    spk009["dataset_split"]
    .value_counts(dropna=False)
)