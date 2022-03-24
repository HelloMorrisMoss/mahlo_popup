# from fresk.models.defect import DefectModel
# from fresk.models.lam_operator import OperatorModel
#
# d1 = DefectModel.new_defect()


import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# from untracked_config.db_uri import DATABASE_URI

DATABASE_URI = '''sqlite:///:memory:'''

# set up sqlalchemy
engine = create_engine(DATABASE_URI, pool_pre_ping=True)
local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(local_session)

Base = declarative_base()

# add useful bits to the Base
Base.scoped_session = Session
Base.query = Base.scoped_session.query_property()
Base.sqla = sqlalchemy
Base.engine = engine


class Tab1(Base):
    __tablename__ = 'tab1'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)


class Tab2(Base):
    __tablename__ = 'tab2'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)


pass
