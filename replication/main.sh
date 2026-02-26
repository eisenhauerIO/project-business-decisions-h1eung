# Setup pipenv properly and install your packages explicitly - 
# This script is designed to be run from the root of the repository 
# If you are having issues with pipenv, try running the script in a clean environment from the terminal
pipenv --rm  # Optional: Remove existing corrupted env
pipenv --python $(which python3)
pipenv install pandas numpy scipy scikit-learn==0.24.0 xgboost==1.7.6 matplotlib seaborn openpyxl==3.1.2
pipenv run python -c "import pandas, numpy, sklearn, xgboost; print('Pipenv env ready.')"

# Running firt stata scripts - generating the data for the predictions
stata -b do "code_stata/01_master.do"

# Delete existing predictions
rm -rf ./data/working/prediction*

# Run predictions and generating the python based outputs
pipenv run python code_python/predictions_1000_no_tuning.py nosample b xgboost
pipenv run python code_python/predictions_1000_no_tuning_hold_out_valid.py nosample b xgboost
pipenv run python code_python/predictions_fpm.py nosample b xgboost
pipenv run python code_python/predictions.py nosample b linear
pipenv run python code_python/predictions.py nosample b xgboost
pipenv run python code_python/predictions.py nosample b lasso
pipenv run python code_python/predictions.py nosample b logistic
pipenv run python code_python/predictions.py sample b xgboost
pipenv run python code_python/predictions.py sample bd xgboost
pipenv run python code_python/predictions.py sample d xgboost
pipenv run python code_python/predictions_half.py nosample b xgboost
pipenv run python code_python/merge_bootstrap.py
pipenv run python code_python/metrics.py
pipenv run python code_python/generate_plots.py
pipenv run python code_python/policy_analysis.py
rm -rf ./data/working/prediction_xgboost_nosample_b_perturbed
pipenv run python code_python/predictions_with_local_interpretability.py
pipenv run python code_python/hyperparam_selection.py 
pipenv run python code_python/local_interpretability.py
pipenv run python code_python/feature_importance.py
pipenv run python code_python/table_c5.py
pipenv run python  code_python/create_audit_reports.py 

# Running second stata scripts - generating the stata based outputs
stata -b do "code_stata/02_master.do"

