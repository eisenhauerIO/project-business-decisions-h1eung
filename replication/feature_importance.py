
import sys
import os

import pandas as pd
import numpy as np


import glob
import os
from xgboost import plot_importance




def load_model(folder_name):
    import pickle as pk
    model_list = []
    for count in range(1000 if 'bootstrap' in folder_name else 5):
        model = pk.load(open(f'{folder_name}/narrow1_fold{count}/fold_{count}_model.pickle','rb'))
        model_list.append(model)
    return model_list






all_model_list = [('prediction_xgboost_nosample_b',load_model(f'./data/working/prediction_xgboost_nosample_b'))]

print(all_model_list)

for model_name, model_list in all_model_list:
    
    try:


        feature_importance_df = pd.DataFrame()
        feature_importance_df['feature'] = model_list[0].get_booster().get_score(importance_type="gain").keys()

        for w in ['gain','weight','cover']:
            for count in range(5):
                feature_importance_df = feature_importance_df.merge(pd.DataFrame(zip(model_list[count].get_booster().get_score(importance_type=w).keys(),
                                                                                model_list[count].get_booster().get_score(importance_type=w).values()),
                                                                                columns = ['feature',f'{w}_{count}']),
                                                                    how='outer', on = 'feature')


        feature_importance_df = feature_importance_df.fillna(0)


        for w in ['gain','weight','cover']:
            feature_importance_df[f'{w}_avg'] = feature_importance_df[[f'{w}_{i}' for i in range(5)]].mean(axis=1)
            feature_importance_df[f'{w}_sum'] = feature_importance_df[[f'{w}_{i}' for i in range(5)]].sum(axis=1)


        feature_importance_df.to_csv(f'./data/working/{model_name}_feature_importance.csv')
    except:
        print(f'error with {model_name}')





