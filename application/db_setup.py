# db_setup.py
from application.config.config_file import postgres_conn
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(postgres_conn, convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    from models.models import *
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
