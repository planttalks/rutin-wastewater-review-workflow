# Rutin Wastewater Review Workflow — ordered pipeline
# Usage: make [target]
#
# Prerequisites:
#   conda env create -f environment.yml && conda activate rutin-review
#   obabel on PATH (or OBABEL_EXE set)
#   vina on PATH  (or VINA_EXE set; or scripts/vina_1.2.7_win.exe present)

PYTHON   ?= python
PYTEST   ?= pytest
OUT      := workflow_outputs/02_analysis

.PHONY: all descriptors docking-prep docking-multi test clean help

# ── Default target ──────────────────────────────────────────────────────────
all: descriptors docking-prep docking-multi
	@echo "Pipeline complete. Outputs in $(OUT)/"

# ── Step 1: Molecular descriptors ───────────────────────────────────────────
descriptors: $(OUT)/rutin_metabolites_descriptors.csv

$(OUT)/rutin_metabolites_descriptors.csv: scripts/rutin_insilico_descriptors_core.py data/species.csv
	$(PYTHON) scripts/rutin_insilico_descriptors_core.py
	@echo "[1/3] Descriptors written."

# ── Step 2: Docking prep (receptor + rutin ligand PDBQT) ────────────────────
docking-prep: $(OUT)/docking/rutin_1MSC/vina_config.txt

$(OUT)/docking/rutin_1MSC/vina_config.txt: scripts/rutin_vina_docking_prep.py
	$(PYTHON) scripts/rutin_vina_docking_prep.py
	@echo "[2/3] Docking prep complete."

# ── Step 3: Multi-ligand docking ────────────────────────────────────────────
docking-multi: $(OUT)/docking/rutin_1MSC_multiligand/summary.csv

$(OUT)/docking/rutin_1MSC_multiligand/summary.csv: scripts/rutin_multiligand_vina_1MSC.py \
    $(OUT)/docking/rutin_1MSC/vina_config.txt
	$(PYTHON) scripts/rutin_multiligand_vina_1MSC.py
	@echo "[3/3] Multi-ligand docking complete."

# ── BioTransformer fetch (optional; requires network) ───────────────────────
biotransformer:
	$(PYTHON) scripts/biotransformer_fetch_rutin.py
	@echo "BioTransformer fetch done."

# ── Tests ────────────────────────────────────────────────────────────────────
test:
	$(PYTEST) tests/test_smoke.py -v --tb=short

# ── Clean generated outputs (not committed files) ────────────────────────────
clean:
	rm -rf $(OUT)/rutin_metabolites_descriptors.csv \
	       $(OUT)/rutin_insilico_manifest.json \
	       $(OUT)/docking/rutin_1MSC/receptor.pdbqt \
	       $(OUT)/docking/rutin_1MSC/ligand.pdbqt \
	       $(OUT)/docking/rutin_1MSC/vina_config.txt \
	       $(OUT)/docking/rutin_1MSC_multiligand/summary.csv
	@echo "Cleaned generated outputs."

# ── Help ─────────────────────────────────────────────────────────────────────
help:
	@echo "Targets:"
	@echo "  all            Run descriptors + docking-prep + docking-multi"
	@echo "  descriptors    Step 1: RDKit descriptors (data/species.csv -> CSV)"
	@echo "  docking-prep   Step 2: Prepare 1MSC receptor + rutin PDBQT"
	@echo "  docking-multi  Step 3: Multi-ligand Vina vs 1MSC"
	@echo "  biotransformer Optional: fetch BioTransformer products via API"
	@echo "  test           Run pytest smoke tests"
	@echo "  clean          Remove generated output files"
