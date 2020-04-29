# import csv
# import pandas as pd


#Input Full-Text screened predictions or included article predictions here:
infile = open('Full-Text Assessed - Predictions only - PCSK9.txt', 'r')


text = infile.readlines()
infile.close()

totalIds = 0

for prediction in text:
    totalIds = totalIds + 1
print("TotalIds:", totalIds, "\n")

##Recall (the number of predictions above a certain threshold, calculated
#using full-text assessed and included):

n = [0, .0001, .001, .01, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]
NumRetained = 0
for threshold in n:
    for prediction in text:
        if ((eval(prediction.strip()))) >= threshold:
            NumRetained = NumRetained + 1
    print("Threshold:", threshold)
    print("Number retained:", NumRetained)
    Recall = NumRetained / totalIds
    NumRetained = 0
    print("Percent recall:", Recall, "\n")

##For work savings, input files are abstract screened and full-text screened, and calculate the percent
#of predictions below the threshold:

n = [0, .0001, .001, .01, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]
NumDiscarded = 0
for threshold in n:
    for prediction in text:
        if ((eval(prediction.strip()))) <= threshold:
            NumDiscarded = NumDiscarded + 1
    print("Threshold:", threshold)
    print("Number filtered out:", NumDiscarded)
    workSavings = NumDiscarded / totalIds
    NumDiscarded = 0
    print("Work Savings:", workSavings, "\n")
