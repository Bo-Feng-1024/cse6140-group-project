# CSE6140 Project — Minimum Vertex Cover

## Team
- 3 members (TBD — fill in names)

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

## Project Structure

```
mvc.py        # Main entry point (CLI parsing, dispatch)
graph.py      # Graph class, I/O, vertex cover validation
utils.py      # Output file writing (.sol, .trace), Timer
bnb.py        # Branch and Bound (exact)
approx.py     # 2-Approximation algorithm
ls1.py        # Local Search variant 1 (TBD)
ls2.py        # Local Search variant 2 (TBD)
data/         # Input datasets (not committed — download from Canvas)
  test/       #   5 test instances
  small/      #   18 small instances
  large/      #   12 large instances
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
