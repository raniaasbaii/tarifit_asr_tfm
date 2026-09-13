import pandas as pd

df = pd.read_csv(
    "/Users/mac/masterAI/tarifit_asr_tfm/data/metadata/spk009_segments_to_append.csv"
)

print(
    df[df["review_status"] == "needs_retranscription"]["duration_seconds"].describe()
)