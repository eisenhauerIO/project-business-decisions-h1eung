***Predicting corruption in Brazil - Replication files***



****---- Data on corruption predictions ----****

**-- Generate dta files

import delimited "$folder/data/working/prediction_xgboost_nosample_b/narrow1_fold0/predict_fold_0.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_nosample_b_fold0.dta", replace

import delimited "$folder/data/working/prediction_xgboost_nosample_b/narrow1_fold1/predict_fold_1.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_nosample_b_fold1.dta", replace

import delimited "$folder/data/working/prediction_xgboost_nosample_b/narrow1_fold2/predict_fold_2.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_nosample_b_fold2.dta", replace

import delimited "$folder/data/working/prediction_xgboost_nosample_b/narrow1_fold3/predict_fold_3.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_nosample_b_fold3.dta", replace

import delimited "$folder/data/working/prediction_xgboost_nosample_b/narrow1_fold4/predict_fold_4.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_nosample_b_fold4.dta", replace


import delimited "$folder/data/working/prediction_xgboost_sample_d/narrow1_fold0/predict_fold_0.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_sample_d_fold0.dta", replace

import delimited "$folder/data/working/prediction_xgboost_sample_d/narrow1_fold1/predict_fold_1.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_sample_d_fold1.dta", replace

import delimited "$folder/data/working/prediction_xgboost_sample_d/narrow1_fold2/predict_fold_2.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_sample_d_fold2.dta", replace

import delimited "$folder/data/working/prediction_xgboost_sample_d/narrow1_fold3/predict_fold_3.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_sample_d_fold3.dta", replace

import delimited "$folder/data/working/prediction_xgboost_sample_d/narrow1_fold4/predict_fold_4.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_sample_d_fold4.dta", replace


import delimited "$folder/data/working/prediction_xgboost_nosample_b_fpm/narrow1_fold0/predict_fold_0.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_nosample_b_fpm_fold0.dta", replace

import delimited "$folder/data/working/prediction_xgboost_nosample_b_fpm/narrow1_fold1/predict_fold_1.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_nosample_b_fpm_fold1.dta", replace

import delimited "$folder/data/working/prediction_xgboost_nosample_b_fpm/narrow1_fold2/predict_fold_2.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_nosample_b_fpm_fold2.dta", replace

import delimited "$folder/data/working/prediction_xgboost_nosample_b_fpm/narrow1_fold3/predict_fold_3.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_nosample_b_fpm_fold3.dta", replace

import delimited "$folder/data/working/prediction_xgboost_nosample_b_fpm/narrow1_fold4/predict_fold_4.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_nosample_b_fpm_fold4.dta", replace


import delimited "$folder/data/working/prediction_xgboost_nosample_b/corr1_fold0/predict_fold_0.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_nosample_b_Avis_fold0.dta", replace

import delimited "$folder/data/working/prediction_xgboost_nosample_b/corr1_fold1/predict_fold_1.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_nosample_b_Avis_fold1.dta", replace

import delimited "$folder/data/working/prediction_xgboost_nosample_b/corr1_fold2/predict_fold_2.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_nosample_b_Avis_fold2.dta", replace

import delimited "$folder/data/working/prediction_xgboost_nosample_b/corr1_fold3/predict_fold_3.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_nosample_b_Avis_fold3.dta", replace

import delimited "$folder/data/working/prediction_xgboost_nosample_b/corr1_fold4/predict_fold_4.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_nosample_b_Avis_fold4.dta", replace


import delimited "$folder/data/working/prediction_xgboost_nosample_b_half/narrow1_fold0/predict_fold_0.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_nosample_b_HoldOutData_fold0.dta", replace

import delimited "$folder/data/working/prediction_xgboost_nosample_b_half/narrow1_fold1/predict_fold_1.csv", encoding(ISO-8859-1)clear
save "$folder/data/working/xgboost_nosample_b_HoldOutData_fold1.dta", replace


****---- Clean the corruption prediction ----****

**-- Version: no sample/budget - single prediction (5 folds) - Term specific dataset

foreach i in 0 1 2 3 4{
use "$folder/data/working/xgboost_nosample_b_fold`i'.dta", clear

replace narrow1_predicted=. if narrow1_train_sample==1

keep cod_mun year narrow1_predicted narrow1_train_sample

rename narrow1_predicted narrow1_predicted_f`i'
rename narrow1_train_sample narrow1_train_sample_f`i'

save "$folder/data/working/corruption_predictions_NS_b_fold`i'.dta", replace
}

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

qui by cod_mun term: egen narrow1_predictionT=mean(narrow1_predictionT_Av) 

keep if year==2001 | year==2005 | year==2009

save "$folder/data/working/corruption_predictions_NS_b_foldAll.dta", replace

**-- Version: sample/demographics - single prediction (5 folds) - Term specific dataset

foreach i in 0 1 2 3 4{
use "$folder/data/working/xgboost_sample_d_fold`i'.dta", clear

replace narrow1_predicted=. if narrow1_train_sample==1

keep cod_mun year narrow1_predicted narrow1_train_sample

rename narrow1_predicted narrow1_predicted_f`i'
rename narrow1_train_sample narrow1_train_sample_f`i'

save "$folder/data/working/corruption_predictions_S_d_fold`i'.dta", replace
}

use "$folder/data/working/corruption_predictions_S_d_fold0.dta", clear
foreach i in 1 2 3 4{
merge 1:1 cod_mun year using "$folder/data/working/corruption_predictions_S_d_fold`i'.dta"
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
qui by cod_mun term: egen narrow1_predictionT=mean(narrow1_predictionT_Av) 

keep if year==2001 | year==2005 | year==2009

rename narrow1_predictionT narrow1_predictionT_d

save "$folder/data/working/corruption_predictions_S_d_foldAll.dta", replace

**-- Version: no sample/budget nofpm - single prediction (5 folds) - Term specific dataset

foreach i in 0 1 2 3 4{
use "$folder/data/working/xgboost_nosample_b_fpm_fold`i'.dta", clear

replace narrow1_predicted=. if narrow1_train_sample==1

keep cod_mun year narrow1_predicted narrow1_train_sample

rename narrow1_predicted narrow1_predicted_f`i'
rename narrow1_train_sample narrow1_train_sample_f`i'

save "$folder/data/working/corruption_predictions_NS_b_fpm_fold`i'.dta", replace
}

use "$folder/data/working/corruption_predictions_NS_b_fpm_fold0.dta", clear
foreach i in 1 2 3 4{
merge 1:1 cod_mun year using "$folder/data/working/corruption_predictions_NS_b_fpm_fold`i'.dta"
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

qui by cod_mun term: egen narrow1_predictionT=mean(narrow1_predictionT_Av) 

keep if year==2001 | year==2005 | year==2009

rename narrow1_predictionT narrow1_predictionT_noFPM

save "$folder/data/working/corruption_predictions_NS_b_fpm_foldAll.dta", replace


**-- Version: no sample/budget - single prediction - HoldOut approach - Term specific dataset

use "$folder/data/working/xgboost_nosample_b_HoldOutData_fold0.dta", clear

replace narrow1_predicted=. if narrow1_train_sample==1
rename narrow1_predicted narrow1_prediction_NS_fold0
replace narrow1_prediction_NS_fold0=1-narrow1_prediction_NS_fold0

drop narrow1_train_sample

merge 1:1 cod_mun year using "$folder/data/working/xgboost_nosample_b_HoldOutData_fold1.dta"
drop if _merge==2
drop _merge

replace narrow1_predicted=. if narrow1_train_sample==1
rename narrow1_predicted narrow1_prediction_NS_fold1
replace narrow1_prediction_NS_fold1=1-narrow1_prediction_NS_fold1

drop narrow1_train_sample

gen term=.
replace term=2001 if year>=2001 & year<=2004
replace term=2005 if year>=2005 & year<=2008
replace term=2009 if year>=2009 & year<=2012

sort cod_mun term

qui by cod_mun term: egen narrow1_predictionT_Av_fold0=mean(narrow1_prediction_NS_fold0) 
qui by cod_mun term: egen narrow1_predictionT_Av_fold1=mean(narrow1_prediction_NS_fold1) 

keep if year==2001 | year==2005 | year==2009

keep cod_mun term narrow1_predictionT_Av_fold0 narrow1_predictionT_Av_fold1

save "$folder/data/working/corruption_predictions_NS_b_foldAll_HoldOutData.dta", replace


**-- Version: no sample/budget - single prediction - HoldOut approach - Year specific dataset

use "$folder/data/working/xgboost_nosample_b_HoldOutData_fold0.dta", clear

replace narrow1_predicted=. if narrow1_train_sample==1
rename narrow1_predicted narrow1_prediction_NS_fold0
replace narrow1_prediction_NS_fold0=1-narrow1_prediction_NS_fold0

drop narrow1_train_sample

merge 1:1 cod_mun year using "$folder/data/working/xgboost_nosample_b_HoldOutData_fold1.dta"
drop if _merge==2
drop _merge

replace narrow1_predicted=. if narrow1_train_sample==1
rename narrow1_predicted narrow1_prediction_NS_fold1
replace narrow1_prediction_NS_fold1=1-narrow1_prediction_NS_fold1

drop narrow1_train_sample

gen term=.
replace term=2001 if year>=2001 & year<=2004
replace term=2005 if year>=2005 & year<=2008
replace term=2009 if year>=2009 & year<=2012

sort cod_mun year

keep cod_mun year narrow1_prediction_NS_fold0 narrow1_prediction_NS_fold1

save "$folder/data/working/corruption_predictions_NS_b_foldAll_HoldOutData_year.dta", replace


**-- Version for bootstrap analysis - Term specific dataset

forvalues i=0(1)999{

import delimited "$folder/data/working/prediction_xgboost_nosample_b_bootstrap/narrow1_fold`i'/predict_fold_`i'.csv", encoding(ISO-8859-1)clear

gen term=.
replace term=2001 if year>=2001 & year<=2004
replace term=2005 if year>=2005 & year<=2008
replace term=2009 if year>=2009 & year<=2012

sort cod_mun term

duplicates report cod_mun year

qui by cod_mun term: egen narrow1_predictionT_Av=mean(narrow1_predicted) 

keep if year==2001 | year==2005 | year==2009

keep cod_mun term narrow1_predictionT_Av

save "$folder/data/working/bootstrap/predict_fold_`i'.dta", replace
}

**-- Version for bootstrap analysis - Year specific dataset

forvalues i=0(1)999{

*******************************************************
****---- 			Dataset cleaning  		   ----****
*******************************************************

import delimited "$folder/data/working/prediction_xgboost_nosample_b_bootstrap/narrow1_fold`i'/predict_fold_`i'.csv", encoding(ISO-8859-1)clear

gen term=.
replace term=2001 if year>=2001 & year<=2004
replace term=2005 if year>=2005 & year<=2008
replace term=2009 if year>=2009 & year<=2012

sort cod_mun term

duplicates report cod_mun year

rename narrow1_predicted narrow1_prediction_NS

replace narrow1_prediction_NS=1-narrow1_prediction_NS

merge 1:1 cod_mun year using "$folder/data/final/panel_budget_corruption.dta", keepusing(narrow1 corr1 corr2)
*all matched from master, 314 not merged from using
drop if _merge==2
drop _merge

rename narrow1 narrow1_audit
rename corr1 corr1_audit
rename corr2 corr2_audit

**-- Importo le date dei sorteggi - dati Brollo

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

order cod_mun id_state year term for_prediction for_prediction2 narrow1_audit broad1_audit corr1_audit corr2_audit distance_audit_brollo  narrow1_prediction*

save "$folder/data/working/bootstrap/predict_fold_`i'_YearVersion.dta", replace

}

**-- Version corruption data from Avis et al. 2019 - Year specific dataset

foreach i in 0 1 2 3 4{
use "$folder/data/working/xgboost_nosample_b_Avis_fold`i'.dta", clear

replace corr1_predicted=. if corr1_train_sample==1

keep cod_mun year corr1_predicted corr1_train_sample

rename corr1_predicted corr1_predicted_f`i'
rename corr1_train_sample corr1_train_sample_f`i'

save "$folder/data/working/corruption_predictions_NS_b_Avis_fold`i'.dta", replace
}

use "$folder/data/working/corruption_predictions_NS_b_Avis_fold0.dta", clear
foreach i in 1 2 3 4{
merge 1:1 cod_mun year using "$folder/data/working/corruption_predictions_NS_b_Avis_fold`i'.dta"
drop if _merge==2
drop _merge
}

egen corr1_predictionT_Av=rowmean(corr1_predicted_f0 corr1_predicted_f1 corr1_predicted_f2 corr1_predicted_f3 corr1_predicted_f4)

drop corr1_predicted_f* corr1_train_sample_f*

replace corr1_predictionT_Av=1-corr1_predictionT_Av

gen term=.
replace term=2001 if year>=2001 & year<=2004
replace term=2005 if year>=2005 & year<=2008
replace term=2009 if year>=2009 & year<=2012

sort cod_mun term

duplicates report cod_mun year

rename corr1_predictionT_Av corr1_prediction_NS

*Variables we use in the analysis do-files
keep cod_mun year corr1_prediction_NS

save "$folder/data/working/corruption_predictions_NS_b_Avis_foldAll.dta", replace


