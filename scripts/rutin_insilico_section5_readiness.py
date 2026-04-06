#!/usr/bin/env python3
"""
§5 illustrative readiness ladder: ordinal scores + SciPy rankdata (descriptive only).

Outputs:
  workflow_outputs/02_analysis/rutin_section5_readiness_ranks.csv
  workflow_outputs/02_analysis/rutin_section5_readiness_ranks.md
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

OUT = Path(__file__).resolve().parents[1] / "workflow_outputs" / "02_analysis"

# Ordinal readiness (0=discovery, 4=implementation-ready) for *wastewater virus log-reduction* context.
ROWS = [
    ("free_chlorine", 4, "Validated infectivity benchmarks in wastewater reviews [23]."),
    ("UV254", 4, "Established dose-response for surrogates/pathogens [26]."),
    ("ozone", 4, "Virus inactivation kinetics documented [28]."),
    ("membrane_RO_NF", 3, "High removal; matrix- and pilot-dependent [25,47]."),
    ("purified_rutin_virion", 1, "Phage proof-of-concept + docking [7]; no wastewater benchmark."),
    ("rutin_rhizosphere_passive", 0, "Hypothesis; Table 2 barrier 2/ passive release."),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    names = [r[0] for r in ROWS]
    scores = np.array([r[1] for r in ROWS], dtype=float)
    # Higher score = more ready → rank highest as 6
    ranks = rankdata(scores, method="average")

    csv_path = OUT / "rutin_section5_readiness_ranks.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["intervention", "readiness_0_to_4", "rank_higher_is_more_ready", "note"])
        for i, (n, s, note) in enumerate(ROWS):
            w.writerow([n, int(s), float(ranks[i]), note])

    lines = [
        "# §5 Readiness ladder (ordinal; not meta-analysis)",
        "",
        "SciPy `scipy.stats.rankdata` on integer readiness scores (higher = more implementation-ready for **documented virus attenuation in water/wastewater**).",
        "",
        "| Intervention | Readiness (0–4) | Rank |",
        "|--------------|-----------------|------|",
    ]
    order = np.argsort(-scores)
    for i in order:
        n, s, _ = ROWS[i]
        lines.append(f"| {n.replace('_', ' ')} | {int(s)} | {ranks[i]:.1f} |")
    lines.append("")
    lines.append(
        "**Caveat:** Scores are author-assigned for narrative comparison only; "
        "they do not replace quantitative benchmarking at matched matrices."
    )
    (OUT / "rutin_section5_readiness_ranks.md").write_text("\n".join(lines), encoding="utf-8")
    print(csv_path)


if __name__ == "__main__":
    main()
