# Model and audio access

The supplied package contains notebooks, references, source metadata, saved predictions and model/tokenizer configuration records. It does not contain trained weights or audio. Public download links have not yet been supplied or verified.

## Before submission

- Add downloadable selected-checkpoint locations in `models/checkpoint_access.csv`. Include weights, matching tokenizer/processor files, configuration, and the base checkpoint identifier. MMS adapter exports also require their exact base model and adapter/head loading procedure.
- Verify a fresh download loads and matches the recorded checkpoint. A directory containing only config/tokenizer files is insufficient.
- Supply a permitted audio package or a documented source-reconstruction route with source URLs, segment timestamps, sample rate, stable IDs and reference transcripts. Inspect source inventory completeness; URLs may no longer resolve and reconstruction has not been tested here.
- Document the access route for the panel if public redistribution is unavailable.
- Choose/document a licence for the author's code and identify applicable terms for each data/model source. No blanket licence is assigned to third-party recordings by this package.

Large assets should be hosted separately and linked here rather than committed as ordinary GitHub files. The original Drive paths in JSON/CSV artifacts record provenance; they are not public download links.
