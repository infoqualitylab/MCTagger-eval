import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def main():
    n, worksavings_abstract = abstractCalc()
    o, recall_fulltext, o2, worksavings_fulltext, ft_full_recall, ft_ninetyfive_recall = fullTextCalc()
    p, recall_included, inc_full_recall, inc_ninetyfive_recall = includedCalc()

    # plt.figure(figsize=(100,5), dpi=600) #Don't need this when using subplots?
    fig, (ax1, ax2) = plt.subplots(2,1, figsize = (15,7), sharey=True)
    ax2.set_title('Percentage of Retrieved Articles Retained After Filtering')
    ax1.set_title('Percentage of Articles Filtered Out at Each Prediction Value')
    ax2.plot(o, recall_fulltext, label = "Retained after abstract screening",
             color = 'orange')
    ax1.plot(o2, worksavings_fulltext, label = "Filtered out during full-text screening",
             color = "blue")
    ax1.plot(n, worksavings_abstract, label = "Filtered out during abstract screening",
             color = 'orange')
    ax2.plot(p, recall_included, label = "Retained after full-text screening", color = 'blue')
    ax1.plot([.01, .01], [0, 1],
             linestyle = "--", color = "green", label = "Recommended prediction value for filtering")
    ax1.text(.01, .4, ".01", rotation = 45)
    # ax2.plot([eval(ft_full_recall), eval(ft_full_recall)],
    #          [0, 1], linestyle = "--", color = "magenta", label = "Abstract screening - Max filtering value with 100% recall")
    # ax2.text(eval(ft_full_recall), .4, eval(ft_full_recall), rotation = 45)
    ax2.plot([eval(inc_full_recall), eval(inc_full_recall)],
               [0, 1], linestyle = "--", color = "red", label = "Max filtering value with 100% recall of included articles")
    ax2.text(eval(inc_full_recall), .3, eval(inc_full_recall), rotation = 45)
    plt.xticks(labels=("0", "\n.0001", "\n\n.001", "\n\n\n.01", ".1", ".2", ".3", ".4", ".5", ".6", ".7", ".8", ".9", "1"),
            ticks=(0, .0001, .001, .01, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1))
    ax1.set_xticklabels(labels=("0", "\n.0001", "\n\n.001", "\n\n\n.01", ".1", ".2", ".3", ".4", ".5", ".6", ".7", ".8", ".9", "1"), rotation = 45)
    ax1.set_xticks(ticks = (0, .0001, .001, .01, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1))
    plt.yticks(labels= ("0%", "10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"),
               ticks = (0, .1, .2, .3, .4,.5,.6,.7,.8, .9, 1))
    plt.xticks(rotation=45)
    plt.xlabel('Prediction Value Used for Filtering')
    ax1.set_xlabel('Prediction Value Used for Filtering\n\n\n')
    plt.tight_layout(pad = 3) # Adds space around and between graphs
    # ax1.set_ylabel('Percentage of Articles Filtered Out')
    # ax2.set_ylabel('Percentage of Articles Retained')
    fig.suptitle('PCSK9 RCT Filtering', fontdict={'fontsize': 30})
    ax1.legend(loc = 'lower right')
    # ax1.legend(loc = 'best') # Try this if the above legend location isn't ideal;
    # or try putting it in the same location as ax2 below
    ax2.legend(loc='best', bbox_to_anchor=(1, -.15))
    # plt.show()
    plt.savefig('Filtering Graphs - PCSK9 - RCT2.png', dpi = 500)
    #Always comment out either the "show" or the "save" part because Python doesn't seem to like both at the same time


def abstractCalc():
    # Input abstract screened predictions here:
    abstractScreened = open('Abstract Screened Predictions (148) - PCSK9.txt', 'r')
    abstractScreenedList = abstractScreened.readlines()
    abstractScreened.close()

    numAbstractScreened = 0

# Counter to figure out the total number of predictions; will use for calculations in next step
    for prediction in abstractScreenedList:
        numAbstractScreened = numAbstractScreened + 1
    print("Number of articles abstract screened:", numAbstractScreened, "\n")

    ## Work Savings: Calculate the percent of predictions below each threshold:

    n = [0, .0001, .001, .01, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]
    # n holds the list of "thresholds"; we will be calculating the amount of work someone doing this
    # review would have saved if they filtered out all articles with predictions below these numbers
    worksavings_abstract = []
    numDiscarded = 0
    for threshold in n: #loop through thresholds
        for prediction in abstractScreenedList: #loop through list from input file
            if ((eval(prediction.strip()))) <= threshold:
                numDiscarded = numDiscarded + 1         # counting up the number that are below the threshold
        workSavings = numDiscarded / numAbstractScreened # Number below threshold divided total
        # print("Threshold:", threshold)
        # print("Number filtered out:", NumDiscarded)
        worksavings_abstract.append(workSavings)   #making a list of the work savings values at each threshold
        numDiscarded = 0 #Set numDiscarded back to zero to get a fresh count for the next prediction
        # print("Work Savings:", workSavings, "\n")
    return n, worksavings_abstract # the values that will be x and y for this line on the graph


def fullTextCalc():
    #Input Full-Text screened predictions here:
    fullText = open('Full-Text Assessed - Predictions only - PCSK9.txt', 'r')
    fullTextList_raw = fullText.readlines()
    fullText.close()

    fullTextList = []

    for prediction in fullTextList_raw:
        fullTextList.append(prediction.strip())

    fullTextList.sort(reverse = True) #sorting in descending order so that 95% recall can be determined by index position

    numFullText = 0

    for prediction in fullTextList:
        numFullText = numFullText + 1
    print("Number of articles full-text screened:", numFullText, "\n")

    #Index position starts as 0, so needs to be one more than it's number in the list;
    #Dropping the decimal effectively rounds down; these cancel out?
    if (numFullText * .95) == int:
        ft_ninetyfive_recall = fullTextList[int(numFullText * .95) - 1]
    else:
        ft_ninetyfive_recall = fullTextList[int(numFullText * .95)]
    ft_full_recall = min(fullTextList)

    print("Abstract screening 95% recall:", fullTextList[int(numFullText * .95)])
    print("Abstract screening 100% recall:", min(fullTextList))

    ##Recall: Calculate the percent of predictions above each threshold:

    o = [0, .0001, .001, .01, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]
    recall_fulltext = []
    full_recall = []
    ninetyfive_recall = [] #this method of getting 95% and 100% recall works if you want to go by "bins" and not the actual number
    numRetained = 0
    for threshold in o:
        for prediction in fullTextList:
            if ((eval(prediction.strip()))) >= threshold: # Check whether the predictions are above threshold
                numRetained = numRetained + 1
        # print("Threshold:", threshold)
        # print("Number retained:", NumRetained)
        Recall = numRetained / numFullText
        # if Recall == 1:
        #     full_recall.append(threshold)
        # if Recall >= .95:
        #     ninetyfive_recall.append(threshold)
        recall_fulltext.append(Recall)
        numRetained = 0
        # print("Percent recall:", Recall, "\n")
    # print(n)
    # print(recall_full_text)
    # print("100% recall:", max(full_recall))
    # print("95% recall:", max(ninetyfive_recall))
    # ft_full_recall = max(full_recall)
    # ft_ninetyfive_recall = max(ninetyfive_recall)

#This file will be checked for both recall and work savings, since it is the result of filtering
#after abstract screening, and will undergo further filtering after full-text screening.

#This work savings calculation is the same as the previous one for the abstract screened files.

    o2 = [0, .0001, .001, .01, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]
    worksavings_fulltext = []
    numDiscarded = 0
    for threshold in o2:
        for prediction in fullTextList:
            if ((eval(prediction.strip()))) <= threshold:
                numDiscarded = numDiscarded + 1
        # ft_worksavings = NumDiscarded / numFullText
        # print("Threshold:", threshold)
        # print("Number filtered out:", NumDiscarded)
        workSavings = numDiscarded / numFullText
        worksavings_fulltext.append(workSavings)
        numDiscarded = 0
        # print("Work Savings:", workSavings, "\n")
    return o, recall_fulltext, o2, worksavings_fulltext, ft_full_recall, ft_ninetyfive_recall #2 x's and 2 y's, and 2 benchmark lines


#Included articles are only checked for recall; they will not be filtered any further, so there
#is no more work savings to calculate

def includedCalc():
    #Input included article predictions here:
    included = open('Included RCT Scores(19).txt', 'r')
    includedList_raw = included.readlines()
    included.close()

    includedList = []

    for prediction in includedList_raw:
        includedList.append(prediction.strip())

    includedList.sort(reverse = True)

    numIncluded = 0

    for prediction in includedList:
        numIncluded = numIncluded + 1
    print("Number of articles included in final review:", numIncluded, "\n")


    #need to multiply total num by .95, round that up, then use it as an indexing position
    #Indexing starts with 0th position, so this is rounded down
    if (numIncluded * .95) == int:
        inc_ninetyfive_recall = includedList[int(numIncluded * .95) - 1]
    else:
        inc_ninetyfive_recall = includedList[int(numIncluded * .95)]
    inc_full_recall = min(includedList)

    print("Full-text screening 95% recall:", inc_ninetyfive_recall)
    print("Full-text screening 100% recall:", inc_full_recall)

    ##Recall (the number of predictions above a certain threshold, calculated
    #using full-text assessed and included):

    p = [0, .0001, .001, .01, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]
    recall_included = []
    # full_recall = []
    # ninetyfive_recall = []
    incNumRetained = 0
    for threshold in p:
        for prediction in includedList:
            if ((eval(prediction.strip()))) >= threshold:
                incNumRetained = incNumRetained + 1
        # inc_recall = incNumRetained / numIncluded
        # print("Threshold:", threshold)
        # print("Number retained:", incNumRetained)
        Recall = incNumRetained / numIncluded
        # if Recall == 1:
        #     full_recall.append(threshold)
        # if Recall >= .95:
        #     ninetyfive_recall.append(threshold)
        recall_included.append(Recall)
        incNumRetained = 0
        # print("Percent recall:", Recall, "\n")
    # print("100% recall:", max(full_recall))
    # print("95% recall:", max(ninetyfive_recall))
    # inc_full_recall = max(full_recall)
    # inc_ninetyfive_recall = max(ninetyfive_recall)
    return p, recall_included, inc_full_recall, inc_ninetyfive_recall

if __name__ == '__main__': main()
