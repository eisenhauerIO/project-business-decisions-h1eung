# Text Audit Repository

**DO NOT RUN THE FOLLOWING COMMANDS: THE COMMAND IS ALREADY INTEGRATED IN THE SCRIPT downstream_analysis.sh - this is provided for reference!**

Unfortunately the links we used are no longer functional. Nevertheless for completeness we provide the relevant code and data:

For the PDF collection run (this code no longer works due to API changes):
    pipenv run python ./code_python/scrape_pdfs.py

For the PDF data extraction run:
    pipenv run python ./code_python/process_pdfs.py

Note that we have changed the analysis code such that instead of the downloaded extracted PDFs it reads in a supplied ZIP with the extracted PDFs as we have downloaded them. 

For the analysis run:
    pipenv run python ./code_python/create_audit_reports.py

