from pathlib import Path
import pandas as pd
import unicodedata
from collections import Counter

PROJECT_ROOT = Path("/Users/mac/masterAI/tarifit_asr_tfm")

METADATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata.csv"
)

df = pd.read_csv(METADATA_PATH)

# --------------------------------------------------
# Define Corpus V1
# --------------------------------------------------

train = df[
    (df["dataset_split"] == "train")
    & (df["speaker_group_id"] == "SPK009")
    & (df["review_status"] == "reviewed")
].copy()

validation = df[
    (df["dataset_split"] == "validation")
    & (df["review_status"] == "reviewed")
    & (df["final_selection"] == "yes")
].copy()

print("=" * 60)
print("CORPUS V1")
print("=" * 60)

print("\nTRAIN")
print("Segments:", len(train))
print("Duration:", round(train["duration_seconds"].sum() / 60, 2), "minutes")
print("Speakers:", sorted(train["speaker_group_id"].unique()))

print("\nVALIDATION")
print("Segments:", len(validation))
print("Duration:", round(validation["duration_seconds"].sum() / 60, 2), "minutes")
print("Speakers:", sorted(validation["speaker_group_id"].unique()))

# --------------------------------------------------
# Transcription checks
# --------------------------------------------------

for name, subset in [
    ("TRAIN", train),
    ("VALIDATION", validation),
]:
    empty = (
        subset["transcription"]
        .fillna("")
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )

    print(f"\n{name} empty transcriptions:", empty)

# --------------------------------------------------
# Duplicate checks
# --------------------------------------------------

combined = pd.concat([train, validation], ignore_index=True)

print("\nDuplicate segment IDs:",
      combined["segment_id"].duplicated().sum())

print("Duplicate audio paths:",
      combined["audio_path"].duplicated().sum())

# --------------------------------------------------
# Speaker leakage
# --------------------------------------------------

train_speakers = set(train["speaker_group_id"])
validation_speakers = set(validation["speaker_group_id"])

overlap = train_speakers & validation_speakers

print("\nTrain-validation speaker overlap:", overlap)

# --------------------------------------------------
# Missing audio
# --------------------------------------------------

missing_audio = []

for _, row in combined.iterrows():
    audio_path = PROJECT_ROOT / row["audio_path"]

    if not audio_path.exists():
        missing_audio.append(
            (row["segment_id"], str(audio_path))
        )

print("\nMissing audio files:", len(missing_audio))

if missing_audio:
    for item in missing_audio[:10]:
        print(item)

# --------------------------------------------------
# Duration checks
# --------------------------------------------------

print("\nSegments > 28 seconds:",
      (combined["duration_seconds"] > 28).sum())

print("Minimum duration:",
      round(combined["duration_seconds"].min(), 3))

print("Maximum duration:",
      round(combined["duration_seconds"].max(), 3))

print("Mean duration:",
      round(combined["duration_seconds"].mean(), 3))

# --------------------------------------------------
# Character inventory
# --------------------------------------------------

all_text = " ".join(
    combined["transcription"]
    .fillna("")
    .astype(str)
)

all_text = unicodedata.normalize("NFC", all_text)

characters = sorted(
    set(all_text) - {" "}
)

print("\nCharacter inventory:")
print(" ".join(characters))

# --------------------------------------------------
# Character frequencies
# --------------------------------------------------

counter = Counter(
    char
    for char in all_text
    if char != " "
)

print("\nCharacter frequencies:")

for char, count in sorted(counter.items()):
    print(f"{repr(char):8} {count}")

# --------------------------------------------------
# Suspicious punctuation
# --------------------------------------------------

punctuation = set('.,!?;:"\'()[]{}…—–')

found_punctuation = sorted(
    set(all_text) & punctuation
)

print("\nUnexpected punctuation:")
print(found_punctuation)

# --------------------------------------------------
# Final decision
# --------------------------------------------------

problems = []

if len(train) == 0:
    problems.append("No train data")

if len(validation) == 0:
    problems.append("No validation data")

if overlap:
    problems.append("Speaker leakage")

if missing_audio:
    problems.append("Missing audio")

if combined["segment_id"].duplicated().any():
    problems.append("Duplicate segment IDs")

if combined["audio_path"].duplicated().any():
    problems.append("Duplicate audio paths")

if found_punctuation:
    problems.append("Unexpected punctuation")

if problems:
    print("\n❌ CORPUS V1 NOT READY")
    print("Problems:", problems)

else:
    print("\n✅ CORPUS V1 READY FOR EXPERIMENTS")