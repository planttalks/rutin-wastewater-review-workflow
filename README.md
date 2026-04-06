# Computational Workflow for Mechanistic Prior Generation: Rutin at the Water-Plant-Virus Interface

[![CI](https://github.com/planttalks/rutin-wastewater-review-workflow/actions/workflows/ci.yml/badge.svg)](https://github.com/planttalks/rutin-wastewater-review-workflow/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CITATION](https://img.shields.io/badge/cite-CITATION.cff-blue)](CITATION.cff)

Reproducible computational scripts and supplementary outputs supporting a critical mini-review on rutin at the water-plant-virus interface in nature-based wastewater treatment. The integration of computational tools within the EPEA framework is intended to provide mechanistic priors, identify metabolic pathways, and quantify ligand-binding potentials that are otherwise absent from the literature. This computational layer is designed to guide future empirical LC-MS/MS and infectivity-based confirmation rather than to replace the validation of active species in complex matrices.

> **Scope:** All outputs are hypothesis-generating only and support evidence synthesis for manuscript sections 2-4 and Supplementary Information (S1-S4). They do not predict treatment performance or substitute for infectivity assays in complex environmental matrices.

---

## EPEA Framework

The review organises evidence and computational outputs around the **EPEA (Evidence-based Phytochemical Environmental Assessment)** four-barrier model:

| Barrier | Description | Workflow connection |
|---------|-------------|---------------------|
| **B1** Sorption and filtration | Virus retention at biofilms, organic matter, roots | Descriptor polarity gradient (Table S2) |
| **B2** Rhizosphere-mediated attenuation | Dissolved rutin / metabolites acting on retained virions | BioTransformer products (Table S3) |
| **B3** Plant internalisation | Virus and rutin co-localisation in tissues | Species pool for future assay design |
| **B4** Intracellular transformation | Metabolism shifts active species | Docking screen: parent vs. products (Table S4) |

Computational outputs (descriptors -> metabolites -> docking affinities) are mapped to B1-B4 to identify which species and compartments should be prioritised in bench-scale experiments. They do **not** predict log-reduction or replace infectivity assays.

---

## Repository layout

```
.
+-- data/
|   +-- species.csv                  # Canonical SMILES source for all ligands
+-- scripts/
|   +-- rutin_insilico_descriptors_core.py   # Step 1: RDKit descriptors
|   +-- rutin_vina_docking_prep.py           # Step 2: Receptor + rutin PDBQT prep
|   +-- rutin_multiligand_vina_1MSC.py       # Step 3: Multi-ligand docking
|   +-- biotransformer_fetch_rutin.py        # Optional: BioTransformer API
|   +-- biotransformer_merge_*.py            # Optional: merge BT outputs
|   +-- README-docking-tools.md             # Vina / Qvina / obabel install notes
+-- tests/
|   +-- test_smoke.py                # pytest: descriptors, SMILES, docking CSV
+-- workflow_outputs/
|   +-- 02_analysis/                 # Generated outputs (not re-committed after release)
+-- Supplementary.md                 # Tables S1-S4
+-- environment.yml                  # Conda environment (recommended)
+-- requirements.txt                 # pip fallback + pytest
+-- Makefile                         # Ordered pipeline (make all / make test)
+-- CITATION.cff                     # Machine-readable citation
+-- CHANGELOG.md
+-- LICENSE
```

---

## Quick start

### 1 - Install dependencies

**Recommended (conda, cross-platform RDKit):**

```bash
conda env create -f environment.yml
conda activate rutin-review
```

**pip fallback:**

```bash
pip install -r requirements.txt
```

> RDKit via pip can be unreliable on some platforms. If `from rdkit import Chem` fails, use the conda route.

### 2 - Install external tools

| Tool | Version | Install |
|------|---------|---------|
| [Open Babel](https://openbabel.org) | >=3.1.1 | `conda install -c conda-forge openbabel` or download installer |
| [AutoDock Vina](https://github.com/ccsb-scripps/AutoDock-Vina/releases) | 1.2.7 | Place binary on PATH **or** drop `vina_1.2.7_win.exe` in `scripts/` |

Set `OBABEL_EXE` / `VINA_EXE` environment variables if the tools are not on `PATH`. See `scripts/README-docking-tools.md` for QuickVina2 and Qvina-W alternatives.

### 3 - Run the pipeline

```bash
# Run all three steps in order
make all

# Or step by step
make descriptors    # Step 1: RDKit descriptors
make docking-prep   # Step 2: 1MSC receptor + rutin ligand
make docking-multi  # Step 3: Multi-ligand Vina vs 1MSC

# Optional: fetch BioTransformer products (requires network + httpx)
make biotransformer
```

### 4 - Run tests

```bash
make test
# or
pytest tests/test_smoke.py -v
```

---

## Output files and manuscript table mapping

| Output | Location | Table |
|--------|----------|-------|
| Computational parameters | `Supplementary.md` Table S1 | S1 |
| Molecular descriptors CSV | `workflow_outputs/02_analysis/rutin_metabolites_descriptors.csv` | S2 |
| BioTransformer products | `workflow_outputs/02_analysis/*.json` + `*.csv` | S3 |
| Docking summary | `workflow_outputs/02_analysis/docking/rutin_1MSC_multiligand/summary.csv` | S4 |
| Run provenance | `workflow_outputs/02_analysis/rutin_insilico_manifest.json` | S1 |

---

## Reproducibility notes

- All software versions are logged in `rutin_insilico_manifest.json` at runtime (Python version, RDKit version, UTC timestamp).
- Docking uses `exhaustiveness=8` (Vina default) on a blind whole-protomer box; affinity values are **not** site-matched to Zure et al. 2024 [6,7]. See `Supplementary.md` Table S1.
- BioTransformer was run in **ENVMICRO single-step** mode. Cached JSON outputs in `workflow_outputs/02_analysis/` are the archival record; re-running the API may return slightly different results as the server is updated.
- SMILES strings are defined once in `data/species.csv` (canonical source). Scripts embed copies for standalone use; a future refactor should read from this CSV.

---

## Citation

Please cite both the manuscript and this repository:

```bibtex
@article{zure2026rutin,
  title   = {Rutin at the Water--Plant--Virus Interface: A Critical Mini-Review
             for Nature-Based Wastewater Treatment},
  author  = {Zure, Diaiti and Rahim, Abdul and Kuo, Hsion-Wen David},
  journal = {Bioresource Technology},
  publisher = {Elsevier},
  year    = {2026},
  note    = {Submitted; currently with editor (March 2026)}
}
```

See `CITATION.cff` for the machine-readable form (GitHub will render a "Cite this repository" button automatically).

---

## License

MIT - see [LICENSE](LICENSE).
