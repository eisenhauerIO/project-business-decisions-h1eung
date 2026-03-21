[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/g5Rk6CRe)
[![Run Notebook](https://github.com/eisenhauerIO/projects-businss-decisions/actions/workflows/run-notebook.yml/badge.svg)](https://github.com/eisenhauerIO/projects-businss-decisions/actions/workflows/run-notebook.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Replication Project: Auerbach, Guo & Tabord-Meehan (2026)

**Paper:** Auerbach, E., Guo, Y., & Tabord-Meehan, M. (2026). The Local Approach to Causal Inference under Network Interference. *Quantitative Economics*, 17, 173–199. https://doi.org/10.3982/QE2484

This repository contains a full replication and critical assessment of the empirical application in Auerbach et al. (2026), which proposes a nonparametric framework for causal inference under network interference. The paper models each node's rooted subgraph ("local configuration") as its treatment and uses a k-nearest-neighbor estimator and permutation test to compare favor exchange outcomes across three network structures — knife (support), fork (star), and spoon (triangular clustering) — in 75 rural Karnataka villages. The headline finding is that fork→spoon rejects distributional equality at p=0.007, suggesting clustering drives favor exchange. Our notebook replicates all primary outputs exactly and then conducts three critical assessments and two independent extensions that reveal the headline result rests on degenerate matching (the spoon configuration has zero exact structural matches across all 75 villages), making the p-value highly sensitive to arbitrary tie-breaking choices.

## Notebook

**[main_project.ipynb](main_project.ipynb)** — Main submission notebook. Runs top-to-bottom using the `my-virtenv-py310` conda environment.



## Analysis Sections

- **Replication Results** — Exact replication of Tables 1, 2, 12, 13 and Figures 6–12; all outputs match byte-for-byte.
- **Critical Assessment 1: Matching Quality** — Documents that the spoon configuration has zero perfect structural matches across all 75 villages, making the KNN estimator unable to condition on the clustering feature it claims to measure.
- **Critical Assessment 2: P-value Sensitivity** — Shows the headline p=0.007 is more extreme than all 10 random tie-breaking seeds in Tables 12–13; only 4/10 seeds reject at α=0.05.
- **Critical Assessment 3: Choice of k and q** — Demonstrates non-convergence of estimates across k and that fork=spoon is significant at only 1 of 3 reported q values (q=10), raising a multiple-comparisons concern.
- **Extension 1: P-values Across Extended q Range** — Sweeps q ∈ {1,…,35} and finds fork=spoon significant at 6/11 values, but with a notable local dip at q=20 explained by the degenerate spoon matching.
- **Extension 2: Full Monte Carlo over Tie-Breaking Seeds** — Runs 1000 random seeds and finds the test rejects at α=0.05 only 33.7% of the time at q=10; the paper's headline p=0.007 sits at the 6.1th percentile of the seed distribution.

## Files

- **[replication/](replication/)** — Original replication package from the paper, including all source scripts, data, and pre-computed outputs from Auerbach et al. (2026).
- **[replication/my_replication_outputs/](replication/my_replication_outputs/)** — All replication outputs and original analysis files produced for this project (tables, figures, logs, and extension results).

---

