***Predicting corruption in Brazil - Replication files***


**-- Analysis

use "$folder/data/final/dataset_AnalysisAudit.dta", clear

merge 1:1 cod_mun year using "$folder/data/working/corruption_predictions_NS_b_Avis_foldAll.dta"
drop if _merge==2
drop _merge

*Binscatter
binsreg  narrow1_prediction_NS corr1_prediction_NS, xtitle("Prediction Brollo et al. data") ytitle("Prediction Avis et al. data (corr1 measure)") xlabel(, angle(45)) ylabel(, angle(45)) graphregion(fcolor(white))
graph export "$folder/output/appendix_figures/FigureB3.png", replace

*Correlation
corr narrow1_prediction_NS corr1_prediction_NS
*0.5122 
