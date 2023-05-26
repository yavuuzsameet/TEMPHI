import pandas as pd
import argparse

def read_phisto_data(phisto_file_path):
    df = pd.read_csv(phisto_file_path, encoding='utf-8', sep=';')
    return df

def create_uniprot_mapping(df):
    uniprot_mapping = {}

    count = 0
    total = len(df)

    for index, row in df.iterrows():
        print("Mapping:{0}%".format(round(count * 100 / total)), end="\r")
        count += 1

        pathogen_protein_uniprot_id = row['Pathogen_Protein_Uniprot_ID']
        host_protein_uniprot_id = row['Human_Protein_Uniprot_ID']

        if pathogen_protein_uniprot_id not in uniprot_mapping: uniprot_mapping[pathogen_protein_uniprot_id] = set([host_protein_uniprot_id])
        else: uniprot_mapping[pathogen_protein_uniprot_id].add(host_protein_uniprot_id)

        if host_protein_uniprot_id not in uniprot_mapping: uniprot_mapping[host_protein_uniprot_id] = set([pathogen_protein_uniprot_id])
        else: uniprot_mapping[host_protein_uniprot_id].add(pathogen_protein_uniprot_id)
    
    return uniprot_mapping

def read_entity_pairs(entity_pairs_file_path):
    df = pd.read_csv(entity_pairs_file_path, encoding='utf-8', keep_default_na=False)
    return df

def label_entity_pairs_single(df, relations):
    for index, row in df.iterrows():
        entity1_uniprot_id = row['entity1_uniprotid']
        entity2_uniprot_id = row['entity2_uniprotid']

        if entity1_uniprot_id != '' and entity2_uniprot_id != '':
            if entity1_uniprot_id in relations and entity2_uniprot_id in relations[entity1_uniprot_id] or entity2_uniprot_id in relations and entity1_uniprot_id in relations[entity2_uniprot_id]:
                df.loc[index, 'label'] = '1'
            else: df.loc[index, 'label'] = '0'
        else: df.loc[index, 'label'] = 'X'
    return df

def label_entity_pairs_multiple(df, relations):
    count = 0
    total = len(df)

    for index, row in df.iterrows():
        print("Labeling:{0}%".format(round(count * 100 / total)), end="\r")
        count += 1

        entity1_uniprot_id_list = eval(row['entity1_uniprotid'])
        entity2_uniprot_id_list = eval(row['entity2_uniprotid'])

        if len(entity1_uniprot_id_list) > 0 and len(entity2_uniprot_id_list) > 0:
            labeled = False
            for entity1_uniprot_id in entity1_uniprot_id_list:
                for entity2_uniprot_id in entity2_uniprot_id_list:
                    if entity1_uniprot_id in relations and entity2_uniprot_id in relations[entity1_uniprot_id] or entity2_uniprot_id in relations and entity1_uniprot_id in relations[entity2_uniprot_id]:
                        df.loc[index, 'label'] = '1'
                        labeled = True
                        break
                if labeled: break
            if not labeled: df.loc[index, 'label'] = '0'
        else: df.loc[index, 'label'] = 'X'
    return df

def create_csv(df, file_name):
    df.to_csv(file_name, encoding='utf-8', index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--phisto', '-p', type=str, help='Path to the phisto file')
    parser.add_argument('--single', '-s', type=str, help='Path to the entity pairs file')
    parser.add_argument('--multiple', '-m', type=str, help='Path to the entity pairs file')
    args = parser.parse_args()

    phisto_df = read_phisto_data(args.phisto)
    relations = create_uniprot_mapping(phisto_df)

    entity_pairs_df = read_entity_pairs(args.single) if args.single else read_entity_pairs(args.multiple)

    labeled_df = label_entity_pairs_single(entity_pairs_df, relations) if args.single else label_entity_pairs_multiple(entity_pairs_df, relations)

    create_csv(labeled_df, './output/labeled_dataset_single.csv') if args.single else create_csv(labeled_df, './output/labeled_dataset_multiple.csv')


    