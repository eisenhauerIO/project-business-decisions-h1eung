import pandas as pd

metrics_by_spec = pd.read_csv('./output/metrics_by_spec.csv')
metrics_bootstrap = pd.read_csv('./output/metrics_bootstrap.csv')

def find_metric(df, model, sampling, data, target):
    return df.query("model == @model and sampling_method == @sampling and data == @data and target == @target").iloc[0]

def format_metric(row, metric):
    return f"{row[metric]:.3f} [{row[f'worst_{metric}']:.3f}, {row[f'best_{metric}']:.3f}]"

def format_bootstrap_metric(row, metric):
    return f"{row[f'{metric}_mean']:.3f} ({row[f'{metric}_std']:.3f})"

# Table 2
table_2 = pd.DataFrame({
    'Model Name': ['Guessing (1)', 'OLS (2)', 'Lasso (3)', 'Logistic (4)', 'XGBoost (5)', 'XGBoost Bootstrap (6)', 'XGBoost Bootstrap Holdout (7)'],
    'Accuracy': [
        "0.580",
        format_metric(find_metric(metrics_by_spec, 'linear','nosample','b','narrow1'), 'accuracy'),
        format_metric(find_metric(metrics_by_spec, 'lasso','nosample','b','narrow1'), 'accuracy'),
        format_metric(find_metric(metrics_by_spec, 'logistic','nosample','b','narrow1'), 'accuracy'),
        format_metric(find_metric(metrics_by_spec, 'xgboost','nosample','b','narrow1'), 'accuracy'),
        format_bootstrap_metric(find_metric(metrics_bootstrap, 'xgboost','nosample','b_bootstrap','narrow1'), 'accuracy'),
        format_bootstrap_metric(find_metric(metrics_bootstrap, 'xgboost','nosample','b_bootstrap_holdout','narrow1'), 'accuracy')
    ],
    'AUC-ROC': [
        "-",
        format_metric(find_metric(metrics_by_spec, 'linear','nosample','b','narrow1'), 'auc'),
        format_metric(find_metric(metrics_by_spec, 'lasso','nosample','b','narrow1'), 'auc'),
        format_metric(find_metric(metrics_by_spec, 'logistic','nosample','b','narrow1'), 'auc'),
        format_metric(find_metric(metrics_by_spec, 'xgboost','nosample','b','narrow1'), 'auc'),
        format_bootstrap_metric(find_metric(metrics_bootstrap, 'xgboost','nosample','b_bootstrap','narrow1'), 'auc'),
        format_bootstrap_metric(find_metric(metrics_bootstrap, 'xgboost','nosample','b_bootstrap_holdout','narrow1'), 'auc')
    ],
    'F1': [
        "0.000",
        format_metric(find_metric(metrics_by_spec, 'linear','nosample','b','narrow1'), 'f1'),
        format_metric(find_metric(metrics_by_spec, 'lasso','nosample','b','narrow1'), 'f1'),
        format_metric(find_metric(metrics_by_spec, 'logistic','nosample','b','narrow1'), 'f1'),
        format_metric(find_metric(metrics_by_spec, 'xgboost','nosample','b','narrow1'), 'f1'),
        format_bootstrap_metric(find_metric(metrics_bootstrap, 'xgboost','nosample','b_bootstrap','narrow1'), 'f1'),
        format_bootstrap_metric(find_metric(metrics_bootstrap, 'xgboost','nosample','b_bootstrap_holdout','narrow1'), 'f1')
    ]
})
table_2.to_csv('./output/tables/table_2.csv', index=False)

# Table A3
models_a3 = [('XGBoost', 'xgboost'), ('OLS', 'linear'), ('Lasso', 'lasso'), ('Logistic', 'logistic')]
table_a3 = pd.DataFrame([
    {
        'Model Name': name,
        'True Negative': find_metric(metrics_by_spec, model, 'nosample', 'b', 'narrow1')['tn'],
        'False Negative': find_metric(metrics_by_spec, model, 'nosample', 'b', 'narrow1')['fn'],
        'False Positive': find_metric(metrics_by_spec, model, 'nosample', 'b', 'narrow1')['fp'],
        'True Positive': find_metric(metrics_by_spec, model, 'nosample', 'b', 'narrow1')['tp']
    }
    for name, model in models_a3
])
table_a3.to_csv('./output/appendix_tables/table_a3.csv', index=False)

# Table B4
configs_b4 = [
    ('XGBoost (municipal sampling) - Budget', 'xgboost','sample','b','narrow1'),
    ('XGBoost (municipal sampling) - Budget + Demo', 'xgboost','sample','bd','narrow1'),
    ('XGBoost (municipal sampling) - Demo', 'xgboost','sample','d','narrow1'),
    ('Avis et al. data - XGBoost', 'xgboost','nosample','b','corr1'),
    ('Avis et al. data - OLS', 'linear','nosample','b','corr1'),
    ('Avis et al. data - LASSO', 'lasso','nosample','b','corr1'),
    ('Avis et al. data - Logistic', 'logistic','nosample','b','corr1')
]
table_b4 = pd.DataFrame([
    {
        'Model Name': name,
        'Accuracy': format_metric(find_metric(metrics_by_spec, model, samp, data, target), 'accuracy'),
        'AUC-ROC': format_metric(find_metric(metrics_by_spec, model, samp, data, target), 'auc'),
        'F1': format_metric(find_metric(metrics_by_spec, model, samp, data, target), 'f1')
    }
    for name, model, samp, data, target in configs_b4
])
table_b4.to_csv('./output/appendix_tables/table_b4.csv', index=False)