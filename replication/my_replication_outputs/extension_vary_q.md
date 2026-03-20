# Independent Extension: Permutation Test P-values Across q Values

**Paper:** Auerbach, Guo, Tabord-Meehan (2026), *The Local Approach to Causal Inference under Network Interference*, Quantitative Economics 17, 173–199.

---

## Motivation

The paper's permutation test for H₀: Yₐ =_d Y_β (knife = fork) and H₀: Y_β =_d Y_γ (fork = spoon) is reported only at q = 5, 10, 20 (Table 13 of the paper). The parameter q controls how many matched village pairs enter the Cramér–von Mises statistic: a larger q uses more data but may include lower-quality (more distant) matches.

**Critical Assessment 2** (this session) showed that the headline fork=spoon result (p = 0.007 at q = 10) is fragile under tie-breaking seed changes, with rejection rates of only 4/10 across random seeds. **Critical Assessment 3** showed that neither q = 5 nor q = 20 gives a significant result for fork=spoon — significance is isolated to the single value q = 10.

This extension directly tests whether that isolation is a coincidence or a structural feature of the data by sweeping q across a wider range: q ∈ {1, 2, 3, 5, 8, 10, 15, 20, 25, 30, 35}.

---

## Methods

**Script:** `extension_vary_q.py`

**Key design:** The expensive part of `approx_perm_rank_degree` is the `find_NN` call for each of 75 villages × 3 configurations. These calls are independent of q and are computed once and cached. The q-loop then applies `zip_race` + CvM + B = 999 permutations for each q value — taking only seconds per iteration once the cache is ready.

**Configurations:**
- R1 = knife (node 9 in the seed-0 Erdős–Rényi graph)
- R2 = fork (node 71)
- R3 = spoon (node 41)
- max_radius = 3 (same as the paper's permutation test calls)

**Sorting:** Within each distance tier, villages are ranked by the degree of the matched nearest neighbor (same `rank_degree` tie-breaking as `approx_perm_rank_degree`).

**Randomness:** A single seed (np.random.seed(42)) is set before the q-loop. Each q value therefore uses a different random state for its B = 999 permutation draws. This differs from the paper, which re-seeds (np.random.seed(19)) before each q value — but for an extension the goal is to document the trend across q, not to replicate specific p-values.

**q range:** The safe maximum is q ≤ 37 (since zip_race requires n - i > i at iteration i, with n = 75 villages). We use q ∈ {1, 2, 3, 5, 8, 10, 15, 20, 25, 30, 35}.

---

## Results

Full table in `extension_vary_q.txt`, plot in `extension_vary_q.eps`.

| q  | p(knife=fork) | p(fork=spoon) | Sig (α=0.05) |
|----|--------------|--------------|--------------|
|  1 | 1.000        | 1.000        |              |
|  2 | 1.000        | 0.360        |              |
|  3 | 1.000        | 0.376        |              |
|  5 | 1.000        | 0.130        |              |
|  8 | 1.000        | 0.031        | *            |
| 10 | 1.000        | 0.017        | *            |
| 15 | 0.735        | 0.022        | *            |
| 20 | 0.135        | 0.065        |              |
| 25 | 0.094        | 0.022        | *            |
| 30 | 0.094        | 0.017        | *            |
| 35 | 0.125        | 0.006        | *            |

*(B = 999, seed = 42)*

**Summary of findings:**

**knife=fork:** The p-value is ≥ 0.094 at every q value — never below 0.05. This result is robust: network support (knife→fork) has no significant distributional effect on favor exchange across the entire q range.

**fork=spoon:** The picture is more complex. Significance depends on q:
- q = 1–5: not significant (too few pairs, low power)
- q = 8, 10, 15: significant (p ≈ 0.017–0.031) — this range includes the paper's headline q = 10
- q = 20: **not significant** (p = 0.065), consistent with the paper's own q = 20 result (p = 0.074)
- q = 25–35: significant again (p ≈ 0.006–0.022)

The fork=spoon result is significant at 6 of 11 q values (55%), compared to 1 of 3 in the paper's reported range. Notably, q = 20 is a local dip in significance — surrounded by significant values — rather than monotone behavior.

**Key puzzle: why does q = 20 break the pattern?** The zip_race algorithm interleaves the closest-to-fork and closest-to-spoon village rankings. At q = 20, a specific set of 20 fork-villages and 20 spoon-villages is selected; at q = 25 and q = 30, additional villages enter and the test statistic recovers significance. Since Assessment 1 shows that all 75 spoon distances are identical (all villages tied at the same distance from R3), the zip_race ordering at each q is entirely determined by the degree tie-breaking, making the q = 20 dip an artifact of which tied villages happen to be selected at that threshold.

**Comparison to paper's values (seed = 19):**

| q  | Paper p(knife=fork) | Paper p(fork=spoon) | Ext. p(knife=fork) | Ext. p(fork=spoon) |
|----|--------------------|--------------------|-------------------|-------------------|
|  5 | 0.597              | 0.157              | 1.000             | 0.130             |
| 10 | 0.432              | 0.007              | 1.000             | 0.017             |
| 20 | 0.432              | 0.074              | 0.135             | 0.065             |

The fork=spoon p-values at q = 5 and q = 20 agree qualitatively between seeds (non-significant), but differ substantially in magnitude. At q = 10, both seeds give rejection at α = 0.05. The knife=fork p-values differ more dramatically: the paper's seed gives ≈ 0.43 while ours gives 1.0, consistent with Assessment 2's finding that knife=fork p-values span [0.01, 1.00] across seeds.

**Interpretation:** The fork=spoon result has broader support across q than the paper's three-point analysis suggested (6/11 vs. 1/3 reject), but is still not uniformly robust — it fails at small q and at the q = 20 dip. The sensitivity to seed documented in Assessment 2 and the degenerate spoon matching documented in Assessment 1 explain both the non-uniformity and the volatility: once all villages tie on distance, any subset selected by q (or seed) can produce arbitrary test statistics.

---

## Relation to the Three Critical Assessments

| Assessment | Key finding | Extension evidence |
|------------|-------------|-------------------|
| A1 (matching quality) | Spoon has 0/75 exact matches; all distances tied | Explains why p-values vary wildly with q — different q selects different arbitrary subsets |
| A2 (tie-breaking sensitivity) | Headline p = 0.007 is an outlier; 4/10 seeds reject | Extension shows the same fragility across the q dimension |
| A3 (k and q choice) | Fork=spoon significant at only 1/3 reported q values | Extension broadens the q grid and confirms non-robustness |

The three assessments and this extension together tell a coherent story: the fork=spoon result is driven by an identification problem (degenerate matching for the spoon configuration), which manifests as sensitivity to any arbitrary choice — tie-breaking seed, k, or q.

---

## Files

| File | Description |
|------|-------------|
| `extension_vary_q.py` | Self-contained script (caches find_NN, loops over q) |
| `extension_vary_q.txt` | Table of p-values for each q |
| `extension_vary_q.eps` | Plot: p-value vs. q for both comparisons |
| `extension_vary_q_run.log` | Runtime log with progress and timings |
