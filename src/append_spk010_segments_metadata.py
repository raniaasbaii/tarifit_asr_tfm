from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path("/Users/mac/masterAI/tarifit_asr_tfm")

MASTER_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata.csv"
)

AWAL_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "rec138_awal_validation.csv"
)

BACKUP_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata_before_rec138_append.csv"
)

master = pd.read_csv(MASTER_PATH)
awal = pd.read_csv(AWAL_PATH)

print("Master rows before:", len(master))
print("REC138 rows:", len(awal))

# --------------------------------------------------
# Finalize REC138
# --------------------------------------------------

awal["review_status"] = "reviewed"
awal["final_selection"] = "yes"

# --------------------------------------------------
# Safety checks
# --------------------------------------------------

if awal["segment_id"].duplicated().any():
    raise ValueError("Duplicate segment IDs inside REC138 staging CSV.")

existing_ids = set(master["segment_id"])
new_ids = set(awal["segment_id"])

overlap = existing_ids.intersection(new_ids)

if overlap:
    raise ValueError(
        f"{len(overlap)} REC138 segment IDs already exist in master. "
        f"Examples: {list(overlap)[:10]}"
    )

empty = (
    awal["transcription"]
    .fillna("")
    .astype(str)
    .str.strip()
    .eq("")
    .sum()
)

if empty:
    raise ValueError(f"{empty} empty REC138 transcriptions found.")

# --------------------------------------------------
# Backup master
# --------------------------------------------------

master.to_csv(
    BACKUP_PATH,
    index=False,
    encoding="utf-8"
)

# --------------------------------------------------
# Align columns
# --------------------------------------------------

for column in master.columns:
    if column not in awal.columns:
        awal[column] = pd.NA

for column in awal.columns:
    if column not in master.columns:
        master[column] = pd.NA

awal = awal[master.columns]

# --------------------------------------------------
# Append
# --------------------------------------------------

updated = pd.concat(
    [master, awal],
    ignore_index=True
)

updated.to_csv(
    MASTER_PATH,
    index=False,
    encoding="utf-8"
)

# --------------------------------------------------
# Final validation statistics
# --------------------------------------------------

final_validation = updated[
    (updated["dataset_split"] == "validation")
    & (updated["final_selection"] == "yes")
].copy()

print("\nDone.")
print("Master rows after:", len(updated))
print("REC138 appended:", len(awal))
print(
    "Final validation segments:",
    len(final_validation)
)
print(
    "Final validation duration:",
    round(final_validation["duration_seconds"].sum() / 60, 2),
    "minutes"
)
print(
    "Validation speakers:",
    final_validation["speaker_group_id"].nunique()
)
print(
    final_validation["speaker_group_id"].value_counts()
)

print("\nBackup saved to:")
print(BACKUP_PATH)