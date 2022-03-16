import flask_sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session

from untracked_config.db_uri import DATABASE_URI

# engine = create_engine(DATABASE_URI, connect_args={'check_same_thread': False})
engine = create_engine(DATABASE_URI)  # , connect_args={'check_same_thread': False})
local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Session = scoped_session(local_session)
Base.scoped_session = Session
Base.query = Base.scoped_session.query_property()

fsa = flask_sqlalchemy.SQLAlchemy()
