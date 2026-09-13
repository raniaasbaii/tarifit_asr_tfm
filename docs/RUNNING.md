# Running and inspecting the project

## Review saved results first

Run `python tools/verify_release.py` from the repository root. No packages or GPU are required. Browse the experiment index and saved notebook outputs. Bootstrap output tables are available under `results/final_test_v1_3/`; the evaluation notebook contains their implementation.

## Re-execute an experiment

1. Obtain audio and the relevant pretrained/selected checkpoint; see RESOURCE_ACCESS.md.
2. Open only the selected notebook for the experiment. Use a separate Colab runtime and run its own dependency installation cell. [Recorded installation cells](NOTEBOOK_DEPENDENCIES.md) show the versions supplied; no complete environment lock was recorded for every run.
3. Update its project, audio, model and output paths. The notebooks originally use `/content/drive/Othercomputers/My MacBook Pro/tarifit_asr_tfm` and, for the newer Kabyle work, `/content/drive/MyDrive/tarifit_asr_tfm`. `docs/notebook_path_inventory.csv` lists their original path-bearing lines. Config/model records are under `model_metadata/` here; that directory is not a loadable model without weights.
4. Preserve the exact frozen development CSV for training and checkpoint selection. Filter the combined final-evaluation CSV to test only. Remap audio paths by segment identity without altering transcripts or split membership.
5. Set a new output directory before executing cells that save results, so the submitted evidence stays intact. Training notebooks can run for hours and require a suitable GPU. Metadata alone is not the processed waveform dataset.
6. Select checkpoints using validation CER, then evaluate the fixed test for reporting. Do not select settings using these already observed test results.

Common controlled notebooks install transformers 4.57.1, datasets 4.4.1 and jiwer 4.0.0; other dependencies are partly range-specified or inherited from Colab. Follow the individual notebook, not a guessed universal dependency lock. Historical KenLM uses additional compiled dependencies and an earlier evaluation partition.

## Corpus-preparation scripts

Scripts under `archive/corpus_scripts/` include sequential, in-place operations developed during corpus creation. `apply_final_split.py` is historical and does not define the final speaker assignment. These scripts require inspection and path adaptation; they are not a safe one-command reconstruction pipeline. Final reconstruction requires the source audio, frozen segment timing/identity metadata and finalized references.
