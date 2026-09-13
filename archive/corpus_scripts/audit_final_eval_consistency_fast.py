# Fast linguistic consistency audit for final V1.3 corpus

from pathlib import Path
from collections import Counter
import pandas as pd
from rapidfuzz.distance import Levenshtein


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
# 1. Load corpus
# --------------------------------------------------

df = pd.read_csv(INPUT)

df["transcription"] = (
    df["transcription"]
    .fillna("")
    .astype(str)
    .str.strip()
)

assert len(df) == 1998


# --------------------------------------------------
# 2. Vocabulary by split
# --------------------------------------------------

def tokenize(text):
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
        for word in tokenize(text)
    )


train_val_vocab = (
    split_vocab["train"]
    + split_vocab["validation"]
)

test_vocab = split_vocab["test"]


print("=" * 80)
print("VOCABULARY")
print("=" * 80)

print(
    "Train+validation types:",
    len(train_val_vocab)
)

print(
    "Test types:",
    len(test_vocab)
)


# --------------------------------------------------
# 3. Test-only words
# --------------------------------------------------

test_only = {
    word: count
    for word, count in test_vocab.items()
    if word not in train_val_vocab
}

print(
    "Test-only types:",
    len(test_only)
)


# --------------------------------------------------
# 4. FAST spelling candidate search
# --------------------------------------------------

# Bucket corpus words by length
length_buckets = {}

for word in train_val_vocab:
    length_buckets.setdefault(
        len(word),
        []
    ).append(word)


variant_rows = []

for test_word, test_count in test_only.items():

    possible_lengths = range(
        max(1, len(test_word) - 2),
        len(test_word) + 3,
    )

    candidates = []

    for length in possible_lengths:

        for corpus_word in length_buckets.get(
            length,
            []
        ):

            distance = Levenshtein.distance(
                test_word,
                corpus_word,
                score_cutoff=2,
            )

            if distance > 2:
                continue

            # Distance 1 always interesting
            # Distance 2 only for longer forms
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
                            corpus_word
                        ],
                        corpus_word,
                    )
                )

    candidates.sort()

    for (
        distance,
        negative_count,
        corpus_word,
    ) in candidates[:5]:

        variant_rows.append({
            "test_word":
            test_word,

            "test_count":
            test_count,

            "corpus_candidate":
            corpus_word,

            "corpus_count":
            -negative_count,

            "edit_distance":
            distance,
        })


variants_df = pd.DataFrame(
    variant_rows
)

variants_df.to_csv(
    OUTPUT_DIR
    / "04_possible_spelling_variants.csv",
    index=False,
)

print(
    "Possible spelling pairs:",
    len(variants_df)
)


# --------------------------------------------------
# 5. d/ḍ t/ṭ h/ḥ variants
# --------------------------------------------------

def base_form(word):
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
    groups.setdefault(
        base_form(word),
        set(),
    ).add(word)


diacritic_rows = []

for base, forms in groups.items():

    if len(forms) < 2:
        continue

    # Only interesting if at least one variant occurs in test
    if not any(
        split_vocab["test"][form] > 0
        for form in forms
    ):
        continue

    for form in sorted(forms):

        diacritic_rows.append({
            "base_form":
            base,

            "form":
            form,

            "train_count":
            split_vocab["train"][form],

            "validation_count":
            split_vocab["validation"][form],

            "test_count":
            split_vocab["test"][form],
        })


diacritic_df = pd.DataFrame(
    diacritic_rows
)

diacritic_df.to_csv(
    OUTPUT_DIR
    / "05_diacritic_variants.csv",
    index=False,
)

print(
    "Diacritic variant rows:",
    len(diacritic_df)
)


# --------------------------------------------------
# 6. Word-boundary variants
# --------------------------------------------------

reference_words = set(
    train_val_vocab
)

reference_bigrams = Counter()

reference = df[
    df["dataset_split"]
    .isin(
        [
            "train",
            "validation",
        ]
    )
]

for text in reference["transcription"]:

    words = tokenize(text)

    for i in range(
        len(words) - 1
    ):
        reference_bigrams[
            (
                words[i],
                words[i + 1],
            )
        ] += 1


# Efficient dictionary:
# joined form -> list of possible separated forms

joined_reference_bigrams = {}

for (
    left,
    right,
), count in reference_bigrams.items():

    joined_reference_bigrams.setdefault(
        left + right,
        []
    ).append(
        (
            left,
            right,
            count,
        )
    )


boundary_rows = []

test_rows = df[
    df["dataset_split"] == "test"
]


for _, row in test_rows.iterrows():

    words = tokenize(
        row["transcription"]
    )

    # Test separated, corpus joined
    for i in range(
        len(words) - 1
    ):

        left = words[i]
        right = words[i + 1]

        joined = left + right

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
                train_val_vocab[joined],

                "transcription":
                row["transcription"],
            })


    # Test joined, corpus separated
    for word in words:

        if word not in joined_reference_bigrams:
            continue

        for (
            left,
            right,
            count,
        ) in joined_reference_bigrams[word]:

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
    OUTPUT_DIR
    / "06_possible_word_boundary_variants.csv",
    index=False,
)

print(
    "Boundary candidates:",
    len(boundary_df)
)


# --------------------------------------------------
# 7. Repeated test-only forms
# --------------------------------------------------

repeated_rows = [
    {
        "test_word": word,
        "test_count": count,
    }
    for word, count in test_only.items()
    if count >= 2
]

repeated_df = pd.DataFrame(
    repeated_rows
)

if not repeated_df.empty:
    repeated_df = repeated_df.sort_values(
        [
            "test_count",
            "test_word",
        ],
        ascending=[
            False,
            True,
        ],
    )

repeated_df.to_csv(
    OUTPUT_DIR
    / "07_repeated_test_only_forms.csv",
    index=False,
)

print(
    "Repeated test-only forms:",
    len(repeated_df)
)


# --------------------------------------------------
# 8. Done
# --------------------------------------------------

print("\n" + "=" * 80)
print("FAST AUDIT COMPLETE")
print("=" * 80)

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
    len(repeated_df)
)

print(
    "\nSaved to:",
    OUTPUT_DIR,
)