from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path("/Users/mac/masterAI/tarifit_asr_tfm")

CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "rec138_awal_validation.csv"
)

df = pd.read_csv(CSV_PATH)

expected = {
    f"REC138_SEG{i:04d}"
    for i in range(1, 48)
}

actual = set(df["segment_id"])

missing = sorted(expected - actual)

print("Rows:", len(df))
print("Missing segment IDs:", missing)

print("\nLast rows:")
print(
    df[
        [
            "segment_id",
            "start_seconds",
            "end_seconds",
            "duration_seconds",
            "transcription",
        ]
    ].tail(10).to_string(index=False)
)