# Normalize final test V1.3 transcription only

from pathlib import Path
import pandas as pd
import unicodedata
import re

INPUT = Path(
    "data/metadata/final_test_v1_3_pre_normalization.csv"
)

OUTPUT = Path(
    "data/metadata/final_test_v1_3.csv"
)

df = pd.read_csv(INPUT)

assert len(df) == 115


def normalize_transcription(text):
    text = "" if pd.isna(text) else str(text)

    # --------------------------------------------------
    # 1. Unicode composition
    # --------------------------------------------------
    text = unicodedata.normalize("NFC", text)

    # --------------------------------------------------
    # 2. V1.2 orthographic normalization rules
    # --------------------------------------------------

    # Historical/emphatic variants removed in V1.2
    text = text.replace("ṣ", "s")
    text = text.replace("ẓ", "z")
    text = text.replace("ṛ", "r")

    # Affricate
    text = text.replace("ǧ", "dj")

    # Legacy/manual symbols
    text = text.replace("3", "ɛ")
    text = text.replace("o", "u")

    # --------------------------------------------------
    # 3. Whitespace normalization
    # --------------------------------------------------
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    # Final NFC pass
    text = unicodedata.normalize("NFC", text)

    return text


# IMPORTANT:
# Orthographic normalization applies ONLY to transcription.
df["transcription"] = (
    df["transcription"]
    .apply(normalize_transcription)
)

# --------------------------------------------------
# Safety checks
# --------------------------------------------------

ALLOWED_LETTERS = set(
    "a b c d ḍ e ɛ f g h ḥ i j k l m n p q r s t ṭ u v w x y z ɣ ʷ"
    .split()
)

allowed_chars = ALLOWED_LETTERS | {" "}

bad_rows = []

for _, row in df.iterrows():
    text = row["transcription"]

    bad = sorted(
        set(text) - allowed_chars
    )

    if bad:
        bad_rows.append(
            {
                "segment_id": row["segment_id"],
                "bad_characters": bad,
                "transcription": text,
            }
        )

if bad_rows:
    print("\nERROR: characters outside V1.2 alphabet remain:\n")

    print(
        pd.DataFrame(bad_rows)
        .to_string(index=False)
    )

    raise ValueError(
        "Fix remaining invalid characters before freezing test set."
    )

# No combining dot below should remain
assert not any(
    "\u0323" in text
    for text in df["transcription"]
)

# Every transcription must be NFC
assert all(
    text == unicodedata.normalize("NFC", text)
    for text in df["transcription"]
)

# No empty references
assert df["transcription"].str.strip().ne("").all()

# IDs unchanged and unique
assert df["segment_id"].is_unique

df.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8",
)

print("Saved:", OUTPUT)
print("Segments:", len(df))
print(
    "Duration:",
    round(df["duration_seconds"].sum() / 60, 2),
    "minutes",
)
print("✓ All transcription strings are NFC.")
print("✓ No combining dot-below remains.")
print("✓ All characters belong to V1.2 alphabet.")
print("✓ Metadata columns were not orthographically normalized.")