import os

import flask_sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session

from untracked_config.db_uri import DATABASE_URI
from untracked_config.development_node import ON_DEV_NODE

os.environ['SQLALCHEMY_WARN_20'] = "true"

# engine = create_engine(DATABASE_URI, connect_args={'check_same_thread': False})

echo = True if ON_DEV_NODE else False
engine = create_engine(DATABASE_URI, pool_pre_ping=True, echo=echo, future=True)
local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()
Session = scoped_session(local_session)
Base.session = Session
Base.query = Session.query_property()

fsa = flask_sqlalchemy.SQLAlchemy()
