***Predicting corruption in Brazil - Replication files***


**-- Analysis

use "$folder/data/final/dataset_AnalysisAudit.dta", clear

**Panel a (True corruption)

preserve
collapse (mean) narrow1_audit corr1_audit, by(cod_mun term)

estpost sum narrow1_audit corr1_audit
esttab . using "$folder/output/tables/Table1_a.tex", cells("mean(fmt(3)) sd(fmt(3)) min(fmt(3)) max(fmt(3)) count") replace
restore

**Panel b (Budget categories)

merge 1:1 cod_mun year using "$folder/data/final/panel_budget_corruption.dta"
drop if _merge==2
drop _merge lottery1 broad1 narrow1 fraction_broad1 fraction_narrow1 nsorteio1 date_sorteio1 year_sorteio1 month_sorteio1 day_sorteio1 date_released1 year_released1 month_released1 day_released1 lottery2 broad2 narrow2 fraction_broad2 fraction_narrow2 nsorteio2 date_sorteio2 year_sorteio2 month_sorteio2 day_sorteio2 date_released2 year_released2 month_released2 day_released2 id_city UF for_prediction lfalha_total lnirregular lmismanagement lno_os nirregular no_os falha_total mismanagement ratio_tot ratio_corr ratio_miss q_ratio_tot q_ratio_corr q_ratio_miss corr1 corr2 for_prediction2

foreach i in  Ativo AtivoFinanceiro Caixa Passivo PassivoFinanceiro Taxas RecPatrimonial DespesasOrçamentárias DespesasdeCapital  DespCorrentes  SUPERAVITouDEFICIT {
gen `i'_PC=`i'/Populacao
}

estpost sum Ativo_PC AtivoFinanceiro_PC Caixa_PC PassivoFinanceiro_PC Taxas_PC RecPatrimonial_PC DespesasOrçamentárias_PC DespesasdeCapital_PC DespCorrentes_PC SUPERAVITouDEFICIT_PC
esttab . using "$folder/output/tables/Table1_b.tex", cells("mean(fmt(1)) sd(fmt(1)) min(fmt(1)) max(fmt(1)) count") replace

**Panel c (Municipal characteristics)

estpost sum income agriculture industry commerce transport service public_administration employed graduated_people poverty gini_coefficient
esttab . using "$folder/output/tables/Table1_c.tex", cells("mean(fmt(1)) sd(fmt(1)) min(fmt(1)) max(fmt(1)) count") replace

**Panel d (Audit reports mentions)

use "$folder/data/working/biscatter_AuditReports.dta", clear

estpost sum count
esttab . using "$folder/output/tables/Table1_d.tex", cells("mean(fmt(1)) sd(fmt(1)) min(fmt(1)) max(fmt(1)) count") replace

