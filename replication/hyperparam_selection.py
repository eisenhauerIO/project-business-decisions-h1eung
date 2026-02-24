import pandas as pd
import pickle as pk
import xgboost as xgb
import glob
import os




def describe_model(model, fold = 0):
    model_test = pk.load(open(f'{model}/narrow1_fold{fold}/fold_{fold}_model.pickle','rb'))    
    booster = model_test.get_booster()
    booster_df = booster.trees_to_dataframe()
    data = dict()
    data['Fold'] = str(fold)
    data['L1 Penalty'] = model_test.reg_alpha
    data['L2 Penalty'] = model_test.reg_lambda
    data['Max Tree Depth'] = model_test.max_depth
    data['Learning Rate'] = model_test.learning_rate
    data['Min. Child Weight'] = model_test.min_child_weight
    data['Tree Count'] = model_test.best_ntree_limit
    data['Node Count'] = booster_df[booster_df.Tree<=model_test.best_ntree_limit-1].shape[0]
    print(data)
    return data
    


folder_name = 'prediction_xgboost_nosample_b'

descriptive = [describe_model('./data/working/' + folder_name, i) for i in range(5)]
descriptive_df = pd.DataFrame(descriptive)
mean_row = descriptive_df[['L1 Penalty', 'L2 Penalty', 'Max Tree Depth', 'Learning Rate', 'Min. Child Weight', 'Tree Count', 'Node Count']].mean(axis=0)
mean_row['Fold'] = 'Mean'
descriptive_df.loc[len(descriptive_df)] = mean_row
descriptive_df.to_csv(f'./output/appendix_tables/table_a2.csv')
print('done')
