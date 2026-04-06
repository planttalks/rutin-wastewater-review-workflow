"""
Smoke tests for the rutin-wastewater-review-workflow.

Run with:  pytest tests/test_smoke.py -v
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _csv_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# 1. Species CSV integrity
# ---------------------------------------------------------------------------

def test_species_csv_exists():
    assert (ROOT / "data" / "species.csv").exists(), "data/species.csv missing"


def test_species_csv_has_rutin():
    rows = _csv_rows(ROOT / "data" / "species.csv")
    names = {r["name"] for r in rows}
    assert "rutin_parent" in names, "rutin_parent not in data/species.csv"


def test_species_csv_smiles_nonempty():
    rows = _csv_rows(ROOT / "data" / "species.csv")
    for row in rows:
        assert row["smiles"].strip(), f"Empty SMILES for {row['name']}"


# ---------------------------------------------------------------------------
# 2. RDKit descriptor script
# ---------------------------------------------------------------------------

rdkit = pytest.importorskip("rdkit", reason="rdkit not installed; skip descriptor tests")


def test_descriptor_script_runs(tmp_path, monkeypatch):
    """rutin_insilico_descriptors_core.main() writes CSV and manifest."""
    import rutin_insilico_descriptors_core as mod

    monkeypatch.setattr(mod, "OUT", tmp_path)
    rc = mod.main()
    assert rc == 0, "descriptor script returned non-zero"
    assert (tmp_path / "rutin_metabolites_descriptors.csv").exists()
    assert (tmp_path / "rutin_insilico_manifest.json").exists()


def test_descriptor_values_rutin(tmp_path, monkeypatch):
    """Check rutin MolLogP < 0 and TPSA > 200 (known from literature)."""
    import rutin_insilico_descriptors_core as mod

    monkeypatch.setattr(mod, "OUT", tmp_path)
    mod.main()
    rows = _csv_rows(tmp_path / "rutin_metabolites_descriptors.csv")
    rutin = next((r for r in rows if r["name"] == "rutin_parent"), None)
    assert rutin is not None, "rutin_parent row missing from output CSV"
    assert float(rutin["MolLogP"]) < 0, f"Expected rutin MolLogP < 0, got {rutin['MolLogP']}"
    assert float(rutin["TPSA"]) > 200, f"Expected rutin TPSA > 200, got {rutin['TPSA']}"


def test_descriptor_values_quercetin(tmp_path, monkeypatch):
    """Quercetin MolLogP > 0 and TPSA < 150 — polarity inversion vs rutin."""
    import rutin_insilico_descriptors_core as mod

    monkeypatch.setattr(mod, "OUT", tmp_path)
    mod.main()
    rows = _csv_rows(tmp_path / "rutin_metabolites_descriptors.csv")
    q = next((r for r in rows if "quercetin" in r["name"]), None)
    assert q is not None, "quercetin row missing from output CSV"
    assert float(q["MolLogP"]) > 0, f"Expected quercetin MolLogP > 0, got {q['MolLogP']}"
    assert float(q["TPSA"]) < 150, f"Expected quercetin TPSA < 150, got {q['TPSA']}"


def test_manifest_has_rdkit_version(tmp_path, monkeypatch):
    import rutin_insilico_descriptors_core as mod

    monkeypatch.setattr(mod, "OUT", tmp_path)
    mod.main()
    manifest = json.loads((tmp_path / "rutin_insilico_manifest.json").read_text())
    assert "rdkit_version" in manifest, "manifest missing rdkit_version"
    assert manifest["rdkit_version"], "rdkit_version is empty"


def test_all_smiles_parse():
    """Every SMILES in data/species.csv must parse cleanly with RDKit."""
    from rdkit import Chem

    rows = _csv_rows(ROOT / "data" / "species.csv")
    failures = []
    for row in rows:
        mol = Chem.MolFromSmiles(row["smiles"])
        if mol is None:
            failures.append(row["name"])
    assert not failures, f"RDKit failed to parse SMILES for: {failures}"


# ---------------------------------------------------------------------------
# 3. Docking output CSV integrity (if present — skip if not yet generated)
# ---------------------------------------------------------------------------

DOCKING_CSV = (
    ROOT
    / "workflow_outputs"
    / "02_analysis"
    / "docking"
    / "rutin_1MSC_multiligand"
    / "summary.csv"
)


@pytest.mark.skipif(not DOCKING_CSV.exists(), reason="docking summary.csv not generated yet")
def test_docking_csv_has_rutin_parent():
    rows = _csv_rows(DOCKING_CSV)
    slugs = {r["slug"] for r in rows}
    assert "rutin_parent" in slugs, "rutin_parent missing from docking summary"


@pytest.mark.skipif(not DOCKING_CSV.exists(), reason="docking summary.csv not generated yet")
def test_docking_rutin_affinity_range():
    """Rutin best affinity should be in the expected ~-4 to -8 kcal/mol range for 1MSC."""
    rows = _csv_rows(DOCKING_CSV)
    rutin = next((r for r in rows if r["slug"] == "rutin_parent"), None)
    if rutin and rutin["best_affinity_kcal_mol"]:
        aff = float(rutin["best_affinity_kcal_mol"])
        assert -10 < aff < -3, f"Rutin affinity {aff} outside expected -10 to -3 kcal/mol"


@pytest.mark.skipif(not DOCKING_CSV.exists(), reason="docking summary.csv not generated yet")
def test_docking_all_ligands_present():
    expected = {
        "rutin_parent", "quercetin", "BT_env_disaccharide", "BT_env_scaffold_286",
        "BT_Q_epimer", "BT_Q_benzopyran", "BT_Q_dicarboxy", "BT_Q_aldehyde_acid",
        "protocatechuic",
    }
    rows = _csv_rows(DOCKING_CSV)
    found = {r["slug"] for r in rows}
    missing = expected - found
    assert not missing, f"Missing ligands in docking summary: {missing}"
