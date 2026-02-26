***Predicting corruption in Brazil - Replication files***


****---- Ancillary data with audit flag ----****

use "$folder/data/working/corruptiondata_lotteries_brollo_reshaped.dta", clear

gen lottery=(lottery1!=.)

rename narrow1 narrow1_auditT

keep cod_mun term narrow1_auditT lottery

save "$folder/data/working/brollo_lottery_flag_ancillary.dta", replace


****---- Data on municipal population ----****

foreach i in 2000 2001 2002 2003 2004 2005 2006 2008 2009{

import excel "$folder/data/source/population/POP-`i'.xls", sheet("municipality") clear

rename A state_code1
rename B state_code2
rename C city_code
rename D city_name
rename E population_census

tostring state_code2, replace
tostring city_code, replace
capture replace population_census=subinstr(population_census, "(*)", "", .)
destring population_census, replace

capture drop F
drop if city_name==""

gen year=`i'

save "$folder/data/working/pop_`i'", replace
}

**Final file
use "$folder/data/working/pop_2000.dta", clear

foreach i in 2001 2002 2003 2004 2005 2006 2008 2009{

append using "$folder/data/working/pop_`i'.dta", force

}

**Make up variables
replace city_name="Alto Alegre dos Parecis" if city_name=="Alto Alegre do Parecis"
replace city_name="Pedra Branca do Amapari" if city_name=="Pedra Branca do Amaparí"
replace city_name="Pindaré Mirim" if city_name=="Pindaré-Mirim"
replace city_name="Massapê do Piauí" if city_name=="Massâpe do Piauí"
replace city_name="Acarape" if city_name=="Acarapé"
replace city_name="São Miguel do Gostoso" if city_name=="São Miguel de Touros"
replace city_name="Quixaba" if city_name=="Quixabá"
replace city_name="Livramento de Nossa Senhora" if city_name=="Livramento do Brumado"
replace city_name="Dona Eusébia" if city_name=="Dona Euzébia"
replace city_name="Gouveia" if city_name=="Gouvêa"
replace city_name="Itabirinha" if city_name=="Itabirinha de Mantena"
replace city_name="Olhos-d'Água" if city_name=="Olhos-D'Água"
replace city_name="Passa-Vinte" if city_name=="Passa Vinte"
replace city_name="Pingo-d'Água" if city_name=="Pingo D'Água"
replace city_name="Queluzito" if city_name=="Queluzita"
replace city_name="Marataízes" if city_name=="Marataizes"
replace city_name="Brodowski" if city_name=="Brodósqui"
replace city_name="Ipaussu" if city_name=="Ipauçu"
replace city_name="Moji Mirim" if city_name=="Moji-Mirim"
replace city_name="Mogi das Cruzes" if city_name=="Moji das Cruzes"
replace city_name="Presidente Castello Branco" if city_name=="Presidente Castelo Branco"
replace city_name="Chiapetta" if city_name=="Chiapeta"
replace city_name="Batayporã" if city_name=="Bataiporã"
replace city_name="Nova Canaã do Norte" if city_name=="Nova Canãa do Norte"
replace city_name="Nova Monte Verde" if city_name=="Nova Monte verde"

drop if city_name=="Piçarras" | city_name=="Vila Alta" | city_name=="Governador Lomanto Júnior" | city_name=="Itamaracá" | city_name=="Espiríto Santo do Oeste"

gen sign=city_code if year==2008
sort state_code2 city_name year

replace sign=sign[_n-1] if city_name==city_name[_n-1] & year!=2008
replace sign=sign[_n+1] if city_name==city_name[_n+1] & year==2007
replace sign=sign[_n+1] if city_name==city_name[_n+1] & year==2006
replace sign=sign[_n+1] if city_name==city_name[_n+1] & year==2005
replace sign=sign[_n+1] if city_name==city_name[_n+1] & year==2004
replace sign=sign[_n+1] if city_name==city_name[_n+1] & year==2003
replace sign=sign[_n+1] if city_name==city_name[_n+1] & year==2002
replace sign=sign[_n+1] if city_name==city_name[_n+1] & year==2001
replace sign=sign[_n+1] if city_name==city_name[_n+1] & year==2000

gen sign2=state_code2+sign

drop state_code2 city_code sign
rename state_code1 state_code
rename sign2 city_code
order state_code city_code city_name year population_census

drop if state_code==""

save "$folder/data/working/population", replace


****---- Data on Transfers (FPM) ----****

import delimited "$folder/data/source/transferencias_para_municipios_yearly.csv", delimiter(";") encoding(ISO-8859-1) clear

drop município transferência  códigosiafi 

rename ano year
rename valorconsolidado FPM_transfers
rename códigoibge city_code

capture replace FPM_transfers=subinstr(FPM_transfers, "R$", "", .)
capture replace FPM_transfers=subinstr(FPM_transfers, ".", "", .)
capture replace FPM_transfers=subinstr(FPM_transfers, ",", ".", .)

destring FPM_transfers, replace
drop if year<2000

tostring city_code, replace

save "$folder/data/working/transfers", replace

****---- Data on municipal margin of victory ----****

**-- Elections 2000 --**

import delimited "$folder/data/source/electoral data/votacao_candidato_munzona_2000_BRASIL.csv", delimiter(";") encoding(ISO-8859-1) clear

keep if nr_turno==1

keep if ds_cargo=="Prefeito"

sort cd_municipio

gen elected=(ds_sit_tot_turno=="ELEITO")

collapse (sum) qt_votos_nominais_validos (mean) elected, by(cd_municipio ano_eleicao sg_uf nr_candidato sg_partido)

by cd_municipio: egen tot_votes=sum(qt_votos_nominais_validos)

gsort ano_eleicao cd_municipio - qt_votos_nominais_validos

gen victory_margin=(qt_votos_nominais_validos-qt_votos_nominais_validos[_n+1])/tot_votes if cd_municipio==cd_municipio[_n+1]

keep if elected==1

*Clean for multiple elected
sort cd_municipio

by cd_municipio: egen sign=sum(elected)

gsort ano_eleicao cd_municipio - qt_votos_nominais_validos

sort cd_municipio

by cd_municipio: gen sign2=_n

keep if sign2==1

drop sign*

*Final data
keep ano_eleicao cd_municipio victory_margin sg_uf sg_partido

rename ano_eleicao year_election
rename cd_municipio code_TSE
rename sg_uf uf

save "$folder/data/working/municipal_elections_2000.dta", replace

**-- Elections 2004 --**

import delimited "$folder/data/source/electoral data/votacao_candidato_munzona_2004_BRASIL.csv", delimiter(";") encoding(ISO-8859-1) clear

keep if nr_turno==1

keep if ds_cargo=="Prefeito"

sort cd_municipio

gen elected=(ds_sit_tot_turno=="ELEITO")

collapse (sum) qt_votos_nominais (mean) elected, by(cd_municipio ano_eleicao sg_uf nr_candidato sg_partido)

by cd_municipio: egen tot_votes=sum(qt_votos_nominais)

gsort ano_eleicao cd_municipio - qt_votos_nominais

gen victory_margin=(qt_votos_nominais-qt_votos_nominais[_n+1])/tot_votes if cd_municipio==cd_municipio[_n+1]

keep if elected==1

*Clean for multiple elected
sort cd_municipio

by cd_municipio: egen sign=sum(elected)

gsort ano_eleicao cd_municipio - qt_votos_nominais

sort cd_municipio

by cd_municipio: gen sign2=_n

keep if sign2==1

drop sign*

*Final data
keep ano_eleicao cd_municipio victory_margin sg_uf sg_partido

rename ano_eleicao year_election
rename cd_municipio code_TSE
rename sg_uf uf

save "$folder/data/working/municipal_elections_2004.dta", replace

**-- Elections 2008 --**

import delimited "$folder/data/source/electoral data/votacao_candidato_munzona_2008_BRASIL.csv", delimiter(";") encoding(ISO-8859-1) clear

keep if nr_turno==1

keep if ds_cargo=="Prefeito"

sort cd_municipio

gen elected=(ds_sit_tot_turno=="ELEITO")

collapse (sum) qt_votos_nominais (mean) elected, by(cd_municipio ano_eleicao sg_uf nr_candidato sg_partido)

by cd_municipio: egen tot_votes=sum(qt_votos_nominais)

gsort ano_eleicao cd_municipio - qt_votos_nominais

gen victory_margin=(qt_votos_nominais-qt_votos_nominais[_n+1])/tot_votes if cd_municipio==cd_municipio[_n+1]

keep if elected==1

*Clean for multiple elected
sort cd_municipio

by cd_municipio: egen sign=sum(elected)

gsort ano_eleicao cd_municipio - qt_votos_nominais

sort cd_municipio

by cd_municipio: gen sign2=_n

keep if sign2==1

drop sign*

*Final data
keep ano_eleicao cd_municipio victory_margin sg_uf sg_partido

rename ano_eleicao year_election
rename cd_municipio code_TSE
rename sg_uf uf

save "$folder/data/working/municipal_elections_2008.dta", replace

**-- Dataset to include IBGE code in the data --**

import delimited "$folder/data/source/electoral data/municipios_brasileiros_tse.csv", encoding(ISO-8859-1)clear

gen cod_mun=int(codigo_ibge/10)
rename codigo_tse code_TSE

save "$folder/data/working/municipality_codes.dta", replace

**-- Final dataset --**

use "$folder/data/working/municipal_elections_2000.dta", clear

append using "$folder/data/working/municipal_elections_2004.dta"
append using "$folder/data/working/municipal_elections_2008.dta"

merge n:1 code_TSE using "$folder/data/working/municipality_codes.dta"
drop if _merge==2
drop _merge

keep year_election cod_mun victory_margin

rename year_election term

sort cod_mun term

replace term=2001 if term==2000
replace term=2005 if term==2004
replace term=2009 if term==2008

save "$folder/data/working/victory_margin_elections.dta", replace

****---- Data on mayor party ----****

use "$folder/data/working/municipal_elections_2000.dta", clear

append using "$folder/data/working/municipal_elections_2004.dta"
append using "$folder/data/working/municipal_elections_2008.dta"

merge n:1 code_TSE using "$folder/data/working/municipality_codes.dta"
drop if _merge==2
drop _merge

keep year_election cod_mun sg_partido

rename year_election term
rename sg_partido SIGLA_PARTIDO

sort cod_mun term

replace term=2001 if term==2000
replace term=2005 if term==2004
replace term=2009 if term==2008

save "$folder/data/working/mayor_terms_all.dta", replace





























