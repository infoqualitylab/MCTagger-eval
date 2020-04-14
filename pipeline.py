#!/usr/bin/python

import sqlite3
import os
import pandas as pd
import re

#get working directory
print(os.getcwd())

#path to database
pathDB='/Users/brandismith/Documents/Tagger Data/all_predictions_1987_2019'

#connect to database
DB = sqlite3.connect(pathDB)

#path to old taggers
pathOld='/Users/brandismith/Documents/Tagger Data/all.csv'

#make variable for old taggers
rctTags=pd.read_table(pathOld)

#select RCT Tagger Table
rctDB = DB.execute("SELECT * FROM RANDOMIZED_CONTROLLED_TRIAL")
#close connection to database
DB.close()

#read starting PubMed IDs from search
startIds=pd.read_csv('OCR_RCT_START_IDS.txt', header=None)
#name columns year and pubmed ID
startIds.rename(columns={0: 'Year', 1: 'PMID'}, inplace=True)
#remove expressions from pubmed IDs
# REF: https://stackoverflow.com/questions/13682044/remove-unwanted-parts-from-strings-in-a-column
startIds['PMID'] = startIds['PMID'].str.split(r'\D').str.get(1)
print(startIds)


#read retrieved abstract PubMed IDs
absRet=pd.read_csv('OCR_RCT_RET_ABS_IDS.txt', header=None)
#name columns year and pubmed ID
absRet.rename(columns={0: 'Year', 1: 'PMID'}, inplace=True)
#remove expressions from pubmed IDs
absRet['PMID'] = absRet['PMID'].str.split(r'\D').str.get(1)
print(absRet)

#match ids to database and csv files
#REF: https://datatofish.com/sql-to-pandas-dataframe/



#print results
