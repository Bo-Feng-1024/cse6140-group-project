"""Output file writing and timing utilities."""

import os
import time


def instance_name(inst_path):
    """Extract instance name from path, e.g. 'data/test/test1' -> 'test1'."""
    return os.path.basename(inst_path)


def write_solution(inst_path, alg, cutoff, seed, cover):
    """Write a .sol file.

    cover: iterable of vertex indices in the cover.
    """
    name = instance_name(inst_path)
    if alg in ('LS1', 'LS2'):
        filename = f"{name}_{alg}_{cutoff}_{seed}.sol"
    else:
        filename = f"{name}_{alg}_{cutoff}.sol"

    cover_sorted = sorted(cover)
    with open(filename, 'w') as f:
        f.write(f"{len(cover_sorted)}\n")
        f.write(' '.join(str(v) for v in cover_sorted) + '\n')


def write_trace(inst_path, alg, cutoff, seed, trace):
    """Write a .trace file.

    trace: list of (timestamp_seconds, best_solution_size) tuples.
    """
    name = instance_name(inst_path)
    if alg in ('LS1', 'LS2'):
        filename = f"{name}_{alg}_{cutoff}_{seed}.trace"
    else:
        filename = f"{name}_{alg}_{cutoff}.trace"

    with open(filename, 'w') as f:
        for t, val in trace:
            f.write(f"{t:.4f} {val}\n")


class Timer:
    """Simple wall-clock timer with cutoff check."""

    def __init__(self, cutoff):
        self.cutoff = cutoff
        self.start = time.time()

    def elapsed(self):
        return time.time() - self.start

    def is_time_up(self):
        return self.elapsed() >= self.cutoff
