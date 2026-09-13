# Updating GitHub

This package has not been pushed. Review README.md, AUDIT_NOTES.md and RESOURCE_ACCESS.md first.

1. Keep a backup of the existing repository and work in a new branch.
2. Copy this package's contents into that checkout. Review obsolete files already present in the old checkout; copying alone does not remove them.
3. Run `python tools/verify_release.py` and review `git diff --stat` and the changed files.
4. Add checkpoint/audio access information and decide the code licence.
5. Commit, push the branch and inspect the rendered notebooks/README on GitHub before merging.
6. Tag the submission version and record the commit identifier in the report or supplementary material.

The package retains original experiment records with machine-specific paths. Do not advertise full training reproducibility until model/audio access and runtime execution have been checked.
