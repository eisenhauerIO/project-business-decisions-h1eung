import pandas as pd
import numpy as np
import glob
import os
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score, confusion_matrix

# Initialize results containers
metrics_results = []
metrics_bootstrap_results = []

# Function to process merged data efficiently
def process_predictions(df, target, folds, prediction_col='oof_prediction'):
    predictions = df[[f'{target}_{prediction_col}_{i}' for i in range(folds)]].values
    metrics_data = []

    for fold in range(folds):
        pred = predictions[:, fold]
        actual = df[target].values

        valid_idx = ~np.isnan(actual) & ~np.isnan(pred) & np.isfinite(pred)
        if valid_idx.sum() == 0:
            continue

        actual_clean = actual[valid_idx]
        pred_clean = pred[valid_idx]
        binary_pred = (pred_clean > 0.5).astype(int)

        auc = roc_auc_score(actual_clean, pred_clean)
        f1 = f1_score(actual_clean, binary_pred)
        acc = accuracy_score(actual_clean, binary_pred)
        tn, fp, fn, tp = confusion_matrix(actual_clean, binary_pred).ravel()
        metrics_data.extend([auc, f1, acc, tn, fp, fn, tp])

    return metrics_data

# Collect folder names
folder_names = [os.path.basename(os.path.dirname(folder)) for folder in glob.glob('data/working/prediction_*/')]

for folder in folder_names:
    split = folder.split('_')
    model_name, sampling_method, data_option = split[1], split[2], '_'.join(split[3:])

    print("Processing:", model_name, sampling_method, data_option)

    merged_file_path = f'./data/working/merged/{model_name}_{sampling_method}_{data_option}.csv'
    if not os.path.exists(merged_file_path):
        print(f"File not found: {merged_file_path}")
        continue

    merged_df = pd.read_csv(merged_file_path)

    if 'b_bootstrap_holdout' in data_option:
        target = 'narrow1'
        prediction_type = 'hold_out'
    elif 'b_bootstrap' in data_option:
        target = 'narrow1'
        prediction_type = 'oof'
    else:
        prediction_type = None

    if prediction_type:
        bootstrap_cols = [f'{target}_{prediction_type}_prediction_{i}' for i in range(1000)]

        if all(col in merged_df.columns for col in bootstrap_cols):
            bootstrap_results = []

            for fold in range(1000):
                preds = merged_df[f'{target}_{prediction_type}_prediction_{fold}']
                actual = merged_df[target]

                valid_idx = ~np.isnan(actual) & ~np.isnan(preds) & np.isfinite(preds)
                if valid_idx.sum() == 0:
                    continue

                preds_clean = preds[valid_idx]
                actual_clean = actual[valid_idx]
                binary_preds = (preds_clean > 0.5).astype(int)

                auc = roc_auc_score(actual_clean, preds_clean)
                f1 = f1_score(actual_clean, binary_preds)
                accuracy = accuracy_score(actual_clean, binary_preds)

                bootstrap_results.append([auc, f1, accuracy])

            if bootstrap_results:
                bootstrap_results = np.array(bootstrap_results)
                metrics_bootstrap_results.append([
                    model_name, sampling_method, data_option, target,
                    bootstrap_results[:, 0].mean(), bootstrap_results[:, 1].mean(), bootstrap_results[:, 2].mean(),
                    bootstrap_results[:, 0].std(), bootstrap_results[:, 1].std(), bootstrap_results[:, 2].std()
                ])
        else:
            print(f"No valid bootstrap columns ({prediction_type}) for {model_name}, {sampling_method}, {data_option}")
        continue

    # Non-bootstrap scenarios
    for target in ['narrow1', 'corr1', 'corr2']:
        prediction_columns = [f'{target}_oof_prediction_{i}' for i in range(5)]
        if all(col in merged_df.columns for col in prediction_columns):
            merged_df_target = merged_df.dropna(subset=[f'{target}_oof_prediction']).copy()

            metrics_fold = process_predictions(merged_df_target, target, folds=5)

            binary_pred_overall = (merged_df_target[f'{target}_oof_prediction'] > 0.5).astype(int)
            auc_overall = roc_auc_score(merged_df_target[target], merged_df_target[f'{target}_oof_prediction'])
            f1_overall = f1_score(merged_df_target[target], binary_pred_overall)
            acc_overall = accuracy_score(merged_df_target[target], binary_pred_overall)
            tn, fp, fn, tp = confusion_matrix(merged_df_target[target], binary_pred_overall).ravel()

            metrics_results.append([
                model_name, sampling_method, data_option, target,
                auc_overall, f1_overall, acc_overall, tn, fp, fn, tp
            ] + metrics_fold)

# Define columns explicitly
fold_columns = []
for fold in range(5):
    fold_columns.extend([f'auc_{fold}', f'f1_{fold}', f'accuracy_{fold}', f'tn_{fold}', f'fp_{fold}', f'fn_{fold}', f'tp_{fold}'])

metrics_columns = ['model', 'sampling_method', 'data', 'target',
                   'auc', 'f1', 'accuracy', 'tn', 'fp', 'fn', 'tp'] + fold_columns

metrics_df = pd.DataFrame(metrics_results, columns=metrics_columns)

for metric in ['auc', 'f1', 'accuracy']:
    fold_metric_cols = [f'{metric}_{fold}' for fold in range(5)]
    metrics_df[f'best_{metric}'] = metrics_df[fold_metric_cols].max(axis=1)
    metrics_df[f'worst_{metric}'] = metrics_df[fold_metric_cols].min(axis=1)
    metrics_df[f'mean_{metric}'] = metrics_df[fold_metric_cols].mean(axis=1)
    metrics_df[f'std_{metric}'] = metrics_df[fold_metric_cols].std(axis=1)

# Save results
os.makedirs('./output', exist_ok=True)
metrics_df.to_csv('./output/metrics_by_spec.csv', index=False)

# Save bootstrap metrics separately
bootstrap_columns = ['model', 'sampling_method', 'data', 'target',
                     'auc_mean', 'f1_mean', 'accuracy_mean',
                     'auc_std', 'f1_std', 'accuracy_std']

metrics_bootstrap_df = pd.DataFrame(metrics_bootstrap_results, columns=bootstrap_columns)
metrics_bootstrap_df.to_csv('./output/metrics_bootstrap.csv', index=False)

print("Metrics and bootstrap metrics saved successfully.")
