wd = '.'
import sys
import os
import pandas as pd
import numpy as np

np.random.seed(0)

from sklearn.model_selection import ParameterGrid,KFold
from itertools import chain
from sklearn.impute import MissingIndicator


def preparing_dataset(option = 'b', test = False):
    #takes in data option and whether this is a test
    #return the original data and feature set
    budget_data = pd.read_stata(wd+'/data/final/panel_budget_corruption.dta',
                                    convert_missing=False)
    budget_data= budget_data[budget_data['Populacao']>0]
    budget_data = budget_data.dropna(axis=1,how='all')
    
    if test:
        budget_data = budget_data.sample(frac = 0.1)
    
    budget_variables = list(budget_data.columns[33:830])
    demographics_variables = list(budget_data.columns[849:]) + list(budget_data.columns[32:33])
    
    if option == 'b':
        col_keep = budget_variables
    elif option == 'd':
        col_keep = demographics_variables
    else:
        col_keep = budget_variables + demographics_variables
    
    X_predict_full = budget_data[col_keep]
    X_predict_full = X_predict_full.fillna(X_predict_full.mean())
    
    return budget_data, X_predict_full

def preparing_dataset_excluding_fpm(option = 'b', test = False):
    #takes in data option and whether this is a test
    #return the original data and feature set
    budget_data = pd.read_stata(wd+'/data/final/panel_budget_corruption.dta',
                                    convert_missing=False)
    budget_data= budget_data[budget_data['Populacao']>0]
    budget_data = budget_data.dropna(axis=1,how='all')
    
    if test:
        budget_data = budget_data.sample(frac = 0.1)
    
    budget_variables = list(budget_data.columns[33:461]) + list(budget_data.columns[463:830])
    demographics_variables = list(budget_data.columns[849:]) + list(budget_data.columns[32:33])
    
    if option == 'b':
        col_keep = budget_variables
    elif option == 'd':
        col_keep = demographics_variables
    else:
        col_keep = budget_variables + demographics_variables
    
    X_predict_full = budget_data[col_keep]
    X_predict_full = X_predict_full.fillna(X_predict_full.mean())
    
    return budget_data, X_predict_full

def preparing_dataset_missing_normalized(option = 'b', test = False):
    #takes in data option and whether this is a test
    #return the original data and feature set
    budget_data = pd.read_stata(wd+'/data/final/panel_budget_corruption.dta',
                                    convert_missing=False)
    budget_data= budget_data[budget_data['Populacao']>0]
    budget_data = budget_data.dropna(axis=1,how='all')
    
    if test:
        budget_data = budget_data.sample(frac = 0.1)
    
    budget_variables = list(budget_data.columns[33:830])
    demographics_variables = list(budget_data.columns[849:]) + list(budget_data.columns[32:33])
    
    if option == 'b':
        col_keep = budget_variables
    elif option == 'd':
        col_keep = demographics_variables
    else:
        col_keep = budget_variables + demographics_variables

    X_predict_full = budget_data[col_keep]

    indicator = MissingIndicator(features='all')
    X_missing = indicator.fit_transform(X_predict_full)
    X_missing = pd.DataFrame(X_missing)
    X_missing.index = X_predict_full.index
    X_missing.columns = [col+'_missing' for col in X_predict_full.columns]
    X_missing = X_missing.astype(int)
    
    X_predict_full = X_predict_full.fillna(X_predict_full.mean())
    for col in col_keep:
        X_predict_full[col] = X_predict_full[col]/budget_data['Populacao']

    X_predict_full = X_predict_full.join(X_missing)
    
    return budget_data, X_predict_full

def preparing_dataset_excluding_last(option = 'b', test = False):
    #takes in data option and whether this is a test
    #return the original data and feature set
    budget_data = pd.read_stata(wd+'/data/final/panel_budget_corruption.dta',
                                    convert_missing=False)
    budget_data = budget_data[budget_data['Populacao']>0]
    budget_data = budget_data.dropna(axis=1,how='all')
    budget_data = budget_data[(budget_data.year_sorteio1!=2009)]
    
    if test:
        budget_data = budget_data.sample(frac = 0.1)
    
    budget_variables = list(budget_data.columns[33:830])
    demographics_variables = list(budget_data.columns[849:]) + list(budget_data.columns[32:33])
    
    if option == 'b':
        col_keep = budget_variables
    elif option == 'd':
        col_keep = demographics_variables
    else:
        col_keep = budget_variables + demographics_variables
    
    X_predict_full = budget_data[col_keep]
    X_predict_full = X_predict_full.fillna(X_predict_full.mean())
    
    return budget_data, X_predict_full



def return_index(train,test,groups,cod_mun):
    test_index = list(chain(*[list(groups[cod_mun[c]]) for c in test]))
    train_index = list(chain(*[list(groups[cod_mun[c]]) for c in train]))
    return train_index, test_index

def return_train_test_split(y_var,
                                      budget_data,
                                      sampling_method,
                                      split):
    
    # only use the indices for which for_prediction2 or for_prediction is set -> all the others we ignore
    if y_var in ['corr1','corr2']:
        index = list(budget_data[budget_data['for_prediction2']==1].dropna(subset=[y_var]).index)
    else:
        index = list(budget_data[budget_data['for_prediction']==1].dropna(subset=[y_var]).index)
    
    # split the indices we have into the fodls
    kf = KFold(n_splits=split,shuffle=True, random_state=40)
    
    if sampling_method == 'nosample':
        # in here we randomly assign the 
        index = np.array(index)
        fold_list = [(index[train],index[test]) for (train,test) in list(kf.split(index))]
    else:
        # in here we split by municipality code
        groups = budget_data.loc[index].groupby(['cod_mun']).groups
        cod_mun = list(groups.keys())
        fold_list = [return_index(train,test,groups,cod_mun) for (train,test) in list(kf.split(cod_mun))]
    return fold_list

#define search space
#xgboost
xgb_param_grid = ParameterGrid({'reg_alpha':[0.1,0.5,1,2],
                                'reg_lambda':[0.1,0.5,1,2],
                                'max_depth':[5,10,20],
                                'learning_rate':[0.1,0.5],
                                'min_child_weight':[1,3,5],
                                'objective':['binary:logistic'],
                                'eval_metric':['error'],
                                'gpu_id':[0],
                                'silent':[1]})

#SGDClassifier
logistic_param_grid = ParameterGrid({'loss':['log'],
                                     'penalty':['elasticnet'],
                                     'max_iter':[100000],
                                     'shuffle':[True],
                                     'l1_ratio':[1,0.75,0.5,0.25,0.15,0.05,0],
                                     'alpha':[0.1**(i) for i in range(-1,5)],
                                     'early_stopping':[True],
                                     'n_iter_no_change':[1000]})
#SGDRegressor
lasso_param_grid = ParameterGrid({'loss':['squared_loss'],
                                     'penalty':['l2'],
                                     'max_iter':[100000],
                                     'shuffle':[True],
                                     'alpha':[0.1**(i) for i in range(-1,5)],
                                     'early_stopping':[True],
                                     'n_iter_no_change':[1000]})
#SGDRegressor
linear_param_grid = ParameterGrid({'loss':['squared_loss'],
                        'penalty':['l2'],
                        'max_iter':[100000],
                        'shuffle':[True],
                        'alpha':[0],
                                   'early_stopping':[True],
                                     'n_iter_no_change':[5000]})

grid_search_dictionary = {
    'xgboost':xgb_param_grid,
    'logistic':logistic_param_grid,
    'lasso':lasso_param_grid,
    'linear':linear_param_grid
}

def train_prediction_model_return_score_xgboost(y_var,
                                                budget_data,
                                                X_predict_full,
                                                train_fold,
                                                test_fold,
                                                p):
    import xgboost as xgb
    model = xgb.XGBClassifier(n_estimators = 10000, seed = 0)
    evalset = [(X_predict_full.loc[train_fold],budget_data[y_var].loc[train_fold])]
    model.set_params(**p)
    
    model.fit(X_predict_full.loc[train_fold], 
              budget_data[y_var].loc[train_fold],
              early_stopping_rounds = 10,
              eval_set = evalset)
        
    predict_label = model.predict(X_predict_full.loc[test_fold])
    
    from sklearn.metrics import accuracy_score
    
    score = accuracy_score(budget_data[y_var].loc[test_fold], predict_label)        
    return score,model

def train_prediction_model_return_score_logistic(y_var,
                                                budget_data,
                                                X_predict_full,
                                                train_fold,
                                                test_fold,
                                                p):
    from sklearn.linear_model import SGDClassifier
    model = SGDClassifier(random_state=0)
    model.set_params(**p)
    
    
    model.fit(X_predict_full.loc[train_fold], 
              budget_data[y_var].loc[train_fold])
    
    score = model.score(X_predict_full.loc[test_fold],
                        budget_data[y_var].loc[test_fold])
    return score,model

def train_prediction_model_return_score_lasso(y_var,
                                                budget_data,
                                                X_predict_full,
                                                train_fold,
                                                test_fold,
                                                p):
    from sklearn.linear_model import SGDRegressor
    model = SGDRegressor(random_state=0)
    model.set_params(**p)
    
    
    model.fit(X_predict_full.loc[train_fold], 
              budget_data[y_var].loc[train_fold])
    predict = model.predict(X_predict_full.loc[test_fold])
    predict_label = [1 if pred > 0.5 else 0 for pred in predict]
    
    from sklearn.metrics import accuracy_score
    
    score = accuracy_score(budget_data[y_var].loc[test_fold], predict_label)
    return score,model

def train_prediction_model_return_score(y_var,
                                        budget_data,
                                        X_predict_full,
                                        train_fold,
                                        model, 
                                        test_fold,
                                        p):
    if model == 'xgboost':
        score,trained_model = train_prediction_model_return_score_xgboost(y_var,
                                                                  budget_data,
                                                                  X_predict_full,
                                                                  train_fold,
                                                                  test_fold,
                                                                  p)
    else:
        pass
    
    if model == 'logistic':
        score,trained_model = train_prediction_model_return_score_logistic(y_var,
                                                budget_data,
                                                X_predict_full,
                                                train_fold,
                                                test_fold,
                                                p)
    else:
        pass
    
    if model == 'lasso':
        score,trained_model = train_prediction_model_return_score_lasso(y_var,
                                                budget_data,
                                                X_predict_full,
                                                train_fold,
                                                test_fold,
                                                p)
    else:
        pass
    
    if model == 'linear':
        score,trained_model = train_prediction_model_return_score_lasso(y_var,
                                                budget_data,
                                                X_predict_full,
                                                train_fold,
                                                test_fold,
                                                p)
    else:
        pass
    
    return score,trained_model

def run_prediction_return_average_score(y_var,
                                model,
                                train_index,
                                p,
                                budget_data,
                                X_predict_full,
                                sampling_method):
    score_list = []
    split = 5
    for train_fold, test_fold in return_train_test_split(y_var = y_var,
                                                                   budget_data = budget_data.loc[train_index],
                                                                   sampling_method = sampling_method,
                                                                   split = split):
        score,trained_model = train_prediction_model_return_score(y_var = y_var,
                                                    budget_data = budget_data.loc[train_index],
                                                    X_predict_full = X_predict_full.loc[train_index],
                                                    train_fold = train_fold,
                                                    model = model, 
                                                    test_fold = test_fold,
                                                    p = p)
        score_list.append(score)
        print(score)
        
    return sum(score_list)/split

def search_hyperparameter(y_var,
                          model,
                          train_index,
                          budget_data,
                          X_predict_full,
                          sampling_method):
    best_score = 0
    best_p = {}
    param_grid = grid_search_dictionary[model]
    
    for p in list(param_grid):
        score = run_prediction_return_average_score(y_var = y_var,
                                               model = model,
                                               train_index = train_index,
                                               p = p,
                                               budget_data = budget_data,
                                               X_predict_full = X_predict_full,
                                               sampling_method = sampling_method)
        print(score)
        if score>best_score:
            print('parameter updated')
            print(p)
            print('score is')
            print(score)
            best_score = score
            best_p = p
    
    return best_score,best_p

def do_prediction(y_var, 
                  model, 
                  train_index,
                  test_index,
                  p,
                  budget_data,
                  X_predict_full,
                  sampling_method,
                  data_option,
                  count):
    prediction_dir = os.getcwd()+f'/data/working/prediction_{model}_{sampling_method}_{data_option}/{y_var}_fold{count}'
    os.mkdir(prediction_dir)
    
    score,trained_model = train_prediction_model_return_score(y_var = y_var,
                                                    budget_data = budget_data,
                                                    X_predict_full = X_predict_full,
                                                    train_fold = train_index,
                                                    model = model, 
                                                    test_fold = test_index,
                                                    p = p)
    budget_data_save = budget_data.copy()
    if model in ['xgboost','logistic']:
        predict_proba = trained_model.predict_proba(X_predict_full)
        predict_proba = [p[0] for p in predict_proba]
        #this line should have been predict_proba = [p[0] for p in predict_proba]
    else:
        predict_proba = trained_model.predict(X_predict_full)
        
    budget_data_save[y_var+'_predicted'] = predict_proba
    budget_data_save[y_var+'_train_sample'] = np.nan
    budget_data_save.loc[train_index,y_var+'_train_sample'] = 1
    budget_data_save.loc[test_index,y_var+'_train_sample'] = 0
    
    cols_keep = ['cod_mun','year','for_prediction2','for_prediction']
    cols_keep = cols_keep + [y_var+'_predicted',y_var+'_train_sample']
    budget_data_save = budget_data_save[cols_keep]
    
    budget_data_save.to_csv(prediction_dir+f'/predict_fold_{count}.csv')
    
    import pickle as pk
    pk.dump(trained_model,open(prediction_dir+f'/fold_{count}_model.pickle','wb'))


def do_prediction_fpm(y_var, 
                  model, 
                  train_index,
                  test_index,
                  p,
                  budget_data,
                  X_predict_full,
                  sampling_method,
                  data_option,
                  count):
    prediction_dir = os.getcwd()+f'/data/working/prediction_{model}_{sampling_method}_{data_option}_fpm/{y_var}_fold{count}'
    os.mkdir(prediction_dir)
    
    score,trained_model = train_prediction_model_return_score(y_var = y_var,
                                                    budget_data = budget_data,
                                                    X_predict_full = X_predict_full,
                                                    train_fold = train_index,
                                                    model = model, 
                                                    test_fold = test_index,
                                                    p = p)
    budget_data_save = budget_data.copy()
    if model in ['xgboost','logistic']:
        predict_proba = trained_model.predict_proba(X_predict_full)
        predict_proba = [p[0] for p in predict_proba]
        #this line should have been predict_proba = [p[0] for p in predict_proba]
    else:
        predict_proba = trained_model.predict(X_predict_full)
        
    budget_data_save[y_var+'_predicted'] = predict_proba
    budget_data_save[y_var+'_train_sample'] = np.nan
    budget_data_save.loc[train_index,y_var+'_train_sample'] = 1
    budget_data_save.loc[test_index,y_var+'_train_sample'] = 0
    
    cols_keep = ['cod_mun','year','for_prediction2','for_prediction']
    cols_keep = cols_keep + [y_var+'_predicted',y_var+'_train_sample']
    budget_data_save = budget_data_save[cols_keep]
    
    budget_data_save.to_csv(prediction_dir+f'/predict_fold_{count}.csv')
    
    import pickle as pk
    pk.dump(trained_model,open(prediction_dir+f'/fold_{count}_model.pickle','wb'))

def do_prediction_select_i(y_var, 
                  model, 
                  train_index,
                  test_index,
                  p,
                  budget_data,
                  X_predict_full,
                  sampling_method,
                  data_option,
                  count,
                  i):
    prediction_dir = os.getcwd()+f'/data/working/prediction_{model}_{sampling_method}_{data_option}_{int(i)}/{y_var}_fold{count}'
    os.mkdir(prediction_dir)
    
    score,trained_model = train_prediction_model_return_score(y_var = y_var,
                                                    budget_data = budget_data,
                                                    X_predict_full = X_predict_full,
                                                    train_fold = train_index,
                                                    model = model, 
                                                    test_fold = test_index,
                                                    p = p)
    budget_data_save = budget_data.copy()
    if model in ['xgboost','logistic']:
        predict_proba = trained_model.predict_proba(X_predict_full)
        predict_proba = [p[0] for p in predict_proba]
        #this line should have been predict_proba = [p[0] for p in predict_proba]
    else:
        predict_proba = trained_model.predict(X_predict_full)
        
    budget_data_save[y_var+'_predicted'] = predict_proba
    budget_data_save[y_var+'_train_sample'] = np.nan
    budget_data_save.loc[train_index,y_var+'_train_sample'] = 1
    budget_data_save.loc[test_index,y_var+'_train_sample'] = 0
    
    cols_keep = ['cod_mun','year','for_prediction2','for_prediction']
    cols_keep = cols_keep + [y_var+'_predicted',y_var+'_train_sample']
    budget_data_save = budget_data_save[cols_keep]
    
    budget_data_save.to_csv(prediction_dir+f'/predict_fold_{count}.csv')
    
    import pickle as pk
    pk.dump(trained_model,open(prediction_dir+f'/fold_{count}_model.pickle','wb'))

def merged_dataset(model_name,sampling_method,data_option, folds=5):
    budget_data_raw = pd.read_stata(wd+'/data/final/panel_budget_corruption.dta',
                                    convert_missing=False)
    truth = budget_data_raw[['cod_mun', 'year','corr1','corr2','narrow1']]
    prediction_dir = os.getcwd()+f'/data/working/prediction_{model_name}_{sampling_method}_{data_option}'
    for target in ['narrow1','corr1','corr2']: 
        list_of_df = []
        for count in range(folds):
            df = pd.read_csv(prediction_dir+f'/{target}_fold{count}/predict_fold_{count}.csv')
            if model_name in ['xgboost','logistic']:
              #this fixed the line 300 
                df[f'{target}_predicted'] = 1 - df[f'{target}_predicted']
            df = df[['cod_mun', 'year', 'for_prediction', 'for_prediction2',
                     f'{target}_predicted',f'{target}_train_sample']]
            df.columns = ['cod_mun', 'year', 'for_prediction', 'for_prediction2',
                     f'{target}_predicted_{count}',f'{target}_train_sample_{count}']
            list_of_df.append(df)
        merged_df = list_of_df[0]
        for count in range(1,folds):
            merged_df = merged_df.merge(list_of_df[count].drop(columns = ['for_prediction', 'for_prediction2']), 
                                        on = ['cod_mun','year'])
        truth = merged_df.merge(truth, on = ['cod_mun', 'year'])
    return truth

def produce_cv_predictions_f(model_name,sampling_method,data_option, folds=5):
    import warnings
    merged_df = merged_dataset(model_name,sampling_method,data_option,folds=5)

    
    print(model_name,sampling_method,data_option)
    print(merged_df.columns.tolist(), flush=True)
    for t in ['narrow1','corr1','corr2']:
        merged_df[f'{t}_cv_prediction'] = np.nan
        if t == 'narrow1':
            merged_df.loc[merged_df[(merged_df.for_prediction!=1)].index,f'{t}_cv_prediction'] = merged_df[(merged_df.for_prediction!=1)][[f'{t}_predicted_{str(i)}' for i in range(folds)]].mean(axis=1)
        else:
            merged_df.loc[merged_df[(merged_df.for_prediction2!=1)].index,f'{t}_cv_prediction'] = merged_df[(merged_df.for_prediction2!=1)][[f'{t}_predicted_{str(i)}' for i in range(folds)]].mean(axis=1)
            
        merged_df[f'{t}_oof_prediction'] = np.nan
        if t == 'narrow1':
            for i in range(folds):
                merged_df.loc[merged_df[(merged_df.for_prediction==1)&(merged_df[f'{t}_train_sample_{str(i)}']!=1)].index,f'{t}_oof_prediction'] = merged_df[(merged_df.for_prediction==1)&(merged_df[f'{t}_train_sample_{str(i)}']!=1)][f'{t}_predicted_{str(i)}']
        else:
            for i in range(folds):
                merged_df.loc[merged_df[(merged_df.for_prediction2==1)&(merged_df[f'{t}_train_sample_{str(i)}']!=1)].index,f'{t}_oof_prediction'] = merged_df[(merged_df.for_prediction2==1)&(merged_df[f'{t}_train_sample_{str(i)}']!=1)][f'{t}_predicted_{str(i)}']

    merged_df.to_csv(f'./data/working/merged/{model_name}_{sampling_method}_{data_option}.csv')
    return merged_df
