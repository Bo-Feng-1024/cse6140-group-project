"""Run LS1 on instances. Does 20 seeds for large1 & large12, 1 seed for others.

Outputs:
  results/ls1/*.sol, *.trace      -- solutions and traces
  results/ls1/summary.csv         -- averaged results
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
from ls1 import local_search_1
from utils import write_solution, write_trace, instance_name


def run(g, cutoff, seed):
    t0 = time.time()
    cover, trace = local_search_1(g, cutoff, seed)
    wall = time.time() - t0
    assert is_vertex_cover(g, cover), "Invalid cover returned by LS1"
    return cover, trace, wall


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


        if name in ["large1", "large12"]:
            seeds = list(range(1, 21))
        else:
            seeds = [1]

        print(f"[{cat}] {name} (cutoff={cutoff}s, seeds={len(seeds)})", flush=True)
        g = read_graph(inst_path)
        ref = ref_size(inst_path)

        total_size = 0
        total_wall = 0

        for seed in seeds:
            cover, trace, wall = run(g, cutoff, seed)


            write_solution(inst_path, "LS1", cutoff, seed, cover)
            write_trace(inst_path, "LS1", cutoff, seed, trace)

            total_size += len(cover)
            total_wall += wall

        avg_size = total_size / len(seeds)
        avg_wall = total_wall / len(seeds)
        rel = (avg_size - ref) / ref if ref else None

        rows.append(
            {
                "inst": name,
                "cat": cat,
                "n": g.n,
                "m": g.m,
                "ref": ref,
                "avg_ls1_size": f"{avg_size:.1f}",
                "rel_err": f"{rel:.4f}" if rel is not None else "",
                "avg_wall_time": f"{avg_wall:.4f}",
                "num_runs": len(seeds),
            }
        )
        print(
            f"   -> avg_size={avg_size:.1f} ref={ref} rel_err={rel} avg_wall={avg_wall:.3f}s",
            flush=True,
        )

    with open("summary.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {len(rows)} rows to {HERE}/summary.csv")


if __name__ == "__main__":
    main()
