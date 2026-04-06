#!/usr/bin/env python3
"""
In silico pipeline for BITE review §§2–4: BioTransformer 3.0 (biotransformer.ca) + RDKit descriptors.

Outputs (under workflow_outputs/02_analysis/):
  - biotransformer_rutin_*.json   (raw API responses)
  - rutin_metabolites_descriptors.csv
  - rutin_insilico_manifest.json  (versions, seeds, SHA256 of inputs)

Does not claim environmental efficacy or infectivity. Hypothesis-generation only.

Usage:
  python scripts/rutin_insilico_sections_2_4.py

Requires: httpx, rdkit (see requirements-optional-insilico.txt).
"""
from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

# --- Reproducibility ---
RANDOM_SEED = 42  # reserved for any stochastic step; API is deterministic per SMILES
RUTIN_SMILES = (
    "CC1C(C(C(C(O1)OCC2C(C(C(C(O2)OC3=C(OC4=CC(=CC(=C4C3=O)O)O)C5=CC(=C(C=C5)O)O)O)O)O)O)O)O"
)
QUERCETIN_SMILES = "Oc1ccc(-c2oc3cc(O)cc(O)c3c(=O)c2O)cc1O"
BASE = "https://biotransformer.ca"
OUT_DIR = Path(__file__).resolve().parents[1] / "workflow_outputs" / "02_analysis"


def qid_from_post(r: httpx.Response) -> int | None:
    if r.status_code in (301, 302, 303, 307, 308):
        m = re.search(r"/queries/(\d+)", r.headers.get("location") or "")
        return int(m.group(1)) if m else None
    return None


async def submit_and_poll(
    client: httpx.AsyncClient,
    label: str,
    smiles: str,
    option: str,
    steps: int = 1,
    max_polls: int = 90,
    sleep_s: float = 4.0,
) -> dict:
    body = {
        "task_type": "PREDICTION",
        "biotransformer_option": option,
        "query_input": f"{label}\t{smiles}",
        "number_of_steps": steps,
    }
    r = await client.post("/queries.json", json=body)
    qid = qid_from_post(r)
    if qid is None:
        return {
            "error": "no_query_id",
            "status_code": r.status_code,
            "text": (r.text or "")[:800],
            "option": option,
        }
    async with httpx.AsyncClient(
        base_url=BASE, timeout=120.0, headers={"Accept": "application/json"}
    ) as gc:
        for _ in range(max_polls):
            await asyncio.sleep(sleep_s)
            gr = await gc.get(f"/queries/{qid}.json")
            if gr.status_code != 200:
                continue
            data = gr.json()
            st = (data.get("status") or "").strip().lower()
            if st in ("done", "failed", "error"):
                data["_poll_query_id"] = qid
                data["_option"] = option
                return data
    return {"error": "timeout", "_option": option, "_query_id": qid}


def collect_smiles_from_biotransformer(data: dict) -> list[tuple[str, str, str]]:
    """Return list of (smiles, reaction_type, product_title)."""
    out: list[tuple[str, str, str]] = []
    preds = data.get("predictions") or []
    if not isinstance(preds, list):
        return out
    for block in preds:
        bts = (block or {}).get("biotransformations") or []
        for bt in bts:
            rt = str(bt.get("reaction_type") or "")
            for p in bt.get("products") or []:
                sm = (p.get("smiles") or "").strip()
                tit = str(p.get("title") or "")
                if sm:
                    out.append((sm, rt, tit))
    return out


def rdkit_descriptors(smiles: str, name: str) -> dict | None:
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors, Lipinski
    except ImportError:
        return None
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return {"name": name, "smiles": smiles, "parse_error": True}
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
    }


async def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # BioTransformer jobs: rutin under environmental + human gut microbial (1 step each)
    jobs = [
        ("rutin_ENVMICRO_1", RUTIN_SMILES, "ENVMICRO", 1),
        ("rutin_HGUT_1", RUTIN_SMILES, "HGUT", 1),
        ("quercetin_ENVMICRO_1", QUERCETIN_SMILES, "ENVMICRO", 1),
    ]
    results: list[dict] = []
    async with httpx.AsyncClient(base_url=BASE, timeout=120.0, follow_redirects=False) as c:
        for label, smi, opt, st in jobs:
            print(f"Submitting {label} ...")
            data = await submit_and_poll(c, label, smi, opt, steps=st)
            results.append({"label": label, "response": data})
            path = OUT_DIR / f"biotransformer_{label}_{ts}.json"
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(f"  -> {path.name} status={(data.get('status') or data.get('error'))!r}")

    # Unique SMILES for descriptor table: parent + quercetin + all products
    seen: dict[str, str] = {}
    seen[RUTIN_SMILES] = "rutin_parent"
    seen[QUERCETIN_SMILES] = "quercetin_aglycone"
    for block in results:
        for sm, rt, tit in collect_smiles_from_biotransformer(block["response"]):
            key = sm
            if key not in seen:
                seen[key] = f"BT_{(tit or rt)[:40]}".replace(" ", "_")

    rows = []
    for smi, tag in seen.items():
        row = rdkit_descriptors(smi, tag)
        if row:
            rows.append(row)

    csv_path = OUT_DIR / "rutin_metabolites_descriptors.csv"
    if rows:
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
            "parse_error",
        ]
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in fields})

    manifest = {
        "generated_utc": ts,
        "random_seed": RANDOM_SEED,
        "rutin_smiles_sha256": hashlib.sha256(RUTIN_SMILES.encode()).hexdigest(),
        "python": sys.version.split()[0],
        "biotransformer_base": BASE,
        "outputs": [str(csv_path.name)] + [
            f"biotransformer_{j[0]}_{ts}.json" for j in jobs
        ],
    }
    try:
        import rdkit

        manifest["rdkit_version"] = getattr(rdkit, "__version__", "unknown")
    except ImportError:
        manifest["rdkit_version"] = "not_installed"

    (OUT_DIR / "rutin_insilico_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(f"Wrote {csv_path} ({len(rows)} structures)")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
