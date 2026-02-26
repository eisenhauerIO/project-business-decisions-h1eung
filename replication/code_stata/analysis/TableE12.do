***Predicting corruption in Brazil - Replication files***


**-- Analysis

use "$folder/data/final/dataset_AnalysisAudit.dta", clear

**-- Baseline analysis

egen stateyear = group(id_state year)

gen d_pre8 = distance_audit_brollo == -8
gen d_pre7 = distance_audit_brollo == -7
gen d_pre6 = distance_audit_brollo == -6
gen d_pre5 = distance_audit_brollo == -5
gen d_pre4 = distance_audit_brollo == -4
gen d_pre3 = distance_audit_brollo == -3
gen d_pre2 = distance_audit_brollo == -2
gen d_pre1 = distance_audit_brollo == -1
gen d_0 = distance_audit_brollo == 0
gen d_post1 = distance_audit_brollo == 1
gen d_post2 = distance_audit_brollo == 2
gen d_post3 = distance_audit_brollo == 3
gen d_post4 = distance_audit_brollo == 4
gen d_post5 = distance_audit_brollo == 5
gen d_post6 = distance_audit_brollo == 6
gen d_post7 = distance_audit_brollo == 7
gen d_post8 = distance_audit_brollo == 8
gen d_post9 = distance_audit_brollo == 9

gen window_pre = distance_audit_brollo <= -4
gen window_post = distance_audit_brollo >= 6

sort cod_mun year

by cod_mun: egen city_narrow_corr=max(narrow1_audit)

by cod_mun: egen city_broad_corr=max(broad1_audit)

by cod_mun: gen city_audit=1 if city_narrow_corr!=.

order cod_mun id_state year term narrow1_audit broad1_audit corr1_audit corr2_audit distance_audit_brollo city_narrow_corr city_broad_corr city_audit

gen narrow1_prediction_NS_bin=(narrow1_prediction_NS>0.5)

**-- Table

qui reghdfe narrow1_prediction_NS_bin window_pre d_pre3 d_pre2 d_0 d_post1 d_post2 d_post3 d_post4 d_post5 window_post if city_audit!=., absorb(cod_mun year) cluster(id_state)
est store reg1

qui reghdfe narrow1_prediction_NS_bin window_pre d_pre3 d_pre2 d_0 d_post1 d_post2 d_post3 d_post4 d_post5 window_post if city_narrow_corr==1, absorb(cod_mun year) cluster(id_state)
est store reg2

qui reghdfe narrow1_prediction_NS_bin window_pre d_pre3 d_pre2 d_0 d_post1 d_post2 d_post3 d_post4 d_post5 window_post if city_broad_corr==0, absorb(cod_mun year) cluster(id_state)
est store reg3

esttab reg1 reg2 reg3 using "$folder/output/appendix_tables/TableE12.tex", compress keep(window_pre d_pre3 d_pre2 d_0 d_post1 d_post2 d_post3 d_post4 d_post5 window_post) label nobaselevels se ar2  staraux collabels(, none) ml(,none) cells(b(star fmt (%9.4f)) se(par)) star(* 0.10 ** 0.05 *** 0.01) replace 
