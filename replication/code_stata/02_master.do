****************************************
* SETUPS SYSTEM AND CURRENT DIRECTORIES*
****************************************
global path_start "D:/aej_replication"
global path_dropbox "D:/aej_replication"
global folder "D:/aej_replication"

sysdir set OLDPLACE "${path_start}/code_stata/ado"
sysdir set PLUS "${path_start}/code_stata/ado"
sysdir set PERSONAL "${path_start}/code_stata/ado"


/*install packs required*/
ssc install binscatter, replace 
net install binsreg, from("https://raw.githubusercontent.com/nppackages/binsreg/master/stata")
ssc install coefplot, replace 
ssc install csdid, replace 
ssc install ranktest, replace 
ssc install ivreg2, replace 
ssc install parmest, replace 
ssc install reghdfe, replace
ssc install ftools, replace
ssc install estout, replace 
ssc install drdid, replace 


***********************
* CLEANING MASTER FILE*
***********************

*to generate dataset: predictions
do "$path_start/code_stata/generate_datasets/03_cleaning_predictions.do" 

*to generate dataset: dataset analysis transfers 
do "$path_start/code_stata/generate_datasets/04_cleaning_dataset_AnaysisTransfers.do" 

*to generate dataset: dataset analysis audits 
do "$path_start/code_stata/generate_datasets/05_cleaning_dataset_AnaysisAudit.do" 


*****************************************************************
* ANALYSIS MASTER FILE											*
*****************************************************************

*****************************************************************
* I. TABLES	(MAIN)												*
*****************************************************************

do "$path_start/code_stata/analysis/Table1.do"
do "$path_start/code_stata/analysis/Table3.do"

*****************************************************************
* II. FIGURES (MAIN)											*
*****************************************************************

do "$path_start/code_stata/analysis/Figure2.do"
do "$path_start/code_stata/analysis/Figure4.do"

*****************************************************************
* III. TABLES (APPENDIX)`										*
*****************************************************************

do "$path_start/code_stata/analysis/TableD8.do"
do "$path_start/code_stata/analysis/TableD9.do"
do "$path_start/code_stata/analysis/TableD10.do"
do "$path_start/code_stata/analysis/TableD11_panel_A.do"
do "$path_start/code_stata/analysis/TableD11_panels_B_C.do"
do "$path_start/code_stata/analysis/TableE12.do"
do "$path_start/code_stata/analysis/TableE13_columns_1_3.do"
do "$path_start/code_stata/analysis/TableE13_columns_4_9.do"


*****************************************************************
* IV. FIGURES (APPENDIX)										*
*****************************************************************

do "$path_start/code_stata/analysis/FigureA2.do"
do "$path_start/code_stata/analysis/FigureB3.do"
do "$path_start/code_stata/analysis/FigureE5.do"
do "$path_start/code_stata/analysis/FigureE6.do"
do "$path_start/code_stata/analysis/FigureE7.do"
do "$path_start/code_stata/analysis/FigureE8.do"
