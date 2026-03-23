#!/usr/bin/env python3
"""
Append BioTransformer 3.0 JAR CSV outputs to rutin_metabolites_descriptors.csv.
Reads SMILES from JAR export columns; dedupes by canonical SMILES vs existing CSV.

Usage (manuscript scope = environmental microbial only):
  python scripts/biotransformer_merge_jar_csv_to_descriptors.py

Optional second CSV for other biosystems (not used in BITE draft):
  python scripts/biotransformer_merge_jar_csv_to_descriptors.py \\
    workflow_outputs/02_analysis/rutin_local_ENVMICRO_1.csv \\
    <other_biotransformer_export.csv>
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "workflow_outputs" / "02_analysis" / "rutin_metabolites_descriptors.csv"
MIN_MW = 120.0


def row_for_smiles(smiles: str, name: str, note: str) -> dict | None:
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return None
    mw = Descriptors.MolWt(m)
    if mw < MIN_MW:
        return None
    can = Chem.MolToSmiles(m)
    return {
        "name": name,
        "smiles": can,
        "MolWt": round(mw, 3),
        "MolLogP": round(Descriptors.MolLogP(m), 3),
        "TPSA": round(Descriptors.TPSA(m), 3),
        "HBD": Lipinski.NumHDonors(m),
        "HBA": Lipinski.NumHAcceptors(m),
        "NumRotatableBonds": Lipinski.NumRotatableBonds(m),
        "FractionCSP3": round(Lipinski.FractionCSP3(m), 4),
        "note": note,
        "error": "",
    }


def iter_jar_rows(path: Path, biosystem_tag: str) -> list[tuple[str, str, str]]:
    """Return (raw_smiles, short_name, note)."""
    out: list[tuple[str, str, str]] = []
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            sm = (row.get("SMILES") or "").strip()
            if not sm:
                continue
            mid = (row.get("Metabolite ID") or "BT").strip()
            rxn = (row.get("Reaction") or "")[:40].replace(",", ";")
            note = f"BioTransformer 3.0 environmental microbial; rutin; {rxn}" if biosystem_tag == "env" else f"BioTransformer3.0 JAR {biosystem_tag}; {rxn}"
            prefix = f"BT_env_rutin_{mid}" if biosystem_tag == "env" else f"BT_JAR_{biosystem_tag}_{mid}"
            out.append((sm, prefix, note))
    return out


def main() -> int:
    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        paths = [ROOT / "workflow_outputs/02_analysis/rutin_local_ENVMICRO_1.csv"]
    tag_by_stem = {
        "rutin_local_ENVMICRO_1": "env",
        "rutin_local_HGUT_1": "hgut",
    }

    seen_can: set[str] = set()
    if CSV_PATH.exists():
        with CSV_PATH.open(encoding="utf-8") as f:
            rd = csv.DictReader(f)
            for line in rd:
                seen_can.add((line.get("smiles") or "").strip())

    new_rows: list[dict] = []
    for p in paths:
        if not p.exists():
            print("skip missing:", p, file=sys.stderr)
            continue
        tag = tag_by_stem.get(p.stem, p.stem)
        for sm, nm, note in iter_jar_rows(p, tag):
            r = row_for_smiles(sm, nm, note)
            if r and r["smiles"] not in seen_can:
                seen_can.add(r["smiles"])
                new_rows.append(r)

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
    with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        for row in new_rows:
            w.writerow({k: row.get(k, "") for k in fields})

    log = ROOT / "workflow_outputs/02_analysis/biotransformer_jar_merge_log.txt"
    log.write_text(
        "sources=" + ",".join(str(x.name) for x in paths if x.exists()) + f"\nappended_rows={len(new_rows)}\n",
        encoding="utf-8",
    )
    print(f"Appended {len(new_rows)} rows to {CSV_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
