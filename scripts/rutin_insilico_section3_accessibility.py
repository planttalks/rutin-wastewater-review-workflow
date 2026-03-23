#!/usr/bin/env python3
"""
§3 support: RDKit descriptors for rutin vs quercetin — coarse ligand-property contrast
(virion-accessible aqueous interaction vs smaller aglycone / metabolites).

Output: workflow_outputs/02_analysis/rutin_section3_ligand_accessibility.md
"""
from __future__ import annotations

from pathlib import Path

RUTIN_SMILES = (
    "CC1C(C(C(C(O1)OCC2C(C(C(C(O2)OC3=C(OC4=CC(=CC(=C4C3=O)O)O)C5=CC(=C(C=C5)O)O)O)O)O)O)O)O"
)
QUERCETIN_SMILES = "Oc1ccc(-c2oc3cc(O)cc(O)c3c(=O)c2O)cc1O"


def rdkit_descriptors(smiles: str, name: str) -> dict | None:
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors, Lipinski
    except ImportError:
        return None
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return {"name": name, "parse_error": True}
    return {
        "name": name,
        "MolWt": round(Descriptors.MolWt(m), 3),
        "MolLogP": round(Descriptors.MolLogP(m), 3),
        "TPSA": round(Descriptors.TPSA(m), 3),
        "HBD": Lipinski.NumHDonors(m),
        "HBA": Lipinski.NumHAcceptors(m),
        "NumRotatableBonds": Lipinski.NumRotatableBonds(m),
    }

OUT = Path(__file__).resolve().parents[1] / "workflow_outputs" / "02_analysis"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    r = rdkit_descriptors(RUTIN_SMILES, "rutin")
    q = rdkit_descriptors(QUERCETIN_SMILES, "quercetin")
    lines = [
        "# §3 Ligand-property contrast (hypothesis only; not docking)",
        "",
        "| Species | MolWt | MolLogP | TPSA | HBD | HBA | RotBonds |",
        "|---------|-------|---------|------|-----|-----|----------|",
    ]
    for row in (r, q):
        if not row or row.get("parse_error"):
            continue
        lines.append(
            f"| {row['name']} | {row['MolWt']} | {row['MolLogP']} | {row['TPSA']} | "
            f"{row['HBD']} | {row['HBA']} | {row['NumRotatableBonds']} |"
        )
    lines += [
        "",
        "**Interpretation (caveated):** Larger MW and TPSA for rutin are consistent with dominant "
        "aqueous-phase, polar surface exposure relevant to **virion coat** encounters; quercetin is "
        "smaller and more lipophilic (higher LogP), which may alter partitioning and intracellular "
        "exposure but does **not** imply superior virion inactivation. Published docking to capsid "
        "proteins used parent rutin [7].",
        "",
    ]
    (OUT / "rutin_section3_ligand_accessibility.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print((OUT / "rutin_section3_ligand_accessibility.md"))


if __name__ == "__main__":
    main()
