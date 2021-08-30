# MCTagger-eval
Multi-Tagger work savings analysis

# new_pipline_v3.py
Retrieves Multi-Tagger predictions for specified study designs.    

Inputs:  
  -List of PMIDs that were abstract screened.   
  -List of PMIDs that were full-text screened.   
  -List of PMIDs that were included in the review.   

Outputs:  
  -List of the Multi-Tagger prediction scores for each PMID. 
  
# PubMed data collection.py
Retreives MeSH terms and publication types from PubMed API.

Inputs:  
  -List of PMIDs for each review.   

Outputs:  
  -List of PMIDs, their MeSH terms, and their publication types.   
  -List of PMIDs that were not found in PubMed.   

# DERP-reports-pubmed_data_web_rct_data.py
Performs calculations and compiles statistics for work savings analysis.

Inputs:  
  -PMIDs and tagger predictions output from new_pipeline_v3.py.   
  -List of MeSH terms and publication types for each PMID from 'PubMed data collection.py'.   
  -RCT scores pulled from the web RCT Tagger API.   
  -List of tagger prediction thresholds for each study design.   
  -List of included/relevant study designs for each review.   
  
 Outputs:    
  -Descriptive statistics tables (one based on filtering with Multi-Tagger alone; and one based on Multi-Tagger, web RCT Tagger, and MeSH terms and publication types).   
  -Graphs (number filtered out during full-text screening, percentage filtered out during full-text screening, number filtered out during abstract screening, percentage filtered out during abstract screening).   
  -List of included articles that were filtered out.   
  -Results files including all relevant predictions, MeSH categories, and publication types for each PMID.   
