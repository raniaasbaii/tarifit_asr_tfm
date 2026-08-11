from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SEGMENTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "transcription_pilot.csv"
)

SAMPLES_PER_GROUP = {
    "SPK001": 10,
    "SPK002": 10,
    "SPK003": 5,
    "SPK008": 5,
}

RANDOM_SEED = 42


df = pd.read_csv(SEGMENTS_FILE)

eligible = df[
    (df["review_status"] == "included")
    & (df["dataset_split"] == "train")
].copy()

pilot_parts = []

for speaker_group_id, sample_size in SAMPLES_PER_GROUP.items():
    speaker_segments = eligible[
        eligible["speaker_group_id"] == speaker_group_id
    ]

    if len(speaker_segments) < sample_size:
        raise ValueError(
            f"{speaker_group_id} has only "
            f"{len(speaker_segments)} eligible segments, "
            f"but {sample_size} were requested."
        )

    selected = speaker_segments.sample(
        n=sample_size,
        random_state=RANDOM_SEED,
    )

    pilot_parts.append(selected)

pilot_df = pd.concat(
    pilot_parts,
    ignore_index=True,
)

pilot_df = pilot_df[
    [
        "segment_id",
        "recording_id",
        "speaker_group_id",
        "dataset_split",
        "duration_seconds",
        "audio_path",
        "review_status",
    ]
].copy()

pilot_df["fastconformer_raw"] = ""
pilot_df["human_notes"] = ""
pilot_df["draft_quality"] = ""
pilot_df["final_transcription"] = ""

pilot_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8",
)

print(f"Pilot segments: {len(pilot_df)}")
print(f"Saved to: {OUTPUT_FILE}")

print("\nSegments by speaker group:")
print(pilot_df["speaker_group_id"].value_counts())

print(
    "\nTotal pilot duration:",
    round(pilot_df["duration_seconds"].sum() / 60, 1),
    "minutes",
)