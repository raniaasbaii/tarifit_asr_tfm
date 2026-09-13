from pathlib import Path
import pandas as pd
import re
import unicodedata

PROJECT_ROOT = Path("/Users/mac/masterAI/tarifit_asr_tfm")

METADATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata.csv"
)

BACKUP_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata_before_character_cleanup.csv"
)

df = pd.read_csv(METADATA_PATH)

# Backup first
df.to_csv(
    BACKUP_PATH,
    index=False,
    encoding="utf-8"
)

replacements = {
    "ạ": "a",
    "ṛ": "r",
    "ḏ": "d",
    "č": "c",
    "\u0331": " ",
    "o": "u",
    "I": "i",
    "3": "ɛ",
}


def clean_text(text):
    if pd.isna(text):
        return text

    text = unicodedata.normalize("NFC", str(text))

    for old, new in replacements.items():
        text = text.replace(old, new)

    # normalize whitespace after replacing combining underline with space
    text = re.sub(r"\s+", " ", text).strip()

    return text


df["transcription"] = df["transcription"].apply(clean_text)

df.to_csv(
    METADATA_PATH,
    index=False,
    encoding="utf-8"
)

print("Character cleanup completed.")
print("Backup:", BACKUP_PATH)

# Check that target characters disappeared
all_text = "".join(
    df["transcription"]
    .fillna("")
    .astype(str)
)

print("\nRemaining target characters:")

for char in replacements:
    print(repr(char), all_text.count(char))