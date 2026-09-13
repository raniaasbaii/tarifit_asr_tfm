# Update V1.2 final selection for reviewed training segments

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path("/Users/mac/masterAI/tarifit_asr_tfm")

PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata_v1_2.csv"
)

df = pd.read_csv(PATH)

has_text = (
    df["transcription"]
    .fillna("")
    .astype(str)
    .str.strip()
    .ne("")
)

mask = (
    df["dataset_split"].eq("train")
    & df["review_status"].eq("reviewed")
    & has_text
)

print("Training rows being activated:", mask.sum())

df.loc[mask, "final_selection"] = "yes"

df.to_csv(
    PATH,
    index=False,
    encoding="utf-8"
)

print("\nFinal selected train rows:")
print(
    df[
        df["dataset_split"].eq("train")
        & df["final_selection"].eq("yes")
        & has_text
    ]["review_status"].value_counts()
)