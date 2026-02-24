import pandas as pd

import glob

import os

locally_perturbed = pd.read_csv('./data/working/locally_perturbed_reshaped.csv')
feature_code_mapping = pd.read_csv('./output/feature_code_mapping.csv')




feature_importances = pd.read_csv('./data/working/prediction_xgboost_nosample_b_feature_importance.csv')

# join feature_code_mapping with feature_importances on feature
joined = feature_importances.merge(feature_code_mapping,how='inner',on='feature')

joined = joined[['feature','code','weight_avg']]


# sort by weight_avg
joined = joined.sort_values(by='weight_avg',ascending=False)
print(joined.head())
print(joined.shape)

rel = locally_perturbed

for i in range(797):
    rel.loc[rel['subtract'] == 1, f'd{i}'] = rel['narrow1_predicted'] - rel[f'v{i}']
    rel.loc[rel['subtract'] == 0, f'd{i}'] = rel[f'v{i}'] - rel['narrow1_predicted']

# for all 'code' remove the first letter v
joined.code = joined.code.apply(lambda x: x[1:])    

# now for every 'code' of joined we want the min, max and avg of the column colunn d{i} of rel (for all i!)

joined['avg'] = joined.code.apply(lambda x: rel[f'd{x}'].mean())
joined['min'] = joined.code.apply(lambda x: rel[f'd{x}'].min())
joined['max'] = joined.code.apply(lambda x: rel[f'd{x}'].max())

# re-add the v to the code
joined.code = joined.code.apply(lambda x: 'v'+x)

# sort by code
joined = joined.sort_values(by='weight_avg',ascending=False)
# only show top 35
# joined = joined.head(35)

joined.to_csv('./output/appendix_tables/table_c5.csv',index=False)