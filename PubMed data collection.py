#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import requests
import lxml.etree
import glob
import pandas as pd
import time
import numpy as np


# ## Set working directory

# In[2]:


os.chdir('PATH TO DIRECTORY')


# ## Import files and collect data

# In[3]:


# Grab the file paths
files = glob.glob('./multitagger_scores/*_v2.csv')

print(len(files))
print('\n'.join(files)) # Should have 10 file paths (10 DERP Multitagger score files) printed out


# In[4]:


not_in_pubmed = [['DERP', 'PMIDs']] # For saving PMIDs do not have PubMed data. # Check these PMIDs.

# Iterate over DERP reports. For each PMID in each DERP, collect MeSH and publication types from PubMed.
for file in files:
    f_name = file.split('/')[-1].replace('_scores_v2.csv', '')
    pmids = pd.read_csv(file, usecols=['PMID'])['PMID'].tolist()
    pmids = [str(pmid) for pmid in pmids]
    n_pmids = len(pmids)
    n_pubs_collected = 0
    
    df = [['PMID', 'Pub_type', 'MeSH']]
    
    # PubMed takes up to 200 PMIDs per query. Split PIMDs into chunks
    for i in np.arange(0, n_pmids, 200):
        
        if i+200 > n_pmids:
            chunk_pmid = pmids[i:]
        else:
            chunk_pmid = pmids[i:i+200]
        
        pmids_string = ','.join(chunk_pmid)

        api_link = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}&retmode=xml".format(pmids_string)

        response = requests.get(api_link)
        tree = lxml.etree.fromstring(response.text)

        pubs = tree.xpath('.//PubmedArticle')
        
        n_pubs_collected += len(pubs)
    
        for pub in pubs:

            pmid = pub.xpath('./MedlineCitation/PMID')[0].text
            pmid_node = pub.xpath('./MedlineCitation/PMID')
            if len(pmid_node) > 1:
                print(pmid, 'More than one PMID node, CHECK!')

            # Get publication type
            pt = []
            pt_nodes = pub.xpath('.//PublicationTypeList/descendant::text()')
            for pt_txt in pt_nodes:
                pt_txt = pt_txt.strip()
                if len(pt_txt) > 0 and pt_txt not in pt:
                    pt.append(pt_txt)
            
            # Get MeSH
            mesh = []
            mesh_nodes = pub.xpath('.//MeshHeading/descendant::text()')
            for mesh_txt in mesh_nodes:
                mesh_txt = mesh_txt.strip()
                if len(mesh_txt) > 0 and mesh_txt not in mesh:
                    mesh.append(mesh_txt)

            df.append([pmid, ';'.join(pt), ';'.join(mesh)])
        
        time.sleep(0.5)
    
    df = pd.DataFrame(df[1:], columns=df[0])
    
    df_pmids = df['PMID'].astype(str).tolist()
    
    diff = list(set(pmids)-set(df_pmids)) # Find the PMIDs in a DERP report that do not have PubMed data. 
    if len(diff) > 0:
        not_in_pubmed.append([f_name, ';'.join(diff)])
    
    print(f_name, n_pmids, n_pubs_collected, diff)
    
    df.set_index('PMID').to_csv('./PT_and_MeSH/{}_PubMed_data.tsv'.format(f_name), sep='\t')
    
not_in_pubmed = pd.DataFrame(not_in_pubmed[1:], columns=not_in_pubmed[0])  
not_in_pubmed.set_index('DERP').to_csv('./PT_and_MeSH/PMIDs_not_in_PubMed.csv')


# In[ ]:
