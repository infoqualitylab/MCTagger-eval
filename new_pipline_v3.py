#!/usr/bin/env python
# coding: utf-8

import pandas as pd

# In[2]:
#READ THE TAGGER PREDICITIONS
#cols_list: PMID + Tags to pull scores
cols_list = ['PMID', 'Randomized Controlled Trial', 'Systematic Review', 'Meta-analysis',
             'Case-Control Studies', 'Cohort Studies', 'Cross-Sectional Studies',
             'Prospective Studies', 'Retrospective Studies', 'Clinical Study', 'Practice Guideline']
df = pd.read_csv("FILE PATH TO mt_modelscores_20210107.tsv", 'r', delimiter="\t", usecols=cols_list)

#READ PMIDS FROM EACH STAGE OF REVIEW
#THREE INPUT FILES GO HERE
input_cols_list = ['PMID']

abs_file = 'FILE PATH TO ABSTRACT SCREENED LIST'
ft_file = 'FILE PATH TO FULL-TEXT SCREENED LIST'
included_file = 'FILE PATH TO INCLUDED LIST'

# THE OUTPUT FILE PATH & NAME
out_file = 'PATH TO OUTPUT FILE'

abs_screened = pd.read_csv(abs_file, 'r', usecols=input_cols_list, dtype=str)
ft_screened = pd.read_csv(ft_file, 'r', usecols=input_cols_list, dtype=str)
included = pd.read_csv(included_file, 'r', usecols=input_cols_list, dtype=str)

abs_screened = abs_screened.loc[abs_screened.PMID.str.isnumeric()].astype(int)
abs_screened = abs_screened.drop_duplicates()
ft_screened = ft_screened.loc[ft_screened.PMID.str.isnumeric()].astype(int)
ft_screened = ft_screened.drop_duplicates()
included = included.loc[included.PMID.str.isnumeric()].astype(int)
included = included.drop_duplicates()

full_df = pd.concat([abs_screened, ft_screened, included])
full_df = full_df.drop_duplicates()

# In[3]:
# RETRIEVE PREDICTIONS
print(abs_screened.shape)
mt_scores = full_df.merge(df, how='left')

mt_scores['abs_screened'] = 0
mt_scores.loc[mt_scores.PMID.isin(abs_screened.PMID), 'abs_screened'] = 1

mt_scores['fulltxt_screened'] = 0
mt_scores.loc[mt_scores.PMID.isin(ft_screened.PMID), 'fulltxt_screened'] = 1

mt_scores['included'] = 0
mt_scores.loc[mt_scores.PMID.isin(included.PMID), 'included'] = 1

if mt_scores.loc[mt_scores['abs_screened'] == 1].shape[0] != abs_screened.shape[0]:
    print('ERROR(abs_screened): Number not match')
    print(mt_scores.loc[mt_scores['abs_screened'] == 1].shape)
    print(abs_screened.shape)
    print(abs_screened.loc[~abs_screened.PMID.isin(mt_scores.PMID)])

if mt_scores.loc[mt_scores['fulltxt_screened'] == 1].shape[0] != ft_screened.shape[0]:
    print('ERROR(fulltxt_screened): Number not match')
    print(mt_scores.loc[mt_scores['fulltxt_screened'] == 1].shape)
    print(ft_screened.shape)
    print(ft_screened.loc[~ft_screened.PMID.isin(mt_scores.PMID)])

if mt_scores.loc[mt_scores['included'] == 1].shape[0] != included.shape[0]:
    print('ERROR(included): Number not match')
    print(mt_scores.loc[mt_scores['included'] == 1].shape)
    print(included.shape)
    print(included.loc[~included.PMID.isin(mt_scores.PMID)])

mt_scores.set_index('PMID').to_csv(out_file)



