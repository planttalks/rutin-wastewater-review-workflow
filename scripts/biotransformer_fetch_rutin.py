#!/usr/bin/env python3
"""Submit rutin to BioTransformer (HGUT + ENVMICRO), poll until Done or timeout. Writes JSON to workflow_outputs/02_analysis/."""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

BASE = "https://biotransformer.ca"
RUTIN = "CC1C(C(C(C(O1)OCC2C(C(C(C(O2)OC3=C(OC4=CC(=CC(=C4C3=O)O)O)C5=CC(=C(C=C5)O)O)O)O)O)O)O)O"
OUT = Path(__file__).resolve().parents[1] / "workflow_outputs" / "02_analysis"


def qid(r: httpx.Response) -> int | None:
    if r.status_code in (301, 302, 303, 307, 308):
        m = re.search(r"/queries/(\d+)", r.headers.get("location") or "")
        return int(m.group(1)) if m else None
    return None


async def run_one(
    client: httpx.AsyncClient, label: str, option: str, steps: int, polls: int, sleep: float
) -> dict:
    body = {
        "task_type": "PREDICTION",
        "biotransformer_option": option,
        "query_input": f"{label}\t{RUTIN}",
        "number_of_steps": steps,
    }
    r = await client.post("/queries.json", json=body)
    qi = qid(r)
    if qi is None:
        return {"label": label, "error": "no_redirect", "text": (r.text or "")[:500]}
    async with httpx.AsyncClient(
        base_url=BASE, timeout=120.0, headers={"Accept": "application/json"}
    ) as gc:
        for _ in range(polls):
            await asyncio.sleep(sleep)
            d = (await gc.get(f"/queries/{qi}.json")).json()
            st = (d.get("status") or "").lower()
            if st in ("done", "failed", "error"):
                d["_label"] = label
                d["_query_id"] = qi
                return d
    return {"_label": label, "_query_id": qi, "status": "timeout_after_polls", "polls": polls}


async def main() -> int:
    ap = argparse.ArgumentParser(description="BioTransformer API: rutin HGUT + ENVMICRO")
    ap.add_argument("--polls", type=int, default=360, help="max GET polls per job (default 360)")
    ap.add_argument("--sleep", type=float, default=20.0, help="seconds between polls (default 20)")
    ap.add_argument(
        "--sequential",
        action="store_true",
        help="run ENVMICRO after HGUT finishes (default: both in parallel)",
    )
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jobs = [("HGUT", "rutin_HGUT_1"), ("ENVMICRO", "rutin_ENVMICRO_1")]

    async with httpx.AsyncClient(base_url=BASE, timeout=120.0, follow_redirects=False) as c:
        if args.sequential:
            out = []
            for opt, lab in jobs:
                print(f"Submit {lab}...", flush=True)
                out.append(await run_one(c, lab, opt, 1, polls=args.polls, sleep=args.sleep))
        else:
            async def submit_poll(opt: str, lab: str) -> dict:
                print(f"Submit {lab}...", flush=True)
                return await run_one(c, lab, opt, 1, polls=args.polls, sleep=args.sleep)

            out = list(await asyncio.gather(*[submit_poll(o, l) for o, l in jobs]))

    p = OUT / f"biotransformer_rutin_HGUT_ENVMICRO_{ts}.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(p, flush=True)
    for b in out:
        print(b.get("_label"), b.get("status"), b.get("number_of_unique_metabolites"), flush=True)
    return 0


if __name__ == "__main__":
    asyncio.run(main())
