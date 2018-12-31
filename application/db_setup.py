# db_setup.py
from sqlalchemy import create_engine

from sqlalchemy.orm import scoped_session, sessionmaker

from sqlalchemy.ext.declarative import declarative_base
from application.config.config_file import postgres_conn

engine = create_engine(postgres_conn, convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()
def init_db():
    from models.models import *
    Base.metadata.create_all(bind=engine)
