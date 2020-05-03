# import csv
# import pandas as pd

def main():
    abstractCalc()
    fullTextCalc()
    includedCalc()
#     # abstractScreened, fullText, Included = Inputs()
#     abs_workSavings = abstractCalc()
#     ft_workSavings, ft_recall = fullTextCalc()
#     # inc_recall = includedCalc()
#     threshold, numIncluded, incNumRetained = includedCalc()
#     outputResults()
# #
# def Inputs():
#     # Input abstract screened predictions here:
#     abstractScreened = open('Tagger Scores only  - Abstract Screened - PCSK9.txt', 'r')
#     abstractScreenedList = abstractScreened.readlines()
#     abstractScreened.close()
#
#     #Input Full-Text screened predictions here:
#     fullText = open('Full-Text Assessed - Predictions only - PCSK9.txt', 'r')
#     fullTextList = fullText.readlines()
#     fullText.close()
#
#     #Input included article predictions here:
#     included = open('Included RCT Scores(19).txt', 'r')
#     includedList = included.readlines()
#     included.close()
#
#     return abstractScreenedList, fullTextList, includedList


def abstractCalc():
    # Input abstract screened predictions here:
    abstractScreened = open('Tagger Scores only  - Abstract Screened - PCSK9.txt', 'r')
    abstractScreenedList = abstractScreened.readlines()
    abstractScreened.close()

    numAbstractScreened = 0

    for prediction in abstractScreenedList:
        numAbstractScreened = numAbstractScreened + 1
    print("Number of articles abstract screened:", numAbstractScreened, "\n")

    ##For work savings, input files are abstract screened and full-text screened, and calculate the percent
    #of predictions below the threshold:

    n = [0, .0001, .001, .01, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]
    NumDiscarded = 0
    for threshold in n:
        for prediction in abstractScreenedList:
            if ((eval(prediction.strip()))) <= threshold:
                NumDiscarded = NumDiscarded + 1
        abs_worksavings = NumDiscarded / numAbstractScreened
        print("Threshold:", threshold)
        print("Number filtered out:", NumDiscarded)
        workSavings = NumDiscarded / numAbstractScreened
        NumDiscarded = 0
        print("Work Savings:", workSavings, "\n")
    # return abs_worksavings


def fullTextCalc():
    #Input Full-Text screened predictions here:
    fullText = open('Full-Text Assessed - Predictions only - PCSK9.txt', 'r')
    fullTextList = fullText.readlines()
    fullText.close()

    numFullText = 0

    for prediction in fullTextList:
        numFullText = numFullText + 1
    print("Number of articles full-text screened:", numFullText, "\n")

    ##Recall (the number of predictions above a certain threshold, calculated
    #using full-text assessed and included):

    n = [0, .0001, .001, .01, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]
    NumRetained = 0
    for threshold in n:
        for prediction in fullTextList:
            if ((eval(prediction.strip()))) >= threshold:
                NumRetained = NumRetained + 1
        ft_recall = NumRetained / numFullText
        print("Threshold:", threshold)
        print("Number retained:", NumRetained)
        Recall = NumRetained / numFullText
        NumRetained = 0
        print("Percent recall:", Recall, "\n")

    ##For work savings, input files are abstract screened and full-text screened, and calculate the percent
    #of predictions below the threshold:

    n = [0, .0001, .001, .01, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]
    NumDiscarded = 0
    for threshold in n:
        for prediction in fullTextList:
            if ((eval(prediction.strip()))) <= threshold:
                NumDiscarded = NumDiscarded + 1
        # ft_worksavings = NumDiscarded / numFullText
        print("Threshold:", threshold)
        print("Number filtered out:", NumDiscarded)
        workSavings = NumDiscarded / numFullText
        NumDiscarded = 0
        print("Work Savings:", workSavings, "\n")
    # return ft_recall, ft_worksavings


def includedCalc():
    #Input included article predictions here:
    included = open('Included RCT Scores(19).txt', 'r')
    includedList = included.readlines()
    included.close()

    numIncluded = 0

    for prediction in includedList:
        numIncluded = numIncluded + 1
    print("Number of articles included in final review:", numIncluded, "\n")

    ##Recall (the number of predictions above a certain threshold, calculated
    #using full-text assessed and included):

    n = [0, .0001, .001, .01, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]
    incNumRetained = 0
    for threshold in n:
        for prediction in includedList:
            if ((eval(prediction.strip()))) >= threshold:
                incNumRetained = incNumRetained + 1
            #     return incNumRetained
        inc_recall = incNumRetained / numIncluded
        print("Threshold:", threshold)
        print("Number retained:", incNumRetained)
        Recall = incNumRetained / numIncluded
        incNumRetained = 0
        print("Percent recall:", Recall, "\n")
        ##COULD I WRITE OUT CSV HERE?
        # outfile = open('inc_recall.csv', 'w')
        # csvout = csv.writer(outfile)
        # # row = threshold, inc_recall
        # csvout.writerow(row)
    # return threshold, numIncluded, incNumRetained

# def outputResults():
#     # threshold, numIncluded, incNumRetained = includedCalc()
#     incRecall = incNumRetained / numIncluded
#     #write out list for included recall, full-text recall, full-text work savings, and abstract work savings
#     print(incRecall)
# #Would it be useful to be able to input any number for n and have work savings and recall returned?

if __name__ == '__main__': main()
