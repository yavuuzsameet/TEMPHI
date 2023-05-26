import requests, json
import argparse

def name2uniprot(protein_name):
    search_url = "https://rest.uniprot.org/uniprotkb/search?query=(reviewed:true)%20AND%20(protein_name:{0})&fields=accession".format(protein_name)
    data = json.loads(requests.get(search_url).text)
    try:
        uniprot_id = [result['primaryAccession'] for result in data['results']]
    except:
        uniprot_id = []
    return uniprot_id

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--protein_name', '-p', type=str, help='Name of the protein to search for')
    args = parser.parse_args()
    print(name2uniprot(args.protein_name))
