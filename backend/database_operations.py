from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "sqlite:///./data.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_relation(db, relation):
    query = text("INSERT INTO relation (id, pubmed_id, protein_1, protein_2, sentence, protein_1_id, protein_2_id) VALUES (:id, :pubmed_id, :protein_1, :protein_2, :sentence, :protein_1_id, :protein_2_id)")
    parameters = {"id": relation.id, "pubmed_id": relation.pubmed_id, "protein_1": relation.protein_1, "protein_2": relation.protein_2, "sentence": relation.sentence, "protein_1_id": relation.protein_1_id, "protein_2_id": relation.protein_2_id}
    try:
        db.execute(query, parameters)
        db.commit()
        return True
    except SQLAlchemyError:
        return False

def get_relation_by_id(db, item_id):
    query = text("SELECT * FROM relation WHERE id = :item_id")
    parameters = {"item_id": item_id}
    try:
        result = db.execute(query, parameters)
        item = result.fetchone()
        return item._asdict() if item else None
    except SQLAlchemyError:
        return None

def get_all_relations(db):
    query = text("SELECT * FROM relation")
    try:
        result = db.execute(query)
        relations = result.fetchall()
        return [relation._asdict() for relation in relations]
    except SQLAlchemyError:
        return None

def update_relation(db, relation_id, relation):
    query = text(
        """
        UPDATE relation 
        SET 
            pubmed_id = :pubmed_id, 
            protein_1 = :protein_1,
            protein_2 = :protein_2,
            sentence = :sentence, 
            protein_1_id = :protein_1_id,
            protein_2_id = :protein_2_id
        WHERE id = :relation_id
        """
    )
    parameters = {
        "relation_id": relation_id,
        "pubmed_id": relation.pubmed_id,
        "protein_1": relation.protein_1,
        "protein_2": relation.protein_2,
        "sentence": relation.sentence,
        "protein_1_id": relation.protein_1_id,
        "protein_2_id": relation.protein_2_id
    }
    try:
        db.execute(query, parameters)
        db.commit()
        return True
    except SQLAlchemyError:
        return False

def get_all_protein_ids(db):
    query_1 = text("SELECT DISTINCT protein_1_id FROM relation WHERE protein_1_id IS NOT NULL")
    query_2 = text("SELECT DISTINCT protein_2_id FROM relation WHERE protein_2_id IS NOT NULL")
    try:
        result_1 = db.execute(query_1)
        result_2 = db.execute(query_2)

        protein_1_ids = [row[0] for row in result_1]
        protein_2_ids = [row[0] for row in result_2]

        return {"protein_1_ids": protein_1_ids, "protein_2_ids": protein_2_ids}
    except SQLAlchemyError:
        return None

def get_relations_by_protein_ids(db, protein_1_id, protein_2_id):
    if protein_2_id and protein_1_id:
        query = text("SELECT * FROM relation WHERE protein_1_id = :protein_1_id AND protein_2_id = :protein_2_id")
        parameters = {"protein_1_id": protein_1_id, "protein_2_id": protein_2_id}
    elif protein_2_id:
        query = text("SELECT * FROM relation WHERE protein_2_id = :protein_2_id")
        parameters = {"protein_2_id": protein_2_id}
    elif protein_1_id:
        query = text("SELECT * FROM relation WHERE protein_1_id = :protein_1_id")
        parameters = {"protein_1_id": protein_1_id}
    else:
        return None

    try:
        result = db.execute(query, parameters)
        relations = result.fetchall()
        return [relation._asdict() for relation in relations]
    except SQLAlchemyError:
        return None
