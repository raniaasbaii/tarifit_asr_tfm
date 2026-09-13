from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RECORDINGS_FILE = PROJECT_ROOT / "data/metadata/recordings.csv"
SELECTED_IDS_FILE = PROJECT_ROOT / "data/metadata/selected_recordings.txt"
OUTPUT_FILE = PROJECT_ROOT / "data/metadata/selected_recordings.csv"

# Columns that belong only to the selected corpus workflow
WORKFLOW_COLUMNS = [
    "speaker_group_id",
    "dataset_split",
    "segmentation_status",
    "transcription_status",
    "normalization_status",
    "usable_duration_seconds",
    "annotation_notes",
]

# Load the full recording inventory
recordings_df = pd.read_csv(RECORDINGS_FILE)

# Load the selected IDs
with open(SELECTED_IDS_FILE, "r", encoding="utf-8") as file:
    selected_ids = [
        line.strip()
        for line in file
        if line.strip()
    ]

# Check that every selected ID exists in recordings.csv
missing_ids = sorted(
    set(selected_ids) - set(recordings_df["recording_id"])
)

if missing_ids:
    raise ValueError(
        f"These IDs are missing from recordings.csv: {missing_ids}"
    )

# Create the updated selected corpus from recordings.csv
selected_df = recordings_df[
    recordings_df["recording_id"].isin(selected_ids)
].copy()

# Preserve manually added workflow information from the previous file
if OUTPUT_FILE.exists():
    previous_df = pd.read_csv(OUTPUT_FILE)

    existing_workflow_columns = [
        column
        for column in WORKFLOW_COLUMNS
        if column in previous_df.columns
    ]

    if existing_workflow_columns:
        previous_workflow_df = previous_df[
            ["recording_id"] + existing_workflow_columns
        ]

        selected_df = selected_df.merge(
            previous_workflow_df,
            on="recording_id",
            how="left",
        )

# Add missing workflow columns with default values
default_values = {
    "speaker_group_id": "",
    "dataset_split": "",
    "segmentation_status": "not_started",
    "transcription_status": "not_started",
    "normalization_status": "not_started",
    "usable_duration_seconds": "",
    "annotation_notes": "",
}

for column, default_value in default_values.items():
    if column not in selected_df.columns:
        selected_df[column] = default_value
    else:
        selected_df[column] = selected_df[column].fillna(default_value)

# Keep the order from selected_recordings.txt
selected_df["selection_order"] = selected_df["recording_id"].apply(
    selected_ids.index
)

selected_df = (
    selected_df
    .sort_values("selection_order")
    .drop(columns="selection_order")
)

# Save the updated file
selected_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8",
)

print(f"Selected recordings: {len(selected_df)}")
print(f"Saved to: {OUTPUT_FILE}")

if "duration_seconds" in selected_df.columns:
    total_seconds = int(selected_df["duration_seconds"].sum())

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    print(
        f"Total selected duration: "
        f"{hours}h {minutes}m {seconds}s"
    )

print("\nSelected IDs:")
print(selected_df["recording_id"].tolist())