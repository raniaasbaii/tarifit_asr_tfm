# Model and audio access

## Model checkpoints

Links to five selected model exports are provided in
[checkpoint_access.csv](../models/checkpoint_access.csv).

All five model exports passed loading, tokenizer-compatibility and forward-pass
checks in Colab. The full-data MMS adapter required browser downloads and
manual upload after automated downloading failed. These checks did not rerun
recognition scores or establish equality to the historical checkpoint files.
See the [verification notebook](../notebooks/evaluation/Model_Download_Verification.ipynb).
The full-data MMS SpecAugment adapter requires the original MMS backbone
and its matching configuration and processor files.

For folders containing multiple checkpoints, use the checkpoint identified
in the access table and evaluation notebooks.

## Corpus audio

The corpus audio is not publicly redistributed. No permission was requested
or obtained from tarifit.info or the owners of the other recordings.
Source-specific redistribution terms have not yet been established.

A private package contains the 1,998 experimental audio segments and
their corresponding frozen references. The package remains restricted.

Source metadata and experimental split definitions are included in the
repository. A complete source-reconstruction workflow has not been verified.
Access arrangements for the examination panel remain to be discussed
with the supervisor.

## Remaining work

- Establish the applicable source terms before distributing audio.
- Review the terms for source-derived transcripts included in the metadata.
- Choose a licence for the author's code separately from third-party
  data and model licences.
