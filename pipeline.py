#!/usr/bin/python

import sqlite3
import os
import pandas as pd
import numpy as np
import re

#get working directory
print(os.getcwd())

#path to database
pathDB='/Users/brandismith/Documents/Tagger Data/all_predictions_1987_2019'

#connect to database
DB = sqlite3.connect(pathDB)

#path to old taggers
pathOld='/Users/brandismith/Documents/Tagger Data/all.csv'

#retrieve old taggers
rctTags=pd.read_table(pathOld)

#select RCT Tagger Table and return as pandas dataframe
#REF: https://datacarpentry.org/python-ecology-lesson/09-working-with-sql/index.html
rctDf = pd.read_sql_query("SELECT * FROM RANDOMIZED_CONTROLLED_TRIAL", DB)

#close connection to database
DB.close()

#subset columns of interest and rename columns
rctDf=rctDf[['id','prediction']]
rctDf.rename(columns={ "id": 'PMID', "prediction": 'RCT Prediction'}, inplace=True)
print(rctDf)

#combine old taggers and predictions from database
rct_frames=[rctTags, rctDf]
rctAll=pd.concat(rct_frames)
print(rctAll)

#size or length of database
len(rctAll.index)#29,283,987 rows


#read starting PubMed IDs from search
startIds=pd.read_csv('OCR_RCT_START_IDS.txt', header=None)
#name columns year and pubmed ID
startIds.rename(columns={0: 'Year', 1: 'PMID'}, inplace=True)
#remove expressions from pubmed IDs
# REF: https://stackoverflow.com/questions/13682044/remove-unwanted-parts-from-strings-in-a-column
startIds['PMID'] = startIds['PMID'].str.split(r'\D').str.get(1)
print(startIds)
len(startIds.index)#6827 rows


#read retrieved abstract PubMed IDs
absRet=pd.read_csv('OCR_RCT_RET_ABS_IDS.txt', header=None)
#name columns year and pubmed ID
absRet.rename(columns={0: 'Year', 1: 'PMID'}, inplace=True)
#remove expressions from pubmed IDs
absRet['PMID'] = absRet['PMID'].str.split(r'\D').str.get(1)
print(absRet)
len(absRet.index)#325

#extract predictions for abstracts retrieved
pred_abs = pd.merge(absRet, rctAll, on=['PMID'], how='inner')
print(pred_abs)
len(pred_abs)#253

#print predictions for abstracts retrieved
pred_abs.to_csv (r'abstract_predictions.csv', index = False, header=True)

#which PMIDs missing between abstracts retrieved list and prediction list?
pred_abs['Year Missing']=np.where(absRet.Year != pred_abs.Year, 'True',"False")
#print predictions for full text retrieved

#calculate works savings from starting IDs, abstracts retreived to full text screened
