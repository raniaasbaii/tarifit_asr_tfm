from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path("/Users/mac/masterAI/tarifit_asr_tfm")

MASTER_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata.csv"
)

SPK007_WORKING_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "spk007_validation_transcription.csv"
)

BACKUP_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata_before_spk007_update.csv"
)

master = pd.read_csv(MASTER_PATH)
working = pd.read_csv(SPK007_WORKING_PATH)

print("Master rows:", len(master))
print("Working SPK007 rows:", len(working))

# --------------------------------------------------
# Keep only rows that actually have a manual transcript
# --------------------------------------------------
working["transcription"] = working["transcription"].fillna("").astype(str).str.strip()

transcribed = working[
    working["transcription"] != ""
].copy()

print("SPK007 manually transcribed rows:", len(transcribed))

# --------------------------------------------------
# Safety checks
# --------------------------------------------------
if transcribed["segment_id"].duplicated().any():
    duplicates = transcribed.loc[
        transcribed["segment_id"].duplicated(),
        "segment_id"
    ].tolist()
    raise ValueError(f"Duplicate segment_ids in working file: {duplicates[:10]}")

missing_ids = set(transcribed["segment_id"]) - set(master["segment_id"])

if missing_ids:
    raise ValueError(
        f"{len(missing_ids)} transcribed segment_ids are missing from master. "
        f"Examples: {list(missing_ids)[:10]}"
    )

# --------------------------------------------------
# Backup master
# --------------------------------------------------
master.to_csv(BACKUP_PATH, index=False, encoding="utf-8")

# --------------------------------------------------
# Add final_selection column if it doesn't exist
# --------------------------------------------------
if "final_selection" not in master.columns:
    master["final_selection"] = "no"

# --------------------------------------------------
# Mark all SPK007 validation rows as NOT selected first
# --------------------------------------------------
spk007_mask = (
    (master["speaker_group_id"] == "SPK007")
    & (master["dataset_split"] == "validation")
)

master.loc[spk007_mask, "final_selection"] = "no"

# --------------------------------------------------
# Update transcription + review status + selection
# --------------------------------------------------
transcription_map = transcribed.set_index("segment_id")["transcription"]

selected_mask = master["segment_id"].isin(transcribed["segment_id"])

master.loc[selected_mask, "transcription"] = (
    master.loc[selected_mask, "segment_id"]
    .map(transcription_map)
)

master.loc[selected_mask, "review_status"] = "reviewed"
master.loc[selected_mask, "final_selection"] = "yes"

# --------------------------------------------------
# Save
# --------------------------------------------------
master.to_csv(MASTER_PATH, index=False, encoding="utf-8")

# --------------------------------------------------
# Final checks
# --------------------------------------------------
final_spk007 = master[
    (master["speaker_group_id"] == "SPK007")
    & (master["dataset_split"] == "validation")
    & (master["final_selection"] == "yes")
].copy()

total_seconds = final_spk007["duration_seconds"].sum()

print("\nDone.")
print("Selected SPK007 segments:", len(final_spk007))
print("Selected duration seconds:", round(total_seconds, 3))
print("Selected duration minutes:", round(total_seconds / 60, 2))
print("Empty selected transcriptions:",
      (final_spk007["transcription"].fillna("").str.strip() == "").sum())
print("Backup saved to:", BACKUP_PATH)
print("Master updated:", MASTER_PATH)