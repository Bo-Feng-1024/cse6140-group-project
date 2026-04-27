"""Orchestrate experiments across all four MVC algorithms.

Outputs go under per-algorithm subdirectories:
    results/bnb/<inst>_BnB_<cutoff>.{sol,trace}
    results/approx/<inst>_Approx_<cutoff>.sol
    results/ls1/<inst>_LS1_<cutoff>_<seed>.{sol,trace}
    results/ls2/<inst>_LS2_<cutoff>_<seed>.{sol,trace}

Per-run summaries are appended to results/<alg>/runs.csv and a final
cross-algorithm aggregate to results/comprehensive_summary.csv.

Default budget (override via CLI):
    BnB     : 1 run / instance, cutoff = 600s
    Approx  : 1 run / instance, cutoff = 10s
    LS1/LS2 : 20 seeds / instance, cutoff = 2s on test/small, 60s on large
    large1, large12 additionally get 20 LS seeds at cutoff = 600s for
              QRTD / SQD / box plots.

Run a subset with the --algs flag, for example:
    python3 results/run_all.py --algs BnB Approx
    python3 results/run_all.py --algs LS1 LS2 --ls-seeds 5
    python3 results/run_all.py --algs qrtd          # only the 600s large1/12 LS runs
    python3 results/run_all.py --summary            # rebuild summary.csv only
"""

import argparse
import csv
import glob
import os
import sys
import time
from statistics import mean


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from graph import read_graph, is_vertex_cover  # noqa: E402
from utils import instance_name  # noqa: E402
from bnb import branch_and_bound  # noqa: E402
from approx import approx_vertex_cover  # noqa: E402
from ls1 import local_search_1  # noqa: E402
from ls2 import local_search_2  # noqa: E402


# ---------- Plumbing ----------

def all_instances():
    plan = []
    for cat in ('test', 'small', 'large'):
        for path in sorted(glob.glob(os.path.join(ROOT, 'data', cat, '*.in'))):
            plan.append((path[:-3], cat))
    return plan


def call_alg(alg, graph, cutoff, seed):
    if alg == 'BnB':
        return branch_and_bound(graph, cutoff)
    if alg == 'Approx':
        return approx_vertex_cover(graph, cutoff)
    if alg == 'LS1':
        return local_search_1(graph, cutoff, seed)
    if alg == 'LS2':
        return local_search_2(graph, cutoff, seed)
    raise ValueError(alg)


def filenames(alg, name, cutoff, seed):
    if alg in ('LS1', 'LS2'):
        stem = f"{name}_{alg}_{cutoff}_{seed}"
    else:
        stem = f"{name}_{alg}_{cutoff}"
    return f"{stem}.sol", f"{stem}.trace"


def write_outputs(out_dir, alg, name, cutoff, seed, cover, trace):
    sol, trc = filenames(alg, name, cutoff, seed)
    with open(os.path.join(out_dir, sol), 'w') as f:
        cover_sorted = sorted(cover)
        f.write(f"{len(cover_sorted)}\n")
        f.write(' '.join(str(v) for v in cover_sorted) + '\n')
    if alg != 'Approx':
        with open(os.path.join(out_dir, trc), 'w') as f:
            for t, val in trace:
                f.write(f"{t:.4f} {val}\n")


def run_one(alg, inst_path, cat, cutoff, seed, out_dir):
    g = read_graph(inst_path)
    name = instance_name(inst_path)
    t0 = time.time()
    cover, trace = call_alg(alg, g, cutoff, seed)
    wall = time.time() - t0
    if not is_vertex_cover(g, cover):
        raise RuntimeError(f"{alg}/{name}: invalid cover")
    write_outputs(out_dir, alg, name, cutoff, seed, cover, trace)
    return {
        'inst': name, 'cat': cat, 'alg': alg,
        'n': g.n, 'm': g.m, 'cutoff': cutoff, 'seed': seed,
        'size': len(cover), 'wall': round(wall, 4),
    }


def append_runs_csv(out_dir, rows):
    if not rows:
        return
    path = os.path.join(out_dir, 'runs.csv')
    write_header = not os.path.exists(path)
    with open(path, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if write_header:
            w.writeheader()
        w.writerows(rows)


# ---------- Per-algorithm runners ----------

def run_bnb(cutoff):
    out_dir = os.path.join(HERE, 'bnb')
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    for inst, cat in all_instances():
        name = instance_name(inst)
        c = 10 if cat == 'test' else cutoff
        print(f"[BnB] {name} (cutoff={c}s)", flush=True)
        rows.append(run_one('BnB', inst, cat, c, 1, out_dir))
        print(f"   -> size={rows[-1]['size']} wall={rows[-1]['wall']}s", flush=True)
    append_runs_csv(out_dir, rows)


def run_approx(cutoff):
    out_dir = os.path.join(HERE, 'approx')
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    for inst, cat in all_instances():
        name = instance_name(inst)
        print(f"[Approx] {name}", flush=True)
        rows.append(run_one('Approx', inst, cat, cutoff, 1, out_dir))
        print(f"   -> size={rows[-1]['size']} wall={rows[-1]['wall']}s", flush=True)
    append_runs_csv(out_dir, rows)


def run_ls(alg, cutoffs, seeds):
    """alg in {'LS1','LS2'}; cutoffs: dict cat->seconds; seeds: list[int]."""
    out_dir = os.path.join(HERE, alg.lower())
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    for inst, cat in all_instances():
        name = instance_name(inst)
        c = cutoffs[cat]
        for s in seeds:
            print(f"[{alg}] {name} cutoff={c}s seed={s}", flush=True)
            rows.append(run_one(alg, inst, cat, c, s, out_dir))
    append_runs_csv(out_dir, rows)


def run_qrtd(seeds):
    """20-seed runs on large1 and large12 at cutoff=600s for QRTD/SQD/box plots."""
    targets = [
        (os.path.join(ROOT, 'data', 'large', 'large1'), 'large'),
        (os.path.join(ROOT, 'data', 'large', 'large12'), 'large'),
    ]
    for alg in ('LS1', 'LS2'):
        out_dir = os.path.join(HERE, alg.lower())
        os.makedirs(out_dir, exist_ok=True)
        rows = []
        for inst, cat in targets:
            name = instance_name(inst)
            for s in seeds:
                print(f"[{alg}/qrtd] {name} cutoff=600s seed={s}", flush=True)
                rows.append(run_one(alg, inst, cat, 600, s, out_dir))
        append_runs_csv(out_dir, rows)


# ---------- Summary aggregation ----------

def ref_size(inst_name, cat):
    path = os.path.join(ROOT, 'data', cat, inst_name + '.out')
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return int(f.readline().strip())


def parse_sol(path):
    with open(path) as f:
        return int(f.readline().strip())


def collect_alg_results(alg):
    """Return dict[inst_name] -> list of (size, wall, seed) tuples."""
    folder = alg.lower()
    runs_csv = os.path.join(HERE, folder, 'runs.csv')
    out = {}
    if not os.path.exists(runs_csv):
        return out
    with open(runs_csv) as f:
        for r in csv.DictReader(f):
            out.setdefault(r['inst'], []).append(
                (int(r['size']), float(r['wall']), int(r['seed']), int(r['cutoff']))
            )
    return out


def build_summary():
    cols = ['inst', 'cat', 'n', 'm', 'ref',
            'bnb_size', 'bnb_wall', 'bnb_relerr',
            'approx_size', 'approx_wall', 'approx_relerr',
            'ls1_avg_size', 'ls1_avg_wall', 'ls1_relerr', 'ls1_runs',
            'ls2_avg_size', 'ls2_avg_wall', 'ls2_relerr', 'ls2_runs']
    bnb = collect_alg_results('bnb')
    approx = collect_alg_results('approx')
    ls1 = collect_alg_results('ls1')
    ls2 = collect_alg_results('ls2')

    rows = []
    for inst, cat in all_instances():
        name = instance_name(inst)
        g = read_graph(inst)
        ref = ref_size(name, cat)

        def cell(d):
            entries = d.get(name, [])
            if not entries:
                return None, None, len(entries)
            sizes = [e[0] for e in entries]
            walls = [e[1] for e in entries]
            return mean(sizes), mean(walls), len(entries)

        b_size, b_wall, _ = cell(bnb)
        a_size, a_wall, _ = cell(approx)
        l1_size, l1_wall, l1_n = cell(ls1)
        l2_size, l2_wall, l2_n = cell(ls2)

        def relerr(s):
            if s is None or ref is None or ref == 0:
                return None
            return (s - ref) / ref

        rows.append({
            'inst': name, 'cat': cat, 'n': g.n, 'm': g.m, 'ref': ref,
            'bnb_size': b_size, 'bnb_wall': b_wall, 'bnb_relerr': relerr(b_size),
            'approx_size': a_size, 'approx_wall': a_wall, 'approx_relerr': relerr(a_size),
            'ls1_avg_size': l1_size, 'ls1_avg_wall': l1_wall, 'ls1_relerr': relerr(l1_size), 'ls1_runs': l1_n,
            'ls2_avg_size': l2_size, 'ls2_avg_wall': l2_wall, 'ls2_relerr': relerr(l2_size), 'ls2_runs': l2_n,
        })

    out = os.path.join(HERE, 'comprehensive_summary.csv')
    with open(out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            for k in ('bnb_wall', 'approx_wall', 'ls1_avg_wall', 'ls2_avg_wall'):
                if r[k] is not None:
                    r[k] = f"{r[k]:.4f}"
            for k in ('bnb_size', 'approx_size', 'ls1_avg_size', 'ls2_avg_size'):
                if r[k] is not None:
                    r[k] = f"{r[k]:.2f}"
            for k in ('bnb_relerr', 'approx_relerr', 'ls1_relerr', 'ls2_relerr'):
                if r[k] is not None:
                    r[k] = f"{r[k]:.4f}"
            w.writerow(r)
    print(f"wrote {out} ({len(rows)} rows)")


# ---------- CLI ----------

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--algs', nargs='+',
                   choices=['BnB', 'Approx', 'LS1', 'LS2', 'qrtd', 'all'],
                   default=['all'],
                   help='which workloads to run')
    p.add_argument('--bnb-cutoff', type=int, default=600)
    p.add_argument('--approx-cutoff', type=int, default=10)
    p.add_argument('--ls-test-cutoff', type=int, default=2)
    p.add_argument('--ls-small-cutoff', type=int, default=2)
    p.add_argument('--ls-large-cutoff', type=int, default=60)
    p.add_argument('--ls-seeds', type=int, default=20,
                   help='number of LS seeds per instance (default 20)')
    p.add_argument('--qrtd-seeds', type=int, default=20,
                   help='number of seeds for the 600s large1/large12 QRTD runs')
    p.add_argument('--summary', action='store_true',
                   help='just rebuild comprehensive_summary.csv from existing runs.csv files')
    args = p.parse_args()

    if args.summary:
        build_summary()
        return

    expand = {'all': ['BnB', 'Approx', 'LS1', 'LS2', 'qrtd']}
    todo = []
    for a in args.algs:
        todo.extend(expand.get(a, [a]))

    seeds = list(range(1, args.ls_seeds + 1))
    qrtd_seeds = list(range(1, args.qrtd_seeds + 1))
    ls_cutoffs = {'test': args.ls_test_cutoff,
                  'small': args.ls_small_cutoff,
                  'large': args.ls_large_cutoff}

    if 'BnB' in todo:
        run_bnb(args.bnb_cutoff)
    if 'Approx' in todo:
        run_approx(args.approx_cutoff)
    if 'LS1' in todo:
        run_ls('LS1', ls_cutoffs, seeds)
    if 'LS2' in todo:
        run_ls('LS2', ls_cutoffs, seeds)
    if 'qrtd' in todo:
        run_qrtd(qrtd_seeds)

    build_summary()


if __name__ == '__main__':
    main()
