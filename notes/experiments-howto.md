# Running the experiments

`results/run_all.py` runs all four algorithms and writes the
`.sol` / `.trace` files needed for the Canvas submission and the
comprehensive table in the report. Run it on **one** machine so the
runtimes in that table are comparable.

## Run

```bash
# all 4 algorithms, ~10 hours
python3 results/run_all.py

# subset
python3 results/run_all.py --algs BnB Approx     # ~2h
python3 results/run_all.py --algs LS1 LS2        # ~8h
python3 results/run_all.py --algs qrtd           # 600s × 20 seeds on large1/large12
python3 results/run_all.py --summary             # rebuild CSV without rerunning
```

Cutoffs are configurable, e.g. `--bnb-cutoff 300 --ls-seeds 5`.

## Outputs

```
results/<alg>/<inst>_<alg>_<cutoff>[_<seed>].sol
results/<alg>/<inst>_<alg>_<cutoff>[_<seed>].trace   # not for Approx
results/comprehensive_summary.csv                    # report table source
```

## Canvas zip

Flatten `*.sol` + `*.trace` from `results/{bnb,approx,ls1,ls2}/`
together with the `.py` source files into one directory and zip it.
Do not include `data/`.
