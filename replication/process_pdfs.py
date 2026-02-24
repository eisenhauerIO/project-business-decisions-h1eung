import pandas as pd
import pdfminer.high_level


import glob
import os

PDF_glob = "./data/source/audit_reports/*.pdf"
TXT_dir = "./data/source/audit_reports/"

os.makedirs(TXT_dir, exist_ok=True)


#  Convert the PDFs to text
def pdf_to_text_store(pdf_path, txt_path):
    text = pdfminer.high_level.extract_text(pdf_path)
    with open(txt_path, "w") as file_object:
        file_object.write(text)


for pdf_path in glob.glob(PDF_glob):
    file_name = str(os.path.basename(pdf_path))
    file_name = file_name.replace(".pdf",".txt")
    txt_path = TXT_dir + "/" + file_name
    if os.path.exists(txt_path):
        continue # skip pdf file if text file already exists
    try:
        pdf_to_text_store(pdf_path, txt_path)
    except:
        print(f"Error in file {pdf_path}")
   