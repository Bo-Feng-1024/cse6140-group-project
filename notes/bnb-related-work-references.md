# BnB-Relevant MVC Reading List

Curated by Bo Feng (BnB algorithm owner) for Congyan to integrate into the
**Related Work** section of the report. Each entry has a one-line role,
the lower-bound / branching idea it contributes, and a BibTeX-friendly
citation key matching what I will add (or have added) to
`report/references.bib`.

---

## Foundational results

1. **Karp 1972 — "Reducibility Among Combinatorial Problems"**
   `karp1972reducibility` (already in `references.bib`)
   *Establishes that Vertex Cover is NP-complete via reduction from SAT.
   The reason an exact branch-and-bound is needed at all.*

2. **Nemhauser, Trotter 1975 — "Vertex packings: structural properties and algorithms"**
   `nemhauser1975vertex` (added to `references.bib`)
   *Proves the LP relaxation of MVC is half-integral and the
   {0, 1/2, 1}-valued LP solution induces the **NT kernel**: every
   v with x*=1 lies in some optimal cover, every v with x*=0 lies
   outside one. This is the LP-relaxation lower bound and
   kernelization that our BnB uses at the root via Hopcroft-Karp on
   the bipartite double cover.*

3. **Hochbaum 1982 — "Approximation algorithms for the set covering and vertex cover problems"**
   `hochbaum1982approximation`
   *Shows how to compute the half-integral LP solution in
   polynomial time through bipartite matching, making
   Nemhauser-Trotter practical. Pairs with Konig's theorem.*

4. **Hopcroft, Karp 1973 — "An n^{5/2} algorithm for maximum matchings in bipartite graphs"**
   `hopcroft1973n52`
   *The matching subroutine our LP lower bound is built on:
   O(E sqrt(V)) max bipartite matching.*

## Reductions / FPT

5. **Niedermeier 2006 — "Invitation to Fixed-Parameter Algorithms" (book)**
   `niedermeier2006invitation`
   *Comprehensive treatment of degree-1, degree-2, crown, and
   LP-based reductions for VC. Our BnB implements the degree-1 and
   degree-2 (triangle case) reductions from this book.*

6. **Akiba, Iwata 2016 — "Branch-and-reduce exponential/FPT algorithms in practice: A case study of vertex cover"**
   `akiba2016branchreduce`
   *Modern engineering of BnB-with-reductions for VC: lists every
   reduction that earns its keep in practice. State-of-the-art for
   exact VC on real-world graphs as of mid-2010s.*

## Modern exact / heuristic frontier

7. **Cai, Su, Luo, Sattar 2013 — "NuMVC: an efficient local search algorithm for minimum vertex cover" (J. AI Research)**
   `cai2013numvc`
   *Configuration checking + edge-weighting local search; the LS
   baseline most modern MVC papers compare against. Useful context
   for the LS1 / LS2 sections.*

8. **Cai 2015 — "Balance between complexity and quality: local search for minimum vertex cover in massive graphs" (FastVC)**
   `cai2015fastvc`
   *Massive-scale variant of NuMVC. Demonstrates how careful
   neighborhood structures scale local search to graphs with
   millions of edges.*

9. **Hespe, Lamm, Schorr, Strash, Schulz 2020 / "WeGotYouCovered" (DIMACS PACE 2019 winner)**
   `hespe2020wegotyoucovered`
   *Combines kernelization, branch-and-reduce, and reduction stacks
   for the PACE Vertex Cover challenge. Currently the strongest
   exact MVC solver for sparse benchmarks; the natural state-of-the-art
   to cite as the upper end of what BnB engineering can deliver.*

---

## How this fits into Section 3 (Related Work)

A coherent narrative for Related Work could be:

- **Theory**: NP-completeness (Karp), 2-approximation guarantee (Bar-Yehuda
  & Even / matching-based), LP half-integrality (Nemhauser-Trotter),
  inapproximability (Dinur-Safra; Khot-Regev — could add if you want).
- **Engineering exact solvers**: Niedermeier's reduction toolkit,
  Akiba-Iwata branch-and-reduce, WeGotYouCovered as DIMACS-grade SOTA.
- **Heuristics**: NuMVC / FastVC for large-scale local search.

Citations 2, 3, 5, 6, 9 are the most relevant for explaining
*why our BnB is structured the way it is*. Citations 7-8 are for
LS1 / LS2 framing.

I have already added entries 2, 3, 4, 5, 6, 9 to `references.bib` so they
can be cited via `\cite{key}` directly. If you want any others, ping me
and I can grab the BibTeX.
