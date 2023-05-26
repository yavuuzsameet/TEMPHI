from pubtator_generator import to_pubtator
from relation_extraction import extract_relation
import relx_inp_converter
import os
import subprocess

def print_pubtator(pubtator):
    if not os.path.exists('./temp'):
        os.makedirs('./temp')

    with open('./temp/pbt', 'w') as f:
        f.write(pubtator)
    
def pipeline(title, abstract):
    # convert to pubtator
    pubtator = to_pubtator(title, abstract)
    print_pubtator(pubtator)

    # apply ner
    subprocess.run(['python3', 'AIONER_Run.py', '-i', '../../../src/temp/', '-o', '../../../src/nerout'], cwd='../nerenv/AIONER/src')

    # get entity pairs
    entity_pairs = relx_inp_converter.get_all_entity_pairs('./nerout/pbt')

    # extract relation
    prediction = extract_relation(entity_pairs)
    print(prediction)


if __name__=='__main__':
    title = "Association of the human papillomavirus type 16 E7 oncoprotein with the 600-kDa retinoblastoma protein-associated factor, p600."
    abstract = "The human papillomavirus type 16 E7 oncoprotein binds and inactivates the retinoblastoma protein, pRB. We have identified a cellular protein, p600, that binds to the E7 protein and to pRB. The p600 protein is a 600-kDa protein that is localized to the nucleus and is associated with the nuclear matrix. The p600 protein is phosphorylated in vivo and in vitro by the cyclin A-dependent protein kinase, cdk2. The p600 protein is also a substrate for the E7-associated protein phosphatase activity. The p600 protein may be a target for the E7-associated protein phosphatase activity and may be involved in the E7-mediated transformation of cells."

    pipeline(title, abstract)