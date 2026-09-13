from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path("/Users/mac/masterAI/tarifit_asr_tfm")

METADATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "corpus_v1_1"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(METADATA_PATH)

# --------------------------------------------------
# TRAIN
# --------------------------------------------------

train = df[
    (df["dataset_split"] == "train")
    & (df["speaker_group_id"] == "SPK009")
    & (df["review_status"] == "reviewed")
].copy()

# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

validation = df[
    (df["dataset_split"] == "validation")
    & (df["review_status"] == "reviewed")
    & (df["final_selection"] == "yes")
].copy()

# Keep only experiment-relevant columns
columns = [
    "segment_id",
    "recording_id",
    "speaker_group_id",
    "audio_path",
    "duration_seconds",
    "transcription",
]

train = train[columns].copy()
validation = validation[columns].copy()

# Add absolute path for convenient local checking
train["absolute_audio_path"] = train["audio_path"].apply(
    lambda p: str(PROJECT_ROOT / p)
)

validation["absolute_audio_path"] = validation["audio_path"].apply(
    lambda p: str(PROJECT_ROOT / p)
)

# --------------------------------------------------
# Export
# --------------------------------------------------

train_path = OUTPUT_DIR / "train.csv"
validation_path = OUTPUT_DIR / "validation.csv"

train.to_csv(train_path, index=False, encoding="utf-8")
validation.to_csv(validation_path, index=False, encoding="utf-8")

print("Corpus V1 exported.")
print()
print("TRAIN")
print("Rows:", len(train))
print("Duration:", round(train["duration_seconds"].sum() / 3600, 3), "hours")
print("Saved:", train_path)

print()
print("VALIDATION")
print("Rows:", len(validation))
print(
    "Duration:",
    round(validation["duration_seconds"].sum() / 60, 2),
    "minutes"
)
print("Saved:", validation_path)