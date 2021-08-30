#!/usr/bin/env python
# coding: utf-8

# ## Setting: 
# - Filter thresholds: RCT=0.01, Other tags=Optimal F1
# - Included study design(s) for each DERP report: Use column D, "Mapped Tags and Extra Tags", in the Study_design.csv

# In[1]:


import os
import matplotlib
print('matplotlib: {}'.format(matplotlib.__version__))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import glob
import collections
import requests
import lxml.etree
import time
import csv
pd.set_option('display.max_colwidth', 1000)


# ## Set working directory

# In[2]:


os.chdir('PATH TO DIRECTORY')


# ## Integrity checking

# In[3]:


#files = glob.glob('./multitagger_scores/*.csv')
files = glob.glob('./multitagger_scores_2021-08-18/*_v2.csv')

# print(len(files))
# print('\n'.join(files))

files_web_rct_data = glob.glob('./web_rct_tagger_scores_from_API/*_abstract_screened_rct_scores.csv')

files_pubmed_data = glob.glob('./PT_and_MeSH/*_PubMed_data.tsv')

# print(len(files_pubmed_data))
# print('\n'.join(files_pubmed_data))

# In[4]:


problematic = []
for file in files:
    file_name = file.split('/')[-1].strip('.csv')
    df = pd.read_csv(file)
    df = df.loc[df.abs_screened!=1]
    df['DERP'] = file_name
    problematic.append(df[['DERP', 'PMID', 'abs_screened', 'fulltxt_screened', 'included']])
    
problematic = pd.concat(problematic)
print(problematic.shape) # Shape should be (0, 5) if there is no problematic PMIDs


# ## Import included designs file and the optimal F1 file

# In[5]:


# Import the included studies info
design = pd.read_csv('./Study_design3.csv')

# In[6]:


# Import the optimal F1
opti_f1 = pd.read_csv('./MultiTagger_Scorefile_layout_Neil_edits.csv')


# In[7]:


# The threshold df for filtering
threshold = opti_f1[['Column Headers in tsv', 'threshold having optimal F1']][1:].copy()
threshold = threshold.rename(columns={'Column Headers in tsv':'tag', 
                                      'threshold having optimal F1': 'threshold'})
# Set the thresold of RCT tag as 0.01
threshold.loc[threshold.tag =='Randomized Controlled Trial', 'threshold'] = 0.01


# ## Evaluation


results = {}

for file in files:
    #derp_name = file.split('/')[-1].replace('_scores.csv', '')
    derp_name = file.split('/')[-1].replace('_scores_v2.csv', '')
    
    df = pd.read_csv(file)
    
    included_designs = design.loc[design['File Name']==derp_name]['Mapped Tags and Extra Tags'].tolist()
    included_designs = included_designs[0].split(';')
    included_designs_thresholds = threshold.loc[threshold.tag.isin(included_designs)]

    cols = ['PMID', 'abs_screened', 'fulltxt_screened', 'included'] + included_designs
    res_prep = df[cols].copy()
    res_prep['qualified_tags_tagger'] = ''

    for tag_threshold in included_designs_thresholds.values.tolist():
        sd_tag = tag_threshold[0]
        sd_threshold = tag_threshold[1]

        df_remaining = df.loc[df[sd_tag] >= sd_threshold]
        df_remaining_pmids = df_remaining['PMID'].tolist()
        res_prep.loc[res_prep['PMID'].isin(df_remaining_pmids),'qualified_tags_tagger']+='{};'.format(sd_tag)

    res_prep['qualified_tags_tagger'] = res_prep['qualified_tags_tagger'].str.strip(';')
    res_prep['qualified_tags_tagger'] = res_prep['qualified_tags_tagger'].replace('', np.nan)
    
    results[derp_name] = res_prep

# print(len(results))
# print(results.keys())


# In[9]:

# The line below is an example of accessing the result of a DERP -- MS-Drugs-Update-3
#results['MS-Drugs-Update-3']



# ### Descriptive stats tables

# In[10]:


all_design_tags_raw = design['Mapped Tags and Extra Tags'].tolist()
all_design_tags = []
for ct in all_design_tags_raw:
    ct_split = ct.split(';')
    for cts in ct_split:
        all_design_tags.append(cts)

all_design_tags = list(set(all_design_tags))


# In[11]:


cols = ['DERP', 
        'Included designs', '#Included designs',
        'Filtered out (not included papers)', '(%)', 
        'Filtered out (included papers)', '(%)', 
        'Remaining (not included papers)', '(%)', 
        'Remaining (included papers)', '(%)']

df_prep = []

missed = []

for derp_name, df in results.items():
    
    included_design = design.loc[design['File Name'] == derp_name]['Mapped Tags and Extra Tags']
    included_design = included_design.tolist()[0].split(';')

    n_total = df.shape[0]
    TN = df.loc[(df.qualified_tags_tagger.isna())&(df['included'] == 0)]
    FN = df.loc[(df.qualified_tags_tagger.isna())&(df['included'] == 1)]
    
    if FN.shape[0] > 0:
        
        all_desings = all_design_tags
        
        FN_cols_init = FN.columns.tolist()
        
        not_included_designs = []
        for ad in all_desings:
            if ad not in FN_cols_init:
                not_included_designs.append(ad)
        
        FN_cols_init.remove('qualified_tags_tagger')
        FN_append = FN.copy()
        FN_append['included_design'] = ';'.join(included_design)
        FN_append['DERP'] = derp_name
        for not_included in not_included_designs:
            FN_append[not_included] = 'not_in_included_designs'
        FN_cols_final = ['DERP', 'included_design', 'PMID', 
                         'abs_screened', 'fulltxt_screened', 'included'] + all_design_tags
        FN_append = FN_append[FN_cols_final]
        missed.append(FN_append)
    
    FP = df.loc[(~df.qualified_tags_tagger.isna())&(df['included'] == 0)]
    TP = df.loc[(~df.qualified_tags_tagger.isna())&(df['included'] == 1)]
    
    nTN = TN.shape[0]
    perc_TN = round(TN.shape[0]/n_total*100, 2)
    
    nFN = FN.shape[0]
    perc_FN = round(FN.shape[0]/n_total*100, 2)

    nFP = FP.shape[0]
    perc_FP = round(FP.shape[0]/n_total*100, 2)
    
    nTP = TP.shape[0]
    perc_TP = round(TP.shape[0]/n_total*100, 2)
    
    df_prep.append([derp_name, '; '.join(included_design), len(included_design),
                    nTN, perc_TN, nFN, perc_FN, nFP, perc_FP, nTP, perc_TP])
    
    
df_stats = pd.DataFrame(df_prep, columns=cols)


# In[12]:


cols = ['DERP', 
        'Included designs', '#Included designs',
        'Work savings', '(%)', 
        'Remaining (not included papers)', '(%)', 
        'Remaining (included papers)', '(%)', 
        'Recall', 
        '#included papers being filtered out']

df_prep = []

for derp_name, df in results.items():
    
    included_design = design.loc[design['File Name'] == derp_name]['Mapped Tags and Extra Tags']
    included_design = included_design.tolist()[0].split(';')

    n_total = df.shape[0]
    TN = df.loc[(df.qualified_tags_tagger.isna())&(df['included'] == 0)]
    FN = df.loc[(df.qualified_tags_tagger.isna())&(df['included'] == 1)]
    
    FP = df.loc[(~df.qualified_tags_tagger.isna())&(df['included'] == 0)]
    TP = df.loc[(~df.qualified_tags_tagger.isna())&(df['included'] == 1)]
    
    nTN = TN.shape[0]
    perc_TN = round(TN.shape[0]/n_total*100, 2)
    
    nFN = FN.shape[0]
    perc_FN = round(FN.shape[0]/n_total*100, 2)

    nFP = FP.shape[0]
    perc_FP = round(FP.shape[0]/n_total*100, 2)
    
    nTP = TP.shape[0]
    perc_TP = round(TP.shape[0]/n_total*100, 2)
    
    recall = round(nTP/(nTP+nFN), 2)
    
    df_prep.append([derp_name, '; '.join(included_design), len(included_design),
                    nTN+nFN, perc_TN+perc_FN, nFP, perc_FP, nTP, perc_TP, recall, nFN])
    
    
df_stats2 = pd.DataFrame(df_prep, columns=cols)
df_stats2 = df_stats2.sort_values(by='Work savings', ascending=False)
df_stats2.set_index('DERP').to_csv('./interim-results-2021-08-18/cohort-adjusted.02/descriptive_stats_multitagger_only.csv')



# # In[28]:
#
#
# # Import DERP coding
#
# Included_derp_coding = [['DERP', 'PMID', 'DERP_coding']]
#
# coding_files = glob.glob('./Included_PMID_study_design/*.txt')
# for c_file in coding_files:
#     derp_name = c_file.split(' - ')[-1].replace('.txt', '')
#
#     # These two reports don't have coding data
#     if derp_name not in ['Benzodiazepines-Summary-Review', 'Hepatitis-C-Update-2']:
#         with open(c_file, 'r') as fin:
#             for line in fin:
#                 line = line.strip()
#
#                 pmid = line.split(',')[0].replace('\ufeff', '')
#                 coding = line.split(',')[1:]
#                 coding = ';'.join(coding)
#                 Included_derp_coding.append([derp_name, pmid, coding])
#
# Included_derp_coding = pd.DataFrame(Included_derp_coding[1:], columns=Included_derp_coding[0])
#
#
# # In[29]:
#
#
# print(missed_df.shape)
#
#
# # In[30]:
#
#
# print(missed_df_pubmed.shape)
#
#
# # In[31]:
#
#
# missed_out = missed_df[['DERP', 'included_design', 'PMID']].merge(missed_df_pubmed)
# missed_out = missed_out.merge(Included_derp_coding, how='left')
#
# missed_out = missed_out.merge(missed_df[['PMID']+all_design_tags])
#
# print(missed_out.shape)
#
# filtered_out_csv = './interim results-2021-07-13/setting-2/filtered_out_included_studies.tsv'
# missed_out.set_index('DERP').to_csv(filtered_out_csv, sep='\t')




#######
# PART TWO - CALCULATIONS USING MESH AND WEB RCT #
#######


# Identify qualified tags, now including the additional PubMed-qualified items and web RCT tagger-qualified items

results2 = {}
qualified_by_pubmed = []

for file in files:
    derp_name = file.split('/')[-1].replace('_scores_v2.csv', '')

    df_initial = pd.read_csv(file)

    included_designs = design.loc[design['File Name']==derp_name]['Mapped Tags and Extra Tags'].tolist()
    included_designs = included_designs[0].split(';')
    included_designs_thresholds = threshold.loc[threshold.tag.isin(included_designs)]

    df_initial['qualified_tags_tagger'] = ''
    df_initial['qualified_tags_pubmed'] = ''
    df_initial['qualified_tags_web_rct'] = ''
    df_initial['qualified_tags_total'] = ''

    cols = ['PMID', 'abs_screened', 'fulltxt_screened', 'included', 'citation-plus-mesh'] + included_designs + ['Pub_type', 'MeSH', 'qualified_tags_tagger', 'qualified_tags_pubmed', 'qualified_tags_web_rct', 'qualified_tags_total']

    qualified_by_web_rct = []
    no_prediction_rct = []
    # qualified_by_web_rct = []
    for report in files_web_rct_data:
        if derp_name in report:
            df_web = pd.read_csv(report)
            df_web = df_web.rename(columns={'pmid':'PMID'})
    df_initial2 = df_initial.merge(df_web[['PMID', 'citation-plus-mesh']], how = 'left')

    for report in files_pubmed_data:
        if derp_name in report:
            df_pubmed = pd.read_csv(report, sep='\t')

    df = df_initial2.merge(df_pubmed[['PMID', 'Pub_type', 'MeSH']], how = 'left')

    df.loc[(df['Randomized Controlled Trial'].isna())&(df['Case-Control Studies'].isna())&(df['Cohort Studies'].isna())&(df['Prospective Studies'].isna())&(df['Retrospective Studies'].isna()), 'qualified_tags_total'] += 'NoTagMultiTagger'
    if derp_name != 'Benzodiazepines-Summary-Review':
        df.loc[df['citation-plus-mesh'].isna(), 'qualified_tags_total'] += 'NoTagWebRCT'
    df.loc[(df['Randomized Controlled Trial'].isna())&(df['Case-Control Studies'].isna())&(df['Cohort Studies'].isna())&(df['Prospective Studies'].isna())&(df['Retrospective Studies'].isna())&(df['citation-plus-mesh'].isna()), 'qualified_tags_total'] = 'NoTagEitherTagger'
    df.loc[(df['citation-plus-mesh'] >= .01),'qualified_tags_web_rct'] = 'Qualified by web RCT'
    df.loc[(df['citation-plus-mesh'] >= .01),'qualified_tags_total'] += 'Qualified'

    missing_web_rct_count = 0
    missing_multi_count = 0

    for item in df['qualified_tags_total']:
        if 'NoTagWebRCT' in item:
            missing_web_rct_count = missing_web_rct_count + 1
        if 'NoTagMultiTagger' in item:
            missing_multi_count = missing_multi_count + 1
    print(derp_name, ": No predictions from Web RCT, but has predictions from Multi-Tagger:", missing_web_rct_count)
    print(derp_name, ": No predictions from Multi-Tagger, but has predictions from Web RCT:", missing_multi_count)



    #
    # qualified_by_pubmed = []
    #
    # for thing in included_designs:
    #     print(derp_name, thing)

    number = 0

    for row in df_pubmed['Pub_type']:
        row = str(row)
        for item in row.split(';'):
            if item in included_designs:
                qualified_by_pubmed.append(df_pubmed['PMID'][number])
            if 'Randomized Controlled Trial' in included_designs:
                if 'Clinical Trial' in item:
                    qualified_by_pubmed.append(df_pubmed['PMID'][number])
            if 'Clinical Study' in included_designs: #We are using Clinical Study for all observational studies
                if 'Observational Study' in item:
                    qualified_by_pubmed.append(df_pubmed['PMID'][number])
            if 'Meta-analysis' in included_designs:
                if 'Meta-Analysis' in item:
                    qualified_by_pubmed.append(df_pubmed['PMID'][number])
        number = number + 1
    # print(len(qualified_by_pubmed))

    number = 0

    for row in df_pubmed['MeSH']:
        row = str(row)
        for item in row.split(';'):
            if item in included_designs:
                qualified_by_pubmed.append(df_pubmed['PMID'][number])
        number = number + 1
    print(len(qualified_by_pubmed))

    res_prep2 = df[cols].copy()

    if derp_name == 'Benzodiazepines-Summary-Review':
        res_prep2 = res_prep2.drop(columns=['citation-plus-mesh'])
    # res_prep2.loc[(res_prep2['Randomized Controlled Trial'].isna())&(res_prep2['Case-Control Studies'].isna())&(res_prep2['Cohort Studies'].isna())&(res_prep2['Prospective Studies'].isna())&(res_prep2['Retrospective Studies'].isna())&(res_prep2['citation-plus-mesh'].isna()),'qualified_tags_total'] = 'NoTag'

    # qualified_by_web_rct_only = []
    for tag_threshold in included_designs_thresholds.values.tolist():
        sd_tag = tag_threshold[0]
        sd_threshold = tag_threshold[1]

        df_remaining = df.loc[df[sd_tag] >= sd_threshold]
        df_remaining_pmids = df_remaining['PMID'].tolist()

        # for item in qualified_by_web_rct:
        #     if item not in df_remaining_pmids:
        #         if item not in qualified_by_web_rct_only:
        #             qualified_by_web_rct_only.append(item)
        df_total_remaining = df_remaining_pmids + qualified_by_pubmed # ADD ITEMS QUALIFIED BY PUBMED BACK INTO REMAINING (Web RCT are already labeled as qualified)
        df_total_remaining = list(set(df_total_remaining)) # DEDUPLICATE
        res_prep2.loc[res_prep2['PMID'].isin(df_remaining_pmids),'qualified_tags_tagger']+='{};'.format(sd_tag)
        res_prep2.loc[res_prep2['PMID'].isin(df_total_remaining),'qualified_tags_total']='{};'.format('Qualified')
        res_prep2.loc[res_prep2['PMID'].isin(qualified_by_pubmed),'qualified_tags_pubmed']='{};'.format('Qualified by PubMed')
        res_prep2.loc[res_prep2['PMID'].isin(qualified_by_web_rct),'qualified_tags_web_rct']='{};'.format('Qualified by web RCT Tagger')

        # res_prep2.loc[res_prep2['PMID'].isin(qualified_by_pubmed),'qualified_tags_pubmed']+='{};'.format(1)

    res_prep2['qualified_tags_tagger'] = res_prep2['qualified_tags_tagger'].str.strip(';')
    res_prep2['qualified_tags_tagger'] = res_prep2['qualified_tags_tagger'].replace('', np.nan)
    res_prep2['qualified_tags_pubmed'] = res_prep2['qualified_tags_pubmed'].str.strip(';')
    res_prep2['qualified_tags_pubmed'] = res_prep2['qualified_tags_pubmed'].replace('', np.nan)
    res_prep2['qualified_tags_total'] = res_prep2['qualified_tags_total'].str.strip(';')
    res_prep2['qualified_tags_total'] = res_prep2['qualified_tags_total'].replace('', np.nan)
    res_prep2['qualified_tags_web_rct'] = res_prep2['qualified_tags_web_rct'].str.strip(';')
    res_prep2['qualified_tags_web_rct'] = res_prep2['qualified_tags_web_rct'].replace('', np.nan)

    results2[derp_name] = res_prep2

# print("Number qualified by web RCT Tagger, but not Multi-Tagger:", len(qualified_by_web_rct_only))
# print(len(results))
# print(results.keys())



# In[9]:

# The line below is an example of accessing the result of a DERP -- MS-Drugs-Update-3
#results['MS-Drugs-Update-3']

for derp_name, df in results2.items():
    save_to = 'interim-results-2021-08-18/cohort-adjusted.02/{}_results.csv'.format(derp_name)
    df.set_index('PMID').to_csv(save_to)
    # print(df.columns)


# Identify qualified tags from PT and MeSH

# results_pubmed_data = {}
#
# for file in files_pubmed_data:
#     derp_name = file.split('/')[-1].replace('_PubMed_data.tsv', '')
#
#     df = pd.read_csv(file)
#
#     included_designs = design.loc[design['File Name']==derp_name]['Mapped Tags and Extra Tags'].tolist()
#
#     cols = ['PMID', 'abs_screened', 'fulltxt_screened', 'included'] + included_designs
#     res_prep = df[cols].copy()
#     res_prep['qualified_tags_pubmed'] = ''
#
#     number = 0
#
#     for design_name in file['pub_type'][number]:
#         if design_name in included_designs:
#             file['qualified_tags_pubmed'].append(design_name)
#         number = number +1
#
#
#         # df_remaining = df.loc[df[sd_tag] >= sd_threshold] # CHECKING WHICH IDs ARE ABOVE THRESHOLDS
#         # df_remaining_pmids = df_remaining['PMID'].tolist()
#         # res_prep.loc[res_prep['PMID'].isin(df_remaining_pmids),'qualified_tags_pubmed']+='{};'.format(sd_tag)
#
#     res_prep['qualified_tags_pubmed'] = res_prep['qualified_tags_pubmed'].str.strip(';')
#     res_prep['qualified_tags_pubmed'] = res_prep['qualified_tags_pubmed'].replace('', np.nan)
#
#     results_pubmed_data[derp_name] = res_prep
#
# print(len(results_pubmed_data))
# print(results_pubmed_data['qualified_tags_pubmed'])






# ### Descriptive stats table 3



# all_design_tags_raw = design['Mapped Tags and Extra Tags'].tolist()
# all_design_tags = []
# for ct in all_design_tags_raw:
#     ct_split = ct.split(';')
#     for cts in ct_split:
#         all_design_tags.append(cts)
#
# all_design_tags = list(set(all_design_tags))


# In[11]:


cols = ['DERP',
        'Included designs', '#Included designs',
        'Filtered out (not included papers)', '(%)',
        'Filtered out (included papers)', '(%)',
        'Remaining (not included papers)', '(%)',
        'Remaining (included papers)', '(%)']

df_prep = []

missed = []

for derp_name, df in results2.items():

    included_design = design.loc[design['File Name'] == derp_name]['Mapped Tags and Extra Tags']
    included_design = included_design.tolist()[0].split(';')

    n_total = df.shape[0]
    TN = df.loc[(df.qualified_tags_total.isna())&(df['included'] == 0)]
    FN = df.loc[(df.qualified_tags_total.isna())&(df['included'] == 1)]

    if FN.shape[0] > 0:

        all_desings = all_design_tags

        FN_cols_init = FN.columns.tolist()

        not_included_designs = []
        for ad in all_desings:
            if ad not in FN_cols_init:
                not_included_designs.append(ad)

        FN_cols_init.remove('qualified_tags_total')
        FN_append = FN.copy()
        FN_append['included_design'] = ';'.join(included_design)
        FN_append['DERP'] = derp_name
        for not_included in not_included_designs:
            FN_append[not_included] = 'not_in_included_designs'
        FN_cols_final = ['DERP', 'included_design', 'PMID',
                         'abs_screened', 'fulltxt_screened', 'included'] + all_design_tags
        FN_append = FN_append[FN_cols_final]
        missed.append(FN_append)

    FP = df.loc[(~df.qualified_tags_total.isna())&(df['included'] == 0)]
    TP = df.loc[(~df.qualified_tags_total.isna())&(df['included'] == 1)]

    nTN = TN.shape[0]
    perc_TN = round(TN.shape[0]/n_total*100, 2)

    nFN = FN.shape[0]
    perc_FN = round(FN.shape[0]/n_total*100, 2)

    nFP = FP.shape[0]
    perc_FP = round(FP.shape[0]/n_total*100, 2)

    nTP = TP.shape[0]
    perc_TP = round(TP.shape[0]/n_total*100, 2)

    df_prep.append([derp_name, '; '.join(included_design), len(included_design),
                    nTN, perc_TN, nFN, perc_FN, nFP, perc_FP, nTP, perc_TP])


df_stats3 = pd.DataFrame(df_prep, columns=cols)



# ### Descriptive stats table 3



# all_design_tags_raw = design['Mapped Tags and Extra Tags'].tolist()
# all_design_tags = []
# for ct in all_design_tags_raw:
#     ct_split = ct.split(';')
#     for cts in ct_split:
#         all_design_tags.append(cts)
#
# all_design_tags = list(set(all_design_tags))


# In[11]:


cols = ['DERP Report',
        '# in initial retrieval set',
        '# filtered out by our strategy', '% work savings',
        '# of finally included articles', '# of finally included articles removed by our strategy',
        '% recall']

df_prep = []

missed = []

for derp_name, df in results2.items():

    included_design = design.loc[design['File Name'] == derp_name]['Mapped Tags and Extra Tags']
    included_design = included_design.tolist()[0].split(';')

    n_total = df.shape[0]
    TN = df.loc[(df.qualified_tags_total.isna())&(df['included'] == 0)]
    FN = df.loc[(df.qualified_tags_total.isna())&(df['included'] == 1)]
    num_included = len(df['PMID'].loc[(df['included'] == 1)])

    if FN.shape[0] > 0:

        all_desings = all_design_tags

        FN_cols_init = FN.columns.tolist()

        not_included_designs = []
        for ad in all_desings:
            if ad not in FN_cols_init:
                not_included_designs.append(ad)

        FN_cols_init.remove('qualified_tags_total')
        FN_append = FN.copy()
        FN_append['included_design'] = ';'.join(included_design)
        FN_append['DERP'] = derp_name
        for not_included in not_included_designs:
            FN_append[not_included] = 'not_in_included_designs'
        FN_cols_final = ['DERP', 'included_design', 'PMID',
                         'abs_screened', 'fulltxt_screened', 'included'] + all_design_tags
        FN_append = FN_append[FN_cols_final]
        missed.append(FN_append)

    FP = df.loc[(~df.qualified_tags_total.isna())&(df['included'] == 0)]
    TP = df.loc[(~df.qualified_tags_total.isna())&(df['included'] == 1)]

    nTN = TN.shape[0]
    perc_TN = round(TN.shape[0]/n_total*100, 2)

    nFN = FN.shape[0]
    perc_FN = round(FN.shape[0]/n_total*100, 2)

    nFP = FP.shape[0]
    perc_FP = round(FP.shape[0]/n_total*100, 2)

    nTP = TP.shape[0]
    perc_TP = round(TP.shape[0]/n_total*100, 2)

    percrecall = round((1 - (nFN/num_included))*100, 2)
    numworksavings = nTN + nFN
    percworksavings = round(numworksavings/n_total*100, 2)
    # df_prep.append([derp_name, '; '.join(included_design), len(included_design),
    #                 nTN, perc_TN, nFN, perc_FN, nFP, perc_FP, nTP, perc_TP])
    df_prep.append([derp_name, n_total, numworksavings, percworksavings, num_included, nFN, percrecall])

df_stats4 = pd.DataFrame(df_prep, columns=cols)
df_stats4 = df_stats4.sort_values(by='DERP Report', ascending=True)
df_stats4.set_index('DERP Report').to_csv('./interim-results-2021-08-18/cohort-adjusted.02/descriptive_stats_3_data_sources_v2.csv')


# The included articles filtered out by the thresholds
missed_df = pd.concat(missed)
print(missed_df.shape)
missed_df['PMID'] = missed_df['PMID'].astype(str)

#missed_df.set_index('DERP').to_csv('./Results/setting-2/filtered_out_included_studies_TagScores.tsv', sep='\t')

terms = ['case-control study', 'case control study', 'case-control studies', 'case control studies',
         'cohort study', 'cohort studies',
         'cross-sectional study', 'cross sectional study', 'cross-sectional studies', 'cross sectional studies',
         'randomized controlled trial', 'randomized controlled trials',
         'systematic review', 'systematic reviews',
         'clinical studies', 'clinical study',
         'observational study', 'observational studies', 'observation study', 'observation studies',
         'retrospective study', 'retrospective studies',
         'prospective study', 'prospective studies',
         'meta-analysis', 'meta analysis', 'meta-analyses', 'meta analyses']



#Pull PubMed data for filtered out items

missed_df_pubmed = [['PMID', 'pub_type', 'MeSH', 'title', 'abstract',
                     'study_design_info']]

# terms = ['case-control study', 'case control study', 'case-control studies', 'case control studies',
#          'cohort study', 'cohort studies',
#          'cross-sectional study', 'cross sectional study', 'cross-sectional studies', 'cross sectional studies',
#          'randomized controlled trial', 'randomized controlled trials',
#          'systematic review', 'systematic reviews',
#          'clinical studies', 'clinical study',
#          'observational study', 'observational studies', 'observation study', 'observation studies',
#          'retrospective study', 'retrospective studies',
#          'prospective study', 'prospective studies',
#          'meta-analysis', 'meta analysis', 'meta-analyses', 'meta analyses']

pmids = missed_df.PMID.tolist()
pmids = ','.join([str(pmid) for pmid in pmids])

api_link = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}&retmode=xml".format(pmids)

response = requests.get(api_link)
tree = lxml.etree.fromstring(response.text)

pubs = tree.xpath('.//PubmedArticle')
print(len(pubs))

for pub in pubs:

    study_design = []
    identified_from = []

    pmid = pub.xpath('./MedlineCitation/PMID')[0].text
    pmid_node = pub.xpath('./MedlineCitation/PMID')
    if len(pmid_node) > 1:
        print(pmid, 'More than one PMID node, CHECK!')

    pt = []
    pt_nodes = pub.xpath('.//PublicationTypeList/descendant::text()')
    for pt_txt in pt_nodes:
        pt_txt = pt_txt.strip()
        if len(pt_txt) > 0 and pt_txt not in pt:
            pt.append(pt_txt)

            if pt_txt.lower() in terms:

                if pt_txt.lower().startswith('case'):
                    unified_term = 'Case-Control Studies'
                elif pt_txt.lower().startswith('cohort'):
                    unified_term = 'Cohort Studies'
                elif pt_txt.lower().startswith('cross'):
                    unified_term = 'Cross-Sectional Studies'
                elif pt_txt.lower().startswith('randomized'):
                    unified_term = 'Randomized Controlled Trial'
                elif pt_txt.lower().startswith('systematic'):
                    unified_term = 'Systematic Review'
                elif pt_txt.lower().startswith('clinical'):
                    unified_term = 'Clinical Studies'
                elif pt_txt.lower().startswith('observation'):
                    unified_term = 'Observational Studies'
                elif pt_txt.lower().startswith('retrospective'):
                    unified_term = 'Retrospective Studies'
                elif pt_txt.lower().startswith('prospective'):
                    unified_term = 'Prospective Studies'
                elif pt_txt.lower().startswith('meta'):
                    unified_term = 'Meta-analysis'

                identified_from.append('{} in PT'.format(unified_term))
                # study_design.append(unified_term)

    mesh = []
    mesh_nodes = pub.xpath('.//MeshHeading/descendant::text()')
    for mesh_txt in mesh_nodes:
        mesh_txt = mesh_txt.strip()
        if len(mesh_txt) > 0 and mesh_txt not in mesh:
            mesh.append(mesh_txt)

            if mesh_txt.lower() in terms:

                if mesh_txt.lower().startswith('case'):
                    unified_term = 'Case-Control Studies'
                elif mesh_txt.lower().startswith('cohort'):
                    unified_term = 'Cohort Studies'
                elif mesh_txt.lower().startswith('cross'):
                    unified_term = 'Cross-Sectional Studies'
                elif mesh_txt.lower().startswith('randomized'):
                    unified_term = 'Randomized Controlled Trial'
                elif mesh_txt.lower().startswith('systematic'):
                    unified_term = 'Systematic Review'
                elif mesh_txt.lower().startswith('clinical'):
                    unified_term = 'Clinical Studies'
                elif mesh_txt.lower().startswith('observation'):
                    unified_term = 'Observational Studies'
                elif mesh_txt.lower().startswith('retrospective'):
                    unified_term = 'Retrospective Studies'
                elif mesh_txt.lower().startswith('prospective'):
                    unified_term = 'Prospective Studies'
                elif mesh_txt.lower().startswith('meta'):
                    unified_term = 'Meta-analysis'

                identified_from.append('{} in MeSH'.format(mesh_txt))
                # study_design.append(unified_term)

    title_node = pub.xpath('./MedlineCitation/Article/ArticleTitle/descendant::text()')
    title = ' '.join(title_node)

    for term in terms:
        if term in title.lower():
            if term.startswith('case'):
                unified_term = 'Case-Control Studies'
            elif term.startswith('cohort'):
                unified_term = 'Cohort Studies'
            elif term.startswith('cross'):
                unified_term = 'Cross-Sectional Studies'
            elif term.startswith('randomized'):
                unified_term = 'Randomized Controlled Trial'
            elif term.startswith('systematic'):
                unified_term = 'Systematic Review'
            elif term.startswith('clinical'):
                unified_term = 'Clinical Studies'
            elif term.startswith('observation'):
                unified_term = 'Observational Studies'
            elif term.startswith('retrospective'):
                unified_term = 'Retrospective Studies'
            elif term.startswith('prospective'):
                unified_term = 'Prospective Studies'
            elif term.startswith('meta'):
                unified_term = 'Meta-analysis'

            identified_from.append('{} in Title'.format(unified_term))

    abstract_node = pub.xpath('./MedlineCitation/Article/Abstract/AbstractText/descendant::text()')
    abstract = ' '.join(abstract_node)

    for term in terms:
        if term in abstract.lower():
            if term.startswith('case'):
                unified_term = 'Case-Control Studies'
            elif term.startswith('cohort'):
                unified_term = 'Cohort Studies'
            elif term.startswith('cross'):
                unified_term = 'Cross-Sectional Studies'
            elif term.startswith('randomized'):
                unified_term = 'Randomized Controlled Trial'
            elif term.startswith('systematic'):
                unified_term = 'Systematic Review'
            elif term.startswith('clinical'):
                unified_term = 'Clinical Studies'
            elif term.startswith('observation'):
                unified_term = 'Observational Studies'
            elif term.startswith('retrospective'):
                unified_term = 'Retrospective Studies'
            elif term.startswith('prospective'):
                unified_term = 'Prospective Studies'
            elif term.startswith('meta'):
                unified_term = 'Meta-analysis'

            identified_from.append('{} in Abstract'.format(unified_term))

    identified_from = ';'.join(list(set(identified_from)))
    # study_design = ';'.join(list(set(study_design)))

    missed_df_pubmed.append([pmid, ';'.join(pt), ';'.join(mesh), title, abstract, identified_from])

missed_df_pubmed = pd.DataFrame(missed_df_pubmed[1:], columns=missed_df_pubmed[0])
missed_df_pubmed = missed_df_pubmed.replace('', np.nan)


# In[28]:


# Import DERP coding

Included_derp_coding = [['DERP', 'PMID', 'DERP_coding']]

coding_files = glob.glob('./Included_PMID_study_design/*.txt')
for c_file in coding_files:
    derp_name = c_file.split(' - ')[-1].replace('.txt', '')

    # These two reports don't have coding data
    if derp_name not in ['Benzodiazepines-Summary-Review', 'Hepatitis-C-Update-2']:
        with open(c_file, 'r') as fin:
            for line in fin:
                line = line.strip()

                pmid = line.split(',')[0].replace('\ufeff', '')
                coding = line.split(',')[1:]
                coding = ';'.join(coding)
                Included_derp_coding.append([derp_name, pmid, coding])

Included_derp_coding = pd.DataFrame(Included_derp_coding[1:], columns=Included_derp_coding[0])


# In[29]:


print(missed_df.shape)


# In[30]:


print(missed_df_pubmed.shape)


# In[31]:


missed_out = missed_df[['DERP', 'included_design', 'PMID']].merge(missed_df_pubmed)
missed_out = missed_out.merge(Included_derp_coding, how='left')

missed_out = missed_out.merge(missed_df[['PMID']+all_design_tags])

print(missed_out.shape)

filtered_out_csv = './interim-results-2021-08-18/cohort-adjusted.02/filtered_out_included_studies.tsv'
missed_out.set_index('DERP').to_csv(filtered_out_csv, sep='\t')



# In[12]:


# cols = ['DERP',
#         'Included designs', '#Included designs',
#         'Work savings', '(%)',
#         'Remaining (not included papers)', '(%)',
#         'Remaining (included papers)', '(%)',
#         'Recall',
#         '#included papers being filtered out']
#
# df_prep = []
#
# for derp_name, df in results2.items():
#
#     included_design = design.loc[design['File Name'] == derp_name]['Mapped Tags and Extra Tags']
#     included_design = included_design.tolist()[0].split(';')
#
#     n_total = df.shape[0]
#     TN = df.loc[(df.qualified_tags_total.isna())&(df['included'] == 0)]
#     FN = df.loc[(df.qualified_tags_total.isna())&(df['included'] == 1)]
#
#     FP = df.loc[(~df.qualified_tags_total.isna())&(df['included'] == 0)]
#     TP = df.loc[(~df.qualified_tags_total.isna())&(df['included'] == 1)]
#
#     nTN = TN.shape[0]
#     perc_TN = round(TN.shape[0]/n_total*100, 2)
#
#     nFN = FN.shape[0]
#     perc_FN = round(FN.shape[0]/n_total*100, 2)
#
#     nFP = FP.shape[0]
#     perc_FP = round(FP.shape[0]/n_total*100, 2)
#
#     nTP = TP.shape[0]
#     perc_TP = round(TP.shape[0]/n_total*100, 2)
#
#     recall = round(nTP/(nTP+nFN), 2)
#
#     df_prep.append([derp_name, '; '.join(included_design), len(included_design),
#                     nTN+nFN, perc_TN+perc_FN, nFP, perc_FP, nTP, perc_TP, recall, nFN])
#
#
# df_stats3 = pd.DataFrame(df_prep, columns=cols)
# df_stats3 = df_stats3.sort_values(by='Work savings', ascending=False)
# df_stats3.set_index('DERP').to_csv('./interim results-2021-08-12/descriptive_stats_3_data_sources.csv')




# ## Abstract screened plot (by number); Threshold: Optimal F1 (0.01 for RCT)

# In[13]:


# Preparing data for plotting

cols = ['DERP',
        'Work savings',
        'Remaining (not included papers)',
        'Remaining (included papers)',
        'Filtered out included papers']

df_prep = []

for derp_name, df in results2.items():

    included_design = design.loc[design['File Name'] == derp_name]['Mapped Tags and Extra Tags']
    included_design = included_design.tolist()[0].split(';')

    n_total = df.shape[0]

    TN = df.loc[(df.qualified_tags_total.isna())&(df['included'] == 0)]
    FN = df.loc[(df.qualified_tags_total.isna())&(df['included'] == 1)]

    FP = df.loc[(~df.qualified_tags_total.isna())&(df['included'] == 0)]
    TP = df.loc[(~df.qualified_tags_total.isna())&(df['included'] == 1)]

    nTN = TN.shape[0]
    nFN = FN.shape[0]
    nTNFN = (nTN+nFN)

    nFP = FP.shape[0]
    nTP = TP.shape[0]

    df_prep.append([derp_name, nTNFN, nFP, nTP, nFN])


df_draw = pd.DataFrame(df_prep, columns=cols)
df_draw = df_draw.sort_values(by=['Work savings'], ascending=False)
df_draw = df_draw.set_index('DERP')


# In[14]:


# Preparing data for plotting (continued)

for_merge = design[['File Name', 'Mapped Tags and Extra Tags']].copy()
for_merge = for_merge.rename(columns={'File Name':'DERP',
                                      'Mapped Tags and Extra Tags':'Included Study Designs'})
for_merge = for_merge.set_index('DERP')
df_draw = df_draw.join(for_merge)


# In[15]:


fields = ['Work savings',
          'Remaining (not included papers)',
          'Remaining (included papers)']
fields.reverse()

colors = ['#1D2F6F', '#FAC748', '#900C3F']

df_draw = df_draw.sort_values(by=['Work savings', 'Remaining (not included papers)'], ascending=True)

# figure and axis
fig, ax = plt.subplots(1, figsize=(18, 10))

# plot bars
left = len(df_draw) * [0]
for idx, name in enumerate(fields):
    ax.barh(df_draw.index, df_draw[name], left = left, color=colors[idx])
    left = left + df_draw[name]

    n_loss = df_draw['Filtered out included papers'].tolist()

    if idx == 2:
        lefts = left.tolist()
        y_ticks = ax.get_yticks()
        w_savings = df_draw['Work savings'].tolist()
        for x_val, y_val, loss_val, w_saving in zip(lefts, y_ticks, n_loss, w_savings):
            ax.text(x=x_val+8, y=y_val-0.3, s='#Included papers being filtered out={}'.format(loss_val), fontsize=12)
            ax.text(x=x_val+8, y=y_val, s='#Work savings={}'.format(w_saving), fontsize=12)

# title, legend, labels
ax.set_title('Work saved\n(# of abstract screened items)', loc='left', size=20, weight='bold')
ax.legend(fields, bbox_to_anchor=([0.42, 1, 0, 0]), ncol=1, frameon=False, fontsize=12)
ax.set_xlabel('Number of papers', size=12)

# study design abbreviations
derps_included_designs = df_draw['Included Study Designs'].tolist()

derps_included_designs_abbr = []
for each_derp in derps_included_designs:
    included_desings_abbr = []
    for sd in each_derp.split(';'):
        abbr = ''
        if sd == 'Randomized Controlled Trial':
            abbr = 'RCT'
        elif sd == 'Systematic Review':
            abbr = 'SR'
        elif sd == 'Case-Control Studies':
            abbr = 'CCS'
        elif sd == "Cohort Studies":
            abbr = 'CS'
        elif sd == 'Cross-Sectional Studies':
            abbr = 'CSS'
        elif sd == 'Prospective Studies':
            abbr = 'PS'
        elif sd == 'Retrospective Studies':
            abbr = 'RS'
        elif sd == 'Meta-analysis':
            abbr = 'MA'

        included_desings_abbr.append(abbr)
    included_desings_abbr = ', '.join(included_desings_abbr)
    derps_included_designs_abbr.append(included_desings_abbr)


# reset y labels
ori_y_lbl = df_draw.index.tolist()
new_y_lbl = []

for ylbl, sd_abbr in zip(ori_y_lbl, derps_included_designs_abbr):
    new_lbl = '{}\n({})'.format(ylbl, sd_abbr)
    new_y_lbl.append(new_lbl)

ax.set_yticks(ax.get_yticks())
ax.set_yticklabels(labels=new_y_lbl, fontsize=12)

# Add text box
props = dict(boxstyle='Square', facecolor='wheat', alpha=0)
textstr = '{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}'.format('RCT = Randomized Controlled Trials',
                                                  'SR = Systematic Reviews',
                                                  'MA = Meta-analysis',
                                                  'CCS = Case-Control Studies',
                                                  'CS = Cohort Studies',
                                                  'CSS = Cross-Sectional Studies',
                                                  'PS = Prospective Studies',
                                                  'RS = Retrospective Studies')

ax.text(0.75, 1, textstr, transform=ax.transAxes, fontsize=12,
        verticalalignment='bottom', bbox=props)

# remove spines
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)

# adjust limits and draw grid lines
ax.set_ylim(-0.5, ax.get_yticks()[-1] + 0.5)
ax.set_axisbelow(True)
ax.xaxis.grid(color='gray', linestyle='dashed')

plt.gcf().subplots_adjust(left=0.23, right=0.82, top=0.8)
plt.savefig('./interim-results-2021-08-18/cohort-adjusted.02/abs_screened_work_savings_by_number.png', dpi=600,
            facecolor='white', transparent=False)
# plt.show()

# Code reference: https://towardsdatascience.com/stacked-bar-charts-with-pythons-matplotlib-f4020e4eb4a7


# ## Abstract screened plot (by percentage); Threshold: Optimal F1 (0.01 for RCT)

# In[16]:


# Preparing data for plotting

cols = ['DERP',
        'Work savings',
        "Remaining (not included papers)",
        "Reamining (included papers)",
        "Filtered out included papers",
        'recall']

df_prep = []

for derp_name, df in results2.items():

    included_design = design.loc[design['File Name'] == derp_name]['Mapped Tags and Extra Tags']
    included_design = included_design.tolist()[0].split(';')

    n_total = df.shape[0]
    TN = df.loc[(df.qualified_tags_total.isna())&(df['included'] == 0)]
    FN = df.loc[(df.qualified_tags_total.isna())&(df['included'] == 1)]

    FP = df.loc[(~df.qualified_tags_total.isna())&(df['included'] == 0)]
    TP = df.loc[(~df.qualified_tags_total.isna())&(df['included'] == 1)]

    nTN = TN.shape[0]
    nFN = FN.shape[0]
    nTNFN = (nTN+nFN)/n_total*100

    nFP = FP.shape[0]/n_total*100
    nTP = TP.shape[0]/n_total*100

    recall = round(TP.shape[0]/(TP.shape[0]+nFN), 2)

    df_prep.append([derp_name, nTNFN, nFP, nTP, nFN, recall])

df_draw_perc = pd.DataFrame(df_prep, columns=cols).round(2)
df_draw_perc = df_draw_perc.sort_values(by=['Work savings'], ascending=False)
df_draw_perc = df_draw_perc.set_index('DERP')


# In[17]:


# Preparing data for plotting (continued)

for_merge = design[['File Name', 'Mapped Tags and Extra Tags']].copy()
for_merge = for_merge.rename(columns={'File Name':'DERP',
                                      'Mapped Tags and Extra Tags':'Included Study Designs'})
for_merge = for_merge.set_index('DERP')
df_draw_perc = df_draw_perc.join(for_merge)


# In[18]:


fields = ['Work savings',
          "Remaining (not included papers)",
          "Reamining (included papers)"]
fields.reverse()

colors = ['#1D2F6F', '#FAC748', '#900C3F']

df_draw_perc = df_draw_perc.sort_values(by=['Work savings', 'Remaining (not included papers)'],
                                        ascending=True)

# figure and axis
fig, ax = plt.subplots(1, figsize=(18, 10))

# plot bars
left = len(df_draw_perc) * [0]
for idx, name in enumerate(fields):
    ax.barh(df_draw_perc.index, df_draw_perc[name], height=0.7,
            left = left, color=colors[idx])
    left = left + df_draw_perc[name]

loss_recall_list = df_draw_perc[['Filtered out included papers', 'recall']].values.tolist()
for i, perc_work_saved in enumerate(df_draw_perc['Work savings'].tolist()):
    loss_val = int(loss_recall_list[i][0])
    recall = loss_recall_list[i][1]
    if loss_val <= 1:
        ax.text(x=101, y=i,
                s='{}% work saved;\nFiltered out {} included paper;\nRecall={}'.format(perc_work_saved,
                                                                                       loss_val,
                                                                                       recall),
                ha='left', va='center', rotation=0)

    elif loss_val > 1:
        ax.text(x=101, y=i,
                s='{}% work saved;\nFiltered out {} included papers;\nRecall={}'.format(perc_work_saved,
                                                                                        loss_val,
                                                                                        recall),
                ha='left', va='center', rotation=0)

# title, legend, labels
ax.set_title('Work saved\n(% of abstract screened items)', loc='left', size=20, weight='bold')
ax.legend(fields, bbox_to_anchor=([0.42, 1, 0, 0]), ncol=1, frameon=False, fontsize=12)
ax.set_xlabel('%', fontsize=14)

# study design abbriviations
derps_included_designs = df_draw_perc['Included Study Designs'].tolist()

derps_included_designs_abbr = []
for each_derp in derps_included_designs:
    included_desings_abbr = []
    for sd in each_derp.split(';'):
        abbr = ''
        if sd == 'Randomized Controlled Trial':
            abbr = 'RCT'
        elif sd == 'Systematic Review':
            abbr = 'SR'
        elif sd == 'Case-Control Studies':
            abbr = 'CCS'
        elif sd == "Cohort Studies":
            abbr = 'CS'
        elif sd == 'Cross-Sectional Studies':
            abbr = 'CSS'
        elif sd == 'Prospective Studies':
            abbr = 'PS'
        elif sd == 'Retrospective Studies':
            abbr = 'RS'
        elif sd == 'Meta-analysis':
            abbr = 'MA'

        included_desings_abbr.append(abbr)
    included_desings_abbr = ', '.join(included_desings_abbr)
    derps_included_designs_abbr.append(included_desings_abbr)

# reset y labels
ori_y_lbl = df_draw_perc.index.tolist()
new_y_lbl = []

for ylbl, sd_abbr in zip(ori_y_lbl, derps_included_designs_abbr):
    new_lbl = '{}\n({})'.format(ylbl, sd_abbr)
    new_y_lbl.append(new_lbl)

ax.set_yticks(ax.get_yticks())
ax.set_yticklabels(labels=new_y_lbl, fontsize=12)

# Add text box
props = dict(boxstyle='Square', facecolor='wheat', alpha=0)
textstr = '{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}'.format('RCT = Randomized Controlled Trials',
                                                  'SR = Systematic Reviews',
                                                  'MA = Meta-analysis',
                                                  'CCS = Case-Control Studies',
                                                  'CS = Cohort Studies',
                                                  'CSS = Cross-Sectional Studies',
                                                  'PS = Prospective Studies',
                                                  'RS = Retrospective Studies')

ax.text(0.75, 1, textstr, transform=ax.transAxes, fontsize=12,
        verticalalignment='bottom', bbox=props)


# remove spines
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
# adjust limits and draw grid lines
ax.set_ylim(-0.5, ax.get_yticks()[-1] + 0.5)
ax.set_axisbelow(True)
ax.xaxis.grid(color='gray', linestyle='dashed')

plt.gcf().subplots_adjust(left=0.25, right=0.9, top=0.8)
plt.savefig('./interim-results-2021-08-18/cohort-adjusted.02/abs_screened_work_savings_by_percentage.png', dpi=600,
            facecolor='white', transparent=False)
# plt.show()

# Code reference: https://towardsdatascience.com/stacked-bar-charts-with-pythons-matplotlib-f4020e4eb4a7


# ## Full-text screened plot (by number); Threshold: Optimal F1 (0.01 for RCT)

# In[19]:


# Preparing data for plotting

cols = ['DERP',
        'Work savings',
        'Remaining (not included papers)',
        'Remaining (included papers)',
        'Filtered out included papers']

df_prep = []

for derp_name, df in results2.items():

    df = df.loc[df.fulltxt_screened==1].copy()

    included_design = design.loc[design['File Name'] == derp_name]['Mapped Tags and Extra Tags']
    included_design = included_design.tolist()[0].split(';')

    n_total = df.shape[0]
    TN = df.loc[(df.qualified_tags_total.isna())&(df['included'] == 0)]
    FN = df.loc[(df.qualified_tags_total.isna())&(df['included'] == 1)]

    FP = df.loc[(~df.qualified_tags_total.isna())&(df['included'] == 0)]
    TP = df.loc[(~df.qualified_tags_total.isna())&(df['included'] == 1)]

    nTN = TN.shape[0]
    nFN = FN.shape[0]
    nTNFN = (nTN+nFN)

    nFP = FP.shape[0]
    nTP = TP.shape[0]

    df_prep.append([derp_name, nTNFN, nFP, nTP, nFN])


df_draw = pd.DataFrame(df_prep, columns=cols)
df_draw = df_draw.sort_values(by=['Work savings'], ascending=False)
df_draw = df_draw.set_index('DERP')


# In[20]:


# Preparing data for plotting (continued)

for_merge = design[['File Name', 'Mapped Tags and Extra Tags']].copy()
for_merge = for_merge.rename(columns={'File Name':'DERP',
                                      'Mapped Tags and Extra Tags':'Included Study Designs'})
for_merge = for_merge.set_index('DERP')
df_draw = df_draw.join(for_merge)


# In[21]:


fields = ['Work savings',
          'Remaining (not included papers)',
          'Remaining (included papers)']
fields.reverse()

colors = ['#1D2F6F', '#FAC748', '#900C3F']

df_draw = df_draw.sort_values(by=['Work savings', 'Remaining (not included papers)'], ascending=True)

# figure and axis
fig, ax = plt.subplots(1, figsize=(18, 10))

# plot bars
left = len(df_draw) * [0]
for idx, name in enumerate(fields):
    ax.barh(df_draw.index, df_draw[name], left = left, color=colors[idx])
    left = left + df_draw[name]

    n_loss = df_draw['Filtered out included papers'].tolist()

    if idx == 2:
        lefts = left.tolist()
        y_ticks = ax.get_yticks()
        w_savings = df_draw['Work savings'].tolist()
        for x_val, y_val, loss_val, w_saving in zip(lefts, y_ticks, n_loss, w_savings):
            ax.text(x=x_val+8, y=y_val-0.3, s='#Included papers being filtered out={}'.format(loss_val), fontsize=12)
            ax.text(x=x_val+8, y=y_val, s='#Work savings={}'.format(w_saving), fontsize=12)

# title, legend, labels
ax.set_title('Work saved\n(# of full-text screened items)', loc='left', size=20, weight='bold')
ax.legend(fields, bbox_to_anchor=([0.42, 1, 0, 0]), ncol=1, frameon=False, fontsize=12)
ax.set_xlabel('Number of papers', size=12)

# study design abbreviations
derps_included_designs = df_draw['Included Study Designs'].tolist()

derps_included_designs_abbr = []
for each_derp in derps_included_designs:
    included_desings_abbr = []
    for sd in each_derp.split(';'):
        abbr = ''
        if sd == 'Randomized Controlled Trial':
            abbr = 'RCT'
        elif sd == 'Systematic Review':
            abbr = 'SR'
        elif sd == 'Case-Control Studies':
            abbr = 'CCS'
        elif sd == "Cohort Studies":
            abbr = 'CS'
        elif sd == 'Cross-Sectional Studies':
            abbr = 'CSS'
        elif sd == 'Prospective Studies':
            abbr = 'PS'
        elif sd == 'Retrospective Studies':
            abbr = 'RS'
        elif sd == 'Meta-analysis':
            abbr = 'MA'

        included_desings_abbr.append(abbr)
    included_desings_abbr = ', '.join(included_desings_abbr)
    derps_included_designs_abbr.append(included_desings_abbr)


# reset y labels
ori_y_lbl = df_draw.index.tolist()
new_y_lbl = []

for ylbl, sd_abbr in zip(ori_y_lbl, derps_included_designs_abbr):
    new_lbl = '{}\n({})'.format(ylbl, sd_abbr)
    new_y_lbl.append(new_lbl)

ax.set_yticks(ax.get_yticks())
ax.set_yticklabels(labels=new_y_lbl, fontsize=12)

# Add text box
props = dict(boxstyle='Square', facecolor='wheat', alpha=0)
textstr = '{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}'.format('RCT = Randomized Controlled Trials',
                                                  'SR = Systematic Reviews',
                                                  'MA = Meta-analysis',
                                                  'CCS = Case-Control Studies',
                                                  'CS = Cohort Studies',
                                                  'CSS = Cross-Sectional Studies',
                                                  'PS = Prospective Studies',
                                                  'RS = Retrospective Studies')

ax.text(0.75, 1, textstr, transform=ax.transAxes, fontsize=12,
        verticalalignment='bottom', bbox=props)

# remove spines
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)

# adjust limits and draw grid lines
ax.set_ylim(-0.5, ax.get_yticks()[-1] + 0.5)
ax.set_axisbelow(True)
ax.xaxis.grid(color='gray', linestyle='dashed')

plt.gcf().subplots_adjust(left=0.23, right=0.82, top=0.8)
plt.savefig('./interim-results-2021-08-18/cohort-adjusted.02/ft_screened_work_savings_by_number.png', dpi=600,
            facecolor='white', transparent=False)
# plt.show()

# Code reference: https://towardsdatascience.com/stacked-bar-charts-with-pythons-matplotlib-f4020e4eb4a7


# ## Full-text screened plot (by percentage); Threshold: Optimal F1 (0.01 for RCT)

# In[22]:


# Preparing data for plotting

cols = ['DERP',
        'Work savings',
        "Remaining (not included papers)",
        "Reamining (included papers)",
        "Filtered out included papers",
        'recall']

df_prep = []

for derp_name, df in results2.items():

    df = df.loc[df.fulltxt_screened==1].copy()

    included_design = design.loc[design['File Name'] == derp_name]['Mapped Tags and Extra Tags']
    included_design = included_design.tolist()[0].split(';')

    n_total = df.shape[0]
    TN = df.loc[(df.qualified_tags_total.isna())&(df['included'] == 0)]
    FN = df.loc[(df.qualified_tags_total.isna())&(df['included'] == 1)]

    FP = df.loc[(~df.qualified_tags_total.isna())&(df['included'] == 0)]
    TP = df.loc[(~df.qualified_tags_total.isna())&(df['included'] == 1)]

    nTN = TN.shape[0]
    nFN = FN.shape[0]
    nTNFN = (nTN+nFN)/n_total*100

    nFP = FP.shape[0]/n_total*100
    nTP = TP.shape[0]/n_total*100

    recall = round(TP.shape[0]/(TP.shape[0]+nFN), 2)

    df_prep.append([derp_name, nTNFN, nFP, nTP, nFN, recall])

df_draw_perc = pd.DataFrame(df_prep, columns=cols).round(2)
df_draw_perc = df_draw_perc.sort_values(by=['Work savings'], ascending=False)
df_draw_perc = df_draw_perc.set_index('DERP')


# In[23]:


# Preparing data for plotting (continued)

for_merge = design[['File Name', 'Mapped Tags and Extra Tags']].copy()
for_merge = for_merge.rename(columns={'File Name':'DERP',
                                      'Mapped Tags and Extra Tags':'Included Study Designs'})
for_merge = for_merge.set_index('DERP')
df_draw_perc = df_draw_perc.join(for_merge)


# In[24]:


fields = ['Work savings',
          "Remaining (not included papers)",
          "Reamining (included papers)"]
fields.reverse()

colors = ['#1D2F6F', '#FAC748', '#900C3F']

df_draw_perc = df_draw_perc.sort_values(by=['Work savings', 'Remaining (not included papers)'],
                                        ascending=True)

# figure and axis
fig, ax = plt.subplots(1, figsize=(18, 10))

# plot bars
left = len(df_draw_perc) * [0]
for idx, name in enumerate(fields):
    ax.barh(df_draw_perc.index, df_draw_perc[name], height=0.7,
            left = left, color=colors[idx])
    left = left + df_draw_perc[name]

loss_recall_list = df_draw_perc[['Filtered out included papers', 'recall']].values.tolist()
for i, perc_work_saved in enumerate(df_draw_perc['Work savings'].tolist()):
    loss_val = int(loss_recall_list[i][0])
    recall = loss_recall_list[i][1]
    if loss_val <= 1:
        ax.text(x=101, y=i,
                s='{}% work saved;\nFiltered out {} included paper;\nRecall={}'.format(perc_work_saved,
                                                                                       loss_val,
                                                                                       recall),
                ha='left', va='center', rotation=0)

    elif loss_val > 1:
        ax.text(x=101, y=i,
                s='{}% work saved;\nFiltered out {} included papers;\nRecall={}'.format(perc_work_saved,
                                                                                        loss_val,
                                                                                        recall),
                ha='left', va='center', rotation=0)

# title, legend, labels
ax.set_title('Work saved\n(% of full-text screened items)', loc='left', size=20, weight="bold")
ax.legend(fields, bbox_to_anchor=([0.42, 1, 0, 0]), ncol=1, frameon=False, fontsize=12)
ax.set_xlabel('%', fontsize=14)

# study design abbriviations
derps_included_designs = df_draw_perc['Included Study Designs'].tolist()

derps_included_designs_abbr = []
for each_derp in derps_included_designs:
    included_desings_abbr = []
    for sd in each_derp.split(';'):
        abbr = ''
        if sd == 'Randomized Controlled Trial':
            abbr = 'RCT'
        elif sd == 'Systematic Review':
            abbr = 'SR'
        elif sd == 'Case-Control Studies':
            abbr = 'CCS'
        elif sd == "Cohort Studies":
            abbr = 'CS'
        elif sd == 'Cross-Sectional Studies':
            abbr = 'CSS'
        elif sd == 'Prospective Studies':
            abbr = 'PS'
        elif sd == 'Retrospective Studies':
            abbr = 'RS'
        elif sd == 'Meta-analysis':
            abbr = 'MA'

        included_desings_abbr.append(abbr)
    included_desings_abbr = ', '.join(included_desings_abbr)
    derps_included_designs_abbr.append(included_desings_abbr)

# reset y labels
ori_y_lbl = df_draw_perc.index.tolist()
new_y_lbl = []

for ylbl, sd_abbr in zip(ori_y_lbl, derps_included_designs_abbr):
    new_lbl = '{}\n({})'.format(ylbl, sd_abbr)
    new_y_lbl.append(new_lbl)

ax.set_yticks(ax.get_yticks())
ax.set_yticklabels(labels=new_y_lbl, fontsize=12)

# Add text box
props = dict(boxstyle='Square', facecolor='wheat', alpha=0)
textstr = '{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}'.format('RCT = Randomized Controlled Trials',
                                                  'SR = Systematic Reviews',
                                                  'MA = Meta-analysis',
                                                  'CCS = Case-Control Studies',
                                                  'CS = Cohort Studies',
                                                  'CSS = Cross-Sectional Studies',
                                                  'PS = Prospective Studies',
                                                  'RS = Retrospective Studies')

ax.text(0.75, 1, textstr, transform=ax.transAxes, fontsize=12,
        verticalalignment='bottom', bbox=props)


# remove spines
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
# adjust limits and draw grid lines
ax.set_ylim(-0.5, ax.get_yticks()[-1] + 0.5)
ax.set_axisbelow(True)
ax.xaxis.grid(color='gray', linestyle='dashed')

plt.gcf().subplots_adjust(left=0.25, right=0.9, top=0.8)
plt.savefig('./interim-results-2021-08-18/cohort-adjusted.02/ft_screened_work_savings_by_percentage.png', dpi=600,
            facecolor='white', transparent=False)
