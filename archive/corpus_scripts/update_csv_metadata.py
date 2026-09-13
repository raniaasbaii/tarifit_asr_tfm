import pandas as pd

segments = pd.read_csv(
    "data/metadata/segments_metadata.csv"
)

selected = pd.read_csv(
    "data/metadata/selected_recordings.csv"
)

segment_recordings = set(
    segments["recording_id"].dropna().unique()
)

selected_recordings = set(
    selected["recording_id"].dropna().unique()
)

missing = sorted(
    segment_recordings - selected_recordings
)

extra = sorted(
    selected_recordings - segment_recordings
)

print("Recordings used in segments but missing from selected_recordings.csv:")
print(missing)

print("\nSelected recordings with no segments:")
print(extra)