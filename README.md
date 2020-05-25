## Purpose
The purpose of this pipeline is to create a more user-friendly approach to extracting tagger predictions from a given set of PubMed IDs or a bibliography file such as .ris or .xml. 

## File descriptions:
1. OCR_RCT_START_IDS.txt : Starting PubMed IDs from protocol search 
2. OCR_RCT_RET_ABS_IDS.txt : Retrieved PubMed IDs from retrieved abstracts for review 
3. pipeline.R : R code which extracts tagger predictions from established SQL database/aggregated database.
4. pipeline.py: python code which has similar purpose as R pipeline, but has better data visualization options
5. Work savings and recall.py : Reads files with lists of predictions from abstract-screened, full-text screened, and included articles, and creates a line graph of the work savings and recall from both screening levels.
6. Histogram.py : Reads files with lists of predictions from abstract-screened, full-text screened, and included articles, and creates a histogram showing the frequency of prediction values in bins at .1 intervals from 0 to 1.
7. Log Scale.py : Reads files with lists of predictions from abstract-screened, full-text screened, and included articles, and creates a line graph showing were all prediction values fall on a logarithmic scale from .0001 to 1.

## Notes on input files
OCR_RCT_START_IDS.txt and OCR_RCT_RET_ABS_IDS.txt are examples of input files for pipeline.R and pipeline.py. Input files for these piplelines need to contain a list of PubMed Ids, but can optionally include a year as these do. 
These files can be found here: https://uofi.app.box.com/folder/110862094043

Inputs for the three graphing programs (Work savings and recall.py, Histogram.py, and Log Scale.py), are three lists of tagger predictions--one list for abstract-screened articles, one for full-text screened, and one for included articles. These lists of predictions can be obtained through pipeline.py, though at present a small amount of manipulation of the pipleline.py output will be needed so that the files contain only the predictions.

## Issues:
1. Not getting predictions for before-1987 PMIDs or after 2019 PMIDs
2. Need access to multiple tables from the database. 
