***Predicting corruption in Brazil - Replication files***


****---- Main dataset (corruption data from Brollo et al. 2013) ----****

use "$folder/data/working/corruption_predictions_NS_b_fold0.dta", clear
foreach i in 1 2 3 4{
merge 1:1 cod_mun year using "$folder/data/working/corruption_predictions_NS_b_fold`i'.dta"
drop if _merge==2
drop _merge
}

egen narrow1_predictionT_Av=rowmean(narrow1_predicted_f0 narrow1_predicted_f1 narrow1_predicted_f2 narrow1_predicted_f3 narrow1_predicted_f4)

drop narrow1_predicted_f* narrow1_train_sample_f*

replace narrow1_predictionT_Av=1-narrow1_predictionT_Av

gen term=.
replace term=2001 if year>=2001 & year<=2004
replace term=2005 if year>=2005 & year<=2008
replace term=2009 if year>=2009 & year<=2012

sort cod_mun term

duplicates report cod_mun year

rename narrow1_predictionT_Av narrow1_prediction_NS

**-- Merge hold out predictions

merge 1:1 cod_mun year using "$folder/data/working/corruption_predictions_NS_b_foldAll_HoldOutData_year.dta"
drop if _merge==2
drop _merge

**-- Merge true corruption data

merge 1:1 cod_mun year using "$folder/data/final/panel_budget_corruption.dta", keepusing(narrow1 corr1 corr2)
*all matched from master, 314 not merged from using
drop if _merge==2
drop _merge

rename narrow1 narrow1_audit
rename corr1 corr1_audit
rename corr2 corr2_audit

**-- Merge lottery data from Brollo et al.

merge 1:1 cod_mun year using "$folder/data/final/panel_budget_corruption.dta", keepusing(broad1 id_state date_sorteio1 date_sorteio2)
*all matched from master, 314 not merged from using
drop if _merge==2
drop _merge

rename broad1 broad1_audit

gen date_sorteio1_format=date(date_sorteio1, "DMY")
gen date_sorteio2_format=date(date_sorteio2, "DMY")

format date_sorteio1_format %td
format date_sorteio2_format %td

gen sign1=year(date_sorteio1_format)
gen sign2=year(date_sorteio2_format)

sort cod_mun year
by cod_mun: egen year_first_sorteio=min(sign1)
by cod_mun: egen year_second_sorteio=max(sign2)

gen sorteio_flag_1=(year_first_sorteio==year)
gen sorteio_flag_2=(year_second_sorteio==year)

gen city_audited_1=(year_first_sorteio!=.)
gen city_audited_2=(year_second_sorteio!=.)

gen distance_audit_brollo=year-year_first_sorteio

sort cod_mun year

drop date_sorteio1 date_sorteio2 date_sorteio1_format date_sorteio2_format sign1 sign2 year_second_sorteio sorteio_flag_1 sorteio_flag_2

**-- Include controls

merge 1:1 cod_mun year using "$folder/data/final/panel_budget_corruption.dta", keepusing(income education agriculture industry commerce transport service public_administration employed graduated_people poverty miserable gini_coefficient)
*all matched from master, 314 not merged from using
drop if _merge==2
drop _merge

**-- Save

drop city_audited_1 city_audited_2

order cod_mun id_state year term narrow1_audit broad1_audit corr1_audit corr2_audit distance_audit_brollo narrow1_prediction*

*Variables we use in the analysis do-files
*keep cod_mun year year_first_sorteio narrow1_prediction_NS income employed agriculture industry commerce transport service public_administration graduated_people poverty gini_coefficient corr1_prediction_NS id_state distance_audit_brollo narrow1_audit broad1_audit cod_amc uf_mun term corr2_audit city_narrow_corr city_broad_corr city_audit

save "$folder/data/final/dataset_AnalysisAudit.dta", replace

****---- Dataset for replication Figure 3 ----****

use "$folder/data/final/dataset_AnalysisAudit.dta", clear 

keep if year==2004

gen narrow1_prediction_bin=narrow1_prediction_NS>0.5

keep cod_mun narrow1_audit narrow1_prediction_bin

export excel using "$folder/data/working/for_map.xls", replace

****---- Dataset for Figure 2 ----****

import delimited "$folder/data/working/merged_desc_counts_weight_avg_left_join.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/biscatter_AuditReports.dta", replace
