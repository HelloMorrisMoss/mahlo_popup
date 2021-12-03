import datetime
import json

from fresk.sqla_instance import fsa
from fresk.defect_args import all_args
# from helpers import Timestamp
from log_setup import lg

class DefectModel(fsa.Model):
    __tablename__ = 'laminator_foam_defect_removal_records'
    
    id = fsa.Column(fsa.Integer, primary_key=True)
    source_lot_number = fsa.Column(fsa.String)
    tabcode = fsa.Column(fsa.String)
    recipe = fsa.Column(fsa.String)
    lam_num = fsa.Column(fsa.Integer)
    rolls_of_product_post_slit = fsa.Column(fsa.Integer)
    defect_start_ts = fsa.Column(fsa.TIMESTAMP(timezone=True))
    defect_end_ts = fsa.Column(fsa.TIMESTAMP(timezone=True))
    # defect_start_ts = fsa.Column(Timestamp(timezone=True))
    # defect_end_ts =  fsa.Column(Timestamp(timezone=True))
    length_of_defect_meters = fsa.Column(fsa.Float(precision=2))
    belt_marks = fsa.Column(fsa.Boolean)
    bursting = fsa.Column(fsa.Boolean)
    contamination = fsa.Column(fsa.Boolean)
    curling = fsa.Column(fsa.Boolean)
    delamination = fsa.Column(fsa.Boolean)
    lost_edge = fsa.Column(fsa.Boolean)
    puckering = fsa.Column(fsa.Boolean)
    shrinkage = fsa.Column(fsa.Boolean)
    thickness = fsa.Column(fsa.Boolean)
    wrinkles = fsa.Column(fsa.Boolean)
    other = fsa.Column(fsa.Boolean)
    rem_l = fsa.Column(fsa.Boolean)
    rem_lc = fsa.Column(fsa.Boolean)
    rem_c = fsa.Column(fsa.Boolean)
    rem_rc = fsa.Column(fsa.Boolean)
    rem_r = fsa.Column(fsa.Boolean)
    entry_created_ts = fsa.Column(fsa.DateTime(timezone=True))
    entry_modified_ts = fsa.Column(fsa.DateTime(timezone=True))
    record_creation_source = fsa.Column(fsa.String())

    def __init__(self, **kwargs):
        # for the kwargs provided, assign them to the corresponding columns
        self_keys = DefectModel.__dict__.keys()
        for kw, val in kwargs.items():
            if kw in self_keys:
                setattr(self, kw, val)

    @classmethod
    def find_by_id(cls, id_):
        return cls.query.filter_by(id=id_).first()

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