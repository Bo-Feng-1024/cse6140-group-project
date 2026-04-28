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


def plot_qrtd(inst, traces, ref, q_stars):
    fig, ax = plt.subplots(figsize=(6, 4.5))
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

        max_time_in_all_traces = max([xs[-1] for xs, _ in traces if xs] + [0])
        plot_x = solve_times + [max(solve_times[-1] * 1.1, max_time_in_all_traces)]
        plot_y = np.append(y_vals, y_vals[-1])

        ax.step(plot_x, plot_y, where="post", linewidth=2, label=f"q* = {q * 100:.1f}%")

    ax.set_title(f"QRTD: {inst}")
    ax.set_xlabel("Runtime (s)")
    ax.set_ylabel("Fraction of Runs Solved")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    out_png = os.path.join(HERE, f"{inst}_ls1_qrtd.png")
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
    print(f"  -> Wrote {out_png}")


def plot_sqd(inst, traces, ref, time_limits):
    fig, ax = plt.subplots(figsize=(6, 4.5))
    n_runs = len(traces)

    for tl in time_limits:
        best_errors = []
        for xs, ys in traces:
            best_val = ys[0] if ys else float("inf")
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

        ax.step(plot_x, plot_y, where="post", linewidth=2, label=f"Time = {tl}s")

    ax.set_title(f"SQD: {inst}")
    ax.set_xlabel("Relative Error (%)")
    ax.set_ylabel("Fraction of Runs Solved")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    out_png = os.path.join(HERE, f"{inst}_ls1_sqd.png")
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
    print(f"  -> Wrote {out_png}")


def plot_boxplot(inst, traces, ref, q_stars):
    fig, ax = plt.subplots(figsize=(6, 4.5))
    data, labels = [], []

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
            labels.append(f"{q * 100:.1f}%\n(n={len(times)})")
        else:
            data.append([0])
            labels.append(f"{q * 100:.1f}%\n(none)")

    if data:
        ax.boxplot(
            data,
            labels=labels,
            patch_artist=True,
            boxprops=dict(facecolor="lightblue", color="blue"),
            medianprops=dict(color="red", linewidth=1.5),
        )
        ax.set_title(f"Runtime Boxplots: {inst}")
        ax.set_xlabel("Target Relative Quality (q*)")
        ax.set_ylabel("Time (s) to reach target")
        ax.grid(True, alpha=0.3, axis="y")
        fig.tight_layout()

        out_png = os.path.join(HERE, f"{inst}_ls1_boxplot.png")
        fig.savefig(out_png, dpi=150)
        plt.close(fig)
        print(f"  -> Wrote {out_png}")


def main():
    target_instances = ["large1", "large12"]
    q_stars = [0.01, 0.03, 0.05]
    time_limits = [60.0, 300.0, 600.0]

    for inst in target_instances:
        ref = get_ref(inst)
        if ref is None:
            print(f"Reference value not found for {inst}, skipping.")
            continue

        trace_files = sorted(glob.glob(os.path.join(HERE, f"{inst}_LS1_600_*.trace")))
        if not trace_files:
            print(f"No 600s trace files found for {inst} in {HERE}.")
            continue

        traces = [read_trace(f) for f in trace_files]

        print(f"\nGenerating plots for {inst} ({len(traces)} runs)...")
        plot_qrtd(inst, traces, ref, q_stars)
        plot_sqd(inst, traces, ref, time_limits)
        plot_boxplot(inst, traces, ref, q_stars)


if __name__ == "__main__":
    main()
