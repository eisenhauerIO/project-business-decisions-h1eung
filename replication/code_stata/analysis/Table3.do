***Predicting corruption in Brazil - Replication files***


**-- Analysis

use "$folder/data/final/dataset_AnalysisTransfer.dta", clear

gen population_term_2=population_term^2
gen population_term_3=population_term^3

encode state_code, gen(state_code_N)
encode city_code, gen(city_code_N)

sort city_code term

**-- Table

qui xi: reg fpm_CPI_term fpm_CPI_term_predict_v2 population_term population_term_2 population_term_3 i.term i.state_code_N if audit_brollo==1,r cluster(city_code_N)
eststo reg_1_1

qui xi: reg narrow1_predictionT fpm_CPI_term_predict_v2 population_term population_term_2 population_term_3 i.term i.state_code_N if audit_brollo==1,r cluster(city_code_N)
eststo reg_2_1

qui xi: ivreg2 narrow1_predictionT  population_term population_term_2 population_term_3 (fpm_CPI_term=fpm_CPI_term_predict_v2) i.term i.state_code_N if audit_brollo==1,r cluster(city_code_N)
eststo reg_3_1


qui xi: reg fpm_CPI_term fpm_CPI_term_predict_v2 population_term population_term_2 population_term_3 i.term i.state_code_N if audit_brollo!=.,r cluster(city_code_N)
eststo reg_1_2

qui xi: reg narrow1_predictionT fpm_CPI_term_predict_v2 population_term population_term_2 population_term_3 i.term i.state_code_N if audit_brollo!=.,r cluster(city_code_N)
eststo reg_2_2

qui xi: ivreg2  narrow1_predictionT population_term population_term_2 population_term_3 (fpm_CPI_term=fpm_CPI_term_predict_v2) i.term i.state_code_N if audit_brollo!=.,r cluster(city_code_N)
eststo reg_3_2


qui xi: reg fpm_CPI_term fpm_CPI_term_predict_v2 population_term population_term_2 population_term_3 i.term i.state_code_N if audit_brollo==0,r cluster(city_code_N)
eststo reg_1_3

qui xi: reg narrow1_predictionT fpm_CPI_term_predict_v2 population_term population_term_2 population_term_3 i.term i.state_code_N if audit_brollo==0,r cluster(city_code_N)
eststo reg_2_3

qui xi: ivreg2  narrow1_predictionT population_term population_term_2 population_term_3 (fpm_CPI_term=fpm_CPI_term_predict_v2) i.term i.state_code_N if audit_brollo==0,r cluster(city_code_N)
eststo reg_3_3

esttab reg_1_1 reg_2_1 reg_3_1 using "$folder/output/tables/Table3_col1.tex", compress keep(fpm_CPI_term_predict_v2 fpm_CPI_term) label nobaselevels se ar2  staraux collabels(, none) ml(,none) cells(b(star fmt (%9.4f)) se(par)) star(* 0.10 ** 0.05 *** 0.01) replace 
esttab reg_1_2 reg_2_2 reg_3_2 using "$folder/output/tables/Table3_col2.tex", compress keep(fpm_CPI_term_predict_v2 fpm_CPI_term) label nobaselevels se ar2  staraux collabels(, none) ml(,none) cells(b(star fmt (%9.4f)) se(par)) star(* 0.10 ** 0.05 *** 0.01) replace
esttab reg_1_3 reg_2_3 reg_3_3 using "$folder/output/tables/Table3_col3.tex", compress keep(fpm_CPI_term_predict_v2 fpm_CPI_term) label nobaselevels se ar2  staraux collabels(, none) ml(,none) cells(b(star fmt (%9.4f)) se(par)) star(* 0.10 ** 0.05 *** 0.01) replace


**-- Check if the instrument does not affect the error rate Y - Y_hat

gen diff_binary=narrow1_auditT-narrow1_predictionT 

gen diff_binary_abs=abs(diff_binary)

 xi: reg diff_binary fpm_CPI_term_predict_v2 population_term population_term_2 population_term_3 i.term i.state_code_N,r cluster(city_code_N)
*not statistically significant
