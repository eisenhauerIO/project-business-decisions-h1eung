***Predicting corruption in Brazil - Replication files***


**-- Analysis

forvalues i=0(1)999{

use "$folder/data/working/bootstrap/predict_fold_`i'_YearVersion.dta", clear

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
parmest, saving("$folder/data/working/bootstrap_outputs/estimates_EventStudy_1_fold_`i'", replace)

qui reghdfe narrow1_prediction_NS_bin window_pre d_pre3 d_pre2 d_0 d_post1 d_post2 d_post3 d_post4 d_post5 window_post if city_narrow_corr==1, absorb(cod_mun year) cluster(id_state)
parmest, saving("$folder/data/working/bootstrap_outputs/estimates_EventStudy_2_fold_`i'", replace)

qui reghdfe narrow1_prediction_NS_bin window_pre d_pre3 d_pre2 d_0 d_post1 d_post2 d_post3 d_post4 d_post5 window_post if city_broad_corr==0, absorb(cod_mun year) cluster(id_state)
parmest, saving("$folder/data/working/bootstrap_outputs/estimates_EventStudy_3_fold_`i'", replace)

}

**-- Recover bootstrapped SE 
*Note: this code creates bootstrapped standard errors which have been manually added in Table E13, column 1-3.

**-- Coefficients - First regression

use "$folder/data/working/bootstrap_outputs/estimates_EventStudy_1_fold_0", clear

keep if parm=="window_pre" | parm=="d_pre3" | parm=="d_pre2" | parm=="d_0" | parm=="d_post1" | parm=="d_post2" | parm=="d_post3" | parm=="d_post4" | parm=="d_post5" | parm=="window_post"

gen ID=0

forvalues i=1(1)999{

append using "$folder/data/working/bootstrap_outputs/estimates_EventStudy_1_fold_`i'"

replace ID=`i' if ID==.

keep if parm=="window_pre" | parm=="d_pre3" | parm=="d_pre2" | parm=="d_0" | parm=="d_post1" | parm=="d_post2" | parm=="d_post3" | parm=="d_post4" | parm=="d_post5" | parm=="window_post"

}

keep parm estimate stderr ID

rename estimate estimate1_
rename stderr stderr1_

reshape wide estimate1_ stderr1_, i(ID) j(parm) string

save "$folder/data/working/bootstrap_outputs/estimates_EventStudy_1_All", replace

**-- Coefficients - Second regression

use "$folder/data/working/bootstrap_outputs/estimates_EventStudy_2_fold_0", clear

keep if parm=="window_pre" | parm=="d_pre3" | parm=="d_pre2" | parm=="d_0" | parm=="d_post1" | parm=="d_post2" | parm=="d_post3" | parm=="d_post4" | parm=="d_post5" | parm=="window_post"

gen ID=0

forvalues i=1(1)999{

append using "$folder/data/working/bootstrap_outputs/estimates_EventStudy_2_fold_`i'"

replace ID=`i' if ID==.

keep if parm=="window_pre" | parm=="d_pre3" | parm=="d_pre2" | parm=="d_0" | parm=="d_post1" | parm=="d_post2" | parm=="d_post3" | parm=="d_post4" | parm=="d_post5" | parm=="window_post"

}

keep parm estimate stderr ID

rename estimate estimate2_
rename stderr stderr2_

reshape wide estimate2_ stderr2_, i(ID) j(parm) string

save "$folder/data/working/bootstrap_outputs/estimates_EventStudy_2_All", replace

**-- Coefficients - Third regression

use "$folder/data/working/bootstrap_outputs/estimates_EventStudy_3_fold_0", clear

keep if parm=="window_pre" | parm=="d_pre3" | parm=="d_pre2" | parm=="d_0" | parm=="d_post1" | parm=="d_post2" | parm=="d_post3" | parm=="d_post4" | parm=="d_post5" | parm=="window_post"

gen ID=0

forvalues i=1(1)999{

append using "$folder/data/working/bootstrap_outputs/estimates_EventStudy_3_fold_`i'"

replace ID=`i' if ID==.

keep if parm=="window_pre" | parm=="d_pre3" | parm=="d_pre2" | parm=="d_0" | parm=="d_post1" | parm=="d_post2" | parm=="d_post3" | parm=="d_post4" | parm=="d_post5" | parm=="window_post"

}

keep parm estimate stderr ID

rename estimate estimate3_
rename stderr stderr3_

reshape wide estimate3_ stderr3_, i(ID) j(parm) string

save "$folder/data/working/bootstrap_outputs/estimates_EventStudy_3_All", replace

**-- Final file

use "$folder/data/working/bootstrap_outputs/estimates_EventStudy_1_All", clear

merge 1:1 ID using "$folder/data/working/bootstrap_outputs/estimates_EventStudy_2_All"
drop if _merge==2
drop _merge

merge 1:1 ID using "$folder/data/working/bootstrap_outputs/estimates_EventStudy_3_All"
drop if _merge==2
drop _merge

**-- Export table

file open myfile using "$folder/output/appendix_tables/TableE13_columns1_3.txt", write replace

sum estimate1_window_pre

scalar mean1_window_pre=r(mean)

sum stderr1_window_pre

scalar se1_window_pre=r(mean)

sum estimate1_d_pre3

scalar mean1_pre3=r(mean)

sum stderr1_d_pre3

scalar se1_pre3=r(mean)

sum estimate1_d_pre2

scalar mean1_pre2=r(mean)

sum stderr1_d_pre2

scalar se1_pre2=r(mean)

sum estimate1_d_0

scalar mean1_0=r(mean)

sum stderr1_d_0

scalar se1_0=r(mean)

sum estimate1_d_post1

scalar mean1_post1=r(mean)

sum stderr1_d_post1

scalar se1_post1=r(mean)

sum estimate1_d_post2

scalar mean1_post2=r(mean)

sum stderr1_d_post2

scalar se1_post2=r(mean)

sum estimate1_d_post3

scalar mean1_post3=r(mean)

sum stderr1_d_post3

scalar se1_post3=r(mean)

sum estimate1_d_post4

scalar mean1_post4=r(mean)

sum stderr1_d_post4

scalar se1_post4=r(mean)

sum estimate1_d_post5

scalar mean1_post5=r(mean)

sum stderr1_d_post5

scalar se1_post5=r(mean)

sum estimate1_window_post

scalar mean1_window_post=r(mean)

sum stderr1_window_post

scalar se1_window_post=r(mean)


sum estimate2_window_pre

scalar mean2_window_pre=r(mean)

sum stderr2_window_pre

scalar se2_window_pre=r(mean)

sum estimate2_d_pre3

scalar mean2_pre3=r(mean)

sum stderr2_d_pre3

scalar se2_pre3=r(mean)

sum estimate2_d_pre2

scalar mean2_pre2=r(mean)

sum stderr2_d_pre2

scalar se2_pre2=r(mean)

sum estimate2_d_0

scalar mean2_0=r(mean)

sum stderr2_d_0

scalar se2_0=r(mean)

sum estimate2_d_post1

scalar mean2_post1=r(mean)

sum stderr2_d_post1

scalar se2_post1=r(mean)

sum estimate2_d_post2

scalar mean2_post2=r(mean)

sum stderr2_d_post2

scalar se2_post2=r(mean)

sum estimate2_d_post3

scalar mean2_post3=r(mean)

sum stderr2_d_post3

scalar se2_post3=r(mean)

sum estimate2_d_post4

scalar mean2_post4=r(mean)

sum stderr2_d_post4

scalar se2_post4=r(mean)

sum estimate2_d_post5

scalar mean2_post5=r(mean)

sum stderr2_d_post5

scalar se2_post5=r(mean)

sum estimate2_window_post

scalar mean2_window_post=r(mean)

sum stderr2_window_post

scalar se2_window_post=r(mean)


sum estimate3_window_pre

scalar mean3_window_pre=r(mean)

sum stderr3_window_pre

scalar se3_window_pre=r(mean)

sum estimate3_d_pre3

scalar mean3_pre3=r(mean)

sum stderr3_d_pre3

scalar se3_pre3=r(mean)

sum estimate3_d_pre2

scalar mean3_pre2=r(mean)

sum stderr3_d_pre2

scalar se3_pre2=r(mean)

sum estimate3_d_0

scalar mean3_0=r(mean)

sum stderr3_d_0

scalar se3_0=r(mean)

sum estimate3_d_post1

scalar mean3_post1=r(mean)

sum stderr3_d_post1

scalar se3_post1=r(mean)

sum estimate3_d_post2

scalar mean3_post2=r(mean)

sum stderr3_d_post2

scalar se3_post2=r(mean)

sum estimate3_d_post3

scalar mean3_post3=r(mean)

sum stderr3_d_post3

scalar se3_post3=r(mean)

sum estimate3_d_post4

scalar mean3_post4=r(mean)

sum stderr3_d_post4

scalar se3_post4=r(mean)

sum estimate3_d_post5

scalar mean3_post5=r(mean)

sum stderr3_d_post5

scalar se3_post5=r(mean)

sum estimate3_window_post

scalar mean3_window_post=r(mean)

sum stderr3_window_post

scalar se3_window_post=r(mean)

file write myfile ("row1 - column1") _tab ("coefficient") _tab (mean1_window_pre) _n

file write myfile ("row1 - column1") _tab ("SE") _tab (se1_window_pre) _n

file write myfile ("row2 - column1") _tab ("coefficient") _tab (mean1_pre3) _n

file write myfile ("row2 - column1") _tab ("SE") _tab (se1_pre3) _n

file write myfile ("row3 - column1") _tab ("coefficient") _tab (mean1_pre2) _n

file write myfile ("row3 - column1") _tab ("SE") _tab (se1_pre2) _n

file write myfile ("row4 - column1") _tab ("coefficient") _tab (mean1_0) _n

file write myfile ("row4 - column1") _tab ("SE") _tab (se1_0) _n

file write myfile ("row5 - column1") _tab ("coefficient") _tab (mean1_post1) _n

file write myfile ("row5 - column1") _tab ("SE") _tab (se1_post1) _n

file write myfile ("row6 - column1") _tab ("coefficient") _tab (mean1_post2) _n

file write myfile ("row6 - column1") _tab ("SE") _tab (se1_post2) _n

file write myfile ("row7 - column1") _tab ("coefficient") _tab (mean1_post3) _n

file write myfile ("row7 - column1") _tab ("SE") _tab (se1_post3) _n

file write myfile ("row8 - column1") _tab ("coefficient") _tab (mean1_post4) _n

file write myfile ("row8 - column1") _tab ("SE") _tab (se1_post4) _n

file write myfile ("row9 - column1") _tab ("coefficient") _tab (mean1_post5) _n

file write myfile ("row9 - column1") _tab ("SE") _tab (se1_post5) _n

file write myfile ("row10 - column1") _tab ("coefficient") _tab (mean1_window_post) _n

file write myfile ("row10 - column1") _tab ("SE") _tab (se1_window_post) _n


file write myfile ("row1 - column2") _tab ("coefficient") _tab (mean2_window_pre) _n

file write myfile ("row1 - column2") _tab ("SE") _tab (se2_window_pre) _n

file write myfile ("row2 - column2") _tab ("coefficient") _tab (mean2_pre3) _n

file write myfile ("row2 - column2") _tab ("SE") _tab (se2_pre3) _n

file write myfile ("row3 - column2") _tab ("coefficient") _tab (mean2_pre2) _n

file write myfile ("row3 - column2") _tab ("SE") _tab (se2_pre2) _n

file write myfile ("row4 - column2") _tab ("coefficient") _tab (mean2_0) _n

file write myfile ("row4 - column2") _tab ("SE") _tab (se2_0) _n

file write myfile ("row5 - column2") _tab ("coefficient") _tab (mean2_post1) _n

file write myfile ("row5 - column2") _tab ("SE") _tab (se2_post1) _n

file write myfile ("row6 - column2") _tab ("coefficient") _tab (mean2_post2) _n

file write myfile ("row6 - column2") _tab ("SE") _tab (se2_post2) _n

file write myfile ("row7 - column2") _tab ("coefficient") _tab (mean2_post3) _n

file write myfile ("row7 - column2") _tab ("SE") _tab (se2_post3) _n

file write myfile ("row8 - column2") _tab ("coefficient") _tab (mean2_post4) _n

file write myfile ("row8 - column2") _tab ("SE") _tab (se2_post4) _n

file write myfile ("row9 - column2") _tab ("coefficient") _tab (mean2_post5) _n

file write myfile ("row9 - column2") _tab ("SE") _tab (se2_post5) _n

file write myfile ("row10 - column2") _tab ("coefficient") _tab (mean2_window_post) _n

file write myfile ("row10 - column2") _tab ("SE") _tab (se2_window_post) _n


file write myfile ("row1 - column3") _tab ("coefficient") _tab (mean3_window_pre) _n

file write myfile ("row1 - column3") _tab ("SE") _tab (se3_window_pre) _n

file write myfile ("row2 - column3") _tab ("coefficient") _tab (mean3_pre3) _n

file write myfile ("row2 - column3") _tab ("SE") _tab (se3_pre3) _n

file write myfile ("row3 - column3") _tab ("coefficient") _tab (mean3_pre2) _n

file write myfile ("row3 - column3") _tab ("SE") _tab (se3_pre2) _n

file write myfile ("row4 - column3") _tab ("coefficient") _tab (mean3_0) _n

file write myfile ("row4 - column3") _tab ("SE") _tab (se3_0) _n

file write myfile ("row5 - column3") _tab ("coefficient") _tab (mean3_post1) _n

file write myfile ("row5 - column3") _tab ("SE") _tab (se3_post1) _n

file write myfile ("row6 - column3") _tab ("coefficient") _tab (mean3_post2) _n

file write myfile ("row6 - column3") _tab ("SE") _tab (se3_post2) _n

file write myfile ("row7 - column3") _tab ("coefficient") _tab (mean3_post3) _n

file write myfile ("row7 - column3") _tab ("SE") _tab (se3_post3) _n

file write myfile ("row8 - column3") _tab ("coefficient") _tab (mean3_post4) _n

file write myfile ("row8 - column3") _tab ("SE") _tab (se3_post4) _n

file write myfile ("row9 - column3") _tab ("coefficient") _tab (mean3_post5) _n

file write myfile ("row9 - column3") _tab ("SE") _tab (se3_post5) _n

file write myfile ("row10 - column3") _tab ("coefficient") _tab (mean3_window_post) _n

file write myfile ("row10 - column3") _tab ("SE") _tab (se3_window_post) _n

file close myfile










