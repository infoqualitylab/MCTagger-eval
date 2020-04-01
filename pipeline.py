#connect to database
#!/usr/bin/python

import sqlite3
import os
import pandas as pd

#get working directory
print(os.getcwd())

#connect to database - database large so have to download to local computer
DB = sqlite3.connect('/Users/brandismith/Documents/Tagger Data/all_predictions_1987_2019')
print("Opened database successfully");

#make variable for old taggers -- may take some time; very large and have to download to local computer
rctTags=pd.read_table("/Users/brandismith/Documents/Tagger Data/all.csv")

#select RCT Tagger Table
rctDB = DB.execute("SELECT * FROM RANDOMIZED_CONTROLLED_TRIAL")
DB.close()

#read starting PubMed IDs
startIds=pd.read_csv('OCR_RCT_START_IDS.txt', header=None)
startIds.rename(columns={0: 'Year', 1: 'PMID'}, inplace=True)
#start.ids<-str_replace_all(start.ids$PubMed.ID, "[.].*","")

#read retrieved abstracts
absRet=pd.read_csv('OCR_RCT_RET_ABS_IDS.txt', header=None)
absRet.rename(columns={0: 'Year', 1: 'PMID'}, inplace=True)
#abs.ret<-str_replace_all(abs.ret$PubMed.ID, "[.].*","")


