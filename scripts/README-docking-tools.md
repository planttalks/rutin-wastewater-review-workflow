# Docking tools in `scripts/` (Vina, Qvina, shell helpers)

## What the Python driver does

`rutin_vina_docking_prep.py` builds **receptor/ligand PDBQT** and **`vina_config.txt`** under  
`workflow_outputs/02_analysis/docking/rutin_1MSC/`, then runs a **Vina-compatible** engine if found.

Engines that accept **`--config vina_config.txt`** include:

- **AutoDock Vina** (`vina`, `vina_1.2.7_win.exe`, …)
- **Quick Vina 2** (`qvina2.1`, `Qvina2-w.exe`, …) -- same config style as Vina for standard runs

## Resolution order (which binary runs)

1. **`VINA_EXE`** -- full path to any compatible executable (forces choice if several tools exist).
2. **`vina` on PATH**
3. **Known filenames** in this folder:  
   `vina_1.2.7_win.exe`, `vina.exe`, `qvina2.1.exe`, `qvina2.exe`, `Qvina2-w.exe`, `qvina-w.exe`, `QuickVina2-W.exe`, `quickvina2.exe`
4. **Exactly one** `*.exe` whose name contains **`vina`** (case-insensitive).  
   If **more than one** match (e.g. both Vina and Qvina), set **`VINA_EXE`** explicitly.

## Shell scripts (Qvina, batch workflows)

If you use **`.sh`** or **`.bat`** wrappers:

1. **Prep only** (no auto dock):

   ```bash
   python scripts/rutin_vina_docking_prep.py --prep-only
   ```

2. **Run your script** from the docking folder (paths are relative to it):

   ```bash
   cd "workflow_outputs/02_analysis/docking/rutin_1MSC"
   # Git Bash / WSL:
   bash ../../../scripts/your_qvina_run.sh
   ```

   Typical one-liner inside the shell script:

   ```bash
   /path/to/qvina2.1 --config vina_config.txt
   ```

3. Or on **cmd/PowerShell**, call your `.bat` after `cd` to `rutin_1MSC` the same way.

## Optional: point Python at Qvina instead of Vina

```powershell
$env:VINA_EXE = "P:\...\scripts\qvina2.1.exe"
python scripts/rutin_vina_docking_prep.py
```

## Files produced

| File | Purpose |
|------|---------|
| `vina_config.txt` | receptor, ligand, box, exhaustiveness |
| `ligand_out.pdbqt` | poses (after a successful dock) |
| `vina_stdout.txt` | engine log |
| `rutin_vina_manifest.json` | which executable ran, affinity if parsed |

**Note:** Qvina/Vina scores are **not** interchangeable with SwissDock or with literature AutoDock4 energies without matching setup.
