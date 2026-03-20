# Critical Assessment 3: Choice of k and q

## Overview

The paper reports estimates for k = 10, 20, 30 (Table 2) and p-values for
q = 5, 10, 20. Both choices are explicitly acknowledged as ad hoc: "we report
results for several values of k" and the parameter q controls how many
observations enter the permutation test. The critique is not that these
parameters are unjustified per se — the paper is transparent about this — but
that the resulting estimates do not stabilize across k, and the significant
result for fork=spoon is present at only one of three q values. In combination
with the degenerate matching identified in Assessment 1, the non-convergence is
diagnostic rather than incidental.

---

## Part A: Non-Convergence of Estimates Across k

### The trending pattern in Table 2

The KNN estimator is expected to exhibit a bias-variance tradeoff as k
increases: small k gives low bias but high variance; large k reduces variance
but accepts more bias from lower-quality matches. In equilibrium, estimates
should stabilize (reach a plateau) as k grows. The data show the opposite:

**knife → fork (E[Y_β] − E[Y_α]):**

| k  | Estimate | 95% CI           | 90% CI           |
|----|----------|------------------|------------------|
| 10 | 0.24     | [−0.35, 0.82]    | [−0.25, 0.73]    |
| 20 | 0.11     | [−0.20, 0.43]    | [−0.15, 0.38]    |
| 30 | **0.07** | [−0.15, **0.29**]| [−0.12, 0.26]    |

**fork → spoon (E[Y_γ] − E[Y_β]):**

| k  | Estimate | 95% CI           | 90% CI           |
|----|----------|------------------|------------------|
| 10 | 0.62     | [0.21, 1.03]     | [0.27, 0.96]     |
| 20 | 0.69     | [0.44, 0.95]     | [0.48, 0.91]     |
| 30 | **0.74** | [**0.55**, 0.94] | [0.58, 0.91]     |

Both estimates are monotone across the entire reported k range — no sign of
plateau. Convergence diagnostics (`assessment3_k_q_choice.py`):

| Comparison   | Estimate shift (k=10→30) | % of k=10 estimate | Shift as % of CI width at k=30 | Direction |
|--------------|--------------------------|--------------------|---------------------------------|-----------|
| knife→fork   | 0.17                     | 71%                | 39%                             | decrease  |
| fork→spoon   | 0.12                     | 19%                | 31%                             | increase  |

For the fork→spoon comparison, the point estimate at k=30 (0.74) is 19% larger
than at k=10 (0.62). The shift of 0.12 is 31% of the final CI width (0.39),
meaning the estimate has moved by nearly a third of its own confidence band
over the reported k range. For knife→fork, the estimate falls by 71% of its
initial value. Neither sequence has settled.

### Why the trends are informative

The monotone trends have a specific interpretation given Assessment 1's
findings. For the spoon configuration, all 75 villages match at the same
distance (1/2 under max_radius=2): there is no hierarchy of match quality.
Adding more k beyond any level does not introduce better or worse matches — it
just adds more villages in tie-breaking order. The estimate increases from
0.62 to 0.74 purely because later villages in the loading-order tie-break
happen to have higher mean outcomes for nodes with the same root degree as
spoon. This is sampling variation from an arbitrary ordering, not evidence
that the estimator is converging to a well-defined limit.

For knife→fork, the decline from 0.24 to 0.07 reflects the dilution of the
5 exact-match villages (distance=1/3) by 65 lower-quality villages
(distance=1/2). As k increases, the exact matches are outnumbered and the
estimate gravitates toward the average outcome for nodes matching at distance
1/2 only. Whether this constitutes "convergence" depends on whether the
distance-1/2 matches are informative for knife neighborhoods; Assessment 1
suggests they are not.

### Implication for inference

The confidence intervals in Table 2 are derived from CLT asymptotics (normal
approximation) assuming the matched outcomes are approximately i.i.d. samples
from the structural function h(g). If the estimator has not converged to h(g)
— because matches are uninformative — the CI is narrowing around the wrong
center. The fork→spoon 95% CI tightens from [0.21, 1.03] at k=10 to
[0.55, 0.94] at k=30, but the center is moving (0.62 → 0.74). The CI at k=30
excludes the center at k=10 from its own confidence band: 0.62 < 0.55. This
is inconsistent with convergence to a stable limit.

---

## Part B: Sensitivity of Significance to q

### The p-values by q value

| q  | p(knife=fork) | Sig @5% | Sig @10% | p(fork=spoon) | Sig @5% | Sig @10% |
|----|---------------|---------|----------|---------------|---------|----------|
|  5 | 1.000         | no      | no       | 0.062         | no      | **YES**  |
| **10** | **1.000** | no  | no       | **0.007**     | **YES** | **YES**  |
| 20 | 0.152         | no      | no       | 0.074         | no      | **YES**  |

**fork=spoon significant at α=0.05: 1/3 q values (q=10 only)**
**fork=spoon significant at α=0.10: 3/3 q values**

The fork=spoon result passes the conventional 5% threshold at only one of the
three q values the paper reports. At q=5 (p=0.062) and q=20 (p=0.074), the
result is borderline and would not be reported as significant under a strict
5% threshold. The paper's headline claim — that clustering matters for favor
exchange — is supported at 5% by a single (q=10) configuration.

### Multiple comparisons

The paper reports results for three q values without adjusting for the fact
that three tests are being conducted. Under a Bonferroni correction for 3
simultaneous tests, the adjusted threshold for 5% family-wise error rate is
5%/3 ≈ 1.7%. The fork=spoon p-value at q=10 (0.007) passes this threshold,
but the combined evidence from all three q values — two of which do not reject
— is weaker than the headline implies.

A pre-registered commitment to a single q before seeing the results would have
had a 2/3 probability (q=5 or q=20) of not delivering a significant fork=spoon
result at 5%. The fact that q is reported as an "ad hoc" choice, combined with
the post-hoc presentation of all three q values, creates a multiple comparisons
concern that the paper does not address.

---

## Part C: The CI–Test Discrepancy

The paper uses two separate inference procedures:
- **Table 2 (CLT-based CI):** Tests whether E[Y_γ] − E[Y_β] ≠ 0.
- **Permutation test (p-values):** Tests whether the *distributions* Y_β and
  Y_γ are equal (Y_β =_d Y_γ).

These test different hypotheses. The 95% CIs exclude zero at **all three k
values** (lower bounds 0.21, 0.44, 0.55 at k=10, 20, 30). The permutation
test rejects distributional equality at **only one of three q values** (q=10).

A natural consistency check is whether both procedures agree across their
respective parameter sweeps. They do not: the CI-based evidence is uniformly
positive, while the permutation-test evidence is present at only q=10. This
divergence suggests at least one of the two procedures is unreliable. Given
Assessment 1's finding that the spoon matches are degenerate, the most likely
explanation is that both are measuring an ill-defined quantity — but the
permutation test, which directly compares distributions rather than just means,
is less forgiving of the matching degeneracy.

---

## Conclusion

Three concrete findings emerge from the analysis of k and q choices:

1. **Non-convergence across k**: The fork→spoon estimate rises monotonically
   from 0.62 (k=10) to 0.74 (k=30), a shift of 31% of the k=30 CI width.
   The knife→fork estimate falls by 71% of its initial value. Neither estimate
   shows any sign of stabilizing within the reported range, which is expected
   given the degenerate spoon matching identified in Assessment 1.

2. **Q-sensitivity**: The fork=spoon result is significant at α=0.05 for only
   1 of 3 q values (q=10). The paper presents this as the headline finding
   without acknowledging the multiple comparison concern: under a Bonferroni
   correction, or under a pre-registered q, the result at q=5 or q=20 would
   be borderline or non-significant.

3. **CI–permutation test inconsistency**: The CLT CIs exclude zero for all k,
   but the permutation test rejects for only one of three q values. Two
   inference procedures designed to test related hypotheses give inconsistent
   evidence across their respective parameter sweeps.

These concerns are partially acknowledged by the authors ("ad hoc" choices),
but the acknowledgment does not resolve them. A complete analysis would require
either a principled model-selection criterion for k and q (e.g.,
cross-validation), a pre-registration commitment to specific values, or a
formal multiple-testing correction across the nine (k, q) combinations
reported.

---

*Supporting code: [assessment3_k_q_choice.py](assessment3_k_q_choice.py)*
*Diagnostic output: [assessment3_k_q_choice.txt](assessment3_k_q_choice.txt)*
*Source tables: [empirical_application/Table2.txt](empirical_application/Table2.txt)*
*Source p-values: [empirical_application/p-values-empirical-applicaiton.txt](empirical_application/p-values-empirical-applicaiton.txt)*
