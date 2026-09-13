from pathlib import Path

import pandas as pd
import soundfile as sf

from silero_vad import (
    load_silero_vad,
    read_audio,
    get_speech_timestamps,
)


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SELECTED_RECORDINGS_FILE = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "selected_recordings.csv"
)

INPUT_AUDIO_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "wav_16khz_mono"
)

SEGMENTS_ROOT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "segments"
)

COMBINED_METADATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata.csv"
)


# --------------------------------------------------
# Approved segmentation settings
# --------------------------------------------------

SAMPLE_RATE = 16000

MIN_SPEECH_DURATION_MS = 500
MIN_SILENCE_DURATION_MS = 1000
MAX_SPEECH_DURATION_S = 15
SPEECH_PADDING_MS = 200

SEGMENTATION_VERSION = "vad_v1"


# --------------------------------------------------
# Load selected recordings
# --------------------------------------------------

if not SELECTED_RECORDINGS_FILE.exists():
    raise FileNotFoundError(
        f"Metadata file not found:\n"
        f"{SELECTED_RECORDINGS_FILE}"
    )

selected_df = pd.read_csv(
    SELECTED_RECORDINGS_FILE
)

required_columns = [
    "recording_id",
    "speaker_group_id",
    "dataset_split",
]

missing_columns = [
    column
    for column in required_columns
    if column not in selected_df.columns
]

if missing_columns:
    raise ValueError(
        "Missing required columns in "
        f"selected_recordings.csv: {missing_columns}"
    )


# --------------------------------------------------
# Create main output folder
# --------------------------------------------------

SEGMENTS_ROOT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# --------------------------------------------------
# Load Silero VAD once
# --------------------------------------------------

print("Loading Silero VAD model...")

model = load_silero_vad()

all_metadata_rows = []


# --------------------------------------------------
# Process each selected recording
# --------------------------------------------------

for _, recording in selected_df.iterrows():

    recording_id = recording["recording_id"]

    speaker_group_id = recording[
        "speaker_group_id"
    ]

    dataset_split = recording[
        "dataset_split"
    ]

    input_audio = (
        INPUT_AUDIO_DIR
        / f"{recording_id}.wav"
    )

    output_dir = (
        SEGMENTS_ROOT_DIR
        / recording_id
    )

    recording_metadata_file = (
        output_dir
        / f"{recording_id}_segments.csv"
    )

    print()
    print(
        f"Processing {recording_id}..."
    )

    # ----------------------------------------------
    # Check input audio
    # ----------------------------------------------

    if not input_audio.exists():

        print(
            "Skipped: audio file not found."
        )

        continue

    # ----------------------------------------------
    # Reuse already completed segmentation
    # ----------------------------------------------

    if recording_metadata_file.exists():

        print(
            "Already segmented. "
            "Loading existing metadata."
        )

        existing_df = pd.read_csv(
            recording_metadata_file
        )

        # Refresh these values from selected_recordings.csv
        existing_df["speaker_group_id"] = (
            speaker_group_id
        )

        existing_df["dataset_split"] = (
            dataset_split
        )

        # Save the updated recording-level metadata
        existing_df.to_csv(
            recording_metadata_file,
            index=False,
            encoding="utf-8",
        )

        all_metadata_rows.extend(
            existing_df.to_dict(
                orient="records"
            )
        )

        continue

    # ----------------------------------------------
    # Create recording output folder
    # ----------------------------------------------

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ----------------------------------------------
    # Read audio
    # ----------------------------------------------

    audio = read_audio(
        str(input_audio),
        sampling_rate=SAMPLE_RATE,
    )

    # ----------------------------------------------
    # Detect speech
    # ----------------------------------------------

    speech_timestamps = (
        get_speech_timestamps(
            audio,
            model,
            sampling_rate=SAMPLE_RATE,
            min_speech_duration_ms=(
                MIN_SPEECH_DURATION_MS
            ),
            min_silence_duration_ms=(
                MIN_SILENCE_DURATION_MS
            ),
            max_speech_duration_s=(
                MAX_SPEECH_DURATION_S
            ),
            speech_pad_ms=(
                SPEECH_PADDING_MS
            ),
        )
    )

    recording_rows = []

    # ----------------------------------------------
    # Save detected speech segments
    # ----------------------------------------------

    for index, timestamp in enumerate(
        speech_timestamps,
        start=1,
    ):

        start_sample = timestamp["start"]
        end_sample = timestamp["end"]

        start_seconds = (
            start_sample
            / SAMPLE_RATE
        )

        end_seconds = (
            end_sample
            / SAMPLE_RATE
        )

        duration_seconds = (
            end_seconds
            - start_seconds
        )

        segment_id = (
            f"{recording_id}"
            f"_SEG{index:04d}"
        )

        output_audio = (
            output_dir
            / f"{segment_id}.wav"
        )

        segment_audio = audio[
            start_sample:end_sample
        ]

        sf.write(
            output_audio,
            segment_audio.numpy(),
            SAMPLE_RATE,
        )

        row = {
            "segment_id": segment_id,
            "recording_id": recording_id,
            "speaker_group_id": (
                speaker_group_id
            ),
            "dataset_split": (
                dataset_split
            ),
            "segmentation_version": (
                SEGMENTATION_VERSION
            ),
            "start_seconds": round(
                start_seconds,
                3,
            ),
            "end_seconds": round(
                end_seconds,
                3,
            ),
            "duration_seconds": round(
                duration_seconds,
                3,
            ),
            "audio_path": str(
                output_audio.relative_to(
                    PROJECT_ROOT
                )
            ),
            "review_status": (
                "not_reviewed"
            ),
            "transcription": "",
        }

        recording_rows.append(row)

    # ----------------------------------------------
    # Save recording-level metadata
    # ----------------------------------------------

    recording_df = pd.DataFrame(
        recording_rows
    )

    recording_df.to_csv(
        recording_metadata_file,
        index=False,
        encoding="utf-8",
    )

    all_metadata_rows.extend(
        recording_rows
    )

    total_speech_seconds = sum(
        row["duration_seconds"]
        for row in recording_rows
    )

    print(
        f"Created segments: "
        f"{len(recording_rows)}"
    )

    print(
        "Detected speech: "
        f"{total_speech_seconds / 60:.1f} "
        "minutes"
    )


# --------------------------------------------------
# Save combined metadata
# --------------------------------------------------

combined_df = pd.DataFrame(
    all_metadata_rows
)

combined_df.to_csv(
    COMBINED_METADATA_FILE,
    index=False,
    encoding="utf-8",
)


# --------------------------------------------------
# Final summary
# --------------------------------------------------

total_segments = len(
    combined_df
)

total_seconds = (
    combined_df[
        "duration_seconds"
    ].sum()
)

hours = int(
    total_seconds
    // 3600
)

minutes = int(
    (
        total_seconds
        % 3600
    )
    // 60
)

seconds = int(
    total_seconds
    % 60
)

print()
print(
    "--------------------------------"
)

print(
    f"Total segments: "
    f"{total_segments}"
)

print(
    "Total detected speech: "
    f"{hours}h {minutes}m {seconds}s"
)

print(
    "Combined metadata saved to:"
)

print(
    COMBINED_METADATA_FILE
)