# Replication Notes
## Paper: "The Local Approach to Causal Inference under Network Interference"
**Authors:** Eric Auerbach, Hongchang Guo, Max Tabord-Meehan
**Published:** Quantitative Economics 17 (2026), 173–199
**DOI:** https://doi.org/10.3982/QE2484

---

## 1. What This Paper Does

The paper proposes a nonparametric framework for causal inference when outcomes depend on how agents are connected in a social or economic network (network interference). The core innovation is modeling an agent's "local configuration" — the structure of the network nearby, as measured by path distance — as the effective treatment. This avoids misspecification of parametric exposure maps.

Two main methodological contributions:
1. **k-nearest neighbors (KNN) estimator** for average policy effects under network interference, with finite-sample MSE bounds
2. **Randomization test** for policy irrelevance (no treatment effect), shown to be asymptotically valid

The empirical application applies these methods to social capital formation data from 75 rural villages in Karnataka, India (Banerjee et al. 2013), testing whether network structure (support and clustering) affects the number of favors exchanged between households.

---

## 2. What We Chose to Replicate and Why

### Priority 1: Empirical Application — Tables 1, 2, 12, 13 + Figures 8–12 + p-values
**Why:** These are the paper's core results. Table 2 and the p-values directly demonstrate the two methodological contributions (KNN estimation and randomization testing) applied to real data. The paper's main conclusion — that clustering plays a role in favor exchange (spoon vs. fork comparison) but support alone does not (fork vs. knife) — rests entirely on these outputs. Tables 12–13 and Figures 8–12 are robustness checks and network visualizations from Supplemental Appendix D that support the empirical findings.

### Priority 2: Figures 6–7
**Why:** These are conceptual/illustrative figures showing how the local approach works. They support the reader's understanding of the methodology and are referenced throughout the paper.

### Skipped / Deprioritized
- **Tables 3–10** (simulation rejection rates): Supplemental Appendix material. Full replication requires a computing cluster (Quest, 48+ hrs per batch). Partial replication of Table 3 was initiated but is computationally intensive.
- **Table 11** (MSE simulation): ~40 hours on a single machine; deprioritized given the 2-day timeline.
- **Tables 14–16, Figures 1–5**: Not produced by code (graphical display only).

---

## 3. Replication Environment

### Software
- **Conda:** 25.7.0 (paper used 25.5.1 — minor version difference, no impact)
- **Virtual environment `my-virtenv-py310`** (used for all empirical results and figures):
  - Python 3.10.6, numpy 1.26.4, networkx 3.3, pandas 2.2.3, matplotlib 3.5.3, scipy 1.11.4, igraph 0.11.8
- **Virtual environment `my-virtenv-py38`** (used for simulation Tables 3–10):
  - Python 3.8.19, numpy 1.24.4, networkx 3.1, pandas 2.0.3, matplotlib 3.7.5, scipy 1.10.1

### Hardware
Replication was run on a Mac (Apple Silicon). The paper's empirical results were originally run on a MacBook Air (Apple M4 Chip). Note: the paper warns that `np.argsort()` may exhibit platform-dependent behavior, so minor numerical differences across machines are possible.

---

## 4. Contents of `my_replication_outputs/`

This folder stores replicated outputs separately from the original pre-computed reference files in the replication package, allowing direct comparison.

```
my_replication_outputs/
│
├── empirical_application/          # Replicated outputs from Empirical-Application/
│   ├── Table1.txt                  # LaTeX: Summary statistics (households per village)
│   ├── Table2.txt                  # LaTeX: KNN estimates + CIs for policy effects (knife/fork/spoon)
│   ├── Table12.txt                 # LaTeX: Supplemental empirical results (App. D)
│   ├── Table13.txt                 # LaTeX: Supplemental empirical results (App. D)
│   ├── p-values-empirical-applicaiton.txt  # p-values for randomization tests (Section 5)
│   ├── Figure8.eps                 # Network visualization: matched rooted networks
│   ├── Figure9.eps                 # Network visualization: matched rooted networks
│   ├── Figure10.eps                # Network visualization: matched rooted networks
│   ├── Figure11.eps                # Network visualization: matched rooted networks
│   └── Figure12.eps                # Network visualization: matched rooted networks
│
├── figures6-7/                     # Replicated outputs from Figures6-7/
│   ├── Figure6-(a).eps             # Illustrative local configuration figures
│   ├── Figure6-(b).eps
│   ├── Figure6-(c).eps
│   ├── Figure6-(d).eps
│   ├── Figure6-(d).pdf
│   ├── Figure6-(e).eps
│   ├── Figure6-(f).eps
│   └── Figure7.eps                 # Additional illustrative figure
│
├── table3_partial/                 # Replicated outputs from Table3/single_computer_codes/
│   ├── partial_replication_results.txt  # Rejection rates for pre-specified null hypotheses
│   └── Table3.txt                  # LaTeX: Table 3 with replicated cells populated
│
├── run_empirical_application.sh    # Wrapper: runs empirical-application.sh, copies outputs here
├── run_figures6-7.sh               # Wrapper: runs figures6-7.sh, copies outputs here
├── run_table3_partial.sh           # Wrapper: runs table3_single_computer_partial.sh, copies outputs here
├── empirical_application_run.log   # Log of the empirical application run
├── figures6-7_run.log              # Log of the figures 6-7 run
└── table3_partial_run.log          # Log of the Table 3 partial run (ongoing)
```

---

## 5. Verification Results

All replicated outputs were compared byte-for-byte against the original pre-computed reference files in the replication package using `diff`. Results:

| Output | Files | Match |
|---|---|---|
| Empirical Application | Table1–2, 12–13, p-values, Figures 8–12 (10 files) | ✅ Exact match |
| Figures 6–7 | Figure6-(a–f), Figure7 (8 files) | ✅ Exact match |
| Table 3 partial | In progress | ⏳ Running |

---

## 6. Runtime Summary

| Task | Runtime | Machine |
|---|---|---|
| Empirical Application | ~3 hours | Mac (Apple Silicon) |
| Figures 6–7 | ~1 hour | Mac (Apple Silicon) |
| Table 3 partial | ~12 hours (estimated) | Mac (Apple Silicon) |

Paper reported ~5–6 hours for Empirical Application on MacBook Pro Intel i5; our faster runtime reflects Apple Silicon performance.

---

## 7. How to Run the Replication

### Prerequisites
1. Install Anaconda/Miniconda
2. Create environments (one-time):
   ```bash
   cd replication/my-virtenv-py310 && bash create-my-virtenv-py310.sh
   cd replication/my-virtenv-py38  && bash create-my-virtenv-py38.sh
   ```

### Running
From `replication/my_replication_outputs/`:
```bash
# Core empirical results (~3-6 hrs)
bash run_empirical_application.sh

# Figures 6-7 (~1 hr)
bash run_figures6-7.sh

# Table 3 partial simulation (~12 hrs)
bash run_table3_partial.sh
```
Each script runs the original code and automatically copies outputs into the appropriate subfolder.
