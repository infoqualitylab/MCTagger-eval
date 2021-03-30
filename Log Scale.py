import pandas as pd
import numpy as np

from matplotlib import pyplot as plt

plt.style.use('fivethirtyeight')

#Get x's and y's for abstract screened:
abs_screened = pd.read_csv('/Users/randiproescholdt/PycharmProjects/pythonProject1/PCSK9/abstract_screened_predictions_RCT_PCSK9.csv', 'r', delimiter=",",
                        dtype=str)

abs_prediction_list = [] #This will be our y
for prediction in abs_screened['Prediction']:
    abs_prediction_list.append(eval(prediction.strip()))

abs_prediction_list.sort(reverse = True)
#Predictions need to be sorted; otherwise, the lines will not have visible order

num_abstract_screened = 0
num_abstract_list = [] #This will be our x

for prediction in abs_screened['Prediction']:
    num_abstract_screened = num_abstract_screened + 1
    num_abstract_list.append(num_abstract_screened)
print("Number of articles abstract screened:", num_abstract_screened, "\n") #Just checking that the number looks right
# print(num_abstract_list)

#Get x's and y's for Full-Text Screened
full_text = pd.read_csv('/Users/randiproescholdt/PycharmProjects/pythonProject1/PCSK9/full_text_screened_predictions_RCT_PCSK9.csv', 'r', delimiter=",",
                         dtype=str)

full_text_prediction_list = []
for prediction in full_text['Prediction']:
    full_text_prediction_list.append(eval(prediction.strip()))

full_text_prediction_list.sort(reverse = True)

num_ft_screened = 0
num_ft_list = []

for prediction in full_text['Prediction']:
    num_ft_screened = num_ft_screened + 1
    num_ft_list.append(num_ft_screened)
print("Number of articles full-text screened:", num_ft_screened, "\n")
# print(num_ft_list)


#Get x's and y's for included articles
included = pd.read_csv('/Users/randiproescholdt/PycharmProjects/pythonProject1/PCSK9/included_predictions_RCT_PCSK9.csv', 'r', delimiter=",",
                         dtype=str)

included_prediction_list = []
for prediction in included['Prediction']:
    included_prediction_list.append(eval(prediction.strip()))

included_prediction_list.sort(reverse = True)

num_included = 0
num_included_list = []

for prediction in included['Prediction']:
    num_included = num_included + 1
    num_included_list.append(num_included)
print("Number of articles included in the review:", num_included, "\n")
# print(num_included_list)

plt.figure(figsize=(12, 6), dpi=100)

#Plot the 3 lines
plt.plot(num_abstract_list, abs_prediction_list, label = "Abstract Screened")
plt.plot(num_ft_list, full_text_prediction_list, label = "Full-Text Screened")
plt.plot(num_included_list, included_prediction_list, label = "Included")

#And a benchmark line
plt.plot([0, num_abstract_screened], [.01, .01], linewidth = 2, linestyle = "--",
         label = ".01 (Recommended prediction value for filtering)")

# plt.xlim(num_abstract_screened, 0)
# plt.ylim(1, .00001)

plt.yscale('log')
plt.yticks(labels = (".00001", ".0001", ".001", ".01", ".1", "1"), ticks = (.00001, .0001, .001, .01, .1, 1))
# plt.title("Cumulative Frequency of Max Predictions for Long Acting Insulins Report:\nCase Control, RCTs, and Cohort Studies")
plt.title("Cumulative Frequency of RCT Predictions for PCSK9 Report")
plt.xlabel("Number of Predictions above Prediction Value")
plt.ylabel("RCT Predictions")
plt.legend(loc = 'best')

plt.tight_layout(pad = 3)

plt.show()
# plt.savefig('/Users/randiproescholdt/PycharmProjects/pythonProject1/LogScale_RCT_PCSK9.png', dpi = 300)
