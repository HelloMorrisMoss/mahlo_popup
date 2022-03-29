import flask_sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session

from untracked_config.db_uri import DATABASE_URI

# set up sqlalchemy
engine = create_engine(DATABASE_URI, pool_pre_ping=True)

Base = declarative_base()


class SelfSessionBase:
    _self_engine = engine
    _scoped_session = None
    query = scoped_session.query_property()

    @classmethod
    def new_session(cls):
        local_session = sessionmaker(autocommit=False, autoflush=False, bind=cls._self_engine)
        Session = scoped_session(local_session)
        return Session

    # @property
    # def query(self):
    #     return self.scoped_session.query_property()

    @property
    def scoped_session(self):
        if not self._scoped_session:
            self._scoped_session = self.new_session()

        return self._scoped_session


# add useful bits to the Base
# Base.scoped_session = Session
# Base.query = Base.scoped_session.query_property()
# Base.sqla = sqlalchemy
# Base.engine = engine

fsa = flask_sqlalchemy.SQLAlchemy()
