# ============================================================
# Update historical ř -> r in corpus transcriptions
# Creates Corpus V1.1 orthographic revision
# ============================================================

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path("/Users/mac/masterAI/tarifit_asr_tfm")

MASTER_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata.csv"
)

BACKUP_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata_before_historical_r_cleanup.csv"
)

df = pd.read_csv(MASTER_PATH)

# Backup before modification
df.to_csv(
    BACKUP_PATH,
    index=False,
    encoding="utf-8"
)

before = (
    df["transcription"]
    .fillna("")
    .astype(str)
    .str.count("ř")
    .sum()
)

print("Occurrences of ř before:", before)

df["transcription"] = (
    df["transcription"]
    .fillna("")
    .astype(str)
    .str.replace("ř", "r", regex=False)
)

after = (
    df["transcription"]
    .str.count("ř")
    .sum()
)

df.to_csv(
    MASTER_PATH,
    index=False,
    encoding="utf-8"
)

print("Occurrences of ř after:", after)
print("Backup:", BACKUP_PATH)
print("Updated:", MASTER_PATH)