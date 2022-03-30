import flask_sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from untracked_config.db_uri import DATABASE_URI

# set up sqlalchemy
engine = create_engine(DATABASE_URI, pool_pre_ping=True)

# add useful bits to the Base
Base = declarative_base()


def new_sqla_session():
    return Session(engine)
    # local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # return local_session
    # Session = scoped_session(local_session)
    # return Session


# Base.scoped_session = Session
# Base.query = Base.scoped_session.query_property()
# Base.sqla = sqlalchemy
# Base.engine = engine

fsa = flask_sqlalchemy.SQLAlchemy()
