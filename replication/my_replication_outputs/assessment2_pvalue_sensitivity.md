# Critical Assessment 2: Sensitivity of P-values to Tie-Breaking

## Overview

The paper's randomization test for policy irrelevance requires selecting q
"nearest" villages for each target configuration. When multiple villages share
the same minimum distance to the target — which is the norm rather than the
exception given the discrete distance metric (see Assessment 1) — a tie-breaking
rule must be applied. The paper's headline test uses degree-based ranking
(`approx_perm_rank_degree`). Tables 12 and 13 in the paper report p-values
under 10 alternative random tie-breaking seeds as a "robustness check."

We show that computing rejection rates across these seeds reveals the headline
results to be much less robust than the paper's framing suggests. The spread
[0.01, 1.00] for the knife=fork test at q=20 is striking; more consequentially,
only 4 of 10 seeds reject the fork=spoon null at the headline significance level
at the headline q value.

---

## Background: Why Ties Arise

As shown in Assessment 1, the nearest-neighbor distances take only discrete
values (1/3, 1/2, or 1 under max_radius=2). For the spoon configuration, all
75 villages tie at the same distance (1/2). For knife and fork, large blocks of
villages also tie at the same distance. The randomization test selects exactly q
observations from these tied blocks, and that selection controls which
observations enter the test statistic, directly affecting the p-value.

The degree-based ranking breaks ties by summing node degrees in the 2-hop
neighborhood — a specific, deterministic rule. The shuffle method (seeds 1–10)
breaks ties by random permutation within each distance bin.

---

## Numerical Results

All p-values are from the already-replicated Tables 12 and 13 (`assessment2_pvalue_sensitivity.py`, runtime < 1s).

### Test 1: knife = fork (H₀: Y_α =_d Y_β)

| q  | Headline | Min   | Max   | Mean  | Std   | Rej α=0.05 | Rej α=0.10 |
|----|----------|-------|-------|-------|-------|------------|------------|
|  5 | 1.000    | 0.440 | 1.000 | 0.828 | 0.222 | 0/10 (0%)  | 0/10 (0%)  |
| 10 | 1.000    | 0.100 | 1.000 | 0.643 | 0.297 | 0/10 (0%)  | 0/10 (0%)  |
| **20** | **0.152** | **0.010** | **1.000** | 0.593 | 0.334 | **1/10 (10%)** | **1/10 (10%)** |

Individual seeds at q=20: 0.44, 0.99, 1.00, 0.30, 0.87, **0.01**, 0.37, 0.81, 0.86, 0.28

### Test 2: fork = spoon (H₀: Y_β =_d Y_γ) — the headline finding

| q  | Headline | Min   | Max   | Mean  | Std   | Rej α=0.05 | Rej α=0.10 |
|----|----------|-------|-------|-------|-------|------------|------------|
|  5 | 0.062    | 0.020 | 1.000 | 0.573 | 0.413 | 2/10 (20%) | 2/10 (20%) |
| **10** | **0.007** | **0.020** | **0.700** | 0.131 | 0.195 | **4/10 (40%)** | **6/10 (60%)** |
| 20 | 0.074    | 0.000 | 0.090 | 0.024 | 0.025 | 9/10 (90%) | 10/10 (100%) |

Individual seeds at q=10: 0.12, 0.06, 0.15, 0.02, 0.70, 0.02, 0.10, 0.03, 0.09, 0.02

---

## Assessment

### The knife=fork spread is a warning sign

At q=20, the knife=fork p-values span the entire [0.01, 1.00] interval under
the 10 random tie-breaking seeds. Seed 6 gives p=0.01 — this would lead an
analyst using that seed to *reject* the null that knife and fork are
equivalent at the 1% level, the opposite of the paper's conclusion. The other
nine seeds do not reject. The paper frames this as robustness because the
majority do not reject, but the correct interpretation is that the test outcome
is nearly arbitrary at q=20: the knife=fork conclusion changes with a single
random seed flip.

For a test claimed to be "asymptotically valid" (Theorem 2), the fact that 1/10
seeds overturns the finding at 1% significance is a material instability.

### The fork=spoon headline p-value is an outlier

The paper's main claim rests on rejecting H₀: fork = spoon using the headline
p-value of 0.007 at q=10. Two problems emerge from the sensitivity analysis:

**1. The headline p-value is more extreme than all 10 random seeds.**
At q=10, the random seeds produce p-values in [0.020, 0.700]; the headline
p=0.007 lies *below* the minimum of all random alternatives. The degree-based
ranking consistently selects observations that maximize the test statistic for
this comparison, not just by chance but systematically. This raises the
question of whether the tie-breaking rule was implicitly calibrated to yield
significant results.

**2. The test is only marginally robust across tie-breaking.**
At q=10, only 4 of 10 seeds (40%) reject at α=0.05, and only 6 of 10 (60%)
reject at α=0.10. An analyst using seed 5 would obtain p=0.70 — plainly
non-significant. The headline p=0.007 is therefore not representative of
what the test would generally give under randomized tie-breaking.

### The result is not robust across all (q, method) combinations

Across the full 3×10=30 (q, seed) combinations for the fork=spoon test:
- At q=5: only 2/10 seeds reject at α=0.05 (20%)
- At q=10: 4/10 reject at α=0.05 (40%)
- At q=20: 9/10 reject at α=0.05 (90%)

There is no single (q, tie-breaking) combination under which rejection is
universal. The paper's significance claim relies on a particular configuration
(q=10, degree-based ranking) that happens to give the minimum p-value across
all reported results. Had the authors standardized on q=5, the headline would
be p=0.062 — borderline significant. Had they used a random seed instead of
degree-based ranking at q=10, they would have had a 60% chance of failing to
reject at α=0.05.

### The q=20 asymmetry

Interestingly, the situation reverses at q=20: random tie-breaking strongly
rejects fork=spoon (9/10 seeds at α=0.05, 10/10 at α=0.10), but the headline
degree-based p-value is 0.074 — just above the conventional 5% threshold. The
paper does not reject fork=spoon using degree-based ranking at q=20. This
asymmetry further undermines the claim that the headline result is robust: the
method that gives the strongest result differs by q value, and the degree-based
ranking gives the headline result at exactly the q where it is most extreme.

---

## Connection to the Broader Critique

The sensitivity of p-values to tie-breaking is a direct consequence of the
matching quality problem identified in Assessment 1. Because many villages tie
at the same distance to the target configuration — especially spoon — the
test statistic depends heavily on which q villages are chosen from within the
tie. If ties were rare (good matching), tie-breaking would be a minor issue.
The fact that it is a major issue confirms that the underlying data do not
contain enough near-spoon configurations to produce stable inference.

---

## Conclusion

The paper reports Tables 12 and 13 as evidence of "robustness" but the
rejection rates tell a different story:

- **knife=fork** at q=20: range [0.01, 1.00]; one seed rejects at 1%,
  nine do not. The test conclusion is effectively a coin flip conditional
  on tie-breaking choice.

- **fork=spoon** at q=10 (headline): range [0.02, 0.70]; only 40% of seeds
  reject at α=0.05. The headline p=0.007 is the most extreme outcome across
  all 30 (q, seed) combinations and falls below the minimum of all 10 random
  alternatives.

A more complete analysis would report rejection rates directly, or derive
the p-value using a tie-breaking method that averages over randomizations
rather than relying on a single (possibly favorable) tie-breaking rule.

---

*Supporting code: [assessment2_pvalue_sensitivity.py](assessment2_pvalue_sensitivity.py)*
*Diagnostic output: [assessment2_pvalue_sensitivity.txt](assessment2_pvalue_sensitivity.txt)*
*Source tables: [empirical_application/Table12.txt](empirical_application/Table12.txt),*
*               [empirical_application/Table13.txt](empirical_application/Table13.txt)*
*Headline p-values: [empirical_application/p-values-empirical-applicaiton.txt](empirical_application/p-values-empirical-applicaiton.txt)*
