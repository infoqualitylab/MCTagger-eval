import pandas as pd
import csv


cols_list = ['PMID', 'Randomized Controlled Trial']
df = pd.read_csv("/Users/randiproescholdt/Documents/Files from HP/RA/NIH/mt_modelscores_20210107.tsv", 'r', delimiter="\t", usecols=cols_list)
prediction_data = csv.reader(df)

#READ PMIDS FROM EACH STAGE OF REVIEW
#THREE INPUT FILES GO HERE
input_cols_list = ['PMID']
abs_screened=pd.read_csv('/Users/randiproescholdt/Documents/Files from HP/RA/NIH/DERP Reports/Long-Acting Insulins/All Records Screened - PMIDs - Long Acting Insulins (1086).csv', 'r', usecols=input_cols_list)
ft_screened=pd.read_csv('/Users/randiproescholdt/Documents/Files from HP/RA/NIH/DERP Reports/Long-Acting Insulins/Full-Text Assessed - PMIDs - Long Acting Insulins.csv', 'r', usecols=input_cols_list)
included=pd.read_csv('/Users/randiproescholdt/Documents/Files from HP/RA/NIH/DERP Reports/Long-Acting Insulins/Included - PMIDS - Long Acting Insulins.csv', 'r', usecols=input_cols_list)

number = 0
pmid_list = []
prediction_list = []

#RETRIEVE PREDICTIONS FOR ABSTRACT SCREENED ITEMS (ALL ITEMS IN REVIEW THAT HAVE PMIDS)
#RENAME FOUR OUTPUT FILES APPROPRIATELY
with open('abstract_screened_predictions_RCT_Long-Acting Insulins.csv', 'w') as csvfile:
    fieldnames = ['PMID', 'Prediction']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for item in df['PMID']:
        for row in abs_screened['PMID']:
            if item == row:
                if item not in pmid_list:
                    writer.writerow({'PMID': item, 'Prediction': df.iloc[number, 1]})
                    pmid_list.append(item)
                    prediction_list.append(df.iloc[number, 1])
        number = number + 1


#LIST ITEMS NOT FOUND IN THE PREDICTION FILE
# missing_row_list =[]
#
# for row in abs_screened['PMID']:
#     if row not in pmid_list:
#         missing_row_list.append(row)
#
# print("Abstract screened items with no prediction found:", missing_row_list)

with open('abstract_screened_RCT_nopredictionfound_Long-Acting Insulins.csv', 'w') as csvfile:
    fieldnames = ['PMID']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for row in abs_screened['PMID']:
        if row not in pmid_list:
            writer.writerow({'PMID': row})


#RETRIEVE PREDICTIONS FOR FULL-TEXT SCREENED ITEMS (FROM THE LIST OF ABSTRACT SCREENED PREDICTIONS)
number = 0
# ft_missing_list = []

with open('full_text_screened_predictions_RCT_Long-Acting Insulins.csv', 'w') as csvfile:
    fieldnames = ['PMID', 'Prediction']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for item in pmid_list:
        for row in ft_screened['PMID']:
            if item == row:
                writer.writerow({'PMID': item, 'Prediction': prediction_list[number]})
        number = number + 1

# print("In full-text screened, but missing from abstract screened:", ft_missing_list)



#RETRIEVE PREDICTIONS FOR INCLUDED ITEMS (FROM THE LIST OF FULL-TEXT SCREENED PREDICTIONS)
number = 0
# inc_missing_list = []

with open('included_predictions_RCT_Long-Acting Insulins.csv', 'w') as csvfile:
    fieldnames = ['PMID', 'Prediction']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for item in pmid_list:
        for row in included['PMID']:
            if item == row:
                writer.writerow({'PMID': item, 'Prediction': prediction_list[number]})
        number = number + 1

# print("In included, but missing from full-text screened:", inc_missing_list)
