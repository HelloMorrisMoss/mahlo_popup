import sqlalchemy as fsa
from sqlalchemy import func
from typing_extensions import Self

from flask_server_files.helpers import jsonize_sqla_model
from flask_server_files.sqla_instance import Base
from log_and_alert.log_setup import lg
from models.model_wrapper import ModelWrapper


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
        lg.info('New operator created: %s', new_op.__dict__.items())
        return new_op

    @classmethod
    def get_active_operators(cls, lam_number=None):
        """Get a list of         """

        if lam_number is None:
            # return cls.query.filter(OperatorModel.date_removed == None).all()
            return cls.query.all()
        else:
            certified_lam_dict = {1: OperatorModel.lam_1_certified, 2: OperatorModel.lam_2_certified}
            certified_lam_dict[0] = certified_lam_dict[1]  # for development
            lam_column_dict = certified_lam_dict[lam_number]
            # return cls.query.filter(OperatorModel.date_removed == None).filter(lam_column_dict).all()
            return cls.query.filter(lam_column_dict).all()

    @classmethod
    def find_by_id(cls, id_, get_sqalchemy=False, wrap_model=True) -> Self:
        """Get a DefectModel of a record by its id.

        :param id_: int, the id.
        :param get_sqalchemy: bool
        :return: DefectModel
        """

        id_df = cls.query.filter_by(id=id_).first()
        id_df = id_df if id_df is not None else id_df  # todo: pretty sure this line does nothing?
        if wrap_model:
            id_df = ModelWrapper(id_df)
        return id_df

    @classmethod
    def check_for_initials(cls, initials):
        return cls.query.filter(cls.initials == initials).all()

    def jsonizable(self):
        return jsonize_sqla_model(self)

    def save_to_database(self):
        """Save the changes to operator to the database."""

        with self.session() as session:
            session.add(self)
            session.commit()
            self.session.remove()

    def disable_operator(self):
        """Set the operator's date removed to now if they are not already disabled."""

        if self.date_removed is None:
            self.date_removed = func.current_timestamp()
            return True
        return False

    def enable_operator(self):
        """Set the operator's date removed to null if they are not already enabled."""

        if self.date_removed is not None:
            self.date_removed = None
            return True
        return False



if __name__ == '__main__':
    OperatorModel.new_operator(first_name='John', last_name='Doe')
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
