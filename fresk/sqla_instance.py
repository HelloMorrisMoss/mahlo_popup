import flask_sqlalchemy
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session

from untracked_config.db_uri import DATABASE_URI

# set up sqlalchemy
engine = create_engine(DATABASE_URI, pool_pre_ping=True)
Base = declarative_base()

active_sessions = []


def new_session(model_class):
    local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    model_class.scoped_session = scoped_session(local_session)

    # add useful bits to the model_class
    model_class.query = model_class.scoped_session.query_property()
    model_class.sqla = sqlalchemy
    model_class.engine = engine


fsa = flask_sqlalchemy.SQLAlchemy()
