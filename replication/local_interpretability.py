
import pandas as pd
import os
import glob
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math

peturbed_folder = './data/working/prediction_xgboost_nosample_b_perturbed'


test = pd.read_csv(f'{peturbed_folder}/narrow1_fold0/predict_fold_0.csv',nrows=6)

test_head = test.head()
print(test_head)

main_col = ['cod_mun', 'year', 'for_prediction2','for_prediction', 'narrow1_train_sample', 'narrow1_predicted']


feature_col = [f[:-2] for f in test.columns[8:] if f[-2:]=='_1']
feature_col_add = [f for f in test.columns[8:] if f[-2:]=='_0']
feature_col_substract = [f for f in test.columns[8:] if f[-2:]=='_1']



def reshape_dataset(df,fold):
    df_substract = df[main_col+feature_col_substract].copy()
    df_substract.columns = main_col+feature_col
    df_substract.loc[:, 'subtract'] = 1
    
    df_add = df[main_col+feature_col_add].copy()
    df_add.columns = main_col+feature_col
    df_add.loc[:, 'subtract'] = 0
    
    df_reshaped = pd.concat([df_substract,df_add],axis=0).reset_index(drop=True)
    df_reshaped['fold'] = fold
    return df_reshaped


reshaped = []


for fold in range(5):
    address = f'{peturbed_folder}/narrow1_fold{fold}/predict_fold_{fold}.csv'
    df = pd.read_csv(address)
    reshaped.append(reshape_dataset(df,fold))
    print(fold)
    
reshaped_df = pd.concat(reshaped,axis=0).reset_index(drop=True)

feature_col_id = dict([(v[1],'v'+str(v[0])) for v in enumerate(feature_col)])

feature_col_id_df = pd.DataFrame(feature_col_id.items())


feature_col_id_df.columns = ['feature','code']


feature_col_id_df.feature = feature_col_id_df.feature.apply(lambda x: '_'.join(x.split('_')[2:]))

feature_col_id_df.to_csv('./output/feature_code_mapping.csv',index=False)


def return_if_exist(v):
    try:
        return feature_col_id[v]
    except:
        return v


reshaped_df.columns = [return_if_exist(v) for v in reshaped_df.columns]


reshaped_df.to_csv('./data/working/locally_perturbed_reshaped.csv',index=False)
print(reshaped_df.columns.tolist())


rel = reshaped_df.copy()

for i in range(797):
    # where subtract = 0 we do vi - narrow1_predicted, if subtract = 1 we do narrow1_predicted - vi
    rel.loc[rel['subtract'] == 1, f'd{i}'] = rel['narrow1_predicted'] - rel[f'v{i}']
    rel.loc[rel['subtract'] == 0, f'd{i}'] = rel[f'v{i}'] - rel['narrow1_predicted']

row = 'Distribution of Effects on Predicted Corruption'

columns_and_titles = [
    ('d126', 'Budget Surplus', -0.25,0.6),
    ('d412', 'Tax on Real Estate Transactions (ITB)',-0.2,0.6),
    ('d130', 'Expenditure on Agriculture',-0.28,0.6),
    ('d440', 'Motor Vehicle Property Tax (IPVA)',-0.4,0.45),
    ('d136', 'Expenditure on Transportation',-0.25,0.45),
    ('d181', 'Civil Servant Per Diems',-0.5,0.5),
]

fig, axes = plt.subplots(3, 2, figsize=(12, 12))

axes = axes.flatten()

for i, (col, title,low,up) in enumerate(columns_and_titles):

    data = rel[col].copy()
    data = data.rename(row)
    
    n_bins = 4*15
    
    
    
    density, bins = np.histogram(data, bins=n_bins, density=True)
    max_density = density.max()

    sns.histplot(data, stat='density', bins=n_bins, ax=axes[i])

    axes[i].set_title(title)

    axes[i].axvline(x=0, linestyle='--', color='black')

    axes[i].set_ylim(0, max_density * 1.3)
    axes[i].set_xlim(low, up)

plt.tight_layout()

plt.savefig('./output/appendix_figures/figure_c4.pdf')




