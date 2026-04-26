"""Run BnB on every test/small/large instance and record results.

Outputs:
  results/bnb/*.sol, *.trace      -- per-instance solution + trace
  results/bnb/summary.csv         -- inst, n, m, ref, bnb_size, rel_err, wall_time, hit_cutoff
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
from bnb import branch_and_bound
from utils import write_solution, write_trace, instance_name


def run(inst_path, cutoff):
    g = read_graph(inst_path)
    t0 = time.time()
    cover, trace = branch_and_bound(g, cutoff)
    wall = time.time() - t0
    assert is_vertex_cover(g, cover), f"Invalid cover for {inst_path}"
    return g, cover, trace, wall


def ref_size(inst_path):
    out = inst_path + '.out'
    if not os.path.exists(out):
        return None
    with open(out) as f:
        return int(f.readline().strip())


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(out_dir)

    plan = []
    for cat, cutoff in [('test', 10), ('small', 60), ('large', 60)]:
        pattern = os.path.join(ROOT, 'data', cat, '*.in')
        for path in sorted(glob.glob(pattern)):
            plan.append((path[:-3], cat, cutoff))

    rows = []
    for inst_path, cat, cutoff in plan:
        name = instance_name(inst_path)
        print(f"[{cat}] {name} (cutoff={cutoff}s)", flush=True)
        g, cover, trace, wall = run(inst_path, cutoff)
        write_solution(inst_path, 'BnB', cutoff, 1, cover)
        write_trace(inst_path, 'BnB', cutoff, 1, trace)
        ref = ref_size(inst_path)
        rel = (len(cover) - ref) / ref if ref else None
        hit = wall >= cutoff - 0.1
        rows.append({
            'inst': name,
            'cat': cat,
            'n': g.n,
            'm': g.m,
            'ref': ref,
            'bnb_size': len(cover),
            'rel_err': f"{rel:.4f}" if rel is not None else "",
            'wall_time': f"{wall:.4f}",
            'hit_cutoff': 'Y' if hit else 'N',
        })
        print(f"   -> size={len(cover)} ref={ref} rel_err={rel} wall={wall:.3f}s hit={hit}",
              flush=True)

    with open('summary.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {len(rows)} rows to {out_dir}/summary.csv")


if __name__ == '__main__':
    main()
