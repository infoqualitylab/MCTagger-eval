---
title: "R Tagger Pipeline"
author: "Author: Brandi P Smith"
date: "3/3/2020"
output: html_document
---

## Purpose
The purpose of this pipeline is to create a more user-friendly approach to extracting tagger predictions from a given set of PubMed IDs or a bibliography file such as .ris or .xml. 

## File descriptions:
1. OCR_RCT_START_IDS.txt : Starting PubMed IDs from protocol search 
2. OCR_RCT_RET_ABS_IDS.txt : Retrieved PubMed IDs from retrieved abstracts for review 
3. pipeline.R : R code which extracts tagger predictions from established SQL database/aggregated database.
4. Rct_Tagger_Aggregate.R : R code which aggregates RCT csv files into a large dataframe which will be used seperate from SQL Databse RCT Taggers.