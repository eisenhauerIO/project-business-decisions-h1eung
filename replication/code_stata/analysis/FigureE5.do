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

gen rand = 100000000000 * uniform()

sort cod_mun year

by cod_mun: egen city_narrow_corr=max(narrow1_audit)

by cod_mun: egen city_broad_corr=max(broad1_audit)

by cod_mun: gen city_audit=1 if city_narrow_corr!=.

order id_state year term narrow1_audit broad1_audit corr1_audit corr2_audit distance_audit_brollo city_narrow_corr city_broad_corr city_audit

gen narrow1_prediction_NS_bin=(narrow1_prediction_NS>0.5)

gen Y=narrow1_prediction_NS_bin
gen i=cod_mun
gen t=year
gen Ei=year_first_sorteio
gen gvar = cond(Ei==., 0, Ei) 

**-- Figure

csdid Y if city_audit!=., ivar(i) time(t) gvar(gvar) notyet cluster(id_state)
estat event, estore(cs) 

coefplot cs, vertical  yline(0, lpattern(dash) lcolor(gray)) drop(Pre_avg Post_avg Tm7 Tm6 Tm5 Tm4 Tp5 Tp6 Tp7 Tp8 Tp9) ytitle("Corruption (Budget-Predicted)")  xtitle("Years before and after Audit Announcement") xlabel( 1 "-3" 2 "-2" 3 "-1" 4 "0" 5 "1" 6 "2" 7 "3" 8 "4", angle(45))  subtitle("Impact Effect of Audits on Corruption") graphregion(color(white)) color(black) ciopts(recast(rcap) color(black black) lwidth(*0.75 *1.25)) levels(95 90) xsize(6) xline(3.5, lpattern(dash) lcolor(gray))
graph export "$folder/output/appendix_figures/FigureE5_a.pdf", replace


csdid Y if city_narrow_corr==1, ivar(i) time(t) gvar(gvar) notyet cluster(id_state)
estat event, estore(cs_corr)

csdid Y if city_broad_corr==0, ivar(i) time(t) gvar(gvar) notyet cluster(id_state)
estat event, estore(cs_nocorr)

coefplot (cs_corr, base offset(0) graphregion(color(white)) color(black) ciopts(recast(rcap) color(black black) lwidth(*0.75 *1.25)) levels(95 90) label("Audits that reveal corruption") drop(Pre_avg Post_avg Tm7 Tm6 Tm5 Tm4 Tp5 Tp6 Tp7 Tp8 Tp9) ) ///
(cs_nocorr, offset(0.1) graphregion(color(white)) color(gs8) ciopts(recast(rcap) color(gs8 gs8) lwidth(*0.75 *1.25)) levels(95 90) label("Audits that do not reveal corruption") drop(Pre_avg Post_avg Tm7 Tm6 Tm5 Tm4 Tp5 Tp6 Tp7 Tp8 Tp9) ),  ///
vertical omitted yline(0, lpattern(dash) lcolor(gray)) xline(3.5, lpattern(dash) lcolor(gray)) xlabel( 1 "-3" 2 "-2" 3 "-1" 4 "0" 5 "1" 6 "2" 7 "3" 8 "4", angle(45)) ytitle("Corruption (Budget-Predicted)") xtitle("Years before and after Audit Announcement") ///
subtitle("Impact Effect of Audits on Corruption: depending on Audits' Outcomes") legend(rows(1)) drop(window_pre d_post5 window_post) xsize(6)
graph export "$folder/output/appendix_figures/FigureE5_b.pdf", replace



