from pathlib import Path

import pandas as pd
import soundfile as sf

from silero_vad import (
    load_silero_vad,
    read_audio,
    get_speech_timestamps,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SELECTED_RECORDINGS_FILE = (
    PROJECT_ROOT / "data" / "metadata" / "selected_recordings.csv"
)

INPUT_AUDIO_DIR = (
    PROJECT_ROOT / "data" / "processed" / "wav_16khz_mono"
)

SEGMENTS_ROOT_DIR = (
    PROJECT_ROOT / "data" / "processed" / "segments"
)

# Separate staging CSV: you will append/update the main CSV yourself.
SPK009_METADATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "spk009_segments_to_append.csv"
)

TARGET_SPEAKER = "SPK009"

SAMPLE_RATE = 16000

MIN_SPEECH_DURATION_MS = 500
MIN_SILENCE_DURATION_MS = 1000
MAX_SPEECH_DURATION_S = 30
SPEECH_PADDING_MS = 200

SEGMENTATION_VERSION = "vad_v2_spk009"


if not SELECTED_RECORDINGS_FILE.exists():
    raise FileNotFoundError(
        f"Metadata file not found:\n{SELECTED_RECORDINGS_FILE}"
    )

selected_df = pd.read_csv(SELECTED_RECORDINGS_FILE)

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
        f"Missing columns in selected_recordings.csv: {missing_columns}"
    )

# Keep only the Bible speaker.
spk009_df = selected_df[
    selected_df["speaker_group_id"].astype(str) == TARGET_SPEAKER
].copy()

if spk009_df.empty:
    raise ValueError(
        f"No recordings found for {TARGET_SPEAKER} "
        "in selected_recordings.csv."
    )

print(f"SPK009 recordings to process: {len(spk009_df)}")

SEGMENTS_ROOT_DIR.mkdir(parents=True, exist_ok=True)

print("Loading Silero VAD model...")
model = load_silero_vad()

all_metadata_rows = []


for _, recording in spk009_df.iterrows():

    recording_id = str(recording["recording_id"])
    speaker_group_id = str(recording["speaker_group_id"])
    dataset_split = str(recording["dataset_split"])

    input_audio = INPUT_AUDIO_DIR / f"{recording_id}.wav"
    output_dir = SEGMENTS_ROOT_DIR / recording_id
    recording_metadata_file = output_dir / f"{recording_id}_segments.csv"

    print(f"\nProcessing {recording_id}...")

    if not input_audio.exists():
        print("Skipped: audio file not found.")
        continue

    # Safe to rerun: existing segment CSV and WAV clips are reused.
    if recording_metadata_file.exists():
        print("Already segmented. Loading existing metadata.")

        existing_df = pd.read_csv(recording_metadata_file)

        existing_df["speaker_group_id"] = speaker_group_id
        existing_df["dataset_split"] = dataset_split

        existing_df.to_csv(
            recording_metadata_file,
            index=False,
            encoding="utf-8",
        )

        all_metadata_rows.extend(
            existing_df.to_dict(orient="records")
        )
        continue

    output_dir.mkdir(parents=True, exist_ok=True)

    audio = read_audio(
        str(input_audio),
        sampling_rate=SAMPLE_RATE,
    )

    speech_timestamps = get_speech_timestamps(
        audio,
        model,
        sampling_rate=SAMPLE_RATE,
        min_speech_duration_ms=MIN_SPEECH_DURATION_MS,
        min_silence_duration_ms=MIN_SILENCE_DURATION_MS,
        max_speech_duration_s=MAX_SPEECH_DURATION_S,
        speech_pad_ms=SPEECH_PADDING_MS,
    )

    recording_rows = []

    for index, timestamp in enumerate(speech_timestamps, start=1):

        start_sample = timestamp["start"]
        end_sample = timestamp["end"]

        start_seconds = start_sample / SAMPLE_RATE
        end_seconds = end_sample / SAMPLE_RATE
        duration_seconds = end_seconds - start_seconds

        segment_id = f"{recording_id}_SEG{index:04d}"
        output_audio = output_dir / f"{segment_id}.wav"

        segment_audio = audio[start_sample:end_sample]

        sf.write(
            output_audio,
            segment_audio.numpy(),
            SAMPLE_RATE,
        )

        recording_rows.append(
            {
                "segment_id": segment_id,
                "recording_id": recording_id,
                "speaker_group_id": speaker_group_id,
                "dataset_split": dataset_split,
                "segmentation_version": SEGMENTATION_VERSION,
                "start_seconds": round(start_seconds, 3),
                "end_seconds": round(end_seconds, 3),
                "duration_seconds": round(duration_seconds, 3),
                "audio_path": str(
                    output_audio.relative_to(PROJECT_ROOT)
                ),
                "review_status": "not_reviewed",
                "transcription": "",
            }
        )

    recording_df = pd.DataFrame(recording_rows)

    recording_df.to_csv(
        recording_metadata_file,
        index=False,
        encoding="utf-8",
    )

    all_metadata_rows.extend(recording_rows)

    print(f"Created segments: {len(recording_rows)}")
    print(
        "Detected speech: "
        f"{sum(row['duration_seconds'] for row in recording_rows) / 60:.1f} minutes"
    )


spk009_segments_df = pd.DataFrame(all_metadata_rows)

spk009_segments_df.to_csv(
    SPK009_METADATA_FILE,
    index=False,
    encoding="utf-8",
)

total_seconds = spk009_segments_df["duration_seconds"].sum()

print("\n--------------------------------")
print(f"Total SPK009 segments: {len(spk009_segments_df)}")
print(f"Total detected speech: {total_seconds / 3600:.2f} hours")
print(f"Saved to:\n{SPK009_METADATA_FILE}")