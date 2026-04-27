# How to run the experiments and assemble the Canvas submission

The script `results/run_all.py` is the single entry point for running
all four algorithms (BnB, Approx, LS1, LS2) end-to-end on one machine.
It writes every `.sol` and `.trace` file required by Canvas section 9
of the project handout, in the exact filename format the autograder
expects, and aggregates the per-cell averages needed for the report's
comprehensive results table.

Run it on **one** machine for the report — having different team
members run different algorithms on different hardware makes the
runtimes in the report's comprehensive table incomparable, which the
report's *Experimental Setup* section is supposed to characterize as a
single platform.

## Prerequisites

- Python 3.10 (Gradescope target). No third-party packages are needed
  to run the algorithms; the convergence plot script
  (`results/bnb/plot_convergence.py`, optional, BnB-only) needs
  `matplotlib`.
- The `data/` directory unpacked from `data.zip` on Canvas, producing
  `data/test/`, `data/small/`, `data/large/` with the `.in`/`.out`
  files. The data is *not* in the repo by design.
- All four algorithm modules merged into `main`. As of this writing,
  `bnb.py`, `approx.py`, `ls1.py` are implemented; `ls2.py` may still
  be a stub — running it before Congyan's PR lands will produce a
  trivial all-vertices cover.

## Quick start

From the project root:

```bash
# Default: all four algorithms, all 35 instances, plus the 600s ×
# 20-seed runs on large1 / large12 for the QRTD/SQD/box plots.
# Total wall time on a recent laptop: ~10 hours. Plan accordingly.
python3 results/run_all.py
```

When the script returns, you have everything you need for the Canvas
zip and for the comprehensive table in the report.

## Subset runs

```bash
# One algorithm at a time:
python3 results/run_all.py --algs BnB
python3 results/run_all.py --algs Approx
python3 results/run_all.py --algs LS1
python3 results/run_all.py --algs LS2

# Multiple algorithms in one invocation:
python3 results/run_all.py --algs BnB Approx

# Only the 600s × 20-seed runs on large1 / large12 used for the
# QRTD / SQD / box plots in the report:
python3 results/run_all.py --algs qrtd

# Quick smoke test with fewer LS seeds (default is 20):
python3 results/run_all.py --algs LS1 --ls-seeds 3

# Rebuild results/comprehensive_summary.csv from existing
# per-algorithm runs.csv files without rerunning anything:
python3 results/run_all.py --summary
```

Cutoffs are configurable: `--bnb-cutoff`, `--approx-cutoff`,
`--ls-test-cutoff`, `--ls-small-cutoff`, `--ls-large-cutoff`,
`--ls-seeds`, `--qrtd-seeds`. Defaults match the handout (BnB 600s,
LS 2s on test/small to match the autograder, 60s on large for the
comprehensive table, 600s for the QRTD sweep on large1/large12).

## Where the outputs land

```
results/
  bnb/
    <inst>_BnB_<cutoff>.sol
    <inst>_BnB_<cutoff>.trace
    runs.csv
  approx/
    <inst>_Approx_<cutoff>.sol           # no .trace per handout 7.3
    runs.csv
  ls1/
    <inst>_LS1_<cutoff>_<seed>.sol
    <inst>_LS1_<cutoff>_<seed>.trace
    runs.csv
  ls2/
    <inst>_LS2_<cutoff>_<seed>.sol
    <inst>_LS2_<cutoff>_<seed>.trace
    runs.csv
  comprehensive_summary.csv              # aggregated table for the report
```

Filenames follow handout §7.3 (`<instance>_<algorithm>_<cutoff>.sol`
without seed for BnB/Approx; with seed appended for LS1/LS2).

`runs.csv` is a per-run log in each algorithm's folder; one row per
invocation with `inst, cat, alg, n, m, cutoff, seed, size, wall`.
`comprehensive_summary.csv` averages over seeds and joins the four
algorithms into one wide table.

`runs.csv` and `comprehensive_summary.csv` are git-ignored — they are
per-machine artifacts that the script regenerates. The `.sol` and
`.trace` files are likewise git-ignored so the repo stays small.

## Comprehensive summary columns

```
inst, cat, n, m, ref,
bnb_size, bnb_wall, bnb_relerr,
approx_size, approx_wall, approx_relerr,
ls1_avg_size, ls1_avg_wall, ls1_relerr, ls1_runs,
ls2_avg_size, ls2_avg_wall, ls2_relerr, ls2_runs
```

Sizes are averaged across all seeds for that instance/algorithm pair
(LS only — BnB/Approx are deterministic with one run each).
Relative error is `(avg_size - ref) / ref`. `ls{1,2}_runs` records the
number of seeds actually run, so you can spot uneven coverage.

## Time budget

Rough numbers on a 2024-ish laptop (Apple M-series or recent Intel):

| Workload | Wall time |
|----------|-----------|
| BnB on all 35 instances (600s cutoff) | ~2 hours |
| Approx on all 35 instances | seconds |
| LS1 on test/small (2s, 20 seeds × 23 inst) | ~15 minutes |
| LS1 on large (60s, 20 seeds × 12 inst) | ~4 hours |
| LS2 on test/small (2s) | ~15 minutes |
| LS2 on large (60s) | ~4 hours |
| QRTD: LS1+LS2 on large1/large12 (600s, 20 seeds × 2 inst × 2 alg) | ~13 hours |
| Default `python3 results/run_all.py` (everything above) | ~24 hours |

If 24 hours is too long, drop the `qrtd` workload (the default already
includes it) and run only the comprehensive-table workload:

```bash
python3 results/run_all.py --algs BnB Approx LS1 LS2
```

That brings it to roughly 10–11 hours. You can then run
`--algs qrtd` separately when you have time before the report is due.

## Building the Canvas zip

Per handout §9, the Canvas `CourseProject-code` zip needs:

1. all source code files (`*.py`)
2. the executable / scripts used to run them (`mvc.py` is the entry
   point; `results/run_all.py` is the orchestrator)
3. a README explaining how to run (the project's top-level `README.md`)
4. **all output files** (`.sol` and `.trace`) for the required datasets
5. (do NOT include the input data files)

A minimal recipe after `run_all.py` finishes:

```bash
cd /tmp
rm -rf cse6140-submit && mkdir cse6140-submit
cd cse6140-submit

# 1. source code
cp <project>/{mvc.py,graph.py,utils.py,bnb.py,approx.py,ls1.py,ls2.py} .

# 2. orchestrator (handy but not required by the autograder)
cp -r <project>/results .

# 3. README -- copy and rename so Canvas finds it
cp <project>/README.md .

# 4. flatten output files into the zip root (handout: "All files may be
#    placed in the same directory inside the zip archive")
cp <project>/results/bnb/*.sol     .
cp <project>/results/bnb/*.trace   .
cp <project>/results/approx/*.sol  .
cp <project>/results/ls1/*.sol     .
cp <project>/results/ls1/*.trace   .
cp <project>/results/ls2/*.sol     .
cp <project>/results/ls2/*.trace   .

cd .. && zip -r CourseProject-code.zip cse6140-submit
```

Upload `CourseProject-code.zip` to Canvas under
*CourseProject-code*. The report PDF goes to Gradescope under
*CourseProject-report*. The Gradescope autograder for
*CourseProject-program* needs only the `*.py` source.

## Common gotchas

- **LS2 returns a trivial all-vertex cover.** The module is still a
  stub on `main` until Congyan's PR lands. Either skip LS2
  (`--algs BnB Approx LS1 qrtd` will skip it but `qrtd` covers both LS
  variants — see below) or rerun once `ls2.py` is implemented.
  Specifically, `qrtd` always runs both LS1 and LS2; if you want just
  LS1 in the QRTD sweep, run the `LS1` workload with a `--ls-large-cutoff
  600` override on those instances by hand.
- **Reproducibility.** LS algorithms are seeded; running with the same
  seed list produces the same `.sol`/`.trace`. The script uses seeds
  `1..N` (default `N=20`).
- **Resuming.** The script writes per-run rows to
  `results/<alg>/runs.csv` as it goes and individual `.sol`/`.trace`
  files immediately. If you kill it midway, the partial data is on
  disk; just rerun the same command — already-finished files will be
  overwritten with identical content (same seeds, deterministic
  algorithms) and `runs.csv` rows for those runs will be duplicated.
  To avoid duplicate `runs.csv` rows on a clean rerun, delete the
  `runs.csv` for the algorithms you are rerunning before invoking the
  script again.
- **Validation.** Each cover is checked with `is_vertex_cover` from
  `graph.py` before its `.sol` is written; an `AssertionError` will
  abort the whole run. If that happens, file a bug — it means the
  algorithm produced an infeasible cover.
