from pydantic import BaseModel
from pubtator_generator import to_pubtator
from typing import Optional
from relx_inp_converter import get_all_entity_pairs_with_string
from relation_extraction import is_relation
from nerenv.AIONER.src.AIONER_Run import entity_tagger

class Article(BaseModel):
    title: str
    abstract: str
    id: int

class Relation(BaseModel):
    id: Optional[int] = None
    pubmed_id: int
    protein_1: str
    protein_2: str
    sentence: str
    protein_1_id: Optional[str] = None
    protein_2_id: Optional[str] = None

def run_pipeline(article: Article):

    # Get title and abstract
    title = article.title
    abstract = article.abstract
    pubmed_id = article.pubmed_id

    pubtator = to_pubtator(title, abstract, pubmed_id)

    # NER
    NER_entities = entity_tagger(pubtator)

    entities = get_all_entity_pairs_with_string(NER_entities)

    relations = []

    for entity in entities:
        if is_relation(entity[2]):
            relation = Relation(pubmed_id = entity[0], sentence = entity[1][2], protein_1 = entity[3], protein_1_id = entity[4], protein_2 = entity[5], protein_2_id = entity[6])
            relations.append(relation)

    return {"relations": relations}