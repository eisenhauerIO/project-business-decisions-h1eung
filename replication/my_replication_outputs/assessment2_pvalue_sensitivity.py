#!/usr/bin/env python3
"""
Assessment 2 Analysis: Sensitivity of P-values to Tie-Breaking
===============================================================
Computes rejection rates and spread statistics from Tables 12 and 13
(already replicated in empirical_application/Table12.txt and Table13.txt).

No new simulation is required. All p-values are read directly from the
replicated outputs. Runtime: < 1 second.

Run from: replication/my_replication_outputs/
  python assessment2_pvalue_sensitivity.py

Output: assessment2_pvalue_sensitivity.txt  (same directory)
"""

import numpy as np
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FILE   = os.path.join(SCRIPT_DIR, 'assessment2_pvalue_sensitivity.txt')

# ---------------------------------------------------------------------------
# P-values extracted verbatim from replicated Tables 12 and 13.
# Each row = one q value; each column = one random tie-breaking seed (1..10).
# ---------------------------------------------------------------------------

# Table 12: testing Y_alpha =_d Y_beta  (knife = fork)
knife_fork = {
    5:  [0.89, 0.44, 1.00, 1.00, 1.00, 1.00, 0.52, 0.53, 0.90, 1.00],
    10: [1.00, 0.60, 0.48, 1.00, 0.60, 0.35, 0.10, 1.00, 0.86, 0.44],
    20: [0.44, 0.99, 1.00, 0.30, 0.87, 0.01, 0.37, 0.81, 0.86, 0.28],
}

# Table 13: testing Y_beta =_d Y_gamma  (fork = spoon)
fork_spoon = {
    5:  [0.56, 0.16, 1.00, 0.16, 1.00, 0.88, 0.92, 0.02, 1.00, 0.03],
    10: [0.12, 0.06, 0.15, 0.02, 0.70, 0.02, 0.10, 0.03, 0.09, 0.02],
    20: [0.01, 0.03, 0.01, 0.00, 0.02, 0.09, 0.04, 0.01, 0.03, 0.00],
}

# Headline p-values (degree-based tie-breaking, approx_perm_rank_degree)
headline = {
    'knife_fork': {5: 1.000, 10: 1.000, 20: 0.152},
    'fork_spoon': {5: 0.062, 10: 0.007, 20: 0.074},
}

ALPHAS = [0.05, 0.10]

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyze(label, pval_dict, alpha_list):
    rows = []
    for q in sorted(pval_dict):
        pvals = np.array(pval_dict[q])
        n = len(pvals)
        row = {
            'q': q,
            'n': n,
            'min': float(np.min(pvals)),
            'max': float(np.max(pvals)),
            'mean': float(np.mean(pvals)),
            'std': float(np.std(pvals)),
            'pvals': pvals,
        }
        for alpha in alpha_list:
            row[f'rej_{alpha}'] = int(np.sum(pvals < alpha))
            row[f'rej_pct_{alpha}'] = 100.0 * row[f'rej_{alpha}'] / n
        rows.append(row)
    return rows


lines = []

lines.append("=" * 72)
lines.append("ASSESSMENT 2: SENSITIVITY OF P-VALUES TO TIE-BREAKING")
lines.append("Auerbach, Guo, Tabord-Meehan (2026) — Empirical Application")
lines.append("=" * 72)
lines.append("")
lines.append("Source: Tables 12 and 13 (replicated at empirical_application/)")
lines.append("        10 random tie-breaking seeds × 3 q values × 2 tests")
lines.append("")

for label, pval_dict, hl_key in [
        ("TEST 1: knife = fork  (H0: Y_alpha =_d Y_beta)", knife_fork, 'knife_fork'),
        ("TEST 2: fork  = spoon (H0: Y_beta  =_d Y_gamma)", fork_spoon, 'fork_spoon')]:

    lines.append("─" * 72)
    lines.append(label)
    lines.append("─" * 72)
    lines.append("")
    lines.append(f"  {'q':<5}  {'Headline':>10}  {'Min':>7}  {'Max':>7}  "
                 f"{'Mean':>7}  {'Std':>7}  {'Rej α=0.05':>12}  {'Rej α=0.10':>12}")
    lines.append("  " + "-"*70)

    rows = analyze(label, pval_dict, ALPHAS)
    for row in rows:
        q = row['q']
        hl = headline[hl_key][q]
        lines.append(
            f"  {q:<5}  {hl:>10.3f}  {row['min']:>7.3f}  {row['max']:>7.3f}  "
            f"{row['mean']:>7.3f}  {row['std']:>7.3f}  "
            f"{row['rej_0.05']:>3}/{row['n']} ({row['rej_pct_0.05']:4.0f}%)  "
            f"{row['rej_0.1']:>3}/{row['n']} ({row['rej_pct_0.1']:4.0f}%)"
        )

    lines.append("")
    lines.append(f"  Individual p-values across 10 seeds:")
    for row in rows:
        pstr = "  ".join(f"{p:.2f}" for p in row['pvals'])
        lines.append(f"    q={row['q']:2d}: {pstr}")
    lines.append("")

lines.append("─" * 72)
lines.append("SUMMARY OF KEY FINDINGS")
lines.append("─" * 72)
lines.append("")

# knife=fork q=20 spread
kf20 = np.array(knife_fork[20])
lines.append(f"  knife=fork, q=20:")
lines.append(f"    Range of p-values:  [{kf20.min():.3f}, {kf20.max():.3f}]")
lines.append(f"    Headline p-value:   {headline['knife_fork'][20]:.3f} (degree-based ranking)")
lines.append(f"    Seeds with p<0.05:  {np.sum(kf20 < 0.05)}/10")
lines.append(f"    Seeds with p<0.10:  {np.sum(kf20 < 0.10)}/10")
lines.append(f"    Interpretation: one seed gives p=0.01 (would reject H0),")
lines.append(f"                    nine seeds give p>=0.28 (would not reject H0).")
lines.append("")

# fork=spoon q=10 spread (headline claim)
fs10 = np.array(fork_spoon[10])
lines.append(f"  fork=spoon, q=10  [headline p-value = {headline['fork_spoon'][10]:.3f}]:")
lines.append(f"    Range of p-values:  [{fs10.min():.3f}, {fs10.max():.3f}]")
lines.append(f"    Seeds with p<0.05:  {np.sum(fs10 < 0.05)}/10")
lines.append(f"    Seeds with p<0.10:  {np.sum(fs10 < 0.10)}/10")
lines.append(f"    Interpretation: the headline p=0.007 is an extreme outcome;")
lines.append(f"                    {np.sum(fs10 >= 0.05)}/10 seeds fail to reject at alpha=0.05.")
lines.append("")

# fork=spoon across all q
lines.append(f"  fork=spoon across all q (headline p = 0.062, 0.007, 0.074):")
for q in [5, 10, 20]:
    pv = np.array(fork_spoon[q])
    lines.append(f"    q={q:2d}: rej rate at alpha=0.05 = {np.sum(pv < 0.05)}/10 = "
                 f"{100*np.sum(pv<0.05)/10:.0f}%;  "
                 f"alpha=0.10 = {np.sum(pv < 0.10)}/10 = "
                 f"{100*np.sum(pv<0.10)/10:.0f}%")
lines.append("")

lines.append("=" * 72)

output = "\n".join(lines)
print(output)

with open(OUT_FILE, 'w') as f:
    f.write(output + "\n")

print(f"\nSaved to: {OUT_FILE}")
