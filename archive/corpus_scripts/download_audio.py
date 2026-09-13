from pathlib import Path
import subprocess
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CSV_PATH = PROJECT_ROOT / "data" / "metadata" / "recordings.csv"

RAW_AUDIO_DIR = (
    PROJECT_ROOT / "data" / "raw" / "audio_original"
)

PROCESSED_AUDIO_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "wav_16khz_mono"
)

RAW_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CSV_PATH)

required_columns = {"recording_id", "source_url"}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    raise ValueError(
        f"Missing required columns: {sorted(missing_columns)}"
    )


for _, row in df.iterrows():
    recording_id = str(row["recording_id"]).strip()
    source_url = str(row["source_url"]).strip()

    raw_audio_path = RAW_AUDIO_DIR / f"{recording_id}_original.wav"

    processed_audio_path = (
        PROCESSED_AUDIO_DIR / f"{recording_id}.wav"
    )

    if processed_audio_path.exists():
        print(f"{recording_id}: already processed, skipping")
        continue

    if not raw_audio_path.exists():
        print(f"{recording_id}: downloading")

        download_command = [
            "yt-dlp",
            "--no-check-certificates",
            "-x",
            "--audio-format",
            "wav",
            "--no-playlist",
            "-o",
            str(raw_audio_path),
            source_url,
        ]

        try:
            subprocess.run(
                download_command,
                check=True,
            )
        except subprocess.CalledProcessError:
            print(f"{recording_id}: download failed")
            continue

    print(f"{recording_id}: converting to 16 kHz mono")

    conversion_command = [
        "ffmpeg",
        "-y",
        "-i",
        str(raw_audio_path),
        "-ar",
        "16000",
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(processed_audio_path),
    ]

    try:
        subprocess.run(
            conversion_command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"{recording_id}: completed")

    except subprocess.CalledProcessError:
        print(f"{recording_id}: conversion failed")


print("Finished processing recordings.")