# Group Meeting Agenda — April 24, 2026

## 1. Task Assignment

We have 4 algorithms + 1 report across 3 people. All algorithms can be developed in parallel.

### Algorithm ownership

| Person | Algorithm(s) | Notes |
|--------|-------------|-------|
| Bo Feng | BnB | Hardest algorithm — lower bound design + pruning |
| Yihao Zhuang | Approx + LS1 | Approx is straightforward (~30 min), so workload ≈ one algorithm |
| Congyan Song | LS2 | Comparable to LS1 |

Each person runs experiments and produces data for their own algorithm(s).

### Report ownership

Report is worth **36–40 out of 50 points** — the biggest scoring component. Split evenly:

| Section | Owner |
|---------|-------|
| Abstract, Introduction | Bo Feng |
| Problem Definition | Bo Feng |
| Related Work | Congyan Song |
| Algorithm — BnB | Bo Feng |
| Algorithm — Approx | Yihao Zhuang |
| Algorithm — LS1 | Yihao Zhuang |
| Algorithm — LS2 | Congyan Song |
| Empirical Evaluation (tables, plots) | Shared — each person contributes their own algorithm's results |
| Discussion, Conclusion | Yihao Zhuang |

### Optional dependency

Approx output can be used as initial upper bound for BnB or initial solution for LS, but this is an optimization — not a blocker for parallel development.

## 2. Algorithm-Specific Notes

Each owner decides their own implementation details. A few constraints to keep in mind:

- **LS1 & LS2 must differ** in family, neighborhood, or perturbation strategy. Since they're owned by different people, **coordinate your choices** before coding to avoid picking the same variant. Common options: Simulated Annealing, Hill Climbing, Tabu Search, Genetic Algorithm.
- **LS autograder:** must reach `.out` reference values on all test and small instances within **2 seconds**
- **LS experiments:** each LS must be run **20 times** (different seeds) on `large1` and `large12` for QRTD, SQD, and box plots
- **BnB** may not finish on large instances — use the `-time` cutoff and return the best solution found so far
- **Approx result** can optionally be used as BnB upper bound or LS initial solution, but not a prerequisite

## 3. Timeline

All three algorithms (BnB, Approx+LS1, LS2) can be developed **in parallel** — each lives in its own file with no code dependencies.

| Milestone | Target Date |
|-----------|-------------|
| All algorithms done | April 25 |
| All experiments complete (20 runs × 2 LS × 35 instances) | April 26 |
| Report draft | April 27 |
| Final submission | April 27/28 |

**Action item:** Confirm the submission deadline on Canvas/Gradescope today.

## 4. Collaboration Workflow

The code skeleton is already set up at: https://github.com/Bo-Feng-1024/cse6140-group-project

- Each algorithm lives in its own file (`bnb.py`, `approx.py`, `ls1.py`, `ls2.py`) — no merge conflicts expected
- Shared interface: every algorithm returns `(cover, trace)` where `cover` is a set of vertex IDs and `trace` is a list of `(timestamp, best_size)` tuples
- **Data is not in the repo** — each person should download `data.zip` from Canvas and unzip it locally (see README)
- **Gradescope environment:** Python 3.10.12 — avoid 3.11+ syntax (e.g., `ExceptionGroup`) or libraries not in the standard library
- Branch strategy: push directly to `main`, or use feature branches + PR? **Decide today.** - Let's go feature branches + PR 

## Current Repo Status

Everything below is already working end-to-end (CLI → read graph → call algorithm → write .sol/.trace):

```
mvc.py        # CLI entry point (fully implemented)
graph.py      # Graph class + I/O + vertex cover validator
utils.py      # Output file writing + Timer
bnb.py        # Stub (returns all vertices)
approx.py     # Stub (returns empty set)
ls1.py        # Stub (returns all vertices)
ls2.py        # Stub (returns all vertices)
report/       # ACM sigconf template with all sections outlined
```

To test: `python3 mvc.py -inst data/test/test1 -alg BnB -time 10 -seed 1`
