#!/usr/bin/env python
# coding: utf-8

import sys
import os



'''
We use the following parameters:

'''


#The data options
#1.only Budget variables - b
#2.only demographic variables - d 
#3.Budget and demographic variables. - bd

#The sampling methods
#1.random - nosample
#2.sample by municipality - sample

#The models
#1.xgboost - xgboost
#2.logistic - logistic regression
#2.lasso - lasso regression
#2.linear - lasso regression with no regularization



script_name,sampling_method,data_option,model_name = sys.argv



from datetime import date
prediction_dir = os.getcwd()+f'/data/working/prediction_{model_name}_{sampling_method}_{data_option}_bootstrap_holdout'
os.mkdir(prediction_dir)



import utilities_prediction_bootstrap as utilities_prediction_bootstrap

from sklearn.model_selection import train_test_split



# 1. we train 1000 predictors with a random 80 - 20 (train - validation) split


budget_data, X_predict_full = utilities_prediction_bootstrap.preparing_dataset(option = data_option,
                                                          test = False)


assert sampling_method == 'nosample'

# taken from utilities.return_train_test_split (note this only works for narrow1 prediction)
index = list(budget_data[budget_data['for_prediction']==1].dropna(subset=["narrow1"]).index)
    
# split the index:

full_train_index, hold_out_test_index = train_test_split(index, test_size=0.2, train_size=0.8, random_state=42)

# the test_set is only used at the end



for counter in range(1000):

    train_index, test_index = train_test_split(full_train_index, test_size=0.2, train_size=0.8, random_state=counter)

    # take the default options
    best_p = {'reg_alpha': 0,
                                'reg_lambda': 1,
                                'max_depth': 6,
                                'learning_rate': 0.3,
                                'min_child_weight': 1,
                                'objective': 'binary:logistic',
                                'eval_metric':'error',
                                'gpu_id': 0,
                                'silent': 1}


    utilities_prediction_bootstrap.do_prediction(y_var = "narrow1", 
                            model = model_name,
                            train_index = train_index,
                            test_index = test_index,
                            p = best_p,
                            budget_data = budget_data,
                            X_predict_full = X_predict_full,
                            sampling_method = sampling_method,
                            data_option = data_option,
                            count = counter,
                            prediction_dir = prediction_dir,
                            hold_out_test_index=hold_out_test_index)

