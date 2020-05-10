## Purpose
The purpose of this pipeline is to create a more user-friendly approach to extracting tagger predictions from a given set of PubMed IDs or a bibliography file such as .ris or .xml. 

## File descriptions:
1. OCR_RCT_START_IDS.txt : Starting PubMed IDs from protocol search 
2. OCR_RCT_RET_ABS_IDS.txt : Retrieved PubMed IDs from retrieved abstracts for review 
3. pipeline.R : R code which extracts tagger predictions from established SQL database/aggregated database.
4. pipeline.py: python code which has similar purpose as R pipeline, but has better data visualization options
5. Work savings and recall.py : Reads files with lists of predictions from abstract-screened, full-text screened, and included articles, and creates a graph of the work savings and recall from both screening levels.

## Issues:
1. Not getting predictions for before-1987 PMIDs or after 2019 PMIDs
2. Need access to multiple tables from the database. 
