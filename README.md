# Rutin Wastewater Review Workflow

Reproducible scripts and supplementary outputs for a critical mini-review on rutin at the water-plant-virus interface in nature-based wastewater treatment.

## Scope

This repository snapshot supports the manuscript's computational and supplementary components (S1-S4), including:

- descriptor calculation (RDKit),
- BioTransformer product retrieval/merge,
- docking preparation and multi-ligand docking workflow (AutoDock Vina context),
- supplementary tables and reproducibility metadata.

No primary wet-lab datasets are included.

## Repository contents

- `Supplementary.md` - Supplementary Information (S1-S4).
- `requirements-optional-insilico.txt` - optional Python dependency notes.
- `scripts/rutin_insilico_descriptors_core.py` - descriptor workflow.
- `scripts/rutin_vina_docking_prep.py` - docking input preparation.
- `scripts/rutin_multiligand_vina_1MSC.py` - multi-ligand docking workflow.
- `scripts/biotransformer_fetch_rutin.py` - BioTransformer fetch helper.
- `scripts/biotransformer_merge_jar_csv_to_descriptors.py` - merge helper for descriptor-ready outputs.
- `scripts/biotransformer_merge_products_to_csv.py` - merge helper for product outputs.

## Quick start

1. Create a Python environment and install dependencies listed in `requirements-optional-insilico.txt`.
2. Run scripts from `scripts/` in the order required by your workflow:
   - descriptors,
   - BioTransformer retrieval/merge,
   - docking preparation,
   - docking execution.
3. Match outputs to table definitions in `Supplementary.md`.

## Reproducibility notes

- Computational settings referenced in `Supplementary.md` Table S1.
- Descriptor summary values are in Table S2.
- BioTransformer product summaries are in Table S3.
- Docking result summaries are in Table S4.

## Citation

If you use this repository, please cite:

- the associated manuscript, and
- the repository DOI (to be minted on Zenodo release).

## License

License to be added by authors before archival release.
