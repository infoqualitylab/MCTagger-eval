import pandas as pd
import numpy as np

from matplotlib import pyplot as plt

plt.style.use('fivethirtyeight')

abstractScreened = open('Abstract Screened Predictions (148) - PCSK9.txt', 'r')
abstractScreenedList = abstractScreened.readlines()
abstractScreened.close()

abs_prediction_list = []
for prediction in abstractScreenedList:
    abs_prediction_list.append(eval(prediction.strip()))

full_text = open('Full-Text Assessed - Predictions only - PCSK9.txt', 'r')
full_text_list = full_text.readlines()
full_text.close()

full_text_prediction_list = []
for prediction in full_text_list:
    full_text_prediction_list.append(eval(prediction.strip()))

included = open('Included RCT Scores(19).txt', 'r')
included_list = included.readlines()
included.close()

included_prediction_list = []
for prediction in included_list:
    included_prediction_list.append(eval(prediction.strip()))

bins = [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]

plt.figure(figsize=(8,10), dpi = 100)

b1 = plt.hist(abs_prediction_list, bins = bins, edgecolor = 'black', hatch = '/', label = "Abstract Screened")
b2 = plt.hist(full_text_prediction_list, bins = bins, edgecolor = 'black', label = "Full-Text Screened")
b3 = plt.hist(included_prediction_list, bins = bins, color = "yellow", hatch = '.', edgecolor = 'black', label = "Included in Review")

plt.title('PCSK9 RCT Prediction Frequencies')
plt.xlabel('RCT Prediction')
plt.ylabel('Frequency')

plt.xticks(labels=("0", ".1", ".2", ".3", ".4", ".5", ".6", ".7", ".8", ".9", "1"),
        ticks=(0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1))

plt.tight_layout()

plt.axvline(.01, color="green", label = ".01 (Recommended prediction value for filtering)", linestyle = "--", linewidth = 2)

plt.legend(loc = "best")

plt.show()
# plt.savefig('Histogram - PCSK9 - RCT.png', dpi = 300)
