#!/usr/bin/env python
# coding: utf-8

import json
import time
import random
import tqdm
import subprocess
from pathlib import Path
import os

import pandas as pd
import requests
import tqdm

OUTPUT_DIR = './data/source/audit_reports'

URL = "https://auditoria.cgu.gov.br/pesquisar?draw=0&colunaOrdenacao=dataPublicacao&direcaoOrdenacao=DESC&tamanhoPagina=15&offset={offset}&titulo=&linhaAtuacao=4&de=&ate=&orgaos=&ujtcus=&estados=&municipios=&fefs=&palavraChave=Sorteio+de+Munic%C3%ADpios"



def get_dataframe_for_offset(offset):
    r = requests.get(URL.format(offset=offset))
    result_string = r.text
    data = json.loads(result_string)["data"]
    return pd.DataFrame.from_records(data)



offsets = range(0, 2325 + 1, 25)

dataframes = []

for o in tqdm.tqdm(offsets):
    dataframes.append(get_dataframe_for_offset(o))
    time.sleep(random.randint(0, 5))



df = pd.concat(dataframes, ignore_index=True)
df.head()

df = df.set_index('id')
df.head()


len(df)


print("creating: ", OUTPUT_DIR)
os.makedirs(OUTPUT_DIR, exist_ok=True)


df.to_csv(Path(OUTPUT_DIR) / "metadata.csv")


def retrieve_file(file_id):
    file_url = f"https://eaud.cgu.gov.br/relatorios/download/{file_id}"
    output_path = f"{OUTPUT_DIR}/{file_id}.pdf"
    subprocess.call(f"wget {file_url} -O {output_path}".split())


for file_id in tqdm.tqdm(df.index):
    if not (Path(OUTPUT_DIR) / f"{file_id}.pdf").exists():
        retrieve_file(file_id)
        time.sleep(random.randint(0, 5))


        

