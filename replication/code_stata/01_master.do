****************************************
* SETUPS SYSTEM AND CURRENT DIRECTORIES*
****************************************
global path_start "~/replication_pack_aej_policy"
global path_dropbox "~/replication_pack_aej_policy"
global folder "~/replication_pack_aej_policy"

sysdir set OLDPLACE "${path_start}/code_stata/ado"
sysdir set PLUS "${path_start}/code_stata/ado"
sysdir set PERSONAL "${path_start}/code_stata/ado"

sysdir 

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

*to generate dataset: ancillary datasets
do "$path_start/code_stata/generate_datasets/01_budget_predictions.do" 
do "$path_start/code_stata/generate_datasets/02_cleaning_ancillary_datasets.do" 

