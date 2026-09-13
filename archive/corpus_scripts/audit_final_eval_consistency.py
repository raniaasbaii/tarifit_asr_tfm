# Audit writing consistency across final V1.3 train/validation/test corpus

from pathlib import Path
from collections import Counter
import pandas as pd
import unicodedata
import re


INPUT = Path(
    "data/metadata/segments_metadata_v1_3_final_eval.csv"
)

OUTPUT_DIR = Path(
    "data/metadata/final_eval_review"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# --------------------------------------------------
# 1. Load exact final evaluation corpus
# --------------------------------------------------

df = pd.read_csv(INPUT)

df["transcription"] = (
    df["transcription"]
    .fillna("")
    .astype(str)
    .str.strip()
)

assert len(df) == 1998

assert (
    df["dataset_split"]
    .value_counts()
    .to_dict()
    == {
        "train": 1754,
        "validation": 129,
        "test": 115,
    }
)

print("=" * 90)
print("FINAL CORPUS")
print("=" * 90)

print(
    df["dataset_split"]
    .value_counts()
)

print(
    "\nEmpty transcriptions:",
    df["transcription"].eq("").sum()
)


# --------------------------------------------------
# 2. Character-level audit
# --------------------------------------------------

ALPHABET = set(
    "a b c d ḍ e ɛ f g h ḥ i j k l m n p q r s t ṭ u v w x y z ɣ ʷ"
    .split()
)

ALLOWED = ALPHABET | {" "}

character_issues = []

for _, row in df.iterrows():

    text = row["transcription"]

    bad = sorted(
        set(text) - ALLOWED
    )

    if bad:
        character_issues.append({
            "segment_id": row["segment_id"],
            "dataset_split": row["dataset_split"],
            "bad_characters": " ".join(bad),
            "transcription": text,
        })


char_df = pd.DataFrame(
    character_issues
)

char_df.to_csv(
    OUTPUT_DIR / "01_character_issues.csv",
    index=False,
)

print("\nCharacter issues:", len(char_df))


# --------------------------------------------------
# 3. Formatting audit
# --------------------------------------------------

format_issues = []

for _, row in df.iterrows():

    text = row["transcription"]

    reasons = []

    if text != text.strip():
        reasons.append("leading/trailing whitespace")

    if "  " in text:
        reasons.append("double spaces")

    if text != unicodedata.normalize(
        "NFC",
        text,
    ):
        reasons.append("not NFC")

    if re.search(r"[A-Z]", text):
        reasons.append("uppercase")

    if reasons:
        format_issues.append({
            "segment_id": row["segment_id"],
            "dataset_split": row["dataset_split"],
            "issue": " | ".join(reasons),
            "transcription": text,
        })


format_df = pd.DataFrame(
    format_issues
)

format_df.to_csv(
    OUTPUT_DIR / "02_formatting_issues.csv",
    index=False,
)

print("Formatting issues:", len(format_df))


# --------------------------------------------------
# 4. Build vocabulary by split
# --------------------------------------------------

def tokens(text):
    return text.split()


split_vocab = {}

for split in [
    "train",
    "validation",
    "test",
]:

    subset = df[
        df["dataset_split"] == split
    ]

    split_vocab[split] = Counter(
        word
        for text in subset["transcription"]
        for word in tokens(text)
    )


train_val_vocab = (
    split_vocab["train"]
    + split_vocab["validation"]
)

test_vocab = split_vocab["test"]


print("\nVocabulary:")
print(
    "Train+validation types:",
    len(train_val_vocab)
)

print(
    "Test types:",
    len(test_vocab)
)


# --------------------------------------------------
# 5. Test words unseen in train/validation
# --------------------------------------------------

unseen_rows = []

for word, count in test_vocab.items():

    if word not in train_val_vocab:
        unseen_rows.append({
            "test_word": word,
            "test_count": count,
        })


unseen_df = pd.DataFrame(
    unseen_rows
)

if not unseen_df.empty:
    unseen_df = unseen_df.sort_values(
        [
            "test_count",
            "test_word",
        ],
        ascending=[
            False,
            True,
        ],
    )


unseen_df.to_csv(
    OUTPUT_DIR / "03_test_words_unseen_in_train_val.csv",
    index=False,
)

print(
    "Test-only word types:",
    len(unseen_df)
)


# --------------------------------------------------
# 6. Edit-distance spelling candidates
# --------------------------------------------------

def edit_distance(a, b):

    prev = list(
        range(
            len(b) + 1
        )
    )

    for i, ca in enumerate(
        a,
        start=1,
    ):

        curr = [i]

        for j, cb in enumerate(
            b,
            start=1,
        ):

            curr.append(
                min(
                    curr[-1] + 1,
                    prev[j] + 1,
                    prev[j - 1]
                    + (ca != cb),
                )
            )

        prev = curr

    return prev[-1]


reference_vocab = list(
    train_val_vocab.keys()
)

variant_rows = []

for test_word, test_count in test_vocab.items():

    if test_word in train_val_vocab:
        continue

    candidates = []

    for reference_word in reference_vocab:

        if abs(
            len(test_word)
            - len(reference_word)
        ) > 2:
            continue

        distance = edit_distance(
            test_word,
            reference_word,
        )

        if (
            distance == 1
            or (
                distance == 2
                and len(test_word) >= 5
            )
        ):

            candidates.append(
                (
                    distance,
                    -train_val_vocab[
                        reference_word
                    ],
                    reference_word,
                )
            )

    candidates.sort()

    for (
        distance,
        negative_frequency,
        reference_word,
    ) in candidates[:5]:

        variant_rows.append({
            "test_word": test_word,
            "test_count": test_count,
            "corpus_candidate": reference_word,
            "corpus_count": -negative_frequency,
            "edit_distance": distance,
        })


variants_df = pd.DataFrame(
    variant_rows
)

variants_df.to_csv(
    OUTPUT_DIR / "04_possible_spelling_variants.csv",
    index=False,
)

print(
    "Possible spelling-variant pairs:",
    len(variants_df)
)


# --------------------------------------------------
# 7. d / ḍ, t / ṭ and h / ḥ consistency candidates
# --------------------------------------------------

def de_emphasize(word):

    return (
        word
        .replace("ḍ", "d")
        .replace("ṭ", "t")
        .replace("ḥ", "h")
    )


all_vocab = (
    split_vocab["train"]
    + split_vocab["validation"]
    + split_vocab["test"]
)

groups = {}

for word in all_vocab:

    base = de_emphasize(
        word
    )

    groups.setdefault(
        base,
        []
    ).append(word)


diacritic_rows = []

for base, forms in groups.items():

    forms = sorted(
        set(forms)
    )

    if len(forms) <= 1:
        continue

    for form in forms:

        diacritic_rows.append({
            "base_form": base,
            "form": form,

            "train_count":
            split_vocab["train"][
                form
            ],

            "validation_count":
            split_vocab[
                "validation"
            ][form],

            "test_count":
            split_vocab["test"][
                form
            ],
        })


diacritic_df = pd.DataFrame(
    diacritic_rows
)

diacritic_df.to_csv(
    OUTPUT_DIR / "05_diacritic_variants.csv",
    index=False,
)

print(
    "Diacritic-variant rows:",
    len(diacritic_df)
)


# --------------------------------------------------
# 8. Possible joined/separated word-boundary variants
# --------------------------------------------------

reference_words = set(
    train_val_vocab.keys()
)

boundary_rows = []

test_rows = df[
    df["dataset_split"] == "test"
]

for _, row in test_rows.iterrows():

    words = tokens(
        row["transcription"]
    )

    for i in range(
        len(words) - 1
    ):

        left = words[i]
        right = words[i + 1]

        joined = (
            left + right
        )

        if joined in reference_words:

            boundary_rows.append({
                "segment_id":
                row["segment_id"],

                "test_form":
                left + " " + right,

                "corpus_form":
                joined,

                "type":
                "test separated / corpus joined",

                "corpus_count":
                train_val_vocab[
                    joined
                ],

                "transcription":
                row["transcription"],
            })


# Opposite direction:
# test has one word which may correspond to
# two reference words.

reference_bigrams = Counter()

reference_rows = df[
    df["dataset_split"]
    .isin(
        [
            "train",
            "validation",
        ]
    )
]

for text in reference_rows[
    "transcription"
]:

    words = tokens(text)

    for i in range(
        len(words) - 1
    ):

        reference_bigrams[
            (
                words[i],
                words[i + 1],
            )
        ] += 1


for _, row in test_rows.iterrows():

    words = tokens(
        row["transcription"]
    )

    for word in words:

        for (
            left,
            right,
        ), count in reference_bigrams.items():

            if (
                left + right
                == word
            ):

                boundary_rows.append({
                    "segment_id":
                    row["segment_id"],

                    "test_form":
                    word,

                    "corpus_form":
                    left + " " + right,

                    "type":
                    "test joined / corpus separated",

                    "corpus_count":
                    count,

                    "transcription":
                    row["transcription"],
                })


boundary_df = pd.DataFrame(
    boundary_rows
)

boundary_df.to_csv(
    OUTPUT_DIR / "06_possible_word_boundary_variants.csv",
    index=False,
)

print(
    "Possible word-boundary variants:",
    len(boundary_df)
)


# --------------------------------------------------
# 9. Repeated test-only forms
# --------------------------------------------------

repeated_unseen = unseen_df[
    unseen_df["test_count"] >= 2
].copy()

repeated_unseen.to_csv(
    OUTPUT_DIR / "07_repeated_test_only_forms.csv",
    index=False,
)

print(
    "Repeated test-only forms:",
    len(repeated_unseen)
)


# --------------------------------------------------
# 10. Final summary
# --------------------------------------------------

print("\n" + "=" * 90)
print("AUDIT COMPLETE")
print("=" * 90)

print(
    "01_character_issues.csv:",
    len(char_df)
)

print(
    "02_formatting_issues.csv:",
    len(format_df)
)

print(
    "03_test_words_unseen_in_train_val.csv:",
    len(unseen_df)
)

print(
    "04_possible_spelling_variants.csv:",
    len(variants_df)
)

print(
    "05_diacritic_variants.csv:",
    len(diacritic_df)
)

print(
    "06_possible_word_boundary_variants.csv:",
    len(boundary_df)
)

print(
    "07_repeated_test_only_forms.csv:",
    len(repeated_unseen)
)

print(
    "\nSaved review files to:",
    OUTPUT_DIR
)