***Predicting corruption in Brazil - Replication files***

set seed 2

**-- Tables

use "$folder/data/final/dataset_AnalysisTransfer.dta", clear

gen population_term_2=population_term^2
gen population_term_3=population_term^3

encode state_code, gen(state_code_N)
encode city_code, gen(city_code_N)

sort city_code term

**-- Table

foreach i in 1 2 3 4{
preserve

display `i'

sample 1101, count

qui xi: reg fpm_CPI_term fpm_CPI_term_predict_v2 population_term population_term_2 population_term_3 i.term i.state_code_N,r cluster(city_code_N)
eststo reg_1
qui xi: reg narrow1_predictionT fpm_CPI_term_predict_v2 population_term population_term_2 population_term_3 i.term i.state_code_N,r cluster(city_code_N)
eststo reg_2
qui xi: ivreg2 narrow1_predictionT  population_term population_term_2 population_term_3 (fpm_CPI_term=fpm_CPI_term_predict_v2) i.term i.state_code_N,r cluster(city_code_N)
eststo reg_3

esttab reg_1 reg_2 reg_3, compress keep(fpm_CPI_term_predict_v2 fpm_CPI_term) label nobaselevels se ar2  staraux star(* 0.10 ** 0.05 *** 0.01) replace
esttab reg_1 reg_2 reg_3 using "$folder/output/appendix_tables/TableD9_col`i'.tex", compress keep(fpm_CPI_term_predict_v2 fpm_CPI_term) label nobaselevels se ar2  staraux collabels(, none) ml(,none) cells(b(star fmt (%9.4f)) se(par)) star(* 0.10 ** 0.05 *** 0.01) replace
restore
}
