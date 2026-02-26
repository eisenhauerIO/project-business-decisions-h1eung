***Predicting corruption in Brazil - Replication files***


**-- Analysis

use "$folder/data/working/biscatter_AuditReports.dta", clear

rename weight_avg weight 

destring weight, replace

gen string_length=length(feature)
gen count_log=log(count)

foreach x in weight count_log count{
egen rank_`x' = rank(`x')
replace rank_`x' = rank_`x' - 1
egen maxrank_`x' = max(rank_`x')
gen pct_`x' = rank_`x' / maxrank_`x'
}

xtile string_length_Q=string_length, n(4)

binscatter  pct_count pct_weight, n(20) controls(i.string_length_Q) xtitle("Classifier Feature Importance Weight") ytitle("Mentions of Feature in Audit Reports") xlabel(, angle(45)) ylabel(, angle(45)) mcolors(black)
graph export "$folder/output/figures/Figure2.png", replace

corr pct_count pct_weight //0.2237

reg pct_count pct_weight i.string_length_Q, r
*pct_weight .1826856   .0461262     3.96   0.000
