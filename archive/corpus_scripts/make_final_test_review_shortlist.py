# Create a high-priority manual consistency review shortlist

from pathlib import Path
import pandas as pd

REVIEW_DIR = Path(
    "data/metadata/final_eval_review"
)

FINAL_MANIFEST = Path(
    "data/metadata/segments_metadata_v1_3_final_eval.csv"
)

OUT = REVIEW_DIR / "08_priority_manual_review.csv"


# --------------------------------------------------
# 1. Load audit outputs
# --------------------------------------------------

spelling = pd.read_csv(
    REVIEW_DIR / "04_possible_spelling_variants.csv"
)

diacritics = pd.read_csv(
    REVIEW_DIR / "05_diacritic_variants.csv"
)

boundaries = pd.read_csv(
    REVIEW_DIR / "06_possible_word_boundary_variants.csv"
)

manifest = pd.read_csv(
    FINAL_MANIFEST
)

test = manifest[
    manifest["dataset_split"] == "test"
].copy()


review_rows = []


# --------------------------------------------------
# 2. High-priority spelling variants
# --------------------------------------------------
# Very similar to an existing form AND:
# - test uses it more than once, OR
# - corpus form is common.

sp = spelling[
    (spelling["edit_distance"] == 1)
    & (
        (spelling["test_count"] >= 2)
        | (spelling["corpus_count"] >= 5)
    )
].copy()

for _, row in sp.iterrows():

    affected = test[
        test["transcription"]
        .str.split()
        .apply(
            lambda words:
            row["test_word"] in words
        )
    ]

    for _, seg in affected.iterrows():

        review_rows.append({
            "priority": "HIGH",
            "category": "spelling",
            "segment_id": seg["segment_id"],

            "test_form":
            row["test_word"],

            "reference_candidate":
            row["corpus_candidate"],

            "test_count":
            row["test_count"],

            "reference_count":
            row["corpus_count"],

            "reason":
            f"edit distance 1; corpus form occurs "
            f"{row['corpus_count']} times",

            "transcription":
            seg["transcription"],
        })


# --------------------------------------------------
# 3. Diacritic variants
# --------------------------------------------------

diacritics["reference_count"] = (
    diacritics["train_count"]
    + diacritics["validation_count"]
)

for base, group in diacritics.groupby(
    "base_form"
):

    test_forms = group[
        group["test_count"] > 0
    ]

    reference_forms = group[
        group["reference_count"] > 0
    ]

    for _, test_form in test_forms.iterrows():

        alternatives = reference_forms[
            reference_forms["form"]
            != test_form["form"]
        ]

        if alternatives.empty:
            continue

        # Most frequent competing corpus form
        best = alternatives.sort_values(
            "reference_count",
            ascending=False
        ).iloc[0]

        # Only flag meaningful corpus evidence
        if best["reference_count"] < 3:
            continue

        affected = test[
            test["transcription"]
            .str.split()
            .apply(
                lambda words:
                test_form["form"] in words
            )
        ]

        for _, seg in affected.iterrows():

            review_rows.append({
                "priority": "HIGH",
                "category": "diacritic",
                "segment_id":
                seg["segment_id"],

                "test_form":
                test_form["form"],

                "reference_candidate":
                best["form"],

                "test_count":
                test_form["test_count"],

                "reference_count":
                best["reference_count"],

                "reason":
                f"same base '{base}' has a common "
                f"alternative in train/validation",

                "transcription":
                seg["transcription"],
            })


# --------------------------------------------------
# 4. Word-boundary variants
# --------------------------------------------------

bd = boundaries[
    boundaries["corpus_count"] >= 3
].copy()

for _, row in bd.iterrows():

    review_rows.append({
        "priority": "HIGH",
        "category": "word_boundary",
        "segment_id":
        row["segment_id"],

        "test_form":
        row["test_form"],

        "reference_candidate":
        row["corpus_form"],

        "test_count":
        None,

        "reference_count":
        row["corpus_count"],

        "reason":
        row["type"],

        "transcription":
        row["transcription"],
    })


# --------------------------------------------------
# 5. Create shortlist
# --------------------------------------------------

review = pd.DataFrame(
    review_rows
)

if not review.empty:

    review = review.drop_duplicates(
        subset=[
            "category",
            "segment_id",
            "test_form",
            "reference_candidate",
        ]
    )

    review = review.sort_values(
        [
            "category",
            "reference_count",
        ],
        ascending=[
            True,
            False,
        ]
    )


review.to_csv(
    OUT,
    index=False,
    encoding="utf-8",
)

print("=" * 80)
print("PRIORITY MANUAL REVIEW")
print("=" * 80)

print("Candidates:", len(review))

if not review.empty:

    print("\nBy category:")
    print(
        review["category"]
        .value_counts()
    )

    print("\nFirst 60 candidates:\n")

    print(
        review[
            [
                "category",
                "segment_id",
                "test_form",
                "reference_candidate",
                "test_count",
                "reference_count",
            ]
        ]
        .head(60)
        .to_string(index=False)
    )

print("\nSaved:", OUT)