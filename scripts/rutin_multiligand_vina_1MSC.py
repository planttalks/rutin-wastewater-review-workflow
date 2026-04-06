#!/usr/bin/env python3
"""
Multi-ligand AutoDock Vina vs MS2 coat 1MSC -- same search box as rutin_vina_docking_prep.py.

Writes workflow_outputs/02_analysis/docking/rutin_1MSC_multiligand/
  summary.csv, vina_multiligand_summary.md, per-ligand logs.

Hypothesis-level only; blind whole-protein box -- not comparable to site-targeted [7].
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "workflow_outputs/02_analysis/docking/rutin_1MSC"
OUT = ROOT / "workflow_outputs/02_analysis/docking/rutin_1MSC_multiligand"

# Import prep helpers from sibling script
sys.path.insert(0, str(ROOT / "scripts"))
from rutin_vina_docking_prep import (  # noqa: E402
    docking_executable,
    ligand_pdbqt_valid,
    prepare_ligand_pdbqt,
)
from rutin_vina_docking_prep import ROOT as _R  # noqa: E402

assert _R == ROOT

# slug, label_for_table, smiles (neutral forms for charged BT products where needed)
LIGANDS: list[tuple[str, str, str | None]] = [
    # SMILES None → reuse ligand.pdbqt from rutin_1MSC (same embed as single-ligand run)
    ("rutin_parent", "Rutin (parent glycoside)", None),
    (
        "quercetin",
        "Quercetin (aglycone)",
        "Oc1ccc(-c2oc3cc(O)cc(O)c3c(=O)c2O)cc1O",
    ),
    (
        "BT_env_disaccharide",
        "ENVMICRO rutin → disaccharide fragment (~326 Da)",
        "CC1OC(OCC2OC(O)C(O)C(O)C2O)C(O)C(O)C1O",
    ),
    (
        "BT_env_scaffold_286",
        "ENVMICRO rutin → C15H10O6 scaffold (~286 Da)",
        "O=c1cc(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12",
    ),
    (
        "BT_Q_epimer",
        "ENVMICRO quercetin → epimerization product",
        "O=C1C=CC(c2oc3cc(O)cc(O)c3c(=O)c2O)=CC1O",
    ),
    (
        "BT_Q_benzopyran",
        "ENVMICRO quercetin → benzopyran-dione isomer",
        "O=C1C(=O)C(c2ccc(O)c(O)c2)Oc2cc(O)cc(O)c21",
    ),
    (
        "BT_Q_dicarboxy",
        "ENVMICRO quercetin → dicarboxylic derivative",
        "O=C(O)C=CC(=CC(=O)O)c1oc2cc(O)cc(O)c2c(=O)c1O",
    ),
    (
        "BT_Q_aldehyde_acid",
        "ENVMICRO quercetin → aldehyde–acid (neutral acid form)",
        "O=CC(=CC=C(O)C(=O)O)c1oc2cc(O)cc(O)c2c(=O)c1O",
    ),
    (
        "protocatechuic",
        "Illustrative ring-cleavage phenolic (small)",
        "Oc1ccc(C(=O)O)cc1O",
    ),
]


def best_affinity_from_vina_stdout(text: str) -> float | None:
    for line in text.splitlines():
        m = re.match(r"^\s+1\s+(-?\d+\.\d+)", line)
        if m:
            return float(m.group(1))
    return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rec = BASE / "receptor.pdbqt"
    cfg_src = BASE / "vina_config.txt"
    pdb = BASE / "1MSC.pdb"
    if not rec.exists() or not cfg_src.exists():
        print("Run first: python scripts/rutin_vina_docking_prep.py", file=sys.stderr)
        return 1

    dock_exe = docking_executable()
    if not dock_exe:
        print("No Vina executable; install or set VINA_EXE", file=sys.stderr)
        return 1

    # Parse box from existing config
    center = {}
    size = {}
    for line in cfg_src.read_text().splitlines():
        line = line.strip()
        if line.startswith("center_"):
            k, v = line.split("=", 1)
            center[k.strip()] = float(v.strip())
        if line.startswith("size_"):
            k, v = line.split("=", 1)
            size[k.strip()] = float(v.strip())

    rows: list[dict] = []
    ts = datetime.now(timezone.utc).isoformat()

    for slug, label, smi in LIGANDS:
        lig_pdbqt = OUT / f"{slug}.pdbqt"
        lig_out = OUT / f"{slug}_out.pdbqt"
        log_f = OUT / f"{slug}_vina.log"
        if smi is None and slug == "rutin_parent":
            src = BASE / "ligand.pdbqt"
            if src.exists() and ligand_pdbqt_valid(src):
                shutil.copy(src, lig_pdbqt)
                ok, how = True, "copy_from_rutin_1MSC"
            else:
                ok, how = False, "missing_BASE_ligand.pdbqt_run_rutin_vina_docking_prep_first"
        else:
            ok, how = prepare_ligand_pdbqt(str(smi), lig_pdbqt, OUT)
        row: dict = {
            "slug": slug,
            "label": label,
            "prep_ok": ok,
            "prep_method": how if ok else how[:200],
            "best_affinity_kcal_mol": "",
            "notes": "",
        }
        if not ok:
            row["notes"] = "ligand_prep_failed"
            rows.append(row)
            continue

        cfg_lines = [
            f"receptor = {rec.resolve()}",
            f"ligand = {lig_pdbqt.resolve()}",
            f"out = {lig_out.resolve()}",
            f"center_x = {center['center_x']:.3f}",
            f"center_y = {center['center_y']:.3f}",
            f"center_z = {center['center_z']:.3f}",
            f"size_x = {size['size_x']:.3f}",
            f"size_y = {size['size_y']:.3f}",
            f"size_z = {size['size_z']:.3f}",
            "exhaustiveness = 8",
            "num_modes = 9",
            "energy_range = 4",
        ]
        cfg_path = OUT / f"{slug}_vina_config.txt"
        cfg_path.write_text("\n".join(cfg_lines) + "\n", encoding="utf-8")

        vr = subprocess.run(
            [dock_exe, "--config", str(cfg_path)],
            cwd=str(OUT),
            capture_output=True,
            text=True,
            timeout=600,
        )
        log_f.write_text((vr.stdout or "") + "\n---\n" + (vr.stderr or ""), encoding="utf-8")
        aff = best_affinity_from_vina_stdout(vr.stdout or "")
        if aff is not None:
            row["best_affinity_kcal_mol"] = f"{aff:.3f}"
        else:
            row["notes"] = f"vina_rc={vr.returncode}"
        rows.append(row)

    csv_path = OUT / "summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "slug",
                "label",
                "prep_ok",
                "best_affinity_kcal_mol",
                "prep_method",
                "notes",
            ],
        )
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    "slug": r["slug"],
                    "label": r["label"],
                    "prep_ok": r["prep_ok"],
                    "best_affinity_kcal_mol": r.get("best_affinity_kcal_mol", ""),
                    "prep_method": (r.get("prep_method") or "")[:80],
                    "notes": r.get("notes") or "",
                }
            )

    # Markdown for manuscript / SI
    md_lines = [
        "# Multi-ligand Vina × 1MSC (blind box)",
        "",
        f"**Generated (UTC):** {ts}",
        "",
        "Same receptor and search box as `rutin_1MSC/vina_config.txt`. "
        "**Not** site-matched to [7]. Lower (more negative) kcal mol⁻¹ = stronger predicted pose in this box.",
        "",
        "| Species (hypothesis pool) | Best Vina (kcal mol⁻¹) | Prep |",
        "|---------------------------|------------------------:|------|",
    ]
    for r in rows:
        aff = r.get("best_affinity_kcal_mol") or "--"
        prep = "OK" if r["prep_ok"] else "fail"
        md_lines.append(f"| {r['label']} | {aff} | {prep} |")
    md_lines.extend(
        [
            "",
            "Raw logs: `workflow_outputs/02_analysis/docking/rutin_1MSC_multiligand/`. "
            "Script: `scripts/rutin_multiligand_vina_1MSC.py`.",
        ]
    )
    (OUT / "vina_multiligand_summary.md").write_text("\n".join(md_lines), encoding="utf-8")

    (OUT / "manifest.json").write_text(
        json.dumps(
            {
                "generated_utc": ts,
                "docking_executable": dock_exe,
                "receptor": str(rec),
                "n_ligands": len(LIGANDS),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
