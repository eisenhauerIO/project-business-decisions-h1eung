***Predicting corruption in Brazil - Replication files***


**-- Tables

use "$folder/data/final/dataset_AnalysisTransfer.dta", clear

replace fpm_coefficient=fpm_coefficient*10

gen pop_groups=.
replace pop_groups=1 if fpm_coefficient==6
replace pop_groups=2 if fpm_coefficient==8
replace pop_groups=3 if fpm_coefficient==10
replace pop_groups=4 if fpm_coefficient==12
replace pop_groups=5 if fpm_coefficient==14
replace pop_groups=6 if fpm_coefficient==16
replace pop_groups=7 if fpm_coefficient==18
replace pop_groups=8 if fpm_coefficient==20

forvalues i=1(1)8{
count if pop_groups==`i'
}

gen sign=1

sort pop_groups
by pop_groups: egen sample_N=sum(sign)

estpost tabstat fpm_CPI_term fpm_CPI_term_predict_v2 narrow1_predictionT sample_N, by(pop_groups)
est store tab_3
esttab tab_3 using "$folder/output/appendix_tables/TableD8.tex", cells("fpm_CPI_term fpm_CPI_term_predict_v2 narrow1_predictionT sample_N") replace
