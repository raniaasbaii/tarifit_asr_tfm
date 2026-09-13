from pathlib import Path
import math
import shutil

import pandas as pd
import soundfile as sf


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path("/Users/mac/masterAI/tarifit_asr_tfm")

CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "spk009_segments_to_append.csv"
)

BACKUP_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "spk009_segments_to_append_before_long_split.csv"
)

MAX_DURATION = 20.0


# --------------------------------------------------
# Load CSV
# --------------------------------------------------

df = pd.read_csv(CSV_PATH)

print("Rows before:", len(df))
print(
    "Segments > 20 s:",
    (df["duration_seconds"] > MAX_DURATION).sum()
)


# --------------------------------------------------
# Backup
# --------------------------------------------------

if not BACKUP_PATH.exists():
    shutil.copy2(CSV_PATH, BACKUP_PATH)
    print("Backup created:", BACKUP_PATH)
else:
    print("Backup already exists:", BACKUP_PATH)


# --------------------------------------------------
# Process rows
# --------------------------------------------------

new_rows = []

for _, row in df.iterrows():

    duration = float(row["duration_seconds"])

    # Normal segment: keep unchanged
    if duration <= MAX_DURATION:
        new_rows.append(row.to_dict())
        continue

    segment_id = row["segment_id"]

    audio_path = PROJECT_ROOT / row["audio_path"]

    if not audio_path.exists():
        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    # --------------------------------------------------
    # KEEP original long row
    # --------------------------------------------------

    original_row = row.to_dict()

    if "status" in original_row:
        original_row["status"] = "to_be_deleted"

    if "review_status" in original_row:
        original_row["review_status"] = "to_be_deleted"

    new_rows.append(original_row)

    # --------------------------------------------------
    # Load audio
    # --------------------------------------------------

    audio, sample_rate = sf.read(audio_path)

    total_samples = len(audio)

    # Minimum number of equal parts required
    n_parts = math.ceil(duration / MAX_DURATION)

    samples_per_part = math.ceil(
        total_samples / n_parts
    )

    print(
        f"\nSplitting {segment_id}: "
        f"{duration:.2f}s -> {n_parts} parts"
    )

    original_start = float(row["start_seconds"])

    # --------------------------------------------------
    # Create split pieces
    # --------------------------------------------------

    for part_idx in range(n_parts):

        sample_start = (
            part_idx * samples_per_part
        )

        sample_end = min(
            (part_idx + 1) * samples_per_part,
            total_samples
        )

        audio_part = audio[
            sample_start:sample_end
        ]

        if len(audio_part) == 0:
            continue

        local_start = sample_start / sample_rate
        local_end = sample_end / sample_rate

        new_start = (
            original_start + local_start
        )

        new_end = (
            original_start + local_end
        )

        new_duration = (
            local_end - local_start
        )

        new_segment_id = (
            f"{segment_id}_PART"
            f"{part_idx + 1:02d}"
        )

        new_audio_path = (
            audio_path.parent
            / f"{new_segment_id}.wav"
        )

        # Save split WAV
        sf.write(
            new_audio_path,
            audio_part,
            sample_rate,
            subtype="PCM_16"
        )

        # --------------------------------------------------
        # New metadata row
        # --------------------------------------------------

        new_row = row.to_dict()

        new_row["segment_id"] = (
            new_segment_id
        )

        new_row["start_seconds"] = round(
            new_start,
            3
        )

        new_row["end_seconds"] = round(
            new_end,
            3
        )

        new_row["duration_seconds"] = round(
            new_duration,
            3
        )

        new_row["audio_path"] = str(
            new_audio_path.relative_to(
                PROJECT_ROOT
            )
        )

        # Empty because you'll map it manually
        new_row["transcription"] = ""

        if "status" in new_row:
            new_row["status"] = (
                "needs_retranscription"
            )

        if "review_status" in new_row:
            new_row["review_status"] = (
                "needs_retranscription"
            )

        new_rows.append(new_row)

        print(
            f"  {new_segment_id}: "
            f"{new_duration:.2f}s"
        )


# --------------------------------------------------
# Save updated CSV
# --------------------------------------------------

new_df = pd.DataFrame(new_rows)

# Preserve original column order
new_df = new_df[df.columns]

new_df.to_csv(
    CSV_PATH,
    index=False,
    encoding="utf-8"
)


# --------------------------------------------------
# Summary
# --------------------------------------------------

print("\nRows before:", len(df))
print("Rows after:", len(new_df))

print(
    "Original long rows marked to_be_deleted:",
    (
        new_df["status"] == "to_be_deleted"
    ).sum()
    if "status" in new_df.columns
    else "status column not found"
)

print(
    "New rows needing transcription:",
    (
        new_df["status"]
        == "needs_retranscription"
    ).sum()
    if "status" in new_df.columns
    else "status column not found"
)

print("\nUpdated CSV:")
print(CSV_PATH)