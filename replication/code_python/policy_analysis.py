import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import accuracy_score, recall_score, precision_score
import os
import glob

sns.set_theme(style="whitegrid")

# ----------------------------
# LOAD THE RAW DATA AND MERGE INTO DF
# ----------------------------


relevant_csv_sample = "./data/working/merged/xgboost_sample_b.csv"
relevant_csv_nosample = "./data/working/merged/xgboost_nosample_b.csv"

print("Working with:")
print(relevant_csv_sample)
print(relevant_csv_nosample)


csv_sample = pd.read_csv(relevant_csv_sample)
csv_nosample = pd.read_csv(relevant_csv_nosample)

# now we rename the columns:


csv_nosample['narrow1_predicted_NS_mean'] = csv_nosample['narrow1_cv_prediction'].fillna(csv_nosample['narrow1_oof_prediction'])
csv_nosample['corr1_predicted_NS_mean'] = csv_nosample['corr1_cv_prediction'].fillna(csv_nosample['corr1_oof_prediction'])

csv_sample['narrow1_predicted_S_mean'] = csv_sample['narrow1_cv_prediction'].fillna(csv_sample['narrow1_oof_prediction'])
csv_sample['corr1_predicted_S_mean'] = csv_sample['corr1_cv_prediction'].fillna(csv_sample['corr1_oof_prediction'])


column_rename_no_sample = {
    'cod_mun': 'cod_mun',
    'year': 'year',
    'narrow1': 'narrow1_audit',
    'corr1': 'corr1_audit',
    'narrow1_predicted_0' : 'narrow1_predicted_NS_fold0',
    'narrow1_predicted_1' : 'narrow1_predicted_NS_fold1',
    'narrow1_predicted_2' : 'narrow1_predicted_NS_fold2',
    'narrow1_predicted_3' : 'narrow1_predicted_NS_fold3',
    'narrow1_predicted_4' : 'narrow1_predicted_NS_fold4',
    'corr1_predicted_0' : 'corr1_predicted_NS_fold0',
    'corr1_predicted_1' : 'corr1_predicted_NS_fold1',
    'corr1_predicted_2' : 'corr1_predicted_NS_fold2',
    'corr1_predicted_3' : 'corr1_predicted_NS_fold3',
    'corr1_predicted_4' : 'corr1_predicted_NS_fold4',
}

columns_rename_sample = {
    'cod_mun': 'cod_mun',
    'year': 'year',
    'narrow1': 'narrow1_audit',
    'corr1': 'corr1_audit',
    'narrow1_predicted_0':'narrow1_predicted_S_fold0',
    'narrow1_predicted_1':'narrow1_predicted_S_fold1',
    'narrow1_predicted_2':'narrow1_predicted_S_fold2',
    'narrow1_predicted_3':'narrow1_predicted_S_fold3',
    'narrow1_predicted_4':'narrow1_predicted_S_fold4',
}


# now we rename the columns:

csv_nosample = csv_nosample.rename(columns=column_rename_no_sample)
csv_sample = csv_sample.rename(columns=columns_rename_sample)

cols_to_keep_no_sample = list(column_rename_no_sample.values()) + ['narrow1_predicted_NS_mean','corr1_predicted_NS_mean','for_prediction','for_prediction2']
cols_to_keep_sample = list(columns_rename_sample.values()) + ['narrow1_predicted_S_mean','corr1_predicted_S_mean','for_prediction','for_prediction2']


# filter out the columns we don't need
csv_nosample_cleaned = csv_nosample[cols_to_keep_no_sample]
csv_sample_cleaned = csv_sample[cols_to_keep_sample]

# merge both dataframes on cod_mun, year, narrow1, corr1

df = pd.merge(csv_nosample_cleaned, csv_sample_cleaned, on=['cod_mun', 'year'], how="outer", indicator=True,suffixes=('_nosample', '_sample'))




# recall that either we are oof or cv but not both so we can add them together!
df['narrow1_prediction_S'] = df['narrow1_predicted_S_mean']
df['narrow1_prediction_NS'] = df['narrow1_predicted_NS_mean']
df['corr1_prediction_S'] = df['corr1_predicted_S_mean']
df['corr1_prediction_NS'] = df['corr1_predicted_NS_mean']



lottery_data = pd.read_stata('./data/working/corruptiondata_lotteries_brollo_reshaped.dta')
lottery_data = lottery_data[['cod_mun','year_sorteio1']]
lottery_data_cleaned = lottery_data.groupby('cod_mun', as_index=False)['year_sorteio1'].min()
df = pd.merge(df, lottery_data_cleaned, on=['cod_mun'], how='left')
df['distance_audit_brollo'] = df['year'] - df['year_sorteio1']




df['term'] = 2005
df.loc[df['year'] <= 2004, 'term'] = 2001
df.loc[df['year'] >= 2009, 'term']  = 2009
print("term value counts: ")
print(df['term'].value_counts())

mayors = pd.read_stata('./data/working/mayor_terms_all.dta')

df_party_conditioned = df.copy()
df_party_conditioned = pd.merge(df_party_conditioned,mayors,how='left',on=['cod_mun','term'])
df_party_conditioned['SIGLA_PARTIDO'] = df_party_conditioned['SIGLA_PARTIDO'].replace('PFL','DEM')
df_party_conditioned['SIGLA_PARTIDO'] = df_party_conditioned['SIGLA_PARTIDO'].replace('PPB','PP')

print(df_party_conditioned.SIGLA_PARTIDO.value_counts())


main_parties = ['PMDB', 'PSDB', 'DEM', 'PP', 'PTB', 'PT']
app_parties = ['PDT', 'PSB', 'PL', 'PPS', 'PR']

df_party_conditioned = df_party_conditioned[df_party_conditioned.SIGLA_PARTIDO.isin(main_parties)].reset_index()

# limit to first audit
df['audit_first'] = (df['distance_audit_brollo'] == 0)
df_party_conditioned['audit_first'] = (df_party_conditioned['distance_audit_brollo'] == 0)

dfg = df[df['audit_first']]
dfg_party_conditioned = df_party_conditioned[df_party_conditioned['audit_first']]

num_audits = df_party_conditioned['audit_first'].sum()
num_munis = len(set(df_party_conditioned['cod_mun']))

print('Number of municipalities: ', num_munis)
print('Number of audits: ', num_audits)


# ----------------------------
# Figure 1 -- Calibration Plot
# ----------------------------

plt.clf()
sns.regplot(x=dfg['narrow1_prediction_NS'], 
            y=dfg['narrow1_audit_nosample'], 
            x_bins=20,
            label="Corruption Rate", 
            fit_reg=False,
               ci=None)

ax = sns.histplot(x=dfg['narrow1_prediction_NS'], bins=20,stat='probability')
ax.set(ylim=(0, 1), xlim=(0,1), ylabel="Audit Detected Corruption Rate", xlabel="Predicted Corruption Probability")
#ax.legend()
sns.lineplot(data=pd.DataFrame([[0,0],[1,1]]),legend=False)
ax.lines[1].set_linestyle("--")
ax.lines[0].set_linestyle("--")
plt.savefig('./output/figures/figure_1.pdf')


# ----------------------------
# Figure A1 -- Additional Calibration Plots
# ----------------------------

# calibration plots for five folds
plt.clf()
ax = sns.regplot(x=dfg['narrow1_predicted_NS_fold0'], 
            y=dfg['narrow1_audit_nosample'], 
            x_bins=20,
            label="Corruption Rate", 
            fit_reg=False,
               ci=None)
sns.regplot(x=dfg['narrow1_predicted_NS_fold1'], 
            y=dfg['narrow1_audit_nosample'], 
            x_bins=20,
            label="Corruption Rate", 
            fit_reg=False,
               ci=None)
sns.regplot(x=dfg['narrow1_predicted_NS_fold2'], 
            y=dfg['narrow1_audit_nosample'], 
            x_bins=20,
            label="Corruption Rate", 
            fit_reg=False,
               ci=None)
sns.regplot(x=dfg['narrow1_predicted_NS_fold3'], 
            y=dfg['narrow1_audit_nosample'], 
            x_bins=20,
            label="Corruption Rate", 
            fit_reg=False,
               ci=None)
sns.regplot(x=dfg['narrow1_predicted_NS_fold4'], 
            y=dfg['narrow1_audit_nosample'], 
            x_bins=20,
            label="Corruption Rate", 
            fit_reg=False,
               ci=None)
#ax = sns.histplot(x=dfg['narrow1_prediction_NS'], bins=20,stat='probability')
ax.set(ylim=(0, 1), xlim=(0,1), ylabel="Audit Detected Corruption Rate", xlabel="Predicted Corruption Probability (Five Folds)")
#ax.legend()
sns.lineplot(data=pd.DataFrame([[0,0],[1,1]]),legend=False)
ax.lines[1].set_linestyle("--")
ax.lines[0].set_linestyle("--")
plt.savefig('./output/appendix_figures/figure_a1_1.pdf')

plt.clf()
sns.regplot(x=dfg['narrow1_predicted_S_mean'], 
            y=dfg['narrow1_audit_sample'], 
            x_bins=20,
            label="Corruption Rate", 
            fit_reg=False,
               ci=None)

ax = sns.histplot(x=dfg['narrow1_predicted_S_mean'], bins=20,stat='probability')
ax.set(ylim=(0, 1), xlim=(0,1), ylabel="Audit Detected Corruption Rate", xlabel="Predicted Corruption Probability")
#ax.legend()
sns.lineplot(data=pd.DataFrame([[0,0],[1,1]]),legend=False)
ax.lines[1].set_linestyle("--")
ax.lines[0].set_linestyle("--")
plt.savefig('./output/appendix_figures/figure_a1_2.pdf')

plt.clf()
sns.regplot(x=dfg['corr1_predicted_NS_mean'], 
            y=dfg['narrow1_audit_nosample'], 
            x_bins=20,
            label="Corruption Rate", 
            fit_reg=False,
               ci=None)

ax = sns.histplot(x=dfg['corr1_predicted_NS_mean'], bins=20,stat='probability')
ax.set(ylim=(0, 1), xlim=(0,1), ylabel="Audit Detected Corruption Rate", xlabel="Predicted Corruption Probability")
#ax.legend()
sns.lineplot(data=pd.DataFrame([[0,0],[1,1]]),legend=False)
ax.lines[1].set_linestyle("--")
ax.lines[0].set_linestyle("--")
plt.savefig('./output/appendix_figures/figure_a1_3.pdf')
plt.clf()

# ----------------------------
# Table 4: Calculations/Results for Targeting Audits
# ----------------------------


df_party_conditioned['narrow1_predicted_NS'] = df_party_conditioned['narrow1_prediction_NS'] > .5
df_party_conditioned['narrow1_prediction_NS_fold0'] = df_party_conditioned['narrow1_predicted_NS_fold0'] > .5
df_party_conditioned['narrow1_prediction_NS_fold1'] = df_party_conditioned['narrow1_predicted_NS_fold1'] > .5
df_party_conditioned['narrow1_prediction_NS_fold2'] = df_party_conditioned['narrow1_predicted_NS_fold2'] > .5
df_party_conditioned['narrow1_prediction_NS_fold3'] = df_party_conditioned['narrow1_predicted_NS_fold3'] > .5
df_party_conditioned['narrow1_prediction_NS_fold4'] = df_party_conditioned['narrow1_predicted_NS_fold4'] > .5
df_party_conditioned['corr1_prediction_NS_fold0'] = df_party_conditioned['corr1_predicted_NS_fold0'] > .5
df_party_conditioned['corr1_prediction_NS_fold1'] = df_party_conditioned['corr1_predicted_NS_fold1'] > .5
df_party_conditioned['corr1_prediction_NS_fold2'] = df_party_conditioned['corr1_predicted_NS_fold2'] > .5
df_party_conditioned['corr1_prediction_NS_fold3'] = df_party_conditioned['corr1_predicted_NS_fold3'] > .5
df_party_conditioned['corr1_prediction_NS_fold4'] = df_party_conditioned['corr1_predicted_NS_fold4'] > .5
df_party_conditioned['corr1_prediction_NS_mean'] = df_party_conditioned['corr1_predicted_NS_mean'] > .5
df_party_conditioned['narrow1_prediction_S_fold0'] = df_party_conditioned['narrow1_predicted_S_fold0'] > .5
df_party_conditioned['narrow1_prediction_S_fold1'] = df_party_conditioned['narrow1_predicted_S_fold1'] > .5
df_party_conditioned['narrow1_prediction_S_fold2'] = df_party_conditioned['narrow1_predicted_S_fold2'] > .5
df_party_conditioned['narrow1_prediction_S_fold3'] = df_party_conditioned['narrow1_predicted_S_fold3'] > .5
df_party_conditioned['narrow1_prediction_S_fold4'] = df_party_conditioned['narrow1_predicted_S_fold4'] > .5
df_party_conditioned['narrow1_prediction_S_mean'] = df_party_conditioned['narrow1_predicted_S_mean'] > .5

# number of audits,number of municipalities, corruption rate
num_audits = df_party_conditioned['audit_first'].sum()
num_munis = len(set(df_party_conditioned['cod_mun']))

print('Number of municipalities: ', num_munis)
print('Number of audits: ', num_audits)

# dictionary for results:
table4 = {}

## Status Quo: Columns 1a / 1b

corrupt_rate_simulated = df_party_conditioned['narrow1_predicted_NS'].mean()
print('Corruption rate, simulated from ML prediction (Table 4, Column 1a, Row 1): ', corrupt_rate_simulated)
table4['1a','1'] = corrupt_rate_simulated

corrupt_rate_true_audited = df_party_conditioned[df_party_conditioned['audit_first']]['narrow1_audit_nosample'].mean()
print('Corruption rate, true if audited (Table 4, Column 1b, Row 1): ', corrupt_rate_true_audited)
table4['1b','1'] = corrupt_rate_true_audited

# number of years where audits happened, number of audits per year
years_with_audits = set(df_party_conditioned[df_party_conditioned['audit_first']]['year'])
num_audit_years = len(years_with_audits)
audits_per_year = num_audits / num_audit_years
print('Years with audits: ', years_with_audits)
print('Number of years with audits: ', num_audit_years)
print('Number of audits per year: ', audits_per_year)

print(df_party_conditioned.groupby('year')['audit_first'].sum())

# Set audit rate, number of corrupt municipalities / number of municipalities
audit_rate = audits_per_year / num_munis
print('Audit rate (Table 4, Columns 1a/1b, Row 3): ', audit_rate)
table4['1a','3'] = audit_rate
table4['1b','3'] = audit_rate

E_corrupt_munis = num_munis * corrupt_rate_true_audited
print('Expected number of corrupt municipalities: ', E_corrupt_munis)

# Probability a municipality detected as corrupt
# = corruption rate * audit rate
detects_per_muni = corrupt_rate_true_audited * audit_rate
print('Overall probability a municipality detected as corrupt: ', detects_per_muni)

# Average corrupt municipalities detected
N_detected_per_year = audits_per_year * corrupt_rate_true_audited
print('Expected number of detected municipalities per year: ', N_detected_per_year)

## Targeting: Columns 2a / 2b

df_party_conditioned['one'] = 1
df_party_conditioned['num_by_year'] = df_party_conditioned.groupby('year')['one'].transform(sum)
df_party_conditioned['num_by_year'].mean()

df['one'] = 1
df['num_by_year'] = df.groupby('year')['one'].transform(sum)

#for j in ['narrow1', 'corr1']:
#    for k in ['S', 'NS']:
for j in ['narrow1']:
    for k in ['NS']:
        df_party_conditioned['rank_by_year_%s_%s' % (j,k)] = df_party_conditioned.groupby('year')['%s_prediction_%s' %(j,k)].rank()   
        df['rank_by_year_%s_%s' % (j,k)] = df.groupby('year')['%s_prediction_%s' %(j,k)].rank()   
                
# ML-targeted municipalities in each year, and the bottom-ranked for comparison
#for j in ['narrow1', 'corr1']:
#    for k in ['S', 'NS']:
for j in ['narrow1']:
    for k in ['NS']:
        df_party_conditioned['targeted_%s_%s'%(j,k)] = df_party_conditioned['rank_by_year_%s_%s'%(j,k)] >= df_party_conditioned['num_by_year'] - audits_per_year
        df_party_conditioned['bottom_%s_%s'%(j,k)] = df_party_conditioned['rank_by_year_%s_%s'%(j,k)] <= audits_per_year
        df['targeted_%s_%s'%(j,k)] = df['rank_by_year_%s_%s'%(j,k)] >= df['num_by_year'] - audits_per_year
        df['bottom_%s_%s'%(j,k)] = df['rank_by_year_%s_%s'%(j,k)] <= audits_per_year

# what is the average predicted corruption probability for the targeted sample?
corrupt_rate_targeted_simulated = {}
for j in ['narrow1']:
    for k in ['NS']:
        corrupt_rate_targeted_simulated[j,k] = df_party_conditioned[df_party_conditioned['targeted_%s_%s'%(j,k)]]['%s_prediction_%s'%(j,k)].mean()

print('Corruption rate for targeted sample, simulated (Table 4, Column 2a, Row 1): ', corrupt_rate_targeted_simulated['narrow1','NS'])
table4['2a','1'] = corrupt_rate_targeted_simulated['narrow1','NS']


print('Targeting ratio over random audits, simulated (Table 4, Column 2a, Row 2): ', corrupt_rate_targeted_simulated['narrow1','NS'] / corrupt_rate_simulated)
table4['2a','2'] = corrupt_rate_targeted_simulated['narrow1','NS'] / corrupt_rate_simulated

# how corrupt for the targeted sample if audited?
corrupt_rate_targeted_true_audited = {}

corrupt_rate_targeted_true_audited[j,k] = df_party_conditioned[df_party_conditioned['audit_first'] & df_party_conditioned['targeted_narrow1_NS']]['narrow1_audit_nosample'].mean()

print('Corruption rate for targeted sample, if actually audited (Table 4, Column 2b, Row 1): ', corrupt_rate_targeted_true_audited['narrow1','NS'])
table4['2b','1'] = corrupt_rate_targeted_true_audited['narrow1','NS']

print('Targeting ratio over random audits, true-if-audited (Table 4, Column 2b, Row 2): ', corrupt_rate_targeted_true_audited['narrow1','NS'] / corrupt_rate_true_audited)
table4['2b','2'] = corrupt_rate_targeted_true_audited['narrow1','NS'] / corrupt_rate_true_audited

# targeted-auditing rate if corrupt, simulated
targeted_rate_if_corrupt_simulated = {}
#for j in ['narrow1', 'corr1']:
#    for k in ['S', 'NS']:
for j in ['narrow1']:
    for k in ['NS']:
        targeted_rate_if_corrupt_simulated[j,k] = df_party_conditioned[df_party_conditioned['%s_predicted_%s'%(j,k)]]['targeted_%s_%s'%(j,k)].mean()

print('Audit rate if corrupt under targeting, if actually audited (Table 4, Column 2a, Row 3): ', targeted_rate_if_corrupt_simulated['narrow1','NS'])
print('Ratio over random audits (Table 4, Column 2a, Row 4): ', targeted_rate_if_corrupt_simulated['narrow1','NS'] / audit_rate)
table4['2a','3'] = targeted_rate_if_corrupt_simulated['narrow1','NS']
table4['2a','4'] = targeted_rate_if_corrupt_simulated['narrow1','NS'] / audit_rate

# targeted-auditing rate if corrupt, limited to truly audited
targeted_rate_if_corrupt_true_audited = {}
#for j in ['narrow1', 'corr1']:
#    for k in ['S', 'NS']:
for j in ['narrow1']:
    for k in ['NS']:
        targeted_rate_if_corrupt_true_audited[j,k] = df_party_conditioned[df_party_conditioned['audit_first'] & df_party_conditioned['narrow1_audit_nosample']]['targeted_%s_%s'%(j,k)].mean()

print('Audit rate if corrupt under targeting, if actually audited (Table 4, Column 2b, Row 3): ', targeted_rate_if_corrupt_true_audited['narrow1','NS'])
print('Ratio over random audits (Table 4, Column 2b, Row 4): ', targeted_rate_if_corrupt_true_audited['narrow1','NS'] / audit_rate)
table4['2b','3'] = targeted_rate_if_corrupt_true_audited['narrow1','NS']
table4['2b','4'] = targeted_rate_if_corrupt_true_audited['narrow1','NS'] / audit_rate

# ----------------------------
# Figure F9 -- Targeting Illustration
# ----------------------------

# by year: lowest corruption probability threshold 
threshold_by_year = {}
for j in ['narrow1']:
    for k in ['NS']:
        threshold_by_year[j,k] = df[df['audit_first'] & df['targeted_%s_%s'%(j,k)]].groupby('year')['%s_prediction_%s'%(j,k)].min()

print('Corruption rate for targeted sample by year: ', threshold_by_year)

avg_thres = {}
for j in ['narrow1']:
    for k in ['NS']:
        avg_thres[j,k] = threshold_by_year[j,k].mean()

print("Average predicted probability threshold across years:", avg_thres)
plt.clf()


for j in ['narrow1']:
    for k in ['NS']:
        #sns.regplot(x=dfg['%s_prediction_%s'%(j,k)], y=dfg['%s_audit'%j], x_bins=20,label="Corruption Rate", ci=None)
        ax = sns.histplot(x=dfg['%s_prediction_%s'%(j,k)], bins=20,stat='probability',color='gray',alpha=.5)
        plt.axvline(x=avg_thres[j,k], color='g', linestyle='--', label="Targeted Audit Threshold")
        plt.axhline(y=audit_rate, color='b', linestyle='--', label="Random Audit Rate")
        ax.set(ylim=(0, 1), xlim=(0,1), ylabel="Corruption and Audit Rate", xlabel="Predicted Corruption Probability")
        
        # dashed line
        sns.lineplot(data=pd.DataFrame([[0,0],[1,1]]),legend=False, alpha=.5)
        ax.lines[2].set_linestyle("--")
        ax.lines[3].set_linestyle("--")
        
        # thick line
        linedf = pd.DataFrame([[avg_thres[j,k],avg_thres[j,k]],[1,1]],columns=['x','y'])
        sns.lineplot(x='x',y='y',data=linedf,label='Targeted Municipalities',linewidth=3,color='g')
        #plt.plot(x=[m_threshold[j,k],m_threshold[j,k]],y=[1,1])
        #ax.lines[2].set_linestyle("--")
        #ax.lines[3].set_linestyle("--")
                
        ax.legend()
        plt.savefig('./output/appendix_figures/figure_f9.pdf')
        plt.clf()
        
        
        
# ----------------------------
# Figure F10 -- Distribution of Parties
# ----------------------------

left2right = ['PT','PMDB','PSDB','PTB','DEM', 'PP',]
sns.set_theme(style="whitegrid")

sns.set_context("paper", font_scale=1.1)  
ax1 = sns.countplot(x=df_party_conditioned['SIGLA_PARTIDO'],order=left2right)
ax1.set(ylabel="Count", xlabel="Mayor Political Party")
plt.savefig('./output/appendix_figures/figure_f10.pdf')
plt.clf()


# ----------------------------
# Figure 5 Panel A
# ----------------------------


dfa = df_party_conditioned[df_party_conditioned['audit_first']==1]
dfa = dfa[pd.notnull(dfa['narrow1_audit_nosample'])]

sns.set_context("paper", font_scale=1.7)  
sns.set_palette("Set2")
fig, ax1 = plt.subplots(figsize=(10, 6.5))
tidy = dfa.melt(id_vars='SIGLA_PARTIDO', value_vars=['narrow1_audit_nosample', 'narrow1_predicted_NS'])
tidy['variable'].replace('narrow1_audit_nosample', 'True Corruption Rate', inplace=True)
tidy['variable'].replace('narrow1_predicted_NS', 'Predicted Corruption Rate', inplace=True)
g = sns.barplot(x='SIGLA_PARTIDO', y='value', hue='variable',data=tidy, ax=ax1,
           order=left2right)
leg = g.legend(loc='upper center', bbox_to_anchor=(0, 0., 0.9, 1))
leg.set_title(None)
#sns.barplot(x='SIGLA_PARTIDO', y='narrow1_NS', data=tidy, ax=ax2)
#sns.despine(fig)
#ax1.legend(title=" ",labels=['True Corruption Rate',"Predicted Corruption Rate"])
ax1.set(ylabel=" ", xlabel="Mayor Political Party")
g.set_title('True Corruption Rate and Predicted Corruption Rate, by Party', fontsize=19)
plt.savefig('./output/figures/figure_5a.pdf')

plt.clf()

# ----------------------------
# Figure 5 Panel B
# ----------------------------

from collections import defaultdict
munis_by_party = defaultdict(int)
audits_by_party = defaultdict(int)
audit_share = {}
parties_all = set(df_party_conditioned.SIGLA_PARTIDO.unique())

# all munis, not just audited
for party in parties_all:  
    if pd.isnull(party):
        continue
    for term in range(2001,2013):
        dft = df_party_conditioned[(df_party_conditioned['SIGLA_PARTIDO'] == party) & (df_party_conditioned['year'] == term)]
        N = len(dft)
        dfy = df_party_conditioned[df_party_conditioned['year'] == term]
        Nyear = len(dfy)        
        munis_by_party[party,term] = N
        audit_share[party,term] = N / Nyear
        # EA use floor to avoid that rounding increases overall audit rate
        audits_by_party[party,term] = np.floor(audit_share[party,term] * audits_per_year)
        
def fair_target(x):
    # returns true if first arg (corruption rank) is greater 
    # EA use > because >= increases overall audit rate
    return x[0] > munis_by_party[x[1],x[2]] - audits_by_party[x[1],x[2]]

# get party ranks and targeting by year
df_party_conditioned['party_rank_NS'] = df_party_conditioned.groupby(['SIGLA_PARTIDO','year'])['narrow1_prediction_NS'].rank()
df_party_conditioned['fair_targeted_NS'] = df_party_conditioned[['party_rank_NS', 'SIGLA_PARTIDO', 'year']].apply(fair_target, axis=1)
df_party_conditioned['targeted_NS'] = df_party_conditioned['targeted_narrow1_NS']

sns.set_context("paper", font_scale=1.7)  
sns.set_palette("Set1")
fig, ax1 = plt.subplots(figsize=(10, 6.5))
tidy = df_party_conditioned.melt(id_vars='SIGLA_PARTIDO', value_vars=['targeted_NS', 'fair_targeted_NS'])
tidy['variable'].replace('targeted_NS', 'Targeted Auditing Rate', inplace=True)
tidy['variable'].replace('fair_targeted_NS', 'Fair Targeting Rate', inplace=True)
g = sns.barplot(x='SIGLA_PARTIDO', y='value', hue='variable',data=tidy, ax=ax1,
           order=left2right)
leg = g.legend(loc='upper center', bbox_to_anchor=(0, 0., 0.75, 1))
leg.set_title(None)
plt.axhline(y=.036, color='g', linestyle='--')

ax1.set(ylabel=" ", xlabel="Mayor Political Party")
g.set_title('Targeted Auditing Rate and Fair Targeting Rate, by Party', fontsize=19)
plt.savefig('./output/figures/figure_5b.pdf')
plt.clf()

# ----------------------------
# Table 4, Column 3
# ----------------------------

corrupt_rate_true_audited_df = df_party_conditioned[df_party_conditioned['audit_first']]['narrow1_audit_nosample'].mean()

# how corrupt for the fair-targeted sample, simulated?
corrupt_rate_fairtarget_simulated = df_party_conditioned[df_party_conditioned['fair_targeted_NS']]['narrow1_prediction_NS'].mean()

print('Corruption rate for fair-targeted sample, if actually audited (Table 4, Column 3, Row 1): ', corrupt_rate_fairtarget_simulated)

table4['3','1'] = corrupt_rate_fairtarget_simulated

print('Targeting ratio over random audits, true-if-audited (Table 4, Column 3, Row 2): ', corrupt_rate_fairtarget_simulated / corrupt_rate_simulated)
table4['3','2'] = corrupt_rate_fairtarget_simulated / corrupt_rate_simulated

# how corrupt for the fair-targeted sample if audited?
corrupt_rate_fairtarget_true_audited = df_party_conditioned[df_party_conditioned['audit_first'] & df_party_conditioned['fair_targeted_NS']]['narrow1_audit_nosample'].mean()

print('Corruption rate for fair-targeted sample, if actually audited (Table 4, Column 3, Row 1): ', corrupt_rate_fairtarget_true_audited)

print('Targeting ratio over random audits, true-if-audited (Table 4, Column 3, Row 2): ', corrupt_rate_fairtarget_true_audited / corrupt_rate_true_audited)

# targeted-auditing rate if corrupt, simulated
fairtargeted_rate_if_corrupt_simulated = df_party_conditioned[df_party_conditioned['narrow1_predicted_NS']]['fair_targeted_NS'].mean()

print('Audit rate if corrupt under fair targeting, if actually audited (Table 4, Column 2a, Row 3): ', fairtargeted_rate_if_corrupt_simulated)
print('Ratio over random audits (Table 4, Column 2a, Row 4): ', fairtargeted_rate_if_corrupt_simulated / audit_rate)

table4['3','3'] = fairtargeted_rate_if_corrupt_simulated
table4['3','4'] = fairtargeted_rate_if_corrupt_simulated / audit_rate

# targeted-auditing rate if corrupt, limited to truly audited
fairtargeted_rate_if_corrupt_true_audited = df_party_conditioned[df_party_conditioned['audit_first'] & df_party_conditioned['narrow1_audit_nosample']]['fair_targeted_NS'].mean()

print('Audit rate if corrupt under targeting, if actually audited (Table 4, Column 2b, Row 3): ', fairtargeted_rate_if_corrupt_true_audited)
print('Ratio over random audits (Table 4, Column 2b, Row 4): ', fairtargeted_rate_if_corrupt_true_audited / audit_rate)



# save table4 as csv 
import csv


with open('./output/tables/table_4.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Policy', 'Evaluation Sample', 'Statistics'])

    for key, value in table4.items():
        writer.writerow([key[0], key[1], value])