# Build corpus V1.3 by adding the finalized held-out test set

from pathlib import Path
import pandas as pd

V1_2_PATH = Path(
    "data/metadata/segments_metadata_v1_2.csv"
)

CLEAN_TEST_METADATA_PATH = Path(
    "data/metadata/test_segments_for_transcription.csv"
)

FINAL_TEST_PATH = Path(
    "data/metadata/final_test_v1_3.csv"
)

OUTPUT_PATH = Path(
    "data/metadata/segments_metadata_v1_3.csv"
)


# --------------------------------------------------
# 1. Load files
# --------------------------------------------------

v12 = pd.read_csv(V1_2_PATH)

test_meta = pd.read_csv(
    CLEAN_TEST_METADATA_PATH
)

test_final = pd.read_csv(
    FINAL_TEST_PATH
)

print("V1.2 rows:", len(v12))
print("Clean test candidate rows:", len(test_meta))
print("Final test rows:", len(test_final))


# --------------------------------------------------
# 2. Basic test checks
# --------------------------------------------------

assert len(test_final) == 115
assert test_final["segment_id"].is_unique

assert set(test_final["recording_id"]) == {
    "REC052",
    "REC059",
}

assert set(test_final["speaker_group_id"]) == {
    "SPK003",
    "SPK004",
}


# --------------------------------------------------
# 3. Get clean metadata for the 115 selected segments
# --------------------------------------------------

final_ids = set(
    test_final["segment_id"]
)

clean_test = test_meta[
    test_meta["segment_id"].isin(final_ids)
].copy()

assert len(clean_test) == 115
assert clean_test["segment_id"].is_unique

missing = (
    final_ids
    - set(clean_test["segment_id"])
)

assert not missing, (
    f"Missing clean metadata for: {missing}"
)


# --------------------------------------------------
# 4. Attach finalized normalized transcription
# --------------------------------------------------

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
            "final_test_transcription"
        }
    )
)

clean_test = clean_test.merge(
    final_text,
    on="segment_id",
    how="left",
    validate="one_to_one",
)

assert (
    clean_test[
        "final_test_transcription"
    ]
    .fillna("")
    .str.strip()
    .ne("")
    .all()
)

clean_test["transcription"] = (
    clean_test[
        "final_test_transcription"
    ]
)

clean_test = clean_test.drop(
    columns=[
        "final_test_transcription"
    ]
)

clean_test["dataset_split"] = "test"

# Mark these as the actual final held-out set
if "final_selection" in clean_test.columns:
    clean_test["final_selection"] = True

if "transcription_status" in clean_test.columns:
    clean_test["transcription_status"] = "final_manual"

if "review_status" in clean_test.columns:
    clean_test["review_status"] = "reviewed"


# --------------------------------------------------
# 5. Keep V1.2 train/validation only
# --------------------------------------------------

v12["dataset_split"] = (
    v12["dataset_split"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
)

base = v12[
    v12["dataset_split"].isin(
        ["train", "validation"]
    )
].copy()

print("\nV1.2 retained:")
print(
    base["dataset_split"]
    .value_counts()
)


# --------------------------------------------------
# 6. Align columns safely
# --------------------------------------------------

all_columns = list(
    dict.fromkeys(
        list(base.columns)
        + list(clean_test.columns)
    )
)

base = base.reindex(
    columns=all_columns
)

clean_test = clean_test.reindex(
    columns=all_columns
)


# --------------------------------------------------
# 7. Build V1.3
# --------------------------------------------------

v13 = pd.concat(
    [
        base,
        clean_test,
    ],
    ignore_index=True,
)

assert v13["segment_id"].is_unique

assert (
    len(
        v13[
            v13["dataset_split"] == "test"
        ]
    )
    == 115
)


# --------------------------------------------------
# 8. Final corpus summary
# --------------------------------------------------

v13["duration_seconds"] = pd.to_numeric(
    v13["duration_seconds"],
    errors="coerce",
)

summary = (
    v13.groupby("dataset_split")
    .agg(
        segments=("segment_id", "count"),
        seconds=("duration_seconds", "sum"),
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

print("\n" + "=" * 80)
print("CORPUS V1.3")
print("=" * 80)

print(summary)

print(
    "\nTotal segments:",
    len(v13),
)


# --------------------------------------------------
# 9. Save
# --------------------------------------------------

v13.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8",
)

print(
    "\nSaved:",
    OUTPUT_PATH,
)