# Check 2 — Audit precomposed and decomposed diacritic letters

from pathlib import Path
import pandas as pd
import unicodedata

PROJECT_ROOT = Path("/Users/mac/masterAI/tarifit_asr_tfm")

METADATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata_v1_2_pre_normalization.csv"
)

df = pd.read_csv(METADATA_PATH)

texts = (
    df["transcription"]
    .fillna("")
    .astype(str)
)

characters_to_check = {
    "ṭ": "t + dot below",
    "ḍ": "d + dot below",
    "ḥ": "h + dot below",
    "ṣ": "s + dot below",
    "ẓ": "z + dot below",
    "ṛ": "r + dot below",
    "ǧ": "g + caron",
}

print("Unicode audit")
print("=" * 60)

for char, description in characters_to_check.items():

    # Decompose the intended character, e.g.
    # ṭ -> t + U+0323
    decomposed = unicodedata.normalize(
        "NFD",
        char
    )

    precomposed_count = sum(
        text.count(char)
        for text in texts
    )

    decomposed_count = sum(
        text.count(decomposed)
        for text in texts
    )

    print(f"\n{char} — {description}")
    print("Precomposed :", precomposed_count)
    print("Decomposed  :", decomposed_count)

    print(
        "NFD form    :",
        [
            f"{c} U+{ord(c):04X}"
            for c in decomposed
        ]
    )


# Check complete rows that are not already NFC-normalized
not_nfc = df[
    df["transcription"]
    .fillna("")
    .astype(str)
    .apply(
        lambda x:
        x != unicodedata.normalize("NFC", x)
    )
]

print("\n" + "=" * 60)
print("Rows not in NFC:", len(not_nfc))

if len(not_nfc):
    print(
        not_nfc[
            [
                "segment_id",
                "speaker_group_id",
                "transcription",
            ]
        ]
        .head(30)
        .to_string(index=False)
    )