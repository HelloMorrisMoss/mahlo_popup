from fresk.sqla_instance import fsa
from defect_args import all_args

class DefectModel(fsa.Model):
    __tablename__ = 'laminator_foam_defect_removal_records'
    
    id = fsa.Column(fsa.Integer, primary_key=True)
    source_lot_number = fsa.Column(fsa.String)
    tabcode = fsa.Column(fsa.String)
    recipe = fsa.Column(fsa.String)
    lam_num = fsa.Column(fsa.Integer)
    rolls_of_product_post_slit = fsa.Column(fsa.Integer)
    defect_start_ts = fsa.Column(fsa.DateTime(timezone=True))
    defect_end_ts = fsa.Column(fsa.DateTime(timezone=True))
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

    def json(self):
        """Get a json representation of the defect instance.

        :return: dict
        """

        return {k: str(v) for k, v in self.__dict__['_sa_instance_state'].__dict__.items()}
