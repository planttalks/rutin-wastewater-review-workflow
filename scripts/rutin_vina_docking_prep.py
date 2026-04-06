#!/usr/bin/env python3
"""
Prepare AutoDock Vina inputs for rutin vs MS2 coat protein (1MSC).

Requires: Open Babel (obabel on PATH or OBABEL_EXE).
Docking engine: env `VINA_EXE`, PATH `vina`, then `scripts/vina_*.exe` / `qvina*.exe` (see `README-docking-tools.md`). Use `--prep-only` if you run Qvina via a shell script.

Outputs under workflow_outputs/02_analysis/docking/rutin_1MSC/:
  1MSC.pdb, receptor.pdbqt, ligand.pdbqt, vina_config.txt,
  vina_docking_analysis.md, rutin_vina_manifest.json

Does not claim biological validity of box or scores--hypothesis-level prep only.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlretrieve

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workflow_outputs" / "02_analysis" / "docking" / "rutin_1MSC"
PDB_URL = "https://files.rcsb.org/download/1MSC.pdb"
# Must match PubChem-style connectivity (same as rutin_insilico_descriptors_core.py).
RUTIN_SMILES = (
    "CC1C(C(C(C(O1)OCC2C(C(C(C(O2)OC3=C(OC4=CC(=CC(=C4C3=O)O)O)"
    "C5=CC(=C(C=C5)O)O)O)O)O)O)O)O"
)


def obabel_exe() -> str:
    for key in ("OBABEL_EXE",):
        v = os.environ.get(key)
        if v and Path(v).exists():
            return v
    w = shutil.which("obabel")
    if w:
        return w
    p = Path(r"C:\Program Files\OpenBabel-2.4.1\obabel.EXE")
    if p.exists():
        return str(p)
    raise FileNotFoundError("obabel not found; set OBABEL_EXE or install Open Babel")


def docking_executable() -> str | None:
    """
    Vina-compatible CLIs: AutoDock Vina, QuickVina2 (qvina2.1), etc. (`--config` file).
    Priority: VINA_EXE → PATH vina → known names under scripts/ → sole *vina*.exe in scripts/.
    """
    v = os.environ.get("VINA_EXE")
    if v and Path(v).expanduser().exists():
        return str(Path(v).expanduser().resolve())
    w = shutil.which("vina")
    if w:
        return w
    sd = ROOT / "scripts"
    for name in (
        "vina_1.2.7_win.exe",
        "vina.exe",
        "qvina2.1.exe",
        "qvina2.exe",
        "Qvina2-w.exe",
        "qvina-w.exe",
        "QuickVina2-W.exe",
        "quickvina2.exe",
    ):
        p = sd / name
        if p.is_file():
            return str(p.resolve())
    vina_like = sorted(p for p in sd.glob("*.exe") if "vina" in p.name.lower())
    if len(vina_like) == 1:
        return str(vina_like[0].resolve())
    return None


def run_ob(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    exe = obabel_exe()
    return subprocess.run(
        [exe] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=120,
    )


def ligand_pdbqt_valid(p: Path) -> bool:
    if not p.exists() or p.stat().st_size < 50:
        return False
    txt = p.read_text(encoding="utf-8", errors="replace")
    return "ATOM" in txt or "HETATM" in txt


def prepare_ligand_pdbqt(smiles: str, out_pdbqt: Path, work_dir: Path) -> tuple[bool, str]:
    """Rutin-sized glycosides often yield empty PDBQT from obabel -:SMILES; use RDKit 3D first."""
    err_parts: list[str] = []
    lig_pdb = work_dir / "ligand_rdkit.pdb"
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            err_parts.append("RDKit MolFromSmiles failed")
        else:
            mol = Chem.AddHs(mol)
            rid = AllChem.EmbedMolecule(mol, randomSeed=42)
            if rid != 0:
                params = AllChem.ETKDGv3()
                params.randomSeed = 42
                rid = AllChem.EmbedMolecule(mol, params)
            if rid != 0:
                err_parts.append(f"RDKit EmbedMolecule code {rid}")
            else:
                AllChem.UFFOptimizeMolecule(mol, maxIters=300)
                Chem.MolToPDBFile(mol, str(lig_pdb))
                if lig_pdb.exists() and lig_pdb.stat().st_size > 200:
                    r = run_ob(
                        ["-ipdb", str(lig_pdb), "-opdbqt", "-O", str(out_pdbqt)],
                        work_dir,
                    )
                    if r.returncode == 0 and ligand_pdbqt_valid(out_pdbqt):
                        return True, "rdkit_3d_obabel_pdbqt"
                    err_parts.append((r.stderr or r.stdout or "")[:500])
    except ImportError:
        err_parts.append("rdkit not installed")
    except Exception as e:
        err_parts.append(str(e))

    r2 = run_ob(
        ["-:" + smiles, "-opdbqt", "-O", str(out_pdbqt), "--gen3d"],
        work_dir,
    )
    if r2.returncode == 0 and ligand_pdbqt_valid(out_pdbqt):
        return True, "obabel_smiles_only"
    err_parts.append((r2.stderr or r2.stdout or "")[:500])
    return False, " | ".join(err_parts)


def pdb_atom_coords(pdb_path: Path) -> list[tuple[float, float, float]]:
    coords: list[tuple[float, float, float]] = []
    for line in pdb_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith(("ATOM  ", "HETATM")):
            continue
        if len(line) < 54:
            continue
        try:
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
        except ValueError:
            continue
        coords.append((x, y, z))
    return coords


def binding_box(coords: list[tuple[float, float, float]], pad: float = 4.0, cap: float = 24.0):
    if not coords:
        return (0.0, 0.0, 0.0), (20.0, 20.0, 20.0)
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    zs = [c[2] for c in coords]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    minz, maxz = min(zs), max(zs)
    cx = (minx + maxx) / 2
    cy = (miny + maxy) / 2
    cz = (minz + maxz) / 2
    sx = min(cap, max(8.0, (maxx - minx) + 2 * pad))
    sy = min(cap, max(8.0, (maxy - miny) + 2 * pad))
    sz = min(cap, max(8.0, (maxz - minz) + 2 * pad))
    return (cx, cy, cz), (sx, sy, sz)


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Rutin × 1MSC docking prep (and optional Vina/Qvina run).")
    ap.add_argument(
        "--prep-only",
        action="store_true",
        help="Write PDBQT + vina_config.txt only; skip docking (use your Qvina/shell script in that folder).",
    )
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    pdb = OUT / "1MSC.pdb"
    rec = OUT / "receptor.pdbqt"
    lig = OUT / "ligand.pdbqt"
    cfg = OUT / "vina_config.txt"
    log_out = OUT / "vina_stdout.txt"

    dock_exe = docking_executable()
    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "script": "rutin_vina_docking_prep.py",
        "pdb_id": "1MSC",
        "pdb_url": PDB_URL,
        "obabel": obabel_exe(),
        "docking_executable": dock_exe,
        "prep_only": bool(args.prep_only),
    }

    if not pdb.exists() or pdb.stat().st_size < 1000:
        urlretrieve(PDB_URL, pdb)
    manifest["pdb_bytes"] = pdb.stat().st_size

    # Receptor: rigid pdbqt (exclude waters common in PDB -- obabel strips many)
    r1 = run_ob(["-ipdb", str(pdb), "-opdbqt", "-O", str(rec), "-xr"], OUT)
    if r1.returncode != 0 or not rec.exists():
        manifest["receptor_error"] = (r1.stderr or r1.stdout)[:2000]
        (OUT / "rutin_vina_manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        sys.stderr.write(f"obabel receptor failed: {r1.stderr}\n")
        return 1

    ok_lig, lig_how = prepare_ligand_pdbqt(RUTIN_SMILES, lig, OUT)
    manifest["ligand_prep"] = lig_how
    if not ok_lig:
        manifest["ligand_error"] = lig_how[:2500]
        (OUT / "rutin_vina_manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        sys.stderr.write(f"ligand pdbqt failed: {lig_how}\n")
        return 1

    coords = pdb_atom_coords(pdb)
    (cx, cy, cz), (sx, sy, sz) = binding_box(coords)
    manifest["search_center"] = {"x": cx, "y": cy, "z": cz}
    manifest["search_size"] = {"x": sx, "y": sy, "z": sz}

    cfg_text = f"""receptor = {rec.name}
ligand = {lig.name}
center_x = {cx:.3f}
center_y = {cy:.3f}
center_z = {cz:.3f}
size_x = {sx:.3f}
size_y = {sy:.3f}
size_z = {sz:.3f}
exhaustiveness = 8
num_modes = 9
energy_range = 4
"""
    cfg.write_text(cfg_text, encoding="utf-8")

    vina_ran = False
    best_affinity = None
    if args.prep_only:
        log_out.write_text(
            f"Prep-only (--prep-only). Working directory:\n  {OUT}\n\n"
            "Vina-compatible engines accept:\n"
            "  <engine> --config vina_config.txt\n\n"
            "From Git Bash / WSL you can run your scripts/*.sh after cd to the path above.\n"
            "See scripts/README-docking-tools.md\n",
            encoding="utf-8",
        )
    elif dock_exe:
        vr = subprocess.run(
            [dock_exe, "--config", str(cfg)],
            cwd=str(OUT),
            capture_output=True,
            text=True,
            timeout=600,
        )
        log_out.write_text((vr.stdout or "") + "\n--- STDERR ---\n" + (vr.stderr or ""), encoding="utf-8")
        manifest["vina_returncode"] = vr.returncode
        vina_ran = vr.returncode == 0
        for line in (vr.stdout or "").splitlines():
            if line.strip().startswith("1 "):
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        best_affinity = float(parts[1])
                    except ValueError:
                        pass
                break
    else:
        log_out.write_text(
            "No docking executable found. Prep complete.\n"
            f'  cd "{OUT}"\n'
            "  vina --config vina_config.txt\n"
            "Or set VINA_EXE to qvina2.1 / QuickVina2; see scripts/README-docking-tools.md\n",
            encoding="utf-8",
        )

    manifest["vina_executed"] = vina_ran
    manifest["best_affinity_kcal_mol"] = best_affinity
    (OUT / "rutin_vina_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    md = f"""# Vina docking prep: rutin × 1MSC (MS2 coat)

**Generated:** {manifest['generated_utc']}

## Files

| File | Role |
|------|------|
| `1MSC.pdb` | RCSB download |
| `receptor.pdbqt` | Rigid receptor (Open Babel) |
| `ligand.pdbqt` | Rutin: RDKit 3D + Open Babel PDBQT |
| `vina_config.txt` | Search box from full-structure extent + padding |
| `vina_stdout.txt` | Vina log or run instructions |

## Search box (blind, geometric)

- Center (Å): ({cx:.2f}, {cy:.2f}, {cz:.2f})
- Size (Å): ({sx:.2f}, {sy:.2f}, {sz:.2f})

**Caveat:** Whole-protein envelope docking is **not** equivalent to the site-specific capsid poses in [7]; scores are **not** comparable without matching the same pocket.

## Docking status

- **Executable:** `{dock_exe or 'NOT FOUND'}`
- **Prep-only:** {args.prep_only}
- **Ran:** {'yes' if vina_ran else 'no'}
- **Best mode 1 affinity (if run):** {best_affinity if best_affinity is not None else 'N/A'}

`scripts/README-docking-tools.md` -- Vina, Qvina, shell scripts. Re-run: `python scripts/rutin_vina_docking_prep.py` (or `--prep-only` then your `.sh`).
"""
    (OUT / "vina_docking_analysis.md").write_text(md, encoding="utf-8")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
