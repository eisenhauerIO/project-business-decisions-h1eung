import pandas as pd
import os
from zipfile import ZipFile
import requests
from collections import Counter
import re
from random import shuffle
from string import punctuation
punc_remover = str.maketrans('','',punctuation)
from glob import glob

file_url = 'https://zenodo.org/records/15129902/files/text_files.zip'
zip_path = './data/source/audit_reports/text_files.zip'

# Ensure the output directory exists
os.makedirs(os.path.dirname(zip_path), exist_ok=True)

# Download the file
print("Downloading dataset from Zenodo...")
with requests.get(file_url, stream=True) as response:
    response.raise_for_status()
    with open(zip_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
print(f"Download complete: {zip_path}")


codebooks = glob('./data/source/budgets/CT*.xlsx')
print(codebooks)

lexicon = []

varnames = {}

for codebook in codebooks:
    label = codebook[7:].split()[0]
    print(label)
    df = pd.read_excel(codebook)
    for i, row in df.iterrows():
        desc = row.DESCRICAO
        desc2 = row['Titulo Finbra']
        varname = ''.join(desc2.split()).translate(punc_remover)
    
        if '=' in desc:
            desc = desc.split('=')[0].strip()
        if desc in lexicon:
            print(desc)
        else:
            lexicon.append(desc)
            varnames[desc] = varname
        if desc2 in lexicon:
            print(desc2)
        else:
            lexicon.append(desc2)
            varnames[desc2] = varname



longstring = ''
num_not_used = 0

with ZipFile('./data/source/audit_reports/text_files.zip', 'r') as zfile:
    members = zfile.namelist()
    shuffle(members)
    for member in members:
        txt = zfile.open(member,'r').read().decode()
        if len(txt) < 10:
            num_not_used += 1
            continue
        nopunc = txt.lower().translate(punc_remover)
        words = ' '.join(nopunc.split())
        longstring += words + ' '
        


lexicon.sort(key = lambda x: len(x), reverse=True)

counts = Counter()

for item in lexicon:
    keyword = ' '.join(item.lower().translate(punc_remover).split())
    matches = re.finditer(keyword,longstring)
    count = len(tuple(matches))
    print(keyword,'\n',count,'\n\n')
    counts[varnames[item]] = count

output = []

for k, v in counts.items():
    row = k, v
    output.append(row)

df2 = pd.DataFrame(output,columns=['varname','count'])
df2.sort_values('count',inplace=True)
df2.to_csv('./output/appendix_tables/table_c6.csv',index=False)

# Load the files

feature_importance = pd.read_csv("./data/working/prediction_xgboost_nosample_b_feature_importance.csv")

 
# Rename the feature column to varname to match the desc-counts.csv structure

df2 = df2.rename(columns={"varname": "feature"})

 

merged_df_left_join = pd.merge(df2, feature_importance[['feature', 'weight_avg']], on="feature", how="left")

 
# Drop observation with controleinterno in desc_counts

merged_df_left_join = merged_df_left_join[merged_df_left_join["feature"] != "controleinterno"]

merged_df_left_join.to_csv("./data/working/merged_desc_counts_weight_avg_left_join.csv", index=False)

 