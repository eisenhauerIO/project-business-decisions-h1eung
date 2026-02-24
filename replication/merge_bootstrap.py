import glob
import os

import utilities_prediction_bootstrap as utilities_prediction_bootstrap

folder_names = [folder for folder in glob.glob('data/working/*/')]
# isolate the top level folder name
folder_names = [os.path.basename(os.path.dirname(folder)) for folder in folder_names]

# filter to only use folders that start with 'prediction_'
folder_names = [folder for folder in folder_names if folder.startswith('prediction_')]

for folder in folder_names:

    split = folder.split('_')
  
    data_option = split[3]
    sampling_method = split[2]
    model_name = split[1]

    if 'holdout' in folder and 'bootstrap' in folder:
        prediction_dir = "./data/working/" + folder
        cv_dir =f'./data/working/merged/{model_name}_{sampling_method}_{data_option}_bootstrap_holdout.csv'
        utilities_prediction_bootstrap.produce_cv_predictions_holdout(model_name,sampling_method,data_option, folds=1000, t_arr=['narrow1'],prediction_dir=prediction_dir,cv_dir=cv_dir)
        
    elif 'holdout' not in folder and 'bootstrap' in folder:
        prediction_dir = "./data/working/" + folder
        cv_dir =f'./data/working/merged/{model_name}_{sampling_method}_{data_option}_bootstrap.csv'
        utilities_prediction_bootstrap.produce_cv_predictions(model_name,sampling_method,data_option, folds=1000, t_arr=['narrow1'],prediction_dir=prediction_dir,cv_dir=cv_dir)

    else:
        continue