***Predicting corruption in Brazil - Replication files***


****---- Dataset ----****

use "$folder/data/working/transfers", clear

merge 1:1 year city_code using "$folder/data/working/population"
drop if _merge==2
drop _merge

sort city_code year

replace state_code=state_code[_n-1] if city_code==city_code[_n-1] & year==2007 & year[_n-1]==2006
replace city_name=city_name[_n-1] if city_code==city_code[_n-1] & year==2007 & year[_n-1]==2006

drop if year>2008
drop if city_name==""

*Adjust at 2000 price
gen FPM_transfers_CPI=FPM_transfers
replace FPM_transfers_CPI=FPM_transfers*0.975936101 if year==2001
replace FPM_transfers_CPI=FPM_transfers*0.954240472 if year==2002
replace FPM_transfers_CPI=FPM_transfers*0.93569538 if year==2003
replace FPM_transfers_CPI=FPM_transfers*0.918615588 if year==2004
replace FPM_transfers_CPI=FPM_transfers*0.902906975 if year==2005
replace FPM_transfers_CPI=FPM_transfers*0.888076805 if year==2006
replace FPM_transfers_CPI=FPM_transfers*0.873994569 if year==2007
replace FPM_transfers_CPI=FPM_transfers*0.860869156 if year==2008

order state_code city_code city_name year population_census FPM_transfers FPM_transfers_CPI

**-- Genero i theoretical transfers (year specific)

*State level transfers
sort state_code year
by state_code year: egen fpm_year_state=sum(FPM_transfers)
by state_code year: egen fpm_CPI_year_state=sum(FPM_transfers_CPI)

gen pop_interval_1=(population_census<10189)
gen pop_interval_2=(population_census>=10189 & population_census<13584)
gen pop_interval_3=(population_census>=13584 & population_census<16980)
gen pop_interval_4=(population_census>=16980 & population_census<23772)
gen pop_interval_5=(population_census>=23772 & population_census<30564)
gen pop_interval_6=(population_census>=30564 & population_census<37356)
gen pop_interval_7=(population_census>=37356 & population_census<44148)
gen pop_interval_8=(population_census>=44148 & population_census<50940)

gen pop_interval_9=(population_census>=50940 & population_census<61128)
gen pop_interval_10=(population_census>=61128 & population_census<71316)
gen pop_interval_11=(population_census>=71316 & population_census<81504)
gen pop_interval_12=(population_census>=81504 & population_census<91692)
gen pop_interval_13=(population_census>=91692 & population_census<101880)
gen pop_interval_14=(population_census>=101880 & population_census<115464)
gen pop_interval_15=(population_census>=115464 & population_census<129048)
gen pop_interval_16=(population_census>=129048 & population_census<142632)
gen pop_interval_17=(population_census>=142632 & population_census<156216)
gen pop_interval_18=(population_census>=156216)

gen fpm_coefficient=.
replace fpm_coefficient=0.6 if pop_interval_1==1
replace fpm_coefficient=0.8 if pop_interval_2==1
replace fpm_coefficient=1 if pop_interval_3==1
replace fpm_coefficient=1.2 if pop_interval_4==1
replace fpm_coefficient=1.4 if pop_interval_5==1
replace fpm_coefficient=1.6 if pop_interval_6==1
replace fpm_coefficient=1.8 if pop_interval_7==1
replace fpm_coefficient=2 if pop_interval_8==1
replace fpm_coefficient=2.2 if pop_interval_9==1
replace fpm_coefficient=2.4 if pop_interval_10==1
replace fpm_coefficient=2.6 if pop_interval_11==1
replace fpm_coefficient=2.8 if pop_interval_12==1
replace fpm_coefficient=3 if pop_interval_13==1
replace fpm_coefficient=3.2 if pop_interval_14==1
replace fpm_coefficient=3.4 if pop_interval_15==1
replace fpm_coefficient=3.6 if pop_interval_16==1
replace fpm_coefficient=3.8 if pop_interval_17==1
replace fpm_coefficient=4 if pop_interval_18==1

by state_code year: egen fpm_coefficient_state=sum(fpm_coefficient)

gen fpm_year_predict=(fpm_year_state*fpm_coefficient)/fpm_coefficient_state
gen fpm_CPI_year_predict=(fpm_CPI_year_state*fpm_coefficient)/fpm_coefficient_state

drop pop_interval_1 pop_interval_2 pop_interval_3 pop_interval_4 pop_interval_5 pop_interval_6 pop_interval_7 pop_interval_8 pop_interval_9 pop_interval_10 pop_interval_11 pop_interval_12 pop_interval_13 pop_interval_14 pop_interval_15 pop_interval_16 pop_interval_17 pop_interval_18 fpm_coefficient fpm_coefficient_state

sort city_code year

**-- Transform the dataset in term specific

/*NB: following brollo et al. the population used for the term 2001 is the average for the years 2000/2001/2002, while the one for the term 2005 
is the average for the years 2004/2005/2006. For the transfers, the value used is the average in the first three years of the term: for 2001 it is 
the average of 2001/2002/2003, for the 2005, the average of 2005/2006/2007.*/

gen term=.
replace term=2001 if year<=2003
replace term=2005 if year>=2004

gen sign1=population_census if year<=2002 | (year>=2004 & year<=2006)
gen sign2=FPM_transfers if (year>=2001 & year<=2003) | (year>=2005 & year<=2007)
gen sign3=FPM_transfers_CPI if (year>=2001 & year<=2003) | (year>=2005 & year<=2007)
gen sign4=fpm_year_predict if (year>=2001 & year<=2003) | (year>=2005 & year<=2007)
gen sign5=fpm_CPI_year_predict if (year>=2001 & year<=2003) | (year>=2005 & year<=2007)

sort state_code city_code term

by state_code city_code term: egen population_term=mean(sign1)
by state_code city_code term: egen fpm_term=mean(sign2)
by state_code city_code term: egen fpm_CPI_term=mean(sign3)
by state_code city_code term: egen fpm_term_predict_v1=mean(sign4)
by state_code city_code term: egen fpm_CPI_term_predict_v1=mean(sign5)

sort city_code year

keep if year==2001 | year==2005
drop population_census FPM_transfers FPM_transfers_CPI sign*

replace fpm_term=fpm_term/100000
replace fpm_CPI_term=fpm_CPI_term/100000
replace fpm_term_predict_v1=fpm_term_predict_v1/100000
replace fpm_CPI_term_predict_v1=fpm_CPI_term_predict_v1/100000

drop year fpm_year_state fpm_CPI_year_state fpm_year_predict fpm_CPI_year_predict

**-- Genero i theoretical transfers (term specific)

*State level transfers
sort state_code term
by state_code term: egen fpm_term_state=sum(fpm_term)
by state_code term: egen fpm_CPI_term_state=sum(fpm_CPI_term)

gen pop_interval_1=(population_term<10189)
gen pop_interval_2=(population_term>=10189 & population_term<13584)
gen pop_interval_3=(population_term>=13584 & population_term<16980)
gen pop_interval_4=(population_term>=16980 & population_term<23772)
gen pop_interval_5=(population_term>=23772 & population_term<30564)
gen pop_interval_6=(population_term>=30564 & population_term<37356)
gen pop_interval_7=(population_term>=37356 & population_term<44148)
gen pop_interval_8=(population_term>=44148 & population_term<50940)

gen pop_interval_9=(population_term>=50940 & population_term<61128)
gen pop_interval_10=(population_term>=61128 & population_term<71316)
gen pop_interval_11=(population_term>=71316 & population_term<81504)
gen pop_interval_12=(population_term>=81504 & population_term<91692)
gen pop_interval_13=(population_term>=91692 & population_term<101880)
gen pop_interval_14=(population_term>=101880 & population_term<115464)
gen pop_interval_15=(population_term>=115464 & population_term<129048)
gen pop_interval_16=(population_term>=129048 & population_term<142632)
gen pop_interval_17=(population_term>=142632 & population_term<156216)
gen pop_interval_18=(population_term>=156216)

gen fpm_coefficient=.
replace fpm_coefficient=0.6 if pop_interval_1==1
replace fpm_coefficient=0.8 if pop_interval_2==1
replace fpm_coefficient=1 if pop_interval_3==1
replace fpm_coefficient=1.2 if pop_interval_4==1
replace fpm_coefficient=1.4 if pop_interval_5==1
replace fpm_coefficient=1.6 if pop_interval_6==1
replace fpm_coefficient=1.8 if pop_interval_7==1
replace fpm_coefficient=2 if pop_interval_8==1
replace fpm_coefficient=2.2 if pop_interval_9==1
replace fpm_coefficient=2.4 if pop_interval_10==1
replace fpm_coefficient=2.6 if pop_interval_11==1
replace fpm_coefficient=2.8 if pop_interval_12==1
replace fpm_coefficient=3 if pop_interval_13==1
replace fpm_coefficient=3.2 if pop_interval_14==1
replace fpm_coefficient=3.4 if pop_interval_15==1
replace fpm_coefficient=3.6 if pop_interval_16==1
replace fpm_coefficient=3.8 if pop_interval_17==1
replace fpm_coefficient=4 if pop_interval_18==1

by state_code term: egen fpm_coefficient_state=sum(fpm_coefficient)

gen fpm_term_predict_v2=(fpm_term_state*fpm_coefficient)/fpm_coefficient_state
gen fpm_CPI_term_predict_v2=(fpm_CPI_term_state*fpm_coefficient)/fpm_coefficient_state

drop pop_interval_1 pop_interval_2 pop_interval_3 pop_interval_4 pop_interval_5 pop_interval_6 pop_interval_7 pop_interval_8 pop_interval_9 pop_interval_10 pop_interval_11 pop_interval_12 pop_interval_13 pop_interval_14 pop_interval_15 pop_interval_16 pop_interval_17 pop_interval_18

sort city_code term

**-- Importo i dati su corruption prediction

gen municipio=city_name
replace municipio=subinstr(municipio, "à", "a", .)
replace municipio=subinstr(municipio, "á", "a", .)
replace municipio=subinstr(municipio, "è", "e", .)
replace municipio=subinstr(municipio, "ì", "i", .)
replace municipio=subinstr(municipio, "ò", "o", .)
replace municipio=subinstr(municipio, "ù", "u", .)
replace municipio=subinstr(municipio, "é", "e", .)
replace municipio=subinstr(municipio, "ô", "o", .)
replace municipio=subinstr(municipio, "ç", "c", .)
replace municipio=subinstr(municipio, "ã", "a", .)
replace municipio=subinstr(municipio, "â", "a", .)
replace municipio=subinstr(municipio, "ê", "e", .)
replace municipio=subinstr(municipio, "í", "i", .)
replace municipio=subinstr(municipio, "ú", "u", .)
replace municipio=subinstr(municipio, "ó", "o", .)
replace municipio=subinstr(municipio, "Í", "i", .)
replace municipio=subinstr(municipio, "-", " ", .)
replace municipio=subinstr(municipio, "õ", "o", .)
replace municipio=subinstr(municipio, "Á", "a", .)
replace municipio=subinstr(municipio, "Â", "a", .)

replace municipio=upper(municipio)

gen id_state=state_code

duplicates report term municipio id_state

**-- Merge predictions

gen cod_mun=city_code
replace cod_mun=substr(cod_mun, 1, 6)
destring cod_mun, replace

merge 1:1 term cod_mun using "$folder/data/working/corruption_predictions_NS_b_foldAll.dta"
drop if _merge==2
drop _merge 

**-- Merge predictions HoldOut

merge 1:1 term cod_mun using "$folder/data/working/corruption_predictions_NS_b_foldAll_HoldOutData.dta"
drop if _merge==2
drop _merge 

sort cod_mun term

**-- Save entire dataset

save "$folder/data/final/dataset_AnalysisTransfer_full.dta", replace

**-- Keep only cities in the sample used by Brollo et al.
*NB: this sample only includes municipalities with population in this range [6,793-50,940]

sort cod_mun term

gen sign=population_term if term==2001

by cod_mun: egen population_2001=max(sign)
drop sign
drop if population_term<6793 | population_term>50940

drop if narrow1_predictionT_Av==.

**-- Merge true corruption levels

merge 1:1 term cod_mun using "$folder/data/working/brollo_lottery_flag_ancillary.dta", keepusing(lottery narrow1_auditT)
drop if _merge==2
drop _merge

replace lottery=0 if lottery==.

gen audit_brollo=(lottery==1)

**-- Merge predictions on demographics

merge 1:1 term cod_mun using "$folder/data/working/corruption_predictions_S_d_foldAll.dta", keepusing(narrow1_predictionT_d)
drop if _merge==2
drop _merge

**-- Merge predictions withouf FPM

merge 1:1 term cod_mun using "$folder/data/working/corruption_predictions_NS_b_fpm_foldAll.dta", keepusing(narrow1_predictionT_noFPM)
drop if _merge==2
drop _merge

**-- Save

*Variables we use in the analysis do-files
*keep population_term state_code city_code fpm_CPI_term fpm_CPI_term_predict_v2 term audit_brollo narrow1_predictionT narrow1_auditT fpm_coefficient narrow1_predictionT_d narrow1_predictionT_noFPM narrow1_predictionT_Av_fold0 narrow1_predictionT_Av_fold1

save "$folder/data/final/dataset_AnalysisTransfer.dta", replace
