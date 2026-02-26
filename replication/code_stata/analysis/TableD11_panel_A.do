***Predicting corruption in Brazil - Replication files***


**-- Analysis

use "$folder/data/final/dataset_AnalysisTransfer.dta", clear

drop narrow1_predictionT_Av narrow1_predictionT narrow1_auditT narrow1_predictionT_d narrow1_predictionT_noFPM

forvalues i=0(1)999{

preserve

**-- Import corruption data and final cleaning

merge 1:1 term cod_mun using "$folder/data/working/bootstrap/predict_fold_`i'.dta"
*dallo using non assegnate 5,524, dal master non assegnati 426 obs.
drop if _merge==2
drop _merge 

drop if narrow1_predictionT_Av==.

rename narrow1_predictionT_Av narrow1_predictionT

replace narrow1_predictionT=1-narrow1_predictionT
*va usato l inverso

gen population_term_2=population_term^2
gen population_term_3=population_term^3

encode state_code, gen(state_code_N)
encode city_code, gen(city_code_N)

sort city_code term

**-- Analysis

qui xi: reg fpm_CPI_term fpm_CPI_term_predict_v2 population_term population_term_2 population_term_3 i.term i.state_code_N if audit_brollo==1,r cluster(city_code_N)
parmest, saving("$folder/data/working/bootstrap_outputs/estimates_1_1_fold_`i'", replace)

qui xi: reg narrow1_predictionT fpm_CPI_term_predict_v2 population_term population_term_2 population_term_3 i.term i.state_code_N if audit_brollo==1,r cluster(city_code_N)
parmest, saving("$folder/data/working/bootstrap_outputs/estimates_2_1_fold_`i'", replace)


qui xi: ivreg2 narrow1_predictionT  population_term population_term_2 population_term_3 (fpm_CPI_term=fpm_CPI_term_predict_v2) i.term i.state_code_N if audit_brollo==1,r cluster(city_code_N)
parmest, saving("$folder/data/working/bootstrap_outputs/estimates_3_1_fold_`i'", replace)


qui xi: reg fpm_CPI_term fpm_CPI_term_predict_v2 population_term population_term_2 population_term_3 i.term i.state_code_N if audit_brollo!=.,r cluster(city_code_N)
parmest, saving("$folder/data/working/bootstrap_outputs/estimates_1_2_fold_`i'", replace)

qui xi: reg narrow1_predictionT fpm_CPI_term_predict_v2 population_term population_term_2 population_term_3 i.term i.state_code_N if audit_brollo!=.,r cluster(city_code_N)
parmest, saving("$folder/data/working/bootstrap_outputs/estimates_2_2_fold_`i'", replace)

qui xi: ivreg2  narrow1_predictionT population_term population_term_2 population_term_3 (fpm_CPI_term=fpm_CPI_term_predict_v2) i.term i.state_code_N if audit_brollo!=.,r cluster(city_code_N)
parmest, saving("$folder/data/working/bootstrap_outputs/estimates_3_2_fold_`i'", replace)


qui xi: reg fpm_CPI_term fpm_CPI_term_predict_v2 population_term population_term_2 population_term_3 i.term i.state_code_N if audit_brollo==0,r cluster(city_code_N)
parmest, saving("$folder/data/working/bootstrap_outputs/estimates_1_3_fold_`i'", replace)

qui xi: reg narrow1_predictionT fpm_CPI_term_predict_v2 population_term population_term_2 population_term_3 i.term i.state_code_N if audit_brollo==0,r cluster(city_code_N)
parmest, saving("$folder/data/working/bootstrap_outputs/estimates_2_3_fold_`i'", replace)

qui xi: ivreg2  narrow1_predictionT population_term population_term_2 population_term_3 (fpm_CPI_term=fpm_CPI_term_predict_v2) i.term i.state_code_N if audit_brollo==0,r cluster(city_code_N)
parmest, saving("$folder/data/working/bootstrap_outputs/estimates_3_3_fold_`i'", replace)

restore
}


*********************************************************
****---- 		Recover bootstrapped SE 		 ----****
*********************************************************
*Note: this code creates bootstrapped standard errors which have been manually added in Table D11, panel A.

**-- Coefficient 2_1

use "$folder/data/working/bootstrap_outputs/estimates_2_1_fold_0", clear

keep if parm=="fpm_CPI_term_predict_v2"

forvalues i=1(1)999{

append using "$folder/data/working/bootstrap_outputs/estimates_2_1_fold_`i'"

keep if parm=="fpm_CPI_term_predict_v2"

}

keep estimate stderr

rename estimate estimate2_1
rename stderr stderr2_1

gen ID=_n

save "$folder/data/working/bootstrap_outputs/estimates_2_1_All", replace


**-- Coefficient 3_1

append using "$folder/data/working/bootstrap_outputs/estimates_3_1_fold_0"

keep if parm=="fpm_CPI_term"

forvalues i=1(1)999{

append using "$folder/data/working/bootstrap_outputs/estimates_3_1_fold_`i'"

keep if parm=="fpm_CPI_term"

}

keep estimate stderr

rename estimate estimate3_1
rename stderr stderr3_1

gen ID=_n

save "$folder/data/working/bootstrap_outputs/estimates_3_1_All", replace


**-- Coefficient 2_2

use "$folder/data/working/bootstrap_outputs/estimates_2_2_fold_0", clear

keep if parm=="fpm_CPI_term_predict_v2"

forvalues i=1(1)999{

append using "$folder/data/working/bootstrap_outputs/estimates_2_2_fold_`i'"

keep if parm=="fpm_CPI_term_predict_v2"

}

keep estimate stderr

rename estimate estimate2_2
rename stderr stderr2_2

gen ID=_n

save "$folder/data/working/bootstrap_outputs/estimates_2_2_All", replace


**-- Coefficient 3_2

use "$folder/data/working/bootstrap_outputs/estimates_3_2_fold_0", clear

keep if parm=="fpm_CPI_term"

forvalues i=1(1)999{

append using "$folder/data/working/bootstrap_outputs/estimates_3_2_fold_`i'"

keep if parm=="fpm_CPI_term"

}

keep estimate stderr

rename estimate estimate3_2
rename stderr stderr3_2

gen ID=_n

save "$folder/data/working/bootstrap_outputs/estimates_3_2_All", replace


**-- Coefficient 2_3

use "$folder/data/working/bootstrap_outputs/estimates_2_3_fold_0", clear

keep if parm=="fpm_CPI_term_predict_v2"

forvalues i=1(1)999{

append using "$folder/data/working/bootstrap_outputs/estimates_2_3_fold_`i'"

keep if parm=="fpm_CPI_term_predict_v2"

}

keep estimate stderr

rename estimate estimate2_3
rename stderr stderr2_3

gen ID=_n

save "$folder/data/working/bootstrap_outputs/estimates_2_3_All", replace


**-- Coefficient 3_3

use "$folder/data/working/bootstrap_outputs/estimates_3_3_fold_0", clear

keep if parm=="fpm_CPI_term"

forvalues i=1(1)999{

append using "$folder/data/working/bootstrap_outputs/estimates_3_3_fold_`i'"

keep if parm=="fpm_CPI_term"

}

keep estimate stderr

rename estimate estimate3_3
rename stderr stderr3_3

gen ID=_n

save "$folder/data/working/bootstrap_outputs/estimates_3_3_All", replace

**-- Final file

use "$folder/data/working/bootstrap_outputs/estimates_2_1_All", clear

merge 1:1 ID using "$folder/data/working/bootstrap_outputs/estimates_3_1_All"
drop if _merge==2
drop _merge

merge 1:1 ID using "$folder/data/working/bootstrap_outputs/estimates_2_2_All"
drop if _merge==2
drop _merge

merge 1:1 ID using "$folder/data/working/bootstrap_outputs/estimates_3_2_All"
drop if _merge==2
drop _merge

merge 1:1 ID using "$folder/data/working/bootstrap_outputs/estimates_2_3_All"
drop if _merge==2
drop _merge

merge 1:1 ID using "$folder/data/working/bootstrap_outputs/estimates_3_3_All"
drop if _merge==2
drop _merge

**-- Export table

file open myfile using "$folder/output/appendix_tables/TableD11_panelA.txt", write replace

sum estimate2_1

scalar mean2_1=r(mean)

sum stderr2_1

scalar se2_1=r(mean)

sum estimate3_1

scalar mean3_1=r(mean)

sum stderr3_1

scalar se3_1=r(mean)

sum estimate2_2

scalar mean2_2=r(mean)

sum stderr2_2

scalar se2_2=r(mean)

sum estimate3_2

scalar mean3_2=r(mean)

sum stderr3_2

scalar se3_2=r(mean)

sum estimate2_3

scalar mean2_3=r(mean)

sum stderr2_3

scalar se2_3=r(mean)

sum estimate3_3

scalar mean3_3=r(mean)

sum stderr3_3

scalar se3_3=r(mean)

display 1, 1, mean2_1 
file write myfile ("row1 - column1") _tab ("coefficient") _tab (mean2_1) _n

display 2, 1, se2_1 
file write myfile ("row1 - column1") _tab ("SE") _tab (se2_1) _n

display 3, 1, mean2_1 
file write myfile ("row2 - column1") _tab ("coefficient") _tab (mean3_1) _n

display 4, 1, se2_1 
file write myfile ("row2 - column1") _tab ("SE") _tab (se3_1) _n

display 1, 2, mean2_2
file write myfile ("row1 - column2") _tab ("coefficient") _tab (mean2_2) _n

display 2, 2, se2_2 
file write myfile ("row1 - column2") _tab ("SE") _tab (se2_2) _n

display 3, 2, mean2_2
file write myfile ("row2 - column2") _tab ("coefficient") _tab (mean3_2) _n

display 4, 2, se2_2 
file write myfile ("row2 - column2") _tab ("SE") _tab (se3_2) _n

display 1, 2, mean2_2
file write myfile ("row1 - column3") _tab ("coefficient") _tab (mean2_3) _n

display 2, 2, se2_2 
file write myfile ("row1 - column3") _tab ("SE") _tab (se2_3) _n

display 3, 2, mean2_2
file write myfile ("row2 - column3") _tab ("coefficient") _tab (mean3_3) _n

display 4, 2, se2_2 
file write myfile ("row2 - column3") _tab ("SE") _tab (se3_3) _n

file close myfile
 

