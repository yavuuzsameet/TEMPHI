import pandas as pd
import os
import requests
import xml.etree.ElementTree as ET

PATH = os.path.join('../phisto', 'phisto_data.xlsx')
df = pd.read_excel(PATH)
df = df.dropna(subset=['Unique Pubmed_ID'])

abstracts = {}

for id in df['Unique Pubmed_ID']:
    try:
        xml = requests.get(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={id}&retmode=xml')
        tree = ET.ElementTree(ET.fromstring(xml.text))

        abstract = tree.find('PubmedArticle/MedlineCitation/Article/Abstract/AbstractText').text
        title = tree.find('PubmedArticle/MedlineCitation/Article/ArticleTitle').text
    except:
        print(int(id))
        continue

    abstracts[int(id)] = {'title': title, 'abstract': abstract}

save = pd.DataFrame.from_dict(abstracts, orient='index')
save.to_csv('abstracts.csv')
    
