import datetime
import json

from fresk.sqla_instance import fsa
from fresk.defect_args import all_args
# from helpers import Timestamp
from log_setup import lg


class DefectModel(fsa.Model):
    __tablename__ = 'laminator_foam_defect_removal_records'
    
    id = fsa.Column(fsa.Integer, primary_key=True)
    source_lot_number = fsa.Column(fsa.String, default='')
    tabcode = fsa.Column(fsa.String, default='')
    recipe = fsa.Column(fsa.String, default='')
    lam_num = fsa.Column(fsa.Integer, default=0)
    # rolls_of_product_post_slit = fsa.Column(fsa.Integer, server_default='''SELECT rolls_of_product_post_slit ORDER BY
    # defect_id DESC LIMIT 1''')
    rolls_of_product_post_slit = fsa.Column(fsa.Integer, default=3)
    defect_start_ts = fsa.Column(fsa.TIMESTAMP(timezone=True), server_default='''NOW()''')
    defect_end_ts = fsa.Column(fsa.TIMESTAMP(timezone=True), server_default='''NOW()''')
    # defect_start_ts = fsa.Column(Timestamp(timezone=True))
    # defect_end_ts =  fsa.Column(Timestamp(timezone=True))
    length_of_defect_meters = fsa.Column(fsa.Float(precision=2), server_default='1.0')
    belt_marks = fsa.Column(fsa.Boolean, server_default='''False''')
    bursting = fsa.Column(fsa.Boolean, server_default='''False''')
    contamination = fsa.Column(fsa.Boolean, server_default='''False''')
    curling = fsa.Column(fsa.Boolean, server_default='''False''')
    delamination = fsa.Column(fsa.Boolean, server_default='''False''')
    lost_edge = fsa.Column(fsa.Boolean, server_default='''False''')
    puckering = fsa.Column(fsa.Boolean, server_default='''False''')
    shrinkage = fsa.Column(fsa.Boolean, server_default='''False''')
    thickness = fsa.Column(fsa.Boolean, server_default='''False''')
    wrinkles = fsa.Column(fsa.Boolean, server_default='''False''')
    other = fsa.Column(fsa.Boolean, server_default='''False''')

    # the section removed
    rem_l = fsa.Column(fsa.Boolean, server_default='''False''')
    rem_lc = fsa.Column(fsa.Boolean, server_default='''False''')
    rem_c = fsa.Column(fsa.Boolean, server_default='''False''')
    rem_rc = fsa.Column(fsa.Boolean, server_default='''False''')
    rem_r = fsa.Column(fsa.Boolean, server_default='''False''')
    entry_created_ts = fsa.Column(fsa.DateTime(timezone=True), server_default='''NOW()''')
    entry_modified_ts = fsa.Column(fsa.DateTime(timezone=True), server_default='''NOW()''')
    record_creation_source = fsa.Column(fsa.String(), server_default='''None''')
    marked_for_deletion = fsa.Column(fsa.Boolean, server_default='''False''')

    flask_sqlalchemy_instance = fsa

    def __init__(self, **kwargs):
        # for the kwargs provided, assign them to the corresponding columns
        self_keys = DefectModel.__dict__.keys()
        for kw, val in kwargs.items():
            if kw in self_keys:
                setattr(self, kw, val)

    @classmethod
    def find_by_id(cls, id_, get_sqalchemy=False):
        id_df = cls.query.filter_by(id=id_).first()
        if get_sqalchemy:
            return id_df, fsa
        return id_df

    @classmethod
    def find_new(cls):
        """Get a list of DefectModel objects where the creation and modification times are the same.

        :return: list, [<DefectModel 1>, <DefectModel 2>]
        """
        # return cls.query.filter(DefectModel.entry_created_ts=DefectModel.entry_modified_ts).all()
        return cls.query.filter(DefectModel.entry_modified_ts == DefectModel.entry_created_ts).all()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def new_defect(cls):
        new_def = DefectModel()
        new_def.save_to_database()
        # nd_db = cls.find_by_id(new_def.id)  # not needed
        return new_def

    # @classmethod
    # def new_defect(cls):
    #     cls.query.filter_by(id=0).first()
    #     # cls.query.insert

    def save_to_database(self):
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

    def json(self):
        """Get a json representation of the defect instance.

        :return: dict
        """
        jdict = {}
        for key in all_args:
            this_val = self.__dict__.get(key)
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
