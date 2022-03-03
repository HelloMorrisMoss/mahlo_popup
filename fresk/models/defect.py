import datetime

import sqlalchemy
from sqlalchemy import func

from fresk.defect_args import all_args
from fresk.sqla_instance import fsa
from log_setup import lg


class DefectModel(fsa.Model):
    """A SQLalchemy model for the defect removal record database."""
    __tablename__ = 'laminator_foam_defect_removal_records'

    id = fsa.Column(fsa.Integer, primary_key=True)
    source_lot_number = fsa.Column(fsa.String, default='')
    tabcode = fsa.Column(fsa.String, default='')
    recipe = fsa.Column(fsa.String, default='')
    lam_num = fsa.Column(fsa.Integer, default=0)
    file_name = fsa.Column(fsa.String, server_default='')
    flagger_fire = fsa.Column(fsa.TIMESTAMP(timezone=True))
    rolls_of_product_post_slit = fsa.Column(fsa.Integer, default=3)
    defect_start_ts = fsa.Column(fsa.TIMESTAMP(timezone=True), server_default=sqlalchemy.func.now())
    defect_end_ts = fsa.Column(fsa.TIMESTAMP(timezone=True), server_default=sqlalchemy.func.now())
    length_of_defect_meters = fsa.Column(fsa.Float(precision=2), server_default='0.0')
    mahlo_start_length = fsa.Column(fsa.Float(precision=2), server_default='0.0')
    mahlo_end_length = fsa.Column(fsa.Float(precision=2), server_default='0.0')

    # reason for removal
    defect_type = fsa.Column(fsa.VARCHAR(13), server_default='''thickness''')

    # the section removed
    rem_l = fsa.Column(fsa.Boolean, server_default='''False''')
    rem_lc = fsa.Column(fsa.Boolean, server_default='''False''')
    rem_c = fsa.Column(fsa.Boolean, server_default='''False''')
    rem_rc = fsa.Column(fsa.Boolean, server_default='''False''')
    rem_r = fsa.Column(fsa.Boolean, server_default='''False''')
    # TODO: these timestamps are being set to model(table) creation time, unlike the ones above
    entry_created_ts = fsa.Column(fsa.DateTime(timezone=True), server_default=sqlalchemy.func.now())
    entry_modified_ts = fsa.Column(fsa.DateTime(timezone=True), server_default=sqlalchemy.func.now())
    record_creation_source = fsa.Column(fsa.String(), server_default='')
    marked_for_deletion = fsa.Column(fsa.Boolean, server_default='''False''')
    operator_saved_time = fsa.Column(fsa.DateTime(timezone=True))

    flask_sqlalchemy_instance = fsa

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
        id_df = cls.query.filter_by(id=id_).first()
        if get_sqalchemy:
            lg.debug('returning with sqlalchemy')
            return id_df, fsa
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
            defect.operator_saved_time = func.now()
            defect.entry_modified_ts = func.now()
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
        fsa.session.add(self)
        fsa.session.commit()

    def get_model_dict(self):
        """Get a dictionary of {column_name: value}

        :return: dict
        """
        jdict = {}
        for key in all_args:
            jdict[key] = self.__dict__.get(key)
        return jdict

    def jsonizable(self):
        """Get a json serializable representation of the defect instance.

        This is needed due to datetimes, they are converted to ISO 8601 format strings.

        :return: dict
        """
        jdict = {}
        for key in all_args:
            this_val = getattr(self, key)
            if isinstance(this_val, datetime.datetime):
                try:
                    this_val = this_val.isoformat()
                except AttributeError as er:
                    lg.error(er)
                    this_val = str(this_val)
            jdict[key] = this_val
        # jdict = json.dumps(jdict, default=lambda x: x.isoformat())  # converting it to json early is not pretty
        # return {k: str(v) for k, v in self.__dict__['_sa_instance_state']._instance_dict.items() if k in all_args}
        # return {k: getattr(self, k) for k in all_args}
        return jdict
