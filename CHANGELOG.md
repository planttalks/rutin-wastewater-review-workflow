# Changelog

All notable changes to this workflow repository are documented here.
Follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) conventions.

---

## [Unreleased]

### Added
- `LICENSE` (MIT) — required for FAIR compliance and Zenodo archival.
- `CITATION.cff` — machine-readable citation in Citation File Format 1.2.
- `environment.yml` — conda environment for cross-platform reproducibility (conda-forge RDKit).
- `requirements.txt` — pip-installable dependencies with `pytest` for CI.
- `data/species.csv` — canonical SMILES source replacing hardcoded strings in scripts.
- `tests/test_smoke.py` — pytest smoke tests: descriptor values, SMILES parsing, docking CSV.
- `tests/__init__.py`
- `.github/workflows/ci.yml` — four-job CI: descriptor tests (Python 3.10/3.11), ruff lint,
  SMILES validation, and repo hygiene checks.
- `Makefile` — ordered workflow orchestration (`make all`, `make test`, `make clean`).
- `CHANGELOG.md` — this file.

### Changed
- `requirements-optional-insilico.txt` retained but superseded by `requirements.txt`
  and `environment.yml`; label updated to reflect that `pandas` is now listed.

### Fixed
- Identified duplicate SMILES strings in `rutin_vina_docking_prep.py` and
  `rutin_insilico_descriptors_core.py` (both hardcode `RUTIN_SMILES`); tracked in
  `data/species.csv` as canonical source. Migration to single-source not yet complete —
  future PR should update scripts to read from `data/species.csv`.
- Hardcoded Windows Open Babel path `C:\Program Files\OpenBabel-2.4.1\obabel.EXE`
  documented in `environment.yml` with cross-platform `OBABEL_EXE` guidance.

---

## [0.1.0] — 2026-01-01 (initial repository snapshot)

### Added
- `Supplementary.md` (Tables S1–S4).
- `requirements-optional-insilico.txt` (rdkit, httpx, numpy, scipy).
- `scripts/rutin_insilico_descriptors_core.py` — RDKit descriptor table.
- `scripts/rutin_vina_docking_prep.py` — 1MSC receptor + rutin ligand prep.
- `scripts/rutin_multiligand_vina_1MSC.py` — multi-ligand docking workflow.
- `scripts/biotransformer_fetch_rutin.py` — BioTransformer API helper.
- `scripts/biotransformer_merge_jar_csv_to_descriptors.py`
- `scripts/biotransformer_merge_products_to_csv.py`
- `README.md` (initial).
