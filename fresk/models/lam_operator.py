import sqlalchemy as fsa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session

from fresk.helpers import jsonizable
from log_setup import lg
from untracked_config.db_uri import DATABASE_URI

# engine = create_engine(DATABASE_URI, connect_args={'check_same_thread': False})
engine = create_engine(DATABASE_URI)  # , connect_args={'check_same_thread': False})
local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.scoped_session = scoped_session(local_session)
Base.query = Base.scoped_session.query_property()


class OperatorModel(Base):
    """A sqlalchemy model for laminator operators."""
    __tablename__ = 'lam_operator_list'

    id = fsa.Column(fsa.Integer, primary_key=True)
    first_name = fsa.Column(fsa.String, default='')
    last_name = fsa.Column(fsa.String, default='')
    initials = fsa.Column(fsa.String, default='', unique=True)
    lam_1_certified = fsa.Column(fsa.Boolean, server_default='''False''')
    lam_2_certified = fsa.Column(fsa.Boolean, server_default='''False''')
    date_added = fsa.Column(fsa.TIMESTAMP(timezone=True), server_default=fsa.func.now())
    date_removed = fsa.Column(fsa.TIMESTAMP(timezone=True))

    flask_sqlalchemy_instance = fsa

    def __init__(self, **kwargs):
        # for the kwargs provided, assign them to the corresponding columns
        self_keys = OperatorModel.__dict__.keys()
        for kw, val in kwargs.items():
            if kw in self_keys:
                setattr(self, kw, val)

    @classmethod
    def new_operator(cls, first_name, last_name, lam_1_certified=None, lam_2_certified=None):
        new_op = OperatorModel(first_name=first_name,
                               last_name=last_name,
                               lam_1_certified=lam_1_certified,
                               lam_2_certified=lam_2_certified)
        # add unique initials
        initial_characters = 1
        initials = f'{first_name[0:initial_characters]}{last_name[0]}'
        while cls.check_for_initials(initials):
            initial_characters += 1
            initials = f'{first_name[0:initial_characters]}{last_name[0]}'
        new_op.initials = initials
        new_op.save_to_database()
        lg.info('New operator created: %s', new_op.__dict__)
        return new_op

    @classmethod
    def get_active_operators(cls, lam_number=None):
        """Get a list of         """

        if lam_number is None:
            return cls.query.filter(OperatorModel.date_removed == None).all()
        else:
            certified_lam_dict = {1: OperatorModel.lam_1_certified, 2: OperatorModel.lam_2_certified}
            certified_lam_dict[0] = certified_lam_dict[1]  # for development
            lam_column_dict = certified_lam_dict[lam_number]
            return cls.query.filter(OperatorModel.date_removed == None).filter(lam_column_dict).all()

    @classmethod
    def check_for_initials(cls, initials):
        return cls.query.filter(cls.initials == initials).all()

    def jsonizable(self):
        return jsonizable(self)

    def save_to_database(self):
        """Save the changed to defect to the database."""
        self.scoped_session.add(self)
        self.scoped_session.commit()


if __name__ == '__main__':
    OperatorModel.new_operator(first_name='Kyle', last_name='Derosa')
    # print(OperatorModel.query.all())

# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from untracked_config.db_uri import DATABASE_URI
#
# SQLALCHEMY_DATABASE_URL = DATABASE_URI
#
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base

# OperatorModel.__table__.create(SessionLocal.object_session)
# Session = sessionmaker(bind=engine)
# sesn = Session()
# sesn = local_session
# with local_session() as sesn:

# # to load the operators in from a manually created json file
# from sqlalchemy.orm import Session
#
# with Session(engine) as sesn:
#     # OperatorModel.__table__.create(sesn.bind, checkfirst=True)
#     # sesn.close()
#
#     import json
#     import datetime
#
#     final_list = []
#     fp = r'C:\Users\lmcglaughlin\PycharmProjects\mahlo_popup\untracked_config\lam_operators.json'
#     with open(fp, 'r') as jf:
#         ld = json.load(jf)
#     joined = {}
#     for ln in (1, 2):
#         for first_name, last_name in ld[str(ln)]:
#             this_dict = {
#                 'first_name': first_name,
#                 'last_name': last_name,
#                 f'lam_{ln}_certified': True,
#                 'date_added': datetime.datetime.now(),
#                 'initials': first_name[0] + last_name[0],
#                 }
#             name_tuple = (first_name, last_name)
#             try:
#                 joined[name_tuple].update(this_dict)
#             except KeyError:
#                 joined[name_tuple] = this_dict
#
#     print(joined)
#     OperatorModel.query = sesn.query()
#     for k, v in joined.items():
#         om = OperatorModel(**v)
#         initials_number = 1
#         while sesn.query(OperatorModel).filter(OperatorModel.initials == om.initials).all():
#             om.initials = om.first_name[:initials_number + 1] + om.last_name[0]
#             initials_number += 1
#
#         sesn.add(om)
#         sesn.commit()
# #         # try:
# #         #     sesn.commit()
# #         # except fsa.exc.IntegrityError:
# #         #     om.initials = om.initials +
