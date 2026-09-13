# Experiment index

All adaptation results use frozen V1.2 development data unless explicitly historical. Generic XLS-R was not tested on the final test set.

| Experiment | Notebook | Evidence |
|---|---|---|
| MMS full training; SpecAugment | [02_mms_full_specaugment](../notebooks/training/02_mms_full_specaugment.ipynb) | [Saved artifacts](../results/mms_1b_tarifit_v1_2_specaug/) |
| Training curves; uses recorded values embedded in plotting cells | [01_training_curves](../notebooks/analysis/01_training_curves.ipynb) | [Saved artifacts](../results/mms_1b_tarifit_v1_2_half_bible_specaug/) |
| OmniASR full training | [05_omniasr_full](../notebooks/training/05_omniasr_full.ipynb) | [Saved artifacts](../results/omniASR_w2v_300m_tarifit_v1_2/) |
| OmniASR half-SPK009 | [06_omniasr_half_spk009](../notebooks/training/06_omniasr_half_spk009.ipynb) | [Saved artifacts](../results/omniASR_w2v_300m_tarifit_v1_2_half_bible/) |
| Assisted transcription for manual review | [01_assisted_transcription](../notebooks/preparation/01_assisted_transcription.ipynb) | Notebook outputs (no separate complete result folder supplied) |
| Historical test-draft annotation aid; do not overwrite frozen references | [02_test_transcription_drafts](../notebooks/preparation/02_test_transcription_drafts.ipynb) | Notebook outputs (no separate complete result folder supplied) |
| MMS SpecAugment and speed perturbation | [03_mms_specaugment_speed](../notebooks/training/03_mms_specaugment_speed.ipynb) | [Saved artifacts](../results/mms_1b_tarifit_v1_2_specaug_speed/) |
| Historical decoder diagnostic; earlier 128-segment validation | [02_historical_kenlm](../notebooks/diagnostics/02_historical_kenlm.ipynb) | Notebook outputs (no separate complete result folder supplied) |
| Kabyle-XLS-R Tarifit adaptation | [10_kabyle_xlsr_full8_noaug](../notebooks/training/10_kabyle_xlsr_full8_noaug.ipynb) | [Saved artifacts](../results/kabyle_xlsr_tarifit_v1_2_noaug_full8_corrected/) |
| Main test comparison; Whisper; bootstrap; error analysis | [01_main_test_comparison](../notebooks/evaluation/01_main_test_comparison.ipynb) | [Saved artifacts](../results/final_test_v1_3/) |
| MMS full training; no augmentation | [01_mms_full_noaug](../notebooks/training/01_mms_full_noaug.ipynb) | [Saved artifacts](../results/mms_1b_tarifit_v1_2_noaug/) |
| MMS half-SPK009; SpecAugment | [04_mms_half_spk009](../notebooks/training/04_mms_half_spk009.ipynb) | [Saved artifacts](../results/mms_1b_tarifit_v1_2_half_bible_specaug/) |
| Kabyle-XLS-R zero-shot/adapted evaluation | [02_kabyle_xlsr_comparison](../notebooks/evaluation/02_kabyle_xlsr_comparison.ipynb) | [Saved artifacts](../results/kabyle_xlsr_zero_shot_and_adapted_final_evaluation/) |
| Generic XLS-R; eight epochs; no augmentation | [09_xlsr_full8_noaug](../notebooks/training/09_xlsr_full8_noaug.ipynb) | [Saved artifacts](../results/xlsr_300m_tarifit_v1_2_noaug_full8/) |
| Fadhma quarter-SPK009 | [08_fadhma_quarter_spk009](../notebooks/training/08_fadhma_quarter_spk009.ipynb) | [Saved artifacts](../results/fadhma_300m_tarifit_v1_2_quarter_bible/) |
| Generic XLS-R SpecAugment blank-collapse diagnostic | [01_xlsr_specaugment_blank_collapse](../notebooks/diagnostics/01_xlsr_specaugment_blank_collapse.ipynb) | Notebook outputs (no separate complete result folder supplied) |
| Fadhma full training | [07_fadhma_full](../notebooks/training/07_fadhma_full.ipynb) | [Saved artifacts](../results/fadhma_300m_tarifit_v1_2_transfer/) |

Fadhma quarter-SPK009: the completed notebook records checkpoint-252, but the supplied checkpoint metadata stops at step 126. Do not treat checkpoint-126 as the selected model.
