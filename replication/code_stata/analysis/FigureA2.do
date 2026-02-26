***Predicting corruption in Brazil - Replication files***


**-- Analysis

use "$folder/data/final/dataset_AnalysisAudit.dta", clear

merge 1:1 cod_mun year using "$folder/data/final/panel_budget_corruption.dta", keepusing(year_sorteio1 year_sorteio2 narrow1 narrow2 fraction_narrow1 fraction_narrow2)
drop if _merge==2
drop _merge

**-- Difference in true corruption

sort cod_mun year

gen year_second_sorteio=year_sorteio2

replace year_first_sorteio=. if year!=year_first_sorteio
replace year_second_sorteio=. if year!=year_second_sorteio

gen sign1=fraction_narrow1 if year_first_sorteio!=.
gen sign2=fraction_narrow2 if year_second_sorteio!=.

by cod_mun: egen corr_first_sorteio=max(sign1)
by cod_mun: egen corr_second_sorteio=max(sign2)

gen corr_diff_audit=corr_second_sorteio-corr_first_sorteio

keep if corr_diff_audit!=.

**-- Difference in predicted corruption - term measure

sort cod_mun term

by cod_mun term: egen sign3=mean(narrow1_prediction_NS)
gen sign4=sign3 if year_first_sorteio!=.
gen sign5=sign3 if year_second_sorteio!=.

by cod_mun: egen corr_first_sorteio_pr=max(sign4)
by cod_mun: egen corr_second_sorteio_pr=max(sign5)

gen corr_diff_predicted=corr_second_sorteio_pr-corr_first_sorteio_pr

duplicates drop cod_mun, force

**-- Binscatter

gen year_first=year_sorteio1
gen year_second=year_sorteio2

binsreg  corr_diff_audit corr_diff_predicted income employed agriculture industry commerce transport service public_administration graduated_people gini_coefficient, absorb(year_first ) xtitle("Difference in predicted corruption") ytitle("Difference in audit-based corruption") xlabel(, angle(45)) ylabel(, angle(45)) graphregion(fcolor(white)) polyreg(1) nbins(10)
graph export "$folder/output/appendix_figures/FigureA2.pdf", replace

**-- Regressions

*Standard
reg corr_diff_audit corr_diff_predicted i.year_first  income  agriculture industry commerce transport service public_administration graduated_people  gini_coefficient, r cluster(cod_mun)

*Without controls
reg corr_diff_audit corr_diff_predicted i.year_first, r cluster(cod_mun)

*Without controls and fixed effects
reg corr_diff_audit corr_diff_predicted, r cluster(cod_mun)
