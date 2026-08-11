from datetime import datetime
from pathlib import Path
import shutil

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SELECTED_RECORDINGS_FILE = (
    PROJECT_ROOT / "data" / "metadata" / "selected_recordings.csv"
)

SEGMENTS_METADATA_FILE = (
    PROJECT_ROOT / "data" / "metadata" / "segments_metadata.csv"
)

SEGMENTS_ROOT_DIR = (
    PROJECT_ROOT / "data" / "processed" / "segments"
)

BACKUP_DIR = (
    PROJECT_ROOT / "data" / "metadata" / "backups"
)

ARCHIVE_ROOT_DIR = (
    PROJECT_ROOT / "data" / "archive" / "removed_spk005_segments"
)


SPLIT_BY_SPEAKER = {
    "SPK001": "train",
    "SPK002": "train",
    "SPK009": "train",
    "SPK007": "validation",
    "SPK003": "test",
    "SPK004": "test",
    "SPK006": "test",
    "SPK008": "test",
}

REMOVED_SPEAKER = "SPK005"


def require_columns(df, columns, filename):
    missing = [column for column in columns if column not in df.columns]

    if missing:
        raise ValueError(
            f"{filename} is missing columns: {missing}"
        )


timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_ROOT_DIR.mkdir(parents=True, exist_ok=True)

selected_df = pd.read_csv(SELECTED_RECORDINGS_FILE)

require_columns(
    selected_df,
    ["recording_id", "speaker_group_id", "dataset_split"],
    SELECTED_RECORDINGS_FILE.name,
)

selected_df["speaker_group_id"] = (
    selected_df["speaker_group_id"].astype(str)
)

# Remove SPK005 from the selected corpus.
selected_df = selected_df[
    selected_df["speaker_group_id"] != REMOVED_SPEAKER
].copy()

unknown_speakers = sorted(
    set(selected_df["speaker_group_id"])
    - set(SPLIT_BY_SPEAKER)
)

if unknown_speakers:
    raise ValueError(
        "These speakers are still in selected_recordings.csv "
        f"but have no assigned split: {unknown_speakers}"
    )

# Apply the frozen split at recording level.
selected_df["dataset_split"] = (
    selected_df["speaker_group_id"].map(SPLIT_BY_SPEAKER)
)

# Back up and save selected_recordings.csv.
selected_backup = (
    BACKUP_DIR
    / f"selected_recordings_before_final_split_{timestamp}.csv"
)

shutil.copy2(SELECTED_RECORDINGS_FILE, selected_backup)

selected_df.to_csv(
    SELECTED_RECORDINGS_FILE,
    index=False,
    encoding="utf-8",
)

print("Updated selected_recordings.csv")
print(selected_df["dataset_split"].value_counts())


# Update existing segment metadata.
segments_df = pd.read_csv(SEGMENTS_METADATA_FILE)

require_columns(
    segments_df,
    [
        "recording_id",
        "speaker_group_id",
        "dataset_split",
    ],
    SEGMENTS_METADATA_FILE.name,
)

segments_df["speaker_group_id"] = (
    segments_df["speaker_group_id"].astype(str)
)

# Identify SPK005 recordings before removing their metadata.
spk005_recording_ids = sorted(
    segments_df.loc[
        segments_df["speaker_group_id"] == REMOVED_SPEAKER,
        "recording_id",
    ]
    .astype(str)
    .unique()
)

# Keep only recordings still selected.
selected_recording_ids = set(
    selected_df["recording_id"].astype(str)
)

updated_segments_df = segments_df[
    segments_df["recording_id"]
    .astype(str)
    .isin(selected_recording_ids)
].copy()

# Refresh speaker and split from selected_recordings.csv.
recording_to_speaker = selected_df.set_index(
    "recording_id"
)["speaker_group_id"]

recording_to_split = selected_df.set_index(
    "recording_id"
)["dataset_split"]

updated_segments_df["speaker_group_id"] = (
    updated_segments_df["recording_id"]
    .map(recording_to_speaker)
)

updated_segments_df["dataset_split"] = (
    updated_segments_df["recording_id"]
    .map(recording_to_split)
)

if updated_segments_df["dataset_split"].isna().any():
    raise ValueError(
        "Some segment rows could not be matched to "
        "selected_recordings.csv."
    )

segments_backup = (
    BACKUP_DIR
    / f"segments_metadata_before_final_split_{timestamp}.csv"
)

shutil.copy2(SEGMENTS_METADATA_FILE, segments_backup)

updated_segments_df.to_csv(
    SEGMENTS_METADATA_FILE,
    index=False,
    encoding="utf-8",
)

print("\nUpdated segments_metadata.csv")
print(updated_segments_df["dataset_split"].value_counts())


# Archive generated SPK005 segment clips safely.
archive_dir = ARCHIVE_ROOT_DIR / timestamp
archive_dir.mkdir(parents=True, exist_ok=True)

for recording_id in spk005_recording_ids:
    segment_folder = SEGMENTS_ROOT_DIR / recording_id

    if not segment_folder.exists():
        print(
            f"\nNo segment folder found for {recording_id}; "
            "nothing to archive."
        )
        continue

    destination = archive_dir / recording_id

    if destination.exists():
        raise FileExistsError(
            f"Archive destination already exists: {destination}"
        )

    shutil.move(str(segment_folder), str(destination))

    print(
        f"\nArchived SPK005 segments:\n"
        f"{segment_folder}\n"
        f"→ {destination}"
    )


print("\n--------------------------------")
print("Final split applied:")
for speaker, split in SPLIT_BY_SPEAKER.items():
    print(f"{speaker}: {split}")

print("\nSPK005 was removed from selected recordings and segment metadata.")
print("Original SPK005 full WAV files were kept.")