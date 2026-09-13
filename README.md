# Tarifit automatic speech recognition

**Development and Evaluation of an Automatic Speech Recognition System for Tarifit**  
Rania Asbai · Master's Degree in Artificial Intelligence · University of Alicante  
Supervisor: Miquel Esplà Gomis

This project constructs a continuous-speech Tarifit corpus with Latin-script transcriptions and evaluates multilingual speech models and Kabyle-to-Tarifit transfer.

## Start here

1. [Experiment index](docs/EXPERIMENTS.md): each experiment, notebook and saved evidence.
2. [Corpus and split definitions](data/README.md).
3. [Run and environment instructions](docs/RUNNING.md).
4. [Audit findings and report corrections](docs/AUDIT_NOTES.md).
5. [Model and audio availability](docs/RESOURCE_ACCESS.md).

This repository supports inspection and recalculation of the saved results.
Links to five selected model exports are provided in
[the checkpoint access table](models/checkpoint_access.csv).
Public access and loading from fresh downloads have not yet been verified.

The corpus audio is not publicly redistributed. A private experimental
audio package has been prepared, but redistribution permissions have not
been obtained from the recording owners. See
[model and audio access](docs/RESOURCE_ACCESS.md) for details.

The notebooks retain their original Colab execution code and recorded
outputs. Re-execution requires the relevant resources, dependencies
and path adjustments described in [the running instructions](docs/RUNNING.md).

## Corpus

| Partition | Segments | Hours | Speaker groups |
|---|---:|---:|---|
| Training | 1,754 | 5.223 | SPK001, SPK002, SPK009 |
| Validation | 129 | 0.298 | SPK007, SPK010 |
| Test | 115 | 0.299 | SPK003, SPK004 |

Use the frozen V1.2 CSV for training/validation and only the test rows from the V1.3 combined CSV for final evaluation. The later combined file contains 19 edited training transcripts; those edits must not silently replace the development snapshot.

## Main test results

All rows below use the same 115 test segments. Lower error rates are better.

| System | WER % | CER % | CER without spaces % |
|---|---:|---:|---:|
| External MMS-Tachebdant | 66.98 | 21.96 | 21.55 |
| MMS, half-SPK009 + SpecAugment | 70.75 | 18.97 | 15.91 |
| MMS, full data + SpecAugment | 73.13 | 19.59 | 16.66 |
| Fadhma, full data | 74.48 | 22.73 | 19.85 |
| OmniASR, full data | 75.40 | 22.66 | 19.84 |

The external reference has the lowest WER; adapted MMS has the lowest CER. Unknown external training-data provenance limits interpretation. The supplementary Kabyle-XLS-R comparison is in [its result directory](results/kabyle_xlsr_zero_shot_and_adapted_final_evaluation/).

## Verify without a GPU

From the repository root, with Python 3:

```bash
python tools/verify_release.py
```

This uses only the Python standard library. It checks frozen hashes, split separation and corpus-level WER/CER from the saved predictions. It does not rerun ASR or regenerate bootstrap intervals.

## Layout

- `notebooks/`: selected preparation, training, evaluation and diagnostic notebooks.
- `data/metadata/`: authoritative frozen metadata and source inventories.
- `results/`: supplied experiment artifacts; original run-directory names retained.
- `model_metadata/`: supplied model/tokenizer/configuration records, **not weights**.
- `models/`: checkpoint access inventory.
- `tools/`: read-only evidence verification.
- `docs/`: experiment index, execution notes and audit findings.
- `archive/`: earlier notebooks, mutable corpus-preparation scripts, earlier metadata and source files.

Historical notebooks and corpus scripts document development; do not execute them against the frozen dataset. No new training, test-set tuning or result substitution was performed during repository organization.
