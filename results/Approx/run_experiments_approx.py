"""Run Approx on every test/small/large instance and record results.

Outputs:
  results/approx/*.sol            -- per-instance solution (NO trace required for Approx)
  results/approx/summary.csv      -- inst, n, m, ref, approx_size, rel_err, wall_time
"""

import csv
import os
import sys
import time
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from graph import read_graph, is_vertex_cover
from approx import approx_vertex_cover
from utils import write_solution, instance_name


def run(inst_path, cutoff):
    g = read_graph(inst_path)
    t0 = time.time()
    cover, _ = approx_vertex_cover(g, cutoff)
    wall = time.time() - t0
    assert is_vertex_cover(g, cover), f"Invalid cover for {inst_path}"
    return g, cover, wall


def ref_size(inst_path):
    out = inst_path + ".out"
    if not os.path.exists(out):
        return None
    with open(out) as f:
        return int(f.readline().strip())


def main():
    os.chdir(HERE)

    plan = []
    for cat, cutoff in [("test", 2), ("small", 2), ("large", 600)]:
        pattern = os.path.join(ROOT, "data", cat, "*.in")
        for path in sorted(glob.glob(pattern)):
            plan.append((path[:-3], cat, cutoff))

    rows = []
    for inst_path, cat, cutoff in plan:
        name = instance_name(inst_path)
        print(f"[{cat}] {name} (Approx)", flush=True)
        g, cover, wall = run(inst_path, cutoff)


        write_solution(inst_path, "Approx", cutoff, None, cover)

        ref = ref_size(inst_path)
        rel = (len(cover) - ref) / ref if ref else None
        rows.append(
            {
                "inst": name,
                "cat": cat,
                "n": g.n,
                "m": g.m,
                "ref": ref,
                "approx_size": len(cover),
                "rel_err": f"{rel:.4f}" if rel is not None else "",
                "wall_time": f"{wall:.4f}",
            }
        )
        print(
            f"   -> size={len(cover)} ref={ref} rel_err={rel} wall={wall:.4f}s",
            flush=True,
        )

    with open("summary.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {len(rows)} rows to {HERE}/summary.csv")


if __name__ == "__main__":
    main()
