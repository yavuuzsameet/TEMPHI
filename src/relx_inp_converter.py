from itertools import combinations
import pandas as pd
import argparse
import os
from name2uniprot import name2uniprot as n2u 

def process_papers(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
        
    papers = content.strip().split("\n\n")  # split by two newlines
    processed_papers = []
    
    doc_num = 0
    total = len(papers)

    uniprot = {}

    for paper in papers:
        lines = paper.split('\n')
        title = ''
        abstract = ''
        id_ = ''
        entities = []

        print("Processing Papers:{0}%".format(round(doc_num * 100 / total)), end="\r")
        doc_num+=1

        for line in lines:
            if '|t|' in line:
                id_, title = line.split('|t|', 1)
                id_ = id_.strip()  # remove whitespace
                title = title.strip()
            elif '|a|' in line:
                id_, abstract = line.split('|a|', 1)
                id_ = id_.strip()  # remove whitespace
                abstract = abstract.strip()
            else:
                entity_info_parts = line.strip().split('\t')
                if len(entity_info_parts) == 5:
                    entity_id, start_index, end_index, name, type_ = entity_info_parts
                    # We assume that the entity_id matches the paper id
                    assert entity_id == id_
                    if type_ == 'Gene':
                        # Get the uniprot id
                        if name in uniprot: uniprot_id = uniprot[name]
                        else:
                            uniprot_id = n2u(name)
                            uniprot[name] = uniprot_id
                        
                        entities.append((start_index, end_index, name, type_, uniprot_id))
        
        combined_text = f"{title} {abstract}"
        processed_papers.append((id_, combined_text, entities))
    
    return processed_papers

def find_sentences_with_indexes(processed_paper):
    id_, text, entities = processed_paper
    sentences = []

    start_index = 0
    for sentence in text.split('. '):
        end_index = start_index + len(sentence)
        sentences.append((start_index, end_index, sentence))
        start_index = end_index + 2  # adjust for ". " delimiter

    return sentences

def replaceEntitiesWithTags(sentence, entity1_start, entity1_end, entity2_start, entity2_end):
    return sentence[:entity1_start] + '@GENE$' + sentence[entity1_end:entity2_start] + '@GENE$' + sentence[entity2_end:]

def generate_entity_pairs(processed_paper, sentences):
    id_, _, entities = processed_paper

    # Map each entity to the sentence it appears in
    entities_in_sentences = {}
    for entity in entities:
        entity_start = int(entity[0])
        entity_end = int(entity[1])
        for sentence_start, sentence_end, sentence in sentences:
            if sentence_start <= entity_start and entity_end <= sentence_end:
                if (sentence_start, sentence_end, sentence) in entities_in_sentences:
                    entities_in_sentences[(sentence_start, sentence_end, sentence)].append(entity)
                else:
                    entities_in_sentences[(sentence_start, sentence_end, sentence)] = [entity]
                break

    # Generate all pairs of entities that appear in the same sentence
    entity_pairs = []
    for sentence, entities in entities_in_sentences.items():
        for entity1, entity2 in combinations(entities, 2):
            new_sentence = replaceEntitiesWithTags(sentence[2], int(entity1[0])-int(sentence[0]), int(entity1[1])-int(sentence[0]), int(entity2[0])-int(sentence[0]), int(entity2[1])-int(sentence[0]))
            entity_pairs.append((id_, new_sentence, entity1[2], entity1[4], entity2[2], entity2[4]))

    return entity_pairs

def export_to_excel(entity_pairs, output_file):
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir) and len(output_dir) > 0:
        os.makedirs(output_dir)

    df = pd.DataFrame(entity_pairs, columns=['id', 'sentence', 'entity1_name', 'entity1_uniprotid', 'entity2_name', 'entity2_uniprotid'])
    df.to_csv(output_file, index=False)

def get_all_entity_pairs(input_path):
    processed_papers = process_papers(input_path)

    entity_pairs_all = []
    doc_num = 0
    total = len(processed_papers)
    for processed_paper in processed_papers:
        print("Generating Entities:{0}%".format(round(doc_num * 100 / total)), end="\r")
        doc_num+=1
        sentences = find_sentences_with_indexes(processed_paper)
        entity_pairs = generate_entity_pairs(processed_paper, sentences)
        entity_pairs_all.extend(entity_pairs)

    return entity_pairs_all

def main():

    # Creating an argument parser
    parser = argparse.ArgumentParser()

    # Adding arguments
    parser.add_argument('--input', '-i',  type=str, help='Input File', required = True)
    parser.add_argument('--output', '-o',  type=str, help='Output File', default = './output/entity_pairs.csv')

    # Parsing the arguments
    args = parser.parse_args()

    entity_pairs_all = get_all_entity_pairs(args.input)

    export_to_excel(entity_pairs_all, args.output)

if __name__ == "__main__":
    main()