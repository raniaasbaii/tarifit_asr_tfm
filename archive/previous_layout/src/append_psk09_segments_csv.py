from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path("/Users/mac/masterAI/tarifit_asr_tfm")

MASTER_CSV = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata.csv"
)

SPK009_CSV = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "spk009_segments_to_append.csv"
)


# Load
master_df = pd.read_csv(MASTER_CSV)
spk009_df = pd.read_csv(SPK009_CSV)

print("Master rows before:", len(master_df))
print("SPK009 rows:", len(spk009_df))


# Make sure column sets match
print("\nMaster columns:")
print(master_df.columns.tolist())

print("\nSPK009 columns:")
print(spk009_df.columns.tolist())


# Check duplicate IDs before appending
existing_spk009 = master_df[
    master_df["segment_id"].isin(
        spk009_df["segment_id"]
    )
]

print(
    "\nSPK009 segment IDs already in master:",
    len(existing_spk009)
)

assert len(existing_spk009) == 0, (
    "Some SPK009 segments are already present in segments.csv."
)


# Reorder SPK009 columns to match master
spk009_df = spk009_df[
    master_df.columns
]


# Append
combined_df = pd.concat(
    [master_df, spk009_df],
    ignore_index=True
)


# Final duplicate check
assert not combined_df["segment_id"].duplicated().any(), (
    "Duplicate segment IDs after append."
)


# Save
combined_df.to_csv(
    MASTER_CSV,
    index=False,
    encoding="utf-8"
)

print("\nMaster rows after:", len(combined_df))
print("Saved:", MASTER_CSV)