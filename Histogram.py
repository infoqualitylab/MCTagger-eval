import pandas as pd
import numpy as np

from matplotlib import pyplot as plt

plt.style.use('fivethirtyeight')

input_cols_list = ['Prediction']

abstractScreened = pd.read_csv('/Users/randiproescholdt/PycharmProjects/pythonProject1/PCSK9/abstract_screened_predictions_RCT_PCSK9.csv', 'r', delimiter=",",
                         dtype=str)
full_text = pd.read_csv('/Users/randiproescholdt/PycharmProjects/pythonProject1/PCSK9/full_text_screened_predictions_RCT_PCSK9.csv', 'r', delimiter=",",
                         dtype=str)
included = pd.read_csv('/Users/randiproescholdt/PycharmProjects/pythonProject1/PCSK9/included_predictions_RCT_PCSK9.csv', 'r', delimiter=",",
                         dtype=str)

abs_prediction_list = []
for prediction in abstractScreened['Prediction']:
    abs_prediction_list.append(eval(prediction.strip()))

full_text_prediction_list = []
for prediction in full_text['Prediction']:
    full_text_prediction_list.append(eval(prediction.strip()))

included_prediction_list = []
for prediction in included['Prediction']:
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
# plt.savefig('/Users/randiproescholdt/PycharmProjects/pythonProject1/Histogram_RCT_PCSK9.png', dpi = 300)
