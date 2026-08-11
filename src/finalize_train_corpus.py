from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path("/Users/mac/masterAI/tarifit_asr_tfm")

CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "spk009_segments_to_append.csv"
)

df = pd.read_csv(CSV_PATH)

print("Total rows:", len(df))

# 1. Review status
print("\nReview status:")
print(df["review_status"].value_counts(dropna=False))

# 2. Empty transcriptions
empty_transcriptions = (
    df["transcription"]
    .fillna("")
    .str.strip()
    .eq("")
)

print(
    "\nEmpty transcriptions:",
    empty_transcriptions.sum()
)

# 3. Duplicate segment IDs
duplicates = df["segment_id"].duplicated()

print(
    "Duplicate segment IDs:",
    duplicates.sum()
)

# 4. Segments >20 seconds
too_long = df["duration_seconds"] > 20

print(
    "Segments >20 seconds:",
    too_long.sum()
)

# 5. Missing audio files
missing_audio = []

for audio_path in df["audio_path"]:
    full_path = PROJECT_ROOT / audio_path

    if not full_path.exists():
        missing_audio.append(audio_path)

print(
    "Missing audio files:",
    len(missing_audio)
)

# 6. Rows still marked for deletion
to_delete = (
    df["review_status"]
    == "to_be_deleted"
)

print(
    "Rows marked to_be_deleted:",
    to_delete.sum()
)