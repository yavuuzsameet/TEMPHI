import requests
import xml.etree.ElementTree as ET
import pandas as pd

def retrieve_articles(query, max_results, query_no):
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    search_url = base_url + 'esearch.fcgi'
    fetch_url = base_url + 'efetch.fcgi'

    # Step 1: Perform a search to retrieve the PubMed IDs of the articles
    search_params = {
        'db': 'pubmed',
        'term': query,
        'retmax': max_results
    }
    try:
        search_response = requests.get(search_url, params=search_params)
        search_tree = ET.fromstring(search_response.text)
        id_list = [id_elem.text for id_elem in search_tree.iter('Id')]
    except:
        print("Error: Could not search articles from PubMed.")
        return []

    # Step 2: Retrieve the article details for each PubMed ID
    articles = {}
    doc_num = 0
    Total_n = len(id_list)
    for article_id in id_list:
        fetch_params = {
            'db': 'pubmed',
            'id': article_id,
            'rettype': 'xml',
            'retmode': 'xml'
        }

        try:
            print("Query No: {1}, Retrieving abstracts:{0}%".format(round(doc_num * 100 / Total_n), query_no), end="\r")
            doc_num += 1

            fetch_response = requests.get(fetch_url, params=fetch_params)
            fetch_tree = ET.fromstring(fetch_response.text)

            # Extract the title and abstract from the fetched XML
            abstract = fetch_tree.find('.//AbstractText').text
            title = fetch_tree.find('.//ArticleTitle').text

            articles[article_id] = {'title': title, 'abstract': abstract}
        except:
            print("Error: Could not fetch article details from PubMed.")
            continue

    return articles

def save(abstracts):
    save = pd.DataFrame.from_dict(abstracts, orient='index')
    save.to_csv('pubmed_abstracts.csv')

def main():
    querylist = ["cancer protein markers",
                "protein targets for cancer therapy",
                "coronavirus spike protein",
                "protein-protein interactions in diabetes",
                "neurodegenerative diseases protein aggregation",
                "protein biomarkers for cardiovascular diseases",
                "protein signaling in immune response",
                "proteins involved in Alzheimer's disease",
                "protein expression in autoimmune disorders",
                "protein targets for antiviral drugs",
                "protein interactions in Parkinson's disease",
                "proteomics of infectious diseases",
                "protein-protein networks in HIV infection",
                "proteins implicated in asthma pathogenesis",
                "protein-protein interactions in liver disease",
                "proteomic profiling of kidney cancer",
                "protein markers for autoimmune thyroid diseases",
                "protein regulation in inflammatory bowel disease",
                "proteins involved in lung cancer progression",
                "protein interactions in multiple sclerosis",
                "protein-protein interactions in heart disease"
                "proteomics of breast cancer",
                "protein markers for liver cirrhosis",
                "protein interactions in viral pathogenesis",
                "protein-protein networks in autoimmune disorders",
                "proteins involved in wound healing",
                "protein targets for antimicrobial therapy",
                "protein regulation in neurodevelopmental disorders",
                "proteomic profiling of pancreatic cancer",
                "protein markers for kidney disease",
                "protein interactions in rheumatoid arthritis",
                "proteins implicated in stroke pathophysiology",
                "protein-protein networks in metabolic syndrome",
                "proteomics of inflammatory lung diseases",
                "protein markers for ovarian cancer",
                "protein regulation in neurodegenerative diseases",
                "proteins involved in autoimmune encephalitis",
                "protein interactions in gastrointestinal disorders",
                "proteomic profiling of melanoma",
                "protein targets for regenerative medicine",
                "protein markers for prostate cancer",
                "protein interactions in inflammatory skin diseases",
                "proteins implicated in liver fibrosis",
                "protein-protein networks in kidney disease",
                "proteomics of cardiovascular diseases"]

    max_results = 500

    abstracts = {}

    for query in querylist:
        articles = retrieve_articles(query, max_results, querylist.index(query))
        abstracts.update(articles)

    save(abstracts)

if __name__ == '__main__':
    main()