# Audit final test transcription style against V1.2 corpus

from pathlib import Path
from collections import Counter
import pandas as pd
import re

CORPUS_PATH = Path(
    "data/metadata/segments_metadata_v1_2.csv"
)

TEST_PATH = Path(
    "data/metadata/final_test_v1_3.csv"
)

OUTPUT_DIR = Path(
    "data/metadata/final_test_review"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

corpus = pd.read_csv(CORPUS_PATH)
test = pd.read_csv(TEST_PATH)

# --------------------------------------------------
# 1. Keep only usable normalized references
# --------------------------------------------------

corpus["transcription"] = (
    corpus["transcription"]
    .fillna("")
    .astype(str)
    .str.strip()
)

test["transcription"] = (
    test["transcription"]
    .fillna("")
    .astype(str)
    .str.strip()
)

reference = corpus[
    corpus["transcription"].ne("")
].copy()

assert len(test) == 115
assert test["transcription"].ne("").all()

print("=" * 80)
print("REFERENCE CORPUS")
print("=" * 80)

print("Reference rows:", len(reference))
print("Test rows:", len(test))


# --------------------------------------------------
# 2. Tokenize
# --------------------------------------------------

def words(text):
    return text.split()


corpus_words = Counter(
    word
    for text in reference["transcription"]
    for word in words(text)
)

test_words = Counter(
    word
    for text in test["transcription"]
    for word in words(text)
)

print("\nCorpus word tokens:", sum(corpus_words.values()))
print("Corpus word types:", len(corpus_words))

print("Test word tokens:", sum(test_words.values()))
print("Test word types:", len(test_words))


# --------------------------------------------------
# 3. Test words never seen in train/validation corpus
# --------------------------------------------------

test_only = []

for word, count in test_words.items():
    if word not in corpus_words:
        test_only.append({
            "word": word,
            "test_count": count,
        })

test_only_df = (
    pd.DataFrame(test_only)
    .sort_values(
        ["test_count", "word"],
        ascending=[False, True],
    )
)

TEST_ONLY_PATH = (
    OUTPUT_DIR
    / "test_words_not_seen_in_v1_2.csv"
)

test_only_df.to_csv(
    TEST_ONLY_PATH,
    index=False,
)

print("\n" + "=" * 80)
print("TEST-ONLY WORD TYPES")
print("=" * 80)

print(
    len(test_only_df),
    "of",
    len(test_words),
    "test word types"
)

print("\nMost frequent unseen forms:")

print(
    test_only_df
    .head(50)
    .to_string(index=False)
)


# --------------------------------------------------
# 4. Simple Levenshtein distance
# --------------------------------------------------

def edit_distance(a, b):
    previous = list(range(len(b) + 1))

    for i, ca in enumerate(a, start=1):
        current = [i]

        for j, cb in enumerate(b, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (ca != cb),
                )
            )

        previous = current

    return previous[-1]


# Only compare against corpus vocabulary of roughly
# similar length to avoid nonsense suggestions.

corpus_vocab = list(corpus_words.keys())

similar_rows = []

for word, count in test_words.items():

    if word in corpus_words:
        continue

    candidates = []

    for candidate in corpus_vocab:

        if abs(len(word) - len(candidate)) > 2:
            continue

        distance = edit_distance(
            word,
            candidate,
        )

        # Distance 1 is particularly useful for typo/style detection.
        # Distance 2 is included only for words >= 5 characters.
        if (
            distance == 1
            or (
                distance == 2
                and len(word) >= 5
            )
        ):
            candidates.append(
                (
                    distance,
                    -corpus_words[candidate],
                    candidate,
                )
            )

    candidates.sort()

    for distance, neg_freq, candidate in candidates[:5]:
        similar_rows.append({
            "test_word": word,
            "test_count": count,
            "corpus_candidate": candidate,
            "edit_distance": distance,
            "corpus_count": -neg_freq,
        })


similar_df = pd.DataFrame(similar_rows)

SIMILAR_PATH = (
    OUTPUT_DIR
    / "possible_spelling_variants.csv"
)

similar_df.to_csv(
    SIMILAR_PATH,
    index=False,
)

print("\n" + "=" * 80)
print("POSSIBLE SPELLING VARIANTS")
print("=" * 80)

if similar_df.empty:
    print("None")
else:
    print(
        similar_df
        .head(100)
        .to_string(index=False)
    )


# --------------------------------------------------
# 5. Flag suspicious repeated forms in test
# --------------------------------------------------

# A test-only word repeated several times deserves
# special inspection: it may be a legitimate new word,
# or a systematically different spelling convention.

repeated_test_only = test_only_df[
    test_only_df["test_count"] >= 2
].copy()

REPEATED_PATH = (
    OUTPUT_DIR
    / "repeated_test_only_words.csv"
)

repeated_test_only.to_csv(
    REPEATED_PATH,
    index=False,
)

print("\n" + "=" * 80)
print("REPEATED TEST-ONLY FORMS")
print("=" * 80)

if repeated_test_only.empty:
    print("None")
else:
    print(
        repeated_test_only
        .to_string(index=False)
    )


# --------------------------------------------------
# 6. Show test segments containing repeated new forms
# --------------------------------------------------

important_words = set(
    repeated_test_only["word"]
)

flagged_segments = []

for _, row in test.iterrows():

    row_words = set(
        words(row["transcription"])
    )

    matched = sorted(
        row_words
        & important_words
    )

    if matched:
        flagged_segments.append({
            "segment_id": row["segment_id"],
            "recording_id": row["recording_id"],
            "flagged_words": " | ".join(matched),
            "transcription": row["transcription"],
        })

flagged_df = pd.DataFrame(
    flagged_segments
)

FLAGGED_PATH = (
    OUTPUT_DIR
    / "segments_for_style_review.csv"
)

flagged_df.to_csv(
    FLAGGED_PATH,
    index=False,
    encoding="utf-8",
)

print("\n" + "=" * 80)
print("FILES SAVED")
print("=" * 80)

print(TEST_ONLY_PATH)
print(SIMILAR_PATH)
print(REPEATED_PATH)
print(FLAGGED_PATH)