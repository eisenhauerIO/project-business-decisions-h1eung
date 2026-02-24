
import sys
import os
import glob

import pandas as pd

import utilities_prediction

import pickle as pk




def return_dataset(model, sampling_method, data_option):
   
    
    #load features
    budget_data, X_predict_full = utilities_prediction.preparing_dataset(option = data_option, test = False)
    
    ##load xgbmodel
    for target in ['narrow1']:
        y_var = target
        try:
            os.mkdir(f'./data/working/prediction_{model}_{sampling_method}_{data_option}_perturbed')
        except:
            pass
        
        
        for count in range(5):
            fold = count
            prediction_dir = f'./data/working/prediction_{model}_{sampling_method}_{data_option}/{y_var}_fold{count}'
            df = pd.read_csv(prediction_dir+f'/predict_fold_{count}.csv')
            model_test = pk.load(open(f'./data/working/prediction_{model}_{sampling_method}_{data_option}/{target}_fold{fold}/fold_{fold}_model.pickle','rb'))
            model_test.set_params(**{'predictor': 'cpu_predictor'})
            for v in X_predict_full.columns:
                v_sd = X_predict_full[v].std()
                print(v)
                X_predict_full_0 = X_predict_full.copy()
                X_predict_full_0[v] = X_predict_full[v]+v_sd
                df[y_var+'_predicted_'+v+'_0'] = [p[0] for p in model_test.predict_proba(X_predict_full_0)]
                X_predict_full_1 = X_predict_full.copy()
                X_predict_full_1[v] = X_predict_full[v]-v_sd
                df[y_var+'_predicted_'+v+'_1'] = [p[0] for p in model_test.predict_proba(X_predict_full_1)]
                del X_predict_full_0, X_predict_full_1
            #setup new directory
            new_prediction_dir = f'./data/working/prediction_{model}_{sampling_method}_{data_option}_perturbed/{y_var}_fold{count}'
            os.mkdir(new_prediction_dir)    
            df.to_csv(new_prediction_dir+f'/predict_fold_{count}.csv')
            del df


return_dataset('xgboost', 'nosample', 'b')