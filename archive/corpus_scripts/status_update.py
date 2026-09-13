import pandas as pd

CSV_PATH = "/Users/mac/masterAI/tarifit_asr_tfm/data/metadata/spk009_segments_to_append.csv"

df = pd.read_csv(CSV_PATH)

# Original long segments: keep them, but mark for deletion
mask_original_long = (
    (df["duration_seconds"] > 20)
    & (~df["segment_id"].str.contains("_PART", na=False))
)

df.loc[
    mask_original_long,
    "review_status"
] = "to_be_deleted"

# New split segments: mark for retranscription
mask_split_parts = df["segment_id"].str.contains(
    "_PART",
    na=False
)

df.loc[
    mask_split_parts,
    "review_status"
] = "needs_retranscription"

# Save
df.to_csv(
    CSV_PATH,
    index=False,
    encoding="utf-8"
)

print("Original long rows marked to_be_deleted:",
      (df["review_status"] == "to_be_deleted").sum())

print("Split rows marked needs_retranscription:",
      (df["review_status"] == "needs_retranscription").sum())

print("Total rows:", len(df))