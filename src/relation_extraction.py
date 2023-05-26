import argparse
import torch
from transformers import AutoTokenizer, AutoModel, BertTokenizer, TFBertModel

# Load the BioBERT model and tokenizer
model_name = "dmis-lab/biobert-base-cased-v1.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
# # Load the pre-trained BioBERT model
# model_name = "monologg/biobert_v1.1_pubmed"
# tokenizer = BertTokenizer.from_pretrained(model_name)
# model = TFBertModel.from_pretrained(model_name, from_pt=True)

# create a function to Pass the input through the model    
def get_relation_output(input_tokens):
    with torch.no_grad():
        output = model(**input_tokens)
    return output.last_hidden_state[:, 0, :]
    # return model(input_tokens)

# create a function to Extract the relation information from the output
def get_relation_representation(relation_output):
    classifier = torch.nn.Linear(relation_output.shape[-1], 2)
    logits = classifier(relation_output)
    prediction = torch.argmax(logits, dim=-1)
    return prediction
    # logits = relation_output.logits
    # # logits = logits.detach().numpy()
    # probs = tf.nn.softmax(logits, axis=-1)
    # prediction = tf.argmax(probs, axis=-1).numpy()[0]
    # return prediction

def get_relation_prediction(prediction):
    return False if prediction.item() == 0 else True

def main(input_file, output_file):
    # read data from csv file
    import pandas as pd
    df = pd.read_csv(input_file, encoding='utf-8')

    # for every sentence of every pubmed id
    for index, row in df.iterrows():
        # get the sentence
        sentence = row['sentence']

        # get entity1 and entity2
        entity1_name = row['entity1']
        entity2_name = row['entity2']

        input_tokens = tokenizer.encode_plus(entity1_name, entity2_name, return_tensors='pt')
        # input_tokens = tokenizer(sentence, entity1_name, entity2_name, return_tensors='pt')
        # input_tokens = {k: tf.convert_to_tensor(v.numpy()) for k, v in input_tokens.items()}

        relation_output = get_relation_output(input_tokens)
        representation = get_relation_representation(relation_output)
        prediction = get_relation_prediction(representation)
        
        with open(output_file, 'a') as f:
            f.write(f'{index},{sentence},{entity1_name},{entity2_name},{prediction}\n')

def extract_relation(entity_pairs):
    for entity_pair in entity_pairs:
        id_, sentence, entity1, entity2 = entity_pair
        input_tokens = tokenizer.encode_plus(entity1, entity2, return_tensors='pt')
        relation_output = get_relation_output(input_tokens)
        representation = get_relation_representation(relation_output)
        prediction = get_relation_prediction(representation)
        print(prediction)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help='input file', type=str, required=True)
    parser.add_argument('--output', '-o', help='output file', type=str, default='./output/output')
    args = parser.parse_args()

    if args.input.endswith('.csv'):
        main(args.input, args.output)

