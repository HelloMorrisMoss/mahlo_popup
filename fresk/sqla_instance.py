import flask_sqlalchemy
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session

from untracked_config.db_uri import DATABASE_URI

# set up sqlalchemy
engine = create_engine(DATABASE_URI, pool_pre_ping=True)
local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Session = scoped_session(local_session)

# add useful bits to the Base
Base.scoped_session = Session
Base.query = Base.scoped_session.query_property()
Base.sqla = sqlalchemy
Base.engine = engine

fsa = flask_sqlalchemy.SQLAlchemy()
