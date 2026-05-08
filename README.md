# CSE6140 Project — Minimum Vertex Cover

## Team
- Bo Feng (bfeng66@gatech.edu)
- Congyan Cruise Song (csong326@gatech.edu)
- Yihao Zhuang (yzhuang80@gatech.edu)

## Language
Python 3.10 (target: Gradescope's Python 3.10.12). No third-party libraries are required to run the solver — `matplotlib` / `numpy` are only used by the plotting scripts under `results/`.

## How to Run

```bash
python3 mvc.py -inst <instance> -alg [BnB|Approx|LS1|LS2] -time <cutoff> -seed <seed>
```

### Examples

```bash
# Branch and Bound on test1, 10-second cutoff
python3 mvc.py -inst data/test/test1 -alg BnB -time 10 -seed 1

# Approximation on small1
python3 mvc.py -inst data/small/small1 -alg Approx -time 600 -seed 1

# Local Search 1 on large1, 600-second cutoff, seed 42
python3 mvc.py -inst data/large/large1 -alg LS1 -time 600 -seed 42

# Local Search 2
python3 mvc.py -inst data/large/large12 -alg LS2 -time 600 -seed 7
```

## Data Setup

The input datasets are **not** included in this repository. Before running, download `data.zip` from Canvas (Assignments → Project) and extract it into the project root:

```bash
# After downloading data.zip to this directory:
unzip data.zip
```

This should create the following structure:

```
data/
  test/       # 5 test instances (6–15 vertices)
  small/      # 18 small instances (25–198 vertices)
  large/      # 12 large instances (800–22963 vertices)
```

## Project Structure

```
mvc.py        # Main entry point (CLI parsing, dispatch)
graph.py      # Graph class, I/O, vertex cover validation
utils.py      # Output file writing (.sol, .trace), Timer
bnb.py        # Branch and Bound (exact) — NT kernel + matching LB
approx.py     # 2-Approximation (edge-pick)
ls1.py        # Local Search 1 — Simulated Annealing
ls2.py        # Local Search 2 — Genetic Algorithm
report/       # ACM sigconf LaTeX report (report.pdf is the compiled artifact)
  report.tex
  references.bib
results/      # Experiment outputs and plotting scripts (see below)
notes/        # Project handout, meeting notes, experiment how-to
```

## Output Files

Each run produces:
- **Solution file** (`.sol`): vertex cover size + vertex list
- **Trace file** (`.trace`): improvement history (timestamp, best size) — BnB/LS1/LS2 only

## Algorithms

| ID     | Category                          | File     | Status |
|--------|-----------------------------------|----------|--------|
| BnB    | Exact (Branch & Bound)            | `bnb.py` | Done — Nemhauser–Trotter LP kernel + matching lower bound + degree-1/2 reductions |
| Approx | 2-Approximation                   | `approx.py` | Done — pick any uncovered edge, add both endpoints |
| LS1    | Local Search — Simulated Annealing | `ls1.py` | Done — SA with k-vertex perturb + greedy repair + reheat |
| LS2    | Local Search — Genetic Algorithm  | `ls2.py` | Done — tournament + intersection crossover + mutation + greedy repair |

## Reproducing the Experiments

`results/run_all.py` runs all four algorithms and writes the `.sol` / `.trace`
files needed for the Canvas submission and the comprehensive table in the
report. See `notes/experiments-howto.md` for full details.

```bash
# all 4 algorithms (BnB + Approx + 20 LS seeds + 600s × 20 LS seeds on large1/12)
python3 results/run_all.py

# subsets
python3 results/run_all.py --algs BnB Approx
python3 results/run_all.py --algs LS1 LS2
python3 results/run_all.py --algs qrtd        # 600s × 20 seeds on large1/large12
python3 results/run_all.py --summary          # rebuild CSV without rerunning
```

Outputs land under:

```
results/<alg>/<inst>_<alg>_<cutoff>[_<seed>].sol
results/<alg>/<inst>_<alg>_<cutoff>[_<seed>].trace   # not for Approx
results/<alg>/runs.csv                               # per-run rows
results/comprehensive_summary.csv                    # cross-algorithm aggregate
results/ls1/*.png, results/ls2/*.png                 # QRTD / SQD / box plots
```

## Compiling the Report

```bash
cd report
pdflatex report.tex && bibtex report && pdflatex report.tex && pdflatex report.tex
```

The compiled `report/report.pdf` is the deliverable submitted to Canvas.
