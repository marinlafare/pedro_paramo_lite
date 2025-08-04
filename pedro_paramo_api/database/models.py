# pedro_paramo_api.database.models.py
from typing import Any
from sqlalchemy import Column, ForeignKey, Integer, String, Float, BigInteger, Table
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean
from pgvector.sqlalchemy import Vector
Base = declarative_base()


def to_dict(obj: Base) -> dict[str, Any]:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
class Version(Base):
    __tablename__ = "version"
    id = Column(Integer, primary_key=True, autoincrement=True)
    version_name = Column("version_name",String, unique = True, nullable=False)
    author = Column("author", String, nullable = False)
    year = Column('year', Integer, nullable = False)
    editorial = Column('editorial', String, nullable = False)
    ISBN = Column('ISBN',BigInteger, nullable = True)
    
    version_data = Column('version_data',String, nullable = False)
    raw_text = Column('raw_text',String, nullable = False)
    n_words = Column('n_words', Integer, nullable = False)
    n_paragraphs = Column('n_paragraphs', Integer, nullable =False)
    words_set = Column('word_set', String, nullable = False)
    raw_words = Column('raw_words', String, nullable = False)
    
class Paragraph(Base):
    __tablename__ = "paragraph"
    id = Column(Integer, primary_key=True, autoincrement=True)
    version_name = Column("version_name",String, unique = False, nullable=False)
    n_paragraph = Column('n_paragraph', Integer, nullable = False)
    text = Column("text", String, nullable=False)
    embedding = Column("embedding",Vector(768), nullable = False)
    n_words = Column('n_words', Integer, nullable = False)
    umap = Column('umap', Vector(3), nullable = False)    
