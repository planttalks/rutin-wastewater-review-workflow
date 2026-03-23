#!/usr/bin/env python3
"""
Core RDKit descriptor table for rutin + literature-aligned species (§§2–4).
Independent of BioTransformer completion; re-run after BT job finishes to merge.

Outputs:
  workflow_outputs/02_analysis/rutin_metabolites_descriptors.csv
  workflow_outputs/02_analysis/rutin_insilico_manifest.json (partial update)
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "workflow_outputs" / "02_analysis"

# (name, smiles, note for manuscript)
SPECIES = [
    (
        "rutin_parent",
        "CC1C(C(C(C(O1)OCC2C(C(C(C(O2)OC3=C(OC4=CC(=CC(=C4C3=O)O)O)C5=CC(=C(C=C5)O)O)O)O)O)O)O)O",
        "Parent glycoside; phage docking studies [7].",
    ),
    (
        "quercetin_aglycone",
        "Oc1ccc(-c2oc3cc(O)cc(O)c3c(=O)c2O)cc1O",
        "Dominant first-step deglycosylation product (rhizosphere/gut microbes).",
    ),
    (
        "isorhamnetin",
        "COc1ccc(-c2oc3cc(O)cc(O)c3c(=O)c2O)cc1O",
        "Illustrative O-methylated flavonol (phase-II / microbial methylation class).",
    ),
    (
        "taxifolin",
        "O=C1c2c(O)cc(O)cc2OC(c2ccc(O)c(O)c2)C1O",
        "Dihydroflavonol; illustrative ring-reduced transformation class.",
    ),
    (
        "protocatechuic_acid",
        "Oc1ccc(C(=O)O)cc1O",
        "Illustrative small phenolic from flavonoid ring cleavage pathways.",
    ),
]


def desc(smiles: str, name: str) -> dict:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Lipinski

    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return {"name": name, "smiles": smiles, "note": "", "error": "parse_failed"}
    return {
        "name": name,
        "smiles": smiles,
        "MolWt": round(Descriptors.MolWt(m), 3),
        "MolLogP": round(Descriptors.MolLogP(m), 3),
        "TPSA": round(Descriptors.TPSA(m), 3),
        "HBD": Lipinski.NumHDonors(m),
        "HBA": Lipinski.NumHAcceptors(m),
        "NumRotatableBonds": Lipinski.NumRotatableBonds(m),
        "FractionCSP3": round(Lipinski.FractionCSP3(m), 4),
        "note": "",
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, smi, note in SPECIES:
        r = desc(smi, name)
        r["note"] = note
        rows.append(r)

    csv_path = OUT / "rutin_metabolites_descriptors.csv"
    fields = [
        "name",
        "smiles",
        "MolWt",
        "MolLogP",
        "TPSA",
        "HBD",
        "HBA",
        "NumRotatableBonds",
        "FractionCSP3",
        "note",
        "error",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})

    man = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "script": "rutin_insilico_descriptors_core.py",
        "rdkit_version": __import__("rdkit").__version__,
        "python": sys.version.split()[0],
        "outputs": [str(csv_path.name)],
        "biotransformer_note": (
            "Optional: merge ENVMICRO/HGUT products via scripts/rutin_insilico_sections_2_4.py "
            "or GET https://biotransformer.ca/queries/<id>.json when status=Done."
        ),
    }
    (OUT / "rutin_insilico_manifest.json").write_text(
        json.dumps(man, indent=2), encoding="utf-8"
    )
    print(csv_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
