# Step 2 — Inventory every character used in the NFC-normalized corpus

from pathlib import Path
from collections import Counter
import pandas as pd
import unicodedata

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata_v1_2_nfc.csv"
)

df = pd.read_csv(INPUT_PATH)

texts = (
    df["transcription"]
    .fillna("")
    .astype(str)
)

character_counts = Counter()

for text in texts:
    character_counts.update(text)

rows = []

for char, count in sorted(
    character_counts.items(),
    key=lambda x: (-x[1], x[0])
):
    if char == " ":
        display_char = "SPACE"
    elif char == "\n":
        display_char = "\\n"
    elif char == "\t":
        display_char = "\\t"
    else:
        display_char = char

    rows.append({
        "character": display_char,
        "count": count,
        "codepoint": f"U+{ord(char):04X}",
        "unicode_name": unicodedata.name(
            char,
            "UNKNOWN"
        ),
    })

inventory = pd.DataFrame(rows)

print("Distinct characters:", len(inventory))
print()

print(
    inventory.to_string(
        index=False
    )
)
# Step 3 — List only letters used in the corpus

letter_counts = Counter()

for text in texts:
    for char in text:
        if unicodedata.category(char).startswith("L"):
            letter_counts[char] += 1

letters_df = pd.DataFrame([
    {
        "letter": char,
        "count": count,
        "codepoint": f"U+{ord(char):04X}",
        "unicode_name": unicodedata.name(
            char,
            "UNKNOWN"
        ),
    }
    for char, count in sorted(
        letter_counts.items(),
        key=lambda x: x[0]
    )
])

print(
    "Distinct letters:",
    len(letters_df)
)

print()

print(
    letters_df.to_string(
        index=False
    )
)