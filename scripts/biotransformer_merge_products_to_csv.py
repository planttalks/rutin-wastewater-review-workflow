#!/usr/bin/env python3
"""
Parse BioTransformer JSON (status Done), merge product SMILES into descriptor CSV.
Skips fragments with MolWt < 120 (e.g. formate). Skips RDKit parse failures.

Usage:
  python scripts/biotransformer_merge_products_to_csv.py workflow_outputs/02_analysis/biotransformer_quercetin_ENVMICRO_1_20260318T062331Z.json
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "workflow_outputs" / "02_analysis" / "rutin_metabolites_descriptors.csv"
MIN_MW = 120.0


def products_from_json(data: dict) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for pred in data.get("predictions") or []:
        for bt in pred.get("biotransformations") or []:
            rt = str(bt.get("reaction_type") or "rxn")[:50]
            for p in bt.get("products") or []:
                sm = (p.get("smiles") or "").strip()
                tit = (p.get("title") or rt).replace(",", ";")[:60]
                if sm:
                    out.append((sm, tit))
    return out


def row_for_smiles(smiles: str, name: str) -> dict | None:
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
        "note": f"BioTransformer ENVMICRO product (quercetin substrate); {name}",
        "error": "",
    }


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "workflow_outputs/02_analysis/biotransformer_quercetin_ENVMICRO_1_20260318T062331Z.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if (data.get("status") or "").lower() != "done":
        print("JSON status is not Done:", data.get("status"), file=sys.stderr)
        return 1

    seen_can = set()
    existing = CSV_PATH.read_text(encoding="utf-8") if CSV_PATH.exists() else ""
    for line in existing.splitlines()[1:]:
        if line:
            seen_can.add(line.split(",")[1] if "," in line else "")

    new_rows = []
    for i, (sm, tit) in enumerate(products_from_json(data)):
        r = row_for_smiles(sm, f"BT_ENVMICRO_Q_{i+1}_{tit[:20]}")
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
        for r in new_rows:
            w.writerow({k: r.get(k, "") for k in fields})

    meta = ROOT / "workflow_outputs/02_analysis" / "biotransformer_merge_log.txt"
    meta.write_text(
        f"source_json={path.name}\nmerged_rows={len(new_rows)}\n", encoding="utf-8"
    )
    print(f"Appended {len(new_rows)} rows to {CSV_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
