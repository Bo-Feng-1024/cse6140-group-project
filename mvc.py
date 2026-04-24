"""Minimum Vertex Cover — main entry point.

Usage:
    python3 mvc.py -inst <instance> -alg [BnB|Approx|LS1|LS2] -time <cutoff> -seed <seed>

Example:
    python3 mvc.py -inst data/test/test1 -alg BnB -time 10 -seed 1
"""

import argparse
import sys

from graph import read_graph
from utils import write_solution, write_trace
from bnb import branch_and_bound
from approx import approx_vertex_cover
from ls1 import local_search_1
from ls2 import local_search_2


def parse_args():
    parser = argparse.ArgumentParser(description='Minimum Vertex Cover Solver')
    parser.add_argument('-inst', required=True, help='Instance path (without .in extension)')
    parser.add_argument('-alg', required=True, choices=['BnB', 'Approx', 'LS1', 'LS2'],
                        help='Algorithm: BnB, Approx, LS1, or LS2')
    parser.add_argument('-time', type=int, required=True, help='Cutoff time in seconds')
    parser.add_argument('-seed', type=int, required=True, help='Random seed')
    return parser.parse_args()


def main():
    args = parse_args()
    inst = args.inst
    alg = args.alg
    cutoff = args.time
    seed = args.seed

    graph = read_graph(inst)

    if alg == 'BnB':
        cover, trace = branch_and_bound(graph, cutoff)
    elif alg == 'Approx':
        cover, trace = approx_vertex_cover(graph, cutoff)
    elif alg == 'LS1':
        cover, trace = local_search_1(graph, cutoff, seed)
    elif alg == 'LS2':
        cover, trace = local_search_2(graph, cutoff, seed)
    else:
        print(f"Unknown algorithm: {alg}", file=sys.stderr)
        sys.exit(1)

    write_solution(inst, alg, cutoff, seed, cover)
    if alg != 'Approx':
        write_trace(inst, alg, cutoff, seed, trace)


if __name__ == '__main__':
    main()
