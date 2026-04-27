"""Generate QRTD, SQD, and Box Plots for LS1.

Reads the 20 .trace files for large1 and large12.
Output: .pdf and .png files for each instance.
"""

import os
import glob
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def read_trace(path):
    xs, ys = [], []
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) == 2:
                xs.append(float(parts[0]))
                ys.append(int(parts[1]))
    return xs, ys


def get_ref(inst):
    for cat in ["test", "small", "large"]:
        path = os.path.join(ROOT, "data", cat, f"{inst}.out")
        if os.path.exists(path):
            with open(path) as f:
                return int(f.readline().strip())
    return None


def plot_qrtd(inst, traces, ref, q_stars, ax):
    """QRTD: Fix target relative quality (q*), vary runtime.
    X: Time, Y: Fraction of runs reaching quality q*
    """
    n_runs = len(traces)

    for q in q_stars:
        target_size = ref * (1 + q)
        solve_times = []

        for xs, ys in traces:
            for t, size in zip(xs, ys):
                if size <= target_size:
                    solve_times.append(t)
                    break

        solve_times.sort()
        if not solve_times:
            ax.plot([0, 1], [0, 0], label=f"q*={q * 100:.1f}% (0 solved)")
            continue

        y_vals = np.arange(1, len(solve_times) + 1) / n_runs

        max_time_in_all_traces = max([xs[-1] for xs, _ in traces if xs])
        plot_x = solve_times + [max(solve_times[-1] * 1.1, max_time_in_all_traces)]
        plot_y = np.append(y_vals, y_vals[-1])

        ax.step(plot_x, plot_y, where="post", label=f"q* = {q * 100:.1f}%")

    ax.set_title(f"QRTD: {inst}")
    ax.set_xlabel("Runtime (s)")
    ax.set_ylabel("Fraction of Runs Solved")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(True, alpha=0.3)


def plot_sqd(inst, traces, ref, time_limits, ax):
    """SQD: Fix runtime limit, vary solution quality.
    X: Target Relative Error (%), Y: Fraction of runs achieving <= that error
    """
    n_runs = len(traces)

    for tl in time_limits:
        best_errors = []

        for xs, ys in traces:
            best_val = ys[0]
            for t, size in zip(xs, ys):
                if t <= tl:
                    best_val = size
                else:
                    break
            rel_err = (best_val - ref) / ref * 100
            best_errors.append(rel_err)

        best_errors.sort()

        if not best_errors:
            continue

        y_vals = np.arange(1, len(best_errors) + 1) / n_runs

        plot_x = best_errors + [best_errors[-1] + max(1.0, best_errors[-1] * 0.1)]
        plot_y = np.append(y_vals, y_vals[-1])

        ax.step(plot_x, plot_y, where="post", label=f"Time = {tl}s")

    ax.set_title(f"SQD: {inst}")
    ax.set_xlabel("Relative Error (%)")
    ax.set_ylabel("Fraction of Runs Solved")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(True, alpha=0.3)


def plot_boxplot(inst, traces, ref, q_stars, ax):
    """Box plot of runtimes required to reach specific q* qualities."""
    data = []
    labels = []

    for q in q_stars:
        target_size = ref * (1 + q)
        times = []
        for xs, ys in traces:
            for t, size in zip(xs, ys):
                if size <= target_size:
                    times.append(t)
                    break
        if times:
            data.append(times)
            labels.append(f"{q * 100:.1f}%")
        else:
            data.append([0])
            labels.append(f"{q * 100:.1f}%\n(none)")

    if data:
        ax.boxplot(data, labels=labels)
        ax.set_title(f"Runtime Boxplots: {inst}")
        ax.set_xlabel("Target Relative Quality (q*)")
        ax.set_ylabel("Time (s) to reach target")
        ax.grid(True, alpha=0.3, axis="y")


def main():
    target_instances = ["large1", "large12"]

    for inst in target_instances:
        ref = get_ref(inst)
        if ref is None:
            continue

        trace_files = glob.glob(os.path.join(HERE, f"{inst}_LS1_*.trace"))
        if not trace_files:
            trace_files = glob.glob(
                os.path.join(ROOT, "data", "large", f"{inst}_LS1_*.trace")
            )

        if not trace_files:
            print(f"No trace files found for {inst}.")
            continue

        traces = [read_trace(f) for f in trace_files]

        fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

        q_stars = [0.01, 0.03, 0.05]

        time_limits = [10.0, 60.0, 300.0]

        plot_qrtd(inst, traces, ref, q_stars, axes[0])
        plot_sqd(inst, traces, ref, time_limits, axes[1])
        plot_boxplot(inst, traces, ref, q_stars, axes[2])

        fig.suptitle(
            f"Local Search 1 Analysis: {inst} ({len(traces)} runs)", fontsize=14
        )
        fig.tight_layout()

        out_pdf = os.path.join(HERE, f"{inst}_ls1_analysis.pdf")
        out_png = os.path.join(HERE, f"{inst}_ls1_analysis.png")

        fig.savefig(out_pdf, bbox_inches="tight")
        fig.savefig(out_png, bbox_inches="tight", dpi=150)

        print(f"Wrote {out_pdf} and {out_png}")


if __name__ == "__main__":
    main()
