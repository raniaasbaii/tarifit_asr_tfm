# Corpus files

`metadata/segments_metadata_v1_2_train_val_frozen.csv` is the exact development snapshot (1,754 train, 129 validation rows).

`metadata/segments_metadata_v1_3_final_eval.csv` contains 1,998 rows, including the 115-row test partition. Always filter `dataset_split == "test"` when evaluating the final test. Its training transcripts differ from the frozen development snapshot in 19 rows. The validation transcripts, membership, speakers and durations are unchanged.

The split names are train, validation and test. `segment_id` links references to recordings and audio; `speaker_group_id` identifies the speaker grouping used for separation. `audio_path` records original machine paths and must be remapped when running elsewhere.

The test composition is SPK003 (75 segments) and SPK004 (40). Source inventory totals precede segmentation/exclusions and must not be confused with the final experimental corpus.

Earlier CSVs and review material are under `archive/metadata/`; they are not alternate final evaluation references. Read the recorded normalization scripts under `archive/corpus_scripts/` for implementation history; no standalone normalization guide was supplied.

Audio is not bundled or publicly redistributed. The experimental audio
package remains private. No permission was requested or obtained from
the recording owners, and redistribution terms remain to be established.
See [resource access](../docs/RESOURCE_ACCESS.md).

Do not regenerate final segmentation from exploratory scripts and assume
it is identical to the frozen data.
