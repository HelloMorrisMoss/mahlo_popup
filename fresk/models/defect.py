import datetime

import sqlalchemy
from sqlalchemy import func

from dev_common import exception_one_line
from fresk.defect_args import all_args
from fresk.helpers import jsonize_sqla_model
from fresk.models.model_wrapper import ModelWrapper
from fresk.sqla_instance import Base, new_sqla_session
from log_setup import lg


class DefectModel(Base):
    """A SQLalchemy model for the defect removal record database."""
    __tablename__ = 'laminator_foam_defect_removal_records'

    # for use below and elsewhere to set a column to the database's current timestamp
    db_current_ts = func.current_timestamp()

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    source_lot_number = sqlalchemy.Column(sqlalchemy.String, default='')
    tabcode = sqlalchemy.Column(sqlalchemy.String, default='')
    recipe = sqlalchemy.Column(sqlalchemy.String, default='')
    lam_num = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    file_name = sqlalchemy.Column(sqlalchemy.String, server_default='')
    flagger_fire = sqlalchemy.Column(sqlalchemy.TIMESTAMP(timezone=True))
    rolls_of_product_post_slit = sqlalchemy.Column(sqlalchemy.Integer, default=3)
    defect_start_ts = sqlalchemy.Column(sqlalchemy.TIMESTAMP(timezone=True), server_default=db_current_ts)
    defect_end_ts = sqlalchemy.Column(sqlalchemy.TIMESTAMP(timezone=True), server_default=db_current_ts)
    length_of_defect_meters = sqlalchemy.Column(sqlalchemy.Float(precision=2), server_default='0.0')
    mahlo_start_length = sqlalchemy.Column(sqlalchemy.Float(precision=2), server_default='0.0')
    mahlo_end_length = sqlalchemy.Column(sqlalchemy.Float(precision=2), server_default='0.0')

    # reason for removal
    defect_type = sqlalchemy.Column(sqlalchemy.VARCHAR(13), server_default='''thickness''')

    # the section removed
    rem_l = sqlalchemy.Column(sqlalchemy.Boolean, server_default='''False''')
    rem_lc = sqlalchemy.Column(sqlalchemy.Boolean, server_default='''False''')
    rem_c = sqlalchemy.Column(sqlalchemy.Boolean, server_default='''False''')
    rem_rc = sqlalchemy.Column(sqlalchemy.Boolean, server_default='''False''')
    rem_r = sqlalchemy.Column(sqlalchemy.Boolean, server_default='''False''')
    # TODO: these timestamps are being set to model(table) creation time, unlike the ones above
    entry_created_ts = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), server_default=db_current_ts)
    entry_modified_ts = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), server_default=db_current_ts,
                                          onupdate=db_current_ts)
    record_creation_source = sqlalchemy.Column(sqlalchemy.String(), server_default='')
    marked_for_deletion = sqlalchemy.Column(sqlalchemy.Boolean, server_default='''False''')
    operator_saved_time = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True))
    operator_initials = sqlalchemy.Column(sqlalchemy.String)
    operator_list_id = sqlalchemy.Column(sqlalchemy.Integer)
    shift_number = sqlalchemy.Column(sqlalchemy.Integer)

    def __init__(self, **kwargs):
        # for the kwargs provided, assign them to the corresponding columns
        self_keys = DefectModel.__dict__.keys()
        for kw, val in kwargs.items():
            if kw in self_keys:
                setattr(self, kw, val)

    @classmethod
    def find_by_id(cls, id_, get_sqalchemy=False):
        """Get a DefectModel of a record by its id.

        :param id_: int, the id.
        :param get_sqalchemy: bool
        :return: DefectModel
        """
        with new_sqla_session() as session:
            id_df = session.query(cls).filter_by(id=id_).first()
            id_df = ModelWrapper(id_df)
        return id_df

    @classmethod
    def find_new(cls, lam_number=None):
        """Get a list of DefectModel objects that are new.
        New here is defined as the creation and modification times are the same or have no operator_saved_time.
        They will be ordered from oldest to newest.

        :return: list, [<DefectModel 1>, <DefectModel 2>]
        """

        if lam_number is None:
            return cls.query.filter(DefectModel.operator_saved_time is None or
                                    DefectModel.entry_modified_ts == DefectModel.entry_created_ts).order_by(
                DefectModel.entry_created_ts.desc()).all()
        else:

            return cls.query.filter(DefectModel.operator_saved_time is None or
                                    DefectModel.entry_modified_ts == DefectModel.entry_created_ts).filter(
                DefectModel.lam_num == lam_number and (DefectModel.flagger_fire is not sqlalchemy.TIMESTAMP or
                                                       DefectModel.record_creation_source == 'operator')).order_by(
                DefectModel.entry_created_ts.desc()).all()

    @classmethod
    def find_all(cls):
        """Get a list of all defect record as DefectModels.

        :return: list
        """
        return cls.query.all()

    @classmethod
    def mark_all_confirmed(cls):
        """Mark all a defect records that have not been confirmed as confirmed at this time.

        :return: list
        """
        unconfirmed = cls.find_new()
        for defect in unconfirmed:
            defect.operator_saved_time = defect.db_current_ts
            defect.save_to_database()

    @classmethod
    def new_defect(cls, **kwargs):
        """Create a new defect using any column values provided as keyword parameters.

        :param kwargs: dict, of kwargs['column_name'] = 'value to use'
        :return: DefectModel
        """
        new_def = DefectModel(**kwargs)
        new_def.save_to_database()
        return new_def

    @classmethod
    def get_defects_between_dates(cls, start_date, end_date):
        start_date = datetime.datetime.fromisoformat(start_date)
        end_date = datetime.datetime.fromisoformat(end_date)
        results = DefectModel.query. \
            filter(DefectModel.defect_start_ts > start_date, DefectModel.defect_start_ts < end_date). \
            order_by(DefectModel.id.desc()).all()
        return results

    def save_to_database(self):
        """Save the changed to defect to the database."""

        self.scoped_session.add(self)
        try:
            self.scoped_session.commit()
        except Exception as exc:
            lg.error(exception_one_line(exception_obj=exc))
            self.scoped_session.rollback()

    def get_model_dict(self):
        """Get a dictionary of {column_name: value}

        :return: dict
        """
        jdict = {}
        for key in all_args:
            jdict[key] = self.__dict__.get(key)
        return jdict

    def jsonizable(self):
        return jsonize_sqla_model(self)


if __name__ == '__main':
    pass
