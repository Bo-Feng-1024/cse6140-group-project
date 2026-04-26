"""Generate BnB anytime convergence plots.

Reads .trace files in this directory and plots best-cover-size over
elapsed seconds for a chosen set of representative instances. Output:
    bnb_convergence.pdf -- one figure with subplots for each instance.

Each trace file has lines: "<timestamp_seconds> <best_cover_size>"
"""

import os
import sys
import glob

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt


HERE = os.path.dirname(os.path.abspath(__file__))


def read_trace(path):
    xs, ys = [], []
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) != 2:
                continue
            xs.append(float(parts[0]))
            ys.append(int(parts[1]))
    return xs, ys


def read_ref(inst):
    proj = os.path.dirname(os.path.dirname(HERE))
    for cat in ('large', 'small', 'test'):
        path = os.path.join(proj, 'data', cat, inst + '.out')
        if os.path.exists(path):
            with open(path) as f:
                return int(f.readline().strip())
    return None


def main():
    instances = [
        ('large1',  'sparse real-world Internet topology'),
        ('large5',  'dense bipartite (LP-tight after kernel)'),
        ('large6',  'dense bipartite (LP-tight after kernel)'),
        ('large12', 'dense DIMACS benchmark'),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(11, 6.5))
    axes = axes.flat

    for ax, (inst, descr) in zip(axes, instances):
        traces = sorted(glob.glob(os.path.join(HERE, f'{inst}_BnB_*.trace')))
        if not traces:
            ax.text(0.5, 0.5, f'no trace for {inst}',
                    transform=ax.transAxes, ha='center', va='center')
            ax.set_title(inst)
            continue
        xs, ys = read_trace(traces[-1])
        # Extend trace with a final flat segment to the cutoff for visual clarity.
        cutoff = 60.0
        if xs and xs[-1] < cutoff:
            xs_plot = xs + [cutoff]
            ys_plot = ys + [ys[-1]]
        else:
            xs_plot, ys_plot = xs, ys
        ax.step(xs_plot, ys_plot, where='post', linewidth=1.8,
                color='C0', label='BnB best-so-far')
        ax.scatter(xs, ys, color='C0', s=22, zorder=3)

        ref = read_ref(inst)
        if ref is not None:
            ax.axhline(ref, color='C3', linestyle='--', linewidth=1.2,
                       label=f'reference = {ref}')

        ax.set_xlabel('elapsed time (s)')
        ax.set_ylabel('best cover size')
        ax.set_title(f'{inst} -- {descr}')
        ax.set_xlim(left=0)
        # Add some y-margin so the trace is visible above/below the reference line.
        if ys:
            ymin = min(ys + [ref] if ref is not None else ys)
            ymax = max(ys + [ref] if ref is not None else ys)
            pad = max(2, (ymax - ymin) * 0.12)
            ax.set_ylim(ymin - pad, ymax + pad)
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)

    fig.suptitle('Branch-and-Bound anytime convergence on representative instances',
                 fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out_pdf = os.path.join(HERE, 'bnb_convergence.pdf')
    out_png = os.path.join(HERE, 'bnb_convergence.png')
    fig.savefig(out_pdf, bbox_inches='tight')
    fig.savefig(out_png, bbox_inches='tight', dpi=150)
    print(f'wrote {out_pdf}')
    print(f'wrote {out_png}')


if __name__ == '__main__':
    main()
