import sys
import os



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

import utilities_prediction_half as utilities

script_name,sampling_method,data_option,model_name = sys.argv


prediction_dir = os.getcwd()+f'/data/working/prediction_{model_name}_{sampling_method}_{data_option}_half'
os.mkdir(prediction_dir)




#make dataset
budget_data, X_predict_full = utilities.preparing_dataset(option = data_option,
                                                          test = False)



#make predictions for each fold
for target in ['narrow1','corr1','corr2']:
    for count,fold in enumerate(utilities.return_train_test_split(y_var = target,
                                                                            budget_data = budget_data,
                                                                            sampling_method = sampling_method,
                                                                            split = 2)):        
        train_index = fold[0]
        test_index = fold[1]
        
        best_score,best_p = utilities.search_hyperparameter(y_var = target,
                                                            model = model_name,
                                                            train_index = train_index,
                                                            budget_data = budget_data,
                                                            X_predict_full = X_predict_full,
                                                            sampling_method = sampling_method)
        utilities.do_prediction(y_var = target, 
                                model = model_name,
                                train_index = train_index,
                                test_index = test_index,
                                p = best_p,
                                budget_data = budget_data,
                                X_predict_full = X_predict_full,
                                sampling_method = sampling_method,
                                data_option = data_option,
                                count = count)

