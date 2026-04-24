# CSE6140 Project — Minimum Vertex Cover

## Team
- Bo Feng (bfeng66@gatech.edu)
- Congyan Cruise Song (csong326@gatech.edu)
- Yihao Zhuang (yzhuang80@gatech.edu)

## Language
Python 3.10+

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
bnb.py        # Branch and Bound (exact)
approx.py     # 2-Approximation algorithm
ls1.py        # Local Search variant 1 (TBD)
ls2.py        # Local Search variant 2 (TBD)
report/       # ACM sigconf LaTeX report
  report.tex
  references.bib
notes/        # Project handout and Piazza posts
```

## Output Files

Each run produces:
- **Solution file** (`.sol`): vertex cover size + vertex list
- **Trace file** (`.trace`): improvement history (timestamp, best size) — BnB/LS1/LS2 only

## Algorithms

| ID     | Category       | Status |
|--------|---------------|--------|
| BnB    | Exact (Branch & Bound) | TODO |
| Approx | 2-Approximation       | TODO |
| LS1    | Local Search 1        | TODO |
| LS2    | Local Search 2        | TODO |
