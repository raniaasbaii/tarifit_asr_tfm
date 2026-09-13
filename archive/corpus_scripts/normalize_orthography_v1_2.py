# Step 1 — Apply the final V1.2 orthographic normalization

from pathlib import Path
from collections import Counter
import pandas as pd
import unicodedata


# ============================================================
# 1. Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata_v1_2_nfc.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata_v1_2.csv"
)


# ============================================================
# 2. Load metadata
# ============================================================

df = pd.read_csv(INPUT_PATH)

df["transcription"] = (
    df["transcription"]
    .fillna("")
    .astype(str)
)

print("Rows:", len(df))


# ============================================================
# 3. Define final orthographic replacements
# ============================================================

REPLACEMENTS = {
    "ṣ": "s",
    "ẓ": "z",
    "ṛ": "r",
    "ǧ": "dj",
    "3": "ɛ",
    "o": "u",
    "\u0323": "",   # x + COMBINING DOT BELOW
}


# ============================================================
# 4. Count replacements before changing anything
# ============================================================

print("\nOccurrences before normalization:")
print("=" * 50)

for old, new in REPLACEMENTS.items():

    count = sum(
        text.count(old)
        for text in df["transcription"]
    )

    visible_old = (
    "standalone combining dot below"
    if old == "\u0323"
    else old
    )

    print(
        f"{visible_old!r} -> {new!r}: "
        f"{count}"
    )


# ============================================================
# 5. Apply normalization
# ============================================================

def normalize_transcription(text):

    # Make Unicode representation consistent first.
    text = unicodedata.normalize(
        "NFC",
        text
    )

    for old, new in REPLACEMENTS.items():
        text = text.replace(
            old,
            new
        )

    # Normalize again after replacements.
    text = unicodedata.normalize(
        "NFC",
        text
    )

    return text


df["transcription"] = (
    df["transcription"]
    .apply(normalize_transcription)
)


# ============================================================
# 6. Define final allowed alphabet
# ============================================================

FINAL_LETTERS = set(
    "abcdefghijklmn"
    "pqrstuvwxyz"
)

# Remove o because final convention maps o -> u.
FINAL_LETTERS.discard("o")

FINAL_LETTERS.update({
    "ɛ",
    "ɣ",
    "ʷ",
    "ḍ",
    "ḥ",
    "ṭ",
})

ALLOWED_CHARACTERS = (
    FINAL_LETTERS
    | {" "}
)


# ============================================================
# 7. Check for unexpected characters
# ============================================================

unexpected = Counter()

for text in df["transcription"]:

    for char in text:

        if char not in ALLOWED_CHARACTERS:
            unexpected[char] += 1


print("\nUnexpected characters after normalization:")
print("=" * 50)

if unexpected:

    for char, count in unexpected.items():

        print(
            repr(char),
            count,
            f"U+{ord(char):04X}",
            unicodedata.name(
                char,
                "UNKNOWN"
            )
        )

else:

    print("✓ None")


# ============================================================
# 8. Ensure no combining marks remain
# ============================================================

combining_marks = Counter()

for text in df["transcription"]:

    for char in text:

        if unicodedata.combining(char):
            combining_marks[char] += 1


print("\nCombining marks remaining:")
print("=" * 50)

if combining_marks:

    for char, count in combining_marks.items():
        print(
            repr(char),
            count,
            unicodedata.name(
                char,
                "UNKNOWN"
            )
        )

else:
    print("✓ None")


# ============================================================
# 9. Generate final letter inventory
# ============================================================

letter_counts = Counter()

for text in df["transcription"]:

    for char in text:

        if (
            unicodedata
            .category(char)
            .startswith("L")
        ):
            letter_counts[char] += 1


print("\nFinal letters:")
print("=" * 50)

for char, count in sorted(
    letter_counts.items()
):
    print(
        f"{char:3s} {count:6d}"
    )


print(
    "\nNumber of distinct letters:",
    len(letter_counts)
)


# ============================================================
# 10. Final assertions
# ============================================================

assert not unexpected, (
    "Unexpected characters remain. "
    "Do not save final metadata yet."
)

assert not combining_marks, (
    "Combining marks remain. "
    "Do not save final metadata yet."
)

for forbidden in [
    "ṣ",
    "ẓ",
    "ṛ",
    "ǧ",
    "o",
    "3",
]:
    assert not any(
        forbidden in text
        for text in df["transcription"]
    ), (
        f"Forbidden character still present: {forbidden}"
    )


# ============================================================
# 11. Save final normalized V1.2 metadata
# ============================================================

df.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8"
)

print("\n============================================")
print("V1.2 ORTHOGRAPHIC NORMALIZATION COMPLETE")
print("============================================")

print("\nSaved final normalized metadata:")
print(OUTPUT_PATH)

