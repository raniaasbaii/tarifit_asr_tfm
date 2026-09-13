# Build exact final evaluation manifest V1.3

from pathlib import Path
import pandas as pd

V1_2_MASTER = Path(
    "data/metadata/segments_metadata_v1_2.csv"
)

FINAL_TEST = Path(
    "data/metadata/final_test_v1_3.csv"
)

CLEAN_TEST_METADATA = Path(
    "data/metadata/test_segments_for_transcription.csv"
)

OUTPUT = Path(
    "data/metadata/segments_metadata_v1_3_final_eval.csv"
)

BAD_VAL_IDS = {
    "REC138_SEG0025",
    "REC138_SEG0033",
    "REC138_SEG0041",
    "REC138_SEG0045",
}


# --------------------------------------------------
# 1. Load files
# --------------------------------------------------

master = pd.read_csv(
    V1_2_MASTER
)

test_final = pd.read_csv(
    FINAL_TEST
)

test_meta = pd.read_csv(
    CLEAN_TEST_METADATA
)


# --------------------------------------------------
# 2. Normalize basic string columns
# --------------------------------------------------

for df in [
    master,
    test_final,
    test_meta,
]:
    for col in [
        "segment_id",
        "recording_id",
        "speaker_group_id",
        "dataset_split",
        "transcription",
    ]:
        if col in df.columns:
            df[col] = (
                df[col]
                .fillna("")
                .astype(str)
                .str.strip()
            )


# --------------------------------------------------
# 3. Recover exact V1.2 experimental train set
# --------------------------------------------------

train = master[
    master["dataset_split"]
    .str.lower()
    .eq("train")
    &
    master["transcription"]
    .ne("")
].copy()

assert len(train) == 1754, (
    f"Expected 1754 train rows, found {len(train)}"
)

train["dataset_split"] = "train"


# --------------------------------------------------
# 4. Recover exact V1.2 validation set
# --------------------------------------------------

validation = master[
    master["dataset_split"]
    .str.lower()
    .eq("validation")
    &
    master["transcription"]
    .ne("")
].copy()

assert len(validation) == 133, (
    f"Expected 133 validation rows before filtering, "
    f"found {len(validation)}"
)

assert BAD_VAL_IDS.issubset(
    set(validation["segment_id"])
)

validation = validation[
    ~validation["segment_id"]
    .isin(BAD_VAL_IDS)
].copy()

assert len(validation) == 129, (
    f"Expected 129 validation rows after filtering, "
    f"found {len(validation)}"
)

validation["dataset_split"] = "validation"


# --------------------------------------------------
# 5. Rebuild final test from clean metadata
# --------------------------------------------------

assert len(test_final) == 115
assert test_final["segment_id"].is_unique

test_ids = set(
    test_final["segment_id"]
)

test = test_meta[
    test_meta["segment_id"]
    .isin(test_ids)
].copy()

assert len(test) == 115
assert test["segment_id"].is_unique

missing = (
    test_ids
    - set(test["segment_id"])
)

assert not missing, (
    f"Missing test metadata for IDs: {missing}"
)


# Attach finalized normalized references

final_text = (
    test_final[
        [
            "segment_id",
            "transcription",
        ]
    ]
    .rename(
        columns={
            "transcription":
            "final_reference"
        }
    )
)

test = test.merge(
    final_text,
    on="segment_id",
    how="left",
    validate="one_to_one",
)

assert (
    test["final_reference"]
    .fillna("")
    .str.strip()
    .ne("")
    .all()
)

test["transcription"] = (
    test["final_reference"]
)

test = test.drop(
    columns=[
        "final_reference"
    ]
)

test["dataset_split"] = "test"


# --------------------------------------------------
# 6. Align columns
# --------------------------------------------------

all_columns = list(
    dict.fromkeys(
        list(train.columns)
        + list(validation.columns)
        + list(test.columns)
    )
)

train = train.reindex(
    columns=all_columns
)

validation = validation.reindex(
    columns=all_columns
)

test = test.reindex(
    columns=all_columns
)


# --------------------------------------------------
# 7. Combine
# --------------------------------------------------

final = pd.concat(
    [
        train,
        validation,
        test,
    ],
    ignore_index=True,
)

assert len(final) == 1998

assert final["segment_id"].is_unique

assert (
    final["dataset_split"]
    .value_counts()
    .to_dict()
    == {
        "train": 1754,
        "validation": 129,
        "test": 115,
    }
)


# --------------------------------------------------
# 8. Speaker leakage checks
# --------------------------------------------------

train_speakers = set(
    train[
        "speaker_group_id"
    ]
)

val_speakers = set(
    validation[
        "speaker_group_id"
    ]
)

test_speakers = set(
    test[
        "speaker_group_id"
    ]
)

assert not (
    train_speakers
    & val_speakers
)

assert not (
    train_speakers
    & test_speakers
)

assert not (
    val_speakers
    & test_speakers
)


# --------------------------------------------------
# 9. Duration summary
# --------------------------------------------------

final["duration_seconds"] = pd.to_numeric(
    final["duration_seconds"],
    errors="raise",
)

summary = (
    final.groupby(
        "dataset_split"
    )
    .agg(
        segments=(
            "segment_id",
            "count",
        ),
        seconds=(
            "duration_seconds",
            "sum",
        ),
        speakers=(
            "speaker_group_id",
            "nunique",
        ),
    )
)

summary["minutes"] = (
    summary["seconds"]
    / 60
)

summary["hours"] = (
    summary["seconds"]
    / 3600
)


# --------------------------------------------------
# 10. Save
# --------------------------------------------------

final.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8",
)

print("=" * 80)
print("FINAL EVALUATION MANIFEST V1.3")
print("=" * 80)

print(summary)

print(
    "\nTotal segments:",
    len(final),
)

print(
    "\nSaved:",
    OUTPUT,
)

print(
    "\n✓ 1754 train"
)

print(
    "✓ 129 validation"
)

print(
    "✓ 115 final test"
)

print(
    "✓ No speaker overlap across splits"
)

print(
    "✓ V1.2 train/validation transcription preserved"
)