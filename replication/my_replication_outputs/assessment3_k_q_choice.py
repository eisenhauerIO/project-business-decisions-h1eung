#!/usr/bin/env python3
"""
Assessment 3 Analysis: Choice of k and q
=========================================
Organizes data from Table 2 and the p-values file to quantify
(a) non-convergence of estimates across k values, and
(b) sensitivity of significance to the choice of q.

No simulation required. All numbers come from already-replicated outputs.
Runtime: < 1 second.

Run from: replication/my_replication_outputs/
  python3 assessment3_k_q_choice.py

Output: assessment3_k_q_choice.txt
"""

import numpy as np
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FILE   = os.path.join(SCRIPT_DIR, 'assessment3_k_q_choice.txt')

# ---------------------------------------------------------------------------
# Data from replicated Table 2
# Columns: knife->fork (beta-alpha), fork->spoon (gamma-beta)
# ---------------------------------------------------------------------------

table2 = {
    # k: (est_kf, ci95_kf_lb, ci95_kf_ub, ci90_kf_lb, ci90_kf_ub,
    #      est_fs, ci95_fs_lb, ci95_fs_ub, ci90_fs_lb, ci90_fs_ub)
    10: dict(kf_est=0.24, kf_ci95=(-0.35, 0.82), kf_ci90=(-0.25, 0.73),
             fs_est=0.62, fs_ci95=( 0.21, 1.03), fs_ci90=( 0.27, 0.96)),
    20: dict(kf_est=0.11, kf_ci95=(-0.20, 0.43), kf_ci90=(-0.15, 0.38),
             fs_est=0.69, fs_ci95=( 0.44, 0.95), fs_ci90=( 0.48, 0.91)),
    30: dict(kf_est=0.07, kf_ci95=(-0.15, 0.29), kf_ci90=(-0.12, 0.26),
             fs_est=0.74, fs_ci95=( 0.55, 0.94), fs_ci90=( 0.58, 0.91)),
}

# Headline p-values (degree-based tie-breaking, approx_perm_rank_degree)
pvalues = {
    # q: (p_kf, p_fs)
    5:  (1.000, 0.062),
    10: (1.000, 0.007),
    20: (0.152, 0.074),
}

# ---------------------------------------------------------------------------
lines = []

lines.append("=" * 72)
lines.append("ASSESSMENT 3: CHOICE OF k AND q")
lines.append("Auerbach, Guo, Tabord-Meehan (2026) — Empirical Application")
lines.append("=" * 72)
lines.append("")

# ── Part A: k-trending ────────────────────────────────────────────────────
lines.append("─" * 72)
lines.append("PART A: Trending Estimates Across k (Table 2)")
lines.append("─" * 72)
lines.append("")
lines.append("  Table 2 reproduces (from replicated output):")
lines.append("")
lines.append(f"  {'k':<6}  {'E[Yβ]-E[Yα] (knife→fork)':<30}  {'E[Yγ]-E[Yβ] (fork→spoon)'}")
lines.append("  " + "-"*65)
for k, d in sorted(table2.items()):
    kf_str = f"{d['kf_est']:.2f}  95%CI [{d['kf_ci95'][0]:.2f},{d['kf_ci95'][1]:.2f}]"
    fs_str = f"{d['fs_est']:.2f}  95%CI [{d['fs_ci95'][0]:.2f},{d['fs_ci95'][1]:.2f}]"
    lines.append(f"  {k:<6}  {kf_str:<30}  {fs_str}")

lines.append("")

# Point-estimate change statistics
kvals = sorted(table2.keys())
kf_ests = [table2[k]['kf_est'] for k in kvals]
fs_ests = [table2[k]['fs_est'] for k in kvals]

kf_range  = max(kf_ests) - min(kf_ests)
fs_range  = max(fs_ests) - min(fs_ests)
kf_shift  = kf_ests[0] - kf_ests[-1]   # change from k=10 to k=30
fs_shift  = fs_ests[-1] - fs_ests[0]   # change from k=10 to k=30

# CI width at k=30
kf_ci_width_k30 = table2[30]['kf_ci95'][1] - table2[30]['kf_ci95'][0]
fs_ci_width_k30 = table2[30]['fs_ci95'][1] - table2[30]['fs_ci95'][0]

lines.append("  Convergence diagnostics:")
lines.append("")
lines.append(f"  knife→fork:")
lines.append(f"    Point estimate k=10: {kf_ests[0]:.2f}")
lines.append(f"    Point estimate k=30: {kf_ests[-1]:.2f}")
lines.append(f"    Total shift (k=10→30): {abs(kf_shift):.2f}  ({100*abs(kf_shift)/kf_ests[0]:.0f}% of k=10 estimate)")
lines.append(f"    CI width at k=30:    {kf_ci_width_k30:.2f}")
lines.append(f"    Shift as % of final CI width: {100*abs(kf_shift)/kf_ci_width_k30:.0f}%")
lines.append(f"    Direction: monotone decrease  ({kf_ests[0]:.2f} → {kf_ests[1]:.2f} → {kf_ests[2]:.2f})")
lines.append("")
lines.append(f"  fork→spoon:")
lines.append(f"    Point estimate k=10: {fs_ests[0]:.2f}")
lines.append(f"    Point estimate k=30: {fs_ests[-1]:.2f}")
lines.append(f"    Total shift (k=10→30): {abs(fs_shift):.2f}  ({100*abs(fs_shift)/fs_ests[0]:.0f}% of k=10 estimate)")
lines.append(f"    CI width at k=30:    {fs_ci_width_k30:.2f}")
lines.append(f"    Shift as % of final CI width: {100*abs(fs_shift)/fs_ci_width_k30:.0f}%")
lines.append(f"    Direction: monotone increase  ({fs_ests[0]:.2f} → {fs_ests[1]:.2f} → {fs_ests[2]:.2f})")
lines.append("")

# ── Part B: q sensitivity ─────────────────────────────────────────────────
lines.append("─" * 72)
lines.append("PART B: Significance as a Function of q")
lines.append("─" * 72)
lines.append("")
lines.append(f"  {'q':<6}  {'p(knife=fork)':>15}  {'Sig@5%':>8}  "
             f"{'p(fork=spoon)':>15}  {'Sig@5%':>8}  {'Sig@10%':>8}")
lines.append("  " + "-"*67)
for q, (pkf, pfs) in sorted(pvalues.items()):
    sig_kf_5  = "YES" if pkf < 0.05 else "no"
    sig_fs_5  = "YES" if pfs < 0.05 else "no"
    sig_fs_10 = "YES" if pfs < 0.10 else "no"
    lines.append(f"  {q:<6}  {pkf:>15.3f}  {sig_kf_5:>8}  "
                 f"{pfs:>15.3f}  {sig_fs_5:>8}  {sig_fs_10:>8}")
lines.append("")

# Count of significant results
n_sig_fs_5  = sum(1 for _, (_, p) in pvalues.items() if p < 0.05)
n_sig_fs_10 = sum(1 for _, (_, p) in pvalues.items() if p < 0.10)
lines.append(f"  fork=spoon significant at alpha=0.05: {n_sig_fs_5}/3 q values")
lines.append(f"  fork=spoon significant at alpha=0.10: {n_sig_fs_10}/3 q values")
lines.append(f"  knife=fork  significant at alpha=0.05: 0/3 q values")
lines.append(f"  knife=fork  significant at alpha=0.10: 0/3 q values")
lines.append("")

# ── Part C: joint summary ─────────────────────────────────────────────────
lines.append("─" * 72)
lines.append("PART C: Parameter Sensitivity Summary")
lines.append("─" * 72)
lines.append("")
lines.append("  For fork=spoon, does the 95% CI exclude zero?")
lines.append("")
lines.append(f"  {'k':<6}  {'95% CI':>20}  {'Excludes 0?':>12}")
lines.append("  " + "-"*42)
for k, d in sorted(table2.items()):
    lb, ub = d['fs_ci95']
    excl = "YES" if lb > 0 else "no"
    lines.append(f"  {k:<6}  [{lb:>6.2f}, {ub:>5.2f}]{'':<4}  {excl:>12}")
lines.append("")
lines.append("  For fork=spoon, does the p-value reject H0 at alpha=0.05?")
lines.append("")
lines.append(f"  {'q':<6}  {'p-value':>10}  {'Rejects?':>10}")
lines.append("  " + "-"*30)
for q, (_, pfs) in sorted(pvalues.items()):
    rej = "YES" if pfs < 0.05 else "no"
    lines.append(f"  {q:<6}  {pfs:>10.3f}  {rej:>10}")
lines.append("")
lines.append("  Note: 95% CIs exclude 0 at all k values, but p-values only")
lines.append("  reject H0 at q=10 (of 3 q values). These are separate procedures")
lines.append("  (CLT-based CI vs permutation test) with separate parameters.")

lines.append("")
lines.append("=" * 72)

output = "\n".join(lines)
print(output)

with open(OUT_FILE, 'w') as f:
    f.write(output + "\n")

print(f"\nSaved to: {OUT_FILE}")
