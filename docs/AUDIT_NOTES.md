# Evidence audit and corrections

## MMS full-data SpecAugment

The saved history reports equal CER at epochs 3 and 4: 0.43267143661066004. Their WER values are 0.8596938775510204 and 0.8499149659863946, respectively. The best-adapter summary selects epoch 3 (step 330); saved validation predictions reproduce **85.97% WER / 43.27% CER**. Use that pair when reporting the selected checkpoint. 84.99% is the epoch-4 WER, not the saved adapter's WER. Test metrics remain 73.13% / 19.59%.

## Corpus versions

The two authoritative CSV hashes match the recorded evaluation hashes. Membership, speaker assignment and duration of development rows agree, but the later combined CSV edits 19 training transcripts. See [the row-level differences](training_transcript_differences.csv). Preserve the original development CSV and use only test rows from the later combined CSV. No data files were corrected or rewritten here.

## Evidence completeness

- The recovered full-data Fadhma notebook has no saved cell outputs; its separate training history, experiment summary and test predictions support inspection of the reported run.
- The quarter-SPK009 Fadhma notebook records the completed run and selected checkpoint-252. Supplied checkpoint metadata ends at checkpoint-126, so a complete selected-model export still needs locating if that model is to be released.
- Model weights and audio were intentionally excluded from the evidence ZIP. Their existence/access cannot be validated from this package.
- Some historical notebooks contain interrupted or failed runs. These are retained as history, not additional valid performance estimates.
- Main final-test `final_model_comparison.csv` contains four adapted models. The external MMS baseline is stored in its own `mms_greedy_baseline` subfolder. Neither file is missing a reported fifth adapted model.
- The Kabyle evaluation notebook's failed broad CSV discovery cell was removed from the selected copy; the succeeding explicit frozen-manifest cell was retained. Its unmodified original is archived.
- The loss-figure notebook embeds recorded plot values. It is retained as plotting provenance, not represented as an automatic plot-from-log script.

Repository packaging did not modify the report, frozen metadata, metrics, model settings or existing GitHub repository.
