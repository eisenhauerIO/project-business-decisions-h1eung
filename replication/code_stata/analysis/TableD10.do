***Predicting corruption in Brazil - Replication files***


**-- Tables

use "$folder/data/final/dataset_AnalysisTransfer.dta", clear

gen population_term_2=population_term^2
gen population_term_3=population_term^3

encode state_code, gen(state_code_N)
encode city_code, gen(city_code_N)

sort city_code term

**-- Table - column 1

qui xi: reg narrow1_predictionT_d fpm_CPI_term_predict_v2 population_term population_term_2 population_term_3 i.term i.state_code_N if audit_brollo!=.,r cluster(city_code_N)
eststo reg_2_1

qui xi: ivreg2  narrow1_predictionT_d population_term population_term_2 population_term_3 (fpm_CPI_term=fpm_CPI_term_predict_v2) i.term i.state_code_N if audit_brollo!=.,r cluster(city_code_N)
eststo reg_3_1

esttab reg_2_1 reg_3_1 using "$folder/output/appendix_tables/TableD10_col1.tex", compress keep(fpm_CPI_term_predict_v2 fpm_CPI_term) label nobaselevels se ar2  staraux collabels(, none) ml(,none) cells(b(star fmt (%9.4f)) se(par)) star(* 0.10 ** 0.05 *** 0.01) replace

**-- Table - column 2

qui xi: reg narrow1_predictionT_noFPM fpm_CPI_term_predict_v2 population_term population_term_2 population_term_3 i.term i.state_code_N if audit_brollo!=.,r cluster(city_code_N)
eststo reg_2_2

qui xi: ivreg2  narrow1_predictionT_noFPM population_term population_term_2 population_term_3 (fpm_CPI_term=fpm_CPI_term_predict_v2) i.term i.state_code_N if audit_brollo!=.,r cluster(city_code_N)
eststo reg_3_2

esttab reg_2_2 reg_3_2 using "$folder/output/appendix_tables/TableD10_col2.tex", compress keep(fpm_CPI_term_predict_v2 fpm_CPI_term) label nobaselevels se ar2  staraux collabels(, none) ml(,none) cells(b(star fmt (%9.4f)) se(par)) star(* 0.10 ** 0.05 *** 0.01) replace
