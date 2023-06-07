from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import text
from pydantic import BaseModel
from pipeline import run_pipeline
from database_operations import get_relation_by_id, get_db, create_relation, get_all_relations, update_relation, get_all_protein_ids, get_relations_by_protein_ids
from typing import Optional

app = FastAPI()

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. Change this in production.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods.
    allow_headers=["*"],  # Allows all headers.
)

class Article(BaseModel):
    title: str
    abstract: str
    pubmed_id: int = 0

class Relation(BaseModel):
    id: Optional[int] = None
    pubmed_id: int
    protein_1: str
    protein_2: str
    sentence: str
    protein_1_id: Optional[str] = None
    protein_2_id: Optional[str] = None

security = HTTPBearer()

def validate_token(token: HTTPAuthorizationCredentials = Depends(security)):
    SECRET_TOKEN = "12345"
    if token.credentials != SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return token

@app.post("/")
async def run_article_pipeline(article: Article):
    return run_pipeline(article)


@app.post("/add-article", dependencies=[Depends(validate_token)])
async def run_pipeline_and_save(article: Article, db = Depends(get_db)):
    relations = run_pipeline(article)
    for relation in relations["relations"]:
        create_relation(db, relation)

    return relations

@app.get("/relation/{relation_id}")
def read_relation_endpoint(relation_id: int, db: Session = Depends(get_db)):
    relation = get_relation_by_id(db, relation_id)
    if relation is None:
        raise HTTPException(status_code=404, detail="Relation not found.")
    else:
        return {"relations": [relation]}

@app.post("/relation/", dependencies=[Depends(validate_token)])
def create_relation_endpoint(relation: Relation, db = Depends(get_db)):
    if create_relation(db, relation):
        return {"message": "Item created successfully."}
    else:
        raise HTTPException(status_code=400, detail="Error occurred during insertion.")

@app.get("/relations/")
def read_all_relations(db: Session = Depends(get_db)):
    relations = get_all_relations(db)
    if relations is None:
        raise HTTPException(status_code=404, detail="No relations found.")
    else:
        return {"relations": relations}

@app.put("/relation/{relation_id}", dependencies=[Depends(validate_token)])
def update_relation_endpoint(relation_id: int, relation: Relation, db: Session = Depends(get_db)):
    if update_relation(db, relation_id, relation):
        return {"message": f"Relation {relation_id} updated successfully."}
    else:
        raise HTTPException(status_code=400, detail="Error occurred during update.")

@app.get("/protein-ids")
def get_protein_ids_endpoint(db: Session = Depends(get_db)):
    protein_ids = get_all_protein_ids(db)
    if protein_ids is not None:
        return protein_ids
    else:
        raise HTTPException(status_code=404, detail="Error occurred during retrieval.")

@app.get("/relations-by-protein-ids")
def get_relations_endpoint(protein_1_id: Optional[str] = None, protein_2_id: Optional[str] = None, db: Session = Depends(get_db)):
    relations = get_relations_by_protein_ids(db, protein_1_id, protein_2_id)
    if relations is not None:
        return {"relations": relations}
    else:
        raise HTTPException(status_code=404, detail="Relations not found.")
