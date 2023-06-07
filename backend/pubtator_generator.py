import argparse
import pandas as pd

def to_pubtator(title, abstract, id=0):
    pubtator_string = ''
    pubtator_string += f'{id}|t|{title}'
    pubtator_string += f'\n'
    pubtator_string += f'{id}|a|{abstract}'
    pubtator_string += f'\n'
    return pubtator_string

def generate_pubtator_from_csv(inp, outp):
    df = pd.read_csv(inp, index_col=0)

    papers = ''
    for id, paper in df.iterrows():
        paper = to_pubtator(id, paper.title, paper.abstract)
        papers += paper + '\n'

    return papers
        

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help='input file', type=str, required=True)
    parser.add_argument('--output', '-o', help='output file', type=str, default='./output/output')
    args = parser.parse_args()

    if args.input.endswith('.csv'):
        pubtator_string = generate_pubtator_from_csv(args.input, args.output)
        with open(args.output, 'w') as f:
            f.write(pubtator_string)
