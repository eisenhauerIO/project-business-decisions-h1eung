# Critical Assessment 1: Matching Quality and the ψ_g Problem

## Overview

The paper's headline empirical finding — that moving from a fork to a spoon
configuration raises favor exchange (E[Y_γ] − E[Y_β] > 0) — is the result the
authors use to challenge the prior conclusion of Jackson et al. (2012) that
*support*, not clustering, drives favor exchange. We argue that this specific
result rests on the weakest — and in fact completely degenerate — matching
quality in the entire analysis, and that the paper's own Figure 12 reveals this
without the authors drawing the implication.

---

## Background: How the KNN Estimator Works

The paper estimates the Average Structural Function (ASF) h(g) = E[Y | local
config = g] using a k-nearest-neighbor (KNN) approach (Section 3.1, implemented
in `EST_CI_ave`). For each of the 75 villages, the estimator:

1. Finds all nodes whose 2-hop rooted subgraph has the minimum distance to
   the target configuration g (knife, fork, or spoon).
2. Records the mean favor-exchange outcome of those nodes as the village's
   "observation" for g.
3. Averages the k closest such observations across villages to estimate h(g).

The distance metric `r_network_distance` measures how deeply two rooted
networks agree. With the estimation setup (`max_radius = 2`):

| Distance | Interpretation |
|----------|----------------|
| 1/3 ≈ 0.333 | **Perfect match**: identical 2-hop structure |
| 1/2 = 0.500 | Agrees only at depth 0 (same root degree, different neighborhood structure) |
| 1   = 1.000 | No structural match even at depth 0 |

The parameter ψ_g(x) is the fraction of villages with nearest-neighbor distance
≤ x. Figure 12 plots this for all three configurations; Theorem 1's MSE bound
depends on it.

---

## Evidence: The Spoon Has Zero Exact Matches

We computed the nearest-neighbor distance from each of the 75 villages to each
target configuration using the same data, target generation (seed=0), and
distance function as the paper (`assessment1_matching_quality.py`). Under the
Table 2 estimation setup (`max_radius = 2`):

**Distance distribution across 75 villages:**

| Configuration | dist=1/3 (perfect) | dist=1/2 (depth-0 only) | dist=1 (no match) |
|--------------|-------------------|--------------------------|-------------------|
| Knife (α)    | 5/75  (6.7%)      | 70/75 (93.3%)            | 0/75  (0.0%)      |
| Fork  (β)    | **15/75 (20.0%)** | 60/75 (80.0%)            | 0/75  (0.0%)      |
| **Spoon (γ)**| **0/75  (0.0%)**  | 73/75 (97.3%)            | **2/75 (2.7%)**   |

**k-th nearest-neighbor distance (the quality of the k-th best match used in Table 2):**

| k  | Knife    | Fork     | Spoon    |
|----|----------|----------|----------|
|  5 | **1/3**  | **1/3**  | 1/2      |
| 10 | 1/2      | **1/3**  | 1/2      |
| 20 | 1/2      | 1/2      | 1/2      |
| 30 | 1/2      | 1/2      | 1/2      |

*Source: `assessment1_matching_quality.py`, runtime ~570 seconds.*

**The spoon configuration has zero perfect matches across all 75 villages and
across both estimation setups (max_radius=2 and max_radius=3).** Every
nearest-neighbor match for spoon is at distance 1/2 (or worse), meaning the
matched node shares only root degree with spoon but not its defining triangular
substructure. Two villages produce no match even at root degree level (distance=1).

---

## The Deeper Problem: Tie-Breaking Determines the Spoon Estimate

Since all 75 villages tie at the same minimum distance (1/2) for the spoon
configuration, the selection of which k villages constitute the "k nearest
neighbors" is entirely determined by tie-breaking — not by any structural
similarity to spoon. In `EST_CI_ave`, the tie is broken by numpy's `argsort`,
which uses a stable sort and therefore defaults to the **original loading order**
of the villages (village 1, 2, ..., k).

This means the spoon KNN estimate at k=10, 20, 30 is simply the average
outcome over the first k villages in loading order among nodes with the same
root degree as spoon. **The triangular clustering structure that defines the
spoon — and the paper's entire motivation for comparing fork to spoon — plays
no role whatsoever in selecting the matched observations.**

The fork estimate does not suffer from this problem: 15 of 75 villages have
exact matches (distance=1/3) for fork, so at k=5 and k=10 the selected
observations are genuinely structurally similar to fork.

---

## Theoretical Connection: Theorem 1 and Assumption 3

The paper's Theorem 1 bounds the MSE of the KNN estimator as a function of
ψ_g (the match quality distribution). The bias component of the bound grows
with the distance of the k-th nearest neighbor: a match at distance 1/2
contributes O((1/2)^α) bias, where α is the smoothness parameter in Assumption
3 (Approximate Sparsity). For the spoon at any k:

- All matches are at distance ≥ 1/2 → the bias bound includes a constant
  O((1/2)^α) term that does not decrease with k.

Assumption 3 requires that nearby configurations (in the ψ_g metric) have
similar potential outcomes. When the nearest match for spoon is always a
node that merely shares root degree — regardless of whether it has a triangle
— there is no reason to believe the outcomes are close to the true E[Y | spoon].
The assumption may be satisfied in a formal sense (the paper proves it holds
under regularity conditions), but its empirical content is vacuous here: the
estimator never conditions on the feature (clustering) that distinguishes spoon
from fork.

---

## The Trending Pattern in Table 2 as a Symptom

Table 2 reports the fork→spoon estimate across k values: 0.62 (k=10), 0.69
(k=20), 0.74 (k=30). This monotone increase is a direct consequence of the
degeneracy above:

- At k=10: average over the 10 "closest" villages (first 10 in loading order,
  after tie-breaking), among nodes with the same root degree as spoon.
- At k=20: average over the first 20 villages.
- At k=30: average over the first 30 villages.

Adding more villages to the average changes the estimate not because the
matching improves, but because the sample is expanding in an arbitrary order.
An estimate that is genuinely converging to a well-defined target should
stabilize as k grows; a monotone increase of 0.12 from k=10 to k=30 suggests
no convergence.

By contrast, the knife→fork estimate *decreases* (0.24 → 0.11 → 0.07) as k
grows, which reflects the progressive inclusion of lower-quality (distance=1/2)
knife matches once the 5 exact (distance=1/3) matches are exhausted. This is
how a well-behaved KNN estimator is expected to trend: estimates are driven
toward a common limit as match quality degrades uniformly. The spoon trend is
qualitatively different.

*(Assessment 3 addresses the choice of k in more detail.)*

---

## Conclusion

The fork → spoon comparison — the paper's most significant empirical finding —
is built on a fundamentally degenerate matching procedure:

1. **Zero exact matches**: Not a single one of 75 villages contains a node
   whose 2-hop rooted neighborhood is isomorphic to the spoon configuration.
   (Knife: 5 exact matches, 6.7%. Fork: 15 exact matches, 20.0%. Spoon: 0.)

2. **Arbitrary village selection**: Since all 75 villages tie at the same
   distance for spoon, the "k nearest neighbors" are selected by numpy's
   stable sort tie-breaking, not by structural proximity to spoon. The
   triangular feature that defines spoon plays no role in choosing observations.

3. **No convergence**: The monotone increase in the fork→spoon estimate
   (0.62 → 0.69 → 0.74 as k grows) is consistent with sampling variation
   across arbitrarily ordered villages, not convergence to a structural target.

The paper reports Figure 12 as a matching quality diagnostic — and Figure 12
does show that spoon has no mass at zero (no perfect matches) while knife and
fork do. But the authors do not discuss the implication: the estimator for the
spoon ASF is not identifying the spoon structural function at all. It is
identifying a coarser conditional mean (average favor exchange conditional on
root degree, not on the full triangular configuration), which is insufficient
to support the claim that clustering — as opposed to support — drives favor
exchange in these villages.

A complete analysis would need to either demonstrate that enough villages
contain near-spoon configurations to make the KNN estimate credible, or
acknowledge that the comparison is underpowered by the absence of good
spoon matches and widen the confidence intervals accordingly.

---

*Supporting code: [assessment1_matching_quality.py](assessment1_matching_quality.py)*
*Diagnostic output: [assessment1_matching_quality.txt](assessment1_matching_quality.txt)*
*Related figures: [empirical_application/Figure12.eps](empirical_application/Figure12.eps)*
*Related tables: [empirical_application/Table2.txt](empirical_application/Table2.txt)*
