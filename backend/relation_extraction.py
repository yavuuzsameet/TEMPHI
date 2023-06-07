import numpy as np
import pandas as pd

import torch

from transformers import BertTokenizer, BertForSequenceClassification, AdamW, BertConfig
from torch.utils.data import TensorDataset, random_split, DataLoader, RandomSampler, SequentialSampler
from transformers import get_linear_schedule_with_warmup

from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

path='biobert/'

device = torch.device('cpu')

SEED = 42

torch.manual_seed(SEED)
torch.backends.cudnn.deterministic = True

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

model = BertForSequenceClassification.from_pretrained(
    'bert-base-uncased',
    num_labels=2,
    output_attentions=False,
    output_hidden_states=False
)

device = torch.device('cpu')
model.cpu()

def predict(model, sentence, tokenizer, maxlen=512):
    # prepare the sentence
    model.load_state_dict(torch.load('biobert/best_model_ppi.pt', map_location=torch.device('cpu')))

    model.eval()
    inputs = tokenizer.encode_plus(
        sentence,
        add_special_tokens=True,
        max_length=maxlen,
        padding='max_length',
        truncation=True,
        return_attention_mask=True,
        return_tensors='pt'
    )

    # run the model
    with torch.no_grad():
        output = model(
            inputs['input_ids'].to(device),
            token_type_ids=None,
            attention_mask=inputs['attention_mask'].to(device)
        )

    # interpret the model's output
    probabilities = torch.nn.functional.softmax(output.logits, dim=-1)
    predicted_class = torch.argmax(probabilities).item()
    
    if predicted_class == 0:
        return 0
    else:
        return 1

def is_relation(sentence):
    return predict(model, sentence, tokenizer)
