# AI Coding Instructions

## Project Overview

This is an econometrics project replicating **Lindo et al. (2010)** - a regression discontinuity design (RDD) study on academic probation effects. The project has two main components:

1. **Student Replication** (`project.ipynb`): Simplified Python-based replication for teaching
2. **Full Replication** (`replication/`): Complete empirical analysis with Stata and Python code

## Architecture & Data Flow

### Core Structure
- **Notebook Driver**: `project.ipynb` orchestrates the analysis workflow
- **Auxiliary Library**: `auxiliary/` contains reusable functions for tables, plots, and predictions
  - `tables.py`: RDD regression analysis with clustered standard errors
  - `plots.py`: RDD visualization functions (curves, scatter plots)
  - `predictions.py`: Data preparation and RDD prediction calculations
- **Data**: Stata files (`data-performance-standards-1.dta`, `-2.dta`) with GPA records
- **Full Replication**: `replication/` mirrors the published paper's empirical workflow

### Analysis Pattern

The RDD methodology is central:
1. **Data Prep**: `predictions.prepare_data()` adds constants, dummy variables for cutoff groups, campus-specific thresholds
2. **Estimation**: `tables.estimate_RDD_multiple_outcomes()` fits OLS with GPA-clustered standard errors
3. **Visualization**: `plots.plot_RDD_curve()` shows treated vs untreated group trajectories
4. **Output**: Tables and figures to `auxiliary/` methods for formatting/styling

## Key Conventions

### Clustering & Estimation
- **Cluster variable**: `clustervar` (GPA-based for handling discrete running variable issues)
- **Cutoff**: Campus-specific thresholds stored in `cutoff` column
- **Regression formula**: Always includes explicit constant via `hasconst=True`
- Use `statsmodels` OLS with `cov_type='cluster'` and `cov_kwds={'groups': clustervar}`

### Data Preparation
- Running variable is GPA; outcomes include enrollment, test scores, credits
- Binary treatment: `gpalscutoff` dummy (1 if GPA < cutoff)
- Missing values: Frequent for student withdrawals - handled in-line with `.dropna(subset=[outcome])`
- Campus variables: `loc_campus3` and others signal campus-specific parameters

### Visualization Style
- Split dataframes by cutoff before plotting: `df[df[running_var] < cutoff]` and `>= cutoff`
- Use `plt.grid(True)` for consistency
- RDD curves show discontinuity at threshold

## Development Workflow

### Running the Notebook
```bash
# Setup environment
conda env create -f environment.yml
conda activate projects-student-template

# Run notebook in JupyterLab
jupyter lab project.ipynb
```

### Testing
```bash
pytest tests/
# Smoke tests verify module imports and key functions (e.g., create_table1, prepare_data, plot_figure1)
```

### Code Quality
- **Linter**: `ruff` configured in `pyproject.toml` (line length 88, targets Python 3.11+)
- **Formatters**: isort enforces `auxiliary` as first-party import
- **Pre-commit**: Hooks run ruff checks before commits

### Full Replication Execution
- `replication/main.sh`: Master script orchestrating Stata and Python pipelines
- Python dependencies: `replication/requirements.txt` or Pipenv
- Stata scripts: `code_stata/` follows numbered prefixes (01, 02) and analysis subfolder

## Common Tasks

### Adding a New Analysis Function
1. Add to appropriate module in `auxiliary/` (tables, plots, or predictions)
2. Include docstring with Args/Returns sections (follow existing patterns)
3. Add corresponding test in `tests/test_imports.py` checking function exists
4. Call from `project.ipynb` with explicit data variables

### Extending RDD Analysis
- Modify `estimate_RDD_multiple_outcomes()` to add new outcomes (list parameter)
- Ensure new outcome columns exist in data and handle `.dropna(subset=[outcome])`
- Cluster by `clustervar` consistently; adjust if study design changes

### Handling Missing Data
- Use `.dropna(subset=[column])` before fitting models (done per-outcome in tables module)
- Track observation counts in output tables (stored in tables DataFrame)
- Document assumptions about missingness in markdown cells

## Critical Details

- **Python 3.11+**: Required by `pyproject.toml`; rely on type hints in docstrings
- **Stata Integration**: Full replication uses Stata for some preprocessing; Python replicates key findings
- **Data Access**: Stata `.dta` files loaded via `pandas.read_stata()` (no special arguments needed)
- **Reproducibility**: Notebook cells are sequential; maintain state between cells for correct analysis order
